"""
Cliente para acessar secrets do Google Cloud Secret Manager
"""

from typing import Optional
from google.cloud import secretmanager


class SecretManager:
    """
    Cliente para acessar secrets armazenados no Google Cloud Secret Manager.

    Examples:
        >>> secret_manager = SecretManager()
        >>> secret_id = "your-secret-id"
        >>> project_id = "your-project-id"
        >>> secret_value = secret_manager.access_secret_version(
        ...     secret_id=secret_id,
        ...     project_id=project_id
        ... )
    """

    def __init__(self):
        """Inicializa o cliente do Secret Manager"""
        self.client = secretmanager.SecretManagerServiceClient()

    def access_secret_version(
        self,
        secret_id: str,
        project_id: str,
        version: str = "latest"
    ) -> str:
        """
        Acessa uma versão específica de um secret.

        Args:
            secret_id: ID do secret no Secret Manager
            project_id: ID do projeto GCP
            version: Versão do secret (padrão: 'latest')

        Returns:
            Valor do secret como string

        Raises:
            Exception: Se houver erro ao acessar o secret

        Examples:
            >>> sm = SecretManager()
            >>> value = sm.access_secret_version(
            ...     secret_id="ga4-credentials",
            ...     project_id="my-project"
            ... )
        """
        # Construir o nome do recurso
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"

        try:
            # Acessar o secret
            response = self.client.access_secret_version(request={"name": name})

            # Decodificar o payload
            payload = response.payload.data.decode("UTF-8")

            return payload

        except Exception as e:
            raise Exception(f"Erro ao acessar secret '{secret_id}': {str(e)}")

    def create_secret(
        self,
        secret_id: str,
        project_id: str
    ) -> None:
        """
        Cria um novo secret (sem valor).

        Args:
            secret_id: ID do secret a ser criado
            project_id: ID do projeto GCP

        Examples:
            >>> sm = SecretManager()
            >>> sm.create_secret("ga4-credentials", "my-project")
        """
        parent = f"projects/{project_id}"

        secret = {"replication": {"automatic": {}}}

        response = self.client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": secret
            }
        )

        print(f"Secret criado: {response.name}")

    def add_secret_version(
        self,
        secret_id: str,
        project_id: str,
        payload: str
    ) -> None:
        """
        Adiciona uma nova versão a um secret existente.

        Args:
            secret_id: ID do secret
            project_id: ID do projeto GCP
            payload: Valor do secret (string)

        Examples:
            >>> sm = SecretManager()
            >>> sm.add_secret_version(
            ...     secret_id="ga4-credentials",
            ...     project_id="my-project",
            ...     payload='{"type": "service_account", ...}'
            ... )
        """
        parent = f"projects/{project_id}/secrets/{secret_id}"

        payload_bytes = payload.encode("UTF-8")

        response = self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {"data": payload_bytes}
            }
        )

        print(f"Versão adicionada: {response.name}")

    def list_secrets(self, project_id: str) -> list:
        """
        Lista todos os secrets em um projeto.

        Args:
            project_id: ID do projeto GCP

        Returns:
            Lista de secrets

        Examples:
            >>> sm = SecretManager()
            >>> secrets = sm.list_secrets("my-project")
            >>> for secret in secrets:
            ...     print(secret.name)
        """
        parent = f"projects/{project_id}"

        secrets = []
        for secret in self.client.list_secrets(request={"parent": parent}):
            secrets.append(secret)

        return secrets

    def delete_secret(
        self,
        secret_id: str,
        project_id: str
    ) -> None:
        """
        Deleta um secret.

        Args:
            secret_id: ID do secret a ser deletado
            project_id: ID do projeto GCP

        Examples:
            >>> sm = SecretManager()
            >>> sm.delete_secret("ga4-credentials", "my-project")
        """
        name = f"projects/{project_id}/secrets/{secret_id}"

        self.client.delete_secret(request={"name": name})

        print(f"Secret deletado: {name}")
