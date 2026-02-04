"""
Configuracoes da API de Extracao GA4 Campaign.

Este modulo contem todas as configuracoes e constantes da aplicacao.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GCPConfig:
    """Configuracoes do Google Cloud Platform."""
    project_id: str = field(default_factory=lambda: os.environ.get("GCP_PROJECT_ID", ""))
    credentials_path: Optional[str] = field(default_factory=lambda: os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    use_secret_manager: bool = field(default_factory=lambda: os.environ.get("USE_SECRET_MANAGER", "false").lower() == "true")
    secret_id_credentials: str = field(default_factory=lambda: os.environ.get("SECRET_ID_CREDENTIALS", "ga4-credentials"))


@dataclass
class BigQueryConfig:
    """Configuracoes do BigQuery."""
    dataset_id: str = field(default_factory=lambda: os.environ.get("BQ_DATASET_ID", "GA4_CAMPAIGN"))
    location: str = field(default_factory=lambda: os.environ.get("BQ_LOCATION", "US"))


@dataclass
class GA4Config:
    """Configuracoes do Google Analytics 4."""
    property_id: str = field(default_factory=lambda: os.environ.get("GA4_PROPERTY_ID", ""))
    timezone: str = field(default_factory=lambda: os.environ.get("GA4_TIMEZONE", "America/Sao_Paulo"))
    default_days_back: int = 1


@dataclass
class AppConfig:
    """Configuracao principal da aplicacao."""
    gcp: GCPConfig = field(default_factory=GCPConfig)
    bigquery: BigQueryConfig = field(default_factory=BigQueryConfig)
    ga4: GA4Config = field(default_factory=GA4Config)
    debug: bool = field(default_factory=lambda: os.environ.get("DEBUG", "false").lower() == "true")
    port: int = field(default_factory=lambda: int(os.environ.get("PORT", "8080")))


# Instancia global de configuracao
config = AppConfig()
