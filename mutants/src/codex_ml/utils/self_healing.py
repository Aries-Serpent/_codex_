"""Self-healing utilities for autonomous error recovery.

This module provides self-healing capabilities that detect and automatically
remediate common training failures.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "FailureType",
    "OOMHandler",
    "SelfHealingContext",
    "auto_remediate",
]


class FailureType(Enum):
    """Types of failures that can be auto-remediated."""

    OOM = "out_of_memory"
    METRIC_REGRESSION = "metric_regression"
    CHECKPOINT_CORRUPTION = "checkpoint_corruption"
    CONFIG_DRIFT = "config_drift"
    UNKNOWN = "unknown"


class OOMHandler:
    """Handler for Out-of-Memory errors with automatic batch size reduction."""

    def __init__(self, initial_batch_size: int, min_batch_size: int = 1):
        """Initialize OOM handler.

        Args:
            initial_batch_size: Starting batch size
            min_batch_size: Minimum allowed batch size
        """
        self.initial_batch_size = initial_batch_size
        self.current_batch_size = initial_batch_size
        self.min_batch_size = min_batch_size
        self.retry_count = 0
        self.max_retries = 3

    def can_retry(self) -> bool:
        """Check if we can retry with reduced batch size."""
        return self.retry_count < self.max_retries and self.current_batch_size > self.min_batch_size

    def reduce_batch_size(self) -> int:
        """Reduce batch size for retry.

        Returns:
            New batch size
        """
        # Reduce by half, but not below minimum
        new_size = max(self.current_batch_size // 2, self.min_batch_size)

        logger.warning(
            f"🔧 OOM detected: Reducing batch size "
            f"{self.current_batch_size} → {new_size} (retry {self.retry_count + 1}/{self.max_retries})"  # noqa: E501
        )

        self.current_batch_size = new_size
        self.retry_count += 1

        return new_size

    def reset(self):
        """Reset to initial state."""
        self.current_batch_size = self.initial_batch_size
        self.retry_count = 0


class SelfHealingContext:
    """Context manager for self-healing training with automatic error recovery.

    Example:
        with SelfHealingContext() as healer:
            train_model(batch_size=healer.batch_size)
    """

    def __init__(
        self,
        batch_size: int = 32,
        enable_oom_recovery: bool = True,
        enable_checkpoint_rollback: bool = True,
    ):
        """Initialize self-healing context.

        Args:
            batch_size: Initial batch size
            enable_oom_recovery: Enable OOM auto-recovery
            enable_checkpoint_rollback: Enable checkpoint rollback on failure
        """
        self.batch_size = batch_size
        self.enable_oom_recovery = enable_oom_recovery
        self.enable_checkpoint_rollback = enable_checkpoint_rollback

        self.oom_handler = OOMHandler(batch_size)
        self.failures: list[tuple[FailureType, Exception]] = []

    def __enter__(self):
        """Enter self-healing context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit self-healing context with error handling."""
        if exc_type is None:
            return False

        # Detect failure type
        failure_type = self._classify_failure(exc_type, exc_val, exc_tb)
        self.failures.append((failure_type, exc_val))

        # Attempt remediation
        remediated = self._attempt_remediation(failure_type, exc_val)

        if remediated:
            logger.info(f"✓ Auto-remediation successful for {failure_type.value}")
            return True  # Suppress exception

        logger.error(f"❌ Auto-remediation failed for {failure_type.value}")
        return False  # Propagate exception

    def _classify_failure(self, exc_type, exc_val, exc_tb) -> FailureType:
        """Classify the type of failure from exception.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            FailureType enum
        """
        exc_str = str(exc_val).lower() if exc_val else ""

        # Check for OOM errors
        if (
            "out of memory" in exc_str
            or "oom" in exc_str
            or ("cuda" in exc_str and "memory" in exc_str)
        ):
            return FailureType.OOM

        # Check for checkpoint corruption
        if "corrupt" in exc_str or "integrity" in exc_str or "hash" in exc_str:
            return FailureType.CHECKPOINT_CORRUPTION

        # Check for config drift
        if "config" in exc_str and "drift" in exc_str:
            return FailureType.CONFIG_DRIFT

        return FailureType.UNKNOWN

    def _attempt_remediation(self, failure_type: FailureType, exc_val: Exception) -> bool:
        """Attempt to remediate the failure.

        Args:
            failure_type: Type of failure
            exc_val: Exception that occurred

        Returns:
            True if remediation successful, False otherwise
        """
        if failure_type == FailureType.OOM and self.enable_oom_recovery:
            return self._remediate_oom()

        if failure_type == FailureType.CHECKPOINT_CORRUPTION and self.enable_checkpoint_rollback:
            return self._remediate_checkpoint_corruption()

        return False

    def _remediate_oom(self) -> bool:
        """Remediate OOM error by reducing batch size.

        Returns:
            True if can retry with reduced batch size
        """
        if self.oom_handler.can_retry():
            self.batch_size = self.oom_handler.reduce_batch_size()
            return True

        logger.error("Cannot remediate OOM: max retries reached or min batch size")
        return False

    def _remediate_checkpoint_corruption(self) -> bool:
        """Remediate checkpoint corruption by rolling back.

        Returns:
            True if rollback successful
        """
        logger.warning("🔧 Checkpoint corruption detected: attempting rollback")
        # Implementation would load previous checkpoint
        # For now, just log
        return False


def auto_remediate(
    func: Callable, *args, max_retries: int = 3, batch_size: int = 32, **kwargs
) -> Any:
    """Execute function with automatic error remediation.

    Args:
        func: Function to execute
        *args: Positional arguments for func
        max_retries: Maximum retry attempts
        batch_size: Initial batch size
        **kwargs: Keyword arguments for func

    Returns:
        Function return value

    Raises:
        Exception: If remediation fails after max_retries
    """
    attempt = 0
    last_exception = None

    while attempt < max_retries:
        try:
            with SelfHealingContext(batch_size=batch_size) as healer:
                # Update batch_size in kwargs if present
                if "batch_size" in kwargs:
                    kwargs["batch_size"] = healer.batch_size

                return func(*args, **kwargs)

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            last_exception = e
            attempt += 1

            logger.warning(
                f"Attempt {attempt}/{max_retries} failed: {e}. "
                f"{'Retrying...' if attempt < max_retries else 'Giving up.'}"
            )

            if attempt >= max_retries:
                break

    # All retries exhausted
    if last_exception is None:
        raise RuntimeError(
            f"All {max_retries} retries exhausted without capturing exception context"
        )
    raise last_exception
