"""
Definicoes de Schema para BigQuery.

Este modulo contem todos os schemas das tabelas GA4.
Cada tabela possui:
    - PK_{NOME_DA_TABELA}: Chave primaria (UUID), unica, not null, required
    - GA4_SESSION_KEY: Chave estrangeira para relacionar tabelas
    - LAST_UPDATE: Timestamp do carregamento no BigQuery

As tabelas sao particionadas por dia (campo 'DATE').
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class TableSchema:
    """Definicao de schema de uma tabela."""
    table_name: str
    description: str
    dimensions: List[str]
    metrics: List[str]
    schema_fields: List[Dict[str, Any]] = field(default_factory=list)


def get_base_fields(table_name: str) -> List[Dict[str, Any]]:
    """
    Retorna os campos base para uma tabela.

    Args:
        table_name: Nome da tabela (sem prefixo)

    Returns:
        Lista de campos base
    """
    return [
        {
            "name": f"PK_{table_name}",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Chave primaria unica (UUID)"
        },
        {
            "name": "GA4_SESSION_KEY",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Chave estrangeira para relacionar tabelas GA4 (PROPERTY_ID + DATE)"
        },
        {
            "name": "PROPERTY_ID",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "ID da propriedade GA4"
        },
        {
            "name": "DATE",
            "type": "DATE",
            "mode": "REQUIRED",
            "description": "Data do registro (campo de particionamento)"
        },
        {
            "name": "LAST_UPDATE",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "Timestamp da execucao e carregamento no BigQuery"
        },
    ]


# =============================================================================
# SCHEMAS POR DIMENSAO
# =============================================================================

DIMENSION_SCHEMAS: Dict[str, TableSchema] = {
    # -------------------------------------------------------------------------
    # CAMPAIGN - Dimensoes de campanha e aquisicao
    # -------------------------------------------------------------------------
    "CAMPAIGN": TableSchema(
        table_name="GA4_DIM_CAMPAIGN",
        description="Dimensoes de campanhas de marketing",
        dimensions=[
            "date",
            "campaignId",
            "campaignName",
            "sessionCampaignId",
            "sessionCampaignName",
            "firstUserCampaignId",
            "firstUserCampaignName",
            "sessionManualAdContent",
            "sessionManualTerm",
            "googleAdsAdGroupId",
            "googleAdsAdGroupName",
            "googleAdsAdNetworkType",
        ],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "activeUsers",
            "engagedSessions",
            "engagementRate",
            "eventCount",
            "conversions",
            "totalRevenue",
        ],
        schema_fields=get_base_fields("GA4_DIM_CAMPAIGN") + [
            {"name": "CAMPAIGN_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha"},
            {"name": "CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha"},
            {"name": "SESSION_CAMPAIGN_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha da sessao"},
            {"name": "SESSION_CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha da sessao"},
            {"name": "FIRST_USER_CAMPAIGN_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha do primeiro usuario"},
            {"name": "FIRST_USER_CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha do primeiro usuario"},
            {"name": "SESSION_MANUAL_AD_CONTENT", "type": "STRING", "mode": "NULLABLE", "description": "Conteudo do anuncio manual"},
            {"name": "SESSION_MANUAL_TERM", "type": "STRING", "mode": "NULLABLE", "description": "Termo manual da sessao"},
            {"name": "GOOGLE_ADS_AD_GROUP_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios Google Ads"},
            {"name": "GOOGLE_ADS_AD_GROUP_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios Google Ads"},
            {"name": "GOOGLE_ADS_AD_NETWORK_TYPE", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de rede Google Ads"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "EVENT_COUNT", "type": "INTEGER", "mode": "NULLABLE", "description": "Contagem de eventos"},
            {"name": "CONVERSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "TOTAL_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
        ]
    ),

    # -------------------------------------------------------------------------
    # SOURCE_MEDIUM - Dimensoes de origem e midia
    # -------------------------------------------------------------------------
    "SOURCE_MEDIUM": TableSchema(
        table_name="GA4_DIM_SOURCE_MEDIUM",
        description="Dimensoes de origem e midia de trafego",
        dimensions=[
            "date",
            "sessionSource",
            "sessionMedium",
            "sessionSourceMedium",
            "sessionSourcePlatform",
            "firstUserSource",
            "firstUserMedium",
            "firstUserSourceMedium",
            "firstUserSourcePlatform",
        ],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "activeUsers",
            "engagedSessions",
            "engagementRate",
            "bounceRate",
            "averageSessionDuration",
            "screenPageViews",
            "conversions",
        ],
        schema_fields=get_base_fields("GA4_DIM_SOURCE_MEDIUM") + [
            {"name": "SESSION_SOURCE", "type": "STRING", "mode": "NULLABLE", "description": "Origem da sessao"},
            {"name": "SESSION_MEDIUM", "type": "STRING", "mode": "NULLABLE", "description": "Midia da sessao"},
            {"name": "SESSION_SOURCE_MEDIUM", "type": "STRING", "mode": "NULLABLE", "description": "Origem/Midia da sessao"},
            {"name": "SESSION_SOURCE_PLATFORM", "type": "STRING", "mode": "NULLABLE", "description": "Plataforma de origem da sessao"},
            {"name": "FIRST_USER_SOURCE", "type": "STRING", "mode": "NULLABLE", "description": "Origem do primeiro usuario"},
            {"name": "FIRST_USER_MEDIUM", "type": "STRING", "mode": "NULLABLE", "description": "Midia do primeiro usuario"},
            {"name": "FIRST_USER_SOURCE_MEDIUM", "type": "STRING", "mode": "NULLABLE", "description": "Origem/Midia do primeiro usuario"},
            {"name": "FIRST_USER_SOURCE_PLATFORM", "type": "STRING", "mode": "NULLABLE", "description": "Plataforma de origem do primeiro usuario"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "BOUNCE_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "AVERAGE_SESSION_DURATION", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "SCREEN_PAGE_VIEWS", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
            {"name": "CONVERSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
        ]
    ),

    # -------------------------------------------------------------------------
    # CHANNEL - Dimensoes de canal
    # -------------------------------------------------------------------------
    "CHANNEL": TableSchema(
        table_name="GA4_DIM_CHANNEL",
        description="Dimensoes de canais de aquisicao",
        dimensions=[
            "date",
            "sessionDefaultChannelGroup",
            "firstUserDefaultChannelGroup",
            "sessionPrimaryChannelGroup",
            "firstUserPrimaryChannelGroup",
        ],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "activeUsers",
            "engagedSessions",
            "engagementRate",
            "bounceRate",
            "averageSessionDuration",
            "conversions",
            "totalRevenue",
        ],
        schema_fields=get_base_fields("GA4_DIM_CHANNEL") + [
            {"name": "SESSION_DEFAULT_CHANNEL_GROUP", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal padrao da sessao"},
            {"name": "FIRST_USER_DEFAULT_CHANNEL_GROUP", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal padrao do primeiro usuario"},
            {"name": "SESSION_PRIMARY_CHANNEL_GROUP", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal primario da sessao"},
            {"name": "FIRST_USER_PRIMARY_CHANNEL_GROUP", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal primario do primeiro usuario"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "BOUNCE_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "AVERAGE_SESSION_DURATION", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "CONVERSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "TOTAL_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
        ]
    ),

    # -------------------------------------------------------------------------
    # GEOGRAPHIC - Dimensoes geograficas
    # -------------------------------------------------------------------------
    "GEOGRAPHIC": TableSchema(
        table_name="GA4_DIM_GEOGRAPHIC",
        description="Dimensoes geograficas dos usuarios",
        dimensions=[
            "date",
            "country",
            "countryId",
            "region",
            "city",
            "cityId",
            "continent",
            "continentId",
            "subContinent",
        ],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "activeUsers",
            "engagedSessions",
            "engagementRate",
            "screenPageViews",
        ],
        schema_fields=get_base_fields("GA4_DIM_GEOGRAPHIC") + [
            {"name": "COUNTRY", "type": "STRING", "mode": "NULLABLE", "description": "Pais"},
            {"name": "COUNTRY_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do pais"},
            {"name": "REGION", "type": "STRING", "mode": "NULLABLE", "description": "Regiao/Estado"},
            {"name": "CITY", "type": "STRING", "mode": "NULLABLE", "description": "Cidade"},
            {"name": "CITY_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da cidade"},
            {"name": "CONTINENT", "type": "STRING", "mode": "NULLABLE", "description": "Continente"},
            {"name": "CONTINENT_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do continente"},
            {"name": "SUB_CONTINENT", "type": "STRING", "mode": "NULLABLE", "description": "Subcontinente"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "SCREEN_PAGE_VIEWS", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
        ]
    ),

    # -------------------------------------------------------------------------
    # DEVICE - Dimensoes de dispositivo
    # -------------------------------------------------------------------------
    "DEVICE": TableSchema(
        table_name="GA4_DIM_DEVICE",
        description="Dimensoes de dispositivos e tecnologia",
        dimensions=[
            "date",
            "deviceCategory",
            "deviceModel",
            "mobileDeviceBranding",
            "mobileDeviceModel",
            "mobileDeviceMarketingName",
            "operatingSystem",
            "operatingSystemVersion",
            "operatingSystemWithVersion",
            "browser",
            "browserVersion",
            "platform",
            "platformDeviceCategory",
            "screenResolution",
        ],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "activeUsers",
            "engagedSessions",
            "engagementRate",
            "screenPageViews",
        ],
        schema_fields=get_base_fields("GA4_DIM_DEVICE") + [
            {"name": "DEVICE_CATEGORY", "type": "STRING", "mode": "NULLABLE", "description": "Categoria do dispositivo"},
            {"name": "DEVICE_MODEL", "type": "STRING", "mode": "NULLABLE", "description": "Modelo do dispositivo"},
            {"name": "MOBILE_DEVICE_BRANDING", "type": "STRING", "mode": "NULLABLE", "description": "Marca do dispositivo movel"},
            {"name": "MOBILE_DEVICE_MODEL", "type": "STRING", "mode": "NULLABLE", "description": "Modelo do dispositivo movel"},
            {"name": "MOBILE_DEVICE_MARKETING_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome de marketing do dispositivo movel"},
            {"name": "OPERATING_SYSTEM", "type": "STRING", "mode": "NULLABLE", "description": "Sistema operacional"},
            {"name": "OPERATING_SYSTEM_VERSION", "type": "STRING", "mode": "NULLABLE", "description": "Versao do sistema operacional"},
            {"name": "OPERATING_SYSTEM_WITH_VERSION", "type": "STRING", "mode": "NULLABLE", "description": "Sistema operacional com versao"},
            {"name": "BROWSER", "type": "STRING", "mode": "NULLABLE", "description": "Navegador"},
            {"name": "BROWSER_VERSION", "type": "STRING", "mode": "NULLABLE", "description": "Versao do navegador"},
            {"name": "PLATFORM", "type": "STRING", "mode": "NULLABLE", "description": "Plataforma"},
            {"name": "PLATFORM_DEVICE_CATEGORY", "type": "STRING", "mode": "NULLABLE", "description": "Categoria de dispositivo da plataforma"},
            {"name": "SCREEN_RESOLUTION", "type": "STRING", "mode": "NULLABLE", "description": "Resolucao de tela"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "SCREEN_PAGE_VIEWS", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
        ]
    ),

    # -------------------------------------------------------------------------
    # PAGE - Dimensoes de pagina
    # -------------------------------------------------------------------------
    "PAGE": TableSchema(
        table_name="GA4_DIM_PAGE",
        description="Dimensoes de paginas e conteudo",
        dimensions=[
            "date",
            "pagePath",
            "pagePathPlusQueryString",
            "pageTitle",
            "landingPage",
            "landingPagePlusQueryString",
            "exitPage",
            "hostname",
            "pageReferrer",
            "contentGroup",
            "contentId",
            "contentType",
        ],
        metrics=[
            "screenPageViews",
            "activeUsers",
            "sessions",
            "engagedSessions",
            "averageSessionDuration",
            "bounceRate",
            "entrances",
            "exits",
        ],
        schema_fields=get_base_fields("GA4_DIM_PAGE") + [
            {"name": "PAGE_PATH", "type": "STRING", "mode": "NULLABLE", "description": "Caminho da pagina"},
            {"name": "PAGE_PATH_PLUS_QUERY_STRING", "type": "STRING", "mode": "NULLABLE", "description": "Caminho da pagina com query string"},
            {"name": "PAGE_TITLE", "type": "STRING", "mode": "NULLABLE", "description": "Titulo da pagina"},
            {"name": "LANDING_PAGE", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de entrada"},
            {"name": "LANDING_PAGE_PLUS_QUERY_STRING", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de entrada com query string"},
            {"name": "EXIT_PAGE", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de saida"},
            {"name": "HOSTNAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do host"},
            {"name": "PAGE_REFERRER", "type": "STRING", "mode": "NULLABLE", "description": "Referenciador da pagina"},
            {"name": "CONTENT_GROUP", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de conteudo"},
            {"name": "CONTENT_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do conteudo"},
            {"name": "CONTENT_TYPE", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de conteudo"},
            {"name": "SCREEN_PAGE_VIEWS", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "AVERAGE_SESSION_DURATION", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "BOUNCE_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "ENTRANCES", "type": "INTEGER", "mode": "NULLABLE", "description": "Entradas"},
            {"name": "EXITS", "type": "INTEGER", "mode": "NULLABLE", "description": "Saidas"},
        ]
    ),

    # -------------------------------------------------------------------------
    # EVENT - Dimensoes de eventos
    # -------------------------------------------------------------------------
    "EVENT": TableSchema(
        table_name="GA4_DIM_EVENT",
        description="Dimensoes de eventos e conversoes",
        dimensions=[
            "date",
            "eventName",
            "isConversionEvent",
        ],
        metrics=[
            "eventCount",
            "eventCountPerUser",
            "eventsPerSession",
            "activeUsers",
            "totalUsers",
            "conversions",
            "eventValue",
            "totalRevenue",
        ],
        schema_fields=get_base_fields("GA4_DIM_EVENT") + [
            {"name": "EVENT_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do evento"},
            {"name": "IS_CONVERSION_EVENT", "type": "STRING", "mode": "NULLABLE", "description": "Indica se e evento de conversao"},
            {"name": "EVENT_COUNT", "type": "INTEGER", "mode": "NULLABLE", "description": "Contagem de eventos"},
            {"name": "EVENT_COUNT_PER_USER", "type": "FLOAT", "mode": "NULLABLE", "description": "Eventos por usuario"},
            {"name": "EVENTS_PER_SESSION", "type": "FLOAT", "mode": "NULLABLE", "description": "Eventos por sessao"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "CONVERSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "EVENT_VALUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Valor do evento"},
            {"name": "TOTAL_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
        ]
    ),

    # -------------------------------------------------------------------------
    # USER - Dimensoes de usuario
    # -------------------------------------------------------------------------
    "USER": TableSchema(
        table_name="GA4_DIM_USER",
        description="Dimensoes de usuarios e demograficos",
        dimensions=[
            "date",
            "newVsReturning",
            "userAgeBracket",
            "userGender",
            "signedInWithUserId",
            "firstSessionDate",
            "firstUserCampaignId",
            "firstUserCampaignName",
            "firstUserGoogleAdsAccountName",
            "firstUserGoogleAdsAdGroupId",
            "firstUserGoogleAdsAdGroupName",
        ],
        metrics=[
            "activeUsers",
            "newUsers",
            "totalUsers",
            "sessions",
            "sessionsPerUser",
            "engagedSessions",
            "engagementRate",
            "averageSessionDuration",
            "screenPageViewsPerSession",
        ],
        schema_fields=get_base_fields("GA4_DIM_USER") + [
            {"name": "NEW_VS_RETURNING", "type": "STRING", "mode": "NULLABLE", "description": "Novo vs recorrente"},
            {"name": "USER_AGE_BRACKET", "type": "STRING", "mode": "NULLABLE", "description": "Faixa etaria do usuario"},
            {"name": "USER_GENDER", "type": "STRING", "mode": "NULLABLE", "description": "Genero do usuario"},
            {"name": "SIGNED_IN_WITH_USER_ID", "type": "STRING", "mode": "NULLABLE", "description": "Logado com user ID"},
            {"name": "FIRST_SESSION_DATE", "type": "STRING", "mode": "NULLABLE", "description": "Data da primeira sessao"},
            {"name": "FIRST_USER_CAMPAIGN_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha do primeiro usuario"},
            {"name": "FIRST_USER_CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha do primeiro usuario"},
            {"name": "FIRST_USER_GOOGLE_ADS_ACCOUNT_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da conta Google Ads do primeiro usuario"},
            {"name": "FIRST_USER_GOOGLE_ADS_AD_GROUP_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios do primeiro usuario"},
            {"name": "FIRST_USER_GOOGLE_ADS_AD_GROUP_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios do primeiro usuario"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "SESSIONS_PER_USER", "type": "FLOAT", "mode": "NULLABLE", "description": "Sessoes por usuario"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "AVERAGE_SESSION_DURATION", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "SCREEN_PAGE_VIEWS_PER_SESSION", "type": "FLOAT", "mode": "NULLABLE", "description": "Visualizacoes por sessao"},
        ]
    ),

    # -------------------------------------------------------------------------
    # ECOMMERCE - Dimensoes de ecommerce
    # -------------------------------------------------------------------------
    "ECOMMERCE": TableSchema(
        table_name="GA4_DIM_ECOMMERCE",
        description="Dimensoes de ecommerce e transacoes",
        dimensions=[
            "date",
            "transactionId",
            "itemId",
            "itemName",
            "itemBrand",
            "itemCategory",
            "itemCategory2",
            "itemCategory3",
            "itemCategory4",
            "itemCategory5",
            "itemListId",
            "itemListName",
            "itemListPosition",
            "itemPromotionCreativeName",
            "itemPromotionId",
            "itemPromotionName",
            "orderCoupon",
            "shippingTier",
        ],
        metrics=[
            "ecommercePurchases",
            "itemsAddedToCart",
            "itemsCheckedOut",
            "itemsClickedInList",
            "itemsClickedInPromotion",
            "itemsPurchased",
            "itemsViewed",
            "itemsViewedInList",
            "itemsViewedInPromotion",
            "itemRevenue",
            "purchaseRevenue",
            "totalRevenue",
            "transactions",
        ],
        schema_fields=get_base_fields("GA4_DIM_ECOMMERCE") + [
            {"name": "TRANSACTION_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da transacao"},
            {"name": "ITEM_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do item"},
            {"name": "ITEM_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do item"},
            {"name": "ITEM_BRAND", "type": "STRING", "mode": "NULLABLE", "description": "Marca do item"},
            {"name": "ITEM_CATEGORY", "type": "STRING", "mode": "NULLABLE", "description": "Categoria do item"},
            {"name": "ITEM_CATEGORY_2", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 2 do item"},
            {"name": "ITEM_CATEGORY_3", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 3 do item"},
            {"name": "ITEM_CATEGORY_4", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 4 do item"},
            {"name": "ITEM_CATEGORY_5", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 5 do item"},
            {"name": "ITEM_LIST_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da lista de itens"},
            {"name": "ITEM_LIST_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da lista de itens"},
            {"name": "ITEM_LIST_POSITION", "type": "STRING", "mode": "NULLABLE", "description": "Posicao na lista de itens"},
            {"name": "ITEM_PROMOTION_CREATIVE_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome criativo da promocao"},
            {"name": "ITEM_PROMOTION_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da promocao"},
            {"name": "ITEM_PROMOTION_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da promocao"},
            {"name": "ORDER_COUPON", "type": "STRING", "mode": "NULLABLE", "description": "Cupom do pedido"},
            {"name": "SHIPPING_TIER", "type": "STRING", "mode": "NULLABLE", "description": "Nivel de envio"},
            {"name": "ECOMMERCE_PURCHASES", "type": "INTEGER", "mode": "NULLABLE", "description": "Compras de ecommerce"},
            {"name": "ITEMS_ADDED_TO_CART", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens adicionados ao carrinho"},
            {"name": "ITEMS_CHECKED_OUT", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens no checkout"},
            {"name": "ITEMS_CLICKED_IN_LIST", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens clicados na lista"},
            {"name": "ITEMS_CLICKED_IN_PROMOTION", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens clicados em promocao"},
            {"name": "ITEMS_PURCHASED", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens comprados"},
            {"name": "ITEMS_VIEWED", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens visualizados"},
            {"name": "ITEMS_VIEWED_IN_LIST", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens visualizados na lista"},
            {"name": "ITEMS_VIEWED_IN_PROMOTION", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens visualizados em promocao"},
            {"name": "ITEM_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita do item"},
            {"name": "PURCHASE_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita de compras"},
            {"name": "TOTAL_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
            {"name": "TRANSACTIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Transacoes"},
        ]
    ),

    # -------------------------------------------------------------------------
    # SESSION - Dimensoes de sessao
    # -------------------------------------------------------------------------
    "SESSION": TableSchema(
        table_name="GA4_DIM_SESSION",
        description="Dimensoes e metricas de sessao",
        dimensions=[
            "date",
            "sessionDefaultChannelGroup",
            "sessionSource",
            "sessionMedium",
            "sessionCampaignName",
            "landingPage",
            "deviceCategory",
            "country",
        ],
        metrics=[
            "sessions",
            "engagedSessions",
            "averageSessionDuration",
            "bounceRate",
            "engagementRate",
            "sessionsPerUser",
            "screenPageViews",
            "screenPageViewsPerSession",
            "activeUsers",
            "newUsers",
            "totalUsers",
        ],
        schema_fields=get_base_fields("GA4_DIM_SESSION") + [
            {"name": "SESSION_DEFAULT_CHANNEL_GROUP", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal padrao"},
            {"name": "SESSION_SOURCE", "type": "STRING", "mode": "NULLABLE", "description": "Origem da sessao"},
            {"name": "SESSION_MEDIUM", "type": "STRING", "mode": "NULLABLE", "description": "Midia da sessao"},
            {"name": "SESSION_CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha"},
            {"name": "LANDING_PAGE", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de entrada"},
            {"name": "DEVICE_CATEGORY", "type": "STRING", "mode": "NULLABLE", "description": "Categoria do dispositivo"},
            {"name": "COUNTRY", "type": "STRING", "mode": "NULLABLE", "description": "Pais"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "AVERAGE_SESSION_DURATION", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "BOUNCE_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "SESSIONS_PER_USER", "type": "FLOAT", "mode": "NULLABLE", "description": "Sessoes por usuario"},
            {"name": "SCREEN_PAGE_VIEWS", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
            {"name": "SCREEN_PAGE_VIEWS_PER_SESSION", "type": "FLOAT", "mode": "NULLABLE", "description": "Visualizacoes por sessao"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
        ]
    ),

    # -------------------------------------------------------------------------
    # GOOGLE_ADS - Dimensoes do Google Ads
    # -------------------------------------------------------------------------
    "GOOGLE_ADS": TableSchema(
        table_name="GA4_DIM_GOOGLE_ADS",
        description="Dimensoes de campanhas Google Ads",
        dimensions=[
            "date",
            "sessionGoogleAdsAccountName",
            "sessionGoogleAdsAdGroupId",
            "sessionGoogleAdsAdGroupName",
            "sessionGoogleAdsAdNetworkType",
            "sessionGoogleAdsCampaignId",
            "sessionGoogleAdsCampaignName",
            "sessionGoogleAdsCampaignType",
            "sessionGoogleAdsCreativeId",
            "sessionGoogleAdsKeyword",
            "sessionGoogleAdsQuery",
            "googleAdsAccountName",
            "googleAdsAdGroupId",
            "googleAdsAdGroupName",
            "googleAdsCampaignId",
            "googleAdsCampaignName",
        ],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "activeUsers",
            "engagedSessions",
            "engagementRate",
            "conversions",
            "totalRevenue",
            "advertiserAdClicks",
            "advertiserAdCost",
            "advertiserAdCostPerClick",
            "advertiserAdImpressions",
        ],
        schema_fields=get_base_fields("GA4_DIM_GOOGLE_ADS") + [
            {"name": "SESSION_GOOGLE_ADS_ACCOUNT_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da conta Google Ads da sessao"},
            {"name": "SESSION_GOOGLE_ADS_AD_GROUP_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios da sessao"},
            {"name": "SESSION_GOOGLE_ADS_AD_GROUP_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios da sessao"},
            {"name": "SESSION_GOOGLE_ADS_AD_NETWORK_TYPE", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de rede de anuncios da sessao"},
            {"name": "SESSION_GOOGLE_ADS_CAMPAIGN_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha Google Ads da sessao"},
            {"name": "SESSION_GOOGLE_ADS_CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha Google Ads da sessao"},
            {"name": "SESSION_GOOGLE_ADS_CAMPAIGN_TYPE", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de campanha Google Ads da sessao"},
            {"name": "SESSION_GOOGLE_ADS_CREATIVE_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do criativo Google Ads da sessao"},
            {"name": "SESSION_GOOGLE_ADS_KEYWORD", "type": "STRING", "mode": "NULLABLE", "description": "Palavra-chave Google Ads da sessao"},
            {"name": "SESSION_GOOGLE_ADS_QUERY", "type": "STRING", "mode": "NULLABLE", "description": "Query Google Ads da sessao"},
            {"name": "GOOGLE_ADS_ACCOUNT_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da conta Google Ads"},
            {"name": "GOOGLE_ADS_AD_GROUP_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios"},
            {"name": "GOOGLE_ADS_AD_GROUP_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios"},
            {"name": "GOOGLE_ADS_CAMPAIGN_ID", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha Google Ads"},
            {"name": "GOOGLE_ADS_CAMPAIGN_NAME", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha Google Ads"},
            {"name": "SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "TOTAL_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "NEW_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "ACTIVE_USERS", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "ENGAGED_SESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "ENGAGEMENT_RATE", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "CONVERSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "TOTAL_REVENUE", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
            {"name": "ADVERTISER_AD_CLICKS", "type": "INTEGER", "mode": "NULLABLE", "description": "Cliques em anuncios"},
            {"name": "ADVERTISER_AD_COST", "type": "FLOAT", "mode": "NULLABLE", "description": "Custo de anuncios"},
            {"name": "ADVERTISER_AD_COST_PER_CLICK", "type": "FLOAT", "mode": "NULLABLE", "description": "Custo por clique"},
            {"name": "ADVERTISER_AD_IMPRESSIONS", "type": "INTEGER", "mode": "NULLABLE", "description": "Impressoes de anuncios"},
        ]
    ),
}


def get_all_schemas() -> Dict[str, TableSchema]:
    """Retorna todos os schemas de dimensao."""
    return DIMENSION_SCHEMAS


def get_schema(dimension_key: str) -> TableSchema:
    """
    Retorna o schema de uma dimensao especifica.

    Args:
        dimension_key: Chave da dimensao (ex: CAMPAIGN, SOURCE_MEDIUM)

    Returns:
        TableSchema da dimensao

    Raises:
        KeyError: Se a dimensao nao existir
    """
    if dimension_key not in DIMENSION_SCHEMAS:
        raise KeyError(f"Schema nao encontrado: {dimension_key}. Disponiveis: {list(DIMENSION_SCHEMAS.keys())}")
    return DIMENSION_SCHEMAS[dimension_key]


def list_available_dimensions() -> list:
    """Retorna lista de dimensoes disponiveis."""
    return list(DIMENSION_SCHEMAS.keys())


def get_pk_field_name(table_name: str) -> str:
    """
    Retorna o nome do campo PK para uma tabela.

    Args:
        table_name: Nome da tabela

    Returns:
        Nome do campo PK (ex: PK_GA4_DIM_CAMPAIGN)
    """
    return f"PK_{table_name}"
