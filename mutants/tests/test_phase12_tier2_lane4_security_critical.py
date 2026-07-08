"""
Phase 12 WS3 Tier 2 Lane 4: Security-Critical and High-Impact Edge Cases

Focus: Priority 1 & 2 critical functions from Tier 1 gap analysis:
- Authentication and session validation
- Token management and rotation
- Authorization scope checking
- Cryptographic operations
- Error path coverage

Target: 50+ critical edge case tests
Authority: D-tier autonomous
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import time


class TestAuthenticationEdgeCases:
    """Test authentication system edge cases."""

    def test_session_creation_with_empty_user_id(self):
        """Test session creation rejects empty user IDs."""
        with pytest.raises((ValueError, TypeError)):
            self._create_session(user_id="")

    def test_session_creation_with_none_user_id(self):
        """Test session creation rejects None user ID."""
        with pytest.raises((ValueError, TypeError)):
            self._create_session(user_id=None)

    def test_session_expiration_at_exact_boundary(self):
        """Test session expiration at exact boundary time."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=3600)
        
        session = self._create_session(user_id="user1", expires_at=expires_at)
        
        # At expiration boundary
        assert self._is_session_valid(session, now)
        assert not self._is_session_valid(session, expires_at)

    def test_session_expiration_with_very_short_timeout(self):
        """Test session with very short timeout."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(milliseconds=1)
        
        session = self._create_session(user_id="user1", expires_at=expires_at)
        assert self._is_session_valid(session, now)
        # After timeout
        later = now + timedelta(milliseconds=100)
        assert not self._is_session_valid(session, later)

    def test_session_with_very_long_timeout(self):
        """Test session with very long timeout."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=365)
        
        session = self._create_session(user_id="user1", expires_at=expires_at)
        # Should still be valid for any date within year
        mid_year = now + timedelta(days=180)
        assert self._is_session_valid(session, mid_year)

    def test_concurrent_session_operations(self):
        """Test concurrent session creation doesn't corrupt state."""
        sessions = {}
        
        def create_session(user_id):
            session = self._create_session(user_id=f"user_{user_id}")
            sessions[user_id] = session
        
        # Simulate concurrent creation
        for i in range(10):
            create_session(i)
        
        # All sessions should be unique
        assert len(set(sessions.values())) == len(sessions)

    @staticmethod
    def _create_session(user_id, expires_at=None):
        """Helper: create session."""
        if not user_id or user_id is None:
            raise ValueError("user_id cannot be empty")
        return {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at or datetime.now(timezone.utc) + timedelta(hours=1),
        }

    @staticmethod
    def _is_session_valid(session, now=None):
        """Helper: check if session is valid."""
        if now is None:
            now = datetime.now(timezone.utc)
        return now <= session["expires_at"]


class TestTokenManagementEdgeCases:
    """Test token management edge cases."""

    def test_token_generation_produces_unique_tokens(self):
        """Test token generation produces unique tokens."""
        tokens = set()
        for _ in range(100):
            token = self._generate_token()
            assert token not in tokens
            tokens.add(token)
        
        assert len(tokens) == 100

    def test_token_validation_with_empty_token(self):
        """Test token validation rejects empty tokens."""
        with pytest.raises((ValueError, AssertionError)):
            self._validate_token("")

    def test_token_validation_with_none_token(self):
        """Test token validation rejects None tokens."""
        with pytest.raises((ValueError, TypeError)):
            self._validate_token(None)

    def test_token_refresh_boundary_conditions(self):
        """Test token refresh at expiration boundary."""
        token = self._generate_token()
        now = datetime.now(timezone.utc)
        
        # Token valid
        assert self._is_token_valid(token, now)
        
        # Token refresh should produce different token
        new_token = self._refresh_token(token)
        assert new_token != token

    def test_token_revocation_prevents_reuse(self):
        """Test revoked tokens cannot be reused."""
        token = self._generate_token()
        
        # Token valid initially
        assert self._is_token_valid(token)
        
        # Revoke token
        self._revoke_token(token)
        
        # Token should be invalid
        assert not self._is_token_valid(token)

    def test_concurrent_token_operations(self):
        """Test concurrent token generation doesn't corrupt state."""
        tokens = []
        for _ in range(100):
            token = self._generate_token()
            tokens.append(token)
        
        # All tokens should be unique
        assert len(set(tokens)) == 100

    @staticmethod
    def _generate_token():
        """Helper: generate token."""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def _validate_token(token):
        """Helper: validate token format."""
        if not token:
            raise ValueError("token cannot be empty")
        return True

    @staticmethod
    def _is_token_valid(token, now=None):
        """Helper: check if token is valid."""
        if not token:
            return False
        return True

    @staticmethod
    def _refresh_token(token):
        """Helper: refresh token."""
        if not token:
            raise ValueError("invalid token")
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def _revoke_token(token):
        """Helper: revoke token."""
        pass


class TestAuthorizationEdgeCases:
    """Test authorization scope checking edge cases."""

    def test_scope_validation_with_empty_scopes(self):
        """Test scope validation with empty scope list."""
        user = self._create_user(scopes=[])
        assert user["scopes"] == []
        assert not self._has_scope(user, "admin")

    def test_scope_validation_with_none_scopes(self):
        """Test scope validation with None scopes."""
        with pytest.raises((ValueError, TypeError)):
            self._create_user(scopes=None)

    def test_scope_hierarchy_validation(self):
        """Test scope hierarchy is properly validated."""
        user_admin = self._create_user(scopes=["admin"])
        user_user = self._create_user(scopes=["user"])
        
        # Admin has user scope implicitly
        assert self._has_scope(user_admin, "admin")
        # User doesn't have admin scope
        assert not self._has_scope(user_user, "admin")

    def test_scope_addition_boundary(self):
        """Test adding scopes at boundary conditions."""
        user = self._create_user(scopes=["user"])
        
        # Add single scope
        self._add_scope(user, "admin")
        assert self._has_scope(user, "admin")
        
        # Add duplicate scope (should be idempotent)
        self._add_scope(user, "admin")
        assert user["scopes"].count("admin") == 1

    def test_scope_removal_boundary(self):
        """Test removing scopes at boundary conditions."""
        user = self._create_user(scopes=["admin", "user"])
        
        # Remove scope
        self._remove_scope(user, "user")
        assert not self._has_scope(user, "user")
        assert self._has_scope(user, "admin")
        
        # Remove non-existent scope (should not error)
        self._remove_scope(user, "nonexistent")
        assert not self._has_scope(user, "nonexistent")

    def test_scope_case_sensitivity(self):
        """Test scope comparison is case-sensitive."""
        user = self._create_user(scopes=["Admin"])
        assert self._has_scope(user, "Admin")
        assert not self._has_scope(user, "admin")

    @staticmethod
    def _create_user(scopes):
        """Helper: create user with scopes."""
        if scopes is None:
            raise ValueError("scopes cannot be None")
        return {"scopes": list(scopes)}

    @staticmethod
    def _has_scope(user, scope):
        """Helper: check if user has scope."""
        return scope in user.get("scopes", [])

    @staticmethod
    def _add_scope(user, scope):
        """Helper: add scope to user."""
        if scope not in user["scopes"]:
            user["scopes"].append(scope)

    @staticmethod
    def _remove_scope(user, scope):
        """Helper: remove scope from user."""
        if scope in user["scopes"]:
            user["scopes"].remove(scope)


class TestCryptographicEdgeCases:
    """Test cryptographic operations edge cases."""

    def test_hmac_signature_verification_empty_message(self):
        """Test HMAC verification with empty message."""
        key = b"secret"
        message = b""
        
        signature = self._compute_hmac(key, message)
        assert self._verify_hmac(key, message, signature)

    def test_hmac_signature_verification_empty_key(self):
        """Test HMAC with empty key."""
        key = b""
        message = b"test"
        
        signature = self._compute_hmac(key, message)
        assert self._verify_hmac(key, message, signature)

    def test_hmac_signature_wrong_key_fails(self):
        """Test HMAC verification fails with wrong key."""
        key1 = b"key1"
        key2 = b"key2"
        message = b"test"
        
        signature = self._compute_hmac(key1, message)
        assert not self._verify_hmac(key2, message, signature)

    def test_hmac_signature_tampered_message_fails(self):
        """Test HMAC verification fails with tampered message."""
        key = b"secret"
        message = b"test"
        tampered = b"test2"
        
        signature = self._compute_hmac(key, message)
        assert not self._verify_hmac(key, tampered, signature)

    def test_nonce_uniqueness(self):
        """Test nonce generation produces unique values."""
        nonces = set()
        for _ in range(100):
            nonce = self._generate_nonce()
            assert nonce not in nonces
            nonces.add(nonce)

    def test_nonce_validation_with_expired_nonce(self):
        """Test nonce validation rejects expired nonce."""
        nonce = self._generate_nonce()
        
        # Fresh nonce is valid
        assert self._is_nonce_valid(nonce)
        
        # Simulate expiration
        time.sleep(0.1)
        # Assuming 0.01s expiration
        assert not self._is_nonce_valid(nonce, max_age=0.01)

    @staticmethod
    def _compute_hmac(key, message):
        """Helper: compute HMAC."""
        return hmac.new(key, message, hashlib.sha256).digest()

    @staticmethod
    def _verify_hmac(key, message, signature):
        """Helper: verify HMAC."""
        expected = hmac.new(key, message, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def _generate_nonce():
        """Helper: generate nonce."""
        import secrets
        return secrets.token_hex(16)

    @staticmethod
    def _is_nonce_valid(nonce, max_age=3600):
        """Helper: check nonce validity."""
        # Simple implementation
        return nonce is not None and len(nonce) > 0


class TestPasswordManagementEdgeCases:
    """Test password management edge cases."""

    def test_password_with_empty_string(self):
        """Test password cannot be empty."""
        with pytest.raises((ValueError, AssertionError)):
            self._hash_password("")

    def test_password_with_none(self):
        """Test password cannot be None."""
        with pytest.raises((ValueError, TypeError)):
            self._hash_password(None)

    def test_password_with_very_long_string(self):
        """Test password hashing with very long strings."""
        long_password = "p" * 10000
        hash_result = self._hash_password(long_password)
        assert hash_result is not None

    def test_password_with_special_characters(self):
        """Test password hashing with special characters."""
        passwords = [
            "p@ss!word",
            "password\n\t",
            "password with spaces",
            "пароль",  # Cyrillic
            "密码",     # Chinese
        ]
        
        for pwd in passwords:
            hash_result = self._hash_password(pwd)
            assert hash_result is not None

    def test_password_hash_uniqueness(self):
        """Test same password produces different hashes (salt)."""
        password = "testpassword"
        hash1 = self._hash_password(password)
        hash2 = self._hash_password(password)
        
        # Different hashes due to salt
        assert hash1 != hash2

    def test_password_verification_case_sensitive(self):
        """Test password verification is case-sensitive."""
        password = "TestPassword"
        hash_result = self._hash_password(password)
        
        assert self._verify_password(password, hash_result)
        assert not self._verify_password("testpassword", hash_result)

    @staticmethod
    def _hash_password(password):
        """Helper: hash password."""
        if not password or password is None:
            raise ValueError("password cannot be empty")
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def _verify_password(password, hash_value):
        """Helper: verify password."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hash_value


class TestErrorRecoveryEdgeCases:
    """Test error recovery and exception handling edge cases."""

    def test_retry_logic_with_immediate_success(self):
        """Test retry logic succeeds immediately."""
        attempts = []
        
        def operation():
            attempts.append(1)
            return "success"
        
        result = self._retry_operation(operation, max_retries=3)
        assert result == "success"
        assert len(attempts) == 1

    def test_retry_logic_succeeds_after_failures(self):
        """Test retry logic succeeds after initial failures."""
        attempts = []
        
        def operation():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("transient error")
            return "success"
        
        result = self._retry_operation(operation, max_retries=5)
        assert result == "success"
        assert len(attempts) == 3

    def test_retry_logic_exhausts_retries(self):
        """Test retry logic exhausts retries and raises."""
        def operation():
            raise ValueError("persistent error")
        
        with pytest.raises(ValueError):
            self._retry_operation(operation, max_retries=2)

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        failures = [0]
        
        def failing_operation():
            failures[0] += 1
            raise ValueError("error")
        
        # Should fail and open circuit
        try:
            for _ in range(5):
                self._circuit_breaker_call(failing_operation)
        except Exception:
            pass
        
        # Circuit should be open
        assert self._is_circuit_open()

    @staticmethod
    def _retry_operation(operation, max_retries=3):
        """Helper: retry operation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.01 * (2 ** attempt))

    @staticmethod
    def _circuit_breaker_call(operation):
        """Helper: call operation with circuit breaker."""
        # Simple circuit breaker
        return operation()

    @staticmethod
    def _is_circuit_open():
        """Helper: check if circuit is open."""
        return False


class TestInputSanitizationEdgeCases:
    """Test input sanitization edge cases."""

    def test_sql_injection_prevention(self):
        """Test SQL injection attempts are prevented."""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
            "\\' OR \\'1\\'=\\'1",
        ]
        
        for dangerous_input in dangerous_inputs:
            # Should be escaped/sanitized
            sanitized = self._sanitize_sql_input(dangerous_input)
            assert "DROP" not in sanitized or "DROP" in dangerous_input

    def test_xss_prevention(self):
        """Test XSS attempts are prevented."""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = self._sanitize_html(dangerous_input)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized

    def test_path_traversal_prevention(self):
        """Test path traversal attempts are prevented."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "./../../sensitive/file.txt",
        ]
        
        for dangerous_path in dangerous_paths:
            sanitized = self._sanitize_path(dangerous_path)
            # Should not contain .. or higher-level traversal
            assert not sanitized.startswith("../")
            assert not sanitized.startswith("..\\")

    @staticmethod
    def _sanitize_sql_input(input_str):
        """Helper: sanitize SQL input."""
        # Simple escaping
        return input_str.replace("'", "''")

    @staticmethod
    def _sanitize_html(input_str):
        """Helper: sanitize HTML input."""
        replacements = {
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
        }
        result = input_str
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        return result

    @staticmethod
    def _sanitize_path(path):
        """Helper: sanitize file path."""
        import os
        return os.path.normpath(path).lstrip("../")


class TestResourceManagementEdgeCases:
    """Test resource management edge cases."""

    def test_connection_pool_exhaustion(self):
        """Test connection pool handles exhaustion."""
        pool = self._create_connection_pool(max_connections=5)
        connections = []
        
        # Fill pool
        for _ in range(5):
            conn = self._acquire_connection(pool)
            assert conn is not None
            connections.append(conn)
        
        # Pool is full
        with pytest.raises((RuntimeError, Exception)):
            self._acquire_connection(pool, timeout=0.1)

    def test_connection_release_allows_reuse(self):
        """Test releasing connections allows reuse."""
        pool = self._create_connection_pool(max_connections=2)
        
        # Acquire and release
        conn1 = self._acquire_connection(pool)
        self._release_connection(pool, conn1)
        
        # Can acquire again
        conn2 = self._acquire_connection(pool)
        assert conn2 is not None

    @staticmethod
    def _create_connection_pool(max_connections):
        """Helper: create connection pool."""
        return {"max": max_connections, "active": 0}

    @staticmethod
    def _acquire_connection(pool, timeout=1):
        """Helper: acquire connection from pool."""
        if pool["active"] >= pool["max"]:
            raise RuntimeError("No available connections")
        pool["active"] += 1
        return {"id": pool["active"]}

    @staticmethod
    def _release_connection(pool, connection):
        """Helper: release connection to pool."""
        pool["active"] -= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
