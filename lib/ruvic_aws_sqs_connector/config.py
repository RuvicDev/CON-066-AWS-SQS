"""Configuración del conector leída desde variables de entorno.

Prefijo: RUVIC_AWS_SQS_
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from .exceptions import AwsSqsConfigError
ENV_PREFIX = "RUVIC_AWS_SQS_"

def _to_bool(value: str, default: bool = False) -> bool:
    raw = (value or "").strip().lower()
    if raw == "": return default
    if raw in {"true","1","yes","y","on"}: return True
    if raw in {"false","0","no","n","off"}: return False
    raise AwsSqsConfigError("Configuración inválida: los campos booleanos deben ser true/false.")

@dataclass(frozen=True)
class AwsSqsConfig:
    """Parámetros para autenticar y usar AWS SQS."""
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str
    queue_url: str
    aws_session_token: str | None = None
    wait_time_seconds: int = 10
    visibility_timeout: int | None = None
    max_messages: int = 10
    allow_delete_message: bool = False
    timeout: int = 20

    @classmethod
    def from_env(cls) -> "AwsSqsConfig":
        """Construye la configuración desde variables RUVIC_AWS_SQS_*.

        Raises:
            ValueError: si faltan variables requeridas.
            AwsSqsConfigError: si un valor opcional es inválido.
        Ejemplo:
            >>> config = AwsSqsConfig.from_env()
            >>> config.region
            'us-east-1'
        """
        aws_access_key_id=os.environ.get(f"{ENV_PREFIX}AWS_ACCESS_KEY_ID","").strip(); aws_secret_access_key=os.environ.get(f"{ENV_PREFIX}AWS_SECRET_ACCESS_KEY","").strip(); region=os.environ.get(f"{ENV_PREFIX}REGION","").strip(); queue_url=os.environ.get(f"{ENV_PREFIX}QUEUE_URL","").strip()
        missing=[n for n,v in ((f"{ENV_PREFIX}AWS_ACCESS_KEY_ID",aws_access_key_id),(f"{ENV_PREFIX}AWS_SECRET_ACCESS_KEY",aws_secret_access_key),(f"{ENV_PREFIX}REGION",region),(f"{ENV_PREFIX}QUEUE_URL",queue_url)) if not v]
        if missing:
            raise ValueError("Faltan variables de entorno del conector aws_sqs: "+", ".join(missing)+". Configura el conector en Settings → Conectores.")
        try:
            wait_time_seconds=int(os.environ.get(f"{ENV_PREFIX}WAIT_TIME_SECONDS","10").strip() or "10"); timeout=int(os.environ.get(f"{ENV_PREFIX}TIMEOUT","20").strip() or "20"); max_messages=int(os.environ.get(f"{ENV_PREFIX}MAX_MESSAGES","10").strip() or "10")
            vt_raw=os.environ.get(f"{ENV_PREFIX}VISIBILITY_TIMEOUT","").strip(); visibility_timeout=int(vt_raw) if vt_raw else None
            allow_delete_message=_to_bool(os.environ.get(f"{ENV_PREFIX}ALLOW_DELETE_MESSAGE","false"), default=False)
        except ValueError as exc:
            raise AwsSqsConfigError("Configuración inválida: WAIT_TIME_SECONDS, TIMEOUT, MAX_MESSAGES y VISIBILITY_TIMEOUT deben ser enteros.") from exc
        if wait_time_seconds < 0 or wait_time_seconds > 20: raise AwsSqsConfigError("RUVIC_AWS_SQS_WAIT_TIME_SECONDS debe estar entre 0 y 20.")
        if timeout <= 0 or timeout > 120: raise AwsSqsConfigError("RUVIC_AWS_SQS_TIMEOUT debe estar entre 1 y 120.")
        if max_messages <= 0 or max_messages > 10: raise AwsSqsConfigError("RUVIC_AWS_SQS_MAX_MESSAGES debe estar entre 1 y 10.")
        if visibility_timeout is not None and (visibility_timeout < 0 or visibility_timeout > 43200): raise AwsSqsConfigError("RUVIC_AWS_SQS_VISIBILITY_TIMEOUT debe estar entre 0 y 43200.")
        return cls(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=os.environ.get(f"{ENV_PREFIX}AWS_SESSION_TOKEN","").strip() or None, region=region, queue_url=queue_url, wait_time_seconds=wait_time_seconds, visibility_timeout=visibility_timeout, max_messages=max_messages, allow_delete_message=allow_delete_message, timeout=timeout)
