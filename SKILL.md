---
name: aws_sqs
description: "Usa la librería ruvic_aws_sqs_connector para gestionar colas AWS SQS: enviar mensajes, recibir mensajes, eliminar mensajes con autorización explícita y consultar atributos de cola. Úsala cuando el usuario pida trabajar con colas de mensajes en AWS SQS."
triggers:
- aws sqs
- sqs
- amazon sqs
- cola de mensajes
- queue
- recibir mensaje
---

# Conector AWS SQS (ruvic_aws_sqs_connector)

## Regla crítica de credenciales

El código generado NUNCA hardcodea credenciales. Siempre se leen de variables de entorno:

| Variable | Contenido |
|---|---|
| `RUVIC_AWS_SQS_AWS_ACCESS_KEY_ID` | Access Key ID de AWS |
| `RUVIC_AWS_SQS_AWS_SECRET_ACCESS_KEY` | Secret Access Key de AWS |
| `RUVIC_AWS_SQS_AWS_SESSION_TOKEN` | Token STS opcional |
| `RUVIC_AWS_SQS_REGION` | Región AWS |
| `RUVIC_AWS_SQS_QUEUE_URL` | URL de la cola SQS |
| `RUVIC_AWS_SQS_WAIT_TIME_SECONDS` | Long polling opcional |
| `RUVIC_AWS_SQS_VISIBILITY_TIMEOUT` | Visibility timeout opcional |
| `RUVIC_AWS_SQS_MAX_MESSAGES` | Máximo de mensajes por recepción |
| `RUVIC_AWS_SQS_ALLOW_DELETE_MESSAGE` | Debe ser true para eliminar mensajes |
| `RUVIC_AWS_SQS_TIMEOUT` | Timeout opcional |

Si estas variables NO existen, el conector no está configurado: no generes código que lo use; indica al usuario que lo configure en Settings → Conectores. Nunca uses variables con alias `_DEFAULT_`, `_TEST_` o `_PRODUCCION_`.

## Conexión

```python
from ruvic_aws_sqs_connector import AwsSqsClient
client = AwsSqsClient()
```

## Capacidad 1 — Enviar mensaje

```python
result = client.send_message('{"evento":"pedido_creado","id":"123"}')
print(result["message_id"])
```

## Capacidad 2 — Recibir mensajes

```python
messages = client.receive_messages(max_messages=5)
for message in messages:
    print(message["message_id"], message["body"])
```

## Capacidad 3 — Eliminar mensaje

Eliminar mensajes está bloqueado por defecto. Requiere `RUVIC_AWS_SQS_ALLOW_DELETE_MESSAGE=true` y confirmación del usuario.

```python
client.delete_message(messages[0]["receipt_handle"])
```

## Capacidad 4 — Consultar atributos

```python
attrs = client.get_queue_attributes()
print(attrs.get("ApproximateNumberOfMessages"))
```

## Manejo de errores

```python
from ruvic_aws_sqs_connector import AwsSqsAuthError, AwsSqsConfigError, AwsSqsDataError, AwsSqsNetworkError, AwsSqsSecurityError
try:
    client.receive_messages()
except AwsSqsConfigError as exc:
    print(f"Configuración inválida: {exc}")
except AwsSqsAuthError:
    print("Credenciales o permisos IAM inválidos para AWS SQS")
except AwsSqsNetworkError:
    print("No se pudo alcanzar AWS SQS")
except AwsSqsSecurityError as exc:
    print(f"Operación bloqueada: {exc}")
except AwsSqsDataError as exc:
    print(f"AWS SQS rechazó la solicitud: {exc}")
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de `RUVIC_AWS_SQS_*`.
2. Nunca imprimas access keys, secret keys ni tokens.
3. No elimines mensajes salvo que el usuario lo confirme y `ALLOW_DELETE_MESSAGE` esté activo.
4. Procesa mensajes de forma idempotente porque SQS puede entregar al menos una vez.
5. Usa long polling para reducir respuestas vacías.
