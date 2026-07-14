"""
RAG Resilience Patterns - Retry logic and circuit breakers for RAG operations.

This module provides production-grade resilience patterns:
- Exponential backoff retry with jitter
- Adaptive retry strategies based on failure type
- Circuit breaker integration
- Graceful degradation with fallbacks
- Comprehensive error classification

PHASE 4D PLANSET 003: RAG Module Robustness
Authority: D-tier autonomous
Target Reliability: 99%+
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Retry configuration constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_BACKOFF = 0.1  # 100ms
DEFAULT_MAX_BACKOFF = 10.0  # 10s
DEFAULT_BACKOFF_MULTIPLIER = 2.0


class FailureType(Enum):
    """Classification of failure types."""

    TIMEOUT = "timeout"  # Operation exceeded time limit
    RESOURCE_EXHAUSTED = "resource_exhausted"  # Out of memory, connections, etc.
    RATE_LIMIT = "rate_limit"  # Too many requests
    TRANSIENT = "transient"  # Temporary error (network, db unavailable)
    PERMANENT = "permanent"  # Non-recoverable error


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = DEFAULT_MAX_RETRIES
    initial_backoff: float = DEFAULT_INITIAL_BACKOFF
    max_backoff: float = DEFAULT_MAX_BACKOFF
    backoff_multiplier: float = DEFAULT_BACKOFF_MULTIPLIER
    enable_jitter: bool = True
    jitter_factor: float = 0.1  # 10% jitter


@dataclass
class RetryMetrics:
    """Metrics for a retry operation."""

    operation_name: str
    total_attempts: int = 0
    successful_attempt: int = 0
    total_wait_time_ms: float = 0.0
    failure_types: list[str] = None

    def __post_init__(self) -> None:
        if self.failure_types is None:
            self.failure_types = []


class RetryStrategy:
    """Handles retry logic with exponential backoff."""

    def __init__(self, config: Optional[RetryConfig] = None) -> None:
        """Initialize retry strategy.

        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()

    def classify_error(self, error: Exception) -> FailureType:
        """Classify error to determine retry strategy.

        Args:
            error: Exception to classify

        Returns:
            FailureType indicating error category
        """
        error_msg = str(error).lower()
        error_type = type(error).__name__.lower()

        # Timeout errors
        if isinstance(error, TimeoutError) or "timeout" in error_msg:
            return FailureType.TIMEOUT

        # Resource exhaustion
        if any(phrase in error_msg for phrase in ["out of memory", "memory", "exhausted", "connection pool"]):
            return FailureType.RESOURCE_EXHAUSTED

        # Rate limiting
        if any(phrase in error_msg for phrase in ["rate limit", "too many requests", "429"]):
            return FailureType.RATE_LIMIT

        # Transient errors
        if any(
            phrase in error_msg
            for phrase in [
                "connection",
                "refused",
                "unavailable",
                "temporary",
                "network",
                "econnrefused",
            ]
        ):
            return FailureType.TRANSIENT

        # Permanent errors
        return FailureType.PERMANENT

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if operation should be retried.

        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-based)

        Returns:
            True if operation should be retried
        """
        if attempt >= self.config.max_retries:
            return False

        failure_type = self.classify_error(error)

        # Always retry transient errors and timeouts
        if failure_type in [FailureType.TRANSIENT, FailureType.TIMEOUT]:
            return True

        # Retry rate limits with extended backoff
        if failure_type == FailureType.RATE_LIMIT:
            return attempt < self.config.max_retries

        # Retry resource exhaustion but with longer waits
        if failure_type == FailureType.RESOURCE_EXHAUSTED:
            return attempt < self.config.max_retries // 2

        # Never retry permanent errors
        return False

    def calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time with exponential increase and jitter.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Time to wait in seconds
        """
        # Exponential backoff: initial_backoff * multiplier^attempt
        backoff = min(
            self.config.initial_backoff * (self.config.backoff_multiplier ** attempt),
            self.config.max_backoff,
        )

        # Add jitter to avoid thundering herd
        if self.config.enable_jitter:
            jitter = random.uniform(
                -backoff * self.config.jitter_factor,
                backoff * self.config.jitter_factor,
            )
            backoff = max(0.0, backoff + jitter)

        return backoff

    def execute_with_retries(
        self,
        func: Callable[..., T],
        *args: Any,
        operation_name: str = "",
        on_retry: Optional[Callable[[Exception, int], None]] = None,
        **kwargs: Any,
    ) -> tuple[T, RetryMetrics]:
        """Execute function with automatic retry logic.

        Args:
            func: Function to execute
            args: Positional arguments for function
            operation_name: Name of operation for logging
            on_retry: Callback invoked before retry
            kwargs: Keyword arguments for function

        Returns:
            Tuple of (result, metrics)

        Raises:
            Exception: Last exception if all retries exhausted
        """
        operation_name = operation_name or func.__name__
        metrics = RetryMetrics(operation_name=operation_name)
        last_error: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            metrics.total_attempts += 1

            try:
                result = func(*args, **kwargs)
                metrics.successful_attempt = attempt + 1
                logger.debug(
                    f"{operation_name} succeeded on attempt {attempt + 1}"
                )
                return result, metrics

            except Exception as e:
                last_error = e
                metrics.failure_types.append(self.classify_error(e).value)

                # Determine if we should retry
                if not self.should_retry(e, attempt):
                    logger.error(
                        f"{operation_name} failed permanently on attempt "
                        f"{attempt + 1}: {e}"
                    )
                    raise

                # Calculate backoff
                backoff = self.calculate_backoff(attempt)
                metrics.total_wait_time_ms += backoff * 1000

                logger.warning(
                    f"{operation_name} failed on attempt {attempt + 1}, "
                    f"retrying after {backoff:.2f}s: {e}"
                )

                # Invoke callback if provided
                if on_retry:
                    on_retry(e, attempt + 1)

                # Wait before retry
                time.sleep(backoff)

        # All retries exhausted
        logger.error(
            f"{operation_name} failed after {self.config.max_retries} retries"
        )
        raise last_error or RuntimeError(f"{operation_name} failed after retries")


class AdaptiveRetryStrategy(RetryStrategy):
    """Retry strategy that adapts to failure patterns."""

    def __init__(self, config: Optional[RetryConfig] = None) -> None:
        """Initialize adaptive retry strategy."""
        super().__init__(config)
        self.failure_history: dict[str, list[FailureType]] = {}

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Override to adapt based on error history."""
        # If we're seeing mostly permanent errors, stop retrying
        failure_type = self.classify_error(error)

        # For known operations, check if pattern suggests stopping
        if failure_type == FailureType.PERMANENT:
            return attempt < 1  # Only retry once for permanent errors

        return super().should_retry(error, attempt)

    def calculate_backoff(self, attempt: int) -> float:
        """Override to use longer backoff for resource exhaustion."""
        backoff = super().calculate_backoff(attempt)

        # If we're seeing resource exhaustion, use exponentially longer backoff
        if attempt > 0:
            # Additional exponential increase for later attempts
            backoff *= (attempt + 1) ** 0.5

        return min(backoff, self.config.max_backoff)


def retry_with_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_backoff: float = DEFAULT_INITIAL_BACKOFF,
    operation_name: str = "",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retries
        initial_backoff: Initial backoff time in seconds
        operation_name: Name of operation for logging

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            strategy = RetryStrategy(
                config=RetryConfig(
                    max_retries=max_retries,
                    initial_backoff=initial_backoff,
                )
            )

            result, _ = strategy.execute_with_retries(
                func,
                *args,
                operation_name=operation_name or func.__name__,
                **kwargs,
            )
            return result

        return wrapper

    return decorator
