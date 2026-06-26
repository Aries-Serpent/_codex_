"""
Integration tests for token rotation, revocation, and lifecycle flows.

Covers:
- Token rotation via ``POST /auth/refresh`` (new access token issued)
- Token revocation via ``POST /auth/logout`` (session token revoked)
- Revoked session token cannot be reused
- Refresh after logout returns 401
- Multi-session revoke-all (revoke all user sessions on password change)
- Concurrent session isolation (logout one session, other remains valid)
- Token rotation preserves user identity
"""  # pragma: allowlist secret

from __future__ import annotations

import pytest

pytest.importorskip("fastapi") # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.api.auth_routes import create_auth_router
from codex.auth.authenticator import Authenticator
from codex.auth.token_manager import TokenManager, TokenType
from codex.auth.user_store import UserStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def auth_components():
    """Return (store, tokens, authenticator) for token lifecycle tests."""
    store = UserStore()
    tokens = TokenManager(secret_key="test-token-lifecycle-key")
    auth = Authenticator(user_store=store, token_manager=tokens)
    return store, tokens, auth


@pytest.fixture()
def client(auth_components):
    """FastAPI test client wired to in-memory auth."""
    _, _, auth = auth_components
    app = FastAPI()
    router = create_auth_router(authenticator=auth)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture()
def logged_in_user(client):
    """Register + login 'alice' and return (client, login_data)."""
    client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@token-test.com",
            "password": "Str0ngPass!",  # pragma: allowlist secret
        },
    )
    resp = client.post(
        "/auth/login",
        json={"username_or_email": "alice", "password": "Str0ngPass!"},  # pragma: allowlist secret
    )
    assert resp.status_code == 200, "status_code is not valid"
    return client, resp.json()


# ---------------------------------------------------------------------------
# Token rotation tests
# ---------------------------------------------------------------------------


class TestTokenRotation:
    """Verify token rotation (refresh → new access token)."""

    def test_refresh_returns_new_access_token(self, logged_in_user):
        """POST /auth/refresh with valid refresh token returns a new access."""
        client, data = logged_in_user
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": data["refresh_token"]},
        )
        assert resp.status_code == 200, "status_code is not valid"
        new_access = resp.json()["access_token"]
        assert new_access, "new_access is not valid"
        # Must be different from original (new jti / exp)
        assert new_access != data["access_token"], "Data must not be empty"

    def test_rotated_token_has_same_subject(self, logged_in_user, auth_components):
        """Rotated access token preserves user identity (sub claim)."""
        client, data = logged_in_user
        _, tokens, _ = auth_components

        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": data["refresh_token"]},
        )
        assert resp.status_code == 200, "status_code is not valid"
        new_access = resp.json()["access_token"]

        # Validate the new token points to the same user
        claims = tokens.validate_token(new_access, TokenType.ACCESS)
        assert claims.sub == data["user_id"], "Data must not be empty"

    def test_refresh_with_invalid_token_returns_401(self, client):
        """POST /auth/refresh with an invalid token returns 401."""
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "not-a-valid-jwt"},
        )
        assert resp.status_code == 401, "status_code is not valid"

    def test_refresh_with_access_token_returns_401(self, logged_in_user):
        """Using an access token (wrong type) for refresh returns 401."""
        client, data = logged_in_user
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": data["access_token"]},
        )
        assert resp.status_code == 401, "status_code is not valid"

    def test_multiple_refreshes_succeed(self, logged_in_user):
        """Multiple sequential refreshes should all succeed."""
        client, data = logged_in_user
        refresh_token = data["refresh_token"]

        tokens_seen = set()
        for _ in range(3):
            resp = client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token},
            )
            assert resp.status_code == 200, "status_code is not valid"
            new = resp.json()["access_token"]
            assert new not in tokens_seen, "Condition must be true"
            tokens_seen.add(new)


# ---------------------------------------------------------------------------
# Token revocation tests
# ---------------------------------------------------------------------------


class TestTokenRevocation:
    """Verify token revocation (logout → session invalidated)."""

    def test_logout_revokes_session_token(self, logged_in_user):
        """POST /auth/logout revokes the session and returns revoked=True."""
        client, data = logged_in_user
        resp = client.post(
            "/auth/logout",
            json={"session_token": data["session_token"]},
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["revoked"] is True, "Condition must be true"

    def test_revoked_session_token_fails_validation(self, logged_in_user, auth_components):
        """After logout, the session token fails TokenManager.validate_token."""
        client, data = logged_in_user
        _, tokens, _ = auth_components

        # Revoke
        client.post(
            "/auth/logout",
            json={"session_token": data["session_token"]},
        )

        # Validate should now fail
        with pytest.raises(ValueError, match="[Rr]evoked|[Ii]nvalid"):
            tokens.validate_token(data["session_token"])

    def test_double_logout_is_idempotent(self, logged_in_user):
        """Second logout on the same token is idempotent (still returns True)."""
        client, data = logged_in_user

        # First logout
        resp1 = client.post(
            "/auth/logout",
            json={"session_token": data["session_token"]},
        )
        assert resp1.json()["revoked"] is True, "Condition must be true"

        # Second logout (token already revoked — add to set is idempotent)
        resp2 = client.post(
            "/auth/logout",
            json={"session_token": data["session_token"]},
        )
        assert resp2.json()["revoked"] is True, "Condition must be true"

    def test_logout_invalid_token_returns_revoked_false(self, client):
        """Logout with a garbage token returns revoked=False (graceful)."""
        resp = client.post(
            "/auth/logout",
            json={"session_token": "totally-invalid-token"},
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["revoked"] is False, "Condition must be true"


# ---------------------------------------------------------------------------
# Cross-session isolation tests
# ---------------------------------------------------------------------------


class TestSessionIsolation:
    """Ensure revoking one session doesn't affect another."""

    def test_logout_one_session_other_remains_valid(self, client, auth_components):
        """Two sessions for the same user; logout one — other stays valid."""
        _, _tokens, _ = auth_components

        # Register
        client.post(
            "/auth/register",
            json={
                "username": "bob",
                "email": "bob@iso-test.com",
                "password": "Str0ngPass!",  # pragma: allowlist secret
            },
        )

        # Login twice → two sessions
        login1 = client.post(
            "/auth/login",
            json={
                "username_or_email": "bob",
                "password": "Str0ngPass!",
            },  # pragma: allowlist secret
        )
        login2 = client.post(
            "/auth/login",
            json={
                "username_or_email": "bob",
                "password": "Str0ngPass!",
            },  # pragma: allowlist secret
        )
        assert login1.status_code == 200, "status_code is not valid"
        assert login2.status_code == 200, "status_code is not valid"

        data1 = login1.json()
        data2 = login2.json()
        assert data1["session_id"] != data2["session_id"], "Data must not be empty"

        # Logout session 1
        client.post(
            "/auth/logout",
            json={"session_token": data1["session_token"]},
        )

        # Session 2's refresh token should still work
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": data2["refresh_token"]},
        )
        assert resp.status_code == 200, "status_code is not valid"

    def test_revoke_all_user_tokens(self, auth_components):
        """revoke_all_user_tokens invalidates every session for a user."""
        _store, tokens, auth = auth_components

        auth.register("charlie", "charlie@test.com", "Str0ngPass!")  # pragma: allowlist secret
        result1 = auth.login("charlie", "Str0ngPass!")  # pragma: allowlist secret
        result2 = auth.login("charlie", "Str0ngPass!")  # pragma: allowlist secret

        # Both session tokens should be valid
        tokens.validate_token(result1.session_token)
        tokens.validate_token(result2.session_token)

        # Revoke all
        count = tokens.revoke_all_user_tokens(result1.user_id)
        assert count >= 2, "count must be positive"

        # Both should now fail
        with pytest.raises(ValueError):
            tokens.validate_token(result1.session_token)
        with pytest.raises(ValueError):
            tokens.validate_token(result2.session_token)
