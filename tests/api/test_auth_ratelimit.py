"""
Tests for auth endpoint rate limiting and CSRF token endpoint.

Validates:
- Login endpoint rate limiting (429 after burst)
- Register endpoint rate limiting
- CSRF token endpoint returns a token
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.api.auth_routes import create_auth_router
from codex.auth.authenticator import Authenticator
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore


@pytest.fixture()
def limited_client():
    """Client with very low rate limits for testing."""
    store = UserStore()
    tokens = TokenManager(secret_key="test-ratelimit")
    auth = Authenticator(user_store=store, token_manager=tokens)

    app = FastAPI()
    router = create_auth_router(
        authenticator=auth,
        login_rate_limit=3,
        register_rate_limit=2,
        default_rate_limit=5,
    )
    app.include_router(router)
    return TestClient(app)


class TestLoginRateLimit:

    def test_login_rate_limited_after_burst(self, limited_client):
        """Login endpoint returns 429 after exceeding rate limit."""
        client = limited_client

        # Register a user first
        client.post(
            "/auth/register",
            json={
                "username": "rateuser",
                "email": "rate@example.com",
                "password": "Str0ngPass!",
            },
        )

        # Exhaust the login rate limit (3 per minute)
        for _ in range(3):
            client.post(
                "/auth/login",
                json={"username_or_email": "rateuser", "password": "Str0ngPass!"},
            )

        # Next request should be rate-limited
        resp = client.post(
            "/auth/login",
            json={"username_or_email": "rateuser", "password": "Str0ngPass!"},
        )
        assert resp.status_code == 429, "status_code is not valid"
        assert "Rate limit" in resp.json()["detail"], "Condition must be true"


class TestRegisterRateLimit:

    def test_register_rate_limited_after_burst(self, limited_client):
        """Register endpoint returns 429 after exceeding rate limit."""
        client = limited_client

        # Exhaust the register rate limit (2 per minute)
        for i in range(2):
            client.post(
                "/auth/register",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                    "password": "Str0ngPass!",
                },
            )

        # Next request should be rate-limited
        resp = client.post(
            "/auth/register",
            json={
                "username": "blocked",
                "email": "blocked@example.com",
                "password": "Str0ngPass!",
            },
        )
        assert resp.status_code == 429, "status_code is not valid"


class TestCSRFTokenEndpoint:

    def test_csrf_token_returns_token(self):
        """GET /auth/csrf-token should return a CSRF token."""
        app = FastAPI()
        router = create_auth_router()
        app.include_router(router)
        client = TestClient(app)

        resp = client.get("/auth/csrf-token")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "csrf_token" in data, "Data must not be empty"
        assert len(data["csrf_token"]) > 10, "Collection must not be empty"

    def test_csrf_tokens_are_unique(self):
        """Each call to csrf-token should return a different token."""
        app = FastAPI()
        router = create_auth_router()
        app.include_router(router)
        client = TestClient(app)

        t1 = client.get("/auth/csrf-token").json()["csrf_token"]
        t2 = client.get("/auth/csrf-token").json()["csrf_token"]
        assert t1 != t2, "t1 is not valid"
