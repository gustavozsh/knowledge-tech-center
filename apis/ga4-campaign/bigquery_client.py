"""
Modulo Cliente BigQuery.

Este modulo contem todas as funcoes para operacoes no BigQuery:
    - Criacao de dataset e tabelas
    - Verificacao de existencia de tabelas
    - Insercao de dados
    - Delecao de particoes
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import config
from schemas import DIMENSION_SCHEMAS, TableSchema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BigQueryClient:
    """Cliente para operacoes no BigQuery."""

    def __init__(self, bq_client, project_id: str, dataset_id: Optional[str] = None):
        """
        Inicializa o cliente BigQuery.

        Args:
            bq_client: Cliente BigQuery do google-cloud-bigquery
            project_id: ID do projeto GCP
            dataset_id: ID do dataset (opcional, usa config se nao fornecido)
        """
        self.client = bq_client
        self.project_id = project_id
        self.dataset_id = dataset_id or config.bigquery.dataset_id
        self.location = config.bigquery.location

    def _get_table_ref(self, table_name: str) -> str:
        """Retorna a referencia completa da tabela."""
        return f"{self.project_id}.{self.dataset_id}.{table_name}"

    def dataset_exists(self) -> bool:
        """
        Verifica se o dataset existe.

        Returns:
            True se o dataset existe
        """
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        try:
            self.client.get_dataset(dataset_ref)
            return True
        except Exception:
            return False

    def create_dataset(self) -> bool:
        """
        Cria o dataset se nao existir.

        Returns:
            True se criou ou ja existe
        """
        from google.cloud import bigquery

        if self.dataset_exists():
            logger.info(f"Dataset ja existe: {self.dataset_id}")
            return True

        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = self.location
        dataset.description = "Dataset para dados do Google Analytics 4 - Campanhas"

        try:
            self.client.create_dataset(dataset)
            logger.info(f"Dataset criado: {dataset_ref}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar dataset {dataset_ref}: {e}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe.

        Args:
            table_name: Nome da tabela

        Returns:
            True se a tabela existe
        """
        table_ref = self._get_table_ref(table_name)
        try:
            self.client.get_table(table_ref)
            return True
        except Exception:
            return False

    def create_table(self, schema: TableSchema) -> bool:
        """
        Cria uma tabela com o schema fornecido.

        Args:
            schema: TableSchema com a definicao da tabela

        Returns:
            True se a tabela foi criada com sucesso
        """
        from google.cloud import bigquery

        table_ref = self._get_table_ref(schema.table_name)

        # Converter schema para formato BigQuery
        bq_schema = []
        for field in schema.schema_fields:
            bq_field = bigquery.SchemaField(
                name=field["name"],
                field_type=field["type"],
                mode=field.get("mode", "NULLABLE"),
                description=field.get("description", "")
            )
            bq_schema.append(bq_field)

        # Criar tabela
        table = bigquery.Table(table_ref, schema=bq_schema)
        table.description = schema.description

        # Configurar particionamento por dia
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="date"
        )

        # Configurar clustering (opcional, melhora performance de queries)
        table.clustering_fields = ["property_id", "ga4_session_key"]

        try:
            self.client.create_table(table)
            logger.info(f"Tabela criada: {table_ref}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabela {table_ref}: {e}")
            return False

    def ensure_table_exists(self, schema: TableSchema) -> bool:
        """
        Garante que uma tabela existe, criando-a se necessario.

        Args:
            schema: TableSchema com a definicao da tabela

        Returns:
            True se a tabela existe ou foi criada
        """
        if self.table_exists(schema.table_name):
            logger.info(f"Tabela ja existe: {schema.table_name}")
            return True

        return self.create_table(schema)

    def create_all_tables(self) -> Dict[str, bool]:
        """
        Cria todas as tabelas definidas nos schemas.

        Returns:
            Dicionario com resultado de criacao de cada tabela
        """
        logger.info("=" * 60)
        logger.info("CRIANDO TABELAS NO BIGQUERY")
        logger.info("=" * 60)

        # Primeiro, garantir que o dataset existe
        self.create_dataset()

        results = {}
        for key, schema in DIMENSION_SCHEMAS.items():
            results[key] = self.ensure_table_exists(schema)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        logger.info("=" * 60)
        logger.info(f"TABELAS CRIADAS: {success_count}/{total_count}")
        logger.info("=" * 60)

        return results

    def delete_partition(self, table_name: str, partition_date: str) -> bool:
        """
        Deleta uma particao especifica de uma tabela.

        Args:
            table_name: Nome da tabela
            partition_date: Data da particao (YYYY-MM-DD)

        Returns:
            True se a particao foi deletada
        """
        table_ref = self._get_table_ref(table_name)

        query = f"""
        DELETE FROM `{table_ref}`
        WHERE date = '{partition_date}'
        """

        try:
            job = self.client.query(query)
            job.result()
            logger.info(f"Particao {partition_date} deletada de {table_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar particao: {e}")
            return False

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insere linhas em uma tabela.

        Args:
            table_name: Nome da tabela
            rows: Lista de dicionarios com os dados

        Returns:
            Resultado da insercao
        """
        if not rows:
            logger.warning(f"Nenhuma linha para inserir em {table_name}")
            return {
                "status": "warning",
                "message": "Nenhuma linha para inserir",
                "rows_inserted": 0
            }

        table_ref = self._get_table_ref(table_name)

        try:
            errors = self.client.insert_rows_json(table_ref, rows)

            if errors:
                logger.error(f"Erros ao inserir dados em {table_name}: {errors}")
                return {
                    "status": "error",
                    "message": f"Erros na insercao: {errors}",
                    "rows_inserted": 0,
                    "errors": errors
                }

            logger.info(f"Inseridas {len(rows)} linhas em {table_name}")
            return {
                "status": "success",
                "message": f"Inseridas {len(rows)} linhas",
                "rows_inserted": len(rows)
            }
        except Exception as e:
            logger.error(f"Erro ao inserir dados em {table_name}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "rows_inserted": 0
            }

    def load_report(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        replace_partition: bool = True
    ) -> Dict[str, Any]:
        """
        Carrega dados de um relatorio em uma tabela.

        Args:
            table_name: Nome da tabela
            data: Lista de dicionarios com os dados
            replace_partition: Se True, deleta a particao antes de inserir

        Returns:
            Resultado do carregamento
        """
        if not data:
            return {
                "status": "warning",
                "message": "Nenhum dado para carregar",
                "table": table_name,
                "rows_inserted": 0
            }

        logger.info(f"Carregando {len(data)} linhas em {table_name}")

        # Deletar particao existente se necessario
        if replace_partition and data:
            partition_date = data[0].get("date")
            if partition_date:
                self.delete_partition(table_name, partition_date)

        # Inserir dados
        result = self.insert_rows(table_name, data)
        result["table"] = table_name

        return result


def initialize_tables(bq_client, project_id: str, dataset_id: Optional[str] = None) -> Dict[str, bool]:
    """
    Funcao de conveniencia para inicializar todas as tabelas.

    Esta funcao deve ser executada ANTES da funcao principal de extracao.

    Args:
        bq_client: Cliente BigQuery
        project_id: ID do projeto GCP
        dataset_id: ID do dataset (opcional)

    Returns:
        Dicionario com resultado de criacao de cada tabela
    """
    client = BigQueryClient(bq_client, project_id, dataset_id)
    return client.create_all_tables()
