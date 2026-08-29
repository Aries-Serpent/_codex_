"""
Integration tests for MFA round-trip and token expiry flows.

Covers:
- MFA enroll → login with TOTP → verify mfa_verified=True (API)
- MFA enroll → login without TOTP → 403 (API)
- MFA wrong code → 403 (API)
- Token expiry → refresh fails with 401 (API)
- Access token expiry → must re-authenticate (API)
"""

from __future__ import annotations  # pragma: allowlist secret

import time
from unittest.mock import patch

import pytest

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
pytest.importorskip("fastapi")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.api.auth_routes import create_auth_router
from codex.auth.authenticator import Authenticator
from codex.auth.mfa_provider import MFAProvider
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mfa_auth_components():
    """Return (store, tokens, mfa, authenticator) with MFA enabled."""
    store = UserStore()
    tokens = TokenManager(secret_key="test-secret-for-mfa-routes")
    mfa = MFAProvider()
    auth = Authenticator(user_store=store, token_manager=tokens, mfa_provider=mfa)
    return store, tokens, mfa, auth


@pytest.fixture()
def mfa_client(mfa_auth_components):
    """FastAPI test client with MFA-enabled auth router."""
    _, _, _, auth = mfa_auth_components
    app = FastAPI()
    router = create_auth_router(authenticator=auth)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture()
def registered_mfa_user(mfa_client, mfa_auth_components):
    """Register 'alice' and return (client, mfa_provider, user)."""
    store, _tokens, mfa, _auth = mfa_auth_components
    # Register via API
    resp = mfa_client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Str0ngPass!",  # pragma: allowlist secret
        },
    )
    assert resp.status_code == 201, "status_code is not valid"
    user = store.find_by_username("alice")
    return mfa_client, mfa, user


# ---------------------------------------------------------------------------
# MFA round-trip tests
# ---------------------------------------------------------------------------


class TestMFARoundTrip:

    def test_enroll_login_with_totp_verified(self, registered_mfa_user):
        """Full MFA flow: enroll → login with correct TOTP → mfa_verified=True."""
        client, mfa, user = registered_mfa_user

        # Step 1: Enroll MFA (generate TOTP secret)
        secret = mfa.generate_totp_secret(user.user_id, issuer="Codex-Test")
        assert mfa.is_mfa_enabled(user.user_id) is True, "Condition must be true"

        # Step 2: Generate a valid TOTP code
        totp_code = mfa.generate_totp(secret.secret)

        # Step 3: Login with the TOTP code
        resp = client.post(
            "/auth/login",
            json={
                "username_or_email": "alice",
                "password": "Str0ngPass!",  # pragma: allowlist secret
                "totp_code": totp_code,
            },
        )
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["mfa_verified"] is True, "Data must not be empty"
        assert data["username"] == "alice", "Data must not be empty"
        assert data["access_token"], "Data must not be empty"
        assert data["session_id"], "Data must not be empty"

    def test_mfa_enrolled_login_without_totp_returns_403(self, registered_mfa_user):
        """When MFA is enrolled, login without TOTP code returns 403."""
        client, mfa, user = registered_mfa_user

        # Enroll MFA
        mfa.generate_totp_secret(user.user_id)

        # Login without TOTP
        resp = client.post(
            "/auth/login",
            json={
                "username_or_email": "alice",
                "password": "Str0ngPass!",  # pragma: allowlist secret
            },
        )
        assert resp.status_code == 403, "status_code is not valid"
        assert "MFA" in resp.json()["detail"], "Condition must be true"

    def test_mfa_wrong_code_returns_403(self, registered_mfa_user):
        """Login with wrong TOTP code returns 403."""
        client, mfa, user = registered_mfa_user

        # Enroll MFA
        mfa.generate_totp_secret(user.user_id)

        # Login with wrong code
        resp = client.post(
            "/auth/login",
            json={
                "username_or_email": "alice",
                "password": "Str0ngPass!",  # pragma: allowlist secret
                "totp_code": "000000",
            },
        )
        assert resp.status_code == 403, "status_code is not valid"
        assert "MFA" in resp.json()["detail"], "Condition must be true"

    def test_login_without_mfa_enrolled_succeeds(self, registered_mfa_user):
        """When MFA is NOT enrolled, login succeeds with mfa_verified=False."""
        client, _mfa, _user = registered_mfa_user

        # Don't enroll MFA — just login normally
        resp = client.post(
            "/auth/login",
            json={
                "username_or_email": "alice",
                "password": "Str0ngPass!",  # pragma: allowlist secret
            },
        )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["mfa_verified"] is False, "Condition must be true"

    def test_mfa_full_lifecycle(self, registered_mfa_user):
        """Enroll → login with TOTP → refresh → logout → verify revoked."""
        client, mfa, user = registered_mfa_user

        # Enroll
        secret = mfa.generate_totp_secret(user.user_id)
        totp_code = mfa.generate_totp(secret.secret)

        # Login with MFA
        login_resp = client.post(
            "/auth/login",
            json={
                "username_or_email": "alice",
                "password": "Str0ngPass!",  # pragma: allowlist secret
                "totp_code": totp_code,
            },
        )
        assert login_resp.status_code == 200, "status_code is not valid"
        data = login_resp.json()
        assert data["mfa_verified"] is True, "Data must not be empty"

        # Refresh
        refresh_resp = client.post(
            "/auth/refresh",
            json={"refresh_token": data["refresh_token"]},
        )
        assert refresh_resp.status_code == 200, "status_code is not valid"
        assert refresh_resp.json()["access_token"], "Condition must be true"

        # Logout
        logout_resp = client.post(
            "/auth/logout",
            json={"session_token": data["session_token"]},
        )
        assert logout_resp.status_code == 200, "status_code is not valid"
        assert logout_resp.json()["revoked"] is True, "Condition must be true"


# ---------------------------------------------------------------------------
# Token expiry tests
# ---------------------------------------------------------------------------


class TestTokenExpiry:

    def test_expired_access_token_rejected_by_validate(self):
        """An expired access token should fail validation."""
        tokens = TokenManager(secret_key="test-expiry-key")

        # Generate a token and then expire it by monkey-patching time
        user_id = "test-user"
        access = tokens.generate_access_token(user_id, scope="user")

        # Validate should work now
        claims = tokens.validate_token(access)
        assert claims.sub == user_id, "sub is not valid"

        # Fast-forward time past expiry (ACCESS_TOKEN_EXPIRY = 900s)
        with patch("time.time", return_value=time.time() + 1000):
            with pytest.raises(ValueError, match="expired"):
                tokens.validate_token(access)

    def test_expired_refresh_token_rejected(self):
        """An expired refresh token should fail refresh."""
        store = UserStore()
        tokens = TokenManager(secret_key="test-expiry-key")
        auth = Authenticator(user_store=store, token_manager=tokens)

        auth.register("bob", "bob@test.com", "Str0ngPass!")
        result = auth.login("bob", "Str0ngPass!")

        # Refresh should work now
        new_access = auth.refresh(result.refresh_token)
        assert new_access, "new_access is not valid"

        # Fast-forward past refresh token expiry (REFRESH_TOKEN_EXPIRY = 604800s)
        with patch("time.time", return_value=time.time() + 700_000):
            with pytest.raises(ValueError, match="expired"):
                auth.refresh(result.refresh_token)

    def test_expired_refresh_returns_401_via_api(self):
        """API returns 401 when refresh token has expired."""
        store = UserStore()
        tokens = TokenManager(secret_key="test-api-expiry")
        auth = Authenticator(user_store=store, token_manager=tokens)

        app = FastAPI()
        app.include_router(create_auth_router(authenticator=auth))
        client = TestClient(app)

        # Register + login
        client.post(
            "/auth/register",
            json={
                "username": "carol",
                "email": "carol@test.com",
                "password": "Str0ngPass!",  # pragma: allowlist secret
            },
        )
        login = client.post(
            "/auth/login",
            json={
                "username_or_email": "carol",
                "password": "Str0ngPass!",
            },  # pragma: allowlist secret
        )
        assert login.status_code == 200, "status_code is not valid"
        refresh_token = login.json()["refresh_token"]

        # Fast-forward past expiry
        with patch("time.time", return_value=time.time() + 700_000):
            resp = client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token},
            )
            assert resp.status_code == 401, "status_code is not valid"

    def test_session_token_expiry(self):
        """An expired session token should fail validation."""
        tokens = TokenManager(secret_key="test-session-expiry")
        session_token, _session_id = tokens.generate_session_token(
            user_id="test-user", ip_address="127.0.0.1"
        )

        # Valid now
        claims = tokens.validate_token(session_token)
        assert claims.sub == "test-user", "sub is not valid"

        # Expired (SESSION_TOKEN_EXPIRY = 2592000s)
        with patch("time.time", return_value=time.time() + 3_000_000):
            with pytest.raises(ValueError, match="expired"):
                tokens.validate_token(session_token)
