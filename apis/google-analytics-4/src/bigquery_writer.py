"""
Cliente para escrever dados no Google BigQuery
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account


class BigQueryWriter:
    """
    Cliente para escrever dados do Google Analytics 4 no BigQuery.

    Attributes:
        client: Cliente do BigQuery
        project_id: ID do projeto GCP
        dataset_id: ID do dataset (padrão: 'RAW')

    Examples:
        >>> writer = BigQueryWriter(
        ...     project_id='my-project',
        ...     credentials=credentials
        ... )
        >>> writer.write_ga4_data(
        ...     table_id='ga4_daily_report',
        ...     data=response_data
        ... )
    """

    def __init__(
        self,
        project_id: str,
        dataset_id: str = "RAW",
        credentials: Optional[service_account.Credentials] = None
    ):
        """
        Inicializa o cliente BigQuery.

        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset (padrão: 'RAW')
            credentials: Credenciais de autenticação (opcional)
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

    def ensure_dataset_exists(self) -> None:
        """
        Garante que o dataset existe, criando-o se necessário.

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> writer.ensure_dataset_exists()
        """
        dataset_ref = f"{self.project_id}.{self.dataset_id}"

        try:
            self.client.get_dataset(dataset_ref)
            print(f"Dataset {dataset_ref} já existe")
        except Exception:
            # Dataset não existe, criar
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # ou sua região preferida
            dataset.description = "Dataset RAW para dados do Google Analytics 4"

            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"Dataset {dataset_ref} criado com sucesso")

    def create_table_if_not_exists(
        self,
        table_id: str,
        schema: Optional[List[bigquery.SchemaField]] = None
    ) -> None:
        """
        Cria uma tabela se ela não existir.

        Args:
            table_id: ID da tabela
            schema: Schema da tabela (opcional, usa schema padrão se não fornecido)

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> writer.create_table_if_not_exists('ga4_daily_report')
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"

        try:
            self.client.get_table(table_ref)
            print(f"Tabela {table_ref} já existe")
        except Exception:
            # Tabela não existe, criar
            if schema is None:
                schema = self._get_default_schema()

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            print(f"Tabela {table_ref} criada com sucesso")

    def _get_default_schema(self) -> List[bigquery.SchemaField]:
        """
        Retorna o schema padrão para tabelas de dados do GA4.

        Returns:
            Lista de SchemaFields
        """
        return [
            bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("report_date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("dimensions", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("metrics", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("row_data", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        ]

    def write_ga4_data(
        self,
        table_id: str,
        data: Dict[str, Any],
        auto_create: bool = True
    ) -> None:
        """
        Escreve dados do GA4 no BigQuery.

        Args:
            table_id: ID da tabela de destino
            data: Dados do GA4 (resposta processada)
            auto_create: Se True, cria a tabela automaticamente se não existir

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> response = client.run_report(request)
            >>> writer.write_ga4_data('ga4_daily_report', response)
        """
        # Garantir que dataset e tabela existem
        if auto_create:
            self.ensure_dataset_exists()
            self.create_table_if_not_exists(table_id)

        # Preparar os dados para inserção
        rows = self._prepare_rows(data)

        if not rows:
            print("Nenhum dado para inserir")
            return

        # Inserir dados
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        errors = self.client.insert_rows_json(table_ref, rows)

        if errors:
            print(f"Erros ao inserir dados: {errors}")
            raise Exception(f"Falha ao inserir dados no BigQuery: {errors}")
        else:
            print(f"✓ {len(rows)} linhas inseridas com sucesso em {table_ref}")

    def _prepare_rows(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepara os dados do GA4 para inserção no BigQuery.

        Args:
            data: Dados processados do GA4

        Returns:
            Lista de dicionários prontos para inserção
        """
        rows = []
        ingestion_timestamp = datetime.utcnow().isoformat()

        for row_data in data.get('rows', []):
            row = {
                "ingestion_timestamp": ingestion_timestamp,
                "report_date": None,  # Será extraído das dimensões se disponível
                "dimensions": json.dumps(row_data.get('dimensions', {})),
                "metrics": json.dumps(row_data.get('metrics', {})),
                "row_data": json.dumps(row_data),
                "metadata": json.dumps(data.get('metadata', {}))
            }

            # Tentar extrair a data do relatório das dimensões
            if 'date' in row_data.get('dimensions', {}):
                date_str = row_data['dimensions']['date']
                # Formato esperado: YYYYMMDD
                try:
                    row['report_date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                except Exception:
                    pass

            rows.append(row)

        return rows

    def write_batch_reports(
        self,
        table_id: str,
        reports: List[Dict[str, Any]],
        auto_create: bool = True
    ) -> None:
        """
        Escreve múltiplos relatórios do GA4 no BigQuery.

        Args:
            table_id: ID da tabela de destino
            reports: Lista de relatórios do GA4
            auto_create: Se True, cria a tabela automaticamente se não existir

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> reports = client.batch_run_reports(requests)
            >>> writer.write_batch_reports('ga4_batch_reports', reports)
        """
        for i, report in enumerate(reports, 1):
            print(f"Processando relatório {i}/{len(reports)}...")
            self.write_ga4_data(table_id, report, auto_create)

    def query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Executa uma query SQL no BigQuery.

        Args:
            sql: Query SQL a ser executada

        Returns:
            Lista de resultados como dicionários

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> results = writer.query(
            ...     "SELECT * FROM RAW.ga4_daily_report LIMIT 10"
            ... )
        """
        query_job = self.client.query(sql)
        results = query_job.result()

        rows = []
        for row in results:
            rows.append(dict(row))

        return rows

    def create_partitioned_table(
        self,
        table_id: str,
        partition_field: str = "report_date",
        schema: Optional[List[bigquery.SchemaField]] = None
    ) -> None:
        """
        Cria uma tabela particionada por data.

        Args:
            table_id: ID da tabela
            partition_field: Campo usado para particionamento
            schema: Schema da tabela (opcional)

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> writer.create_partitioned_table('ga4_daily_report')
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"

        if schema is None:
            schema = self._get_default_schema()

        table = bigquery.Table(table_ref, schema=schema)

        # Configurar particionamento
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field
        )

        # Criar tabela
        table = self.client.create_table(table)
        print(f"Tabela particionada {table_ref} criada com sucesso")

    def get_table_info(self, table_id: str) -> Dict[str, Any]:
        """
        Obtém informações sobre uma tabela.

        Args:
            table_id: ID da tabela

        Returns:
            Dicionário com informações da tabela

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> info = writer.get_table_info('ga4_daily_report')
            >>> print(f"Total de linhas: {info['num_rows']}")
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        table = self.client.get_table(table_ref)

        return {
            "table_id": table.table_id,
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "created": table.created.isoformat() if table.created else None,
            "modified": table.modified.isoformat() if table.modified else None,
            "schema": [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode
                }
                for field in table.schema
            ]
        }

    def delete_table(self, table_id: str) -> None:
        """
        Deleta uma tabela.

        Args:
            table_id: ID da tabela a ser deletada

        Examples:
            >>> writer = BigQueryWriter('my-project')
            >>> writer.delete_table('ga4_test_table')
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        self.client.delete_table(table_ref, not_found_ok=True)
        print(f"Tabela {table_ref} deletada com sucesso")

    def __repr__(self) -> str:
        return f"BigQueryWriter(project='{self.project_id}', dataset='{self.dataset_id}')"
