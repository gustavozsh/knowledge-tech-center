"""
Google Analytics 4 API Wrapper
A Python wrapper for Google Analytics 4 Data API
"""

from .ga4_client import GA4Client
from .models import DateRange, Dimension, Metric, RunReportRequest

__version__ = "1.0.0"
__all__ = ["GA4Client", "DateRange", "Dimension", "Metric", "RunReportRequest"]
