"""
Observability module for Personalized Learning Path Generator.
Provides logging, tracing, and metrics collection.
"""

from .logging_config import setup_logging, get_logger
from .metrics_collector import MetricsCollector

__all__ = ["setup_logging", "get_logger", "MetricsCollector"]

