"""Middleware and rate limiting behaviours for :mod:`services.api.main`."""

from __future__ import annotations

import importlib

import pytest

fastapi = pytest.importorskip("fastapi")  # noqa: F401  # ensure FastAPI is available
from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def test_api_key_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_KEY", "secret-token")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)

    with pytest.raises(HTTPException) as excinfo:
        client.get("/status")
    assert excinfo.value.status_code == 401

    authorized = client.get("/status", headers={"x-api-key": "secret-token"})
    assert authorized.status_code == 200
    assert authorized.json()["ok"] is True


def test_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_RATE_LIMIT", "2")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)

    first = client.get("/status")
    second = client.get("/status")
    third = client.get("/status")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["detail"] == "rate limit exceeded"
