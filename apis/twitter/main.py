"""
API de Extração de Dados do Twitter/X para BigQuery.

Esta API fornece endpoints REST para extrair dados do Twitter
e carregá-los no Google BigQuery.

Autor: Manus AI
Data: Janeiro de 2026

Para executar localmente:
    python main.py

Para deploy no Cloud Run:
    A função principal é `main()` que inicia o servidor Flask.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify
import pytz

from config import (
    gcp_config,
    twitter_accounts_config,
    date_config,
    tables_config,
    twitter_api_config,
    TwitterAccount
)
from src.twitter_client import TwitterClient, TwitterDataExtractor
from src.bigquery_writer import BigQueryWriter
from src.secret_manager import SecretManagerClient

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

def get_date_range(days_start: int = None, days_end: int = None) -> tuple:
    """
    Calcula o range de datas para extração.
    
    Args:
        days_start: Dias de início (D-X)
        days_end: Dias de fim (D-X)
        
    Returns:
        Tupla com (data_inicio, data_fim)
    """
    if days_start is None:
        days_start = date_config.DAYS_START
    if days_end is None:
        days_end = date_config.DAYS_END
    
    tz = pytz.timezone(date_config.TIMEZONE)
    now = datetime.now(tz)
    
    start_date = now - timedelta(days=days_start)
    end_date = now - timedelta(days=days_end)
    
    return start_date, end_date


def get_bearer_token(account: TwitterAccount = None) -> str:
    """
    Obtém o Bearer Token do Twitter.
    
    Args:
        account: Conta do Twitter (opcional)
        
    Returns:
        Bearer Token
    """
    # Se a conta tem um token específico, usa ele
    if account and account.bearer_token:
        return account.bearer_token
    
    # Tenta obter do Secret Manager
    try:
        secret_client = SecretManagerClient(gcp_config.PROJECT_ID)
        return secret_client.get_secret(gcp_config.SECRET_ID_TWITTER)
    except Exception as e:
        logger.warning(f"Não foi possível obter token do Secret Manager: {e}")
    
    # Usa o token padrão da configuração
    if twitter_accounts_config.DEFAULT_BEARER_TOKEN:
        return twitter_accounts_config.DEFAULT_BEARER_TOKEN
    
    # Tenta obter de variável de ambiente
    token = os.environ.get("TWITTER_BEARER_TOKEN")
    if token:
        return token
    
    raise ValueError("Bearer Token do Twitter não configurado")


def get_bigquery_writer() -> BigQueryWriter:
    """
    Obtém uma instância do BigQueryWriter com credenciais.
    
    Returns:
        Instância do BigQueryWriter
    """
    try:
        # Tenta obter credenciais do Secret Manager
        secret_client = SecretManagerClient(gcp_config.PROJECT_ID)
        credentials = secret_client.get_credentials_from_secret(gcp_config.SECRET_ID_BQ)
        return BigQueryWriter(
            project_id=gcp_config.PROJECT_ID,
            dataset_id=gcp_config.DATASET_ID,
            credentials=credentials
        )
    except Exception as e:
        logger.warning(f"Usando credenciais padrão do ambiente: {e}")
        return BigQueryWriter(
            project_id=gcp_config.PROJECT_ID,
            dataset_id=gcp_config.DATASET_ID
        )


def ensure_tables_exist(writer: BigQueryWriter) -> Dict[str, bool]:
    """
    Garante que todas as tabelas existem no BigQuery.
    
    Args:
        writer: Instância do BigQueryWriter
        
    Returns:
        Dicionário com status de cada tabela
    """
    results = {}
    
    for table_config in tables_config.get_all_tables():
        success = writer.ensure_table_exists(
            table_name=table_config.name,
            schema=table_config.fields,
            description=table_config.description
        )
        results[table_config.name] = success
    
    return results


# =============================================================================
# FUNÇÕES DE EXTRAÇÃO
# =============================================================================

def extract_and_load_profile(
    account: TwitterAccount,
    writer: BigQueryWriter,
    bearer_token: str
) -> Dict[str, Any]:
    """
    Extrai e carrega dados do perfil de uma conta.
    
    Args:
        account: Conta do Twitter
        writer: Instância do BigQueryWriter
        bearer_token: Token de autenticação
        
    Returns:
        Resultado da operação
    """
    client = TwitterClient(
        bearer_token=bearer_token,
        request_delay=twitter_api_config.REQUEST_DELAY,
        request_timeout=twitter_api_config.REQUEST_TIMEOUT
    )
    extractor = TwitterDataExtractor(client, date_config.TIMEZONE)
    
    # Extrair dados do perfil
    profile_data = extractor.extract_profile_data(
        username=account.username,
        user_id=account.user_id,
        account_name=account.name
    )
    
    if not profile_data:
        return {"status": "error", "message": "Não foi possível extrair dados do perfil"}
    
    # Carregar no BigQuery
    result = writer.insert_rows(
        table_name=tables_config.PERFIL.name,
        rows=[profile_data]
    )
    
    return {
        "table": tables_config.PERFIL.name,
        "account": account.username,
        **result
    }


def extract_and_load_posts(
    account: TwitterAccount,
    writer: BigQueryWriter,
    bearer_token: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Extrai e carrega dados dos posts de uma conta.
    
    Args:
        account: Conta do Twitter
        writer: Instância do BigQueryWriter
        bearer_token: Token de autenticação
        start_date: Data de início
        end_date: Data de fim
        
    Returns:
        Resultado da operação
    """
    client = TwitterClient(
        bearer_token=bearer_token,
        request_delay=twitter_api_config.REQUEST_DELAY,
        request_timeout=twitter_api_config.REQUEST_TIMEOUT
    )
    extractor = TwitterDataExtractor(client, date_config.TIMEZONE)
    
    # Extrair dados dos posts
    posts_data = extractor.extract_posts_data(
        username=account.username,
        user_id=account.user_id,
        account_name=account.name,
        start_date=start_date,
        end_date=end_date
    )
    
    if not posts_data:
        return {"status": "warning", "message": "Nenhum post encontrado no período", "rows_inserted": 0}
    
    # Carregar no BigQuery
    result = writer.insert_rows(
        table_name=tables_config.POSTS.name,
        rows=posts_data
    )
    
    return {
        "table": tables_config.POSTS.name,
        "account": account.username,
        **result
    }


def extract_and_load_additional_metrics(
    account: TwitterAccount,
    writer: BigQueryWriter,
    bearer_token: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Extrai e carrega métricas adicionais dos posts de uma conta.
    
    Args:
        account: Conta do Twitter
        writer: Instância do BigQueryWriter
        bearer_token: Token de autenticação
        start_date: Data de início
        end_date: Data de fim
        
    Returns:
        Resultado da operação
    """
    client = TwitterClient(
        bearer_token=bearer_token,
        request_delay=twitter_api_config.REQUEST_DELAY,
        request_timeout=twitter_api_config.REQUEST_TIMEOUT
    )
    extractor = TwitterDataExtractor(client, date_config.TIMEZONE)
    
    # Extrair métricas adicionais
    metrics_data = extractor.extract_additional_metrics(
        username=account.username,
        user_id=account.user_id,
        account_name=account.name,
        start_date=start_date,
        end_date=end_date
    )
    
    if not metrics_data:
        return {"status": "warning", "message": "Nenhuma métrica adicional encontrada", "rows_inserted": 0}
    
    # Carregar no BigQuery
    result = writer.insert_rows(
        table_name=tables_config.METRICAS_ADICIONAIS.name,
        rows=metrics_data
    )
    
    return {
        "table": tables_config.METRICAS_ADICIONAIS.name,
        "account": account.username,
        **result
    }


def process_account(
    account: TwitterAccount,
    start_date: datetime = None,
    end_date: datetime = None
) -> Dict[str, Any]:
    """
    Processa todos os relatórios para uma conta.
    
    Args:
        account: Conta do Twitter
        start_date: Data de início (opcional)
        end_date: Data de fim (opcional)
        
    Returns:
        Resultado da operação
    """
    # Calcular datas se não fornecidas
    if start_date is None or end_date is None:
        start_date, end_date = get_date_range()
    
    # Obter token e writer
    bearer_token = get_bearer_token(account)
    writer = get_bigquery_writer()
    
    # Garantir que as tabelas existem
    ensure_tables_exist(writer)
    
    results = {
        "account": account.username,
        "account_name": account.name,
        "period": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "reports": {}
    }
    
    # Extrair e carregar perfil
    try:
        results["reports"]["profile"] = extract_and_load_profile(
            account, writer, bearer_token
        )
    except Exception as e:
        logger.error(f"Erro ao processar perfil de @{account.username}: {e}")
        results["reports"]["profile"] = {"status": "error", "message": str(e)}
    
    # Extrair e carregar posts
    try:
        results["reports"]["posts"] = extract_and_load_posts(
            account, writer, bearer_token, start_date, end_date
        )
    except Exception as e:
        logger.error(f"Erro ao processar posts de @{account.username}: {e}")
        results["reports"]["posts"] = {"status": "error", "message": str(e)}
    
    # Extrair e carregar métricas adicionais
    try:
        results["reports"]["additional_metrics"] = extract_and_load_additional_metrics(
            account, writer, bearer_token, start_date, end_date
        )
    except Exception as e:
        logger.error(f"Erro ao processar métricas adicionais de @{account.username}: {e}")
        results["reports"]["additional_metrics"] = {"status": "error", "message": str(e)}
    
    # Calcular resumo
    total_rows = 0
    successful = 0
    failed = 0
    
    for report_name, report_result in results["reports"].items():
        if report_result.get("status") == "success":
            successful += 1
            total_rows += report_result.get("rows_inserted", 0)
        elif report_result.get("status") == "error":
            failed += 1
        else:
            successful += 1  # warning também é considerado sucesso
    
    results["summary"] = {
        "total_reports": len(results["reports"]),
        "successful": successful,
        "failed": failed,
        "total_rows_inserted": total_rows
    }
    
    return results


# =============================================================================
# ENDPOINTS DA API
# =============================================================================

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Twitter API Extractor",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/config", methods=["GET"])
def get_config():
    """Retorna a configuração atual da API."""
    return jsonify({
        "project_id": gcp_config.PROJECT_ID,
        "dataset_id": gcp_config.DATASET_ID,
        "date_range": {
            "days_start": date_config.DAYS_START,
            "days_end": date_config.DAYS_END,
            "timezone": date_config.TIMEZONE
        },
        "accounts_count": len(twitter_accounts_config.ACCOUNTS),
        "tables": [t.name for t in tables_config.get_all_tables()]
    })


@app.route("/tables", methods=["GET"])
def list_tables():
    """Lista todas as tabelas configuradas."""
    tables = []
    for table in tables_config.get_all_tables():
        tables.append({
            "name": table.name,
            "description": table.description,
            "fields_count": len(table.fields)
        })
    return jsonify({"tables": tables})


@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Lista todas as contas configuradas."""
    accounts = []
    for account in twitter_accounts_config.ACCOUNTS:
        accounts.append({
            "username": account.username,
            "user_id": account.user_id,
            "name": account.name
        })
    return jsonify({"accounts": accounts})


@app.route("/report/all", methods=["POST"])
def run_all_reports():
    """
    Executa todos os relatórios para uma conta específica.
    
    Request Body:
        {
            "username": "conta_twitter",
            "user_id": "123456789",
            "start_date": "2024-01-01",  # opcional
            "end_date": "2024-01-07"     # opcional
        }
    """
    data = request.get_json() or {}
    
    # Obter conta
    username = data.get("username")
    user_id = data.get("user_id")
    
    if not username and not user_id:
        return jsonify({
            "status": "error",
            "message": "É necessário fornecer 'username' ou 'user_id'"
        }), 400
    
    # Buscar conta na configuração ou criar uma nova
    account = None
    for acc in twitter_accounts_config.ACCOUNTS:
        if acc.username == username or acc.user_id == user_id:
            account = acc
            break
    
    if not account:
        if username and user_id:
            account = TwitterAccount(
                username=username,
                user_id=user_id,
                name=data.get("name", username)
            )
        else:
            return jsonify({
                "status": "error",
                "message": "Conta não encontrada na configuração. Forneça 'username' e 'user_id'."
            }), 404
    
    # Processar datas
    start_date = None
    end_date = None
    
    if data.get("start_date") and data.get("end_date"):
        tz = pytz.timezone(date_config.TIMEZONE)
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").replace(tzinfo=tz)
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(tzinfo=tz)
    
    # Executar
    try:
        result = process_account(account, start_date, end_date)
        return jsonify({"status": "success", **result})
    except Exception as e:
        logger.error(f"Erro ao processar conta @{account.username}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "account": account.username
        }), 500


@app.route("/report/batch", methods=["POST"])
def run_batch_reports():
    """
    Executa relatórios para múltiplas contas.
    
    Request Body:
        {
            "accounts": [
                {"username": "conta1", "user_id": "123"},
                {"username": "conta2", "user_id": "456"}
            ],
            "start_date": "2024-01-01",  # opcional
            "end_date": "2024-01-07"     # opcional
        }
    
    Se 'accounts' não for fornecido, usa todas as contas configuradas.
    """
    data = request.get_json() or {}
    
    # Obter lista de contas
    accounts_data = data.get("accounts")
    
    if accounts_data:
        accounts = [
            TwitterAccount(
                username=acc.get("username"),
                user_id=acc.get("user_id"),
                name=acc.get("name", acc.get("username"))
            )
            for acc in accounts_data
        ]
    else:
        accounts = twitter_accounts_config.ACCOUNTS
    
    if not accounts:
        return jsonify({
            "status": "error",
            "message": "Nenhuma conta configurada ou fornecida"
        }), 400
    
    # Processar datas
    start_date = None
    end_date = None
    
    if data.get("start_date") and data.get("end_date"):
        tz = pytz.timezone(date_config.TIMEZONE)
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").replace(tzinfo=tz)
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(tzinfo=tz)
    
    # Executar para cada conta
    results = []
    for account in accounts:
        try:
            result = process_account(account, start_date, end_date)
            results.append(result)
        except Exception as e:
            logger.error(f"Erro ao processar conta @{account.username}: {e}")
            results.append({
                "account": account.username,
                "status": "error",
                "message": str(e)
            })
    
    # Calcular resumo geral
    total_accounts = len(results)
    successful_accounts = sum(1 for r in results if r.get("summary", {}).get("failed", 1) == 0)
    total_rows = sum(r.get("summary", {}).get("total_rows_inserted", 0) for r in results)
    
    return jsonify({
        "status": "success",
        "summary": {
            "total_accounts": total_accounts,
            "successful_accounts": successful_accounts,
            "failed_accounts": total_accounts - successful_accounts,
            "total_rows_inserted": total_rows
        },
        "results": results
    })


@app.route("/report/profile/<username>", methods=["POST"])
def run_profile_report(username: str):
    """
    Executa apenas o relatório de perfil para uma conta.
    
    Args:
        username: Username da conta do Twitter
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    # Buscar conta
    account = None
    for acc in twitter_accounts_config.ACCOUNTS:
        if acc.username == username:
            account = acc
            break
    
    if not account:
        if user_id:
            account = TwitterAccount(
                username=username,
                user_id=user_id,
                name=data.get("name", username)
            )
        else:
            return jsonify({
                "status": "error",
                "message": f"Conta @{username} não encontrada. Forneça 'user_id' no body."
            }), 404
    
    try:
        bearer_token = get_bearer_token(account)
        writer = get_bigquery_writer()
        ensure_tables_exist(writer)
        
        result = extract_and_load_profile(account, writer, bearer_token)
        return jsonify({"status": "success", **result})
    except Exception as e:
        logger.error(f"Erro ao processar perfil de @{username}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "account": username
        }), 500


@app.route("/report/posts/<username>", methods=["POST"])
def run_posts_report(username: str):
    """
    Executa apenas o relatório de posts para uma conta.
    
    Args:
        username: Username da conta do Twitter
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    # Buscar conta
    account = None
    for acc in twitter_accounts_config.ACCOUNTS:
        if acc.username == username:
            account = acc
            break
    
    if not account:
        if user_id:
            account = TwitterAccount(
                username=username,
                user_id=user_id,
                name=data.get("name", username)
            )
        else:
            return jsonify({
                "status": "error",
                "message": f"Conta @{username} não encontrada. Forneça 'user_id' no body."
            }), 404
    
    # Processar datas
    start_date, end_date = get_date_range()
    
    if data.get("start_date") and data.get("end_date"):
        tz = pytz.timezone(date_config.TIMEZONE)
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").replace(tzinfo=tz)
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(tzinfo=tz)
    
    try:
        bearer_token = get_bearer_token(account)
        writer = get_bigquery_writer()
        ensure_tables_exist(writer)
        
        result = extract_and_load_posts(account, writer, bearer_token, start_date, end_date)
        return jsonify({"status": "success", **result})
    except Exception as e:
        logger.error(f"Erro ao processar posts de @{username}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "account": username
        }), 500


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal para iniciar o servidor."""
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
