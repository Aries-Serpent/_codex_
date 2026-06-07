"""Resilience primitives for the Codex platform.

Provides building blocks for fault-tolerant external-service integration:

* :class:`~codex.resilience.circuit_breaker.CircuitBreaker` — three-state
  (CLOSED / OPEN / HALF_OPEN) circuit breaker that automatically stops
  propagating calls to a failing downstream service and recovers after a
  configurable timeout.

* :class:`~codex.resilience.circuit_breaker.CircuitState` — enum for the
  three circuit states.

* :class:`~codex.resilience.circuit_breaker.CircuitOpenError` — raised when
  a call is rejected because the circuit is OPEN.

* :class:`~codex.resilience.degradation.GracefulDegradation` — decorator /
  context-manager that catches exceptions and substitutes a fallback value,
  preventing failures in non-critical paths from crashing the main workflow.

* :class:`~codex.resilience.degradation.DegradationError` — raised by
  :class:`GracefulDegradation` when a failure occurs and no fallback is set.

* :func:`~codex.resilience.retry.retry_with_backoff` — decorator / callable
  wrapper that retries a function with exponential backoff and optional jitter.

* :exc:`~codex.resilience.retry.RetryExhausted` — raised after all retry
  attempts are exhausted; the last exception is chained as ``__cause__``.

Quick start::

    from codex.resilience import CircuitBreaker, CircuitOpenError
    from codex.resilience import GracefulDegradation, DegradationError
    from codex.resilience import retry_with_backoff, RetryExhausted

    # --- Circuit breaker ---
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
    try:
        result = cb.call(http_get, url)
    except CircuitOpenError:
        result = cached_value

    # --- Graceful degradation (decorator) ---
    @GracefulDegradation(fallback="N/A")
    def fetch_metric() -> str:
        return external_api.get_metric()

    # --- Graceful degradation (context manager) ---
    with GracefulDegradation(fallback=None) as dg:
        dg.result = risky_operation()
    value = dg.result  # None if risky_operation() raised

    # --- Exponential backoff retry (decorator) ---
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def call_external_api() -> dict:
        return requests.get("https://api.example.com/data").json()

    # --- Exponential backoff retry (direct wrapper) ---
    try:
        result = retry_with_backoff(max_retries=2)(some_func)(arg)
    except RetryExhausted as exc:
        logger.error("All retries failed: %s", exc.__cause__)
"""

from codex.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)
from codex.resilience.degradation import (
    DegradationError,
    GracefulDegradation,
)
from codex.resilience.retry import (
    RetryExhausted,
    retry_with_backoff,
)

__all__ = [
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "DegradationError",
    "GracefulDegradation",
    "RetryExhausted",
    "retry_with_backoff",
]
