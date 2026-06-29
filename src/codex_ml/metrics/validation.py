"""Metric registry validation utilities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class MetricValidationError(Exception):
    """Exception raised when metric validation fails."""


def validate_metric_registry() -> list[str]:
    """Validate all registered metrics have implementations.

    Checks that all metrics in the registry can be successfully
    retrieved and are callable.

    Returns:
        list of validation warnings (empty if all valid)

    Raises:
        MetricValidationError: If a critical validation error occurs
    """
    warnings: list[str] = []

    try:
        from codex_ml.metrics.registry import METRIC_REGISTRY, get_metric
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        raise MetricValidationError(f"Failed to import metric registry: {e}") from e

    for metric_name in METRIC_REGISTRY:
        try:
            metric_fn = get_metric(metric_name)
            if not callable(metric_fn):
                raise MetricValidationError(f"Metric '{metric_name}' is not callable")
        except (ImportError, AttributeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            raise MetricValidationError(
                f"Metric '{metric_name}' registered but not implemented: {e}"
            ) from e

    return warnings


def validate_metric_exists(metric_name: str) -> bool:
    """Check if a specific metric exists and is callable.

    Args:
        metric_name: Name of the metric to validate

    Returns:
        True if metric exists and is callable, False otherwise
    """
    try:
        from codex_ml.metrics.registry import get_metric

        metric_fn = get_metric(metric_name)
        return callable(metric_fn)
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return False


def get_all_registered_metrics() -> list[str]:
    """Get list of all registered metric names.

    Returns:
        list of metric names
    """
    try:
        from codex_ml.metrics.registry import METRIC_REGISTRY

        return list(METRIC_REGISTRY.keys())
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        return []


__all__ = [
    "MetricValidationError",
    "get_all_registered_metrics",
    "validate_metric_exists",
    "validate_metric_registry",
]
