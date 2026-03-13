"""
Tests for the authentication API routes.

Validates ``POST /auth/register``, ``POST /auth/login``,
``POST /auth/logout``, and ``POST /auth/refresh`` via the FastAPI
test client.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.codex.api.auth_routes import create_auth_router
from src.codex.auth.authenticator import Authenticator
from src.codex.auth.token_manager import TokenManager
from src.codex.auth.user_store import UserStore


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
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "bob"
        assert data["email"] == "bob@example.com"
        assert "user_id" in data
        assert "user" in data["roles"]

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
        assert resp.status_code == 201
        assert "admin" in resp.json()["roles"]

    def test_register_duplicate_username_returns_400(self, registered_client):
        resp = registered_client.post(
            "/auth/register",
            json={
                "username": "alice",
                "email": "alice2@example.com",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 400

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
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestLoginEndpoint:

    def test_login_success(self, registered_client):
        resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "alice"
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["session_token"]
        assert data["session_id"]

    def test_login_by_email(self, registered_client):
        resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice@example.com", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 200
        assert resp.json()["username"] == "alice"

    def test_login_wrong_password_returns_401(self, registered_client):
        resp = registered_client.post(
            "/auth/login",
            json={"username_or_email": "alice", "password": "WrongPass!!"},
        )
        assert resp.status_code == 401

    def test_login_unknown_user_returns_401(self, client):
        resp = client.post(
            "/auth/login",
            json={"username_or_email": "nobody", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 401


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
        assert resp.status_code == 200
        assert resp.json()["revoked"] is True

    def test_logout_invalid_token(self, client):
        resp = client.post(
            "/auth/logout",
            json={"session_token": "bogus-token"},
        )
        assert resp.status_code == 200
        assert resp.json()["revoked"] is False


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
        assert resp.status_code == 200
        assert resp.json()["access_token"]

    def test_refresh_invalid_token_returns_401(self, client):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert resp.status_code == 401


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

        # register → login round-trip with the default in-memory store
        reg = tc.post(
            "/auth/register",
            json={
                "username": "factory_user",
                "email": "factory@test.com",
                "password": "Str0ngPass!",
            },
        )
        assert reg.status_code == 201

        login = tc.post(
            "/auth/login",
            json={"username_or_email": "factory_user", "password": "Str0ngPass!"},
        )
        assert login.status_code == 200
        assert login.json()["username"] == "factory_user"

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
        assert resp.status_code == 201
