"""Monitoring Dashboard Package."""

__version__ = "1.0.0"
__author__ = "Copilot Agent System"

from .metrics_collector import MetricsCollector
from .system_metrics import SystemMetricsLogger

__all__ = ["MetricsCollector", "SystemMetricsLogger"]
