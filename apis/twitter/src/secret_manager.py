"""
Módulo para acesso ao Google Cloud Secret Manager.

Este módulo fornece funcionalidades para recuperar secrets
armazenados no Secret Manager do GCP.

Autor: Manus AI
Data: Janeiro de 2026
"""

import json
import logging
from typing import Dict, Any, Optional
from google.cloud import secretmanager
from google.oauth2 import service_account

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecretManagerClient:
    """Cliente para acesso ao Secret Manager do GCP."""
    
    def __init__(
        self,
        project_id: str,
        credentials: Optional[service_account.Credentials] = None
    ):
        """
        Inicializa o cliente do Secret Manager.
        
        Args:
            project_id: ID do projeto no GCP
            credentials: Credenciais da conta de serviço (opcional)
        """
        self.project_id = project_id
        
        if credentials:
            self.client = secretmanager.SecretManagerServiceClient(
                credentials=credentials
            )
        else:
            self.client = secretmanager.SecretManagerServiceClient()
        
        logger.info(f"SecretManagerClient inicializado para projeto: {project_id}")
    
    def get_secret(
        self,
        secret_id: str,
        version: str = "latest"
    ) -> str:
        """
        Recupera o valor de um secret.
        
        Args:
            secret_id: ID do secret
            version: Versão do secret (padrão: latest)
            
        Returns:
            Valor do secret como string
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        
        try:
            response = self.client.access_secret_version(name=name)
            secret_value = response.payload.data.decode("UTF-8")
            logger.info(f"Secret recuperado: {secret_id}")
            return secret_value
        except Exception as e:
            logger.error(f"Erro ao recuperar secret {secret_id}: {e}")
            raise
    
    def get_secret_json(
        self,
        secret_id: str,
        version: str = "latest"
    ) -> Dict[str, Any]:
        """
        Recupera o valor de um secret como JSON.
        
        Args:
            secret_id: ID do secret
            version: Versão do secret (padrão: latest)
            
        Returns:
            Valor do secret como dicionário
        """
        secret_value = self.get_secret(secret_id, version)
        return json.loads(secret_value)
    
    def get_credentials_from_secret(
        self,
        secret_id: str,
        version: str = "latest"
    ) -> service_account.Credentials:
        """
        Recupera credenciais de conta de serviço de um secret.
        
        Args:
            secret_id: ID do secret contendo as credenciais JSON
            version: Versão do secret (padrão: latest)
            
        Returns:
            Objeto de credenciais da conta de serviço
        """
        credentials_dict = self.get_secret_json(secret_id, version)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict
        )
        logger.info(f"Credenciais carregadas do secret: {secret_id}")
        return credentials


def get_secret_from_file(file_path: str) -> Dict[str, Any]:
    """
    Recupera credenciais de um arquivo JSON local.
    
    Args:
        file_path: Caminho para o arquivo JSON
        
    Returns:
        Conteúdo do arquivo como dicionário
    """
    with open(file_path, "r") as f:
        return json.load(f)


def get_credentials_from_file(file_path: str) -> service_account.Credentials:
    """
    Recupera credenciais de conta de serviço de um arquivo local.
    
    Args:
        file_path: Caminho para o arquivo JSON de credenciais
        
    Returns:
        Objeto de credenciais da conta de serviço
    """
    credentials = service_account.Credentials.from_service_account_file(file_path)
    logger.info(f"Credenciais carregadas do arquivo: {file_path}")
    return credentials
