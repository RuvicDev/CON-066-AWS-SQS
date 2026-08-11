# Conector AWS SQS para Ruvic

Conector Ruvic para gestión de colas de mensajes con Amazon Simple Queue Service (AWS SQS): enviar mensaje, recibir mensajes, eliminar mensaje y consultar atributos.

## Capacidades

1. `send_message(...)`.
2. `receive_messages(...)`.
3. `delete_message(receipt_handle)` bloqueado por defecto.
4. `get_queue_attributes(...)`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./lib
```

Desde Git:

```bash
pip install git+https://github.com/montealegre777/conector-AWS_SQS.git#subdirectory=lib
```

## Variables de entorno

| Variable | Obligatoria | Descripción | Default |
|---|---:|---|---|
| `RUVIC_AWS_SQS_AWS_ACCESS_KEY_ID` | Sí | Access Key ID | — |
| `RUVIC_AWS_SQS_AWS_SECRET_ACCESS_KEY` | Sí | Secret Access Key | — |
| `RUVIC_AWS_SQS_AWS_SESSION_TOKEN` | No | Token STS temporal | — |
| `RUVIC_AWS_SQS_REGION` | Sí | Región AWS | — |
| `RUVIC_AWS_SQS_QUEUE_URL` | Sí | URL de la cola SQS | — |
| `RUVIC_AWS_SQS_WAIT_TIME_SECONDS` | No | Long polling, 0-20 | `10` |
| `RUVIC_AWS_SQS_VISIBILITY_TIMEOUT` | No | Visibility timeout | — |
| `RUVIC_AWS_SQS_MAX_MESSAGES` | No | Máximo recepción, 1-10 | `10` |
| `RUVIC_AWS_SQS_ALLOW_DELETE_MESSAGE` | No | Habilita delete real | `false` |
| `RUVIC_AWS_SQS_TIMEOUT` | No | Timeout de red | `20` |

## Permisos IAM mínimos

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["sqs:GetQueueAttributes", "sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage"],
    "Resource": "arn:aws:sqs:REGION:ACCOUNT_ID:QUEUE_NAME"
  }]
}
```

## Pruebas

```bash
python test_connection.py
python validate_local.py
```

Para eliminar un mensaje real recibido:

```bash
export RUVIC_AWS_SQS_ALLOW_DELETE_MESSAGE=true
export RUVIC_AWS_SQS_RUN_DELETE_TESTS=true
python validate_local.py
```

## Seguridad

- No uses credenciales root.
- Nunca subas access keys al repositorio.
- `delete_message` está bloqueado por defecto porque elimina mensajes.
- Diseña consumidores idempotentes: SQS ofrece entrega al menos una vez.
