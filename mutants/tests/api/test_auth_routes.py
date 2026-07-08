"""
Tests for the authentication API routes.

Validates ``POST /auth/register``, ``POST /auth/login``,
``POST /auth/logout``, and ``POST /auth/refresh`` via the FastAPI
test client.
"""

import pytest

pytest.importorskip("fastapi")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.api.auth_routes import create_auth_router
from codex.auth.authenticator import Authenticator
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import (
    UserStore,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def _auth_components():
    """Return a fresh (store, tokens, authenticator) tuple."""
    store = UserStore()
    tokens = TokenManager(secret_key="test-secret-for-routes")
    auth = Authenticator(user_store=store, token_manager=tokens)
    return store, tokens, auth


@pytest.fixture()
def client(_auth_components):
    """FastAPI test client with the auth router mounted."""
    _, _, auth = _auth_components
    app = FastAPI()
    router = create_auth_router(authenticator=auth)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture()
def registered_client(client, _auth_components):
    """Client with one pre-registered user (alice / Str0ngPass!)."""
    _, _, auth = _auth_components
    auth.register("alice", "alice@example.com", "Str0ngPass!")
    return client


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegisterEndpoint:

    def test_register_success(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "username": "bob",
                "email": "bob@example.com",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 201, "status_code is not valid"
        data = resp.json()
        assert data["username"] == "bob", "Data must not be empty"
        assert data["email"] == "bob@example.com", "Data must not be empty"
        assert "user_id" in data, "Data must not be empty"
        assert "user" in data["roles"], "Data must not be empty"

    def test_register_with_custom_roles(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "username": "carol",
                "email": "carol@example.com",
                "password": "Str0ngPass!",
                "roles": ["admin"],
            },
        )
        assert resp.status_code == 201, "status_code is not valid"
        assert "admin" in resp.json()["roles"], "Condition must be true"

    def test_register_duplicate_username_returns_400(self, registered_client):
        resp = registered_client.post(
            "/auth/register",
            json={
                "username": "alice",
                "email": "alice2@example.com",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 400, "status_code is not valid"

    def test_register_weak_password_returns_400(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "username": "dave",
                "email": "dave@example.com",
                "password": "short",
            },
        )
        assert resp.status_code in (400, 422)

    def test_register_missing_fields_returns_422(self, client):
        resp = client.post("/auth/register", json={"username": "eve"})
        assert resp.status_code == 422, "status_code is not valid"

    def test_register_invalid_email_rejected(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "username": "bad_email",
                "email": "not-an-email",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 422, "status_code is not valid"

    def test_register_email_normalised_to_lowercase(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "username": "upper",
                "email": "UPPER@Example.COM",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 201, "status_code is not valid"
        assert resp.json()["email"] == "upper@example.com", "Condition must be true"

    def test_register_password_at_min_boundary(self, client):
        """Exactly 8-character password should be accepted."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "minpw",
                "email": "minpw@example.com",
                "password": "Abcd1!xy",
            },
        )
        assert resp.status_code == 201, f"8-char password should be accepted; got {resp.json()}"

    def test_register_password_at_max_boundary(self, client):
        """128-character password should be accepted."""
        long_pw = "A1!x" * 32  # exactly 128 chars
        resp = client.post(
            "/auth/register",
            json={
                "username": "maxpw",
                "email": "maxpw@example.com",
                "password": long_pw,
            },
        )
        assert resp.status_code == 201, f"128-char password should be accepted; got {resp.json()}"

    def test_register_password_over_max_rejected(self, client):
        """>128-character password should be rejected at validation level."""
        long_pw = "A" * 129
        resp = client.post(
            "/auth/register",
            json={
                "username": "overlimit",
                "email": "overlimit@example.com",
                "password": long_pw,
            },
        )
        assert resp.status_code == 422, "status_code is not valid"

    def test_register_special_chars_in_username(self, client):
        """Special characters in username are handled without crash."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "user<script>alert(1)</script>",
                "email": "xss@example.com",
                "password": "Str0ngPass!",
            },
        )
        # Should either succeed (stored safely) or return 400 — never 500
        assert resp.status_code in (201, 400, 422)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestLoginEndpoint:

    def test_login_success(self, registered_client):
        resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["username"] == "alice", "Data must not be empty"
        assert data["access_token"], "Data must not be empty"
        assert data["refresh_token"], "Data must not be empty"
        assert data["session_token"], "Data must not be empty"
        assert data["session_id"], "Data must not be empty"

    def test_login_by_email(self, registered_client):
        resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice@example.com", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["username"] == "alice", "Condition must be true"

    def test_login_wrong_password_returns_401(self, registered_client):
        resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "WrongPass!!"},
        )
        assert resp.status_code == 401, "status_code is not valid"

    def test_login_unknown_user_returns_401(self, client):
        resp = client.post(
            "/auth/login",
            json={"username_or_email": "nobody", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 401, "status_code is not valid"

    def test_login_error_uses_generic_message(self, registered_client):
        """Error detail should not leak whether user exists."""
        resp_bad_pw = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "WrongPass!!"},
        )
        resp_no_user = registered_client.post(
            "/auth/login",
            json={"username_or_email": "nonexistent", "password": "Str0ngPass!"},
        )
        assert resp_bad_pw.json()["detail"] == resp_no_user.json()["detail"], "Condition must be true"


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestLogoutEndpoint:

    def test_logout_revokes_session(self, registered_client):
        login_resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "Str0ngPass!"},
        )
        session_token = login_resp.json()["session_token"]

        resp = registered_client.post(
            "/auth/logout",
            json={"session_token": session_token},
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["revoked"] is True, "Condition must be true"

    def test_logout_invalid_token(self, client):
        resp = client.post(
            "/auth/logout",
            json={"session_token": "bogus-token"},
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["revoked"] is False, "Condition must be true"

    def test_logout_same_token_twice(self, registered_client):
        """Logging out with the same token twice is handled gracefully."""
        login_resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "Str0ngPass!"},
        )
        session_token = login_resp.json()["session_token"]

        first = registered_client.post("/auth/logout", json={"session_token": session_token})
        assert first.json()["revoked"] is True, "Condition must be true"

        second = registered_client.post("/auth/logout", json={"session_token": session_token})
        # Second call should succeed without error (idempotent)
        assert second.status_code == 200, "status_code is not valid"


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


class TestRefreshEndpoint:

    def test_refresh_success(self, registered_client):
        login_resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "Str0ngPass!"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        resp = registered_client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["access_token"], "Condition must be true"

    def test_refresh_invalid_token_returns_401(self, client):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert resp.status_code == 401, "status_code is not valid"

    def test_refresh_returns_different_access_token(self, registered_client):
        """Two refresh calls should yield distinct access tokens."""
        login_resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "Str0ngPass!"},
        )
        data = login_resp.json()
        first = registered_client.post(
            "/auth/refresh", json={"refresh_token": data["refresh_token"]}
        )
        second = registered_client.post(
            "/auth/refresh", json={"refresh_token": data["refresh_token"]}
        )
        assert first.json()["access_token"] != second.json()["access_token"], "Condition must be true"


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------


class TestRouterFactory:

    def test_default_router_creates_authenticator(self):
        """create_auth_router() with no args produces a working router."""
        app = FastAPI()
        router = create_auth_router()
        app.include_router(router)
        tc = TestClient(app)

        reg = tc.post(
            "/auth/register",
            json={
                "username": "factory_user",
                "email": "factory@test.com",
                "password": "Str0ngPass!",
            },
        )
        assert reg.status_code == 201, "status_code is not valid"

        login = tc.post(
            "/auth/login",
            json={"username_or_email": "factory_user", "password": "Str0ngPass!"},
        )
        assert login.status_code == 200, "status_code is not valid"
        assert login.json()["username"] == "factory_user", "Condition must be true"

    def test_custom_prefix(self):
        """Router respects a custom URL prefix."""
        app = FastAPI()
        router = create_auth_router(prefix="/api/v1/auth")
        app.include_router(router)
        tc = TestClient(app)

        resp = tc.post(
            "/api/v1/auth/register",
            json={
                "username": "prefix_user",
                "email": "prefix@test.com",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 201, "status_code is not valid"

    def test_explicit_secret_key(self):
        """Explicit secret_key is accepted."""
        app = FastAPI()
        router = create_auth_router(secret_key="explicit-test-key")
        app.include_router(router)
        tc = TestClient(app)

        reg = tc.post(
            "/auth/register",
            json={
                "username": "key_user",
                "email": "key@test.com",
                "password": "Str0ngPass!",
            },
        )
        assert reg.status_code == 201, "status_code is not valid"


# ---------------------------------------------------------------------------
# Full round-trip
# ---------------------------------------------------------------------------


class TestFullRoundTrip:

    def test_register_login_refresh_logout(self, client):
        """Complete lifecycle: register → login → refresh → logout."""
        # Register
        reg = client.post(
            "/auth/register",
            json={
                "username": "lifecycle",
                "email": "life@example.com",
                "password": "Str0ngPass!",
            },
        )
        assert reg.status_code == 201, "status_code is not valid"

        # Login
        login = client.post(
            "/auth/login",
            json={"username_or_email": "lifecycle", "password": "Str0ngPass!"},
        )
        assert login.status_code == 200, "status_code is not valid"
        data = login.json()

        # Refresh
        refresh = client.post(
            "/auth/refresh",
            json={"refresh_token": data["refresh_token"]},
        )
        assert refresh.status_code == 200, "status_code is not valid"

        # Logout
        logout = client.post(
            "/auth/logout",
            json={"session_token": data["session_token"]},
        )
        assert logout.status_code == 200, "status_code is not valid"
        assert logout.json()["revoked"] is True, "Condition must be true"
