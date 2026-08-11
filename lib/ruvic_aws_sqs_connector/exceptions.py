"""Excepciones propias del conector AWS SQS."""
class AwsSqsConnectorError(Exception):
    """Error base del conector AWS SQS."""
class AwsSqsConfigError(AwsSqsConnectorError):
    """Falta configuración requerida o algún valor de configuración es inválido."""
class AwsSqsAuthError(AwsSqsConnectorError):
    """Credenciales AWS inválidas, expiradas o permisos IAM insuficientes."""
class AwsSqsNetworkError(AwsSqsConnectorError):
    """Error de red, DNS, timeout o endpoint AWS SQS no alcanzable."""
class AwsSqsDataError(AwsSqsConnectorError):
    """Solicitud inválida, cola inexistente, receipt handle inválido o límite SQS alcanzado."""
class AwsSqsSecurityError(AwsSqsConnectorError):
    """Operación bloqueada por reglas de seguridad del conector."""
