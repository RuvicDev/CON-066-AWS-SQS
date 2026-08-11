"""Prueba de conexión estándar del conector AWS SQS."""
from __future__ import annotations

def test_connection() -> tuple[bool, str]:
    """Prueba credenciales, permisos y acceso a la cola SQS."""
    try:
        from ruvic_aws_sqs_connector import AwsSqsAuthError, AwsSqsClient, AwsSqsConfigError, AwsSqsDataError, AwsSqsNetworkError, AwsSqsSecurityError
    except ImportError:
        return False, "La librería ruvic-aws-sqs-connector no está instalada. Instala con: pip install git+https://github.com/montealegre777/conector-AWS_SQS.git#subdirectory=lib"
    try:
        client = AwsSqsClient(); client.ping()
    except ValueError as exc:
        return False, str(exc)
    except AwsSqsConfigError as exc:
        return False, f"Configuración inválida: {exc}"
    except AwsSqsAuthError as exc:
        return False, f"Autenticación o permisos AWS inválidos: {exc}"
    except AwsSqsNetworkError as exc:
        return False, f"Error de red hacia AWS SQS: {exc}"
    except AwsSqsSecurityError as exc:
        return False, f"Bloqueo de seguridad: {exc}"
    except AwsSqsDataError as exc:
        return False, f"AWS SQS rechazó la solicitud: {exc}"
    except Exception as exc:
        return False, f"Error inesperado probando AWS SQS: {exc}"
    return True, f"Conexión exitosa a AWS SQS en región {client.config.region}."
if __name__ == "__main__":
    ok, message = test_connection(); print(f"{'OK' if ok else 'FALLO'}: {message}"); raise SystemExit(0 if ok else 1)
