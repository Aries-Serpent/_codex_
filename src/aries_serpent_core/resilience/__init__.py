"""Resilience primitives for the Codex platform.

Provides building blocks for fault-tolerant external-service integration:

* :class:`~aries_serpent_core.resilience.circuit_breaker.CircuitBreaker` — three-state
  (CLOSED / OPEN / HALF_OPEN) circuit breaker that automatically stops
  propagating calls to a failing downstream service and recovers after a
  configurable timeout.

* :class:`~aries_serpent_core.resilience.circuit_breaker.CircuitState` — enum for the
  three circuit states.

* :class:`~aries_serpent_core.resilience.circuit_breaker.CircuitOpenError` — raised when
  a call is rejected because the circuit is OPEN.

* :class:`~aries_serpent_core.resilience.degradation.GracefulDegradation` — decorator /
  context-manager that catches exceptions and substitutes a fallback value,
  preventing failures in non-critical paths from crashing the main workflow.

* :class:`~aries_serpent_core.resilience.degradation.DegradationError` — raised by
  :class:`GracefulDegradation` when a failure occurs and no fallback is set.

* :func:`~aries_serpent_core.resilience.retry.retry_with_backoff` — decorator / callable
  wrapper that retries a function with exponential backoff and optional jitter.

* :exc:`~aries_serpent_core.resilience.retry.RetryExhausted` — raised after all retry
  attempts are exhausted; the last exception is chained as ``__cause__``.

All three wrappers are synchronous; none awaits a returned coroutine.
Retrying repeats the wrapped operation, so use it only when repetition is
acceptable (for example, an idempotent read). The breaker counts OSError and
import-related failures, whereas retry and degradation use their configured
exception tuples. Choose those tuples explicitly when composing wrappers.

No-network composition example::

    from aries_serpent_core.resilience import (
        CircuitBreaker, CircuitOpenError, GracefulDegradation,
        RetryExhausted, retry_with_backoff,
    )

    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=30)

    @GracefulDegradation(
        fallback="cached",
        exceptions=(CircuitOpenError, RetryExhausted),
    )
    @retry_with_backoff(max_retries=1, base_delay=0, jitter=0, exceptions=(OSError,))
    def read_with_fallback(operation):
        return breaker.call(operation)

    def unavailable():
        raise OSError("service unavailable")

    assert read_with_fallback(unavailable) == "cached"

Here the first OSError opens the breaker. The retry reaches the breaker but
does not invoke ``unavailable`` again: ``CircuitOpenError`` bypasses the
OSError-only retry and is handled by the outer degradation wrapper. Moving
retry inside ``breaker.call`` would instead expose only its final result or
``RetryExhausted`` to the breaker; the latter is not a counted failure.
"""

from aries_serpent_core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)
from aries_serpent_core.resilience.degradation import (
    DegradationError,
    GracefulDegradation,
)
from aries_serpent_core.resilience.retry import (
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
