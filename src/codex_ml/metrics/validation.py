"""Metric registry validation utilities."""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from typing import List


class MetricValidationError(Exception):
    """Exception raised when metric validation fails."""

    pass


def validate_metric_registry() -> List[str]:
    """Validate all registered metrics have implementations.

    Checks that all metrics in the registry can be successfully
    retrieved and are callable.

    Returns:
        List of validation warnings (empty if all valid)

    Raises:
        MetricValidationError: If a critical validation error occurs
    """
    warnings: List[str] = []

    try:
        from codex_ml.metrics.registry import METRIC_REGISTRY, get_metric
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        raise MetricValidationError(f"Failed to import metric registry: {e}") from e

    for metric_name in METRIC_REGISTRY.keys():
        try:
            metric_fn = get_metric(metric_name)
            if not callable(metric_fn):
                raise MetricValidationError(f"Metric '{metric_name}' is not callable")
        except (ImportError, AttributeError) as e:
            logger.debug(f"Exception: {e}")
            raise MetricValidationError(
                f"Metric '{metric_name}' registered but not implemented: {e}"
            ) from e
        except Exception as e:
            logger.debug(f"Exception: {e}")
            # Non-critical errors become warnings
            warnings.append(
                f"Warning: Metric '{metric_name}' raised exception during validation: {e}"
            )

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
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False


def get_all_registered_metrics() -> List[str]:
    """Get list of all registered metric names.

    Returns:
        List of metric names
    """
    try:
        from codex_ml.metrics.registry import METRIC_REGISTRY

        return list(METRIC_REGISTRY.keys())
    except ImportError as e:
       logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        return []


__all__ = [
    "MetricValidationError",
    "validate_metric_registry",
    "validate_metric_exists",
    "get_all_registered_metrics",
]
