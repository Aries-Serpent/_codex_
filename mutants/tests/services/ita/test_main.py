from __future__ import annotations

import importlib

import pytest

pytest.importorskip("fastapi")
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient


@pytest.fixture()
def main_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("ITA_API_KEY", "ita-test-key")
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "ita-test-pepper")
    return importlib.reload(importlib.import_module("services.ita.app.main"))


def test_get_request_id_and_authenticate_request(main_module) -> None:
    scope = {"type": "http", "headers": [], "method": "GET", "path": "/"}
    request = Request(scope)
    assert main_module._get_request_id(request) == "unknown", "Condition must be true"

    with pytest.raises(HTTPException) as exc:
        main_module._authenticate_request(None, "key")
    assert exc.value.status_code == 400, "Value must be initialized"


def test_get_request_context_missing_raises(main_module) -> None:
    request = Request({"type": "http", "headers": [], "method": "GET", "path": "/"})
    with pytest.raises(HTTPException) as exc:
        import asyncio

        asyncio.run(main_module.get_request_context(request))
    assert exc.value.status_code == 401, "Value must be initialized"


def test_main_endpoints_with_valid_headers(main_module) -> None:
    with TestClient(main_module.app) as client:
        headers = {"X-API-Key": "ita-test-key", "X-Request-Id": "req-123"}
        health = client.get("/healthz", headers=headers)
        kb = client.post("/kb/search", headers=headers, json={"query": "copilot", "top_k": 1})
        pr_guard = client.post(
            "/git/create-pr?dry_run=false",
            headers=headers,
            json={
                "repo": "octo/repo",
                "title": "t",
                "body": "b",
                "base": "main",
                "head": "branch",
            },
        )

    assert health.status_code == 200, "status_code is not valid"
    assert health.headers["X-Request-Id"] == "req-123", "Condition must be true"
    assert kb.status_code == 200, "status_code is not valid"
    assert pr_guard.status_code == 412, "status_code is not valid"


def test_main_middleware_returns_500_for_unhandled_exception(
    main_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        main_module,
        "_authenticate_request",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with TestClient(main_module.app) as client:
        response = client.get(
            "/healthz", headers={"X-API-Key": "ita-test-key", "X-Request-Id": "req-1"}
        )
    assert response.status_code == 500, "Response must not be empty"
    assert response.json()["detail"] == "Internal server error", "Response must not be empty"
