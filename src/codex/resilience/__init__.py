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

Quick start::

    from codex.resilience import CircuitBreaker, CircuitOpenError
    from codex.resilience import GracefulDegradation, DegradationError

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

__all__ = [
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "DegradationError",
    "GracefulDegradation",
]
