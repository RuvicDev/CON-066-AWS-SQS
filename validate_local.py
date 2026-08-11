"""Validación local del conector AWS SQS contra AWS real.

Requiere RUVIC_AWS_SQS_* apuntando a una cola de prueba. Por defecto prueba
ping, atributos, envío y recepción. La eliminación real requiere flag explícito.
"""
from __future__ import annotations
import os, json
from ruvic_aws_sqs_connector import AwsSqsClient, AwsSqsSecurityError, setup_logging
setup_logging("INFO")
client = AwsSqsClient()
print("== Ping =="); print(client.ping())
print("== Atributos =="); attrs = client.get_queue_attributes(); print({k: attrs.get(k) for k in ["QueueArn","ApproximateNumberOfMessages","VisibilityTimeout"]})
print("== Enviar mensaje real de prueba =="); sent = client.send_message(json.dumps({"source":"ruvic-local-test","kind":"validation"})); print(sent)
print("== Recibir mensajes =="); messages = client.receive_messages(max_messages=5, wait_time_seconds=5); print(f"Mensajes: {len(messages)}"); [print({"message_id":m["message_id"],"body":m["body"]}) for m in messages]
print("== Bloqueo delete por defecto ==")
try:
    client.delete_message("fake-receipt-handle")
except AwsSqsSecurityError as exc:
    print(f"  OK bloqueo confirmado: {exc}")
else:
    raise RuntimeError("FALLO: delete_message no se bloqueó")
if os.environ.get("RUVIC_AWS_SQS_RUN_DELETE_TESTS", "").lower() == "true":
    if not messages:
        raise RuntimeError("No hay mensajes recibidos para probar delete real")
    print("== Eliminación real de mensaje =="); print(client.delete_message(messages[0]["receipt_handle"]))
else:
    print("Delete real omitido. Define RUN_DELETE_TESTS=true y ALLOW_DELETE_MESSAGE=true para eliminar.")
