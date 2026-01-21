"""
API de Extração de Dados do Google Analytics 4 para BigQuery.

Este é o arquivo principal da API, que expõe endpoints REST
para extrair dados do GA4 e carregá-los no BigQuery.

Autor: Manus AI
Data: Janeiro de 2026
Versão: 2.0.0

Para executar localmente:
    python main.py

Para testar autenticação:
    python main.py --test

Para extrair via CLI:
    python main.py --extract <property_id> [start_date] [end_date]

Para deploy no Cloud Run:
    A função principal é `main()` que inicia o servidor Flask.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)


# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

class Config:
    """Configurações da API."""
    PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "cadastra-yduqs-uat")
    DATASET_ID = os.environ.get("BQ_DATASET_ID", "RAW")
    CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)
    USE_SECRET_MANAGER = os.environ.get("USE_SECRET_MANAGER", "true").lower() == "true"


# =============================================================================
# FUNÇÕES PRINCIPAIS
# =============================================================================

def run_extraction(
    property_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    load_to_bigquery: bool = True
) -> Dict[str, Any]:
    """
    Executa a extração completa de dados do GA4.
    
    Esta é a função principal que orquestra todo o processo:
    1. Autentica no GCP
    2. Extrai dados do GA4
    3. Carrega no BigQuery (opcional)
    
    Args:
        property_id: ID da propriedade GA4
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        load_to_bigquery: Se True, carrega os dados no BigQuery
        
    Returns:
        Resultado da extração e carga
    """
    # Importar módulos locais
    from auth import initialize_all_clients
    from ga4 import extract_all_reports, get_date_range
    from bigquery import load_all_reports_to_bigquery
    
    logger.info("=" * 60)
    logger.info("INICIANDO EXTRAÇÃO GA4")
    logger.info("=" * 60)
    
    # 1. AUTENTICAÇÃO
    logger.info("Passo 1: Autenticando no GCP...")
    try:
        clients = initialize_all_clients(
            project_id=Config.PROJECT_ID,
            credentials_path=Config.CREDENTIALS_PATH,
            use_secret_manager=Config.USE_SECRET_MANAGER
        )
    except Exception as e:
        logger.error(f"Falha na autenticação: {e}")
        return {
            "status": "error",
            "step": "authentication",
            "message": str(e)
        }
    
    # 2. CALCULAR DATAS
    if not start_date or not end_date:
        start_date, end_date = get_date_range()
    
    logger.info(f"Período: {start_date} a {end_date}")
    
    # 3. EXTRAÇÃO DO GA4
    logger.info("Passo 2: Extraindo dados do GA4...")
    try:
        extraction_results = extract_all_reports(
            ga4_client=clients["ga4"],
            property_id=property_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Falha na extração: {e}")
        return {
            "status": "error",
            "step": "extraction",
            "message": str(e)
        }
    
    # 4. CARGA NO BIGQUERY
    if load_to_bigquery:
        logger.info("Passo 3: Carregando dados no BigQuery...")
        try:
            load_results = load_all_reports_to_bigquery(
                bq_client=clients["bigquery"],
                project_id=Config.PROJECT_ID,
                dataset_id=Config.DATASET_ID,
                extraction_results=extraction_results
            )
        except Exception as e:
            logger.error(f"Falha na carga: {e}")
            return {
                "status": "error",
                "step": "load",
                "message": str(e),
                "extraction": extraction_results["summary"]
            }
    else:
        load_results = {"summary": {"message": "Carga no BigQuery desabilitada"}}
    
    # 5. RESULTADO FINAL
    logger.info("=" * 60)
    logger.info("EXTRAÇÃO CONCLUÍDA COM SUCESSO")
    logger.info("=" * 60)
    
    return {
        "status": "success",
        "property_id": property_id,
        "period": {"start": start_date, "end": end_date},
        "extraction": extraction_results["summary"],
        "load": load_results.get("summary", {})
    }


# =============================================================================
# ENDPOINTS DA API
# =============================================================================

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "GA4 API Extractor",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "project_id": Config.PROJECT_ID,
            "dataset_id": Config.DATASET_ID
        }
    })


@app.route("/test-auth", methods=["GET"])
def test_auth():
    """Testa a autenticação no GCP."""
    from auth import test_authentication
    
    success = test_authentication(Config.CREDENTIALS_PATH)
    
    return jsonify({
        "status": "success" if success else "error",
        "message": "Autenticação OK" if success else "Falha na autenticação"
    })


@app.route("/reports", methods=["GET"])
def list_reports():
    """Lista todos os relatórios disponíveis."""
    from ga4 import list_available_reports
    
    return jsonify(list_available_reports())


@app.route("/extract", methods=["POST"])
def extract():
    """
    Extrai dados do GA4 e carrega no BigQuery.
    
    Request Body:
        {
            "property_id": "123456789",
            "start_date": "2024-01-01",  // opcional
            "end_date": "2024-01-01",    // opcional
            "load_to_bigquery": true     // opcional, padrão true
        }
    """
    data = request.get_json() or {}
    
    property_id = data.get("property_id")
    if not property_id:
        return jsonify({
            "status": "error",
            "message": "property_id é obrigatório"
        }), 400
    
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    load_to_bigquery = data.get("load_to_bigquery", True)
    
    try:
        result = run_extraction(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            load_to_bigquery=load_to_bigquery
        )
        
        status_code = 200 if result.get("status") == "success" else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Erro na extração: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/extract/dimension/<report_key>", methods=["POST"])
def extract_dimension(report_key: str):
    """
    Extrai um relatório de dimensão específico.
    
    Args:
        report_key: Chave do relatório (USUARIO, GEOGRAFICA, etc.)
    """
    from auth import initialize_all_clients
    from ga4 import extract_dimension_report, get_date_range, DIMENSION_REPORTS
    from bigquery import load_report_to_bigquery
    
    data = request.get_json() or {}
    
    property_id = data.get("property_id")
    if not property_id:
        return jsonify({"status": "error", "message": "property_id é obrigatório"}), 400
    
    report_key = report_key.upper()
    if report_key not in DIMENSION_REPORTS:
        return jsonify({
            "status": "error",
            "message": f"Relatório não encontrado: {report_key}",
            "available": list(DIMENSION_REPORTS.keys())
        }), 404
    
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if not start_date or not end_date:
        start_date, end_date = get_date_range()
    
    try:
        clients = initialize_all_clients(
            project_id=Config.PROJECT_ID,
            credentials_path=Config.CREDENTIALS_PATH,
            use_secret_manager=Config.USE_SECRET_MANAGER
        )
        
        report = extract_dimension_report(
            clients["ga4"], property_id, report_key, start_date, end_date
        )
        
        load_result = load_report_to_bigquery(
            clients["bigquery"], Config.PROJECT_ID, Config.DATASET_ID, report
        )
        
        return jsonify({
            "status": "success",
            "report": report_key,
            "extraction": {"rows": report["rows_count"]},
            "load": load_result
        })
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/extract/metric/<report_key>", methods=["POST"])
def extract_metric(report_key: str):
    """
    Extrai um relatório de métrica específico.
    
    Args:
        report_key: Chave do relatório (USUARIOS, SESSAO, etc.)
    """
    from auth import initialize_all_clients
    from ga4 import extract_metric_report, get_date_range, METRIC_REPORTS
    from bigquery import load_report_to_bigquery
    
    data = request.get_json() or {}
    
    property_id = data.get("property_id")
    if not property_id:
        return jsonify({"status": "error", "message": "property_id é obrigatório"}), 400
    
    report_key = report_key.upper()
    if report_key not in METRIC_REPORTS:
        return jsonify({
            "status": "error",
            "message": f"Relatório não encontrado: {report_key}",
            "available": list(METRIC_REPORTS.keys())
        }), 404
    
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if not start_date or not end_date:
        start_date, end_date = get_date_range()
    
    try:
        clients = initialize_all_clients(
            project_id=Config.PROJECT_ID,
            credentials_path=Config.CREDENTIALS_PATH,
            use_secret_manager=Config.USE_SECRET_MANAGER
        )
        
        report = extract_metric_report(
            clients["ga4"], property_id, report_key, start_date, end_date
        )
        
        load_result = load_report_to_bigquery(
            clients["bigquery"], Config.PROJECT_ID, Config.DATASET_ID, report
        )
        
        return jsonify({
            "status": "success",
            "report": report_key,
            "extraction": {"rows": report["rows_count"]},
            "load": load_result
        })
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal para iniciar o servidor ou executar testes."""
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Modo de teste
            logger.info("Executando teste de autenticação...")
            from auth import test_authentication
            success = test_authentication(Config.CREDENTIALS_PATH)
            sys.exit(0 if success else 1)
        
        elif sys.argv[1] == "--extract":
            # Modo de extração via CLI
            if len(sys.argv) < 3:
                print("Uso: python main.py --extract <property_id> [start_date] [end_date]")
                sys.exit(1)
            
            property_id = sys.argv[2]
            start_date = sys.argv[3] if len(sys.argv) > 3 else None
            end_date = sys.argv[4] if len(sys.argv) > 4 else None
            
            result = run_extraction(property_id, start_date, end_date)
            print(result)
            sys.exit(0 if result.get("status") == "success" else 1)
    
    # Modo servidor
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
