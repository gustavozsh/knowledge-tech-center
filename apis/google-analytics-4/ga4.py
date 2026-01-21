"""
Módulo de Extração de Dados do Google Analytics 4.

Este módulo contém todas as funções para extrair dados do GA4
usando a API Data v1beta.

Autor: Manus AI
Data: Janeiro de 2026
Versão: 2.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÃO DE RELATÓRIOS
# =============================================================================

@dataclass
class ReportConfig:
    """Configuração de um relatório GA4."""
    name: str
    table_name: str
    dimensions: List[str]
    metrics: List[str]
    description: str = ""


# Configurações de relatórios por categoria
DIMENSION_REPORTS = {
    "USUARIO": ReportConfig(
        name="Dimensões de Usuário",
        table_name="TB_001_GA4_DIM_USUARIO",
        dimensions=["date", "newVsReturning", "userAgeBracket", "userGender"],
        metrics=["activeUsers", "newUsers", "totalUsers"],
        description="Dados demográficos e comportamentais dos usuários"
    ),
    "GEOGRAFICA": ReportConfig(
        name="Dimensões Geográficas",
        table_name="TB_002_GA4_DIM_GEOGRAFICA",
        dimensions=["date", "city", "cityId", "country", "countryId", "region", "continent"],
        metrics=["activeUsers", "sessions"],
        description="Localização geográfica dos usuários"
    ),
    "DISPOSITIVO": ReportConfig(
        name="Dimensões de Dispositivo",
        table_name="TB_003_GA4_DIM_DISPOSITIVO",
        dimensions=["date", "browser", "deviceCategory", "operatingSystem", "platform", "screenResolution"],
        metrics=["activeUsers", "sessions"],
        description="Informações de dispositivo e tecnologia"
    ),
    "AQUISICAO": ReportConfig(
        name="Dimensões de Aquisição",
        table_name="TB_004_GA4_DIM_AQUISICAO",
        dimensions=["date", "sessionSource", "sessionMedium", "sessionSourceMedium", "sessionCampaignId", "sessionCampaignName", "sessionDefaultChannelGroup"],
        metrics=["activeUsers", "sessions", "newUsers"],
        description="Origem e campanhas de aquisição"
    ),
    "PAGINA": ReportConfig(
        name="Dimensões de Página",
        table_name="TB_005_GA4_DIM_PAGINA",
        dimensions=["date", "pagePath", "pageTitle", "landingPage", "hostName"],
        metrics=["screenPageViews", "activeUsers"],
        description="Páginas e conteúdo acessado"
    ),
    "EVENTO": ReportConfig(
        name="Dimensões de Evento",
        table_name="TB_006_GA4_DIM_EVENTO",
        dimensions=["date", "eventName", "isConversionEvent"],
        metrics=["eventCount", "activeUsers"],
        description="Eventos e conversões"
    ),
    "PUBLICO": ReportConfig(
        name="Dimensões de Público",
        table_name="TB_007_GA4_DIM_PUBLICO",
        dimensions=["date", "audienceId", "audienceName"],
        metrics=["activeUsers"],
        description="Públicos-alvo configurados"
    ),
}

METRIC_REPORTS = {
    "USUARIOS": ReportConfig(
        name="Métricas de Usuários",
        table_name="TB_008_GA4_MET_USUARIOS",
        dimensions=["date"],
        metrics=["activeUsers", "newUsers", "totalUsers", "dauPerMau", "dauPerWau", "wauPerMau"],
        description="Métricas de usuários ativos e novos"
    ),
    "SESSAO": ReportConfig(
        name="Métricas de Sessão",
        table_name="TB_009_GA4_MET_SESSAO",
        dimensions=["date"],
        metrics=["sessions", "sessionsPerUser", "averageSessionDuration", "bounceRate", "engagedSessions", "engagementRate"],
        description="Métricas de sessões e engajamento"
    ),
    "EVENTOS": ReportConfig(
        name="Métricas de Eventos",
        table_name="TB_010_GA4_MET_EVENTOS",
        dimensions=["date"],
        metrics=["eventCount", "eventCountPerUser", "eventsPerSession", "conversions"],
        description="Métricas de eventos e conversões"
    ),
    "VISUALIZACAO": ReportConfig(
        name="Métricas de Visualização",
        table_name="TB_011_GA4_MET_VISUALIZACAO",
        dimensions=["date"],
        metrics=["screenPageViews", "screenPageViewsPerSession", "screenPageViewsPerUser"],
        description="Métricas de visualizações de página"
    ),
    "ECOMMERCE": ReportConfig(
        name="Métricas de E-commerce",
        table_name="TB_012_GA4_MET_ECOMMERCE",
        dimensions=["date"],
        metrics=["totalRevenue", "purchaseRevenue", "transactions", "ecommercePurchases", "averagePurchaseRevenue"],
        description="Métricas de receita e transações"
    ),
}


# =============================================================================
# FUNÇÕES DE EXTRAÇÃO
# =============================================================================

def get_date_range(days_back: int = 1, timezone: str = "America/Sao_Paulo") -> tuple:
    """
    Calcula o range de datas para extração (D-1 por padrão).
    
    Args:
        days_back: Quantos dias atrás (padrão: 1 = ontem)
        timezone: Timezone para cálculo
        
    Returns:
        Tupla (start_date, end_date) no formato YYYY-MM-DD
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    target_date = now - timedelta(days=days_back)
    date_str = target_date.strftime("%Y-%m-%d")
    
    return date_str, date_str


def run_ga4_report(
    ga4_client,
    property_id: str,
    dimensions: List[str],
    metrics: List[str],
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Executa um relatório no GA4.
    
    Args:
        ga4_client: Cliente do GA4 (obtido via auth.get_ga4_client)
        property_id: ID da propriedade GA4 (ex: "properties/123456789")
        dimensions: Lista de dimensões
        metrics: Lista de métricas
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        
    Returns:
        Lista de dicionários com os dados
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
    
    logger.info(f"Executando relatório GA4 para {property_id}")
    logger.info(f"  Período: {start_date} a {end_date}")
    logger.info(f"  Dimensões: {dimensions}")
    logger.info(f"  Métricas: {metrics}")
    
    # Construir request
    request = RunReportRequest(
        property=property_id,
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=100000
    )
    
    # Executar
    try:
        response = ga4_client.run_report(request)
    except Exception as e:
        logger.error(f"Erro ao executar relatório: {e}")
        raise
    
    # Processar resposta
    rows = []
    
    for row in response.rows:
        row_data = {}
        
        # Adicionar dimensões
        for i, dim_value in enumerate(row.dimension_values):
            dim_name = dimensions[i]
            row_data[dim_name] = dim_value.value
        
        # Adicionar métricas
        for i, metric_value in enumerate(row.metric_values):
            metric_name = metrics[i]
            # Converter para número se possível
            try:
                if "." in metric_value.value:
                    row_data[metric_name] = float(metric_value.value)
                else:
                    row_data[metric_name] = int(metric_value.value)
            except ValueError:
                row_data[metric_name] = metric_value.value
        
        rows.append(row_data)
    
    logger.info(f"  ✓ {len(rows)} linhas retornadas")
    return rows


def extract_dimension_report(
    ga4_client,
    property_id: str,
    report_key: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Extrai um relatório de dimensão específico.
    
    Args:
        ga4_client: Cliente do GA4
        property_id: ID da propriedade
        report_key: Chave do relatório (ex: "USUARIO", "GEOGRAFICA")
        start_date: Data de início
        end_date: Data de fim
        
    Returns:
        Dicionário com dados do relatório e metadados
    """
    if report_key not in DIMENSION_REPORTS:
        raise ValueError(f"Relatório de dimensão não encontrado: {report_key}")
    
    config = DIMENSION_REPORTS[report_key]
    
    logger.info(f"Extraindo: {config.name}")
    
    rows = run_ga4_report(
        ga4_client=ga4_client,
        property_id=property_id,
        dimensions=config.dimensions,
        metrics=config.metrics,
        start_date=start_date,
        end_date=end_date
    )
    
    # Adicionar metadados
    extraction_time = datetime.now().isoformat()
    for row in rows:
        row["property_id"] = property_id.replace("properties/", "")
        row["extraction_timestamp"] = extraction_time
    
    return {
        "report_key": report_key,
        "report_name": config.name,
        "table_name": config.table_name,
        "rows_count": len(rows),
        "data": rows
    }


def extract_metric_report(
    ga4_client,
    property_id: str,
    report_key: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Extrai um relatório de métrica específico.
    
    Args:
        ga4_client: Cliente do GA4
        property_id: ID da propriedade
        report_key: Chave do relatório (ex: "USUARIOS", "SESSAO")
        start_date: Data de início
        end_date: Data de fim
        
    Returns:
        Dicionário com dados do relatório e metadados
    """
    if report_key not in METRIC_REPORTS:
        raise ValueError(f"Relatório de métrica não encontrado: {report_key}")
    
    config = METRIC_REPORTS[report_key]
    
    logger.info(f"Extraindo: {config.name}")
    
    rows = run_ga4_report(
        ga4_client=ga4_client,
        property_id=property_id,
        dimensions=config.dimensions,
        metrics=config.metrics,
        start_date=start_date,
        end_date=end_date
    )
    
    # Adicionar metadados
    extraction_time = datetime.now().isoformat()
    for row in rows:
        row["property_id"] = property_id.replace("properties/", "")
        row["extraction_timestamp"] = extraction_time
    
    return {
        "report_key": report_key,
        "report_name": config.name,
        "table_name": config.table_name,
        "rows_count": len(rows),
        "data": rows
    }


def extract_all_reports(
    ga4_client,
    property_id: str,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Extrai todos os relatórios configurados.
    
    Args:
        ga4_client: Cliente do GA4
        property_id: ID da propriedade
        start_date: Data de início (opcional, usa D-1 se não fornecido)
        end_date: Data de fim (opcional, usa D-1 se não fornecido)
        
    Returns:
        Dicionário com todos os relatórios extraídos
    """
    # Calcular datas se não fornecidas
    if not start_date or not end_date:
        start_date, end_date = get_date_range()
    
    logger.info("=" * 50)
    logger.info("EXTRAINDO TODOS OS RELATÓRIOS GA4")
    logger.info(f"Property: {property_id}")
    logger.info(f"Período: {start_date} a {end_date}")
    logger.info("=" * 50)
    
    results = {
        "property_id": property_id,
        "period": {"start": start_date, "end": end_date},
        "dimensions": {},
        "metrics": {},
        "summary": {
            "total_reports": 0,
            "successful": 0,
            "failed": 0,
            "total_rows": 0
        }
    }
    
    # Extrair relatórios de dimensão
    for key in DIMENSION_REPORTS:
        try:
            report = extract_dimension_report(
                ga4_client, property_id, key, start_date, end_date
            )
            results["dimensions"][key] = report
            results["summary"]["successful"] += 1
            results["summary"]["total_rows"] += report["rows_count"]
        except Exception as e:
            logger.error(f"Erro ao extrair {key}: {e}")
            results["dimensions"][key] = {"error": str(e)}
            results["summary"]["failed"] += 1
        
        results["summary"]["total_reports"] += 1
    
    # Extrair relatórios de métrica
    for key in METRIC_REPORTS:
        try:
            report = extract_metric_report(
                ga4_client, property_id, key, start_date, end_date
            )
            results["metrics"][key] = report
            results["summary"]["successful"] += 1
            results["summary"]["total_rows"] += report["rows_count"]
        except Exception as e:
            logger.error(f"Erro ao extrair {key}: {e}")
            results["metrics"][key] = {"error": str(e)}
            results["summary"]["failed"] += 1
        
        results["summary"]["total_reports"] += 1
    
    logger.info("=" * 50)
    logger.info("EXTRAÇÃO CONCLUÍDA")
    logger.info(f"Relatórios: {results['summary']['successful']}/{results['summary']['total_reports']}")
    logger.info(f"Total de linhas: {results['summary']['total_rows']}")
    logger.info("=" * 50)
    
    return results


def list_available_reports() -> Dict[str, List[str]]:
    """
    Lista todos os relatórios disponíveis.
    
    Returns:
        Dicionário com listas de relatórios de dimensão e métrica
    """
    return {
        "dimensions": list(DIMENSION_REPORTS.keys()),
        "metrics": list(METRIC_REPORTS.keys()),
        "dimension_details": {
            k: {"name": v.name, "table": v.table_name, "description": v.description}
            for k, v in DIMENSION_REPORTS.items()
        },
        "metric_details": {
            k: {"name": v.name, "table": v.table_name, "description": v.description}
            for k, v in METRIC_REPORTS.items()
        }
    }
