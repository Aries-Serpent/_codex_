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

from src.mcp.middleware.rate_limit_middleware import RateLimitMiddleware, clear_buckets


def test_rate_limit_throttling():
    clear_buckets()
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    app.add_middleware(RateLimitMiddleware, rate=1, burst=2)
    client = TestClient(app)

    res1 = client.get("/ping")
    assert res1.status_code == 200
    res2 = client.get("/ping")
    assert res2.status_code == 200

    throttled = False
    for _ in range(5):
        r = client.get("/ping")
        if r.status_code == 429:
            throttled = True
            break
        time.sleep(0.01)
    assert throttled, "Expected at least one request to be throttled (429)"
