"""
Módulo de Autenticação para GCP, BigQuery e Secret Manager.

Este módulo contém todas as funções de autenticação e inicialização
de clientes para os serviços do Google Cloud Platform.

IMPORTANTE: Este módulo deve ser importado PRIMEIRO antes de qualquer
outro módulo que utilize serviços do GCP.

Autor: Manus AI
Data: Janeiro de 2026
Versão: 2.0.0
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÃO DE AUTENTICAÇÃO
# =============================================================================

@dataclass
class AuthConfig:
    """Configuração de autenticação."""
    project_id: str = "cadastra-yduqs-uat"
    secret_id_bq: str = "Acesso_BQ"
    secret_id_ga4: str = "ga4-credentials"
    credentials_path: Optional[str] = None  # Caminho local para credenciais (desenvolvimento)


# Configuração global
AUTH_CONFIG = AuthConfig()


# =============================================================================
# FUNÇÕES DE AUTENTICAÇÃO
# =============================================================================

def authenticate_gcp(
    project_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
    credentials_json: Optional[str] = None
) -> Tuple[Any, str]:
    """
    Autentica no Google Cloud Platform.
    
    Esta é a PRIMEIRA função que deve ser chamada antes de usar
    qualquer serviço do GCP.
    
    Args:
        project_id: ID do projeto GCP (usa AUTH_CONFIG se não fornecido)
        credentials_path: Caminho para arquivo JSON de credenciais
        credentials_json: String JSON com credenciais
        
    Returns:
        Tupla (credentials, project_id)
        
    Raises:
        ValueError: Se não conseguir autenticar
        
    Exemplo:
        >>> credentials, project = authenticate_gcp()
        >>> # Agora pode usar os outros serviços
    """
    from google.oauth2 import service_account
    from google.auth import default as google_auth_default
    
    project = project_id or AUTH_CONFIG.project_id
    credentials = None
    
    logger.info(f"Iniciando autenticação GCP para projeto: {project}")
    
    # Método 1: Credenciais via JSON string
    if credentials_json:
        logger.info("Usando credenciais via JSON string")
        credentials_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict
        )
        logger.info("✓ Autenticação via JSON string bem-sucedida")
        return credentials, project
    
    # Método 2: Credenciais via arquivo local
    if credentials_path:
        if os.path.exists(credentials_path):
            logger.info(f"Usando credenciais do arquivo: {credentials_path}")
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            logger.info("✓ Autenticação via arquivo bem-sucedida")
            return credentials, project
        else:
            logger.warning(f"Arquivo de credenciais não encontrado: {credentials_path}")
    
    # Método 3: Credenciais do AUTH_CONFIG
    if AUTH_CONFIG.credentials_path and os.path.exists(AUTH_CONFIG.credentials_path):
        logger.info(f"Usando credenciais do AUTH_CONFIG: {AUTH_CONFIG.credentials_path}")
        credentials = service_account.Credentials.from_service_account_file(
            AUTH_CONFIG.credentials_path
        )
        logger.info("✓ Autenticação via AUTH_CONFIG bem-sucedida")
        return credentials, project
    
    # Método 4: Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS
    env_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_credentials and os.path.exists(env_credentials):
        logger.info(f"Usando GOOGLE_APPLICATION_CREDENTIALS: {env_credentials}")
        credentials = service_account.Credentials.from_service_account_file(
            env_credentials
        )
        logger.info("✓ Autenticação via variável de ambiente bem-sucedida")
        return credentials, project
    
    # Método 5: Credenciais padrão do ambiente (Cloud Run, Compute Engine, etc.)
    try:
        logger.info("Tentando usar credenciais padrão do ambiente (ADC)")
        credentials, detected_project = google_auth_default()
        if detected_project:
            project = detected_project
        logger.info("✓ Autenticação via ADC bem-sucedida")
        return credentials, project
    except Exception as e:
        logger.error(f"Falha na autenticação ADC: {e}")
    
    raise ValueError(
        "Não foi possível autenticar no GCP. "
        "Configure uma das opções: credentials_path, credentials_json, "
        "GOOGLE_APPLICATION_CREDENTIALS ou execute em ambiente GCP."
    )


def get_secret_manager_client(credentials: Any = None, project_id: Optional[str] = None):
    """
    Obtém um cliente do Secret Manager.
    
    Args:
        credentials: Credenciais GCP (obtidas via authenticate_gcp)
        project_id: ID do projeto
        
    Returns:
        Cliente do Secret Manager
    """
    from google.cloud import secretmanager
    
    project = project_id or AUTH_CONFIG.project_id
    
    if credentials:
        client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    else:
        client = secretmanager.SecretManagerServiceClient()
    
    logger.info(f"✓ Cliente Secret Manager inicializado para projeto: {project}")
    return client, project


def get_secret(
    secret_id: str,
    credentials: Any = None,
    project_id: Optional[str] = None,
    version: str = "latest"
) -> str:
    """
    Recupera um secret do Secret Manager.
    
    Args:
        secret_id: ID do secret
        credentials: Credenciais GCP
        project_id: ID do projeto
        version: Versão do secret
        
    Returns:
        Valor do secret como string
    """
    client, project = get_secret_manager_client(credentials, project_id)
    
    name = f"projects/{project}/secrets/{secret_id}/versions/{version}"
    
    try:
        response = client.access_secret_version(name=name)
        secret_value = response.payload.data.decode("UTF-8")
        logger.info(f"✓ Secret recuperado: {secret_id}")
        return secret_value
    except Exception as e:
        logger.error(f"✗ Erro ao recuperar secret {secret_id}: {e}")
        raise


def get_secret_as_json(
    secret_id: str,
    credentials: Any = None,
    project_id: Optional[str] = None,
    version: str = "latest"
) -> Dict[str, Any]:
    """
    Recupera um secret do Secret Manager como JSON.
    
    Args:
        secret_id: ID do secret
        credentials: Credenciais GCP
        project_id: ID do projeto
        version: Versão do secret
        
    Returns:
        Valor do secret como dicionário
    """
    secret_value = get_secret(secret_id, credentials, project_id, version)
    return json.loads(secret_value)


def get_credentials_from_secret(
    secret_id: str,
    credentials: Any = None,
    project_id: Optional[str] = None
) -> Any:
    """
    Recupera credenciais de conta de serviço de um secret.
    
    Args:
        secret_id: ID do secret contendo as credenciais JSON
        credentials: Credenciais GCP para acessar o Secret Manager
        project_id: ID do projeto
        
    Returns:
        Objeto de credenciais da conta de serviço
    """
    from google.oauth2 import service_account
    
    credentials_dict = get_secret_as_json(secret_id, credentials, project_id)
    new_credentials = service_account.Credentials.from_service_account_info(
        credentials_dict
    )
    logger.info(f"✓ Credenciais carregadas do secret: {secret_id}")
    return new_credentials


def get_bigquery_client(credentials: Any = None, project_id: Optional[str] = None):
    """
    Obtém um cliente do BigQuery.
    
    Args:
        credentials: Credenciais GCP (obtidas via authenticate_gcp)
        project_id: ID do projeto
        
    Returns:
        Cliente do BigQuery
    """
    from google.cloud import bigquery
    
    project = project_id or AUTH_CONFIG.project_id
    
    if credentials:
        client = bigquery.Client(project=project, credentials=credentials)
    else:
        client = bigquery.Client(project=project)
    
    logger.info(f"✓ Cliente BigQuery inicializado para projeto: {project}")
    return client


def get_ga4_client(credentials: Any = None):
    """
    Obtém um cliente do Google Analytics Data API.
    
    Args:
        credentials: Credenciais GCP (obtidas via authenticate_gcp)
        
    Returns:
        Cliente do GA4 Data API
    """
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    
    if credentials:
        client = BetaAnalyticsDataClient(credentials=credentials)
    else:
        client = BetaAnalyticsDataClient()
    
    logger.info("✓ Cliente GA4 Data API inicializado")
    return client


# =============================================================================
# FUNÇÃO DE INICIALIZAÇÃO COMPLETA
# =============================================================================

def initialize_all_clients(
    project_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
    use_secret_manager: bool = True
) -> Dict[str, Any]:
    """
    Inicializa todos os clientes necessários para a API.
    
    Esta função é o ponto de entrada principal para autenticação.
    Ela autentica no GCP e inicializa todos os clientes necessários.
    
    Args:
        project_id: ID do projeto GCP
        credentials_path: Caminho para arquivo de credenciais
        use_secret_manager: Se True, tenta obter credenciais do Secret Manager
        
    Returns:
        Dicionário com todos os clientes inicializados:
        {
            "credentials": credentials,
            "project_id": project_id,
            "bigquery": bigquery_client,
            "ga4": ga4_client,
            "secret_manager": secret_manager_client
        }
        
    Exemplo:
        >>> clients = initialize_all_clients()
        >>> bq_client = clients["bigquery"]
        >>> ga4_client = clients["ga4"]
    """
    logger.info("=" * 50)
    logger.info("INICIALIZANDO CLIENTES GCP")
    logger.info("=" * 50)
    
    # 1. Autenticar no GCP
    credentials, project = authenticate_gcp(
        project_id=project_id,
        credentials_path=credentials_path
    )
    
    # 2. Inicializar clientes
    clients = {
        "credentials": credentials,
        "project_id": project,
        "bigquery": None,
        "ga4": None,
        "secret_manager": None
    }
    
    # 3. Tentar obter credenciais específicas do Secret Manager
    ga4_credentials = credentials
    bq_credentials = credentials
    
    if use_secret_manager:
        try:
            # Credenciais para GA4
            ga4_credentials = get_credentials_from_secret(
                AUTH_CONFIG.secret_id_ga4,
                credentials,
                project
            )
        except Exception as e:
            logger.warning(f"Usando credenciais padrão para GA4: {e}")
        
        try:
            # Credenciais para BigQuery
            bq_credentials = get_credentials_from_secret(
                AUTH_CONFIG.secret_id_bq,
                credentials,
                project
            )
        except Exception as e:
            logger.warning(f"Usando credenciais padrão para BigQuery: {e}")
    
    # 4. Inicializar clientes específicos
    try:
        clients["bigquery"] = get_bigquery_client(bq_credentials, project)
    except Exception as e:
        logger.error(f"Erro ao inicializar BigQuery: {e}")
    
    try:
        clients["ga4"] = get_ga4_client(ga4_credentials)
    except Exception as e:
        logger.error(f"Erro ao inicializar GA4: {e}")
    
    try:
        clients["secret_manager"], _ = get_secret_manager_client(credentials, project)
    except Exception as e:
        logger.error(f"Erro ao inicializar Secret Manager: {e}")
    
    logger.info("=" * 50)
    logger.info("INICIALIZAÇÃO CONCLUÍDA")
    logger.info("=" * 50)
    
    return clients


# =============================================================================
# TESTE DE AUTENTICAÇÃO
# =============================================================================

def test_authentication(credentials_path: Optional[str] = None) -> bool:
    """
    Testa se a autenticação está funcionando corretamente.
    
    Args:
        credentials_path: Caminho para arquivo de credenciais
        
    Returns:
        True se a autenticação foi bem-sucedida
    """
    logger.info("Testando autenticação...")
    
    try:
        credentials, project = authenticate_gcp(credentials_path=credentials_path)
        logger.info(f"✓ Autenticação OK - Projeto: {project}")
        
        # Testar BigQuery
        try:
            bq_client = get_bigquery_client(credentials, project)
            datasets = list(bq_client.list_datasets(max_results=1))
            logger.info(f"✓ BigQuery OK - {len(datasets)} dataset(s) encontrado(s)")
        except Exception as e:
            logger.warning(f"⚠ BigQuery: {e}")
        
        # Testar GA4
        try:
            ga4_client = get_ga4_client(credentials)
            logger.info("✓ GA4 Client OK")
        except Exception as e:
            logger.warning(f"⚠ GA4: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Falha na autenticação: {e}")
        return False


if __name__ == "__main__":
    # Executar teste de autenticação
    test_authentication()
