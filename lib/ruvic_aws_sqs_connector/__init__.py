"""Conector Ruvic para AWS SQS."""
from .client import AwsSqsClient
from .config import ENV_PREFIX, AwsSqsConfig
from .exceptions import AwsSqsAuthError, AwsSqsConfigError, AwsSqsConnectorError, AwsSqsDataError, AwsSqsNetworkError, AwsSqsSecurityError
from .logging_utils import setup_logging
__all__=["ENV_PREFIX","AwsSqsAuthError","AwsSqsClient","AwsSqsConfig","AwsSqsConfigError","AwsSqsConnectorError","AwsSqsDataError","AwsSqsNetworkError","AwsSqsSecurityError","setup_logging"]
__version__="1.0.0"
