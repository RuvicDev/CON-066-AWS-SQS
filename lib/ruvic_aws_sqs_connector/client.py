"""Cliente para AWS SQS.

Capacidades:
- send_message(): enviar mensaje a una cola.
- receive_messages(): recibir mensajes.
- delete_message(): eliminar mensaje usando receipt handle, bloqueado por defecto.
- get_queue_attributes(): consultar atributos de la cola.
"""
from __future__ import annotations
import json
from typing import Any
import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError, ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError
from .config import AwsSqsConfig
from .exceptions import AwsSqsAuthError, AwsSqsDataError, AwsSqsNetworkError, AwsSqsSecurityError
from .logging_utils import get_logger

class AwsSqsClient:
    """Cliente para gestión de colas con AWS SQS.

    Args:
        config: configuración opcional. Si se omite, lee RUVIC_AWS_SQS_*.
    Ejemplo:
        >>> client = AwsSqsClient()
        >>> client.get_queue_attributes()
        {'ApproximateNumberOfMessages': '0'}
    """
    def __init__(self, config: AwsSqsConfig | None = None) -> None:
        self.config=config or AwsSqsConfig.from_env(); self._logger=get_logger(); self._sqs=self._build_sqs_client()
    def _build_sqs_client(self):
        boto_config=BotoConfig(connect_timeout=self.config.timeout, read_timeout=self.config.timeout, retries={"max_attempts":3,"mode":"standard"})
        session=boto3.Session(aws_access_key_id=self.config.aws_access_key_id, aws_secret_access_key=self.config.aws_secret_access_key, aws_session_token=self.config.aws_session_token, region_name=self.config.region)
        return session.client("sqs", config=boto_config)
    def _handle_client_error(self, exc: ClientError) -> None:
        error=exc.response.get("Error",{}); code=error.get("Code","Unknown"); message=error.get("Message",str(exc))
        if code in {"AuthFailure","AccessDenied","AccessDeniedException","InvalidClientTokenId","SignatureDoesNotMatch","UnrecognizedClientException","ExpiredToken","InvalidSecurity"}:
            raise AwsSqsAuthError(f"AWS SQS rechazó credenciales o permisos ({code}). Revisa access key, secret, región y permisos IAM sqs:SendMessage, sqs:ReceiveMessage, sqs:DeleteMessage y sqs:GetQueueAttributes.") from exc
        if code in {"AWS.SimpleQueueService.NonExistentQueue","QueueDoesNotExist","ReceiptHandleIsInvalid","InvalidParameterValue","InvalidMessageContents","OverLimit","ThrottlingException","RequestThrottled"}:
            raise AwsSqsDataError(f"AWS SQS rechazó la solicitud ({code}): {message}. Verifica Queue URL, receipt handle, atributos y límites SQS.") from exc
        raise AwsSqsDataError(f"AWS SQS retornó un error ({code}): {message}.") from exc
    def _call(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        try: return getattr(self._sqs, operation)(**kwargs)
        except (EndpointConnectionError, ConnectTimeoutError, ReadTimeoutError) as exc: raise AwsSqsNetworkError(f"No se pudo conectar con AWS SQS en región {self.config.region}. Verifica región, red, DNS y firewall.") from exc
        except ClientError as exc: self._handle_client_error(exc); raise AssertionError("unreachable")
        except BotoCoreError as exc: raise AwsSqsNetworkError(f"Error de comunicación con AWS SQS: {exc}.") from exc
    def ping(self) -> bool:
        """Verifica acceso a la cola consultando atributos básicos.

        Returns:
            True si SQS responde.
        Ejemplo:
            >>> client.ping()
            True
        """
        self._call("get_queue_attributes", QueueUrl=self.config.queue_url, AttributeNames=["QueueArn"]); self._logger.info("Ping exitoso a AWS SQS"); return True
    def send_message(self, message_body: str, delay_seconds: int = 0, message_attributes: dict[str, str] | None = None, message_group_id: str | None = None, message_deduplication_id: str | None = None) -> dict[str, str]:
        """Envía un mensaje a la cola SQS configurada.

        Args:
            message_body: cuerpo del mensaje.
            delay_seconds: demora de entrega entre 0 y 900 segundos.
            message_attributes: atributos string opcionales.
            message_group_id: requerido para colas FIFO sin configuración especial.
            message_deduplication_id: opcional para colas FIFO.
        Returns:
            Dict con `message_id` y `md5_of_body`.
        Ejemplo:
            >>> client.send_message('{"evento":"pedido"}')
            {'message_id': '...', 'md5_of_body': '...'}
        """
        if not message_body or not message_body.strip(): raise AwsSqsDataError("message_body no puede estar vacío.")
        if len(message_body.encode("utf-8")) > 262144: raise AwsSqsSecurityError("Mensaje bloqueado: SQS permite máximo 256 KB por mensaje.")
        delay_seconds=max(0,min(int(delay_seconds),900)); payload={"QueueUrl":self.config.queue_url,"MessageBody":message_body,"DelaySeconds":delay_seconds}
        if message_attributes: payload["MessageAttributes"]={k:{"DataType":"String","StringValue":str(v)} for k,v in message_attributes.items()}
        if message_group_id: payload["MessageGroupId"]=message_group_id
        if message_deduplication_id: payload["MessageDeduplicationId"]=message_deduplication_id
        response=self._call("send_message", **payload); self._logger.info("Mensaje enviado a SQS")
        return {"message_id":response.get("MessageId",""),"md5_of_body":response.get("MD5OfMessageBody","")}
    def receive_messages(self, max_messages: int | None = None, wait_time_seconds: int | None = None, visibility_timeout: int | None = None) -> list[dict[str, Any]]:
        """Recibe mensajes de la cola SQS.

        Args:
            max_messages: máximo de mensajes, 1 a 10.
            wait_time_seconds: long polling, 0 a 20.
            visibility_timeout: timeout de invisibilidad opcional.
        Returns:
            Lista de mensajes con message_id, receipt_handle, body y attributes.
        Ejemplo:
            >>> client.receive_messages(max_messages=5)
            [{'message_id': '...', 'receipt_handle': '...', 'body': '...'}]
        """
        mm=max(1,min(int(max_messages or self.config.max_messages),10)); wait=max(0,min(int(wait_time_seconds if wait_time_seconds is not None else self.config.wait_time_seconds),20))
        payload={"QueueUrl":self.config.queue_url,"MaxNumberOfMessages":mm,"WaitTimeSeconds":wait,"AttributeNames":["All"],"MessageAttributeNames":["All"]}
        vt=visibility_timeout if visibility_timeout is not None else self.config.visibility_timeout
        if vt is not None: payload["VisibilityTimeout"]=max(0,min(int(vt),43200))
        response=self._call("receive_message", **payload); messages=[]
        for msg in response.get("Messages",[]):
            messages.append({"message_id":msg.get("MessageId",""),"receipt_handle":msg.get("ReceiptHandle",""),"body":msg.get("Body",""),"attributes":msg.get("Attributes",{}),"message_attributes":msg.get("MessageAttributes",{})})
        self._logger.info("Recibidos %d mensajes de SQS", len(messages)); return messages
    def delete_message(self, receipt_handle: str) -> bool:
        """Elimina un mensaje de la cola usando su receipt handle.

        Bloqueado por defecto porque elimina definitivamente el mensaje recibido.
        Activa RUVIC_AWS_SQS_ALLOW_DELETE_MESSAGE=true para permitirlo.

        Args:
            receipt_handle: receipt handle devuelto por receive_messages().
        Returns:
            True si AWS acepta la eliminación.
        Ejemplo:
            >>> client.delete_message(receipt_handle)
            True
        """
        if not self.config.allow_delete_message:
            raise AwsSqsSecurityError("Eliminación bloqueada por defecto. Activa RUVIC_AWS_SQS_ALLOW_DELETE_MESSAGE=true solo para uso autorizado.")
        if not receipt_handle or not receipt_handle.strip(): raise AwsSqsDataError("receipt_handle no puede estar vacío.")
        self._call("delete_message", QueueUrl=self.config.queue_url, ReceiptHandle=receipt_handle); self._logger.info("Mensaje eliminado de SQS"); return True
    def get_queue_attributes(self, attribute_names: list[str] | None = None) -> dict[str, str]:
        """Consulta atributos de la cola SQS configurada.

        Args:
            attribute_names: lista de atributos o None para All.
        Returns:
            Diccionario de atributos de la cola.
        Ejemplo:
            >>> client.get_queue_attributes()
            {'ApproximateNumberOfMessages': '0'}
        """
        response=self._call("get_queue_attributes", QueueUrl=self.config.queue_url, AttributeNames=attribute_names or ["All"])
        attrs=response.get("Attributes",{}); self._logger.info("Consultados atributos de cola SQS"); return dict(attrs)
