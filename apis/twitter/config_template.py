"""
Configurações da API de extração de dados do Twitter/X para BigQuery.

Este arquivo contém todas as configurações necessárias para a execução da API,
incluindo configurações do GCP, tabelas do BigQuery, e contas do Twitter.

Autor: Manus AI
Data: Janeiro de 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# =============================================================================
# CONFIGURAÇÕES DO GOOGLE CLOUD PLATFORM
# =============================================================================

@dataclass
class GCPConfig:
    """Configurações do Google Cloud Platform."""
    
    # ID do projeto no GCP
    PROJECT_ID: str = "cadastra-yduqs-uat"
    
    # Nome do dataset no BigQuery
    DATASET_ID: str = "RAW"
    
    # ID do secret no Secret Manager (credenciais do BigQuery)
    SECRET_ID_BQ: str = "Acesso_BQ"
    
    # ID do secret no Secret Manager (Bearer Token do Twitter)
    SECRET_ID_TWITTER: str = "twitter-bearer-token"
    
    # Região padrão
    REGION: str = "us-central1"


# =============================================================================
# CONFIGURAÇÕES DAS CONTAS DO TWITTER
# =============================================================================

@dataclass
class TwitterAccount:
    """Representa uma conta do Twitter a ser monitorada."""
    username: str
    user_id: str
    name: str
    bearer_token: Optional[str] = None  # Se None, usa o token padrão


@dataclass
class TwitterAccountsConfig:
    """Configurações das contas do Twitter."""
    
    # Lista de contas a serem monitoradas
    # Adicione suas contas aqui
    ACCOUNTS: List[TwitterAccount] = field(default_factory=lambda: [
        TwitterAccount(
            username="CLIENTENAME",
            user_id="524779913",
            name="Cliente Principal"
        ),
        # Adicione mais contas conforme necessário
        # TwitterAccount(
        #     username="outra_conta",
        #     user_id="123456789",
        #     name="Outra Conta"
        # ),
    ])
    
    # Bearer Token padrão (será usado se a conta não tiver um token específico)
    # IMPORTANTE: Em produção, use o Secret Manager para armazenar este token
    DEFAULT_BEARER_TOKEN: str = ""


# =============================================================================
# CONFIGURAÇÕES DE PERÍODO DE EXTRAÇÃO
# =============================================================================

@dataclass
class DateConfig:
    """Configurações de período de extração."""
    
    # Dias de início (D-7 = 7 dias atrás)
    DAYS_START: int = 7
    
    # Dias de fim (D-2 = 2 dias atrás)
    DAYS_END: int = 2
    
    # Timezone
    TIMEZONE: str = "America/Sao_Paulo"


# =============================================================================
# CONFIGURAÇÕES DAS TABELAS DO BIGQUERY
# =============================================================================

@dataclass
class TableConfig:
    """Configuração de uma tabela do BigQuery."""
    name: str
    description: str
    fields: List[Dict[str, str]]


class TablesConfig:
    """Configurações de todas as tabelas do BigQuery."""
    
    # Tabela de perfil/dados gerais
    PERFIL = TableConfig(
        name="TB_013_TWITTER_PERFIL",
        description="Dados gerais do perfil do Twitter - métricas de seguidores e atividade",
        fields=[
            {"name": "date_extraction", "type": "DATE", "description": "Data da extração"},
            {"name": "date_insertion", "type": "TIMESTAMP", "description": "Data/hora da inserção no BigQuery"},
            {"name": "account_username", "type": "STRING", "description": "Username da conta"},
            {"name": "account_name", "type": "STRING", "description": "Nome configurado da conta"},
            {"name": "user_id", "type": "STRING", "description": "ID do usuário no Twitter"},
            {"name": "display_name", "type": "STRING", "description": "Nome de exibição do perfil"},
            {"name": "followers_count", "type": "INTEGER", "description": "Número de seguidores"},
            {"name": "following_count", "type": "INTEGER", "description": "Número de contas seguidas"},
            {"name": "tweet_count", "type": "INTEGER", "description": "Total de tweets"},
            {"name": "listed_count", "type": "INTEGER", "description": "Número de listas em que está incluído"},
        ]
    )
    
    # Tabela de posts/tweets
    POSTS = TableConfig(
        name="TB_014_TWITTER_POSTS",
        description="Dados de posts/tweets do Twitter - métricas de engajamento por post",
        fields=[
            {"name": "date_extraction", "type": "DATE", "description": "Data da extração"},
            {"name": "date_insertion", "type": "TIMESTAMP", "description": "Data/hora da inserção no BigQuery"},
            {"name": "account_username", "type": "STRING", "description": "Username da conta"},
            {"name": "account_name", "type": "STRING", "description": "Nome configurado da conta"},
            {"name": "tweet_id", "type": "STRING", "description": "ID do tweet"},
            {"name": "created_at", "type": "TIMESTAMP", "description": "Data de criação do tweet"},
            {"name": "tweet_type", "type": "STRING", "description": "Tipo do tweet (post, retweet, reply, quote)"},
            {"name": "text", "type": "STRING", "description": "Texto do tweet"},
            {"name": "url", "type": "STRING", "description": "URL do tweet"},
            {"name": "reply_count", "type": "INTEGER", "description": "Número de respostas"},
            {"name": "retweet_count", "type": "INTEGER", "description": "Número de retweets"},
            {"name": "like_count", "type": "INTEGER", "description": "Número de likes"},
            {"name": "quote_count", "type": "INTEGER", "description": "Número de quotes"},
            {"name": "impression_count", "type": "INTEGER", "description": "Número de impressões"},
            {"name": "bookmark_count", "type": "INTEGER", "description": "Número de bookmarks"},
        ]
    )
    
    # Tabela de métricas adicionais
    METRICAS_ADICIONAIS = TableConfig(
        name="TB_015_TWITTER_METRICAS_ADICIONAIS",
        description="Métricas adicionais do Twitter - cliques, vídeos e engajamento detalhado",
        fields=[
            {"name": "date_extraction", "type": "DATE", "description": "Data da extração"},
            {"name": "date_insertion", "type": "TIMESTAMP", "description": "Data/hora da inserção no BigQuery"},
            {"name": "account_username", "type": "STRING", "description": "Username da conta"},
            {"name": "account_name", "type": "STRING", "description": "Nome configurado da conta"},
            {"name": "tweet_id", "type": "STRING", "description": "ID do tweet"},
            {"name": "created_at", "type": "TIMESTAMP", "description": "Data de criação do tweet"},
            {"name": "url_link_clicks", "type": "INTEGER", "description": "Cliques em URLs do tweet"},
            {"name": "user_profile_clicks", "type": "INTEGER", "description": "Cliques no perfil a partir do tweet"},
            {"name": "has_media", "type": "BOOLEAN", "description": "Se o tweet possui mídia anexada"},
            {"name": "media_type", "type": "STRING", "description": "Tipo de mídia (photo, video, animated_gif)"},
            {"name": "video_view_count", "type": "INTEGER", "description": "Visualizações de vídeo"},
            {"name": "video_playback_0_count", "type": "INTEGER", "description": "Vídeo iniciado (0%)"},
            {"name": "video_playback_25_count", "type": "INTEGER", "description": "Vídeo 25% assistido"},
            {"name": "video_playback_50_count", "type": "INTEGER", "description": "Vídeo 50% assistido"},
            {"name": "video_playback_75_count", "type": "INTEGER", "description": "Vídeo 75% assistido"},
            {"name": "video_playback_100_count", "type": "INTEGER", "description": "Vídeo 100% assistido"},
        ]
    )
    
    @classmethod
    def get_all_tables(cls) -> List[TableConfig]:
        """Retorna todas as configurações de tabelas."""
        return [cls.PERFIL, cls.POSTS, cls.METRICAS_ADICIONAIS]
    
    @classmethod
    def get_table_by_name(cls, name: str) -> Optional[TableConfig]:
        """Retorna a configuração de uma tabela pelo nome."""
        for table in cls.get_all_tables():
            if table.name == name:
                return table
        return None


# =============================================================================
# CONFIGURAÇÕES DA API DO TWITTER
# =============================================================================

@dataclass
class TwitterAPIConfig:
    """Configurações da API do Twitter."""
    
    # URL base da API
    BASE_URL: str = "https://api.twitter.com/2"
    
    # Campos do usuário a serem retornados
    USER_FIELDS: str = "public_metrics,created_at,description,location,verified"
    
    # Campos do tweet a serem retornados
    TWEET_FIELDS: str = "text,public_metrics,created_at,referenced_tweets,entities,attachments,non_public_metrics,organic_metrics"
    
    # Expansões para incluir mídia
    EXPANSIONS: str = "attachments.media_keys"
    
    # Campos de mídia a serem retornados
    MEDIA_FIELDS: str = "public_metrics,non_public_metrics,type,duration_ms"
    
    # Máximo de resultados por página
    MAX_RESULTS: int = 100
    
    # Tempo de espera entre requisições (em segundos)
    REQUEST_DELAY: float = 2.0
    
    # Timeout para requisições (em segundos)
    REQUEST_TIMEOUT: int = 30


# =============================================================================
# INSTÂNCIAS DE CONFIGURAÇÃO
# =============================================================================

gcp_config = GCPConfig()
twitter_accounts_config = TwitterAccountsConfig()
date_config = DateConfig()
tables_config = TablesConfig()
twitter_api_config = TwitterAPIConfig()
