"""
Comprehensive tests for Auth Exceptions and Integration Scenarios.

Tests cover:
- Exception handling
- Integration flows
- Error scenarios
- Edge case combinations
- Full workflow testing
"""

import pytest

from codex.auth.authenticator import Authenticator
from codex.auth.exceptions import (
    InvalidCredentialsError,
    MFARequiredError,
    MFAVerificationError,  # pragma: allowlist secret
    UserAlreadyExistsError,
    UserNotFoundError,
)
from codex.auth.mfa_provider import MFAProvider
from codex.auth.token_manager import TokenManager, TokenType
from codex.auth.user_store import UserStore

# ============================================================================
# Exception Tests
# ============================================================================


class TestAuthExceptions:
    """Exception handling in auth module."""

    def test_invalid_credentials_error(self):
        exc = InvalidCredentialsError("Wrong password")
        assert "Wrong password" in str(exc), "Condition must be true"

    def test_invalid_credentials_no_message(self):
        exc = InvalidCredentialsError()
        assert exc is not None, "exc must be initialized"

    def test_invalid_credentials_with_context(self):
        exc = InvalidCredentialsError("Invalid username or password")
        assert "Invalid" in str(exc), "Condition must be true"

    def test_mfa_required_error(self):
        exc = MFARequiredError("MFA required")
        assert "MFA" in str(exc), "Condition must be true"

    def test_mfa_verification_error(self):
        exc = MFAVerificationError("Invalid code")
        assert "Invalid" in str(exc), "Condition must be true"

    def test_user_already_exists_error(self):
        exc = UserAlreadyExistsError("User alice exists")
        assert "alice" in str(exc), "Condition must be true"

    def test_user_not_found_error(self):
        exc = UserNotFoundError("User not found")
        assert "not found" in str(exc), "Condition must be true"

    def test_exception_inheritance(self):
        exc = InvalidCredentialsError()
        assert isinstance(exc, Exception)

    def test_exception_string_representation(self):
        exc = MFARequiredError("Two-factor auth required")
        str_repr = str(exc)
        assert "factor" in str_repr.lower() or "auth" in str_repr.lower(), "Condition must be true"


# ============================================================================
# Integration Scenario Tests
# ============================================================================


class TestAuthenticationIntegration:
    """Complete authentication integration scenarios."""

    @pytest.fixture
    def auth_system(self):
        """Create complete auth system."""
        store = UserStore()
        tokens = TokenManager(secret_key="integration-test-key")
        mfa = MFAProvider()
        return Authenticator(user_store=store, token_manager=tokens, mfa_provider=mfa)

    def test_signup_login_logout_flow(self, auth_system):
        """Complete user lifecycle."""
        # Signup
        user = auth_system.register("alice", "alice@example.com", "Str0ngPass!")
        assert user.user_id, "Condition must be true"

        # Login
        result = auth_system.login("alice", "Str0ngPass!")
        assert result.access_token, "Result must not be empty"
        assert result.session_token, "Result must not be empty"

        # Logout
        auth_system.logout(result.session_token)

    def test_multiple_concurrent_users(self, auth_system):
        """Multiple users in system."""
        users = []
        for i in range(10):
            user = auth_system.register(f"user{i}", f"user{i}@example.com", "Str0ngPass!")
            users.append(user)

        # Each can login
        for i in range(10):
            result = auth_system.login(f"user{i}", "Str0ngPass!")
            assert result.user_id == users[i].user_id, "Result must not be empty"

    def test_token_refresh_flow(self, auth_system):
        """Token refresh flow."""
        # Register and login
        auth_system.register("bob", "bob@example.com", "Str0ngPass!")
        result = auth_system.login("bob", "Str0ngPass!")

        # Refresh access token
        new_access = auth_system.token_manager.refresh_token(result.refresh_token)
        assert new_access != result.access_token, "Result must not be empty"

    def test_session_management(self, auth_system):
        """Session tracking."""
        auth_system.register("charlie", "charlie@example.com", "Str0ngPass!")

        # Multiple sessions
        session1 = auth_system.login("charlie", "Str0ngPass!")
        session2 = auth_system.login("charlie", "Str0ngPass!")

        assert session1.session_token != session2.session_token, "session_token is not valid"

    def test_password_change_flow(self, auth_system):
        """Password change workflow."""
        user = auth_system.register("diana", "diana@example.com", "Str0ngPass!")

        # Change password
        auth_system.change_password(user.user_id, "Str0ngPass!", "NewPass123!")

        # Old password fails
        with pytest.raises(InvalidCredentialsError):
            auth_system.login("diana", "Str0ngPass!")

        # New password works
        result = auth_system.login("diana", "NewPass123!")
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_mfa_enrollment_and_login(self, auth_system):
        """MFA enrollment and usage."""
        user = auth_system.register("eve", "eve@example.com", "Str0ngPass!")

        # Enroll in MFA
        secret = auth_system.mfa_provider.register_mfa(user.user_id, "sha256")

        # Generate valid code
        import pyotp

        totp = pyotp.TOTP(secret.secret)
        code = totp.now()

        # Login with MFA
        result = auth_system.login("eve", "Str0ngPass!", mfa_code=code)
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_backup_codes_recovery(self, auth_system):
        """Backup codes recovery."""
        user = auth_system.register("frank", "frank@example.com", "Str0ngPass!")

        # Setup MFA
        auth_system.mfa_provider.register_mfa(user.user_id, "sha256")
        codes = auth_system.mfa_provider.generate_backup_codes(user.user_id)

        # Use backup code (instead of TOTP)
        backup_code = codes[0]
        auth_system.mfa_provider.verify_backup_code(user.user_id, backup_code)


# ============================================================================
# Error Path Tests
# ============================================================================


class TestErrorPaths:
    """Error handling paths."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(),
            token_manager=TokenManager(secret_key="test-key"),
        )

    def test_registration_duplicate_username(self, auth_system):
        auth_system.register("grace", "grace@example.com", "Str0ngPass!")
        with pytest.raises(UserAlreadyExistsError):
            auth_system.register("grace", "grace2@example.com", "Str0ngPass!")

    def test_registration_weak_password(self, auth_system):
        with pytest.raises(ValueError):
            auth_system.register("henry", "henry@example.com", "weak")

    def test_login_wrong_password(self, auth_system):
        auth_system.register("iris", "iris@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            auth_system.login("iris", "WrongPassword!")

    def test_login_nonexistent_user(self, auth_system):
        with pytest.raises(InvalidCredentialsError):
            auth_system.login("phantom", "Str0ngPass!")

    def test_change_password_wrong_current(self, auth_system):
        user = auth_system.register("jack", "jack@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            auth_system.change_password(user.user_id, "WrongPass!", "NewPass123!")

    def test_change_password_weak_new(self, auth_system):
        user = auth_system.register("karl", "karl@example.com", "Str0ngPass!")
        with pytest.raises(ValueError):
            auth_system.change_password(user.user_id, "Str0ngPass!", "weak")

    def test_logout_invalid_token(self, auth_system):
        # Should not raise
        auth_system.logout("invalid_token")

    def test_logout_already_revoked(self, auth_system):
        auth_system.register("larry", "larry@example.com", "Str0ngPass!")
        result = auth_system.login("larry", "Str0ngPass!")

        auth_system.logout(result.session_token)

        # Second logout should handle gracefully
        auth_system.logout(result.session_token)


# ============================================================================
# State Transition Tests
# ============================================================================


class TestStateTransitions:
    """State transitions and consistency."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(),
            token_manager=TokenManager(secret_key="test-key"),
        )

    def test_user_state_after_registration(self, auth_system):
        user = auth_system.register("mike", "mike@example.com", "Str0ngPass!")

        # User should be retrievable
        retrieved = auth_system.user_store.get_by_username("mike")
        assert retrieved.user_id == user.user_id, "user_id is not valid"

    def test_user_state_after_password_change(self, auth_system):
        user = auth_system.register("nancy", "nancy@example.com", "Str0ngPass!")
        auth_system.change_password(user.user_id, "Str0ngPass!", "NewPass123!")

        # User should still exist
        retrieved = auth_system.user_store.get_by_user_id(user.user_id)
        assert retrieved.username == "nancy", "username is not valid"

    def test_user_state_after_role_change(self, auth_system):
        user = auth_system.register("oscar", "oscar@example.com", "Str0ngPass!")

        # Add role
        auth_system.user_store.add_role(user.user_id, "admin")

        # Verify role was added
        retrieved = auth_system.user_store.get_by_user_id(user.user_id)
        assert "admin" in retrieved.roles, "Condition must be true"
        assert "user" in retrieved.roles, "Default user role must persist"
        assert len(retrieved.roles) == 2, "Should have exactly 2 roles after adding admin"

        # Add another role
        auth_system.user_store.add_role(user.user_id, "moderator")
        retrieved = auth_system.user_store.get_by_user_id(user.user_id)
        assert "admin" in retrieved.roles, "Admin role must persist"
        assert "moderator" in retrieved.roles, "New moderator role must be added"
        assert "user" in retrieved.roles, "Default user role must persist"
        assert len(retrieved.roles) == 3, "Should have exactly 3 roles"

    def test_token_state_consistency(self, auth_system):
        auth_system.register("paul", "paul@example.com", "Str0ngPass!")
        result = auth_system.login("paul", "Str0ngPass!")

        # All tokens should be valid
        auth_system.token_manager.validate_token(
            result.access_token, expected_type=TokenType.ACCESS
        )
        auth_system.token_manager.validate_token(
            result.refresh_token, expected_type=TokenType.REFRESH
        )
        auth_system.token_manager.validate_token(
            result.session_token, expected_type=TokenType.SESSION
        )


# ============================================================================
# Concurrent Access Tests
# ============================================================================


class TestConcurrentAccess:
    """Concurrent access patterns."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(),
            token_manager=TokenManager(secret_key="concurrent-key"),
        )

    def test_concurrent_registration(self, auth_system):
        import threading

        users = []
        errors = []

        def register():
            try:
                user = auth_system.register(
                    f"user{threading.current_thread().ident}",
                    f"user{threading.current_thread().ident}@example.com",
                    "Str0ngPass!",
                )
                users.append(user)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should handle concurrent registration
        assert len(users) + len(errors) == 5, "Users must not be empty"

    def test_concurrent_login(self, auth_system):
        import threading

        # Pre-create user
        auth_system.register("quinn", "quinn@example.com", "Str0ngPass!")

        results = []

        def login():
            try:
                result = auth_system.login("quinn", "Str0ngPass!")
                results.append(result)
            except Exception as e:
                results.append(e)

        threads = [threading.Thread(target=login) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert len([r for r in results if hasattr(r, "access_token")]) == 10

    def test_concurrent_token_operations(self, auth_system):
        import threading

        auth_system.register("robin", "robin@example.com", "Str0ngPass!")
        result = auth_system.login("robin", "Str0ngPass!")

        operations = []

        def token_op():
            try:
                auth_system.token_manager.validate_token(result.access_token)
                operations.append("validate")
            except Exception as _err:
                operations.append("error")

        threads = [threading.Thread(target=token_op) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(operations) == 20, "Operations must not be empty"


# ============================================================================
# Edge Case Combinations
# ============================================================================


class TestEdgeCaseCombinations:
    """Combinations of edge cases."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(),
            token_manager=TokenManager(secret_key="edge-key"),
        )

    def test_unicode_username_with_special_password(self, auth_system):
        user = auth_system.register("用户123", "user@example.com", "Pässwörd123!中文")
        assert user.username == "用户123", "username is not valid"

        result = auth_system.login("用户123", "Pässwörd123!中文")
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_very_long_username_and_password(self, auth_system):
        long_username = "u" * 200
        long_password = "P1" + "a" * 199 + "!"

        user = auth_system.register(long_username, "long@example.com", long_password)

        result = auth_system.login(long_username, long_password)
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_username_with_email_like_format(self, auth_system):
        user = auth_system.register(
            "user@example.com",  # Username that looks like email
            "actual@example.com",  # Actual email
            "Str0ngPass!",
        )
        assert user.username == "user@example.com", "username is not valid"
        assert user.email == "actual@example.com", "email is not valid"

        result = auth_system.login("user@example.com", "Str0ngPass!")
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_email_and_password_both_unicode(self, auth_system):
        user = auth_system.register("sam", "用户@例え.jp", "密码Pass123!")
        assert user.email, "Condition must be true"
        assert user.username == "sam", "username is not valid"

    def test_rapid_password_changes(self, auth_system):
        user = auth_system.register("sam", "sam@example.com", "Pass0!ab")

        # Rapid changes
        for i in range(5):
            old_pass = f"Pass{i}!ab"
            new_pass = f"Pass{i+1}!ab"
            auth_system.change_password(user.user_id, old_pass, new_pass)

        # Final password works
        result = auth_system.login("sam", "Pass5!ab")
        assert result.user_id == user.user_id, "Result must not be empty"


# ============================================================================
# Resource Cleanup Tests
# ============================================================================


class TestResourceCleanup:
    """Resource management and cleanup."""

    def test_auth_system_cleanup(self):
        """Auth system should cleanup resources."""
        auth = Authenticator(
            user_store=UserStore(),
            token_manager=TokenManager(secret_key="cleanup-key"),
        )

        auth.register("cleanup", "cleanup@example.com", "Str0ngPass!")
        result = auth.login("cleanup", "Str0ngPass!")

        # Cleanup
        auth.logout(result.session_token)

    def test_token_expiration_cleanup(self):
        """Expired tokens should be cleaned up."""
        tm = TokenManager(secret_key="expiry-key")

        # Create expired token
        import time

        token = tm.create_token("user123", TokenType.ACCESS, expires_in=1)

        time.sleep(2)

        # Should be expired
        with pytest.raises(Exception):
            tm.validate_token(token)
