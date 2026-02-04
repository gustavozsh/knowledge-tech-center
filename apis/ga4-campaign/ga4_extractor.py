"""
Modulo de Extracao de Dados do Google Analytics 4.

Este modulo contem funcoes para extrair dados do GA4 usando a Data API v1beta.
Baseado nos exemplos do repositorio:
https://github.com/googleanalytics/python-docs-samples/tree/main/google-analytics-data
"""

import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz

from config import config
from schemas import DIMENSION_SCHEMAS, TableSchema, get_schema, list_available_dimensions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def camel_to_snake(name: str) -> str:
    """
    Converte camelCase para snake_case.

    Args:
        name: String em camelCase

    Returns:
        String em snake_case
    """
    # Trata casos especiais como 'ID' no meio da string
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def get_date_range(days_back: int = 1, timezone: str = None) -> tuple:
    """
    Calcula o range de datas para extracao.

    Args:
        days_back: Quantos dias atras (padrao: 1 = ontem)
        timezone: Timezone para calculo

    Returns:
        Tupla (start_date, end_date) no formato YYYY-MM-DD
    """
    tz_str = timezone or config.ga4.timezone
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)

    target_date = now - timedelta(days=days_back)
    date_str = target_date.strftime("%Y-%m-%d")

    return date_str, date_str


def generate_id() -> str:
    """Gera um UUID unico para usar como ID."""
    return str(uuid.uuid4())


def generate_session_key(property_id: str, date: str) -> str:
    """
    Gera a chave de sessao para relacionar tabelas.

    Args:
        property_id: ID da propriedade GA4
        date: Data no formato YYYY-MM-DD

    Returns:
        Chave de sessao no formato "property_id_date"
    """
    clean_property_id = property_id.replace("properties/", "")
    return f"{clean_property_id}_{date}"


def run_report(
    ga4_client,
    property_id: str,
    dimensions: List[str],
    metrics: List[str],
    start_date: str,
    end_date: str,
    limit: int = 100000
) -> List[Dict[str, Any]]:
    """
    Executa um relatorio no GA4.

    Args:
        ga4_client: Cliente GA4 BetaAnalyticsDataClient
        property_id: ID da propriedade GA4 (ex: "123456789" ou "properties/123456789")
        dimensions: Lista de dimensoes
        metrics: Lista de metricas
        start_date: Data de inicio (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        limit: Limite de linhas

    Returns:
        Lista de dicionarios com os dados extraidos
    """
    from google.analytics.data_v1beta.types import (
        RunReportRequest,
        Dimension,
        Metric,
        DateRange
    )

    # Garantir formato correto do property_id
    if not property_id.startswith("properties/"):
        property_id = f"properties/{property_id}"

    # Filtrar dimensoes customizadas (que contem ':')
    valid_dimensions = [d for d in dimensions if ':' not in d]

    logger.info(f"Executando relatorio GA4 para {property_id}")
    logger.info(f"  Periodo: {start_date} a {end_date}")
    logger.info(f"  Dimensoes: {valid_dimensions}")
    logger.info(f"  Metricas: {metrics}")

    # Construir request
    request = RunReportRequest(
        property=property_id,
        dimensions=[Dimension(name=d) for d in valid_dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit
    )

    # Executar
    try:
        response = ga4_client.run_report(request)
    except Exception as e:
        logger.error(f"Erro ao executar relatorio: {e}")
        raise

    # Processar resposta
    rows = []

    for row in response.rows:
        row_data = {}

        # Adicionar dimensoes
        for i, dim_value in enumerate(row.dimension_values):
            dim_name = valid_dimensions[i]
            # Converter para snake_case
            field_name = camel_to_snake(dim_name)
            row_data[field_name] = dim_value.value

        # Adicionar metricas
        for i, metric_value in enumerate(row.metric_values):
            metric_name = metrics[i]
            # Converter para snake_case
            field_name = camel_to_snake(metric_name)

            # Converter para numero se possivel
            try:
                if "." in metric_value.value:
                    row_data[field_name] = float(metric_value.value)
                else:
                    row_data[field_name] = int(metric_value.value)
            except ValueError:
                row_data[field_name] = metric_value.value

        rows.append(row_data)

    logger.info(f"  {len(rows)} linhas retornadas")
    return rows


def extract_dimension(
    ga4_client,
    property_id: str,
    dimension_key: str,
    start_date: str,
    end_date: str,
    dataset_id: Optional[str] = None,
    table_prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extrai dados de uma dimensao especifica.

    Args:
        ga4_client: Cliente GA4
        property_id: ID da propriedade GA4
        dimension_key: Chave da dimensao (ex: CAMPAIGN, SOURCE_MEDIUM)
        start_date: Data de inicio (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        dataset_id: ID do dataset BigQuery (opcional, para customizar)
        table_prefix: Prefixo customizado para nome da tabela

    Returns:
        Dicionario com os dados extraidos e metadados
    """
    schema = get_schema(dimension_key)
    clean_property_id = property_id.replace("properties/", "")

    logger.info(f"Extraindo: {schema.description}")

    # Executar relatorio
    raw_data = run_report(
        ga4_client=ga4_client,
        property_id=property_id,
        dimensions=schema.dimensions,
        metrics=schema.metrics,
        start_date=start_date,
        end_date=end_date
    )

    # Processar dados adicionando campos base
    execution_time = datetime.utcnow().isoformat() + "Z"
    processed_data = []

    for row in raw_data:
        # Obter a data do registro
        row_date = row.get("date", start_date)

        # Adicionar campos base
        processed_row = {
            "id": generate_id(),
            "ga4_session_key": generate_session_key(clean_property_id, row_date),
            "property_id": clean_property_id,
            "date": row_date,
            "last_update": execution_time,
        }

        # Adicionar dados extraidos
        processed_row.update(row)
        processed_data.append(processed_row)

    # Determinar nome da tabela
    table_name = schema.table_name
    if table_prefix:
        table_name = f"{table_prefix}_{schema.table_name}"

    return {
        "dimension_key": dimension_key,
        "table_name": table_name,
        "description": schema.description,
        "rows_count": len(processed_data),
        "data": processed_data,
        "period": {"start": start_date, "end": end_date},
        "property_id": clean_property_id,
        "extraction_time": execution_time
    }


def extract_all_dimensions(
    ga4_client,
    property_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    dimensions: Optional[List[str]] = None,
    table_prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extrai todas as dimensoes configuradas (ou um subconjunto).

    Args:
        ga4_client: Cliente GA4
        property_id: ID da propriedade GA4
        start_date: Data de inicio (opcional, usa D-1 se nao fornecido)
        end_date: Data de fim (opcional, usa D-1 se nao fornecido)
        dimensions: Lista de dimensoes a extrair (opcional, extrai todas se nao fornecido)
        table_prefix: Prefixo customizado para nomes de tabelas

    Returns:
        Dicionario com todos os relatorios extraidos
    """
    # Calcular datas se nao fornecidas
    if not start_date or not end_date:
        start_date, end_date = get_date_range()

    # Determinar quais dimensoes extrair
    dimensions_to_extract = dimensions or list_available_dimensions()

    logger.info("=" * 60)
    logger.info("EXTRACAO GA4 - TODAS AS DIMENSOES")
    logger.info(f"Property: {property_id}")
    logger.info(f"Periodo: {start_date} a {end_date}")
    logger.info(f"Dimensoes: {dimensions_to_extract}")
    logger.info("=" * 60)

    results = {
        "property_id": property_id,
        "period": {"start": start_date, "end": end_date},
        "extractions": {},
        "summary": {
            "total_dimensions": len(dimensions_to_extract),
            "successful": 0,
            "failed": 0,
            "total_rows": 0
        }
    }

    for dimension_key in dimensions_to_extract:
        try:
            extraction = extract_dimension(
                ga4_client=ga4_client,
                property_id=property_id,
                dimension_key=dimension_key,
                start_date=start_date,
                end_date=end_date,
                table_prefix=table_prefix
            )
            results["extractions"][dimension_key] = extraction
            results["summary"]["successful"] += 1
            results["summary"]["total_rows"] += extraction["rows_count"]

            logger.info(f"  {dimension_key}: {extraction['rows_count']} linhas")

        except Exception as e:
            logger.error(f"Erro ao extrair {dimension_key}: {e}")
            results["extractions"][dimension_key] = {
                "error": str(e),
                "dimension_key": dimension_key
            }
            results["summary"]["failed"] += 1

    logger.info("=" * 60)
    logger.info("EXTRACAO CONCLUIDA")
    logger.info(f"Dimensoes: {results['summary']['successful']}/{results['summary']['total_dimensions']}")
    logger.info(f"Total de linhas: {results['summary']['total_rows']}")
    logger.info("=" * 60)

    return results


def run_batch_report(
    ga4_client,
    property_id: str,
    reports: List[Dict[str, Any]],
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Executa multiplos relatorios em batch (ate 5 por vez).

    Args:
        ga4_client: Cliente GA4
        property_id: ID da propriedade GA4
        reports: Lista de dicionarios com {dimensions, metrics}
        start_date: Data de inicio
        end_date: Data de fim

    Returns:
        Lista de resultados dos relatorios
    """
    from google.analytics.data_v1beta.types import (
        BatchRunReportsRequest,
        RunReportRequest,
        Dimension,
        Metric,
        DateRange
    )

    # Garantir formato correto do property_id
    if not property_id.startswith("properties/"):
        property_id = f"properties/{property_id}"

    # GA4 permite no maximo 5 relatorios por batch
    batch_size = 5
    all_results = []

    for i in range(0, len(reports), batch_size):
        batch = reports[i:i + batch_size]

        requests = []
        for report in batch:
            # Filtrar dimensoes customizadas
            valid_dimensions = [d for d in report["dimensions"] if ':' not in d]

            req = RunReportRequest(
                property=property_id,
                dimensions=[Dimension(name=d) for d in valid_dimensions],
                metrics=[Metric(name=m) for m in report["metrics"]],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=100000
            )
            requests.append(req)

        batch_request = BatchRunReportsRequest(
            property=property_id,
            requests=requests
        )

        try:
            response = ga4_client.batch_run_reports(batch_request)

            for report_response in response.reports:
                rows = []
                dim_headers = [h.name for h in report_response.dimension_headers]
                metric_headers = [h.name for h in report_response.metric_headers]

                for row in report_response.rows:
                    row_data = {}

                    # Dimensoes
                    for j, dim_value in enumerate(row.dimension_values):
                        field_name = camel_to_snake(dim_headers[j])
                        row_data[field_name] = dim_value.value

                    # Metricas
                    for j, metric_value in enumerate(row.metric_values):
                        field_name = camel_to_snake(metric_headers[j])
                        try:
                            if "." in metric_value.value:
                                row_data[field_name] = float(metric_value.value)
                            else:
                                row_data[field_name] = int(metric_value.value)
                        except ValueError:
                            row_data[field_name] = metric_value.value

                    rows.append(row_data)

                all_results.append(rows)

        except Exception as e:
            logger.error(f"Erro no batch report: {e}")
            raise

    return all_results


def get_property_metadata(ga4_client, property_id: str) -> Dict[str, Any]:
    """
    Obtem metadados da propriedade GA4 (dimensoes e metricas disponiveis).

    Args:
        ga4_client: Cliente GA4
        property_id: ID da propriedade GA4

    Returns:
        Dicionario com metadados da propriedade
    """
    from google.analytics.data_v1beta.types import GetMetadataRequest

    # Garantir formato correto
    if not property_id.startswith("properties/"):
        property_id = f"properties/{property_id}"

    request = GetMetadataRequest(name=f"{property_id}/metadata")

    try:
        response = ga4_client.get_metadata(request)

        dimensions = [
            {
                "api_name": d.api_name,
                "ui_name": d.ui_name,
                "description": d.description,
                "category": d.category
            }
            for d in response.dimensions
        ]

        metrics = [
            {
                "api_name": m.api_name,
                "ui_name": m.ui_name,
                "description": m.description,
                "category": m.category,
                "type": m.type_.name
            }
            for m in response.metrics
        ]

        return {
            "property_id": property_id,
            "dimensions_count": len(dimensions),
            "metrics_count": len(metrics),
            "dimensions": dimensions,
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Erro ao obter metadados: {e}")
        raise
