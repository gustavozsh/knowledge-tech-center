"""
API de Extracao de Dados do Google Analytics 4 - Campanhas.

Esta API extrai dados de campanhas do GA4 e carrega no BigQuery.
Projetada para execucao no Google Cloud Run.

Endpoints:
    GET  /                  - Health check
    GET  /dimensions        - Lista dimensoes disponiveis
    GET  /metadata          - Obtem metadados da propriedade GA4
    POST /init-tables       - Inicializa tabelas no BigQuery
    POST /extract           - Extrai todas as dimensoes
    POST /extract/<key>     - Extrai uma dimensao especifica

Para executar localmente:
    python main.py

Para deploy no Cloud Run:
    A funcao principal e `main()` que inicia o servidor Flask.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify

from config import config
from gcp_connection import connect_gcp, gcp_connection
from schemas import list_available_dimensions, get_schema, DIMENSION_SCHEMAS
from bigquery_client import BigQueryClient, initialize_tables
from ga4_extractor import (
    extract_dimension,
    extract_all_dimensions,
    get_date_range,
    get_property_metadata
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)


# =============================================================================
# FUNCOES AUXILIARES
# =============================================================================

def get_gcp_clients():
    """Obtem os clientes GCP, conectando se necessario."""
    if not gcp_connection.is_connected:
        connect_gcp()
    return gcp_connection.get_all_clients()


def run_full_extraction(
    property_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    dimensions: Optional[list] = None,
    dataset_id: Optional[str] = None,
    table_prefix: Optional[str] = None,
    init_tables: bool = True
) -> Dict[str, Any]:
    """
    Executa a extracao completa de dados do GA4.

    Esta funcao orquestra todo o processo:
    1. Conecta ao GCP
    2. Inicializa tabelas no BigQuery (opcional)
    3. Extrai dados do GA4
    4. Carrega no BigQuery

    Args:
        property_id: ID da propriedade GA4
        start_date: Data de inicio (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        dimensions: Lista de dimensoes a extrair (todas se None)
        dataset_id: ID do dataset BigQuery (usa config se None)
        table_prefix: Prefixo customizado para nomes de tabelas
        init_tables: Se True, inicializa tabelas antes da extracao

    Returns:
        Resultado da extracao e carga
    """
    logger.info("=" * 60)
    logger.info("INICIANDO EXTRACAO GA4 CAMPAIGN")
    logger.info("=" * 60)

    # 1. CONECTAR AO GCP
    logger.info("Passo 1: Conectando ao GCP...")
    try:
        clients = get_gcp_clients()
        bq_client = clients["bigquery"]
        ga4_client = clients["ga4"]
        project_id = clients["project_id"]
    except Exception as e:
        logger.error(f"Falha na conexao GCP: {e}")
        return {
            "status": "error",
            "step": "gcp_connection",
            "message": str(e)
        }

    # 2. INICIALIZAR TABELAS (opcional)
    ds_id = dataset_id or config.bigquery.dataset_id
    if init_tables:
        logger.info("Passo 2: Inicializando tabelas no BigQuery...")
        try:
            bq_helper = BigQueryClient(bq_client, project_id, ds_id)
            bq_helper.create_all_tables()
        except Exception as e:
            logger.error(f"Falha ao inicializar tabelas: {e}")
            return {
                "status": "error",
                "step": "init_tables",
                "message": str(e)
            }

    # 3. CALCULAR DATAS
    if not start_date or not end_date:
        start_date, end_date = get_date_range()
    logger.info(f"Periodo: {start_date} a {end_date}")

    # 4. EXTRAIR DADOS DO GA4
    logger.info("Passo 3: Extraindo dados do GA4...")
    try:
        extraction_results = extract_all_dimensions(
            ga4_client=ga4_client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            table_prefix=table_prefix
        )
    except Exception as e:
        logger.error(f"Falha na extracao: {e}")
        return {
            "status": "error",
            "step": "extraction",
            "message": str(e)
        }

    # 5. CARREGAR NO BIGQUERY
    logger.info("Passo 4: Carregando dados no BigQuery...")
    load_results = {
        "successful": 0,
        "failed": 0,
        "details": {}
    }

    bq_helper = BigQueryClient(bq_client, project_id, ds_id)

    for dim_key, extraction in extraction_results["extractions"].items():
        if "error" in extraction:
            load_results["details"][dim_key] = {"status": "skipped", "reason": extraction["error"]}
            continue

        try:
            result = bq_helper.load_report(
                table_name=extraction["table_name"],
                data=extraction["data"],
                replace_partition=True
            )
            load_results["details"][dim_key] = result

            if result.get("status") == "success":
                load_results["successful"] += 1
            else:
                load_results["failed"] += 1

        except Exception as e:
            logger.error(f"Erro ao carregar {dim_key}: {e}")
            load_results["details"][dim_key] = {"status": "error", "message": str(e)}
            load_results["failed"] += 1

    # 6. RESULTADO FINAL
    logger.info("=" * 60)
    logger.info("EXTRACAO CONCLUIDA")
    logger.info("=" * 60)

    return {
        "status": "success",
        "property_id": property_id,
        "period": {"start": start_date, "end": end_date},
        "extraction": extraction_results["summary"],
        "load": {
            "successful": load_results["successful"],
            "failed": load_results["failed"],
            "total": load_results["successful"] + load_results["failed"]
        }
    }


# =============================================================================
# ENDPOINTS DA API
# =============================================================================

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "GA4 Campaign Extractor API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "config": {
            "project_id": config.gcp.project_id or "(not set)",
            "dataset_id": config.bigquery.dataset_id,
            "ga4_property_id": config.ga4.property_id or "(not set)"
        }
    })


@app.route("/dimensions", methods=["GET"])
def list_dimensions():
    """Lista todas as dimensoes disponiveis para extracao."""
    dimensions = list_available_dimensions()
    details = {}

    for dim_key in dimensions:
        schema = get_schema(dim_key)
        details[dim_key] = {
            "table_name": schema.table_name,
            "description": schema.description,
            "dimensions_count": len(schema.dimensions),
            "metrics_count": len(schema.metrics)
        }

    return jsonify({
        "available_dimensions": dimensions,
        "count": len(dimensions),
        "details": details
    })


@app.route("/metadata", methods=["GET", "POST"])
def get_metadata():
    """
    Obtem metadados da propriedade GA4 (dimensoes e metricas disponiveis).

    Query params ou body:
        property_id: ID da propriedade GA4
    """
    if request.method == "POST":
        data = request.get_json() or {}
        property_id = data.get("property_id")
    else:
        property_id = request.args.get("property_id")

    property_id = property_id or config.ga4.property_id

    if not property_id:
        return jsonify({
            "status": "error",
            "message": "property_id e obrigatorio"
        }), 400

    try:
        clients = get_gcp_clients()
        metadata = get_property_metadata(clients["ga4"], property_id)
        return jsonify({
            "status": "success",
            "metadata": metadata
        })
    except Exception as e:
        logger.error(f"Erro ao obter metadados: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/init-tables", methods=["POST"])
def init_tables():
    """
    Inicializa todas as tabelas no BigQuery.

    Body (opcional):
        {
            "dataset_id": "CUSTOM_DATASET"
        }
    """
    data = request.get_json() or {}
    dataset_id = data.get("dataset_id")

    try:
        clients = get_gcp_clients()
        results = initialize_tables(
            clients["bigquery"],
            clients["project_id"],
            dataset_id
        )

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        return jsonify({
            "status": "success",
            "message": f"Tabelas criadas: {success_count}/{total_count}",
            "details": results
        })
    except Exception as e:
        logger.error(f"Erro ao inicializar tabelas: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/extract", methods=["POST"])
def extract_all():
    """
    Extrai todas as dimensoes do GA4 e carrega no BigQuery.

    Body:
        {
            "property_id": "123456789",        // obrigatorio
            "start_date": "2024-01-01",        // opcional (default: D-1)
            "end_date": "2024-01-01",          // opcional (default: D-1)
            "dimensions": ["CAMPAIGN", "..."], // opcional (default: todas)
            "dataset_id": "CUSTOM_DATASET",    // opcional
            "table_prefix": "PREFIX",          // opcional
            "init_tables": true                // opcional (default: true)
        }
    """
    data = request.get_json() or {}

    property_id = data.get("property_id") or config.ga4.property_id
    if not property_id:
        return jsonify({
            "status": "error",
            "message": "property_id e obrigatorio"
        }), 400

    try:
        result = run_full_extraction(
            property_id=property_id,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            dimensions=data.get("dimensions"),
            dataset_id=data.get("dataset_id"),
            table_prefix=data.get("table_prefix"),
            init_tables=data.get("init_tables", True)
        )

        status_code = 200 if result.get("status") == "success" else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Erro na extracao: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/extract/<dimension_key>", methods=["POST"])
def extract_single(dimension_key: str):
    """
    Extrai uma dimensao especifica do GA4.

    Args:
        dimension_key: Chave da dimensao (ex: CAMPAIGN, SOURCE_MEDIUM)

    Body:
        {
            "property_id": "123456789",     // obrigatorio
            "start_date": "2024-01-01",     // opcional
            "end_date": "2024-01-01",       // opcional
            "dataset_id": "CUSTOM_DATASET", // opcional
            "table_prefix": "PREFIX"        // opcional
        }
    """
    data = request.get_json() or {}

    property_id = data.get("property_id") or config.ga4.property_id
    if not property_id:
        return jsonify({
            "status": "error",
            "message": "property_id e obrigatorio"
        }), 400

    dimension_key = dimension_key.upper()
    available = list_available_dimensions()

    if dimension_key not in available:
        return jsonify({
            "status": "error",
            "message": f"Dimensao nao encontrada: {dimension_key}",
            "available": available
        }), 404

    try:
        clients = get_gcp_clients()
        bq_client = clients["bigquery"]
        ga4_client = clients["ga4"]
        project_id = clients["project_id"]
        dataset_id = data.get("dataset_id") or config.bigquery.dataset_id

        # Calcular datas
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if not start_date or not end_date:
            start_date, end_date = get_date_range()

        # Garantir que a tabela existe
        schema = get_schema(dimension_key)
        bq_helper = BigQueryClient(bq_client, project_id, dataset_id)
        bq_helper.ensure_table_exists(schema)

        # Extrair dados
        extraction = extract_dimension(
            ga4_client=ga4_client,
            property_id=property_id,
            dimension_key=dimension_key,
            start_date=start_date,
            end_date=end_date,
            table_prefix=data.get("table_prefix")
        )

        # Carregar no BigQuery
        load_result = bq_helper.load_report(
            table_name=extraction["table_name"],
            data=extraction["data"],
            replace_partition=True
        )

        return jsonify({
            "status": "success",
            "dimension": dimension_key,
            "property_id": property_id,
            "period": {"start": start_date, "end": end_date},
            "extraction": {
                "rows": extraction["rows_count"],
                "table": extraction["table_name"]
            },
            "load": load_result
        })

    except Exception as e:
        logger.error(f"Erro ao extrair {dimension_key}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =============================================================================
# FUNCAO PRINCIPAL
# =============================================================================

def main():
    """Funcao principal para iniciar o servidor ou executar via CLI."""

    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--init-tables":
            # Modo de inicializacao de tabelas
            logger.info("Inicializando tabelas no BigQuery...")
            clients = get_gcp_clients()
            results = initialize_tables(
                clients["bigquery"],
                clients["project_id"]
            )
            success = sum(1 for v in results.values() if v)
            print(f"Tabelas criadas: {success}/{len(results)}")
            sys.exit(0 if success == len(results) else 1)

        elif sys.argv[1] == "--extract":
            # Modo de extracao via CLI
            if len(sys.argv) < 3:
                print("Uso: python main.py --extract <property_id> [start_date] [end_date]")
                sys.exit(1)

            property_id = sys.argv[2]
            start_date = sys.argv[3] if len(sys.argv) > 3 else None
            end_date = sys.argv[4] if len(sys.argv) > 4 else None

            result = run_full_extraction(property_id, start_date, end_date)
            print(result)
            sys.exit(0 if result.get("status") == "success" else 1)

        elif sys.argv[1] == "--help":
            print("""
GA4 Campaign Extractor API

Uso:
    python main.py                                    # Inicia servidor Flask
    python main.py --init-tables                      # Inicializa tabelas no BigQuery
    python main.py --extract <property_id> [start] [end]  # Extrai dados via CLI
    python main.py --help                             # Mostra esta ajuda

Variaveis de ambiente:
    GCP_PROJECT_ID          - ID do projeto GCP
    GA4_PROPERTY_ID         - ID da propriedade GA4
    BQ_DATASET_ID           - ID do dataset BigQuery (default: GA4_CAMPAIGN)
    GOOGLE_APPLICATION_CREDENTIALS - Caminho para credenciais
    PORT                    - Porta do servidor (default: 8080)
    DEBUG                   - Modo debug (default: false)
            """)
            sys.exit(0)

    # Modo servidor
    port = config.port
    debug = config.debug

    logger.info(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
