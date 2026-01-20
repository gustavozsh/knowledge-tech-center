"""
Entry point principal para Cloud Run
API REST para executar relatórios do Google Analytics 4 e salvar no BigQuery

Versão Python: 3.11
"""

import os
import json
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials

from src.secret_manager import SecretManager
from src.ga4_client import GoogleAnalytics4
from src.bigquery_writer import BigQueryWriter
from src.models import DateRange, Dimension, Metric, RunReportRequest

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Google Analytics 4 API',
        'version': '1.0.0'
    }), 200


@app.route('/run-report', methods=['POST'])
def run_report():
    """
    Endpoint para executar relatório do GA4 e salvar no BigQuery.

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
        # Validar request
        if not request.is_json:
            return jsonify({'error': 'Request deve ser JSON'}), 400

        data = request.get_json()

        # Extrair parâmetros obrigatórios
        project_id = data.get('project_id')
        secret_id = data.get('secret_id')
        property_id = data.get('property_id')
        bigquery_table = data.get('bigquery_table')

        if not all([project_id, secret_id, property_id, bigquery_table]):
            return jsonify({
                'error': 'Parâmetros obrigatórios faltando',
                'required': ['project_id', 'secret_id', 'property_id', 'bigquery_table']
            }), 400

        logger.info(f"Processando relatório para property {property_id}")

        # 1. Buscar credenciais no Secret Manager
        logger.info(f"Buscando credenciais do Secret Manager: {secret_id}")
        secret_manager = SecretManager()
        secret_value = secret_manager.access_secret_version(
            secret_id=secret_id,
            project_id=project_id
        )

        # 2. Carregar JSON e criar objeto Credentials
        service_account_json = json.loads(secret_value)
        credentials = Credentials.from_service_account_info(service_account_json)

        # 3. Instanciar GoogleAnalytics4
        logger.info("Inicializando cliente Google Analytics 4")
        ga4 = GoogleAnalytics4(credentials)

        # 4. Preparar requisição do relatório
        date_ranges = [
            DateRange(**dr) for dr in data.get('date_ranges', [
                {'start_date': '7daysAgo', 'end_date': 'today'}
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

        # Criar requisição
        report_request = RunReportRequest(
            property_id=property_id,
            date_ranges=date_ranges,
            dimensions=dimensions,
            metrics=metrics,
            limit=data.get('limit', 10000),
            offset=data.get('offset', 0)
        )

        # 5. Executar relatório
        logger.info("Executando relatório do GA4")
        response = ga4.run_report(report_request)

        logger.info(f"Relatório executado: {response['row_count']} linhas retornadas")

        # 6. Salvar no BigQuery
        logger.info("Salvando dados no BigQuery")
        bigquery_dataset = data.get('bigquery_dataset', 'RAW')
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

        logger.info("Dados salvos com sucesso no BigQuery")

        # 7. Retornar resultado
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


@app.route('/batch-reports', methods=['POST'])
def batch_reports():
    """
    Endpoint para executar múltiplos relatórios do GA4 em lote.

    Request Body (JSON):
    {
        "project_id": "your-project-id",
        "secret_id": "ga4-credentials",
        "property_id": "123456789",
        "bigquery_table": "ga4_batch_reports",
        "bigquery_dataset": "RAW",
        "requests": [
            {
                "date_ranges": [...],
                "dimensions": [...],
                "metrics": [...]
            },
            ...
        ]
    }

    Returns:
        JSON com status e informações do processamento
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Request deve ser JSON'}), 400

        data = request.get_json()

        # Extrair parâmetros
        project_id = data.get('project_id')
        secret_id = data.get('secret_id')
        property_id = data.get('property_id')
        bigquery_table = data.get('bigquery_table')
        requests_data = data.get('requests', [])

        if not all([project_id, secret_id, property_id, bigquery_table]):
            return jsonify({
                'error': 'Parâmetros obrigatórios faltando'
            }), 400

        if not requests_data:
            return jsonify({
                'error': 'Nenhuma requisição fornecida'
            }), 400

        logger.info(f"Processando {len(requests_data)} relatórios em lote")

        # Buscar credenciais
        secret_manager = SecretManager()
        secret_value = secret_manager.access_secret_version(
            secret_id=secret_id,
            project_id=project_id
        )

        service_account_json = json.loads(secret_value)
        credentials = Credentials.from_service_account_info(service_account_json)

        # Inicializar cliente
        ga4 = GoogleAnalytics4(credentials)

        # Preparar requisições
        report_requests = []
        for req_data in requests_data:
            date_ranges = [DateRange(**dr) for dr in req_data.get('date_ranges', [])]
            dimensions = [Dimension(**dim) for dim in req_data.get('dimensions', [])]
            metrics = [Metric(**met) for met in req_data.get('metrics', [])]

            report_requests.append(RunReportRequest(
                property_id=property_id,
                date_ranges=date_ranges,
                dimensions=dimensions,
                metrics=metrics,
                limit=req_data.get('limit', 10000)
            ))

        # Executar relatórios em lote
        logger.info("Executando relatórios em lote")
        responses = ga4.batch_run_reports(report_requests)

        # Salvar no BigQuery
        logger.info("Salvando dados no BigQuery")
        bigquery_dataset = data.get('bigquery_dataset', 'RAW')
        bq_writer = BigQueryWriter(
            project_id=project_id,
            dataset_id=bigquery_dataset,
            credentials=credentials
        )

        bq_writer.write_batch_reports(
            table_id=bigquery_table,
            reports=responses,
            auto_create=True
        )

        total_rows = sum(r['row_count'] for r in responses)

        return jsonify({
            'status': 'success',
            'message': 'Relatórios em lote processados e salvos',
            'details': {
                'property_id': property_id,
                'reports_processed': len(responses),
                'total_rows': total_rows,
                'bigquery_table': f"{project_id}.{bigquery_dataset}.{bigquery_table}"
            }
        }), 200

    except Exception as e:
        logger.error(f"Erro ao processar relatórios em lote: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/realtime-report', methods=['POST'])
def realtime_report():
    """
    Endpoint para executar relatório em tempo real do GA4.

    Request Body (JSON):
    {
        "project_id": "your-project-id",
        "secret_id": "ga4-credentials",
        "property_id": "123456789",
        "bigquery_table": "ga4_realtime",
        "bigquery_dataset": "RAW",
        "dimensions": [
            {"name": "country"}
        ],
        "metrics": [
            {"name": "activeUsers"}
        ],
        "limit": 10
    }

    Returns:
        JSON com status e dados em tempo real
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Request deve ser JSON'}), 400

        data = request.get_json()

        project_id = data.get('project_id')
        secret_id = data.get('secret_id')
        property_id = data.get('property_id')
        bigquery_table = data.get('bigquery_table')

        if not all([project_id, secret_id, property_id, bigquery_table]):
            return jsonify({
                'error': 'Parâmetros obrigatórios faltando'
            }), 400

        # Buscar credenciais
        secret_manager = SecretManager()
        secret_value = secret_manager.access_secret_version(
            secret_id=secret_id,
            project_id=project_id
        )

        service_account_json = json.loads(secret_value)
        credentials = Credentials.from_service_account_info(service_account_json)

        # Inicializar cliente
        ga4 = GoogleAnalytics4(credentials)

        # Preparar dimensões e métricas
        dimensions = [Dimension(**dim) for dim in data.get('dimensions', [])]
        metrics = [Metric(**met) for met in data.get('metrics', [])]

        # Executar relatório em tempo real
        logger.info("Executando relatório em tempo real")
        response = ga4.run_realtime_report(
            dimensions=dimensions,
            metrics=metrics,
            limit=data.get('limit', 10)
        )

        # Salvar no BigQuery
        bigquery_dataset = data.get('bigquery_dataset', 'RAW')
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
            'message': 'Relatório em tempo real processado',
            'details': {
                'property_id': property_id,
                'active_users': response['row_count'],
                'bigquery_table': f"{project_id}.{bigquery_dataset}.{bigquery_table}"
            }
        }), 200

    except Exception as e:
        logger.error(f"Erro ao processar relatório em tempo real: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Configurações para Cloud Run
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
