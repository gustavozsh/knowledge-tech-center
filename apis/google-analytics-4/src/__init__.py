"""
Google Analytics 4 API Wrapper
A Python wrapper for Google Analytics 4 Data API

Este pacote fornece uma interface simplificada para interagir com a
Google Analytics 4 Data API e salvar os dados no BigQuery.

Módulos:
    - ga4_client: Cliente principal para a API GA4
    - bigquery_writer: Writer para salvar dados no BigQuery
    - secret_manager: Cliente para o Secret Manager
    - models: Modelos de dados (DateRange, Dimension, Metric, etc.)
    - report_manager: Gerenciador de relatórios por categoria

Versão Python: 3.11+
"""

from .ga4_client import GoogleAnalytics4, GA4Client
from .models import DateRange, Dimension, Metric, RunReportRequest, OrderBy, FilterExpression
from .secret_manager import SecretManager
from .bigquery_writer import BigQueryWriter
from .report_manager import ReportManager, ReportConfig

__version__ = "2.0.0"

__all__ = [
    # Clientes
    "GoogleAnalytics4",
    "GA4Client",
    "BigQueryWriter",
    "SecretManager",
    "ReportManager",
    
    # Modelos
    "DateRange",
    "Dimension",
    "Metric",
    "RunReportRequest",
    "OrderBy",
    "FilterExpression",
    "ReportConfig",
]
