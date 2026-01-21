"""
Configurações da API Google Analytics 4

Este arquivo contém todas as configurações necessárias para a execução da API,
incluindo nomes de tabelas, dimensões, métricas e configurações do BigQuery.

Versão Python: 3.11+
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


# =============================================================================
# CONFIGURAÇÕES DO PROJETO GCP
# =============================================================================

class GCPConfig:
    """Configurações do Google Cloud Platform"""
    
    # Projeto GCP
    PROJECT_ID = "cadastra-yduqs-uat"
    
    # Dataset do BigQuery
    DATASET_ID = "RAW"
    
    # Secret Manager - ID do secret com as credenciais do GA4
    SECRET_ID = "ga4-credentials"
    
    # Região padrão
    REGION = "us-central1"


# =============================================================================
# CONFIGURAÇÕES DAS TABELAS DO BIGQUERY
# =============================================================================

class TableConfig:
    """Configurações das tabelas do BigQuery"""
    
    # Prefixo padrão para tabelas GA4
    PREFIX = "TB"
    
    # Tabelas de Dimensões
    TABLES_DIMENSIONS = {
        "TB_001_GA4_DIM_USUARIO": {
            "description": "Dimensões de usuário do Google Analytics 4",
            "dimensions": ["newVsReturning", "userAgeBracket", "userGender"],
            "base_metrics": ["activeUsers", "newUsers", "totalUsers"]
        },
        "TB_002_GA4_DIM_GEOGRAFICA": {
            "description": "Dimensões geográficas do Google Analytics 4",
            "dimensions": ["city", "cityId", "country", "countryId", "region", "continent", "continentId"],
            "base_metrics": ["activeUsers", "sessions", "screenPageViews"]
        },
        "TB_003_GA4_DIM_DISPOSITIVO": {
            "description": "Dimensões de dispositivo e tecnologia do Google Analytics 4",
            "dimensions": ["browser", "deviceCategory", "operatingSystem", "operatingSystemVersion", "platform", "screenResolution", "mobileDeviceBranding", "mobileDeviceModel"],
            "base_metrics": ["activeUsers", "sessions", "screenPageViews"]
        },
        "TB_004_GA4_DIM_AQUISICAO": {
            "description": "Dimensões de aquisição e campanha do Google Analytics 4",
            "dimensions": ["source", "medium", "sourceMedium", "campaignId", "campaignName", "defaultChannelGroup", "sessionSource", "sessionMedium", "sessionSourceMedium", "sessionCampaignId", "sessionCampaignName", "sessionDefaultChannelGroup", "firstUserSource", "firstUserMedium", "firstUserSourceMedium", "firstUserCampaignId", "firstUserCampaignName", "firstUserDefaultChannelGroup"],
            "base_metrics": ["activeUsers", "sessions", "newUsers", "conversions"]
        },
        "TB_005_GA4_DIM_PAGINA": {
            "description": "Dimensões de página e conteúdo do Google Analytics 4",
            "dimensions": ["pagePath", "pageTitle", "landingPage", "hostName", "contentGroup", "pagePathPlusQueryString", "landingPagePlusQueryString"],
            "base_metrics": ["activeUsers", "sessions", "screenPageViews", "averageSessionDuration"]
        },
        "TB_006_GA4_DIM_EVENTO": {
            "description": "Dimensões de evento do Google Analytics 4",
            "dimensions": ["eventName", "isConversionEvent"],
            "base_metrics": ["eventCount", "eventCountPerUser", "conversions", "eventValue"]
        },
        "TB_007_GA4_DIM_PUBLICO": {
            "description": "Dimensões de público-alvo do Google Analytics 4",
            "dimensions": ["audienceId", "audienceName"],
            "base_metrics": ["activeUsers", "totalUsers", "newUsers"]
        }
    }
    
    # Tabelas de Métricas
    TABLES_METRICS = {
        "TB_008_GA4_MET_USUARIOS": {
            "description": "Métricas de usuários do Google Analytics 4",
            "metrics": ["activeUsers", "newUsers", "totalUsers", "active1DayUsers", "active7DayUsers", "active28DayUsers", "dauPerMau", "dauPerWau", "wauPerMau"],
            "base_dimension": "date"
        },
        "TB_009_GA4_MET_SESSAO": {
            "description": "Métricas de sessão do Google Analytics 4",
            "metrics": ["sessions", "sessionsPerUser", "averageSessionDuration", "bounceRate", "engagedSessions", "engagementRate", "userEngagementDuration"],
            "base_dimension": "date"
        },
        "TB_010_GA4_MET_EVENTOS": {
            "description": "Métricas de eventos do Google Analytics 4",
            "metrics": ["eventCount", "eventCountPerUser", "eventsPerSession", "conversions", "eventValue"],
            "base_dimension": "date"
        },
        "TB_011_GA4_MET_VISUALIZACAO": {
            "description": "Métricas de visualização do Google Analytics 4",
            "metrics": ["screenPageViews", "screenPageViewsPerSession", "screenPageViewsPerUser"],
            "base_dimension": "date"
        },
        "TB_012_GA4_MET_ECOMMERCE": {
            "description": "Métricas de e-commerce do Google Analytics 4",
            "metrics": ["totalRevenue", "purchaseRevenue", "transactions", "ecommercePurchases", "averagePurchaseRevenue", "averageRevenuePerUser", "addToCarts", "checkouts", "cartToViewRate", "purchaseToViewRate", "itemRevenue", "itemsPurchased"],
            "base_dimension": "date"
        }
    }
    
    @classmethod
    def get_all_tables(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna todas as tabelas configuradas"""
        all_tables = {}
        all_tables.update(cls.TABLES_DIMENSIONS)
        all_tables.update(cls.TABLES_METRICS)
        return all_tables
    
    @classmethod
    def get_dimension_tables(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna apenas as tabelas de dimensões"""
        return cls.TABLES_DIMENSIONS
    
    @classmethod
    def get_metric_tables(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna apenas as tabelas de métricas"""
        return cls.TABLES_METRICS


# =============================================================================
# CONFIGURAÇÕES DE PROPRIEDADES GA4
# =============================================================================

class GA4Properties:
    """
    Configurações das propriedades GA4 a serem consultadas.
    
    Adicione aqui os IDs das propriedades GA4 que deseja consultar.
    O ID pode ser encontrado em: Admin > Propriedade > Detalhes da propriedade
    """
    
    # Lista de propriedades GA4 (adicione os IDs conforme necessário)
    PROPERTIES = [
        # Exemplo: {"id": "123456789", "name": "Site Principal"},
        # {"id": "987654321", "name": "App Mobile"},
    ]
    
    @classmethod
    def get_property_ids(cls) -> List[str]:
        """Retorna lista de IDs das propriedades"""
        return [prop["id"] for prop in cls.PROPERTIES]
    
    @classmethod
    def add_property(cls, property_id: str, name: str = None):
        """Adiciona uma nova propriedade à lista"""
        cls.PROPERTIES.append({
            "id": property_id,
            "name": name or f"Property {property_id}"
        })


# =============================================================================
# CONFIGURAÇÕES DE PERÍODO
# =============================================================================

class DateConfig:
    """Configurações de período para os relatórios"""
    
    # Período padrão: D-1 (dia anterior)
    DEFAULT_START_DATE = "yesterday"
    DEFAULT_END_DATE = "yesterday"
    
    # Formatos de data
    DATE_FORMAT = "%Y-%m-%d"
    DATE_FORMAT_BQ = "YYYYMMDD"


# =============================================================================
# CONFIGURAÇÕES DE LIMITE E PAGINAÇÃO
# =============================================================================

class PaginationConfig:
    """Configurações de paginação para requisições à API"""
    
    # Limite máximo de linhas por requisição
    MAX_ROWS_PER_REQUEST = 100000
    
    # Limite padrão
    DEFAULT_LIMIT = 10000
    
    # Offset inicial
    DEFAULT_OFFSET = 0


# =============================================================================
# MAPEAMENTO DE DIMENSÕES E MÉTRICAS
# =============================================================================

class DimensionsMapping:
    """Mapeamento completo de dimensões disponíveis na API GA4"""
    
    # Dimensões de Usuário
    USUARIO = [
        "newVsReturning",
        "userAgeBracket", 
        "userGender"
    ]
    
    # Dimensões Geográficas
    GEOGRAFICA = [
        "city",
        "cityId",
        "country",
        "countryId",
        "region",
        "continent",
        "continentId",
        "subContinent"
    ]
    
    # Dimensões de Dispositivo/Tecnologia
    DISPOSITIVO = [
        "browser",
        "deviceCategory",
        "operatingSystem",
        "operatingSystemVersion",
        "operatingSystemWithVersion",
        "platform",
        "platformDeviceCategory",
        "screenResolution",
        "mobileDeviceBranding",
        "mobileDeviceMarketingName",
        "mobileDeviceModel"
    ]
    
    # Dimensões de Aquisição/Campanha
    AQUISICAO = [
        "source",
        "medium",
        "sourceMedium",
        "sourcePlatform",
        "campaignId",
        "campaignName",
        "defaultChannelGroup",
        "sessionSource",
        "sessionMedium",
        "sessionSourceMedium",
        "sessionSourcePlatform",
        "sessionCampaignId",
        "sessionCampaignName",
        "sessionDefaultChannelGroup",
        "firstUserSource",
        "firstUserMedium",
        "firstUserSourceMedium",
        "firstUserSourcePlatform",
        "firstUserCampaignId",
        "firstUserCampaignName",
        "firstUserDefaultChannelGroup"
    ]
    
    # Dimensões de Página/Conteúdo
    PAGINA = [
        "pagePath",
        "pagePathPlusQueryString",
        "pageTitle",
        "landingPage",
        "landingPagePlusQueryString",
        "hostName",
        "contentGroup",
        "contentId",
        "contentType",
        "pageLocation",
        "pageReferrer"
    ]
    
    # Dimensões de Evento
    EVENTO = [
        "eventName",
        "isConversionEvent"
    ]
    
    # Dimensões de Público-alvo
    PUBLICO = [
        "audienceId",
        "audienceName",
        "audienceResourceName"
    ]
    
    # Dimensões de Data/Hora
    DATA_HORA = [
        "date",
        "dateHour",
        "dateHourMinute",
        "day",
        "dayOfWeek",
        "dayOfWeekName",
        "hour",
        "minute",
        "month",
        "week",
        "year",
        "yearMonth",
        "yearWeek"
    ]


class MetricsMapping:
    """Mapeamento completo de métricas disponíveis na API GA4"""
    
    # Métricas de Usuários
    USUARIOS = [
        "activeUsers",
        "newUsers",
        "totalUsers",
        "active1DayUsers",
        "active7DayUsers",
        "active28DayUsers",
        "dauPerMau",
        "dauPerWau",
        "wauPerMau"
    ]
    
    # Métricas de Sessão
    SESSAO = [
        "sessions",
        "sessionsPerUser",
        "averageSessionDuration",
        "bounceRate",
        "engagedSessions",
        "engagementRate",
        "userEngagementDuration"
    ]
    
    # Métricas de Eventos
    EVENTOS = [
        "eventCount",
        "eventCountPerUser",
        "eventsPerSession",
        "conversions",
        "eventValue"
    ]
    
    # Métricas de Visualização
    VISUALIZACAO = [
        "screenPageViews",
        "screenPageViewsPerSession",
        "screenPageViewsPerUser"
    ]
    
    # Métricas de E-commerce
    ECOMMERCE = [
        "totalRevenue",
        "purchaseRevenue",
        "transactions",
        "ecommercePurchases",
        "averagePurchaseRevenue",
        "averagePurchaseRevenuePerPayingUser",
        "averagePurchaseRevenuePerUser",
        "averageRevenuePerUser",
        "addToCarts",
        "checkouts",
        "cartToViewRate",
        "purchaseToViewRate",
        "purchaserConversionRate",
        "itemRevenue",
        "itemsPurchased",
        "itemsAddedToCart",
        "itemsCheckedOut",
        "itemsViewed",
        "refundAmount",
        "shippingAmount",
        "taxAmount"
    ]


# =============================================================================
# CONFIGURAÇÕES DO AIRFLOW
# =============================================================================

class AirflowConfig:
    """Configurações para a DAG do Airflow"""
    
    # Nome da DAG
    DAG_ID = "dag_ga4_daily_load"
    
    # Descrição
    DESCRIPTION = "DAG para carga diária de dados do Google Analytics 4 para o BigQuery"
    
    # Schedule (diário às 06:00 UTC)
    SCHEDULE_INTERVAL = "0 6 * * *"
    
    # Tags
    TAGS = ["ga4", "bigquery", "daily", "etl"]
    
    # Configurações de retry
    DEFAULT_RETRIES = 3
    RETRY_DELAY_MINUTES = 5
    
    # Timeout em segundos
    EXECUTION_TIMEOUT = 3600  # 1 hora
    
    # Owner
    OWNER = "data-engineering"


# =============================================================================
# CONFIGURAÇÕES DO CLOUD RUN
# =============================================================================

class CloudRunConfig:
    """Configurações para deploy no Cloud Run"""
    
    # Nome do serviço
    SERVICE_NAME = "ga4-api"
    
    # Região
    REGION = "us-central1"
    
    # Memória
    MEMORY = "512Mi"
    
    # CPU
    CPU = "1"
    
    # Timeout em segundos
    TIMEOUT = 300
    
    # Máximo de instâncias
    MAX_INSTANCES = 10
    
    # Mínimo de instâncias
    MIN_INSTANCES = 0
    
    # Porta
    PORT = 8080


# =============================================================================
# FUNÇÃO PRINCIPAL PARA OBTER CONFIGURAÇÃO COMPLETA
# =============================================================================

def get_full_config() -> Dict[str, Any]:
    """
    Retorna a configuração completa como um dicionário.
    
    Returns:
        Dict com todas as configurações
    """
    return {
        "gcp": {
            "project_id": GCPConfig.PROJECT_ID,
            "dataset_id": GCPConfig.DATASET_ID,
            "secret_id": GCPConfig.SECRET_ID,
            "region": GCPConfig.REGION
        },
        "tables": {
            "dimensions": TableConfig.TABLES_DIMENSIONS,
            "metrics": TableConfig.TABLES_METRICS
        },
        "properties": GA4Properties.PROPERTIES,
        "date": {
            "start_date": DateConfig.DEFAULT_START_DATE,
            "end_date": DateConfig.DEFAULT_END_DATE
        },
        "pagination": {
            "max_rows": PaginationConfig.MAX_ROWS_PER_REQUEST,
            "default_limit": PaginationConfig.DEFAULT_LIMIT
        },
        "airflow": {
            "dag_id": AirflowConfig.DAG_ID,
            "schedule": AirflowConfig.SCHEDULE_INTERVAL,
            "retries": AirflowConfig.DEFAULT_RETRIES
        },
        "cloud_run": {
            "service_name": CloudRunConfig.SERVICE_NAME,
            "region": CloudRunConfig.REGION,
            "port": CloudRunConfig.PORT
        }
    }
