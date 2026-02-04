"""
Definicoes de Schema para BigQuery.

Este modulo contem todos os schemas das tabelas GA4.
Cada tabela possui:
    - id: Chave primaria (UUID), unica, not null, required
    - ga4_session_key: Chave estrangeira para relacionar tabelas
    - last_update: Timestamp do carregamento no BigQuery

As tabelas sao particionadas por dia (campo 'date').
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


# =============================================================================
# CAMPOS BASE (presentes em todas as tabelas)
# =============================================================================

BASE_FIELDS = [
    {
        "name": "id",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "Chave primaria unica (UUID)"
    },
    {
        "name": "ga4_session_key",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "Chave estrangeira para relacionar tabelas GA4 (property_id + date)"
    },
    {
        "name": "property_id",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "ID da propriedade GA4"
    },
    {
        "name": "date",
        "type": "DATE",
        "mode": "REQUIRED",
        "description": "Data do registro (campo de particionamento)"
    },
    {
        "name": "last_update",
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
    # CAMPANHA - Dimensoes de campanha e aquisicao
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
        schema_fields=BASE_FIELDS + [
            {"name": "campaign_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha"},
            {"name": "campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha"},
            {"name": "session_campaign_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha da sessao"},
            {"name": "session_campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha da sessao"},
            {"name": "first_user_campaign_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha do primeiro usuario"},
            {"name": "first_user_campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha do primeiro usuario"},
            {"name": "session_manual_ad_content", "type": "STRING", "mode": "NULLABLE", "description": "Conteudo do anuncio manual"},
            {"name": "session_manual_term", "type": "STRING", "mode": "NULLABLE", "description": "Termo manual da sessao"},
            {"name": "google_ads_ad_group_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios Google Ads"},
            {"name": "google_ads_ad_group_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios Google Ads"},
            {"name": "google_ads_ad_network_type", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de rede Google Ads"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "event_count", "type": "INTEGER", "mode": "NULLABLE", "description": "Contagem de eventos"},
            {"name": "conversions", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "total_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
        ]
    ),

    # -------------------------------------------------------------------------
    # SOURCE/MEDIUM - Dimensoes de origem e midia
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
        schema_fields=BASE_FIELDS + [
            {"name": "session_source", "type": "STRING", "mode": "NULLABLE", "description": "Origem da sessao"},
            {"name": "session_medium", "type": "STRING", "mode": "NULLABLE", "description": "Midia da sessao"},
            {"name": "session_source_medium", "type": "STRING", "mode": "NULLABLE", "description": "Origem/Midia da sessao"},
            {"name": "session_source_platform", "type": "STRING", "mode": "NULLABLE", "description": "Plataforma de origem da sessao"},
            {"name": "first_user_source", "type": "STRING", "mode": "NULLABLE", "description": "Origem do primeiro usuario"},
            {"name": "first_user_medium", "type": "STRING", "mode": "NULLABLE", "description": "Midia do primeiro usuario"},
            {"name": "first_user_source_medium", "type": "STRING", "mode": "NULLABLE", "description": "Origem/Midia do primeiro usuario"},
            {"name": "first_user_source_platform", "type": "STRING", "mode": "NULLABLE", "description": "Plataforma de origem do primeiro usuario"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "bounce_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "average_session_duration", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "screen_page_views", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
            {"name": "conversions", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "session_default_channel_group", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal padrao da sessao"},
            {"name": "first_user_default_channel_group", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal padrao do primeiro usuario"},
            {"name": "session_primary_channel_group", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal primario da sessao"},
            {"name": "first_user_primary_channel_group", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal primario do primeiro usuario"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "bounce_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "average_session_duration", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "conversions", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "total_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Pais"},
            {"name": "country_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do pais"},
            {"name": "region", "type": "STRING", "mode": "NULLABLE", "description": "Regiao/Estado"},
            {"name": "city", "type": "STRING", "mode": "NULLABLE", "description": "Cidade"},
            {"name": "city_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da cidade"},
            {"name": "continent", "type": "STRING", "mode": "NULLABLE", "description": "Continente"},
            {"name": "continent_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do continente"},
            {"name": "sub_continent", "type": "STRING", "mode": "NULLABLE", "description": "Subcontinente"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "screen_page_views", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "device_category", "type": "STRING", "mode": "NULLABLE", "description": "Categoria do dispositivo"},
            {"name": "device_model", "type": "STRING", "mode": "NULLABLE", "description": "Modelo do dispositivo"},
            {"name": "mobile_device_branding", "type": "STRING", "mode": "NULLABLE", "description": "Marca do dispositivo movel"},
            {"name": "mobile_device_model", "type": "STRING", "mode": "NULLABLE", "description": "Modelo do dispositivo movel"},
            {"name": "mobile_device_marketing_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome de marketing do dispositivo movel"},
            {"name": "operating_system", "type": "STRING", "mode": "NULLABLE", "description": "Sistema operacional"},
            {"name": "operating_system_version", "type": "STRING", "mode": "NULLABLE", "description": "Versao do sistema operacional"},
            {"name": "operating_system_with_version", "type": "STRING", "mode": "NULLABLE", "description": "Sistema operacional com versao"},
            {"name": "browser", "type": "STRING", "mode": "NULLABLE", "description": "Navegador"},
            {"name": "browser_version", "type": "STRING", "mode": "NULLABLE", "description": "Versao do navegador"},
            {"name": "platform", "type": "STRING", "mode": "NULLABLE", "description": "Plataforma"},
            {"name": "platform_device_category", "type": "STRING", "mode": "NULLABLE", "description": "Categoria de dispositivo da plataforma"},
            {"name": "screen_resolution", "type": "STRING", "mode": "NULLABLE", "description": "Resolucao de tela"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "screen_page_views", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "page_path", "type": "STRING", "mode": "NULLABLE", "description": "Caminho da pagina"},
            {"name": "page_path_plus_query_string", "type": "STRING", "mode": "NULLABLE", "description": "Caminho da pagina com query string"},
            {"name": "page_title", "type": "STRING", "mode": "NULLABLE", "description": "Titulo da pagina"},
            {"name": "landing_page", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de entrada"},
            {"name": "landing_page_plus_query_string", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de entrada com query string"},
            {"name": "exit_page", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de saida"},
            {"name": "hostname", "type": "STRING", "mode": "NULLABLE", "description": "Nome do host"},
            {"name": "page_referrer", "type": "STRING", "mode": "NULLABLE", "description": "Referenciador da pagina"},
            {"name": "content_group", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de conteudo"},
            {"name": "content_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do conteudo"},
            {"name": "content_type", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de conteudo"},
            {"name": "screen_page_views", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "average_session_duration", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "bounce_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "entrances", "type": "INTEGER", "mode": "NULLABLE", "description": "Entradas"},
            {"name": "exits", "type": "INTEGER", "mode": "NULLABLE", "description": "Saidas"},
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
            "customEvent:parameter_name",
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
        schema_fields=BASE_FIELDS + [
            {"name": "event_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome do evento"},
            {"name": "is_conversion_event", "type": "STRING", "mode": "NULLABLE", "description": "Indica se e evento de conversao"},
            {"name": "event_count", "type": "INTEGER", "mode": "NULLABLE", "description": "Contagem de eventos"},
            {"name": "event_count_per_user", "type": "FLOAT", "mode": "NULLABLE", "description": "Eventos por usuario"},
            {"name": "events_per_session", "type": "FLOAT", "mode": "NULLABLE", "description": "Eventos por sessao"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "conversions", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "event_value", "type": "FLOAT", "mode": "NULLABLE", "description": "Valor do evento"},
            {"name": "total_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "new_vs_returning", "type": "STRING", "mode": "NULLABLE", "description": "Novo vs recorrente"},
            {"name": "user_age_bracket", "type": "STRING", "mode": "NULLABLE", "description": "Faixa etaria do usuario"},
            {"name": "user_gender", "type": "STRING", "mode": "NULLABLE", "description": "Genero do usuario"},
            {"name": "signed_in_with_user_id", "type": "STRING", "mode": "NULLABLE", "description": "Logado com user ID"},
            {"name": "first_session_date", "type": "STRING", "mode": "NULLABLE", "description": "Data da primeira sessao"},
            {"name": "first_user_campaign_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha do primeiro usuario"},
            {"name": "first_user_campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha do primeiro usuario"},
            {"name": "first_user_google_ads_account_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da conta Google Ads do primeiro usuario"},
            {"name": "first_user_google_ads_ad_group_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios do primeiro usuario"},
            {"name": "first_user_google_ads_ad_group_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios do primeiro usuario"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "sessions_per_user", "type": "FLOAT", "mode": "NULLABLE", "description": "Sessoes por usuario"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "average_session_duration", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "screen_page_views_per_session", "type": "FLOAT", "mode": "NULLABLE", "description": "Visualizacoes por sessao"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "transaction_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da transacao"},
            {"name": "item_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do item"},
            {"name": "item_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome do item"},
            {"name": "item_brand", "type": "STRING", "mode": "NULLABLE", "description": "Marca do item"},
            {"name": "item_category", "type": "STRING", "mode": "NULLABLE", "description": "Categoria do item"},
            {"name": "item_category_2", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 2 do item"},
            {"name": "item_category_3", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 3 do item"},
            {"name": "item_category_4", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 4 do item"},
            {"name": "item_category_5", "type": "STRING", "mode": "NULLABLE", "description": "Categoria 5 do item"},
            {"name": "item_list_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da lista de itens"},
            {"name": "item_list_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da lista de itens"},
            {"name": "item_list_position", "type": "STRING", "mode": "NULLABLE", "description": "Posicao na lista de itens"},
            {"name": "item_promotion_creative_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome criativo da promocao"},
            {"name": "item_promotion_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da promocao"},
            {"name": "item_promotion_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da promocao"},
            {"name": "order_coupon", "type": "STRING", "mode": "NULLABLE", "description": "Cupom do pedido"},
            {"name": "shipping_tier", "type": "STRING", "mode": "NULLABLE", "description": "Nivel de envio"},
            {"name": "ecommerce_purchases", "type": "INTEGER", "mode": "NULLABLE", "description": "Compras de ecommerce"},
            {"name": "items_added_to_cart", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens adicionados ao carrinho"},
            {"name": "items_checked_out", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens no checkout"},
            {"name": "items_clicked_in_list", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens clicados na lista"},
            {"name": "items_clicked_in_promotion", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens clicados em promocao"},
            {"name": "items_purchased", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens comprados"},
            {"name": "items_viewed", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens visualizados"},
            {"name": "items_viewed_in_list", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens visualizados na lista"},
            {"name": "items_viewed_in_promotion", "type": "INTEGER", "mode": "NULLABLE", "description": "Itens visualizados em promocao"},
            {"name": "item_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita do item"},
            {"name": "purchase_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita de compras"},
            {"name": "total_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
            {"name": "transactions", "type": "INTEGER", "mode": "NULLABLE", "description": "Transacoes"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "session_default_channel_group", "type": "STRING", "mode": "NULLABLE", "description": "Grupo de canal padrao"},
            {"name": "session_source", "type": "STRING", "mode": "NULLABLE", "description": "Origem da sessao"},
            {"name": "session_medium", "type": "STRING", "mode": "NULLABLE", "description": "Midia da sessao"},
            {"name": "session_campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha"},
            {"name": "landing_page", "type": "STRING", "mode": "NULLABLE", "description": "Pagina de entrada"},
            {"name": "device_category", "type": "STRING", "mode": "NULLABLE", "description": "Categoria do dispositivo"},
            {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Pais"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "average_session_duration", "type": "FLOAT", "mode": "NULLABLE", "description": "Duracao media da sessao"},
            {"name": "bounce_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de rejeicao"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "sessions_per_user", "type": "FLOAT", "mode": "NULLABLE", "description": "Sessoes por usuario"},
            {"name": "screen_page_views", "type": "INTEGER", "mode": "NULLABLE", "description": "Visualizacoes de pagina"},
            {"name": "screen_page_views_per_session", "type": "FLOAT", "mode": "NULLABLE", "description": "Visualizacoes por sessao"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
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
        schema_fields=BASE_FIELDS + [
            {"name": "session_google_ads_account_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da conta Google Ads da sessao"},
            {"name": "session_google_ads_ad_group_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios da sessao"},
            {"name": "session_google_ads_ad_group_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios da sessao"},
            {"name": "session_google_ads_ad_network_type", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de rede de anuncios da sessao"},
            {"name": "session_google_ads_campaign_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha Google Ads da sessao"},
            {"name": "session_google_ads_campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha Google Ads da sessao"},
            {"name": "session_google_ads_campaign_type", "type": "STRING", "mode": "NULLABLE", "description": "Tipo de campanha Google Ads da sessao"},
            {"name": "session_google_ads_creative_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do criativo Google Ads da sessao"},
            {"name": "session_google_ads_keyword", "type": "STRING", "mode": "NULLABLE", "description": "Palavra-chave Google Ads da sessao"},
            {"name": "session_google_ads_query", "type": "STRING", "mode": "NULLABLE", "description": "Query Google Ads da sessao"},
            {"name": "google_ads_account_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da conta Google Ads"},
            {"name": "google_ads_ad_group_id", "type": "STRING", "mode": "NULLABLE", "description": "ID do grupo de anuncios"},
            {"name": "google_ads_ad_group_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome do grupo de anuncios"},
            {"name": "google_ads_campaign_id", "type": "STRING", "mode": "NULLABLE", "description": "ID da campanha Google Ads"},
            {"name": "google_ads_campaign_name", "type": "STRING", "mode": "NULLABLE", "description": "Nome da campanha Google Ads"},
            {"name": "sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Numero de sessoes"},
            {"name": "total_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Total de usuarios"},
            {"name": "new_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Novos usuarios"},
            {"name": "active_users", "type": "INTEGER", "mode": "NULLABLE", "description": "Usuarios ativos"},
            {"name": "engaged_sessions", "type": "INTEGER", "mode": "NULLABLE", "description": "Sessoes engajadas"},
            {"name": "engagement_rate", "type": "FLOAT", "mode": "NULLABLE", "description": "Taxa de engajamento"},
            {"name": "conversions", "type": "INTEGER", "mode": "NULLABLE", "description": "Conversoes"},
            {"name": "total_revenue", "type": "FLOAT", "mode": "NULLABLE", "description": "Receita total"},
            {"name": "advertiser_ad_clicks", "type": "INTEGER", "mode": "NULLABLE", "description": "Cliques em anuncios"},
            {"name": "advertiser_ad_cost", "type": "FLOAT", "mode": "NULLABLE", "description": "Custo de anuncios"},
            {"name": "advertiser_ad_cost_per_click", "type": "FLOAT", "mode": "NULLABLE", "description": "Custo por clique"},
            {"name": "advertiser_ad_impressions", "type": "INTEGER", "mode": "NULLABLE", "description": "Impressoes de anuncios"},
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
