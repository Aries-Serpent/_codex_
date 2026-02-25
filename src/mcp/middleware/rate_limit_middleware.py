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

import os
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# In-memory token-bucket per principal (scoped to process).
# WARNING: This is process-local. In multi-replica deployments each worker has
# its own bucket, giving clients N× the configured rate limit where N is the
# number of worker processes. Replace with a Redis-backed implementation for
# production multi-process/multi-replica use.
_BUCKETS: dict[str, dict] = {}
DEFAULT_RATE = 5
BURST = 10


def _get_bucket(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, {"tokens": burst, "last": time.time()})
    return b


def clear_buckets() -> None:
    _BUCKETS.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Very small in-memory rate limiter. Suitable for dev/testing only.

    WARNING: Process-local — not effective in multi-worker deployments.
    Replace ``_BUCKETS`` with a Redis-backed store before production use.

    - principal is taken from request.state.principal.api_key (fall back to 'anonymous')
    - Returns 429 when bucket empty.
    """

    def __init__(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(os.environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(os.environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    async def dispatch(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)
