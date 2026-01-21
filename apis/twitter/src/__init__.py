"""
Módulo src da API do Twitter.

Este módulo contém os componentes principais para extração de dados
do Twitter e carregamento no BigQuery.
"""

from .twitter_client import TwitterClient, TwitterDataExtractor
from .bigquery_writer import BigQueryWriter
from .secret_manager import SecretManagerClient, get_secret_from_file, get_credentials_from_file

__all__ = [
    "TwitterClient",
    "TwitterDataExtractor",
    "BigQueryWriter",
    "SecretManagerClient",
    "get_secret_from_file",
    "get_credentials_from_file",
]
