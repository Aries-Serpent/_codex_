"""Tests for mcp.server.middleware.auth — APIKeyAuthMiddleware."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from mcp.server.middleware.auth import DEV_KEYS, APIKeyAuthMiddleware


def _build_app(dev_keys: dict | None = None) -> tuple[FastAPI, TestClient]:
    """Create a minimal FastAPI app with auth middleware and an echo endpoint."""
    app = FastAPI()
    app.add_middleware(APIKeyAuthMiddleware)

    @app.get("/whoami")
    async def whoami(request: Request):
        principal = getattr(request.state, "principal", None)
        return {"principal": principal}

    client = TestClient(app, raise_server_exceptions=False)
    return app, client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_valid_key() -> str:
    """Return the first registered dev key."""
    return next(iter(DEV_KEYS))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_no_key_allows_anonymous_access():
    _, client = _build_app()
    resp = client.get("/whoami")
    assert resp.status_code == 200
    data = resp.json()
    assert data["principal"]["tenant"] == "anonymous"
    assert data["principal"]["scopes"] == []


def test_valid_bearer_token_sets_principal():
    key = _get_valid_key()
    _, client = _build_app()
    resp = client.get("/whoami", headers={"Authorization": "Bearer " + key})
    assert resp.status_code == 200
    data = resp.json()
    assert data["principal"]["tenant"] == DEV_KEYS[key]["tenant"]
    assert "read" in data["principal"]["scopes"]


def test_valid_x_api_key_header_sets_principal():
    key = _get_valid_key()
    _, client = _build_app()
    resp = client.get("/whoami", headers={"X-API-Key": key})
    assert resp.status_code == 200
    data = resp.json()
    assert data["principal"]["tenant"] == DEV_KEYS[key]["tenant"]


def test_unknown_key_returns_401():
    _, client = _build_app()
    resp = client.get("/whoami", headers={"X-API-Key": "totally-invalid-key"})
    assert resp.status_code == 401


def test_unknown_bearer_returns_401():
    _, client = _build_app()
    prefix = "Bearer "
    resp = client.get("/whoami", headers={"Authorization": prefix + "totally-unknown-key-xyz"})
    assert resp.status_code == 401


def test_bearer_prefix_case_insensitive():
    """Authorization header parsing is case-insensitive for 'bearer ' prefix."""
    key = _get_valid_key()
    _, client = _build_app()
    resp = client.get("/whoami", headers={"Authorization": f"BEARER {key}"})
    assert resp.status_code == 200


def test_dev_keys_contain_scopes():
    """Ensure all DEV_KEYS entries have a 'scopes' list."""
    for _key_val, info in DEV_KEYS.items():
        assert "scopes" in info
        assert isinstance(info["scopes"], list)


def test_dev_keys_contain_tenant():
    for _key, info in DEV_KEYS.items():
        assert "tenant" in info
        assert isinstance(info["tenant"], str)


def test_anonymous_principal_has_empty_scopes():
    _, client = _build_app()
    resp = client.get("/whoami")
    assert resp.status_code == 200
    principal = resp.json()["principal"]
    assert principal["scopes"] == []


def test_anonymous_principal_tenant_is_anonymous():
    _, client = _build_app()
    resp = client.get("/whoami")
    assert resp.json()["principal"]["tenant"] == "anonymous"
