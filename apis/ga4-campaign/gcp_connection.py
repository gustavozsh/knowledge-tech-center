"""
Modulo de Conexao com Google Cloud Platform.

IMPORTANTE: Este modulo deve ser chamado PRIMEIRO antes de qualquer
outra operacao que necessite de servicos GCP.

Funcoes principais:
    - connect_gcp(): Autentica e conecta ao GCP
    - get_clients(): Retorna todos os clientes inicializados
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Tuple

from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GCPConnection:
    """Gerenciador de conexao com Google Cloud Platform."""

    def __init__(self):
        self._credentials = None
        self._project_id = None
        self._bigquery_client = None
        self._ga4_client = None
        self._secret_manager_client = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def credentials(self):
        return self._credentials

    def connect(
        self,
        project_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        credentials_json: Optional[str] = None
    ) -> bool:
        """
        Conecta ao Google Cloud Platform.

        Esta funcao DEVE ser chamada antes de qualquer outra operacao.

        Args:
            project_id: ID do projeto GCP
            credentials_path: Caminho para arquivo JSON de credenciais
            credentials_json: String JSON com credenciais

        Returns:
            True se conectou com sucesso

        Raises:
            ValueError: Se nao conseguir autenticar
        """
        from google.oauth2 import service_account
        from google.auth import default as google_auth_default

        project = project_id or config.gcp.project_id
        credentials = None

        logger.info("=" * 60)
        logger.info("CONECTANDO AO GOOGLE CLOUD PLATFORM")
        logger.info("=" * 60)

        # Metodo 1: Credenciais via JSON string
        if credentials_json:
            logger.info("Autenticando via JSON string...")
            credentials_dict = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict
            )
            logger.info("Autenticacao via JSON string bem-sucedida")
            self._credentials = credentials
            self._project_id = project
            self._connected = True
            return True

        # Metodo 2: Credenciais via arquivo local
        creds_path = credentials_path or config.gcp.credentials_path
        if creds_path and os.path.exists(creds_path):
            logger.info(f"Autenticando via arquivo: {creds_path}")
            credentials = service_account.Credentials.from_service_account_file(
                creds_path
            )
            logger.info("Autenticacao via arquivo bem-sucedida")
            self._credentials = credentials
            self._project_id = project
            self._connected = True
            return True

        # Metodo 3: Variavel de ambiente GOOGLE_APPLICATION_CREDENTIALS
        env_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if env_credentials and os.path.exists(env_credentials):
            logger.info(f"Autenticando via GOOGLE_APPLICATION_CREDENTIALS")
            credentials = service_account.Credentials.from_service_account_file(
                env_credentials
            )
            logger.info("Autenticacao via variavel de ambiente bem-sucedida")
            self._credentials = credentials
            self._project_id = project
            self._connected = True
            return True

        # Metodo 4: Application Default Credentials (Cloud Run, Compute Engine, etc.)
        try:
            logger.info("Autenticando via Application Default Credentials (ADC)...")
            credentials, detected_project = google_auth_default()
            if detected_project:
                project = detected_project
            logger.info("Autenticacao via ADC bem-sucedida")
            self._credentials = credentials
            self._project_id = project
            self._connected = True
            return True
        except Exception as e:
            logger.error(f"Falha na autenticacao ADC: {e}")

        raise ValueError(
            "Nao foi possivel autenticar no GCP. "
            "Configure: credentials_path, credentials_json, "
            "GOOGLE_APPLICATION_CREDENTIALS ou execute em ambiente GCP."
        )

    def get_bigquery_client(self):
        """
        Retorna o cliente BigQuery.

        Returns:
            Cliente BigQuery inicializado
        """
        if not self._connected:
            raise RuntimeError("GCP nao conectado. Chame connect() primeiro.")

        if self._bigquery_client is None:
            from google.cloud import bigquery
            self._bigquery_client = bigquery.Client(
                project=self._project_id,
                credentials=self._credentials
            )
            logger.info(f"Cliente BigQuery inicializado - Projeto: {self._project_id}")

        return self._bigquery_client

    def get_ga4_client(self):
        """
        Retorna o cliente GA4 Data API.

        Returns:
            Cliente GA4 BetaAnalyticsDataClient
        """
        if not self._connected:
            raise RuntimeError("GCP nao conectado. Chame connect() primeiro.")

        if self._ga4_client is None:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            self._ga4_client = BetaAnalyticsDataClient(
                credentials=self._credentials
            )
            logger.info("Cliente GA4 Data API inicializado")

        return self._ga4_client

    def get_secret_manager_client(self):
        """
        Retorna o cliente Secret Manager.

        Returns:
            Cliente Secret Manager
        """
        if not self._connected:
            raise RuntimeError("GCP nao conectado. Chame connect() primeiro.")

        if self._secret_manager_client is None:
            from google.cloud import secretmanager
            self._secret_manager_client = secretmanager.SecretManagerServiceClient(
                credentials=self._credentials
            )
            logger.info("Cliente Secret Manager inicializado")

        return self._secret_manager_client

    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Recupera um secret do Secret Manager.

        Args:
            secret_id: ID do secret
            version: Versao do secret

        Returns:
            Valor do secret como string
        """
        client = self.get_secret_manager_client()
        name = f"projects/{self._project_id}/secrets/{secret_id}/versions/{version}"

        try:
            response = client.access_secret_version(name=name)
            secret_value = response.payload.data.decode("UTF-8")
            logger.info(f"Secret recuperado: {secret_id}")
            return secret_value
        except Exception as e:
            logger.error(f"Erro ao recuperar secret {secret_id}: {e}")
            raise

    def get_all_clients(self) -> Dict[str, Any]:
        """
        Retorna todos os clientes inicializados.

        Returns:
            Dicionario com todos os clientes
        """
        return {
            "bigquery": self.get_bigquery_client(),
            "ga4": self.get_ga4_client(),
            "credentials": self._credentials,
            "project_id": self._project_id
        }


# Instancia global de conexao
gcp_connection = GCPConnection()


def connect_gcp(
    project_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
    credentials_json: Optional[str] = None
) -> GCPConnection:
    """
    Funcao de conveniencia para conectar ao GCP.

    Esta funcao DEVE ser chamada PRIMEIRO antes de qualquer outra operacao.

    Args:
        project_id: ID do projeto GCP
        credentials_path: Caminho para arquivo de credenciais
        credentials_json: JSON string com credenciais

    Returns:
        Instancia de GCPConnection

    Exemplo:
        >>> gcp = connect_gcp(project_id="meu-projeto")
        >>> bq_client = gcp.get_bigquery_client()
        >>> ga4_client = gcp.get_ga4_client()
    """
    gcp_connection.connect(project_id, credentials_path, credentials_json)
    return gcp_connection


def get_clients() -> Dict[str, Any]:
    """
    Retorna todos os clientes GCP inicializados.

    IMPORTANTE: connect_gcp() deve ser chamado antes.

    Returns:
        Dicionario com clientes: bigquery, ga4, credentials, project_id
    """
    if not gcp_connection.is_connected:
        raise RuntimeError("GCP nao conectado. Chame connect_gcp() primeiro.")

    return gcp_connection.get_all_clients()
