from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytest.importorskip("fastapi")
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from services.msp_gateway.middleware.rate_limit import (
    RateLimitMiddleware,
    TokenBucket,
    rate_limiter,
)


class _InjectTenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.tenant = {
            "tenant_id": "tenant-x",
            "quota": {"requests_per_minute": 5, "tokens_per_minute": 30},
        }
        return await call_next(request)


def _app_for_infer() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(_InjectTenantMiddleware)

    @app.post("/v1/infer")
    async def infer(request: Request):
        payload = await request.json()
        return JSONResponse(
            {"ok": True, "max_tokens": payload.get("max_tokens", 0), "tokens_used": 5}
        )

    return app


def test_dispatch_returns_429_when_request_limit_reached(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app_for_infer()
    monkeypatch.setattr(
        rate_limiter,
        "check_request_limit",
        lambda tenant_id, quota=None: False,  # noqa: ARG005
    )
    with TestClient(app) as client:
        response = client.post("/v1/infer", json={"max_tokens": 3})
    assert response.status_code == 429, "Response must not be empty"
    assert "Request rate limit exceeded" in response.json()["detail"], "Response must not be empty"


def test_dispatch_returns_429_when_preflight_token_quota_is_exhausted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app_for_infer()
    monkeypatch.setattr(
        rate_limiter, "check_request_limit", lambda tenant_id, quota=None: True
    )  # noqa: ARG005

    depleted = TokenBucket(capacity=10, tokens=0.0, last_refill=0.0, refill_rate=0.0)
    monkeypatch.setattr(rate_limiter, "_get_or_create_bucket", lambda *args, **kwargs: depleted)

    with TestClient(app) as client:
        response = client.post("/v1/infer", json={"max_tokens": 9})
    assert response.status_code == 429, "Response must not be empty"
    assert "Token quota exceeded" in response.json()["detail"], "Response must not be empty"


def test_dispatch_reinserts_request_body_and_handles_accounting_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app_for_infer()
    monkeypatch.setattr(
        rate_limiter, "check_request_limit", lambda tenant_id, quota=None: True
    )  # noqa: ARG005

    bucket = MagicMock()
    bucket.available_tokens.return_value = 100.0
    bucket.consume.return_value = True
    monkeypatch.setattr(rate_limiter, "_get_or_create_bucket", lambda *args, **kwargs: bucket)

    with TestClient(app) as client:
        response = client.post("/v1/infer", json={"max_tokens": 7})

    assert response.status_code == 200, "Response must not be empty"
    assert response.json()["max_tokens"] == 7, "Response must not be empty"
    # Current middleware gracefully handles body-iterator accounting errors.
    bucket.consume.assert_not_called()
