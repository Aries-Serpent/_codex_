"""Compatibility wrapper for the legacy ``codex.archive.retry`` import path."""

from __future__ import annotations

from aries_serpent_core.archive.retry import (  # noqa: F401
    RetryConfig,
    calculate_backoff,
    retry_with_backoff,
)


class RetryPolicy:
    """Compatibility adapter matching the legacy retry-policy API."""

    def __init__(self, max_retries=3, backoff_factor=1.0, timeout=None):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

    def get_delay(self, attempt):
        return self.backoff_factor * (2 ** max(0, attempt))

    def execute(self, func, *args, **kwargs):
        import time

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - compatibility fallback
                last_error = exc
                if attempt >= self.max_retries:
                    raise
                time.sleep(self.get_delay(attempt) / 10.0)
        if last_error is not None:
            raise last_error
        raise RuntimeError("RetryPolicy execution failed")


class CircuitBreaker:
    """Legacy circuit-breaker compatibility stub."""

    def __init__(self, failure_threshold=3, timeout=1.0, *args, **kwargs):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "closed"
        self.failures = 0

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            raise RuntimeError("Circuit is open")
        try:
            return func(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.failures > self.failure_threshold:
                self.state = "open"
            raise


__all__ = [
    "CircuitBreaker",
    "RetryConfig",
    "RetryPolicy",
    "calculate_backoff",
    "retry_with_backoff",
]
