"""Deterministic token bucket rate limiter for MCP tests."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class _Bucket:
    tokens: float
    updated_at: float


class MCPRateLimiter:
    """Simple token-bucket rate limiter keyed by principal+tool."""

    def __init__(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def _key(self, principal_id: str | None, tool_name: str | None) -> tuple[str, str]:
        return (principal_id or "*", tool_name or "*")

    def _refill(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def allow(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def reset(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(key, None)


__all__ = ["MCPRateLimiter"]
