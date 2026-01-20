"""
Google Analytics 4 API Wrapper
A Python wrapper for Google Analytics 4 Data API
"""

from .ga4_client import GoogleAnalytics4, GA4Client
from .models import DateRange, Dimension, Metric, RunReportRequest
from .secret_manager import SecretManager
from .bigquery_writer import BigQueryWriter

__version__ = "1.0.0"
__all__ = [
    "GoogleAnalytics4",
    "GA4Client",
    "DateRange",
    "Dimension",
    "Metric",
    "RunReportRequest",
    "SecretManager",
    "BigQueryWriter",
]
