"""
RAG Timeout Management - Prevent timeout failures in RAG pipeline.

This module provides timeout guards, circuit breakers, and fallback logic
to ensure RAG operations complete reliably within service SLAs.

Features:
- Adaptive timeout configuration based on operation type
- Circuit breaker pattern for cascading failure prevention
- Graceful degradation with fallback strategies
- Comprehensive timeout telemetry and alerting
- Timeout budget management for complex operations

PHASE 4D PLANSET 003: RAG Module Robustness
Authority: D-tier autonomous
Target Reliability: 99%+
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

# Timeout constants (in seconds)
DEFAULT_EMBEDDING_TIMEOUT = 30.0  # Model loading + single embedding
DEFAULT_BATCH_EMBEDDING_TIMEOUT = 60.0  # Batch embedding (up to 100 texts)
DEFAULT_RETRIEVAL_TIMEOUT = 10.0  # Vector search
DEFAULT_QUANTUM_TIMEOUT = 15.0  # Quantum scoring
DEFAULT_CACHE_TIMEOUT = 2.0  # Cache operations
DEFAULT_CIRCUIT_BREAKER_THRESHOLD = 5  # Failures before circuit opens
DEFAULT_CIRCUIT_BREAKER_RESET_TIME = 60.0  # Seconds before attempting reset

T = TypeVar("T")


class CircuitState(Enum):
    """States for circuit breaker pattern."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class TimeoutConfig:
    """Configuration for timeout management."""

    embedding_timeout: float = DEFAULT_EMBEDDING_TIMEOUT
    batch_embedding_timeout: float = DEFAULT_BATCH_EMBEDDING_TIMEOUT
    retrieval_timeout: float = DEFAULT_RETRIEVAL_TIMEOUT
    quantum_timeout: float = DEFAULT_QUANTUM_TIMEOUT
    cache_timeout: float = DEFAULT_CACHE_TIMEOUT
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = DEFAULT_CIRCUIT_BREAKER_THRESHOLD
    circuit_breaker_reset_time: float = DEFAULT_CIRCUIT_BREAKER_RESET_TIME
    enable_telemetry: bool = True


@dataclass
class TimeoutMetrics:
    """Metrics for timeout monitoring."""

    operation_type: str
    start_time: float
    end_time: float = 0.0
    duration_ms: float = 0.0
    timed_out: bool = False
    fallback_used: bool = False
    circuit_state: str = "closed"
    error_message: str = ""

    def compute_duration(self) -> float:
        """Compute operation duration in milliseconds."""
        if self.end_time == 0.0:
            self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        return self.duration_ms


@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker."""

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    state: CircuitState = CircuitState.CLOSED
    last_state_change: float = field(default_factory=time.time)

    def reset(self) -> None:
        """Reset failure counters."""
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0

    def is_open(self, config: TimeoutConfig) -> bool:
        """Check if circuit should be open."""
        if self.state == CircuitState.OPEN:
            # Check if reset time has passed
            if time.time() - self.last_state_change >= config.circuit_breaker_reset_time:
                # Try half-open state
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
                return False
            return True

        if self.state == CircuitState.HALF_OPEN:
            if self.failure_count > 0:
                # Transition back to open
                self.state = CircuitState.OPEN
                self.last_state_change = time.time()
                logger.warning("Circuit breaker reopening after HALF_OPEN failure")
                return True
            elif self.success_count >= 3:
                # Transition back to closed
                self.state = CircuitState.CLOSED
                self.last_state_change = time.time()
                self.reset()
                logger.info("Circuit breaker closing after successful recovery")
                return False
            return False

        return False

    def record_success(self, config: TimeoutConfig) -> None:
        """Record successful operation."""
        self.success_count += 1
        if self.state == CircuitState.HALF_OPEN:
            logger.debug(f"Circuit breaker success in HALF_OPEN: {self.success_count}/3")

    def record_failure(self, config: TimeoutConfig) -> None:
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= config.circuit_breaker_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error(
                f"Circuit breaker opening after {self.failure_count} failures"
            )


class TimeoutManager:
    """Central timeout management for RAG operations."""

    def __init__(self, config: Optional[TimeoutConfig] = None) -> None:
        """Initialize timeout manager.

        Args:
            config: Timeout configuration
        """
        self.config = config or TimeoutConfig()
        self._circuit_breakers: dict[str, CircuitBreakerState] = {}
        self._metrics: list[TimeoutMetrics] = []

        logger.info(
            "TimeoutManager initialized: embedding_timeout=%.1f, "
            "retrieval_timeout=%.1f, circuit_breaker_enabled=%s",
            self.config.embedding_timeout,
            self.config.retrieval_timeout,
            self.config.enable_circuit_breaker,
        )

    def get_circuit_breaker(self, operation_type: str) -> CircuitBreakerState:
        """Get or create circuit breaker for operation type."""
        if operation_type not in self._circuit_breakers:
            self._circuit_breakers[operation_type] = CircuitBreakerState()
        return self._circuit_breakers[operation_type]

    def is_circuit_open(self, operation_type: str) -> bool:
        """Check if circuit breaker is open for operation."""
        if not self.config.enable_circuit_breaker:
            return False

        circuit = self.get_circuit_breaker(operation_type)
        return circuit.is_open(self.config)

    def record_timeout(self, operation_type: str, metrics: TimeoutMetrics) -> None:
        """Record a timeout event."""
        if self.config.enable_telemetry:
            self._metrics.append(metrics)
            metrics.compute_duration()

            logger.warning(
                f"Timeout recorded: {operation_type} - {metrics.duration_ms:.1f}ms "
                f"(fallback={'used' if metrics.fallback_used else 'not used'})"
            )

    def record_success(self, operation_type: str, metrics: TimeoutMetrics) -> None:
        """Record successful operation."""
        if self.config.enable_telemetry:
            self._metrics.append(metrics)
            if hasattr(metrics, 'compute_duration'):
                metrics.compute_duration()

            if self.config.enable_circuit_breaker:
                circuit = self.get_circuit_breaker(operation_type)
                circuit.record_success(self.config)

    def record_failure(self, operation_type: str, metrics: TimeoutMetrics, error: Optional[str] = None) -> None:
        """Record failed operation."""
        if error and hasattr(metrics, 'error_message'):
            metrics.error_message = error

        if self.config.enable_telemetry:
            self._metrics.append(metrics)
            if hasattr(metrics, 'compute_duration'):
                metrics.compute_duration()

            if self.config.enable_circuit_breaker:
                circuit = self.get_circuit_breaker(operation_type)
                circuit.record_failure(self.config)

                logger.error(
                    f"Operation failed: {operation_type} - {error} "
                    f"(circuit_state={circuit.state.value}, failures={circuit.failure_count})"
                )

    def get_timeout_for_operation(self, operation_type: str) -> float:
        """Get configured timeout for operation type."""
        timeout_map = {
            "embedding": self.config.embedding_timeout,
            "batch_embedding": self.config.batch_embedding_timeout,
            "retrieval": self.config.retrieval_timeout,
            "quantum": self.config.quantum_timeout,
            "cache": self.config.cache_timeout,
        }
        return timeout_map.get(operation_type, self.config.embedding_timeout)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of timeout metrics."""
        if not self._metrics:
            return {"total_operations": 0, "timeouts": 0, "failures": 0}

        total = len(self._metrics)
        timeouts = sum(1 for m in self._metrics if m.timed_out)
        fallbacks = sum(1 for m in self._metrics if m.fallback_used)
        avg_duration = sum(m.duration_ms for m in self._metrics) / total if total > 0 else 0

        return {
            "total_operations": total,
            "timeouts": timeouts,
            "timeout_rate": timeouts / total if total > 0 else 0,
            "fallbacks_used": fallbacks,
            "average_duration_ms": avg_duration,
            "circuit_breakers": {
                op_type: {
                    "state": circuit.state.value,
                    "failures": circuit.failure_count,
                    "successes": circuit.success_count,
                }
                for op_type, circuit in self._circuit_breakers.items()
            },
        }

    def clear_metrics(self) -> None:
        """Clear accumulated metrics."""
        self._metrics.clear()
        logger.info("Timeout metrics cleared")


def with_timeout(
    operation_type: str,
    timeout_manager: Optional[TimeoutManager] = None,
    fallback_fn: Optional[Callable[..., T]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add timeout protection to functions.

    Args:
        operation_type: Type of operation for timeout management
        timeout_manager: TimeoutManager instance (uses default if None)
        fallback_fn: Optional fallback function if timeout occurs

    Returns:
        Decorated function with timeout protection
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal timeout_manager
            if timeout_manager is None:
                timeout_manager = _get_default_timeout_manager()

            # Check circuit breaker
            if timeout_manager.is_circuit_open(operation_type):
                logger.warning(f"Circuit breaker open for {operation_type}, using fallback")
                if fallback_fn:
                    return fallback_fn(*args, **kwargs)
                raise RuntimeError(f"Circuit breaker open for {operation_type}")

            # Get timeout for operation
            timeout = timeout_manager.get_timeout_for_operation(operation_type)

            # Record start
            metrics = TimeoutMetrics(
                operation_type=operation_type,
                start_time=time.time(),
            )

            try:
                # Execute with timeout
                result = _execute_with_timeout(func, timeout, *args, **kwargs)
                metrics.end_time = time.time()
                timeout_manager.record_success(operation_type, metrics)
                return result

            except TimeoutError:
                metrics.timed_out = True
                metrics.end_time = time.time()
                timeout_manager.record_timeout(operation_type, metrics)

                if fallback_fn:
                    logger.warning(
                        f"Timeout on {operation_type} after {timeout}s, "
                        "using fallback"
                    )
                    metrics.fallback_used = True
                    return fallback_fn(*args, **kwargs)
                raise

            except Exception as e:
                metrics.end_time = time.time()
                timeout_manager.record_failure(
                    operation_type, metrics, str(e)
                )
                raise

        return wrapper

    return decorator


def _execute_with_timeout(
    func: Callable[..., T],
    timeout: float,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute function with timeout protection.

    For sync functions, uses signal-based timeout (Unix only).
    For async functions, uses asyncio.timeout.
    """
    import inspect

    if inspect.iscoroutinefunction(func):
        # For async functions, use asyncio.timeout
        return asyncio.run(_async_timeout_wrapper(func, timeout, *args, **kwargs))
    else:
        # For sync functions, use a simple time-based check
        import signal

        class TimeoutHandler:
            def __init__(self, timeout: float):
                self.timeout = timeout
                self.start_time = time.time()

            def __enter__(self) -> None:
                if hasattr(signal, "SIGALRM"):
                    # Unix systems
                    signal.signal(signal.SIGALRM, self._timeout_handler)
                    signal.alarm(int(self.timeout) + 1)

            def __exit__(self, *args: Any) -> None:
                if hasattr(signal, "SIGALRM"):
                    signal.alarm(0)

            def _timeout_handler(self, signum: int, frame: Any) -> None:
                raise TimeoutError(f"Operation timed out after {self.timeout}s")

        with TimeoutHandler(timeout):
            elapsed = time.time() - TimeoutHandler(timeout).start_time
            if elapsed > timeout:
                raise TimeoutError(f"Operation timed out after {timeout}s")
            return func(*args, **kwargs)


async def _async_timeout_wrapper(
    func: Callable[..., T],
    timeout: float,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Wrapper for async functions with timeout."""
    try:
        # Python 3.11+ has asyncio.timeout context manager
        import sys
        if sys.version_info >= (3, 11):
            async with asyncio.timeout(timeout):
                return await func(*args, **kwargs)
        else:
            # Fallback for older Python versions
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout}s")


# Global default timeout manager instance
_default_timeout_manager: Optional[TimeoutManager] = None


def _get_default_timeout_manager() -> TimeoutManager:
    """Get or create default timeout manager."""
    global _default_timeout_manager
    if _default_timeout_manager is None:
        _default_timeout_manager = TimeoutManager()
    return _default_timeout_manager


def set_default_timeout_manager(manager: TimeoutManager) -> None:
    """Set global default timeout manager."""
    global _default_timeout_manager
    _default_timeout_manager = manager


def get_default_timeout_manager() -> TimeoutManager:
    """Get global default timeout manager."""
    return _get_default_timeout_manager()
