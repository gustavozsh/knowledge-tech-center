"""
DAGs Airflow para carga diária de dados do Twitter no BigQuery.

Este módulo contém DAGs para orquestrar a extração de dados do Twitter
utilizando a Taskflow API do Airflow.

Autor: Manus AI
Data: Janeiro de 2026

DAGs disponíveis:
    - dag_twitter_daily_load: Carga diária automática para todas as contas
    - dag_twitter_single_account: Execução manual para uma conta específica
    - dag_twitter_backfill: Carga de dados históricos
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import logging

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
import requests

# Configurar logging
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÕES PADRÃO
# =============================================================================

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# Tags para organização
TAGS = ["twitter", "social-media", "bigquery", "daily-load"]


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_api_url() -> str:
    """Obtém a URL da API do Twitter a partir das variáveis do Airflow."""
    return Variable.get("twitter_api_url", default_var="http://localhost:8080")


def get_twitter_accounts() -> List[Dict[str, str]]:
    """Obtém a lista de contas do Twitter a partir das variáveis do Airflow."""
    accounts_json = Variable.get("twitter_accounts", default_var="[]")
    return json.loads(accounts_json)


def make_api_request(
    endpoint: str,
    method: str = "POST",
    data: Dict[str, Any] = None,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Faz uma requisição à API do Twitter.
    
    Args:
        endpoint: Endpoint da API
        method: Método HTTP
        data: Dados da requisição
        timeout: Timeout em segundos
        
    Returns:
        Resposta da API
    """
    api_url = get_api_url()
    url = f"{api_url}/{endpoint}"
    
    logger.info(f"Fazendo requisição {method} para {url}")
    
    if method == "POST":
        response = requests.post(url, json=data, timeout=timeout)
    else:
        response = requests.get(url, timeout=timeout)
    
    response.raise_for_status()
    return response.json()


# =============================================================================
# DAG 1: CARGA DIÁRIA AUTOMÁTICA
# =============================================================================

@dag(
    dag_id="dag_twitter_daily_load",
    description="Carga diária de dados do Twitter para BigQuery",
    schedule_interval="0 6 * * *",  # Executa às 06:00 UTC todos os dias
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=TAGS,
    max_active_runs=1,
)
def dag_twitter_daily_load():
    """
    DAG principal para carga diária de dados do Twitter.
    
    Executa automaticamente todos os dias às 06:00 UTC para todas
    as contas configuradas na variável 'twitter_accounts'.
    """
    
    @task(task_id="validate_config")
    def validate_config() -> Dict[str, Any]:
        """Valida as configurações necessárias."""
        logger.info("Validando configurações...")
        
        # Verificar URL da API
        api_url = get_api_url()
        if not api_url:
            raise ValueError("Variável 'twitter_api_url' não configurada")
        
        # Verificar contas
        accounts = get_twitter_accounts()
        if not accounts:
            logger.warning("Nenhuma conta configurada na variável 'twitter_accounts'")
        
        # Verificar se a API está online
        try:
            response = make_api_request("", method="GET", timeout=30)
            api_status = response.get("status", "unknown")
        except Exception as e:
            logger.error(f"API não está acessível: {e}")
            raise
        
        return {
            "api_url": api_url,
            "api_status": api_status,
            "accounts_count": len(accounts),
            "accounts": accounts
        }
    
    @task(task_id="process_accounts")
    def process_accounts(config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa todas as contas configuradas."""
        accounts = config.get("accounts", [])
        
        if not accounts:
            logger.warning("Nenhuma conta para processar")
            return []
        
        results = []
        
        for account in accounts:
            username = account.get("username")
            user_id = account.get("user_id")
            
            logger.info(f"Processando conta: @{username}")
            
            try:
                response = make_api_request(
                    endpoint="report/all",
                    method="POST",
                    data={
                        "username": username,
                        "user_id": user_id,
                        "name": account.get("name", username)
                    },
                    timeout=600
                )
                
                results.append({
                    "account": username,
                    "status": "success",
                    "summary": response.get("summary", {}),
                    "reports": response.get("reports", {})
                })
                
            except Exception as e:
                logger.error(f"Erro ao processar @{username}: {e}")
                results.append({
                    "account": username,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    @task(task_id="consolidate_results")
    def consolidate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolida os resultados de todas as contas."""
        total_accounts = len(results)
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = total_accounts - successful
        
        total_rows = 0
        for result in results:
            if result.get("status") == "success":
                summary = result.get("summary", {})
                total_rows += summary.get("total_rows_inserted", 0)
        
        consolidated = {
            "execution_date": datetime.now().isoformat(),
            "total_accounts": total_accounts,
            "successful_accounts": successful,
            "failed_accounts": failed,
            "total_rows_inserted": total_rows,
            "details": results
        }
        
        logger.info(f"Consolidação: {successful}/{total_accounts} contas processadas com sucesso")
        logger.info(f"Total de linhas inseridas: {total_rows}")
        
        return consolidated
    
    @task(task_id="notify_completion", trigger_rule=TriggerRule.ALL_DONE)
    def notify_completion(consolidated: Dict[str, Any]) -> None:
        """Notifica a conclusão da execução."""
        logger.info("=" * 50)
        logger.info("EXECUÇÃO CONCLUÍDA")
        logger.info("=" * 50)
        logger.info(f"Data: {consolidated.get('execution_date')}")
        logger.info(f"Contas processadas: {consolidated.get('successful_accounts')}/{consolidated.get('total_accounts')}")
        logger.info(f"Linhas inseridas: {consolidated.get('total_rows_inserted')}")
        
        if consolidated.get("failed_accounts", 0) > 0:
            logger.warning(f"Contas com falha: {consolidated.get('failed_accounts')}")
            for detail in consolidated.get("details", []):
                if detail.get("status") == "error":
                    logger.warning(f"  - @{detail.get('account')}: {detail.get('error')}")
    
    # Definir fluxo
    config = validate_config()
    results = process_accounts(config)
    consolidated = consolidate_results(results)
    notify_completion(consolidated)


# =============================================================================
# DAG 2: EXECUÇÃO MANUAL PARA UMA CONTA
# =============================================================================

@dag(
    dag_id="dag_twitter_single_account",
    description="Execução manual para uma conta específica do Twitter",
    schedule_interval=None,  # Apenas execução manual
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=TAGS + ["manual"],
    params={
        "username": "",
        "user_id": "",
        "name": "",
        "start_date": "",
        "end_date": ""
    },
)
def dag_twitter_single_account():
    """
    DAG para execução manual de uma conta específica.
    
    Parâmetros:
        username: Username da conta do Twitter
        user_id: ID do usuário no Twitter
        name: Nome da conta (opcional)
        start_date: Data de início (formato YYYY-MM-DD, opcional)
        end_date: Data de fim (formato YYYY-MM-DD, opcional)
    """
    
    @task(task_id="validate_params")
    def validate_params(**context) -> Dict[str, Any]:
        """Valida os parâmetros fornecidos."""
        params = context["params"]
        
        username = params.get("username", "").strip()
        user_id = params.get("user_id", "").strip()
        
        if not username or not user_id:
            raise ValueError("Parâmetros 'username' e 'user_id' são obrigatórios")
        
        return {
            "username": username,
            "user_id": user_id,
            "name": params.get("name", "").strip() or username,
            "start_date": params.get("start_date", "").strip() or None,
            "end_date": params.get("end_date", "").strip() or None
        }
    
    @task(task_id="process_account")
    def process_account(params: Dict[str, Any]) -> Dict[str, Any]:
        """Processa a conta especificada."""
        logger.info(f"Processando conta: @{params['username']}")
        
        request_data = {
            "username": params["username"],
            "user_id": params["user_id"],
            "name": params["name"]
        }
        
        if params.get("start_date") and params.get("end_date"):
            request_data["start_date"] = params["start_date"]
            request_data["end_date"] = params["end_date"]
        
        response = make_api_request(
            endpoint="report/all",
            method="POST",
            data=request_data,
            timeout=600
        )
        
        return response
    
    @task(task_id="log_results")
    def log_results(result: Dict[str, Any]) -> None:
        """Loga os resultados da execução."""
        logger.info("=" * 50)
        logger.info("RESULTADO DA EXECUÇÃO")
        logger.info("=" * 50)
        logger.info(f"Conta: @{result.get('account')}")
        logger.info(f"Período: {result.get('period', {})}")
        
        summary = result.get("summary", {})
        logger.info(f"Relatórios: {summary.get('successful', 0)}/{summary.get('total_reports', 0)}")
        logger.info(f"Linhas inseridas: {summary.get('total_rows_inserted', 0)}")
    
    # Definir fluxo
    params = validate_params()
    result = process_account(params)
    log_results(result)


# =============================================================================
# DAG 3: BACKFILL DE DADOS HISTÓRICOS
# =============================================================================

@dag(
    dag_id="dag_twitter_backfill",
    description="Backfill de dados históricos do Twitter",
    schedule_interval=None,  # Apenas execução manual
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        **DEFAULT_ARGS,
        "retries": 1,
        "execution_timeout": timedelta(hours=6),
    },
    tags=TAGS + ["backfill", "manual"],
    params={
        "start_date": "",
        "end_date": "",
        "accounts": ""  # JSON array ou vazio para todas
    },
)
def dag_twitter_backfill():
    """
    DAG para backfill de dados históricos.
    
    Parâmetros:
        start_date: Data de início (formato YYYY-MM-DD)
        end_date: Data de fim (formato YYYY-MM-DD)
        accounts: JSON array de contas ou vazio para todas as configuradas
    """
    
    @task(task_id="validate_params")
    def validate_params(**context) -> Dict[str, Any]:
        """Valida os parâmetros de backfill."""
        params = context["params"]
        
        start_date = params.get("start_date", "").strip()
        end_date = params.get("end_date", "").strip()
        
        if not start_date or not end_date:
            raise ValueError("Parâmetros 'start_date' e 'end_date' são obrigatórios")
        
        # Validar formato das datas
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Datas devem estar no formato YYYY-MM-DD")
        
        # Obter contas
        accounts_param = params.get("accounts", "").strip()
        if accounts_param:
            accounts = json.loads(accounts_param)
        else:
            accounts = get_twitter_accounts()
        
        if not accounts:
            raise ValueError("Nenhuma conta especificada ou configurada")
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "accounts": accounts
        }
    
    @task(task_id="run_backfill")
    def run_backfill(params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o backfill para todas as contas."""
        accounts = params["accounts"]
        start_date = params["start_date"]
        end_date = params["end_date"]
        
        logger.info(f"Iniciando backfill de {start_date} até {end_date}")
        logger.info(f"Contas: {len(accounts)}")
        
        # Preparar dados para requisição batch
        accounts_data = [
            {
                "username": acc.get("username"),
                "user_id": acc.get("user_id"),
                "name": acc.get("name", acc.get("username"))
            }
            for acc in accounts
        ]
        
        response = make_api_request(
            endpoint="report/batch",
            method="POST",
            data={
                "accounts": accounts_data,
                "start_date": start_date,
                "end_date": end_date
            },
            timeout=1800  # 30 minutos para backfill
        )
        
        return response
    
    @task(task_id="log_backfill_results")
    def log_backfill_results(result: Dict[str, Any]) -> None:
        """Loga os resultados do backfill."""
        logger.info("=" * 50)
        logger.info("RESULTADO DO BACKFILL")
        logger.info("=" * 50)
        
        summary = result.get("summary", {})
        logger.info(f"Contas processadas: {summary.get('successful_accounts', 0)}/{summary.get('total_accounts', 0)}")
        logger.info(f"Linhas inseridas: {summary.get('total_rows_inserted', 0)}")
        
        if summary.get("failed_accounts", 0) > 0:
            logger.warning(f"Contas com falha: {summary.get('failed_accounts')}")
    
    # Definir fluxo
    params = validate_params()
    result = run_backfill(params)
    log_backfill_results(result)


# =============================================================================
# INSTANCIAR DAGs
# =============================================================================

dag_daily = dag_twitter_daily_load()
dag_single = dag_twitter_single_account()
dag_backfill = dag_twitter_backfill()
