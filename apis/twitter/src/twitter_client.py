"""
Cliente para a API do Twitter/X v2.

Este módulo fornece uma interface para interagir com a API do Twitter,
permitindo buscar dados de perfis e tweets.

Autor: Manus AI
Data: Janeiro de 2026
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterClient:
    """Cliente para interagir com a API do Twitter v2."""
    
    def __init__(
        self,
        bearer_token: str,
        base_url: str = "https://api.twitter.com/2",
        request_delay: float = 2.0,
        request_timeout: int = 30
    ):
        """
        Inicializa o cliente do Twitter.
        
        Args:
            bearer_token: Token de autenticação Bearer do Twitter
            base_url: URL base da API do Twitter
            request_delay: Tempo de espera entre requisições (segundos)
            request_timeout: Timeout para requisições (segundos)
        """
        self.bearer_token = bearer_token
        self.base_url = base_url
        self.request_delay = request_delay
        self.request_timeout = request_timeout
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Faz uma requisição à API do Twitter.
        
        Args:
            endpoint: Endpoint da API (sem a URL base)
            params: Parâmetros da requisição
            
        Returns:
            Resposta da API em formato de dicionário
            
        Raises:
            requests.exceptions.RequestException: Se houver erro na requisição
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP na requisição: {e}")
            logger.error(f"Response: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            raise
    
    def get_user_by_username(
        self,
        username: str,
        user_fields: str = "public_metrics,created_at,description,location,verified"
    ) -> Dict[str, Any]:
        """
        Busca informações de um usuário pelo username.
        
        Args:
            username: Username do usuário (sem @)
            user_fields: Campos do usuário a serem retornados
            
        Returns:
            Dados do usuário
        """
        endpoint = f"users/by/username/{username}"
        params = {"user.fields": user_fields}
        
        logger.info(f"Buscando dados do usuário: @{username}")
        response = self._make_request(endpoint, params)
        
        if "data" not in response:
            logger.warning(f"Usuário não encontrado: @{username}")
            return {}
        
        return response
    
    def get_user_by_id(
        self,
        user_id: str,
        user_fields: str = "public_metrics,created_at,description,location,verified"
    ) -> Dict[str, Any]:
        """
        Busca informações de um usuário pelo ID.
        
        Args:
            user_id: ID do usuário
            user_fields: Campos do usuário a serem retornados
            
        Returns:
            Dados do usuário
        """
        endpoint = f"users/{user_id}"
        params = {"user.fields": user_fields}
        
        logger.info(f"Buscando dados do usuário ID: {user_id}")
        response = self._make_request(endpoint, params)
        
        if "data" not in response:
            logger.warning(f"Usuário não encontrado: {user_id}")
            return {}
        
        return response
    
    def get_user_tweets(
        self,
        user_id: str,
        start_time: str,
        end_time: str,
        tweet_fields: str = "text,public_metrics,created_at,referenced_tweets,entities,attachments",
        expansions: str = "attachments.media_keys",
        media_fields: str = "public_metrics,type,duration_ms",
        max_results: int = 100,
        exclude: str = "replies",
        pagination_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca tweets de um usuário em um período específico.
        
        Args:
            user_id: ID do usuário
            start_time: Data/hora de início (formato ISO 8601)
            end_time: Data/hora de fim (formato ISO 8601)
            tweet_fields: Campos do tweet a serem retornados
            expansions: Expansões a serem incluídas
            media_fields: Campos de mídia a serem retornados
            max_results: Número máximo de resultados por página
            exclude: Tipos de tweets a excluir
            pagination_token: Token para paginação
            
        Returns:
            Dados dos tweets
        """
        endpoint = f"users/{user_id}/tweets"
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "tweet.fields": tweet_fields,
            "expansions": expansions,
            "media.fields": media_fields,
            "max_results": max_results,
            "exclude": exclude
        }
        
        if pagination_token:
            params["pagination_token"] = pagination_token
        
        logger.info(f"Buscando tweets do usuário {user_id} de {start_time} até {end_time}")
        return self._make_request(endpoint, params)
    
    def get_all_user_tweets(
        self,
        user_id: str,
        start_time: str,
        end_time: str,
        tweet_fields: str = "text,public_metrics,created_at,referenced_tweets,entities,attachments",
        expansions: str = "attachments.media_keys",
        media_fields: str = "public_metrics,type,duration_ms",
        max_results: int = 100,
        exclude: str = "replies"
    ) -> List[Dict[str, Any]]:
        """
        Busca todos os tweets de um usuário em um período, com paginação automática.
        
        Args:
            user_id: ID do usuário
            start_time: Data/hora de início (formato ISO 8601)
            end_time: Data/hora de fim (formato ISO 8601)
            tweet_fields: Campos do tweet a serem retornados
            expansions: Expansões a serem incluídas
            media_fields: Campos de mídia a serem retornados
            max_results: Número máximo de resultados por página
            exclude: Tipos de tweets a excluir
            
        Returns:
            Lista com todos os tweets e dados de mídia
        """
        all_tweets = []
        all_media = {}
        pagination_token = None
        page_count = 0
        
        while True:
            page_count += 1
            logger.info(f"Buscando página {page_count} de tweets...")
            
            response = self.get_user_tweets(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=tweet_fields,
                expansions=expansions,
                media_fields=media_fields,
                max_results=max_results,
                exclude=exclude,
                pagination_token=pagination_token
            )
            
            # Verificar se há dados
            if "data" not in response:
                logger.info("Nenhum tweet encontrado nesta página")
                break
            
            # Adicionar tweets à lista
            all_tweets.extend(response["data"])
            
            # Processar mídia incluída
            if "includes" in response and "media" in response["includes"]:
                for media in response["includes"]["media"]:
                    all_media[media.get("media_key")] = media
            
            # Verificar se há mais páginas
            meta = response.get("meta", {})
            pagination_token = meta.get("next_token")
            
            if not pagination_token:
                logger.info("Não há mais páginas de tweets")
                break
            
            # Aguardar antes da próxima requisição
            time.sleep(self.request_delay)
        
        logger.info(f"Total de tweets encontrados: {len(all_tweets)}")
        
        return {
            "tweets": all_tweets,
            "media": all_media
        }
    
    def get_tweet_by_id(
        self,
        tweet_id: str,
        tweet_fields: str = "text,public_metrics,created_at,referenced_tweets,entities,attachments,non_public_metrics,organic_metrics",
        expansions: str = "attachments.media_keys",
        media_fields: str = "public_metrics,non_public_metrics,type,duration_ms"
    ) -> Dict[str, Any]:
        """
        Busca um tweet específico pelo ID.
        
        Args:
            tweet_id: ID do tweet
            tweet_fields: Campos do tweet a serem retornados
            expansions: Expansões a serem incluídas
            media_fields: Campos de mídia a serem retornados
            
        Returns:
            Dados do tweet
        """
        endpoint = f"tweets/{tweet_id}"
        params = {
            "tweet.fields": tweet_fields,
            "expansions": expansions,
            "media.fields": media_fields
        }
        
        logger.info(f"Buscando tweet ID: {tweet_id}")
        return self._make_request(endpoint, params)
    
    def get_tweets_by_ids(
        self,
        tweet_ids: List[str],
        tweet_fields: str = "text,public_metrics,created_at,referenced_tweets,entities,attachments,non_public_metrics,organic_metrics",
        expansions: str = "attachments.media_keys",
        media_fields: str = "public_metrics,non_public_metrics,type,duration_ms"
    ) -> Dict[str, Any]:
        """
        Busca múltiplos tweets pelos IDs (máximo 100 por requisição).
        
        Args:
            tweet_ids: Lista de IDs dos tweets
            tweet_fields: Campos do tweet a serem retornados
            expansions: Expansões a serem incluídas
            media_fields: Campos de mídia a serem retornados
            
        Returns:
            Dados dos tweets
        """
        if len(tweet_ids) > 100:
            raise ValueError("Máximo de 100 tweets por requisição")
        
        endpoint = "tweets"
        params = {
            "ids": ",".join(tweet_ids),
            "tweet.fields": tweet_fields,
            "expansions": expansions,
            "media.fields": media_fields
        }
        
        logger.info(f"Buscando {len(tweet_ids)} tweets por ID")
        return self._make_request(endpoint, params)


class TwitterDataExtractor:
    """Extrator de dados do Twitter para processamento."""
    
    def __init__(self, client: TwitterClient, timezone: str = "America/Sao_Paulo"):
        """
        Inicializa o extrator de dados.
        
        Args:
            client: Cliente do Twitter
            timezone: Timezone para datas
        """
        self.client = client
        self.timezone = pytz.timezone(timezone)
    
    def extract_profile_data(
        self,
        username: str,
        user_id: str,
        account_name: str
    ) -> Dict[str, Any]:
        """
        Extrai dados do perfil de um usuário.
        
        Args:
            username: Username do usuário
            user_id: ID do usuário
            account_name: Nome configurado da conta
            
        Returns:
            Dados do perfil formatados
        """
        now = datetime.now(self.timezone)
        
        # Buscar dados do usuário
        response = self.client.get_user_by_username(username)
        
        if not response or "data" not in response:
            logger.warning(f"Não foi possível obter dados do perfil: @{username}")
            return {}
        
        user_data = response["data"]
        public_metrics = user_data.get("public_metrics", {})
        
        return {
            "date_extraction": now.strftime("%Y-%m-%d"),
            "date_insertion": now.isoformat(),
            "account_username": username,
            "account_name": account_name,
            "user_id": user_data.get("id", user_id),
            "display_name": user_data.get("name", ""),
            "followers_count": public_metrics.get("followers_count", 0),
            "following_count": public_metrics.get("following_count", 0),
            "tweet_count": public_metrics.get("tweet_count", 0),
            "listed_count": public_metrics.get("listed_count", 0),
        }
    
    def extract_posts_data(
        self,
        username: str,
        user_id: str,
        account_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Extrai dados dos posts de um usuário.
        
        Args:
            username: Username do usuário
            user_id: ID do usuário
            account_name: Nome configurado da conta
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            Lista de posts formatados
        """
        now = datetime.now(self.timezone)
        
        # Formatar datas para a API
        start_time = start_date.strftime("%Y-%m-%dT00:00:00Z")
        end_time = end_date.strftime("%Y-%m-%dT23:59:59Z")
        
        # Buscar tweets
        response = self.client.get_all_user_tweets(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        
        tweets = response.get("tweets", [])
        posts_data = []
        
        for tweet in tweets:
            public_metrics = tweet.get("public_metrics", {})
            
            # Determinar tipo do tweet
            tweet_type = "post"
            referenced_tweets = tweet.get("referenced_tweets", [])
            if referenced_tweets:
                tweet_type = referenced_tweets[0].get("type", "post")
            
            post = {
                "date_extraction": now.strftime("%Y-%m-%d"),
                "date_insertion": now.isoformat(),
                "account_username": username,
                "account_name": account_name,
                "tweet_id": tweet.get("id", ""),
                "created_at": tweet.get("created_at", ""),
                "tweet_type": tweet_type,
                "text": tweet.get("text", ""),
                "url": f"https://twitter.com/{username}/status/{tweet.get('id', '')}",
                "reply_count": public_metrics.get("reply_count", 0),
                "retweet_count": public_metrics.get("retweet_count", 0),
                "like_count": public_metrics.get("like_count", 0),
                "quote_count": public_metrics.get("quote_count", 0),
                "impression_count": public_metrics.get("impression_count", 0),
                "bookmark_count": public_metrics.get("bookmark_count", 0),
            }
            
            posts_data.append(post)
        
        logger.info(f"Extraídos {len(posts_data)} posts de @{username}")
        return posts_data
    
    def extract_additional_metrics(
        self,
        username: str,
        user_id: str,
        account_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Extrai métricas adicionais dos posts (cliques, vídeos, etc.).
        
        Args:
            username: Username do usuário
            user_id: ID do usuário
            account_name: Nome configurado da conta
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            Lista de métricas adicionais formatadas
        """
        now = datetime.now(self.timezone)
        
        # Formatar datas para a API
        start_time = start_date.strftime("%Y-%m-%dT00:00:00Z")
        end_time = end_date.strftime("%Y-%m-%dT23:59:59Z")
        
        # Buscar tweets com métricas adicionais
        response = self.client.get_all_user_tweets(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            tweet_fields="text,public_metrics,created_at,attachments,non_public_metrics,organic_metrics",
            media_fields="public_metrics,non_public_metrics,type,duration_ms"
        )
        
        tweets = response.get("tweets", [])
        media_data = response.get("media", {})
        metrics_data = []
        
        for tweet in tweets:
            non_public_metrics = tweet.get("non_public_metrics", {})
            organic_metrics = tweet.get("organic_metrics", {})
            
            # Verificar se tem mídia
            attachments = tweet.get("attachments", {})
            media_keys = attachments.get("media_keys", [])
            has_media = len(media_keys) > 0
            
            # Dados de mídia
            media_type = ""
            video_view_count = 0
            video_playback_0 = 0
            video_playback_25 = 0
            video_playback_50 = 0
            video_playback_75 = 0
            video_playback_100 = 0
            
            if has_media and media_keys:
                media_key = media_keys[0]
                media_info = media_data.get(media_key, {})
                media_type = media_info.get("type", "")
                
                if media_type == "video":
                    media_public = media_info.get("public_metrics", {})
                    media_non_public = media_info.get("non_public_metrics", {})
                    
                    video_view_count = media_public.get("view_count", 0)
                    video_playback_0 = media_non_public.get("playback_0_count", 0)
                    video_playback_25 = media_non_public.get("playback_25_count", 0)
                    video_playback_50 = media_non_public.get("playback_50_count", 0)
                    video_playback_75 = media_non_public.get("playback_75_count", 0)
                    video_playback_100 = media_non_public.get("playback_100_count", 0)
            
            metric = {
                "date_extraction": now.strftime("%Y-%m-%d"),
                "date_insertion": now.isoformat(),
                "account_username": username,
                "account_name": account_name,
                "tweet_id": tweet.get("id", ""),
                "created_at": tweet.get("created_at", ""),
                "url_link_clicks": non_public_metrics.get("url_link_clicks", 0) or organic_metrics.get("url_link_clicks", 0),
                "user_profile_clicks": non_public_metrics.get("user_profile_clicks", 0) or organic_metrics.get("user_profile_clicks", 0),
                "has_media": has_media,
                "media_type": media_type,
                "video_view_count": video_view_count,
                "video_playback_0_count": video_playback_0,
                "video_playback_25_count": video_playback_25,
                "video_playback_50_count": video_playback_50,
                "video_playback_75_count": video_playback_75,
                "video_playback_100_count": video_playback_100,
            }
            
            metrics_data.append(metric)
        
        logger.info(f"Extraídas métricas adicionais de {len(metrics_data)} posts de @{username}")
        return metrics_data
