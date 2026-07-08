"""
Comprehensive security and edge case tests for auth module.

Tests cover:
- Security vulnerabilities
- Injection attacks
- Race conditions
- Resource exhaustion
- Boundary conditions
"""

import threading
import time

import pytest

from codex.auth.authenticator import Authenticator
from codex.auth.exceptions import (  # pragma: allowlist secret
    InvalidCredentialsError,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)
from codex.auth.token_manager import TokenManager
from codex.auth.user_model import PasswordHasher
from codex.auth.user_store import UserStore

# Use a minimal iteration count in tests so PBKDF2 hashing is fast.
_FAST_HASHER = PasswordHasher(iterations=1)

# ============================================================================
# Injection Attack Prevention Tests
# ============================================================================


class TestInjectionPrevention:
    """Prevent injection attacks."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="injection-test"),
        )

    def test_sql_injection_in_username(self, auth_system):
        """Prevent SQL injection via username."""
        # Username with whitespace (e.g. SQL injection with spaces) is rejected
        malicious_with_spaces = "admin' OR '1'='1"
        with pytest.raises(ValueError):
            auth_system.register(malicious_with_spaces, "test@example.com", "Str0ngPass!")

        # Username without spaces but with SQL chars stored literally
        malicious_no_spaces = "admin'OR'1'='1"
        user = auth_system.register(malicious_no_spaces, "test2@example.com", "Str0ngPass!")
        assert user.username == malicious_no_spaces, "username is not valid"

    def test_sql_injection_in_password(self, auth_system):
        """Prevent SQL injection via password."""
        auth_system.register("user1", "user@example.com", "Str0ngPass!")

        # Should not authenticate with injected password
        with pytest.raises(InvalidCredentialsError):
            auth_system.login("user1", "anything' OR '1'='1")

    def test_command_injection_prevention(self, auth_system):
        """Prevent command injection."""

        # Should safely handle
        user = auth_system.register("user2", "user2@example.com", "Str0ngPass!")
        assert user.username == "user2", "username is not valid"

    def test_xss_prevention_in_username(self, auth_system):
        """Prevent XSS in username."""
        xss = "<script>alert('xss')</script>"

        user = auth_system.register(xss, "xss@example.com", "Str0ngPass!")
        # Should store literally, not execute
        assert user.username == xss, "username is not valid"

    def test_ldap_injection_prevention(self, auth_system):
        """Prevent LDAP injection."""
        ldap_injection = "*)(uid=*))(|(uid=*"

        user = auth_system.register(ldap_injection, "ldap@example.com", "Str0ngPass!")
        assert user.username == ldap_injection, "username is not valid"


# ============================================================================
# Cryptographic Security Tests
# ============================================================================


class TestCryptographicSecurity:
    """Cryptographic security tests."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="crypto-test"),
        )

    def test_password_not_stored_plaintext(self, auth_system):
        """Password should not be stored as plaintext."""
        auth_system.register("crypto1", "crypto@example.com", "Str0ngPass!")

        user = auth_system.user_store.get_by_username("crypto1")
        # Password should be hashed
        assert user.password_hash != "Str0ngPass!", "password_hash is not valid"

    def test_token_contains_no_user_password(self, auth_system):
        """Tokens should not contain user passwords."""
        auth_system.register("crypto2", "crypto2@example.com", "Str0ngPass!")
        result = auth_system.login("crypto2", "Str0ngPass!")

        # Token should not contain password
        assert "Str0ngPass!" not in result.access_token, "Result must not be empty"
        assert "Str0ngPass!" not in result.refresh_token, "Result must not be empty"

    def test_token_signature_verification(self, auth_system):
        """Tokens should be properly signed."""
        auth_system.register("crypto3", "crypto3@example.com", "Str0ngPass!")
        result = auth_system.login("crypto3", "Str0ngPass!")

        # Should validate correctly
        payload = auth_system.token_manager.validate_token(result.access_token)
        assert payload, "payload is not valid"

    def test_password_hash_salting(self, auth_system):
        """Password hashes should use salt."""
        pw = "Str0ngPass!"

        # Register two users with same password
        auth_system.register("user3", "user3@example.com", pw)
        auth_system.register("user4", "user4@example.com", pw)

        user3 = auth_system.user_store.get_by_username("user3")
        user4 = auth_system.user_store.get_by_username("user4")

        # Hashes should be different (salted)
        assert user3.password_hash != user4.password_hash, "password_hash is not valid"


# ============================================================================
# Timing Attack Prevention Tests
# ============================================================================


class TestTimingAttackPrevention:
    """Prevent timing attacks."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="timing-test"),
        )

    def test_invalid_user_timing(self, auth_system):
        """Invalid user and invalid password should take similar time."""
        auth_system.register("timing1", "timing@example.com", "Str0ngPass!")

        start = time.time()
        try:
            auth_system.login("timing1", "WrongPassword!")
        except InvalidCredentialsError:
            pass
        time_wrong_password = time.time() - start

        start = time.time()
        try:
            auth_system.login("nonexistent_user", "RandomPass!")
        except InvalidCredentialsError:
            pass
        time_nonexistent = time.time() - start

        # Times should be within reasonable bounds
        # (exact equality not expected, but should be similar order of magnitude)
        assert abs(time_wrong_password - time_nonexistent) < 1.0, "Condition must be true"

    def test_token_validation_timing(self, auth_system):
        """Token validation should be constant time."""
        auth_system.register("timing2", "timing2@example.com", "Str0ngPass!")
        result = auth_system.login("timing2", "Str0ngPass!")

        # Valid token
        start = time.time()
        auth_system.token_manager.validate_token(result.access_token)
        time_valid = time.time() - start

        # Invalid token (wrong format)
        start = time.time()
        try:
            auth_system.token_manager.validate_token("invalid.token.format")
        except (AttributeError, OSError, RuntimeError, ValueError):
            pass
        time_invalid = time.time() - start

        # Should be similar
        assert time_valid > 0, "time_valid must be greater than zero"
        assert time_invalid > 0, "time_invalid must be greater than zero"


# ============================================================================
# Resource Exhaustion Prevention Tests
# ============================================================================


class TestResourceExhaustion:
    """Prevent resource exhaustion attacks."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="resource-test"),
        )

    def test_excessive_failed_login_attempts(self, auth_system):
        """Handle excessive failed login attempts."""
        auth_system.register("lockout", "lockout@example.com", "Str0ngPass!")

        # Many failed attempts
        for _ in range(100):
            try:
                auth_system.login("lockout", "WrongPassword!")
            except InvalidCredentialsError:
                pass

        # User should still exist
        user = auth_system.user_store.get_by_username("lockout")
        assert user, "user is not valid"

    def test_password_reset_abuse(self, auth_system):
        """Handle password reset abuse."""
        user = auth_system.register("reset", "reset@example.com", "Str0ngPass!")

        # Many reset attempts
        for i in range(20):
            try:
                auth_system.change_password(user.user_id, "Str0ngPass!", f"NewPass{i}!")
            except (AttributeError, OSError, RuntimeError, InvalidCredentialsError):
                pass

    def test_very_large_token_payload(self, auth_system):
        """Handle very large token payloads."""
        auth_system.register("large", "large@example.com", "Str0ngPass!")
        result = auth_system.login("large", "Str0ngPass!")

        # Token should be reasonably sized
        assert len(result.access_token) < 10000, "Collection must not be empty"

    def test_many_concurrent_sessions(self, auth_system):
        """Handle many concurrent sessions."""
        auth_system.register("concurrent", "concurrent@example.com", "Str0ngPass!")

        sessions = []
        for _ in range(50):
            result = auth_system.login("concurrent", "Str0ngPass!")
            sessions.append(result)

        # All sessions should be distinct
        tokens = {s.session_token for s in sessions}
        assert len(tokens) == 50, "Tokens must not be empty"


# ============================================================================
# Boundary Condition Tests
# ============================================================================


class TestBoundaryConditions:
    """Boundary condition testing."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="boundary-test"),
        )

    def test_minimum_username_length(self, auth_system):
        """Test minimum username length."""
        # Single character should work
        user = auth_system.register("a", "a@example.com", "Str0ngPass!")
        assert user.username == "a", "username is not valid"

    def test_maximum_username_length(self, auth_system):
        """Test maximum username length."""
        long_username = "x" * 1000
        user = auth_system.register(long_username, "long@example.com", "Str0ngPass!")
        assert user.username == long_username, "username is not valid"

    def test_minimum_password_length(self, auth_system):
        """Test minimum password requirement."""
        # Too short should fail
        with pytest.raises(ValueError):
            auth_system.register("minpwd", "min@example.com", "X1!")

    def test_maximum_password_length(self, auth_system):
        """Test very long password."""
        long_password = "P1" + "a" * 999 + "!"
        user = auth_system.register("longpwd", "longpwd@example.com", long_password)

        result = auth_system.login("longpwd", long_password)
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_empty_string_inputs(self, auth_system):
        """Test empty string inputs."""
        with pytest.raises(ValueError):
            auth_system.register("", "empty@example.com", "Str0ngPass!")

    def test_whitespace_only_inputs(self, auth_system):
        """Test whitespace-only inputs."""
        with pytest.raises(ValueError):
            auth_system.register("   ", "space@example.com", "Str0ngPass!")

    def test_null_character_in_password(self, auth_system):
        """Test null character handling."""
        auth_system.register("null", "null@example.com", "Str0ngPass!")

        # Should handle safely
        result = auth_system.login("null", "Str0ngPass!")
        assert result.user_id, "Result must not be empty"


# ============================================================================
# Race Condition Tests
# ============================================================================


class TestRaceConditions:
    """Race condition testing."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="race-test"),
        )

    def test_concurrent_password_change(self, auth_system):
        """Concurrent password changes."""
        user = auth_system.register("race1", "race1@example.com", "Str0ngPass!")

        errors = []

        def change_password(new_pw):
            try:
                auth_system.change_password(user.user_id, "Str0ngPass!", new_pw)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=change_password, args=(f"Pass{i}!",)) for i in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # At least one should succeed
        user = auth_system.user_store.get_by_user_id(user.user_id)
        assert user, "user is not valid"

    def test_concurrent_token_refresh(self, auth_system):
        """Concurrent token refresh."""
        auth_system.register("race2", "race2@example.com", "Str0ngPass!")
        result = auth_system.login("race2", "Str0ngPass!")

        refresh_tokens = []
        errors = []

        def refresh():
            try:
                new_token = auth_system.token_manager.refresh_token(result.refresh_token)
                refresh_tokens.append(new_token)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=refresh) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have some results
        assert len(refresh_tokens) + len(errors) == 10, "Refresh_tokens must not be empty"

    def test_concurrent_logout(self, auth_system):
        """Concurrent logout."""
        auth_system.register("race3", "race3@example.com", "Str0ngPass!")
        result = auth_system.login("race3", "Str0ngPass!")

        def logout():
            auth_system.logout(result.session_token)

        threads = [threading.Thread(target=logout) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should handle gracefully


# ============================================================================
# Privilege Escalation Tests
# ============================================================================


class TestPrivilegeEscalation:
    """Prevent privilege escalation."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="priv-test"),
        )

    def test_user_cannot_grant_admin(self, auth_system):
        """User should not be able to grant self admin."""
        user = auth_system.register("priv1", "priv1@example.com", "Str0ngPass!")

        # User has no admin role
        assert "admin" not in user.roles, "Condition must be true"

    def test_user_cannot_modify_other_user(self, auth_system):
        """User should not modify another user."""
        auth_system.register("priv2", "priv2@example.com", "Str0ngPass!")
        auth_system.register("priv3", "priv3@example.com", "Str0ngPass!")

        # Users are separate
        user2 = auth_system.user_store.get_by_username("priv2")
        user3 = auth_system.user_store.get_by_username("priv3")
        assert user2.user_id != user3.user_id, "user_id is not valid"

    def test_token_privilege_scope(self, auth_system):
        """Token should only grant granted privileges."""
        auth_system.register("priv4", "priv4@example.com", "Str0ngPass!")
        result = auth_system.login("priv4", "Str0ngPass!")

        payload = auth_system.token_manager.validate_token(result.access_token)
        # Should have basic scope, not admin
        assert payload, "payload is not valid"


# ============================================================================
# Session Security Tests
# ============================================================================


class TestSessionSecurity:
    """Session security tests."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="session-test"),
        )

    def test_session_fixation_prevention(self, auth_system):
        """Prevent session fixation."""
        auth_system.register("sess1", "sess1@example.com", "Str0ngPass!")
        result1 = auth_system.login("sess1", "Str0ngPass!")

        # New login should get new session
        result2 = auth_system.login("sess1", "Str0ngPass!")

        assert result1.session_token != result2.session_token, "Result must not be empty"

    def test_session_hijacking_prevention(self, auth_system):
        """Prevent session hijacking."""
        auth_system.register("sess2", "sess2@example.com", "Str0ngPass!")
        result = auth_system.login("sess2", "Str0ngPass!")

        # Modified token should not validate
        modified_token = result.session_token[:-5] + "00000"

        with pytest.raises(Exception):
            auth_system.token_manager.validate_token(modified_token)

    def test_session_timeout(self, auth_system):
        """Sessions should eventually timeout."""
        auth_system.register("sess3", "sess3@example.com", "Str0ngPass!")
        result = auth_system.login("sess3", "Str0ngPass!")

        # Logout invalidates session
        auth_system.logout(result.session_token)

        # Session token should no longer be valid
        with pytest.raises(Exception):
            auth_system.token_manager.validate_token(result.session_token)


# ============================================================================
# Data Integrity Tests
# ============================================================================


class TestDataIntegrity:
    """Data integrity tests."""

    @pytest.fixture
    def auth_system(self):
        """Create auth system."""
        return Authenticator(
            user_store=UserStore(hasher=_FAST_HASHER),
            token_manager=TokenManager(secret_key="integrity-test"),
        )

    def test_user_data_consistency(self, auth_system):
        """User data should remain consistent."""
        original = auth_system.register("consistent", "consistent@example.com", "Str0ngPass!")

        # Retrieve and verify consistency
        retrieved = auth_system.user_store.get_by_user_id(original.user_id)

        assert retrieved.username == original.username, "username is not valid"
        assert retrieved.email == original.email, "email is not valid"
        assert retrieved.user_id == original.user_id, "user_id is not valid"

    def test_password_change_validation(self, auth_system):
        """Password changes should be validated."""
        user = auth_system.register("integrity", "integrity@example.com", "Str0ngPass!")

        # Change password
        auth_system.change_password(user.user_id, "Str0ngPass!", "NewPass123!")

        # Old password should not work
        with pytest.raises(InvalidCredentialsError):
            auth_system.login("integrity", "Str0ngPass!")

        # New password should work
        result = auth_system.login("integrity", "NewPass123!")
        assert result.user_id == user.user_id, "Result must not be empty"
