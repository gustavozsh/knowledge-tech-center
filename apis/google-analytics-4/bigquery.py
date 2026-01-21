"""
Módulo de Escrita no Google BigQuery.

Este módulo contém todas as funções para criar tabelas e inserir dados
no BigQuery.

Autor: Manus AI
Data: Janeiro de 2026
Versão: 2.0.0
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÃO DO BIGQUERY
# =============================================================================

DATASET_ID = "RAW"

# Schema base para todas as tabelas
BASE_SCHEMA = [
    {"name": "date", "type": "DATE", "description": "Data do registro"},
    {"name": "property_id", "type": "STRING", "description": "ID da propriedade GA4"},
    {"name": "extraction_timestamp", "type": "TIMESTAMP", "description": "Timestamp da extração"},
]


# =============================================================================
# FUNÇÕES DE TABELA
# =============================================================================

def table_exists(bq_client, project_id: str, dataset_id: str, table_name: str) -> bool:
    """
    Verifica se uma tabela existe no BigQuery.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        table_name: Nome da tabela
        
    Returns:
        True se a tabela existe
    """
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    
    try:
        bq_client.get_table(table_ref)
        return True
    except Exception:
        return False


def create_table(
    bq_client,
    project_id: str,
    dataset_id: str,
    table_name: str,
    schema: List[Dict[str, str]],
    description: str = "",
    partition_field: str = "date"
) -> bool:
    """
    Cria uma tabela no BigQuery.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        table_name: Nome da tabela
        schema: Schema da tabela
        description: Descrição da tabela
        partition_field: Campo para particionamento
        
    Returns:
        True se a tabela foi criada com sucesso
    """
    from google.cloud import bigquery
    
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    
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
    
    # Configurar particionamento
    if partition_field:
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field
        )
    
    try:
        bq_client.create_table(table)
        logger.info(f"✓ Tabela criada: {table_ref}")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao criar tabela {table_ref}: {e}")
        return False


def ensure_table_exists(
    bq_client,
    project_id: str,
    dataset_id: str,
    table_name: str,
    schema: List[Dict[str, str]],
    description: str = ""
) -> bool:
    """
    Garante que uma tabela existe, criando-a se necessário.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        table_name: Nome da tabela
        schema: Schema da tabela
        description: Descrição da tabela
        
    Returns:
        True se a tabela existe ou foi criada
    """
    if table_exists(bq_client, project_id, dataset_id, table_name):
        logger.info(f"Tabela já existe: {table_name}")
        return True
    
    return create_table(
        bq_client, project_id, dataset_id, table_name, schema, description
    )


# =============================================================================
# FUNÇÕES DE INSERÇÃO
# =============================================================================

def insert_rows(
    bq_client,
    project_id: str,
    dataset_id: str,
    table_name: str,
    rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Insere linhas em uma tabela do BigQuery.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        table_name: Nome da tabela
        rows: Lista de dicionários com os dados
        
    Returns:
        Resultado da inserção
    """
    if not rows:
        logger.warning(f"Nenhuma linha para inserir em {table_name}")
        return {
            "status": "warning",
            "message": "Nenhuma linha para inserir",
            "rows_inserted": 0
        }
    
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    
    try:
        errors = bq_client.insert_rows_json(table_ref, rows)
        
        if errors:
            logger.error(f"Erros ao inserir dados em {table_name}: {errors}")
            return {
                "status": "error",
                "message": f"Erros na inserção: {errors}",
                "rows_inserted": 0,
                "errors": errors
            }
        
        logger.info(f"✓ Inseridas {len(rows)} linhas em {table_name}")
        return {
            "status": "success",
            "message": f"Inseridas {len(rows)} linhas",
            "rows_inserted": len(rows)
        }
    except Exception as e:
        logger.error(f"✗ Erro ao inserir dados em {table_name}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "rows_inserted": 0
        }


def delete_partition(
    bq_client,
    project_id: str,
    dataset_id: str,
    table_name: str,
    partition_date: str
) -> bool:
    """
    Deleta uma partição específica de uma tabela.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        table_name: Nome da tabela
        partition_date: Data da partição (formato YYYY-MM-DD)
        
    Returns:
        True se a partição foi deletada
    """
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    
    query = f"""
    DELETE FROM `{table_ref}`
    WHERE date = '{partition_date}'
    """
    
    try:
        job = bq_client.query(query)
        job.result()
        logger.info(f"✓ Partição {partition_date} deletada de {table_name}")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao deletar partição: {e}")
        return False


# =============================================================================
# FUNÇÕES DE CARGA DE RELATÓRIOS
# =============================================================================

def get_schema_for_report(report_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Gera o schema baseado nos dados do relatório.
    
    Args:
        report_data: Dados do relatório extraído
        
    Returns:
        Schema para a tabela
    """
    if not report_data.get("data"):
        return BASE_SCHEMA.copy()
    
    # Usar a primeira linha para inferir o schema
    sample_row = report_data["data"][0]
    schema = []
    
    for key, value in sample_row.items():
        field_type = "STRING"
        
        if key == "date":
            field_type = "DATE"
        elif key == "extraction_timestamp":
            field_type = "TIMESTAMP"
        elif isinstance(value, int):
            field_type = "INTEGER"
        elif isinstance(value, float):
            field_type = "FLOAT"
        elif isinstance(value, bool):
            field_type = "BOOLEAN"
        
        schema.append({
            "name": key,
            "type": field_type,
            "description": ""
        })
    
    return schema


def load_report_to_bigquery(
    bq_client,
    project_id: str,
    dataset_id: str,
    report_data: Dict[str, Any],
    replace_partition: bool = True
) -> Dict[str, Any]:
    """
    Carrega um relatório extraído no BigQuery.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        report_data: Dados do relatório (retorno de extract_*_report)
        replace_partition: Se True, deleta a partição antes de inserir
        
    Returns:
        Resultado da carga
    """
    table_name = report_data.get("table_name")
    data = report_data.get("data", [])
    
    if not table_name:
        return {"status": "error", "message": "table_name não encontrado no report_data"}
    
    if not data:
        return {
            "status": "warning",
            "message": "Nenhum dado para carregar",
            "table": table_name,
            "rows_inserted": 0
        }
    
    logger.info(f"Carregando {len(data)} linhas em {table_name}")
    
    # Gerar schema
    schema = get_schema_for_report(report_data)
    
    # Garantir que a tabela existe
    ensure_table_exists(
        bq_client, project_id, dataset_id, table_name, schema,
        description=report_data.get("report_name", "")
    )
    
    # Deletar partição existente se necessário
    if replace_partition and data:
        partition_date = data[0].get("date")
        if partition_date:
            delete_partition(bq_client, project_id, dataset_id, table_name, partition_date)
    
    # Inserir dados
    result = insert_rows(bq_client, project_id, dataset_id, table_name, data)
    result["table"] = table_name
    
    return result


def load_all_reports_to_bigquery(
    bq_client,
    project_id: str,
    dataset_id: str,
    extraction_results: Dict[str, Any],
    replace_partition: bool = True
) -> Dict[str, Any]:
    """
    Carrega todos os relatórios extraídos no BigQuery.
    
    Args:
        bq_client: Cliente do BigQuery
        project_id: ID do projeto
        dataset_id: ID do dataset
        extraction_results: Resultado de extract_all_reports
        replace_partition: Se True, deleta a partição antes de inserir
        
    Returns:
        Resultado consolidado da carga
    """
    logger.info("=" * 50)
    logger.info("CARREGANDO RELATÓRIOS NO BIGQUERY")
    logger.info("=" * 50)
    
    results = {
        "dimension_loads": {},
        "metric_loads": {},
        "summary": {
            "total_tables": 0,
            "successful": 0,
            "failed": 0,
            "total_rows": 0
        }
    }
    
    # Carregar relatórios de dimensão
    for key, report in extraction_results.get("dimensions", {}).items():
        if "error" in report:
            results["dimension_loads"][key] = {"status": "skipped", "reason": report["error"]}
            continue
        
        try:
            load_result = load_report_to_bigquery(
                bq_client, project_id, dataset_id, report, replace_partition
            )
            results["dimension_loads"][key] = load_result
            
            if load_result.get("status") == "success":
                results["summary"]["successful"] += 1
                results["summary"]["total_rows"] += load_result.get("rows_inserted", 0)
            else:
                results["summary"]["failed"] += 1
        except Exception as e:
            logger.error(f"Erro ao carregar {key}: {e}")
            results["dimension_loads"][key] = {"status": "error", "message": str(e)}
            results["summary"]["failed"] += 1
        
        results["summary"]["total_tables"] += 1
    
    # Carregar relatórios de métrica
    for key, report in extraction_results.get("metrics", {}).items():
        if "error" in report:
            results["metric_loads"][key] = {"status": "skipped", "reason": report["error"]}
            continue
        
        try:
            load_result = load_report_to_bigquery(
                bq_client, project_id, dataset_id, report, replace_partition
            )
            results["metric_loads"][key] = load_result
            
            if load_result.get("status") == "success":
                results["summary"]["successful"] += 1
                results["summary"]["total_rows"] += load_result.get("rows_inserted", 0)
            else:
                results["summary"]["failed"] += 1
        except Exception as e:
            logger.error(f"Erro ao carregar {key}: {e}")
            results["metric_loads"][key] = {"status": "error", "message": str(e)}
            results["summary"]["failed"] += 1
        
        results["summary"]["total_tables"] += 1
    
    logger.info("=" * 50)
    logger.info("CARGA CONCLUÍDA")
    logger.info(f"Tabelas: {results['summary']['successful']}/{results['summary']['total_tables']}")
    logger.info(f"Total de linhas: {results['summary']['total_rows']}")
    logger.info("=" * 50)
    
    return results
