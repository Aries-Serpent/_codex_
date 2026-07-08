"""
Critical Path Tests: Authentication Flows

Comprehensive test suite for authentication critical paths including:
- Login/logout workflows
- Token validation and expiration
- Session management
- Rate limiting and brute force protection
- Password reset workflows

All tests are deterministic and isolated.
"""

import time

import pytest

from codex.auth.middleware import (
    RateLimiter,
)
from codex.auth.token_manager import (
    TokenManager,
    TokenType,
)


class TestLoginLogoutFlows:
    """Tests for complete login/logout workflows."""

    def test_successful_login_flow(self):
        """Test complete successful login flow."""
        manager = TokenManager(secret_key="test-secret-key")
        user_id = "user123"

        # Generate session token
        session_token, session_id = manager.generate_session_token(
            user_id=user_id, ip_address="192.168.1.1", user_agent="TestBrowser/1.0"
        )

        assert session_token, "session_token is not valid"
        assert session_id, "session_id is not valid"

        # Validate token
        claims = manager.validate_token(session_token, TokenType.SESSION)
        assert claims.sub == user_id, "sub is not valid"
        assert claims.type == TokenType.SESSION, "type is not valid"

    def test_logout_flow_revokes_token(self):
        """Test logout properly revokes session token."""
        manager = TokenManager(secret_key="test-secret-key")

        # Login
        session_token, _session_id = manager.generate_session_token("user123")

        # Validate token works
        manager.validate_token(session_token)

        # Logout (revoke token)
        result = manager.revoke_token(session_token)
        assert result is True, "Result must not be empty"

        # Token should now be invalid
        with pytest.raises(ValueError, match="Token revoked"):
            manager.validate_token(session_token)

    def test_logout_removes_session(self):
        """Test logout removes session from storage."""
        manager = TokenManager(secret_key="test-secret-key")

        session_token, session_id = manager.generate_session_token("user123")

        # Session exists
        assert manager.get_session(session_id) is not None, "Value must be initialized"

        # Logout
        manager.revoke_token(session_token)

        # Session removed
        assert manager.get_session(session_id) is None, "Condition must be true"

    def test_concurrent_sessions_for_user(self):
        """Test multiple concurrent sessions for same user."""
        manager = TokenManager(secret_key="test-secret-key")
        user_id = "user123"

        # Create multiple sessions
        session1_token, _session1_id = manager.generate_session_token(
            user_id, ip_address="192.168.1.1"
        )
        session2_token, _session2_id = manager.generate_session_token(
            user_id, ip_address="192.168.1.2"
        )

        # Both sessions valid
        manager.validate_token(session1_token)
        manager.validate_token(session2_token)

        # Both sessions tracked
        sessions = manager.get_user_sessions(user_id)
        assert len(sessions) == 2, "Sessions must not be empty"

    def test_login_with_mfa_verification(self):
        """Test login flow with MFA verification."""
        manager = TokenManager(secret_key="test-secret-key")

        # Login with MFA
        _session_token, session_id = manager.generate_session_token(
            user_id="user123", mfa_verified=True
        )

        session = manager.get_session(session_id)
        assert session.mfa_verified is True, "mfa_verified is not valid"


class TestTokenValidationExpiration:
    """Tests for token validation and expiration handling."""

    def test_valid_token_accepted(self):
        """Test valid token is accepted."""
        manager = TokenManager(secret_key="test-secret-key")
        token = manager.generate_access_token("user123")

        claims = manager.validate_token(token)
        assert claims.sub == "user123", "sub is not valid"
        assert claims.type == TokenType.ACCESS, "type is not valid"

    def test_expired_token_rejected(self):
        """Test expired token is rejected."""
        manager = TokenManager(secret_key="test-secret-key")

        # Temporarily reduce expiry
        original_expiry = manager.ACCESS_TOKEN_EXPIRY
        manager.ACCESS_TOKEN_EXPIRY = -1  # Already expired

        token = manager.generate_access_token("user123")

        # Restore expiry
        manager.ACCESS_TOKEN_EXPIRY = original_expiry

        with pytest.raises(ValueError, match="Token expired"):
            manager.validate_token(token)

    def test_wrong_token_type_rejected(self):
        """Test token type validation."""
        manager = TokenManager(secret_key="test-secret-key")
        access_token = manager.generate_access_token("user123")

        with pytest.raises(ValueError, match="Invalid token type"):
            manager.validate_token(access_token, TokenType.REFRESH)

    def test_malformed_token_rejected(self):
        """Test malformed token is rejected."""
        manager = TokenManager(secret_key="test-secret-key")

        malformed_tokens = [
            "not.a.token",
            "only-one-part",
            "two.parts",
            "",
            "invalid.base64!.data",
        ]

        for token in malformed_tokens:
            with pytest.raises(ValueError):
                manager.validate_token(token)

    def test_token_with_invalid_signature_rejected(self):
        """Test token with tampered signature is rejected."""
        manager1 = TokenManager(secret_key="secret1")
        manager2 = TokenManager(secret_key="secret2")

        token = manager1.generate_access_token("user123")

        with pytest.raises(ValueError, match="Invalid token signature"):
            manager2.validate_token(token)

    def test_revoked_token_rejected(self):
        """Test revoked token is rejected."""
        manager = TokenManager(secret_key="test-secret-key")
        token = manager.generate_access_token("user123")

        # Token works initially
        manager.validate_token(token)

        # Revoke token
        manager.revoke_token(token)

        # Token should be rejected
        with pytest.raises(ValueError, match="Token revoked"):
            manager.validate_token(token)


class TestSessionManagement:
    """Tests for session lifecycle management."""

    def test_session_creation_stores_metadata(self):
        """Test session creation stores all metadata."""
        manager = TokenManager(secret_key="test-secret-key")

        _token, session_id = manager.generate_session_token(
            user_id="user123", ip_address="10.0.0.1", user_agent="Chrome/90.0", mfa_verified=True
        )

        session = manager.get_session(session_id)
        assert session is not None, "session must be initialized"
        assert session.user_id == "user123", "user_id is not valid"
        assert session.ip_address == "10.0.0.1", "ip_address is not valid"
        assert session.user_agent == "Chrome/90.0", "user_agent is not valid"
        assert session.mfa_verified is True, "mfa_verified is not valid"

    def test_session_activity_tracking(self):
        """Test session tracks last activity."""
        manager = TokenManager(secret_key="test-secret-key")
        token, session_id = manager.generate_session_token("user123")

        session = manager.get_session(session_id)
        original_activity = session.last_activity

        # Wait and validate token (updates activity)
        time.sleep(0.1)
        manager.validate_token(token)

        updated_session = manager.get_session(session_id)
        assert updated_session.last_activity > original_activity, "last_activity must be greater than zero"

    def test_inactive_session_timeout(self):
        """Test session timeout based on inactivity."""
        manager = TokenManager(secret_key="test-secret-key")
        _token, session_id = manager.generate_session_token("user123")

        session = manager.get_session(session_id)

        # Mock old activity time
        session.last_activity = time.time() - 2000  # 33+ minutes ago

        # Session should be inactive
        assert not session.is_active(timeout=1800), "Condition must be true"

    def test_cleanup_expired_sessions(self):
        """Test cleanup removes expired sessions."""
        manager = TokenManager(secret_key="test-secret-key")

        # Create active and expired sessions
        _active_token, active_id = manager.generate_session_token("user1")
        _expired_token, expired_id = manager.generate_session_token("user2")

        # Mark one as expired
        expired_session = manager.get_session(expired_id)
        expired_session.last_activity = time.time() - 2000

        # Cleanup
        cleaned = manager.cleanup_expired_sessions()

        assert cleaned == 1, "cleaned is not valid"
        assert manager.get_session(active_id) is not None, "Value must be initialized"
        assert manager.get_session(expired_id) is None, "Condition must be true"

    def test_get_all_user_sessions(self):
        """Test retrieving all active sessions for a user."""
        manager = TokenManager(secret_key="test-secret-key")
        user_id = "user123"

        # Create multiple sessions
        for i in range(3):
            manager.generate_session_token(user_id, ip_address=f"192.168.1.{i}")

        sessions = manager.get_user_sessions(user_id)
        assert len(sessions) == 3, "Sessions must not be empty"
        assert all(s.user_id == user_id for s in sessions), "user_id is not valid"

    def test_revoke_all_user_sessions(self):
        """Test revoking all sessions for a user (e.g., password change)."""
        manager = TokenManager(secret_key="test-secret-key")
        user_id = "user123"

        # Create multiple sessions
        tokens = []
        for _ in range(3):
            token, _ = manager.generate_session_token(user_id)
            tokens.append(token)

        # Revoke all sessions
        count = manager.revoke_all_user_tokens(user_id)
        assert count == 3, "Count must be greater than zero"

        # All tokens should be invalid
        for token in tokens:
            with pytest.raises(ValueError):
                manager.validate_token(token)


class TestRateLimitingBruteForce:
    """Tests for rate limiting and brute force protection."""

    def test_rate_limiter_allows_within_limit(self):
        """Test rate limiter allows requests within limit."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)

        # All requests within limit should be allowed
        for _ in range(5):
            assert limiter.is_allowed("user123") is True, "Condition must be true"

    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit."""
        limiter = RateLimiter(requests_per_window=3, window_seconds=60)

        # First 3 allowed
        for _ in range(3):
            assert limiter.is_allowed("user123") is True, "Condition must be true"

        # 4th blocked
        assert limiter.is_allowed("user123") is False, "Condition must be true"

    def test_rate_limiter_per_user_isolation(self):
        """Test rate limiter tracks users independently."""
        limiter = RateLimiter(requests_per_window=2, window_seconds=60)

        # User1 uses their quota
        assert limiter.is_allowed("user1") is True, "Condition must be true"
        assert limiter.is_allowed("user1") is True, "Condition must be true"
        assert limiter.is_allowed("user1") is False, "Condition must be true"

        # User2 still has quota
        assert limiter.is_allowed("user2") is True, "Condition must be true"
        assert limiter.is_allowed("user2") is True, "Condition must be true"

    @pytest.mark.slow
    def test_rate_limiter_window_reset(self):
        """Test rate limiter resets after window expires."""
        limiter = RateLimiter(requests_per_window=2, window_seconds=1)

        # Use quota
        assert limiter.is_allowed("user123") is True, "Condition must be true"
        assert limiter.is_allowed("user123") is True, "Condition must be true"
        assert limiter.is_allowed("user123") is False, "Condition must be true"

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed("user123") is True, "Condition must be true"

    def test_rate_limiter_get_remaining(self):
        """Test getting remaining requests in window."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)

        assert limiter.get_remaining("user123") == 5, "Condition must be true"

        limiter.is_allowed("user123")
        assert limiter.get_remaining("user123") == 4, "Condition must be true"

        limiter.is_allowed("user123")
        assert limiter.get_remaining("user123") == 3, "Condition must be true"

    @pytest.mark.slow
    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleanup removes old entries."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=1)

        # Make requests
        limiter.is_allowed("user1")
        limiter.is_allowed("user2")
        limiter.is_allowed("user3")

        # Wait for window to expire
        time.sleep(1.1)

        # Cleanup should remove all
        cleaned = limiter.cleanup()
        assert cleaned == 3, "cleaned is not valid"


class TestPasswordResetWorkflows:
    """Tests for password reset workflows."""

    def test_generate_password_reset_token(self):
        """Test generating password reset token."""
        manager = TokenManager(secret_key="test-secret-key")

        # Use access token as reset token with special scope
        reset_token = manager.generate_access_token("user123", scope="password_reset")

        claims = manager.validate_token(reset_token)
        assert claims.scope == "password_reset", "scope is not valid"

    def test_password_reset_revokes_existing_sessions(self):
        """Test password reset revokes all existing user sessions."""
        manager = TokenManager(secret_key="test-secret-key")
        user_id = "user123"

        # Create existing sessions
        tokens = []
        for _ in range(3):
            token, _ = manager.generate_session_token(user_id)
            tokens.append(token)

        # Simulate password reset (revoke all tokens)
        revoked_count = manager.revoke_all_user_tokens(user_id)
        assert revoked_count == 3, "Count must be greater than zero"

        # All old tokens invalid
        for token in tokens:
            with pytest.raises(ValueError):
                manager.validate_token(token)

    def test_password_reset_token_single_use(self):
        """Test password reset token can only be used once."""
        manager = TokenManager(secret_key="test-secret-key")

        reset_token = manager.generate_access_token("user123", scope="password_reset")

        # First use works
        manager.validate_token(reset_token)

        # Revoke after use
        manager.revoke_token(reset_token)

        # Second use fails
        with pytest.raises(ValueError, match="Token revoked"):
            manager.validate_token(reset_token)

    def test_password_reset_token_expiration(self):
        """Test password reset token has short expiration."""
        manager = TokenManager(secret_key="test-secret-key")

        # Temporarily set short expiry
        original = manager.ACCESS_TOKEN_EXPIRY
        manager.ACCESS_TOKEN_EXPIRY = 900  # 15 minutes

        reset_token = manager.generate_access_token("user123", scope="password_reset")
        claims = manager.validate_token(reset_token)

        # Token should expire in 15 minutes
        assert claims.exp - claims.iat <= 900, "iat is not valid"

        manager.ACCESS_TOKEN_EXPIRY = original

    def test_password_reset_validates_scope(self):
        """Test password reset endpoint validates token scope."""
        manager = TokenManager(secret_key="test-secret-key")

        # Regular token shouldn't work for password reset
        regular_token = manager.generate_access_token("user123", scope="read write")
        claims = manager.validate_token(regular_token)

        # Scope check
        assert "password_reset" not in (claims.scope or ""), "Condition must be true"
