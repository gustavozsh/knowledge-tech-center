"""
Entry point principal para Cloud Run
API REST para executar relatórios do Google Analytics 4 e salvar no BigQuery

Este módulo fornece endpoints REST para:
- Executar relatórios de dimensões específicas
- Executar relatórios de métricas específicas
- Executar todos os relatórios de uma vez
- Health check e status da API

Versão Python: 3.11+
Autor: Data Engineering Team
Data: Janeiro 2025
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials

from src.secret_manager import SecretManager
from src.ga4_client import GoogleAnalytics4
from src.bigquery_writer import BigQueryWriter
from src.report_manager import ReportManager
from src.models import DateRange, Dimension, Metric, RunReportRequest
from config import (
    GCPConfig,
    TableConfig,
    GA4Properties,
    DateConfig,
    CloudRunConfig,
    get_full_config
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
# FUNÇÕES AUXILIARES
# =============================================================================

def get_credentials(project_id: str = None, secret_id: str = None) -> Credentials:
    """
    Obtém as credenciais do Secret Manager.
    
    Args:
        project_id: ID do projeto GCP (usa config se não fornecido)
        secret_id: ID do secret (usa config se não fornecido)
        
    Returns:
        Objeto Credentials
    """
    project_id = project_id or GCPConfig.PROJECT_ID
    secret_id = secret_id or GCPConfig.SECRET_ID
    
    secret_manager = SecretManager()
    secret_value = secret_manager.access_secret_version(
        secret_id=secret_id,
        project_id=project_id
    )
    
    service_account_json = json.loads(secret_value)
    return Credentials.from_service_account_info(service_account_json)


def validate_request_json() -> tuple:
    """
    Valida se a requisição contém JSON válido.
    
    Returns:
        Tuple (is_valid, data_or_error)
    """
    if not request.is_json:
        return False, {'error': 'Request deve ser JSON'}
    return True, request.get_json()


# =============================================================================
# ENDPOINTS DE HEALTH CHECK E STATUS
# =============================================================================

@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON com status da API
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Google Analytics 4 API',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'project_id': GCPConfig.PROJECT_ID,
        'dataset_id': GCPConfig.DATASET_ID
    }), 200


@app.route('/config', methods=['GET'])
def get_config():
    """
    Retorna a configuração atual da API.
    
    Returns:
        JSON com configurações (sem dados sensíveis)
    """
    config = get_full_config()
    # Remover informações sensíveis
    config.pop('properties', None)
    
    return jsonify({
        'status': 'success',
        'config': config
    }), 200


@app.route('/tables', methods=['GET'])
def list_tables():
    """
    Lista todas as tabelas configuradas.
    
    Returns:
        JSON com lista de tabelas
    """
    return jsonify({
        'status': 'success',
        'tables': {
            'dimensions': list(TableConfig.TABLES_DIMENSIONS.keys()),
            'metrics': list(TableConfig.TABLES_METRICS.keys())
        },
        'total': len(TableConfig.get_all_tables())
    }), 200


@app.route('/reports/available', methods=['GET'])
def list_available_reports():
    """
    Lista todos os relatórios disponíveis.
    
    Returns:
        JSON com relatórios disponíveis
    """
    return jsonify({
        'status': 'success',
        'reports': ReportManager.get_available_reports()
    }), 200


# =============================================================================
# ENDPOINTS DE RELATÓRIOS DE DIMENSÕES
# =============================================================================

@app.route('/report/dimension/<table_name>', methods=['POST'])
def run_dimension_report(table_name: str):
    """
    Executa um relatório de dimensão específico.
    
    Path Parameters:
        table_name: Nome da tabela (ex: TB_001_GA4_DIM_USUARIO)
    
    Request Body (JSON):
    {
        "property_id": "123456789",
        "start_date": "yesterday",  // opcional, default: yesterday
        "end_date": "yesterday",    // opcional, default: yesterday
        "project_id": "...",        // opcional, usa config
        "secret_id": "..."          // opcional, usa config
    }
    
    Returns:
        JSON com status e informações do processamento
    """
    try:
        # Validar request
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        # Extrair parâmetros
        property_id = data.get('property_id')
        if not property_id:
            return jsonify({
                'error': 'property_id é obrigatório'
            }), 400
        
        start_date = data.get('start_date', DateConfig.DEFAULT_START_DATE)
        end_date = data.get('end_date', DateConfig.DEFAULT_END_DATE)
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        
        logger.info(f"Executando relatório de dimensão: {table_name} para property {property_id}")
        
        # Obter credenciais
        credentials = get_credentials(project_id, secret_id)
        
        # Criar ReportManager
        manager = ReportManager(
            credentials=credentials,
            property_id=property_id,
            project_id=project_id,
            dataset_id=GCPConfig.DATASET_ID
        )
        
        # Executar relatório
        result = manager.run_dimension_report(
            table_name=table_name,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Erro ao processar relatório: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/report/dimensions/all', methods=['POST'])
def run_all_dimension_reports():
    """
    Executa todos os relatórios de dimensão.
    
    Request Body (JSON):
    {
        "property_id": "123456789",
        "start_date": "yesterday",
        "end_date": "yesterday"
    }
    
    Returns:
        JSON com resultados de todos os relatórios
    """
    try:
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        property_id = data.get('property_id')
        if not property_id:
            return jsonify({'error': 'property_id é obrigatório'}), 400
        
        start_date = data.get('start_date', DateConfig.DEFAULT_START_DATE)
        end_date = data.get('end_date', DateConfig.DEFAULT_END_DATE)
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        
        logger.info(f"Executando todos os relatórios de dimensão para property {property_id}")
        
        credentials = get_credentials(project_id, secret_id)
        
        manager = ReportManager(
            credentials=credentials,
            property_id=property_id,
            project_id=project_id,
            dataset_id=GCPConfig.DATASET_ID
        )
        
        results = manager.run_all_dimension_reports(start_date, end_date)
        
        return jsonify({
            'status': 'success',
            'property_id': property_id,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar relatórios: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# =============================================================================
# ENDPOINTS DE RELATÓRIOS DE MÉTRICAS
# =============================================================================

@app.route('/report/metric/<table_name>', methods=['POST'])
def run_metric_report(table_name: str):
    """
    Executa um relatório de métrica específico.
    
    Path Parameters:
        table_name: Nome da tabela (ex: TB_008_GA4_MET_USUARIOS)
    
    Request Body (JSON):
    {
        "property_id": "123456789",
        "start_date": "yesterday",
        "end_date": "yesterday"
    }
    
    Returns:
        JSON com status e informações do processamento
    """
    try:
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        property_id = data.get('property_id')
        if not property_id:
            return jsonify({'error': 'property_id é obrigatório'}), 400
        
        start_date = data.get('start_date', DateConfig.DEFAULT_START_DATE)
        end_date = data.get('end_date', DateConfig.DEFAULT_END_DATE)
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        
        logger.info(f"Executando relatório de métrica: {table_name} para property {property_id}")
        
        credentials = get_credentials(project_id, secret_id)
        
        manager = ReportManager(
            credentials=credentials,
            property_id=property_id,
            project_id=project_id,
            dataset_id=GCPConfig.DATASET_ID
        )
        
        result = manager.run_metric_report(
            table_name=table_name,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Erro ao processar relatório: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/report/metrics/all', methods=['POST'])
def run_all_metric_reports():
    """
    Executa todos os relatórios de métrica.
    
    Request Body (JSON):
    {
        "property_id": "123456789",
        "start_date": "yesterday",
        "end_date": "yesterday"
    }
    
    Returns:
        JSON com resultados de todos os relatórios
    """
    try:
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        property_id = data.get('property_id')
        if not property_id:
            return jsonify({'error': 'property_id é obrigatório'}), 400
        
        start_date = data.get('start_date', DateConfig.DEFAULT_START_DATE)
        end_date = data.get('end_date', DateConfig.DEFAULT_END_DATE)
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        
        logger.info(f"Executando todos os relatórios de métrica para property {property_id}")
        
        credentials = get_credentials(project_id, secret_id)
        
        manager = ReportManager(
            credentials=credentials,
            property_id=property_id,
            project_id=project_id,
            dataset_id=GCPConfig.DATASET_ID
        )
        
        results = manager.run_all_metric_reports(start_date, end_date)
        
        return jsonify({
            'status': 'success',
            'property_id': property_id,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar relatórios: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# =============================================================================
# ENDPOINT PRINCIPAL - EXECUTAR TODOS OS RELATÓRIOS
# =============================================================================

@app.route('/report/all', methods=['POST'])
def run_all_reports():
    """
    Executa todos os relatórios (dimensões e métricas) para uma propriedade.
    
    Este é o endpoint principal para a carga diária de dados.
    
    Request Body (JSON):
    {
        "property_id": "123456789",
        "start_date": "yesterday",
        "end_date": "yesterday"
    }
    
    Returns:
        JSON com resultados de todos os relatórios
    """
    try:
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        property_id = data.get('property_id')
        if not property_id:
            return jsonify({'error': 'property_id é obrigatório'}), 400
        
        start_date = data.get('start_date', DateConfig.DEFAULT_START_DATE)
        end_date = data.get('end_date', DateConfig.DEFAULT_END_DATE)
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        
        logger.info(f"Executando TODOS os relatórios para property {property_id}")
        
        credentials = get_credentials(project_id, secret_id)
        
        manager = ReportManager(
            credentials=credentials,
            property_id=property_id,
            project_id=project_id,
            dataset_id=GCPConfig.DATASET_ID
        )
        
        results = manager.run_all_reports(start_date, end_date)
        
        return jsonify({
            'status': 'success',
            'property_id': property_id,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar relatórios: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/report/batch', methods=['POST'])
def run_batch_reports():
    """
    Executa relatórios para múltiplas propriedades.
    
    Request Body (JSON):
    {
        "property_ids": ["123456789", "987654321"],
        "start_date": "yesterday",
        "end_date": "yesterday"
    }
    
    Returns:
        JSON com resultados de todas as propriedades
    """
    try:
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        property_ids = data.get('property_ids', [])
        if not property_ids:
            return jsonify({'error': 'property_ids é obrigatório e deve ser uma lista'}), 400
        
        start_date = data.get('start_date', DateConfig.DEFAULT_START_DATE)
        end_date = data.get('end_date', DateConfig.DEFAULT_END_DATE)
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        
        logger.info(f"Executando relatórios em lote para {len(property_ids)} propriedades")
        
        credentials = get_credentials(project_id, secret_id)
        
        all_results = {}
        
        for property_id in property_ids:
            try:
                manager = ReportManager(
                    credentials=credentials,
                    property_id=property_id,
                    project_id=project_id,
                    dataset_id=GCPConfig.DATASET_ID
                )
                
                results = manager.run_all_reports(start_date, end_date)
                all_results[property_id] = {
                    'status': 'success',
                    'results': results
                }
                
            except Exception as e:
                logger.error(f"Erro ao processar property {property_id}: {str(e)}")
                all_results[property_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Calcular estatísticas gerais
        successful = sum(1 for r in all_results.values() if r['status'] == 'success')
        failed = len(all_results) - successful
        
        return jsonify({
            'status': 'success',
            'summary': {
                'total_properties': len(property_ids),
                'successful': successful,
                'failed': failed
            },
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'results': all_results
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar relatórios em lote: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# =============================================================================
# ENDPOINTS LEGADOS (MANTIDOS PARA COMPATIBILIDADE)
# =============================================================================

@app.route('/run-report', methods=['POST'])
def run_report_legacy():
    """
    Endpoint legado para executar relatório customizado do GA4.
    Mantido para compatibilidade com versões anteriores.
    
    Request Body (JSON):
    {
        "project_id": "your-project-id",
        "secret_id": "ga4-credentials",
        "property_id": "123456789",
        "bigquery_table": "ga4_daily_report",
        "bigquery_dataset": "RAW",
        "date_ranges": [
            {
                "start_date": "7daysAgo",
                "end_date": "today"
            }
        ],
        "dimensions": [
            {"name": "country"},
            {"name": "city"}
        ],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "sessions"}
        ],
        "limit": 10000
    }
    
    Returns:
        JSON com status e informações do processamento
    """
    try:
        is_valid, data = validate_request_json()
        if not is_valid:
            return jsonify(data), 400
        
        # Extrair parâmetros obrigatórios
        project_id = data.get('project_id', GCPConfig.PROJECT_ID)
        secret_id = data.get('secret_id', GCPConfig.SECRET_ID)
        property_id = data.get('property_id')
        bigquery_table = data.get('bigquery_table')
        
        if not all([property_id, bigquery_table]):
            return jsonify({
                'error': 'Parâmetros obrigatórios faltando',
                'required': ['property_id', 'bigquery_table']
            }), 400
        
        logger.info(f"[LEGACY] Processando relatório para property {property_id}")
        
        # Buscar credenciais
        credentials = get_credentials(project_id, secret_id)
        
        # Inicializar cliente GA4
        ga4 = GoogleAnalytics4(
            property_id=property_id,
            credentials=credentials
        )
        
        # Preparar requisição
        date_ranges = [
            DateRange(**dr) for dr in data.get('date_ranges', [
                {'start_date': 'yesterday', 'end_date': 'yesterday'}
            ])
        ]
        
        dimensions = [
            Dimension(**dim) for dim in data.get('dimensions', [])
        ]
        
        metrics = [
            Metric(**met) for met in data.get('metrics', [])
        ]
        
        if not dimensions and not metrics:
            return jsonify({
                'error': 'Deve especificar ao menos uma dimension ou metric'
            }), 400
        
        report_request = RunReportRequest(
            property_id=property_id,
            date_ranges=date_ranges,
            dimensions=dimensions,
            metrics=metrics,
            limit=data.get('limit', 10000),
            offset=data.get('offset', 0)
        )
        
        # Executar relatório
        response = ga4.run_report(report_request)
        logger.info(f"Relatório executado: {response['row_count']} linhas")
        
        # Salvar no BigQuery
        bigquery_dataset = data.get('bigquery_dataset', GCPConfig.DATASET_ID)
        bq_writer = BigQueryWriter(
            project_id=project_id,
            dataset_id=bigquery_dataset,
            credentials=credentials
        )
        
        bq_writer.write_ga4_data(
            table_id=bigquery_table,
            data=response,
            auto_create=True
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Relatório processado e salvo no BigQuery',
            'details': {
                'property_id': property_id,
                'rows_processed': response['row_count'],
                'bigquery_table': f"{project_id}.{bigquery_dataset}.{bigquery_table}",
                'dimensions': response['dimension_headers'],
                'metrics': [m['name'] for m in response['metric_headers']]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar relatório: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# =============================================================================
# FUNÇÃO MAIN PARA CLOUD RUN
# =============================================================================

def main():
    """
    Função principal para execução no Cloud Run.
    
    Esta função é chamada quando o serviço é iniciado.
    O Cloud Run espera que a aplicação escute na porta definida
    pela variável de ambiente PORT.
    """
    port = int(os.environ.get('PORT', CloudRunConfig.PORT))
    
    logger.info(f"Iniciando API Google Analytics 4 na porta {port}")
    logger.info(f"Projeto GCP: {GCPConfig.PROJECT_ID}")
    logger.info(f"Dataset: {GCPConfig.DATASET_ID}")
    
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
