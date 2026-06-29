"""
Comprehensive tests for the high-level Authenticator service.

Tests cover:
- User registration and validation
- Login/logout workflows
- Password management
- MFA integration
- Token lifecycle
- Edge cases and error handling
"""

import pytest

from codex.auth.authenticator import Authenticator, LoginResult
from codex.auth.exceptions import (
    InvalidCredentialsError,
    MFARequiredError,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    UserAlreadyExistsError,
)
from codex.auth.mfa_provider import MFAProvider
from codex.auth.token_manager import TokenManager, TokenType
from codex.auth.user_store import User, UserStore

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def token_manager():
    """Create a token manager with test secret."""
    return TokenManager(secret_key="test-secret-key-comprehensive")


@pytest.fixture
def user_store():
    """Create an in-memory user store."""
    return UserStore()


@pytest.fixture
def mfa_provider():
    """Create an MFA provider."""
    return MFAProvider()


@pytest.fixture
def auth_no_mfa(user_store, token_manager):
    """Create authenticator without MFA."""
    return Authenticator(user_store=user_store, token_manager=token_manager)


@pytest.fixture
def auth_with_mfa(user_store, token_manager, mfa_provider):
    """Create authenticator with MFA."""
    return Authenticator(
        user_store=user_store, token_manager=token_manager, mfa_provider=mfa_provider
    )


# ============================================================================
# Registration Tests
# ============================================================================


class TestRegisterBasic:
    """Basic registration functionality."""

    def test_register_creates_user(self, auth_no_mfa):
        user = auth_no_mfa.register("alice", "alice@example.com", "Str0ngPass!")
        assert user.username == "alice", "username is not valid"
        assert user.email == "alice@example.com", "email is not valid"
        assert user.user_id, "Condition must be true"

    def test_register_with_custom_roles(self, auth_no_mfa):
        user = auth_no_mfa.register(
            "bob", "bob@example.com", "Str0ngPass!", roles=["admin", "moderator"]
        )
        assert "admin" in user.roles, "Condition must be true"
        assert "moderator" in user.roles, "Condition must be true"
        # Verify the exact set of roles without default "user" role
        assert set(user.roles) == {"admin", "moderator"}, "Roles must be exactly as specified"
        assert isinstance(user.roles, list), "Roles must be returned as a list"

    def test_register_with_empty_roles(self, auth_no_mfa):
        user = auth_no_mfa.register("charlie", "charlie@example.com", "Str0ngPass!", roles=[])
        assert "user" in user.roles, "Condition must be true"
        # Verify default role is the only role when empty list is provided
        assert len(user.roles) == 1, "Should have exactly 1 default role"
        assert set(user.roles) == {"user"}, "Default role must be exactly 'user'"

        # Test with explicit None as well
        user2 = auth_no_mfa.register("diane", "diane@example.com", "Str0ngPass!", roles=None)
        assert "user" in user2.roles, "Default role must be assigned when roles is None"
        assert set(user2.roles) == {"user"}, "Default role must be exactly 'user'"

    def test_register_returns_user_object(self, auth_no_mfa):
        user = auth_no_mfa.register("dave", "dave@example.com", "Str0ngPass!")
        assert isinstance(user, User)

    def test_register_sets_created_timestamp(self, auth_no_mfa):
        user = auth_no_mfa.register("eve", "eve@example.com", "Str0ngPass!")
        assert user.created_at > 0, "created_at must be greater than zero"


class TestRegisterValidation:
    """Registration validation rules."""

    def test_register_duplicate_username_raises(self, auth_no_mfa):
        auth_no_mfa.register("frank", "frank@example.com", "Str0ngPass!")
        with pytest.raises(UserAlreadyExistsError):
            auth_no_mfa.register("frank", "frank2@example.com", "Str0ngPass!")

    def test_register_weak_password_too_short(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("grace", "grace@example.com", "short")

    def test_register_weak_password_no_uppercase(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("henry", "henry@example.com", "lowercaseonly123!")

    def test_register_weak_password_no_number(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("iris", "iris@example.com", "NoNumbersHere!")

    def test_register_weak_password_no_special(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("jack", "jack@example.com", "NoSpecialChar123")

    def test_register_empty_username_raises(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("", "test@example.com", "Str0ngPass!")

    def test_register_empty_email_raises(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("karl", "", "Str0ngPass!")

    def test_register_invalid_email_raises(self, auth_no_mfa):
        with pytest.raises(ValueError):
            auth_no_mfa.register("larry", "notanemail", "Str0ngPass!")

    def test_register_none_username_raises(self, auth_no_mfa):
        with pytest.raises((ValueError, TypeError)):
            auth_no_mfa.register(None, "test@example.com", "Str0ngPass!")

    def test_register_none_password_raises(self, auth_no_mfa):
        with pytest.raises((ValueError, TypeError)):
            auth_no_mfa.register("mike", "mike@example.com", None)


class TestRegisterUnicode:
    """Unicode and special character handling in registration."""

    def test_register_unicode_username(self, auth_no_mfa):
        user = auth_no_mfa.register("用户", "user@example.com", "Str0ngPass!")
        assert user.username == "用户", "username is not valid"

    def test_register_unicode_email(self, auth_no_mfa):
        # Standard emails don't support unicode in local part, but test domain
        user = auth_no_mfa.register("nancy", "nancy@例え.jp", "Str0ngPass!")
        assert "nancy@" in user.email, "Condition must be true"

    def test_register_emoji_username(self, auth_no_mfa):
        # Username with emoji
        user = auth_no_mfa.register("oscar😀", "oscar@example.com", "Str0ngPass!")
        assert "oscar" in user.username, "Condition must be true"

    def test_register_special_chars_username(self, auth_no_mfa):
        user = auth_no_mfa.register("paul_test-user", "paul@example.com", "Str0ngPass!")
        assert user.username == "paul_test-user", "username is not valid"


# ============================================================================
# Login Tests
# ============================================================================


class TestLoginBasic:
    """Basic login functionality."""

    def test_login_with_username(self, auth_no_mfa):
        auth_no_mfa.register("quinn", "quinn@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("quinn", "Str0ngPass!")
        assert isinstance(result, LoginResult)
        assert result.username == "quinn", "Result must not be empty"
        assert result.user_id, "Result must not be empty"

    def test_login_with_email(self, auth_no_mfa):
        auth_no_mfa.register("robin", "robin@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("robin@example.com", "Str0ngPass!")
        assert result.username == "robin", "Result must not be empty"

    def test_login_returns_all_tokens(self, auth_no_mfa):
        auth_no_mfa.register("sam", "sam@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("sam", "Str0ngPass!")
        assert result.access_token, "Result must not be empty"
        assert result.refresh_token, "Result must not be empty"
        assert result.session_token, "Result must not be empty"
        assert result.session_id, "Result must not be empty"

    def test_login_with_ip_address(self, auth_no_mfa):
        auth_no_mfa.register("tina", "tina@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("tina", "Str0ngPass!", ip_address="192.168.1.1")
        assert result.user_id, "Result must not be empty"

    def test_login_multiple_times(self, auth_no_mfa):
        auth_no_mfa.register("uma", "uma@example.com", "Str0ngPass!")
        result1 = auth_no_mfa.login("uma", "Str0ngPass!")
        result2 = auth_no_mfa.login("uma", "Str0ngPass!")
        # Different sessions
        assert result1.session_token != result2.session_token, "Result must not be empty"


class TestLoginFailure:
    """Login failure scenarios."""

    def test_login_wrong_password(self, auth_no_mfa):
        auth_no_mfa.register("victor", "victor@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            auth_no_mfa.login("victor", "WrongPass!")

    def test_login_nonexistent_user(self, auth_no_mfa):
        with pytest.raises(InvalidCredentialsError):
            auth_no_mfa.login("wendy", "Str0ngPass!")

    def test_login_case_sensitive_username(self, auth_no_mfa):
        auth_no_mfa.register("xavier", "xavier@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            auth_no_mfa.login("XAVIER", "Str0ngPass!")

    def test_login_empty_password(self, auth_no_mfa):
        auth_no_mfa.register("yara", "yara@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            auth_no_mfa.login("yara", "")

    def test_login_none_username_raises(self, auth_no_mfa):
        with pytest.raises((InvalidCredentialsError, TypeError)):
            auth_no_mfa.login(None, "Str0ngPass!")


class TestLoginMFA:
    """Login with MFA enabled."""

    def test_login_mfa_required(self, auth_with_mfa):
        auth_with_mfa.register("zoe", "zoe@example.com", "Str0ngPass!")
        # Enable MFA for user
        user = auth_with_mfa.user_store.get_by_username("zoe")
        auth_with_mfa.mfa_provider.register_mfa(user.user_id, "sha256")

        with pytest.raises(MFARequiredError):
            auth_with_mfa.login("zoe", "Str0ngPass!")

    def test_login_mfa_with_valid_code(self, auth_with_mfa):
        auth_with_mfa.register("zane", "zane@example.com", "Str0ngPass!")
        user = auth_with_mfa.user_store.get_by_username("zane")
        secret = auth_with_mfa.mfa_provider.register_mfa(user.user_id, "sha256")

        # Get valid TOTP code
        import pyotp

        totp = pyotp.TOTP(secret.secret)
        code = totp.now()

        result = auth_with_mfa.login("zane", "Str0ngPass!", mfa_code=code)
        assert result.user_id == user.user_id, "Result must not be empty"


# ============================================================================
# Logout Tests
# ============================================================================


class TestLogout:
    """Logout functionality."""

    def test_logout_invalidates_session(self, auth_no_mfa):
        auth_no_mfa.register("abby", "abby@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("abby", "Str0ngPass!")
        auth_no_mfa.logout(result.session_token)
        # Attempting to use the token should fail
        with pytest.raises(Exception):
            auth_no_mfa.token_manager.validate_token(
                result.session_token, expected_type=TokenType.SESSION
            )

    def test_logout_none_token(self, auth_no_mfa):
        # Should not raise and should return False
        result = auth_no_mfa.logout(None)
        assert result is False, "Logout with None token should return False"

    def test_logout_invalid_token(self, auth_no_mfa):
        # Should not raise and should return False
        result = auth_no_mfa.logout("invalid.token.here")
        assert result is False, "Logout with invalid token should return False"

        # Also test with empty string
        result = auth_no_mfa.logout("")
        assert result is False, "Logout with empty token should return False"


# ============================================================================
# Password Management Tests
# ============================================================================


class TestPasswordChange:
    """Password change functionality."""

    def test_change_password_requires_old_password(self, auth_no_mfa):
        auth_no_mfa.register("billy", "billy@example.com", "Str0ngPass!")
        user = auth_no_mfa.user_store.get_by_username("billy")
        auth_no_mfa.change_password(user.user_id, "Str0ngPass!", "NewStr0ng!")
        # Old password should not work
        with pytest.raises(InvalidCredentialsError):
            auth_no_mfa.login("billy", "Str0ngPass!")
        # New password should work
        result = auth_no_mfa.login("billy", "NewStr0ng!")
        assert result.username == "billy", "Result must not be empty"

    def test_change_password_wrong_old_password(self, auth_no_mfa):
        auth_no_mfa.register("cora", "cora@example.com", "Str0ngPass!")
        user = auth_no_mfa.user_store.get_by_username("cora")
        with pytest.raises(InvalidCredentialsError):
            auth_no_mfa.change_password(user.user_id, "WrongPass!", "NewStr0ng!")

    def test_change_password_weak_new_password(self, auth_no_mfa):
        auth_no_mfa.register("diana", "diana@example.com", "Str0ngPass!")
        user = auth_no_mfa.user_store.get_by_username("diana")
        with pytest.raises(ValueError):
            auth_no_mfa.change_password(user.user_id, "Str0ngPass!", "weak")

    def test_change_password_same_as_old(self, auth_no_mfa):
        auth_no_mfa.register("edgar", "edgar@example.com", "Str0ngPass!")
        user = auth_no_mfa.user_store.get_by_username("edgar")
        # Should allow same password (implementation dependent)
        auth_no_mfa.change_password(user.user_id, "Str0ngPass!", "Str0ngPass!")


# ============================================================================
# Session Management Tests
# ============================================================================


class TestSessionManagement:
    """Session lifecycle and management."""

    def test_session_id_unique_per_login(self, auth_no_mfa):
        auth_no_mfa.register("fiona", "fiona@example.com", "Str0ngPass!")
        result1 = auth_no_mfa.login("fiona", "Str0ngPass!")
        result2 = auth_no_mfa.login("fiona", "Str0ngPass!")
        assert result1.session_id != result2.session_id, "Result must not be empty"

    def test_session_tokens_are_different(self, auth_no_mfa):
        auth_no_mfa.register("greg", "greg@example.com", "Str0ngPass!")
        result1 = auth_no_mfa.login("greg", "Str0ngPass!")
        result2 = auth_no_mfa.login("greg", "Str0ngPass!")
        assert result1.session_token != result2.session_token, "Result must not be empty"

    def test_access_token_valid_after_login(self, auth_no_mfa):
        auth_no_mfa.register("hannah", "hannah@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("hannah", "Str0ngPass!")
        claims = auth_no_mfa.token_manager.validate_token(
            result.access_token, expected_type=TokenType.ACCESS
        )
        assert claims.sub == result.user_id, "Result must not be empty"

    def test_refresh_token_valid_after_login(self, auth_no_mfa):
        auth_no_mfa.register("ivan", "ivan@example.com", "Str0ngPass!")
        result = auth_no_mfa.login("ivan", "Str0ngPass!")
        claims = auth_no_mfa.token_manager.validate_token(
            result.refresh_token, expected_type=TokenType.REFRESH
        )
        assert claims.sub == result.user_id, "Result must not be empty"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and edge cases."""

    def test_simultaneous_registrations(self, auth_no_mfa):
        auth_no_mfa.register("jack", "jack@example.com", "Str0ngPass!")
        with pytest.raises(UserAlreadyExistsError):
            auth_no_mfa.register("jack", "jack2@example.com", "Str0ngPass!")

    def test_user_with_special_characters_username(self, auth_no_mfa):
        # Some systems support these characters
        try:
            user = auth_no_mfa.register("kate@123", "kate@example.com", "Str0ngPass!")
            assert user.username, "Condition must be true"
        except ValueError:
            # If not supported, that's okay
            pass

    def test_very_long_username(self, auth_no_mfa):
        long_username = "a" * 255
        user = auth_no_mfa.register(long_username, "long@example.com", "Str0ngPass!")
        assert len(user.username) <= 255, "Collection must not be empty"

    def test_very_long_email(self, auth_no_mfa):
        long_email = "a" * 240 + "@example.com"
        try:
            user = auth_no_mfa.register("longmail", long_email, "Str0ngPass!")
            assert user.email, "Condition must be true"
        except ValueError:
            pass

    def test_whitespace_in_credentials(self, auth_no_mfa):
        # Username with whitespace should fail
        with pytest.raises(ValueError) as exc_info:
            auth_no_mfa.register("user name", "user@example.com", "Str0ngPass!")
        assert "username" in str(exc_info.value).lower(), "Error should reference username validation"

        # Whitespace-only username should fail
        with pytest.raises(ValueError):
            auth_no_mfa.register("   ", "user@example.com", "Str0ngPass!")

        # Email with only whitespace should fail
        with pytest.raises(ValueError):
            auth_no_mfa.register("validuser", "   ", "Str0ngPass!")

        # Valid username but whitespace-only password should fail
        with pytest.raises(ValueError):
            auth_no_mfa.register("validuser", "valid@example.com", "   ")


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration scenarios combining multiple operations."""

    def test_full_user_lifecycle(self, auth_no_mfa):
        # Register
        user = auth_no_mfa.register("lifecycle", "lifecycle@example.com", "Str0ngPass!")
        assert user.user_id, "Condition must be true"

        # Login
        result = auth_no_mfa.login("lifecycle", "Str0ngPass!")
        assert result.access_token, "Result must not be empty"

        # Change password
        auth_no_mfa.change_password(user.user_id, "Str0ngPass!", "NewPass123!")

        # Login with new password
        result = auth_no_mfa.login("lifecycle", "NewPass123!")
        assert result.user_id == user.user_id, "Result must not be empty"

        # Logout
        auth_no_mfa.logout(result.session_token)

    def test_multiple_users(self, auth_no_mfa):
        users = []
        for i in range(5):
            user = auth_no_mfa.register(f"user{i}", f"user{i}@example.com", "Str0ngPass!")
            users.append(user)

        assert len(users) == 5, "Users must not be empty"
        assert all(u.user_id for u in users), "Condition must be true"
        assert len(set(u.user_id for u in users)) == 5, "Collection must not be empty"

    def test_login_after_password_change(self, auth_no_mfa):
        auth_no_mfa.register("sarah", "sarah@example.com", "Str0ngPass!")
        user = auth_no_mfa.user_store.get_by_username("sarah")

        auth_no_mfa.change_password(user.user_id, "Str0ngPass!", "Str0ngPass2!")
        auth_no_mfa.change_password(user.user_id, "Str0ngPass2!", "Str0ngPass3!")

        result = auth_no_mfa.login("sarah", "Str0ngPass3!")
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_mixed_login_methods(self, auth_no_mfa):
        auth_no_mfa.register("thomas", "thomas@example.com", "Str0ngPass!")
        result1 = auth_no_mfa.login("thomas", "Str0ngPass!")
        result2 = auth_no_mfa.login("thomas@example.com", "Str0ngPass!")
        assert result1.user_id == result2.user_id, "Result must not be empty"
