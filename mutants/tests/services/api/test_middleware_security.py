"""Middleware and rate limiting behaviours for :mod:`services.api.main`."""

from __future__ import annotations

import importlib

import pytest

fastapi = pytest.importorskip("fastapi")  # ensure FastAPI is available
from fastapi.testclient import TestClient


def test_api_key_required(monkeypatch: pytest.MonkeyPatch) -> None:
    # Disable JWT auth middleware so this test exercises only the API_KEY
    # middleware. With JWT auth enabled, the JWT layer intercepts before the
    # API_KEY check, causing the authorized request to return 401 instead of 200.
    monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    monkeypatch.setenv("API_KEY", "secret-token")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)

    unauthorized = client.get("/status")
    assert unauthorized.status_code == 401, "status_code is not valid"
    assert unauthorized.json()["detail"] == "unauthorized", "unauth is not valid"

    authorized = client.get("/status", headers={"x-api-key": "secret-token"})
    assert authorized.status_code == 200, "status_code is not valid"
    assert authorized.json()["ok"] is True, "auth is not valid"


def test_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    # Disable JWT auth middleware so rate-limit logic is reached.
    monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    monkeypatch.setenv("API_RATE_LIMIT", "2")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)

    first = client.get("/status")
    second = client.get("/status")
    third = client.get("/status")

    assert first.status_code == 200, "status_code is not valid"
    assert second.status_code == 200, "status_code is not valid"
    assert third.status_code == 429, "status_code is not valid"
    assert third.json()["detail"] == "rate limit exceeded", "Condition must be true"
