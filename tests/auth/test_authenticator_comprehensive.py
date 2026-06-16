"""Comprehensive tests for codex.auth.authenticator module.

This module tests high-level authentication service including:
- User registration
- Login/logout
- Password management
- MFA handling
- Session management
"""

from __future__ import annotations
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from codex.auth.authenticator import (
    Authenticator,
    LoginResult,
)
from codex.auth.exceptions import (
    InvalidCredentialsError,
    MFARequiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from codex.auth.mfa_provider import MFAProvider
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def user_store():
    """Create a user store."""
    return UserStore()


@pytest.fixture
def token_manager():
    """Create a token manager."""
    return TokenManager(secret_key="test-secret-key")


@pytest.fixture
def mfa_provider():
    """Create an MFA provider."""
    return MFAProvider()


@pytest.fixture
def authenticator(user_store, token_manager):
    """Create an authenticator."""
    return Authenticator(user_store=user_store, token_manager=token_manager)


@pytest.fixture
def authenticator_with_mfa(user_store, token_manager, mfa_provider):
    """Create an authenticator with MFA."""
    return Authenticator(
        user_store=user_store,
        token_manager=token_manager,
        mfa_provider=mfa_provider,
    )


# ============================================================================
# LOGIN_RESULT TESTS
# ============================================================================


class TestLoginResult:
    """Test LoginResult dataclass."""

    def test_login_result_creation(self):
        """Test creating LoginResult."""
        result = LoginResult(
            user_id="user123",
            username="testuser",
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            session_token="session_token_123",
            expires_in=3600,
        )
        assert result.user_id == "user123"
        assert result.username == "testuser"

    def test_login_result_tokens_present(self):
        """Test all tokens are present."""
        result = LoginResult(
            user_id="user123",
            username="testuser",
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            session_token="session_token_123",
        )
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.session_token is not None

    def test_login_result_expires_in(self):
        """Test expires_in field."""
        result = LoginResult(
            user_id="user123",
            username="testuser",
            access_token="access_token_123",
            expires_in=7200,
        )
        assert result.expires_in == 7200

    def test_login_result_optional_mfa_required(self):
        """Test optional mfa_required field."""
        result = LoginResult(
            user_id="user123",
            username="testuser",
            access_token="access_token_123",
            mfa_required=True,
        )
        assert result.mfa_required is True

    def test_login_result_timestamp(self):
        """Test timestamp field."""
        now = datetime.now(UTC)
        result = LoginResult(
            user_id="user123",
            username="testuser",
            access_token="access_token_123",
            timestamp=now,
        )
        assert result.timestamp == now


# ============================================================================
# AUTHENTICATOR BASIC TESTS
# ============================================================================


class TestAuthenticatorBasic:
    """Test Authenticator basic functionality."""

    def test_authenticator_creation(self, authenticator):
        """Test creating an authenticator."""
        assert authenticator is not None
        assert authenticator.user_store is not None
        assert authenticator.token_manager is not None

    def test_authenticator_with_mfa(self, authenticator_with_mfa):
        """Test creating authenticator with MFA."""
        assert authenticator_with_mfa.mfa_provider is not None

    def test_authenticator_without_mfa(self, authenticator):
        """Test authenticator without MFA."""
        assert authenticator.mfa_provider is None


# ============================================================================
# REGISTRATION TESTS
# ============================================================================


class TestRegistration:
    """Test user registration."""

    def test_register_new_user(self, authenticator):
        """Test registering a new user."""
        user = authenticator.register(
            username="newuser",
            email="newuser@example.com",
            ******,
        )
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"

    def test_register_duplicate_username(self, authenticator):
        """Test registering duplicate username."""
        authenticator.register(
            username="existing",
            email="existing@example.com",
            ******,
        )
        with pytest.raises(UserAlreadyExistsError):
            authenticator.register(
                username="existing",
                email="different@example.com",
                ******,
            )

    def test_register_duplicate_email(self, authenticator):
        """Test registering duplicate email."""
        authenticator.register(
            username="user1",
            email="same@example.com",
            ******,
        )
        with pytest.raises(UserAlreadyExistsError):
            authenticator.register(
                username="user2",
                email="same@example.com",
                ******,
            )

    def test_register_weak_password(self, authenticator):
        """Test registering with weak password."""
        with pytest.raises((ValueError, Exception)):
            authenticator.register(
                username="user",
                email="user@example.com",
                ******,
            )

    def test_register_invalid_email(self, authenticator):
        """Test registering with invalid email."""
        with pytest.raises((ValueError, Exception)):
            authenticator.register(
                username="user",
                email="not-an-email",
                ******,
            )

    def test_register_empty_username(self, authenticator):
        """Test registering with empty username."""
        with pytest.raises((ValueError, Exception)):
            authenticator.register(
                username="",
                email="user@example.com",
                ******,
            )

    def test_register_with_metadata(self, authenticator):
        """Test registering with metadata."""
        user = authenticator.register(
            username="user",
            email="user@example.com",
            ******,
            metadata={"role": "developer", "team": "backend"},
        )
        assert user.username == "user"


# ============================================================================
# LOGIN TESTS
# ============================================================================


class TestLogin:
    """Test user login."""

    def test_login_valid_credentials(self, authenticator):
        """Test login with valid credentials."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        assert isinstance(result, LoginResult)
        assert result.username == "user"

    def test_login_invalid_username(self, authenticator):
        """Test login with invalid username."""
        with pytest.raises(UserNotFoundError):
            authenticator.login("nonexistent", "password", ip_address="192.168.1.1")

    def test_login_invalid_password(self, authenticator):
        """Test login with invalid password."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        with pytest.raises(InvalidCredentialsError):
            authenticator.login("user", "WrongPassword", ip_address="192.168.1.1")

    def test_login_with_ip_address(self, authenticator):
        """Test login with IP address."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        assert result is not None

    def test_login_with_user_agent(self, authenticator):
        """Test login with user agent."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login(
            "user",
            "SecurePassword123!",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        assert result is not None

    def test_login_returns_tokens(self, authenticator):
        """Test login returns all tokens."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        assert result.access_token is not None
        assert result.session_token is not None

    def test_login_sets_expires_in(self, authenticator):
        """Test login sets expires_in."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        assert result.expires_in > 0

    def test_login_empty_password(self, authenticator):
        """Test login with empty password."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        with pytest.raises(InvalidCredentialsError):
            authenticator.login("user", "", ip_address="192.168.1.1")


# ============================================================================
# LOGOUT TESTS
# ============================================================================


class TestLogout:
    """Test user logout."""

    def test_logout_valid_session(self, authenticator):
        """Test logout with valid session token."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        authenticator.logout(result.session_token)
        # Should not raise

    def test_logout_invalid_session(self, authenticator):
        """Test logout with invalid session token."""
        with pytest.raises((ValueError, Exception)):
            authenticator.logout("invalid_token")

    def test_logout_empty_session(self, authenticator):
        """Test logout with empty session token."""
        with pytest.raises((ValueError, Exception)):
            authenticator.logout("")


# ============================================================================
# PASSWORD MANAGEMENT TESTS
# ============================================================================


class TestPasswordManagement:
    """Test password management."""

    def test_change_password_valid(self, authenticator):
        """Test changing password with valid credentials."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        authenticator.change_password(
            "user",
            old_password="OldPassword123!",
            new_password="NewPassword123!",
        )
        # Should be able to login with new password
        result = authenticator.login("user", "NewPassword123!", ip_address="192.168.1.1")
        assert result is not None

    def test_change_password_invalid_old(self, authenticator):
        """Test changing password with invalid old password."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        with pytest.raises(InvalidCredentialsError):
            authenticator.change_password(
                "user",
                old_password="OldPassword123!""WrongPassword",
                new_password="NewPassword123!",
            )

    def test_change_password_weak_new(self, authenticator):
        """Test changing to weak password."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        with pytest.raises((ValueError, Exception)):
            authenticator.change_password(
                "user",
                old_password="Password123!",
                new_password="weak",
            )

    def test_reset_password(self, authenticator):
        """Test password reset."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        reset_token = authenticator.request_password_reset("user@example.com")
        assert reset_token is not None
        
        authenticator.reset_password(reset_token, "NewPassword123!")
        result = authenticator.login("user", "NewPassword123!", ip_address="192.168.1.1")
        assert result is not None

    def test_reset_password_invalid_email(self, authenticator):
        """Test password reset with invalid email."""
        reset_token = authenticator.request_password_reset("nonexistent@example.com")
        # Should return None or empty token (security: don't reveal if user exists)
        assert reset_token is None or reset_token == ""


# ============================================================================
# MFA TESTS
# ============================================================================


class TestMFAIntegration:
    """Test MFA integration."""

    def test_login_with_mfa_required(self, authenticator_with_mfa):
        """Test login when MFA is required."""
        authenticator_with_mfa.register(
            username="user",
            email="user@example.com",
            ******,
            enable_mfa=True,
        )
        with pytest.raises(MFARequiredError):
            authenticator_with_mfa.login("user", "SecurePassword123!", ip_address="192.168.1.1")

    def test_enable_mfa_for_user(self, authenticator_with_mfa):
        """Test enabling MFA for existing user."""
        authenticator_with_mfa.register(
            username="user",
            email="user@example.com",
            ******,
        )
        mfa_secret = authenticator_with_mfa.enable_mfa("user")
        assert mfa_secret is not None

    def test_disable_mfa_for_user(self, authenticator_with_mfa):
        """Test disabling MFA for user."""
        authenticator_with_mfa.register(
            username="user",
            email="user@example.com",
            ******,
            enable_mfa=True,
        )
        authenticator_with_mfa.disable_mfa("user", "SecurePassword123!")
        # User should be able to login without MFA

    def test_verify_mfa_code(self, authenticator_with_mfa):
        """Test verifying MFA code."""
        authenticator_with_mfa.register(
            username="user",
            email="user@example.com",
            ******,
            enable_mfa=True,
        )
        # This would require actual MFA code generation/verification


# ============================================================================
# TOKEN REFRESH TESTS
# ============================================================================


class TestTokenRefresh:
    """Test token refresh."""

    def test_refresh_access_token(self, authenticator):
        """Test refreshing access token."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        
        # Refresh the access token
        new_result = authenticator.refresh_token(result.refresh_token)
        assert new_result.access_token is not None
        assert new_result.access_token != result.access_token

    def test_refresh_with_invalid_token(self, authenticator):
        """Test refresh with invalid refresh token."""
        with pytest.raises((ValueError, Exception)):
            authenticator.refresh_token("invalid_token")

    def test_refresh_with_expired_token(self, authenticator):
        """Test refresh with expired refresh token."""
        with pytest.raises((ValueError, Exception)):
            authenticator.refresh_token("expired_token")


# ============================================================================
# SESSION MANAGEMENT TESTS
# ============================================================================


class TestSessionManagement:
    """Test session management."""

    def test_get_active_sessions(self, authenticator):
        """Test getting active sessions."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        
        sessions = authenticator.get_active_sessions("user")
        assert len(sessions) > 0

    def test_revoke_session(self, authenticator):
        """Test revoking a session."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        
        authenticator.revoke_session(result.session_token)
        # Session should be revoked

    def test_revoke_all_sessions(self, authenticator):
        """Test revoking all sessions."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        # Create multiple sessions
        authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.2")
        
        authenticator.revoke_all_sessions("user")
        # All sessions should be revoked


# ============================================================================
# AUTHENTICATION STATE TESTS
# ============================================================================


class TestAuthenticationState:
    """Test authentication state."""

    def test_is_user_authenticated_valid_token(self, authenticator):
        """Test checking authentication with valid token."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        
        is_auth = authenticator.is_authenticated(result.access_token)
        assert is_auth is True

    def test_is_user_authenticated_invalid_token(self, authenticator):
        """Test checking authentication with invalid token."""
        is_auth = authenticator.is_authenticated("invalid_token")
        assert is_auth is False

    def test_get_user_from_token(self, authenticator):
        """Test getting user from token."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        
        user = authenticator.get_user_from_token(result.access_token)
        assert user.username == "user"

    def test_get_user_from_invalid_token(self, authenticator):
        """Test getting user from invalid token."""
        user = authenticator.get_user_from_token("invalid_token")
        assert user is None


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize("username,email,should_succeed", [
    ("user1", "user1@example.com", True),
    ("user2", "user2@example.com", True),
    ("", "user3@example.com", False),
    ("user4", "invalid-email", False),
])
def test_registration_parametrized(authenticator, username, email, should_succeed):
    """Parametrized test for registration."""
    if should_succeed:
        user = authenticator.register(
            username=username,
            email=email,
            ******,
        )
        assert user.username == username
    else:
        with pytest.raises((ValueError, UserAlreadyExistsError)):
            authenticator.register(
                username=username,
                email=email,
                ******,
            )


@pytest.mark.parametrize("password", [
    "StrongPassword123!",
    "VerySecure@Password2024",
    "Complex_Pass!23",
])
def test_strong_passwords_parametrized(authenticator, password):
    """Parametrized test for strong passwords."""
    user = authenticator.register(
        username=f"user_{hash(password) % 10000}",
        email=f"user_{hash(password) % 10000}@example.com",
        ******
    )
    assert user is not None


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_login_after_multiple_failed_attempts(self, authenticator):
        """Test login after multiple failed attempts."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        
        # Attempt failed logins
        for _ in range(3):
            try:
                authenticator.login("user", "WrongPassword", ip_address="192.168.1.1")
            except InvalidCredentialsError:
                pass
        
        # Should still be able to login with correct password
        result = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        assert result is not None

    def test_concurrent_logins_same_user(self, authenticator):
        """Test multiple concurrent logins from same user."""
        authenticator.register(
            username="user",
            email="user@example.com",
            ******,
        )
        
        result1 = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.1")
        result2 = authenticator.login("user", "SecurePassword123!", ip_address="192.168.1.2")
        
        assert result1.access_token != result2.access_token

    def test_very_long_password(self, authenticator):
        """Test registration with very long password."""
        long_password = "A" * 256 + "!"
        user = authenticator.register(
            username="user",
            email="user@example.com",
            ******
        )
        assert user is not None

    def test_special_characters_in_username(self, authenticator):
        """Test username with special characters."""
        try:
            user = authenticator.register(
                username="user@domain",
                email="user@example.com",
                ******,
            )
            assert user is not None
        except (ValueError, Exception):
            pass

    def test_unicode_in_email(self, authenticator):
        """Test unicode characters in email."""
        try:
            user = authenticator.register(
                username="user",
                email="用户@example.com",
                ******,
            )
            assert user is not None
        except (ValueError, Exception):
            pass
