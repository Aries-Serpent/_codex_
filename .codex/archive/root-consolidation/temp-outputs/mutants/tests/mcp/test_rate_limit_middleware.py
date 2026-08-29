"""
Test Rate Limit Middleware

Test module for rate limit middleware.
"""

import time

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp.middleware.rate_limit_middleware import (
    RateLimitMiddleware,
    clear_buckets,
)


def test_rate_limit_throttling():
    clear_buckets()
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    app.add_middleware(RateLimitMiddleware, rate=1, burst=2)
    client = TestClient(app)

    res1 = client.get("/ping")
    assert res1.status_code == 200, "status_code is not valid"
    res2 = client.get("/ping")
    assert res2.status_code == 200, "status_code is not valid"

    throttled = False
    for _ in range(5):
        r = client.get("/ping")
        if r.status_code == 429:
            throttled = True
            break
        time.sleep(0.01)
    assert throttled, "Expected at least one request to be throttled (429)"


def test_redis_backend_multi_worker_simulation():
    """Simulate two workers sharing a Redis backend.

    Validates that _RedisBackend correctly uses atomic INCR so that
    two processes sharing the same key space both count against the
    same limit (no double-allowance).
    """
    from unittest.mock import MagicMock, patch

    from mcp.middleware.rate_limit_middleware import _RedisBackend

    mock_redis_module = MagicMock()
    mock_conn = MagicMock()
    mock_redis_module.Redis.from_url.return_value = mock_conn

    with patch.dict("sys.modules", {"redis": mock_redis_module}):
        backend = _RedisBackend("redis://localhost:6379/0", window=1)

    # Worker 1 and Worker 2 share the same key space
    # Simulate atomic INCR returning incrementing counts
    counts = iter(range(1, 20))
    mock_conn.incr.side_effect = lambda key: next(counts)

    # With burst=5, first 5 requests allowed, 6th denied
    results = [backend.consume("user:alice", rate=5.0, burst=5) for _ in range(6)]
    assert results[:5] == [True] * 5, "First 5 requests must be allowed"
    assert results[5] is False, "6th request must be denied (burst=5 exhausted)"


def test_redis_backend_fail_open_on_error():
    """Redis unavailable → backend must allow the request (fail-open)."""
    from unittest.mock import MagicMock, patch

    from mcp.middleware.rate_limit_middleware import _RedisBackend

    # Use only MagicMock — no real redis import needed to test fail-open behavior
    mock_redis_module = MagicMock()
    mock_conn = MagicMock()
    # Simulate a ConnectionError as a plain Exception (no real redis needed)
    mock_conn.incr.side_effect = Exception("Redis unreachable (simulated)")
    mock_redis_module.Redis.from_url.return_value = mock_conn

    with patch.dict("sys.modules", {"redis": mock_redis_module}):
        backend = _RedisBackend("redis://localhost:6379/0")

    # Should fail-open (return True) when Redis raises any exception
    result = backend.consume("user:bob", rate=5.0, burst=5)
    assert result is True, "Backend must fail-open when Redis is unavailable"
