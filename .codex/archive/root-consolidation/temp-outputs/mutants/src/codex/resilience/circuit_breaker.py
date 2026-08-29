"""Circuit breaker for external service calls.

Implements the classic three-state circuit-breaker pattern:

* **CLOSED** — normal operation; failures are counted.
* **OPEN**   — calls are rejected immediately with :exc:`CircuitOpenError`
  until the recovery timeout has elapsed.
* **HALF_OPEN** — a limited number of trial calls are allowed; consecutive
  successes close the circuit, any failure re-opens it.

Usage::

    from codex.resilience import CircuitBreaker, CircuitOpenError

    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

    try:
        result = cb.call(requests.get, "https://example.com/api")
    except CircuitOpenError:
        result = cached_fallback()
"""

from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Possible states of a :class:`CircuitBreaker`."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when :meth:`CircuitBreaker.call` is invoked while the circuit is OPEN.

    Args:
        message: Human-readable description of the open circuit.
        retry_after: Approximate seconds remaining before the circuit enters
            HALF_OPEN state (``None`` if unknown).
    """

    def __init__(self, message: str = "Circuit is OPEN", retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreaker:
    """Thread-safe circuit breaker for protecting calls to external services.

    Args:
        failure_threshold: Number of consecutive failures that trip the circuit
            to OPEN state.  Defaults to ``5``.
        recovery_timeout: Seconds to wait in OPEN state before attempting a
            probe call (transition to HALF_OPEN).  Defaults to ``60``.
        success_threshold: Number of consecutive successes in HALF_OPEN state
            required to close the circuit again.  Defaults to ``2``.
        name: Optional label used in log messages.

    Thread safety:
        All state mutations are protected by an internal :class:`threading.Lock`.

    Example::

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        result = cb.call(my_function, arg1, kwarg=value)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60,
        success_threshold: int = 2,
        name: str = "circuit_breaker",
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")
        if success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.name = name

        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._success_count: int = 0
        self._opened_at: float | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        """Current state, recalculated on access to respect *recovery_timeout*."""
        with self._lock:
            return self._get_state_locked()

    def call(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call *fn* with *args* / *kwargs* through the circuit breaker.

        Args:
            fn: Callable to protect.
            *args: Positional arguments forwarded to *fn*.
            **kwargs: Keyword arguments forwarded to *fn*.

        Returns:
            Whatever *fn* returns on success.

        Raises:
            CircuitOpenError: When the circuit is OPEN and the recovery timeout
                has not yet elapsed.
            Exception: Any exception raised by *fn* is re-raised after the
                circuit's failure counter is incremented.
        """
        with self._lock:
            state = self._get_state_locked()

            if state is CircuitState.OPEN:
                retry_after = self._retry_after_locked()
                logger.warning(
                    "[%s] Circuit is OPEN — rejecting call. Retry after ~%.1fs.",
                    self.name,
                    retry_after if retry_after is not None else 0,
                )
                raise CircuitOpenError(
                    f"[{self.name}] Circuit is OPEN",
                    retry_after=retry_after,
                )

        # Execute outside the lock so we don't block other threads during I/O.
        try:
            result = fn(*args, **kwargs)
        except (IOError, OSError) as exc:
            self._on_failure()
            raise exc from exc
        else:
            self._on_success()
            return result

    def reset(self) -> None:
        """Manually reset the circuit to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
        logger.info("[%s] Circuit manually reset to CLOSED.", self.name)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_state_locked(self) -> CircuitState:
        """Return current state, auto-transitioning OPEN → HALF_OPEN if timeout elapsed."""
        if self._state is CircuitState.OPEN:
            if (
                self._opened_at is not None
                and (time.monotonic() - self._opened_at) >= self.recovery_timeout
            ):
                logger.info(
                    "[%s] Recovery timeout elapsed — transitioning OPEN → HALF_OPEN.",
                    self.name,
                )
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
        return self._state

    def _retry_after_locked(self) -> float | None:
        if self._opened_at is None:
            return None
        elapsed = time.monotonic() - self._opened_at
        remaining = self.recovery_timeout - elapsed
        return max(0.0, remaining)

    def _on_success(self) -> None:
        with self._lock:
            state = self._get_state_locked()
            if state is CircuitState.HALF_OPEN:
                self._success_count += 1
                logger.debug(
                    "[%s] HALF_OPEN success %d/%d.",
                    self.name,
                    self._success_count,
                    self.success_threshold,
                )
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self._opened_at = None
                    logger.info(
                        "[%s] Circuit closed after %d consecutive successes.",
                        self.name,
                        self.success_threshold,
                    )
            elif state is CircuitState.CLOSED:
                # Reset failure count on each success in CLOSED state.
                self._failure_count = 0

    def _on_failure(self) -> None:
        with self._lock:
            state = self._get_state_locked()
            if state is CircuitState.HALF_OPEN:
                # Any failure in HALF_OPEN immediately re-opens the circuit.
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()
                self._success_count = 0
                logger.warning("[%s] Failure in HALF_OPEN — circuit re-opened.", self.name)
            elif state is CircuitState.CLOSED:
                self._failure_count += 1
                logger.debug(
                    "[%s] Failure %d/%d.",
                    self.name,
                    self._failure_count,
                    self.failure_threshold,
                )
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    self._opened_at = time.monotonic()
                    logger.warning(
                        "[%s] Failure threshold reached — circuit OPENED.",
                        self.name,
                    )

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CircuitBreaker(name={self.name!r}, state={self._state.value}, "
            f"failures={self._failure_count}/{self.failure_threshold})"
        )
