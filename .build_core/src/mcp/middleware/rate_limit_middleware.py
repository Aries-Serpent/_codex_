"""
Rate Limit Middleware Module

This module provides functionality for rate limit middleware.

Usage:
    from middleware.rate_limit_middleware import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

DEFAULT_RATE = 5
BURST = 10

# ---------------------------------------------------------------------------
# Backend protocol
# ---------------------------------------------------------------------------


class _RateLimitBackend(ABC):
    """Abstract backend for rate-limit token buckets."""

    @abstractmethod
    def consume(self, key: str, rate: float, burst: int) -> bool:
        """Return True if the request should be allowed, False if throttled."""
        raise NotImplementedError("Subclasses must implement consume()")

    def close(self) -> None:
        """Optional cleanup."""


# Module-level bucket store used by _InMemoryBackend.
# Exposed at module scope so tests can call ``rate_limit_middleware._BUCKETS.clear()``
# to reset state between runs without needing to reload the module.
# All _InMemoryBackend instances share this dict (process-local singleton state).
_BUCKETS: dict[str, dict] = {}


class _InMemoryBackend(_RateLimitBackend):
    """Process-local in-memory token bucket.

    All instances share the module-level ``_BUCKETS`` dict (singleton state).
    Tests can reset state by calling ``rate_limit_middleware._BUCKETS.clear()``.

    WARNING: Each worker process has an independent state.  In a multi-worker
    deployment (Gunicorn/uvicorn with ``--workers N``) each client gets N× the
    configured rate limit.  Use ``_RedisBackend`` for shared-state rate limiting.
    """

    def consume(self, key: str, rate: float, burst: int) -> bool:
        b = _BUCKETS.setdefault(key, {"tokens": float(burst), "last": time.time()})
        now = time.time()
        elapsed = now - b["last"]
        b["tokens"] = min(burst, b["tokens"] + elapsed * rate)
        b["last"] = now
        if b["tokens"] < 1:
            return False
        b["tokens"] -= 1
        return True

    def clear(self) -> None:
        _BUCKETS.clear()


class _RedisBackend(_RateLimitBackend):
    """Redis-backed token bucket (safe for multi-process deployments).

    Uses atomic INCR + EXPIRE so each sliding window slot is counted
    correctly across all worker processes and replicas.

    Required env var:  ``REDIS_URL``  (e.g. ``redis://localhost:6379/0``)
    """

    def __init__(self, redis_url: str, window: int = 1) -> None:
        import redis as _redis  # guarded import — optional dependency

        self._redis = _redis.Redis.from_url(redis_url, decode_responses=True)
        self._window = window  # sliding window size in seconds

    def consume(self, key: str, rate: float, burst: int) -> bool:
        slot = int(time.time() // self._window)
        redis_key = f"rl:{key}:{slot}"
        try:
            count = self._redis.incr(redis_key)
            if count == 1:
                self._redis.expire(redis_key, self._window * 2)
            # Allow up to ``burst`` requests per window slot
            return count <= burst
        except (IOError, OSError) as exc:
            # Redis unavailable — allow the request (fail open)
            logging.getLogger(__name__).warning(
                "Redis rate-limit backend error: %s — allowing request", exc
            )
            return True

    def close(self) -> None:
        try:
            self._redis.close()
        except (ConnectionError, TimeoutError) as exc:
            logging.getLogger(__name__).warning("Redis rate-limit backend close() error: %s", exc)


def _build_backend(rate: float, burst: int) -> _RateLimitBackend:
    """Select the best available backend.

    Preference: Redis (if ``REDIS_URL`` is set and ``redis`` is installed) →
    in-memory (fallback).
    """
    redis_url = os.environ.get("REDIS_URL") or os.environ.get("RATE_LIMIT_REDIS_URL")
    if redis_url:
        try:
            backend = _RedisBackend(redis_url)
            logging.getLogger(__name__).info(
                "RateLimitMiddleware: using Redis backend (%s)", redis_url
            )
            return backend
        except ImportError:
            logging.getLogger(__name__).warning(
                "redis package not installed; falling back to in-memory rate limiting. "
                "Install with: pip install redis"
            )
    logging.getLogger(__name__).warning(
        "RateLimitMiddleware: using process-local in-memory backend. "
        "Set REDIS_URL for distributed rate limiting."
    )
    return _InMemoryBackend()


# Kept for backward compatibility with tests that call clear_buckets()
def clear_buckets() -> None:
    """Clear the in-memory buckets on the module-level default backend (if any)."""
    if isinstance(_DEFAULT_BACKEND, _InMemoryBackend):
        _DEFAULT_BACKEND.clear()


_DEFAULT_BACKEND: _RateLimitBackend | None = None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket rate limiter middleware.

    Automatically selects a Redis backend when ``REDIS_URL`` is set (requires
    the ``redis`` package), otherwise falls back to a process-local in-memory
    bucket.

    Configuration (env vars or constructor args):
        ``RATE_LIMIT_RATE``  — token refill rate per second (default: 5)
        ``RATE_LIMIT_BURST`` — maximum burst size (default: 10)
        ``REDIS_URL``        — Redis connection string for distributed limiting

    Principal is taken from ``request.state.principal.api_key`` (falls back to
    ``"anonymous"``).
    """

    def __init__(
        self,
        app,
        rate: int | None = None,
        burst: int | None = None,
        backend: _RateLimitBackend | None = None,
    ):
        super().__init__(app)
        self.rate = (
            rate
            if rate is not None
            else int(float(os.environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        )
        self.burst = (
            burst
            if burst is not None
            else int(float(os.environ.get("RATE_LIMIT_BURST", str(BURST))))
        )
        if backend is not None:
            self._backend = backend
        else:
            global _DEFAULT_BACKEND
            if _DEFAULT_BACKEND is None:
                _DEFAULT_BACKEND = _build_backend(self.rate, self.burst)
            self._backend = _DEFAULT_BACKEND

    async def dispatch(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        if not self._backend.consume(key, self.rate, self.burst):
            return Response("Rate limit exceeded", status_code=429)
        return await call_next(request)
