from __future__ import annotations

import importlib

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def test_create_app_health_and_root() -> None:
    app_module = importlib.import_module("services.msp_gateway.app")
    app = app_module.create_app()
    with TestClient(app) as client:
        health = client.get("/health")
        root = client.get("/")
    assert health.status_code == 200, "status_code is not valid"
    assert health.json()["status"] == "healthy", "Condition must be true"
    assert root.status_code == 200, "status_code is not valid"
    assert root.json()["name"] == "MSP Gateway", "Condition must be true"


def test_create_app_production_requires_non_placeholder_cors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("services.msp_gateway.app")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.delenv("CORS_ALLOW_PLACEHOLDER_OVERRIDE", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "production")
    with pytest.raises(RuntimeError, match="Invalid CORS configuration for production"):
        importlib.reload(module)
    monkeypatch.setenv("ENVIRONMENT", "development")
    importlib.reload(module)


def test_create_app_production_override_allows_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("CORS_ALLOW_PLACEHOLDER_OVERRIDE", "true")
    module = importlib.reload(importlib.import_module("services.msp_gateway.app"))
    app = module.create_app()
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200, "Response must not be empty"


def test_global_exception_handler_uses_offline_detail_toggle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_module = importlib.import_module("services.msp_gateway.app")
    app = app_module.create_app()

    @app.get("/boom")
    async def boom():
        raise RuntimeError("kaboom")

    monkeypatch.setattr(app_module.settings, "api_key_required", False)
    monkeypatch.setattr(app_module.settings, "offline", True)
    with TestClient(app, raise_server_exceptions=False) as client:
        offline_resp = client.get("/boom")
    assert offline_resp.status_code == 500, "status_code is not valid"
    assert offline_resp.json()["details"] == {}, "Condition must be true"

    monkeypatch.setattr(app_module.settings, "offline", False)
    with TestClient(app, raise_server_exceptions=False) as client:
        online_resp = client.get("/boom")
    assert online_resp.status_code == 500, "status_code is not valid"
    assert online_resp.json()["details"]["exception"] == "kaboom", "Condition must be true"
