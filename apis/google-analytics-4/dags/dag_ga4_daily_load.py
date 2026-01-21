"""
DAG Airflow para Carga Diária de Dados do Google Analytics 4

Esta DAG é responsável por orquestrar a carga diária de dados do GA4
para o BigQuery, executando relatórios de dimensões e métricas.

Utiliza a Taskflow API do Airflow para uma sintaxe mais limpa e moderna.

Autor: Data Engineering Team
Data: Janeiro 2025
Versão: 2.0.0

Configuração:
    - Schedule: Diário às 06:00 UTC (03:00 BRT)
    - Retries: 3 tentativas com intervalo de 5 minutos
    - Timeout: 1 hora

Variáveis Airflow necessárias:
    - ga4_property_ids: Lista de IDs das propriedades GA4 (JSON)
    - gcp_project_id: ID do projeto GCP (opcional, usa default)
    - ga4_secret_id: ID do secret no Secret Manager (opcional, usa default)

Connections Airflow necessárias:
    - google_cloud_default: Conexão com o GCP
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import logging

from airflow.decorators import dag, task, task_group
from airflow.models import Variable
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import get_current_context
from airflow.utils.trigger_rule import TriggerRule

import requests


# =============================================================================
# CONFIGURAÇÕES DA DAG
# =============================================================================

# Configurações padrão
DEFAULT_ARGS = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# Configurações do projeto
GCP_PROJECT_ID = "cadastra-yduqs-uat"
DATASET_ID = "RAW"
SECRET_ID = "ga4-credentials"

# URL do serviço Cloud Run (será configurada após deploy)
# Pode ser sobrescrita pela variável Airflow 'ga4_api_url'
CLOUD_RUN_URL = "https://ga4-api-xxxxxxxxxx-uc.a.run.app"

# Tabelas de dimensões
DIMENSION_TABLES = [
    "TB_001_GA4_DIM_USUARIO",
    "TB_002_GA4_DIM_GEOGRAFICA",
    "TB_003_GA4_DIM_DISPOSITIVO",
    "TB_004_GA4_DIM_AQUISICAO",
    "TB_005_GA4_DIM_PAGINA",
    "TB_006_GA4_DIM_EVENTO",
    "TB_007_GA4_DIM_PUBLICO"
]

# Tabelas de métricas
METRIC_TABLES = [
    "TB_008_GA4_MET_USUARIOS",
    "TB_009_GA4_MET_SESSAO",
    "TB_010_GA4_MET_EVENTOS",
    "TB_011_GA4_MET_VISUALIZACAO",
    "TB_012_GA4_MET_ECOMMERCE"
]


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_api_url() -> str:
    """
    Obtém a URL da API do Cloud Run.
    
    Primeiro tenta obter da variável Airflow, depois usa o default.
    """
    try:
        return Variable.get("ga4_api_url", default_var=CLOUD_RUN_URL)
    except Exception:
        return CLOUD_RUN_URL


def get_property_ids() -> List[str]:
    """
    Obtém a lista de Property IDs do GA4.
    
    A lista deve ser configurada como uma variável Airflow no formato JSON.
    Exemplo: ["123456789", "987654321"]
    """
    try:
        property_ids_json = Variable.get("ga4_property_ids")
        return json.loads(property_ids_json)
    except Exception as e:
        logging.warning(f"Variável ga4_property_ids não encontrada: {e}")
        return []


def call_api(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Faz uma chamada à API do Cloud Run.
    
    Args:
        endpoint: Endpoint da API (ex: /report/all)
        payload: Dados a serem enviados no body da requisição
        
    Returns:
        Resposta da API como dicionário
    """
    api_url = get_api_url()
    url = f"{api_url}{endpoint}"
    
    logging.info(f"Chamando API: {url}")
    logging.info(f"Payload: {json.dumps(payload)}")
    
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=300  # 5 minutos de timeout
    )
    
    response.raise_for_status()
    return response.json()


# =============================================================================
# DEFINIÇÃO DA DAG
# =============================================================================

@dag(
    dag_id='dag_ga4_daily_load',
    description='DAG para carga diária de dados do Google Analytics 4 para o BigQuery',
    schedule_interval='0 6 * * *',  # Diário às 06:00 UTC
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=['ga4', 'bigquery', 'daily', 'etl', 'google-analytics'],
    max_active_runs=1,
    doc_md=__doc__
)
def dag_ga4_daily_load():
    """
    DAG principal para carga diária de dados do GA4.
    
    Fluxo:
    1. Validar configurações
    2. Para cada propriedade GA4:
        a. Executar relatórios de dimensões
        b. Executar relatórios de métricas
    3. Consolidar resultados
    4. Notificar conclusão
    """
    
    # =========================================================================
    # TASK: Validar Configurações
    # =========================================================================
    
    @task(task_id='validate_config')
    def validate_config() -> Dict[str, Any]:
        """
        Valida as configurações necessárias para a execução da DAG.
        
        Returns:
            Dicionário com configurações validadas
        """
        logging.info("Validando configurações...")
        
        # Obter Property IDs
        property_ids = get_property_ids()
        
        if not property_ids:
            raise ValueError(
                "Nenhum Property ID configurado. "
                "Configure a variável Airflow 'ga4_property_ids' com uma lista JSON de IDs."
            )
        
        # Obter URL da API
        api_url = get_api_url()
        
        # Verificar se a API está acessível
        try:
            response = requests.get(f"{api_url}/", timeout=30)
            response.raise_for_status()
            api_status = response.json()
            logging.info(f"API Status: {api_status}")
        except Exception as e:
            raise ConnectionError(f"Não foi possível conectar à API: {e}")
        
        config = {
            'property_ids': property_ids,
            'api_url': api_url,
            'project_id': GCP_PROJECT_ID,
            'dataset_id': DATASET_ID,
            'secret_id': SECRET_ID,
            'execution_date': datetime.now().strftime('%Y-%m-%d'),
            'date_range': {
                'start_date': 'yesterday',
                'end_date': 'yesterday'
            }
        }
        
        logging.info(f"Configuração validada: {len(property_ids)} propriedades")
        return config
    
    # =========================================================================
    # TASK GROUP: Processar Propriedade
    # =========================================================================
    
    @task_group(group_id='process_properties')
    def process_properties(config: Dict[str, Any]):
        """
        Grupo de tasks para processar todas as propriedades GA4.
        """
        
        @task(task_id='get_properties')
        def get_properties(config: Dict[str, Any]) -> List[str]:
            """Retorna a lista de propriedades a processar."""
            return config['property_ids']
        
        @task(task_id='process_property', max_active_tis_per_dag=3)
        def process_property(property_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
            """
            Processa uma propriedade GA4 específica.
            
            Executa todos os relatórios (dimensões e métricas) para a propriedade.
            
            Args:
                property_id: ID da propriedade GA4
                config: Configurações da execução
                
            Returns:
                Resultado do processamento
            """
            logging.info(f"Processando propriedade: {property_id}")
            
            payload = {
                'property_id': property_id,
                'start_date': config['date_range']['start_date'],
                'end_date': config['date_range']['end_date'],
                'project_id': config['project_id'],
                'secret_id': config['secret_id']
            }
            
            try:
                result = call_api('/report/all', payload)
                
                logging.info(f"Propriedade {property_id} processada com sucesso")
                logging.info(f"Resumo: {result.get('results', {}).get('summary', {})}")
                
                return {
                    'property_id': property_id,
                    'status': 'success',
                    'result': result
                }
                
            except Exception as e:
                logging.error(f"Erro ao processar propriedade {property_id}: {e}")
                return {
                    'property_id': property_id,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Obter lista de propriedades
        properties = get_properties(config)
        
        # Processar cada propriedade (com paralelismo limitado)
        return process_property.expand(
            property_id=properties,
            config=[config] * len(config['property_ids'])
        )
    
    # =========================================================================
    # TASK: Consolidar Resultados
    # =========================================================================
    
    @task(task_id='consolidate_results', trigger_rule=TriggerRule.ALL_DONE)
    def consolidate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolida os resultados de todas as propriedades processadas.
        
        Args:
            results: Lista de resultados de cada propriedade
            
        Returns:
            Resumo consolidado da execução
        """
        logging.info("Consolidando resultados...")
        
        total_properties = len(results)
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = total_properties - successful
        
        total_rows = 0
        for result in results:
            if result.get('status') == 'success':
                summary = result.get('result', {}).get('results', {}).get('summary', {})
                total_rows += summary.get('total_rows_processed', 0)
        
        consolidated = {
            'execution_date': datetime.now().isoformat(),
            'total_properties': total_properties,
            'successful': successful,
            'failed': failed,
            'total_rows_processed': total_rows,
            'success_rate': f"{(successful / total_properties * 100):.1f}%" if total_properties > 0 else "0%",
            'details': results
        }
        
        logging.info(f"Execução concluída: {successful}/{total_properties} propriedades processadas com sucesso")
        logging.info(f"Total de linhas processadas: {total_rows}")
        
        if failed > 0:
            failed_properties = [r['property_id'] for r in results if r.get('status') == 'error']
            logging.warning(f"Propriedades com falha: {failed_properties}")
        
        return consolidated
    
    # =========================================================================
    # TASK: Notificar Conclusão
    # =========================================================================
    
    @task(task_id='notify_completion', trigger_rule=TriggerRule.ALL_DONE)
    def notify_completion(summary: Dict[str, Any]) -> None:
        """
        Notifica a conclusão da execução da DAG.
        
        Args:
            summary: Resumo consolidado da execução
        """
        context = get_current_context()
        dag_run = context['dag_run']
        
        message = f"""
        ========================================
        DAG GA4 Daily Load - Execução Concluída
        ========================================
        
        Data de Execução: {summary['execution_date']}
        DAG Run ID: {dag_run.run_id}
        
        Resumo:
        - Total de Propriedades: {summary['total_properties']}
        - Sucesso: {summary['successful']}
        - Falhas: {summary['failed']}
        - Taxa de Sucesso: {summary['success_rate']}
        - Total de Linhas: {summary['total_rows_processed']:,}
        
        ========================================
        """
        
        logging.info(message)
        
        # Aqui você pode adicionar notificações adicionais:
        # - Enviar email
        # - Enviar mensagem no Slack
        # - Registrar métricas no Cloud Monitoring
        # - etc.
    
    # =========================================================================
    # DEFINIÇÃO DO FLUXO DA DAG
    # =========================================================================
    
    # 1. Validar configurações
    config = validate_config()
    
    # 2. Processar todas as propriedades
    results = process_properties(config)
    
    # 3. Consolidar resultados
    summary = consolidate_results(results)
    
    # 4. Notificar conclusão
    notify_completion(summary)


# =============================================================================
# DAG ALTERNATIVA: Processar Propriedade Individual
# =============================================================================

@dag(
    dag_id='dag_ga4_single_property',
    description='DAG para processar uma única propriedade GA4 (trigger manual)',
    schedule_interval=None,  # Apenas trigger manual
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=['ga4', 'bigquery', 'manual', 'single-property'],
    params={
        'property_id': '',
        'start_date': 'yesterday',
        'end_date': 'yesterday'
    },
    doc_md="""
    # DAG para Processar Propriedade Individual
    
    Esta DAG permite processar uma única propriedade GA4 manualmente.
    
    ## Parâmetros
    - `property_id`: ID da propriedade GA4 (obrigatório)
    - `start_date`: Data inicial (default: yesterday)
    - `end_date`: Data final (default: yesterday)
    
    ## Uso
    Trigger manual com configuração dos parâmetros.
    """
)
def dag_ga4_single_property():
    """DAG para processar uma única propriedade GA4."""
    
    @task(task_id='validate_params')
    def validate_params(**context) -> Dict[str, Any]:
        """Valida os parâmetros fornecidos."""
        params = context['params']
        
        property_id = params.get('property_id')
        if not property_id:
            raise ValueError("property_id é obrigatório")
        
        return {
            'property_id': property_id,
            'start_date': params.get('start_date', 'yesterday'),
            'end_date': params.get('end_date', 'yesterday'),
            'project_id': GCP_PROJECT_ID,
            'secret_id': SECRET_ID
        }
    
    @task(task_id='run_reports')
    def run_reports(config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa os relatórios para a propriedade."""
        logging.info(f"Processando propriedade: {config['property_id']}")
        
        payload = {
            'property_id': config['property_id'],
            'start_date': config['start_date'],
            'end_date': config['end_date'],
            'project_id': config['project_id'],
            'secret_id': config['secret_id']
        }
        
        result = call_api('/report/all', payload)
        
        logging.info(f"Resultado: {result.get('results', {}).get('summary', {})}")
        return result
    
    @task(task_id='log_result')
    def log_result(result: Dict[str, Any]) -> None:
        """Registra o resultado da execução."""
        summary = result.get('results', {}).get('summary', {})
        logging.info(f"""
        Execução concluída:
        - Relatórios processados: {summary.get('total_reports', 0)}
        - Sucesso: {summary.get('successful', 0)}
        - Falhas: {summary.get('failed', 0)}
        - Total de linhas: {summary.get('total_rows_processed', 0)}
        """)
    
    # Fluxo
    config = validate_params()
    result = run_reports(config)
    log_result(result)


# =============================================================================
# DAG ALTERNATIVA: Backfill de Dados
# =============================================================================

@dag(
    dag_id='dag_ga4_backfill',
    description='DAG para backfill de dados históricos do GA4',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=['ga4', 'bigquery', 'backfill', 'manual'],
    params={
        'property_id': '',
        'start_date': '',
        'end_date': ''
    },
    doc_md="""
    # DAG para Backfill de Dados Históricos
    
    Esta DAG permite carregar dados históricos do GA4 para um período específico.
    
    ## Parâmetros
    - `property_id`: ID da propriedade GA4 (obrigatório)
    - `start_date`: Data inicial no formato YYYY-MM-DD (obrigatório)
    - `end_date`: Data final no formato YYYY-MM-DD (obrigatório)
    
    ## Limitações
    - O GA4 permite consultar dados de até 14 meses atrás
    - Períodos muito longos podem exceder os limites de quota da API
    """
)
def dag_ga4_backfill():
    """DAG para backfill de dados históricos."""
    
    @task(task_id='validate_params')
    def validate_params(**context) -> Dict[str, Any]:
        """Valida os parâmetros de backfill."""
        params = context['params']
        
        property_id = params.get('property_id')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        if not all([property_id, start_date, end_date]):
            raise ValueError("property_id, start_date e end_date são obrigatórios")
        
        # Validar formato das datas
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Datas devem estar no formato YYYY-MM-DD")
        
        return {
            'property_id': property_id,
            'start_date': start_date,
            'end_date': end_date,
            'project_id': GCP_PROJECT_ID,
            'secret_id': SECRET_ID
        }
    
    @task(task_id='run_backfill')
    def run_backfill(config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o backfill para o período especificado."""
        logging.info(f"Executando backfill para {config['property_id']}")
        logging.info(f"Período: {config['start_date']} a {config['end_date']}")
        
        payload = {
            'property_id': config['property_id'],
            'start_date': config['start_date'],
            'end_date': config['end_date'],
            'project_id': config['project_id'],
            'secret_id': config['secret_id']
        }
        
        result = call_api('/report/all', payload)
        return result
    
    @task(task_id='log_backfill_result')
    def log_backfill_result(result: Dict[str, Any]) -> None:
        """Registra o resultado do backfill."""
        summary = result.get('results', {}).get('summary', {})
        logging.info(f"Backfill concluído: {summary.get('total_rows_processed', 0)} linhas processadas")
    
    # Fluxo
    config = validate_params()
    result = run_backfill(config)
    log_backfill_result(result)


# =============================================================================
# INSTANCIAR AS DAGS
# =============================================================================

# DAG principal de carga diária
dag_daily = dag_ga4_daily_load()

# DAG para propriedade individual
dag_single = dag_ga4_single_property()

# DAG para backfill
dag_backfill = dag_ga4_backfill()
