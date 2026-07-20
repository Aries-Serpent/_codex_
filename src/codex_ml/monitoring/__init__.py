"""Monitoring and observability for Codex ML.

This module provides comprehensive monitoring capabilities including:

- Cognitive logging with memory consolidation (STM/LTM)
- Metrics collection and export (Prometheus)
- System resource monitoring
- Data drift detection
- Model drift detection
- Health checks

Installation:
    Monitoring is included in all profiles. For advanced features:
    pip install codex-ml[cognitive]  # For memory consolidation
    pip install codex-ml[full]       # For all monitoring features

Quick Start:
    from codex_ml.monitoring.codex_logging import CodexLogger
    
    logger = CodexLogger(experiment_name="training")
    logger.log_event("training_start", {"epoch": 0})
    
    # Query learned patterns across sessions
    patterns = logger.query_patterns("training_*")

Features:
    - **Cognitive Logging**: Logs events to memory with automatic consolidation
    - **Pattern Learning**: Learns patterns from event history
    - **STM/LTM**: Automatic consolidation from short-term to long-term memory
    - **Metrics Export**: Prometheus metrics endpoint
    - **Drift Detection**: Detect data and model drift automatically
    - **Health Monitoring**: Track system resource usage

Classes:
    CodexLogger: Main logging interface for cognitive memory
    CodexMetricsRegistry: Prometheus metrics registry
    SystemMetricsLogger: System resource monitoring
    DataDriftDetector: Detect data distribution changes
    ModelDriftDetector: Detect model performance degradation

Functions:
    metrics_enabled: Check if metrics collection is enabled
    get_metrics_text: Get metrics in text format
    metrics_endpoint_fastapi: FastAPI metrics endpoint

Configuration:
    Set environment variables to control monitoring:
    
    CODEX_EXPERIMENTS_DIR: Directory for experiment logs (default: .codex/experiments)
    CODEX_LOG_LEVEL: Logging level (default: INFO)
    CODEX_METRICS_ENABLED: Enable metrics (default: true)
    CODEX_DRIFT_THRESHOLD: Drift detection threshold (default: 0.1)

Integration with Training:
    from codex_ml.monitoring.codex_logging import CodexLogger
    from codex_ml.training.trainer import Trainer
    
    logger = CodexLogger(experiment_name="model_training")
    trainer = Trainer(config=config, logger=logger)
    trainer.train()
    
    # Patterns automatically consolidated from STM to LTM
    patterns = logger.query_patterns("*")

See Also:
    - docs/optional_features_guide.md for Cognitive Brain and Memory Systems
    - docs/INTEGRATION_GUIDE_COMPREHENSIVE.md for integration examples
    - docs/PERFORMANCE_OPTIMIZATION_GUIDE.md for tuning monitoring overhead

Author: Codex Team
Version: 0.3.0
"""

from __future__ import annotations

from .prometheus_metrics import CodexMetricsRegistry, metrics_enabled
from .system_metrics import SystemMetricsLogger

__all__ = [
    "CodexMetricsRegistry",
    "SystemMetricsLogger",
    "get_metrics_text",
    "metrics_enabled",
    "metrics_endpoint_fastapi",
]


def _metrics_endpoint_fastapi_wrapper(
    registry: object | None = None,
) -> object:
    """Graceful wrapper for metrics_endpoint_fastapi when FastAPI is unavailable."""
    try:
        from .metrics_export import metrics_endpoint_fastapi

        return metrics_endpoint_fastapi(registry)
    except ImportError:
        # FastAPI not available - return text metrics directly
        from .metrics_export import get_metrics_text

        return get_metrics_text(registry)


def __getattr__(name: str) -> object:
    """Lazy-load metrics_export to avoid prometheus_client import in core profile."""
    if name == "get_metrics_text":
        from .metrics_export import get_metrics_text

        globals()[name] = get_metrics_text
        return get_metrics_text
    elif name == "metrics_endpoint_fastapi":
        globals()[name] = _metrics_endpoint_fastapi_wrapper
        return _metrics_endpoint_fastapi_wrapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
