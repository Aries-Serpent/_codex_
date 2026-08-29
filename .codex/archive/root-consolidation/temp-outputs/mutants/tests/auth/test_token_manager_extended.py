"""
Test Codex Auth Module - Token Manager Extended Tests

Comprehensive unit tests for production authentication functionality.
Part of IP-004: Production Authentication Implementation.
"""

from __future__ import annotations

import time
import warnings

import pytest


class TestTokenManagerInitialization:
    """Tests for TokenManager initialization."""

    def test_init_with_secret_key(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret-key-12345")
        assert tm is not None, "tm must be initialized"

    def test_init_without_secret_key_warns(self) -> None:
        from codex.auth.token_manager import TokenManager

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            TokenManager(secret_key=None)
            assert len(w) == 1, "W must not be empty"
            assert "Auto-generating" in str(w[0].message), "Condition must be true"

    def test_init_creates_empty_revoked_tokens(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        assert isinstance(tm._revoked_tokens, set)
        assert len(tm._revoked_tokens) == 0, "Collection must not be empty"

    def test_init_creates_empty_sessions(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        assert isinstance(tm._sessions, dict)
        assert len(tm._sessions) == 0, "Collection must not be empty"


class TestAccessTokenGeneration:
    """Tests for access token generation."""

    def test_generate_access_token_returns_string(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")
        assert isinstance(token, str)

    def test_generate_access_token_format(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")
        parts = token.split(".")
        assert len(parts) == 3, "Parts must not be empty"

    def test_generate_access_token_with_scope(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123", scope="read write")
        claims = tm.validate_token(token)
        assert claims.scope == "read write", "scope is not valid"

    def test_generate_access_token_has_correct_type(self) -> None:
        from codex.auth.token_manager import TokenManager, TokenType

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")
        claims = tm.validate_token(token)
        assert claims.type == TokenType.ACCESS, "type is not valid"


class TestRefreshTokenGeneration:
    """Tests for refresh token generation."""

    def test_generate_refresh_token_returns_string(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_refresh_token("user123")
        assert isinstance(token, str)

    def test_generate_refresh_token_format(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_refresh_token("user123")
        parts = token.split(".")
        assert len(parts) == 3, "Parts must not be empty"

    def test_generate_refresh_token_has_correct_type(self) -> None:
        from codex.auth.token_manager import TokenManager, TokenType

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_refresh_token("user123")
        claims = tm.validate_token(token)
        assert claims.type == TokenType.REFRESH, "type is not valid"


class TestSessionTokenGeneration:
    """Tests for session token generation."""

    def test_generate_session_token_returns_tuple(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        result = tm.generate_session_token("user123")
        assert isinstance(result, tuple)
        assert len(result) == 2, "Result must not be empty"

    def test_generate_session_token_creates_session(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        _token, session_id = tm.generate_session_token("user123")
        assert session_id in tm._sessions, "Condition must be true"

    def test_generate_session_token_with_mfa(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        _token, session_id = tm.generate_session_token("user123", mfa_verified=True)
        session = tm.get_session(session_id)
        assert session.mfa_verified is True, "mfa_verified is not valid"

    def test_generate_session_token_with_ip(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        _token, session_id = tm.generate_session_token("user123", ip_address="192.168.1.100")
        session = tm.get_session(session_id)
        assert session.ip_address == "192.168.1.100", "ip_address is not valid"

    def test_generate_session_token_with_user_agent(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        _token, session_id = tm.generate_session_token("user123", user_agent="Mozilla/5.0")
        session = tm.get_session(session_id)
        assert session.user_agent == "Mozilla/5.0", "user_agent is not valid"


class TestTokenValidation:
    """Tests for token validation."""

    def test_validate_access_token(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")
        claims = tm.validate_token(token)
        assert claims.sub == "user123", "sub is not valid"

    def test_validate_expired_token_raises(self) -> None:
        from codex.auth.token_manager import TokenClaims, TokenManager, TokenType

        tm = TokenManager(secret_key="test-secret")
        # Create an already expired token
        now = time.time()
        claims = TokenClaims(
            sub="user123",
            iat=now - 1000,
            exp=now - 100,  # Expired
            type=TokenType.ACCESS,
        )
        token = tm._encode_token(claims)

        with pytest.raises(ValueError, match="expired"):
            tm.validate_token(token)

    def test_validate_token_wrong_type_raises(self) -> None:
        from codex.auth.token_manager import TokenManager, TokenType

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")

        with pytest.raises(ValueError, match="Invalid token type"):
            tm.validate_token(token, expected_type=TokenType.REFRESH)

    def test_validate_invalid_token_raises(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")

        with pytest.raises(ValueError):
            tm.validate_token("invalid.token.here")

    def test_validate_tampered_token_raises(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")

        # Tamper with the token
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + "." + "tampered"

        with pytest.raises(ValueError):
            tm.validate_token(tampered)


class TestTokenRevocation:
    """Tests for token revocation."""

    def test_revoke_token(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")

        result = tm.revoke_token(token)
        assert result is True, "Result must not be empty"

    def test_revoke_token_prevents_validation(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        token = tm.generate_access_token("user123")

        tm.revoke_token(token)

        with pytest.raises(ValueError, match="revoked"):
            tm.validate_token(token)

    def test_revoke_invalid_token_returns_false(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        result = tm.revoke_token("invalid.token.here")
        assert result is False, "Result must not be empty"

    def test_revoke_all_user_tokens(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")

        # Create multiple sessions for a user
        tm.generate_session_token("user123")
        tm.generate_session_token("user123")
        tm.generate_session_token("user123")

        count = tm.revoke_all_user_tokens("user123")
        assert count == 3, "Count must be greater than zero"

    def test_revoke_all_user_tokens_no_sessions(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        count = tm.revoke_all_user_tokens("nonexistent")
        assert count == 0, "Count must be greater than zero"


class TestRefreshAccessToken:
    """Tests for refreshing access tokens."""

    def test_refresh_access_token(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        refresh_token = tm.generate_refresh_token("user123")

        new_access_token = tm.refresh_access_token(refresh_token)
        assert isinstance(new_access_token, str)

    def test_refresh_with_invalid_token_raises(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")

        with pytest.raises(ValueError):
            tm.refresh_access_token("invalid.token.here")

    def test_refresh_with_access_token_raises(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        access_token = tm.generate_access_token("user123")

        with pytest.raises(ValueError, match="Invalid token type"):
            tm.refresh_access_token(access_token)


class TestSessionManagement:
    """Tests for session management."""

    def test_get_session(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        _token, session_id = tm.generate_session_token("user123")

        session = tm.get_session(session_id)
        assert session is not None, "session must be initialized"
        assert session.user_id == "user123", "user_id is not valid"

    def test_get_nonexistent_session(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        session = tm.get_session("nonexistent")
        assert session is None, "session is not valid"

    def test_get_user_sessions(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")
        tm.generate_session_token("user123")
        tm.generate_session_token("user123")
        tm.generate_session_token("user456")

        sessions = tm.get_user_sessions("user123")
        assert len(sessions) == 2, "Sessions must not be empty"

    def test_cleanup_expired_sessions(self) -> None:
        from codex.auth.token_manager import TokenManager

        tm = TokenManager(secret_key="test-secret")

        # Create a session and make it expired
        _token, session_id = tm.generate_session_token("user123")
        session = tm.get_session(session_id)
        session.last_activity = time.time() - 3600  # 1 hour ago

        count = tm.cleanup_expired_sessions()
        assert count == 1, "Count must be greater than zero"


class TestSessionInfo:
    """Tests for SessionInfo data class."""

    def test_session_info_creation(self) -> None:
        from codex.auth.token_manager import SessionInfo

        now = time.time()
        session = SessionInfo(
            session_id="sess123",
            user_id="user123",
            created_at=now,
            last_activity=now,
        )
        assert session.session_id == "sess123", "session_id is not valid"
        assert session.user_id == "user123", "user_id is not valid"

    def test_session_is_active(self) -> None:
        from codex.auth.token_manager import SessionInfo

        now = time.time()
        session = SessionInfo(
            session_id="sess123",
            user_id="user123",
            created_at=now,
            last_activity=now,
        )
        assert session.is_active() is True, "Condition must be true"

    def test_session_is_not_active(self) -> None:
        from codex.auth.token_manager import SessionInfo

        now = time.time()
        session = SessionInfo(
            session_id="sess123",
            user_id="user123",
            created_at=now - 3600,
            last_activity=now - 3600,  # 1 hour ago
        )
        assert session.is_active(timeout=1800) is False, "Condition must be true"

    def test_session_update_activity(self) -> None:
        from codex.auth.token_manager import SessionInfo

        now = time.time()
        session = SessionInfo(
            session_id="sess123",
            user_id="user123",
            created_at=now - 100,
            last_activity=now - 100,
        )

        old_activity = session.last_activity
        session.update_activity()
        assert session.last_activity > old_activity, "last_activity must be greater than zero"


class TestTokenClaims:
    """Tests for TokenClaims data class."""

    def test_token_claims_creation(self) -> None:
        from codex.auth.token_manager import TokenClaims, TokenType

        now = time.time()
        claims = TokenClaims(
            sub="user123",
            iat=now,
            exp=now + 900,
            type=TokenType.ACCESS,
        )
        assert claims.sub == "user123", "sub is not valid"
        assert claims.type == TokenType.ACCESS, "type is not valid"

    def test_token_claims_to_dict(self) -> None:
        from codex.auth.token_manager import TokenClaims, TokenType

        now = time.time()
        claims = TokenClaims(
            sub="user123",
            iat=now,
            exp=now + 900,
            type=TokenType.ACCESS,
            scope="read write",
            jti="token123",
        )

        data = claims.to_dict()
        assert data["sub"] == "user123", "Data must not be empty"
        assert data["type"] == "access", "Data must not be empty"
        assert data["scope"] == "read write", "Data must not be empty"

    def test_token_claims_from_dict(self) -> None:
        from codex.auth.token_manager import TokenClaims, TokenType

        now = time.time()
        data = {
            "sub": "user123",
            "iat": now,
            "exp": now + 900,
            "type": "access",
            "scope": "read",
            "jti": "token123",
        }

        claims = TokenClaims.from_dict(data)
        assert claims.sub == "user123", "sub is not valid"
        assert claims.type == TokenType.ACCESS, "type is not valid"


class TestTokenType:
    """Tests for TokenType enum."""

    def test_token_type_values(self) -> None:
        from codex.auth.token_manager import TokenType

        assert TokenType.ACCESS.value == "access", "Value must be initialized"
        assert TokenType.REFRESH.value == "refresh", "Value must be initialized"
        assert TokenType.SESSION.value == "session", "Value must be initialized"

    def test_token_type_from_value(self) -> None:
        from codex.auth.token_manager import TokenType

        assert TokenType("access") == TokenType.ACCESS, "Condition must be true"
        assert TokenType("refresh") == TokenType.REFRESH, "Condition must be true"
        assert TokenType("session") == TokenType.SESSION, "Condition must be true"


class TestTokenExpiry:
    """Tests for token expiry constants."""

    def test_access_token_expiry(self) -> None:
        from codex.auth.token_manager import TokenManager

        assert TokenManager.ACCESS_TOKEN_EXPIRY == 900, "ACCESS_TOKEN_EXPIRY is not valid"

    def test_refresh_token_expiry(self) -> None:
        from codex.auth.token_manager import TokenManager

        assert TokenManager.REFRESH_TOKEN_EXPIRY == 604800, "REFRESH_TOKEN_EXPIRY is not valid"

    def test_session_token_expiry(self) -> None:
        from codex.auth.token_manager import TokenManager

        assert TokenManager.SESSION_TOKEN_EXPIRY == 2592000, "SESSION_TOKEN_EXPIRY is not valid"
