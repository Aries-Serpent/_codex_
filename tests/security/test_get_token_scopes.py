"""Acceptance tests for CB-001: get_token_scopes JWT validation.

Validates that the FastAPI dependency ``get_token_scopes`` in
``security.decorators`` correctly:
  - Returns scopes from a valid token
  - Raises HTTP 401 on an expired token (with WWW-Authenticate header)
  - Raises HTTP 401 on an invalid/tampered token
  - Raises HTTP 503 when CODEX_AUTH_SECRET is not set
  - Returns an empty list when the token has no scope claim
"""

import os
import time
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.auth.token_manager import TokenManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SECRET = "cb001-test-secret-do-not-use-in-prod"


def _make_app(secret: str = _SECRET) -> "FastAPI":
    """Build a minimal FastAPI app that exposes get_token_scopes as a route."""
    from fastapi import Depends

    from security.decorators import get_token_scopes

    app = FastAPI()

    @app.get("/protected")
    async def protected(scopes: list = Depends(get_token_scopes)):  # type: ignore[type-arg]
        return {"scopes": scopes}

    return app


def _issue_token(scope: str | None = "repo:read", ttl: int = 300) -> str:
    """Issue a signed JWT using TokenManager."""
    tm = TokenManager(secret_key=_SECRET)
    return tm.generate_access_token("test-user", scope=scope)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetTokenScopes:
    """Acceptance tests for get_token_scopes FastAPI dependency (CB-001)."""

    def test_valid_token_returns_scopes(self):
        """A valid JWT with scope claim returns the expected scope list."""
        token = _issue_token(scope="repo:read workflow:write")
        with patch.dict(os.environ, {"CODEX_AUTH_SECRET": _SECRET}):
            app = _make_app()
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "repo:read" in data["scopes"], "Data must not be empty"
        assert "workflow:write" in data["scopes"], "Data must not be empty"

    def test_valid_token_no_scope_returns_empty_list(self):
        """A valid JWT with no scope claim returns an empty list (fail-closed)."""
        token = _issue_token(scope=None)
        with patch.dict(os.environ, {"CODEX_AUTH_SECRET": _SECRET}):
            app = _make_app()
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["scopes"] == [], "Condition must be true"

    def test_invalid_token_returns_401(self):
        """A tampered or invalid Bearer token raises HTTP 401."""
        with patch.dict(os.environ, {"CODEX_AUTH_SECRET": _SECRET}):
            app = _make_app()
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/protected",
                headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
            )
        assert resp.status_code == 401, "status_code is not valid"

    def test_missing_secret_returns_503(self):
        """When CODEX_AUTH_SECRET is not set, raises HTTP 503 (service unavailable)."""
        token = _issue_token()
        env_without_secret = {k: v for k, v in os.environ.items() if k != "CODEX_AUTH_SECRET"}
        with patch.dict(os.environ, env_without_secret, clear=True):
            app = _make_app()
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == 503, "status_code is not valid"

    def test_expired_token_returns_401_with_www_authenticate(self):
        """An expired token raises HTTP 401 with WWW-Authenticate: Bearer header."""
        # Generate a token then manually expire it by patching time
        tm = TokenManager(secret_key=_SECRET)
        token = tm.generate_access_token("test-user", scope="repo:read")

        # Validate then forcibly expire via a patch on time.time so the
        # TokenManager's expiry check fires.
        with patch.dict(os.environ, {"CODEX_AUTH_SECRET": _SECRET}):
            with patch("time.time", return_value=time.time() + 86400 * 365):
                app = _make_app()
                client = TestClient(app, raise_server_exceptions=False)
                resp = client.get(
                    "/protected",
                    headers={"Authorization": f"Bearer {token}"},
                )
        assert resp.status_code == 401, "status_code is not valid"
        assert "Bearer" in resp.headers.get("WWW-Authenticate", "")
