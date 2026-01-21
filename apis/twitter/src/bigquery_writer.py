"""
Módulo para escrita de dados no Google BigQuery.

Este módulo fornece funcionalidades para criar tabelas e inserir dados
no BigQuery a partir dos dados extraídos do Twitter.

Autor: Manus AI
Data: Janeiro de 2026
"""

import logging
from typing import Dict, List, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryWriter:
    """Classe para escrita de dados no BigQuery."""
    
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        credentials: Optional[service_account.Credentials] = None
    ):
        """
        Inicializa o escritor do BigQuery.
        
        Args:
            project_id: ID do projeto no GCP
            dataset_id: ID do dataset no BigQuery
            credentials: Credenciais da conta de serviço (opcional)
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        
        if credentials:
            self.client = bigquery.Client(
                project=project_id,
                credentials=credentials
            )
        else:
            self.client = bigquery.Client(project=project_id)
        
        logger.info(f"BigQueryWriter inicializado para {project_id}.{dataset_id}")
    
    def _get_table_ref(self, table_name: str) -> str:
        """
        Retorna a referência completa da tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Referência completa no formato project.dataset.table
        """
        return f"{self.project_id}.{self.dataset_id}.{table_name}"
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            True se a tabela existe, False caso contrário
        """
        table_ref = self._get_table_ref(table_name)
        try:
            self.client.get_table(table_ref)
            return True
        except Exception:
            return False
    
    def create_table(
        self,
        table_name: str,
        schema: List[Dict[str, str]],
        description: str = "",
        partition_field: Optional[str] = "date_extraction"
    ) -> bool:
        """
        Cria uma tabela no BigQuery.
        
        Args:
            table_name: Nome da tabela
            schema: Schema da tabela (lista de campos)
            description: Descrição da tabela
            partition_field: Campo para particionamento (opcional)
            
        Returns:
            True se a tabela foi criada com sucesso
        """
        table_ref = self._get_table_ref(table_name)
        
        # Converter schema para formato BigQuery
        bq_schema = []
        for field in schema:
            bq_field = bigquery.SchemaField(
                name=field["name"],
                field_type=field["type"],
                description=field.get("description", "")
            )
            bq_schema.append(bq_field)
        
        # Criar tabela
        table = bigquery.Table(table_ref, schema=bq_schema)
        table.description = description
        
        # Configurar particionamento se especificado
        if partition_field:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field
            )
        
        try:
            self.client.create_table(table)
            logger.info(f"Tabela criada: {table_ref}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabela {table_ref}: {e}")
            return False
    
    def ensure_table_exists(
        self,
        table_name: str,
        schema: List[Dict[str, str]],
        description: str = ""
    ) -> bool:
        """
        Garante que uma tabela existe, criando-a se necessário.
        
        Args:
            table_name: Nome da tabela
            schema: Schema da tabela
            description: Descrição da tabela
            
        Returns:
            True se a tabela existe ou foi criada com sucesso
        """
        if self.table_exists(table_name):
            logger.info(f"Tabela já existe: {table_name}")
            return True
        
        return self.create_table(table_name, schema, description)
    
    def insert_rows(
        self,
        table_name: str,
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insere linhas em uma tabela.
        
        Args:
            table_name: Nome da tabela
            rows: Lista de dicionários com os dados
            
        Returns:
            Resultado da inserção
        """
        if not rows:
            logger.warning(f"Nenhuma linha para inserir em {table_name}")
            return {"status": "warning", "message": "Nenhuma linha para inserir", "rows_inserted": 0}
        
        table_ref = self._get_table_ref(table_name)
        
        try:
            errors = self.client.insert_rows_json(table_ref, rows)
            
            if errors:
                logger.error(f"Erros ao inserir dados em {table_name}: {errors}")
                return {
                    "status": "error",
                    "message": f"Erros na inserção: {errors}",
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
    
    def load_dataframe(
        self,
        table_name: str,
        dataframe,
        write_disposition: str = "WRITE_APPEND"
    ) -> Dict[str, Any]:
        """
        Carrega um DataFrame pandas em uma tabela.
        
        Args:
            table_name: Nome da tabela
            dataframe: DataFrame pandas com os dados
            write_disposition: Modo de escrita (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
            
        Returns:
            Resultado do carregamento
        """
        table_ref = self._get_table_ref(table_name)
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition
        )
        
        try:
            job = self.client.load_table_from_dataframe(
                dataframe,
                table_ref,
                job_config=job_config
            )
            job.result()  # Aguardar conclusão
            
            logger.info(f"Carregadas {len(dataframe)} linhas em {table_name}")
            return {
                "status": "success",
                "message": f"Carregadas {len(dataframe)} linhas",
                "rows_loaded": len(dataframe)
            }
        except Exception as e:
            logger.error(f"Erro ao carregar DataFrame em {table_name}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "rows_loaded": 0
            }
    
    def delete_partition(
        self,
        table_name: str,
        partition_date: str
    ) -> bool:
        """
        Deleta uma partição específica de uma tabela.
        
        Args:
            table_name: Nome da tabela
            partition_date: Data da partição (formato YYYY-MM-DD)
            
        Returns:
            True se a partição foi deletada com sucesso
        """
        table_ref = self._get_table_ref(table_name)
        
        query = f"""
        DELETE FROM `{table_ref}`
        WHERE date_extraction = '{partition_date}'
        """
        
        try:
            job = self.client.query(query)
            job.result()
            logger.info(f"Partição {partition_date} deletada de {table_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar partição: {e}")
            return False
