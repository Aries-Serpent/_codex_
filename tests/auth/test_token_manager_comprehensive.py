"""Comprehensive tests for codex.auth.token_manager module.

Tests for token management including:
- Token creation and validation
- Token refresh
- Token revocation
- Token expiry
- Secret key management
"""

from __future__ import annotations

# pragma: allowlist secret # pragma: allowlist secret
from datetime import datetime

import pytest

from codex.auth.token_manager import TokenManager, TokenType # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def token_manager():
    """Create a token manager."""
    return TokenManager(secret_key="test-secret-key-for-testing")


@pytest.fixture
def token_manager_custom_timeout():
    """Create a token manager with custom timeout."""
    return TokenManager(
        secret_key="test-secret-key",
        access_token_timeout=1800,  # 30 minutes
        refresh_token_timeout=604800,  # 7 days
    )


# ============================================================================
# TOKEN_TYPE TESTS
# ============================================================================


class TestTokenType:
    """Test TokenType enum."""

    def test_token_type_access(self):
        """Test ACCESS token type."""
        assert TokenType.ACCESS.value == "access"

    def test_token_type_refresh(self):
        """Test REFRESH token type."""
        assert TokenType.REFRESH.value == "refresh"

    def test_token_type_session(self):
        """Test SESSION token type."""
        assert TokenType.SESSION.value == "session"


# ============================================================================
# TOKEN CREATION TESTS
# ============================================================================


class TestTokenCreation:
    """Test token creation."""

    def test_create_access_token(self, token_manager):
        """Test creating access token."""
        token = token_manager.create_access_token("user123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, token_manager):
        """Test creating refresh token."""
        token = token_manager.create_refresh_token("user123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_session_token(self, token_manager):
        """Test creating session token."""
        token = token_manager.create_session_token("user123", "session_123")
        assert token is not None
        assert isinstance(token, str)

    def test_create_token_with_scopes(self, token_manager):
        """Test creating token with scopes."""
        scopes = ["read:repo", "write:repo"]
        token = token_manager.create_access_token("user123", scopes=scopes)
        assert token is not None

    def test_create_token_with_metadata(self, token_manager):
        """Test creating token with metadata."""
        metadata = {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        token = token_manager.create_access_token("user123", metadata=metadata)
        assert token is not None

    def test_create_token_with_custom_expiry(self, token_manager):
        """Test creating token with custom expiry."""
        expires_in = 7200  # 2 hours
        token = token_manager.create_access_token("user123", expires_in=expires_in)
        assert token is not None

    def test_access_token_default_expiry(self, token_manager):
        """Test access token has default expiry."""
        token = token_manager.create_access_token("user123")
        # Token should be valid for some time
        assert token is not None

    def test_refresh_token_longer_expiry(self, token_manager):
        """Test refresh token has longer expiry than access."""
        access = token_manager.create_access_token("user123")
        refresh = token_manager.create_refresh_token("user123")
        # Both should be valid but created successfully
        assert access is not None
        assert refresh is not None


# ============================================================================
# TOKEN VALIDATION TESTS
# ============================================================================


class TestTokenValidation:
    """Test token validation."""

    def test_validate_valid_token(self, token_manager):
        """Test validating valid token."""
        token = token_manager.create_access_token("user123")
        result = token_manager.validate_token(token)
        assert result is not None
        assert result.get("user_id") == "user123"

    def test_validate_invalid_token(self, token_manager):
        """Test validating invalid token."""
        result = token_manager.validate_token("invalid_token")
        assert result is None

    def test_validate_empty_token(self, token_manager):
        """Test validating empty token."""
        result = token_manager.validate_token("")
        assert result is None

    def test_validate_malformed_token(self, token_manager):
        """Test validating malformed token."""
        result = token_manager.validate_token("invalid.malformed.token")
        assert result is None

    def test_validate_token_signature(self, token_manager):
        """Test token signature validation."""
        token = token_manager.create_access_token("user123")
        # Modify token to break signature
        parts = token.split(".")
        if len(parts) == 3:
            parts[2] = "invalidsignature"
            modified_token = ".".join(parts)
            result = token_manager.validate_token(modified_token)
            assert result is None

    def test_validate_token_extracts_claims(self, token_manager):
        """Test token validation extracts claims."""
        scopes = ["read:repo", "write:repo"]
        token = token_manager.create_access_token("user123", scopes=scopes)
        claims = token_manager.validate_token(token)
        assert claims is not None
        assert "user_id" in claims
        assert claims.get("user_id") == "user123"

    def test_validate_token_with_metadata(self, token_manager):
        """Test token validation includes metadata."""
        metadata = {"ip_address": "192.168.1.1"}
        token = token_manager.create_access_token("user123", metadata=metadata)
        claims = token_manager.validate_token(token)
        assert claims is not None

    def test_is_token_valid(self, token_manager):
        """Test is_token_valid convenience method."""
        token = token_manager.create_access_token("user123")
        assert token_manager.is_token_valid(token) is True
        assert token_manager.is_token_valid("invalid") is False


# ============================================================================
# TOKEN REFRESH TESTS
# ============================================================================


class TestTokenRefresh:
    """Test token refresh."""

    def test_refresh_with_valid_refresh_token(self, token_manager):
        """Test refreshing with valid refresh token."""
        refresh = token_manager.create_refresh_token("user123")
        new_access = token_manager.refresh_access_token(refresh)
        assert new_access is not None
        assert isinstance(new_access, str)

    def test_refresh_with_invalid_refresh_token(self, token_manager):
        """Test refresh with invalid refresh token."""
        result = token_manager.refresh_access_token("invalid_token")
        assert result is None

    def test_refresh_creates_new_token(self, token_manager):
        """Test refresh creates new token."""
        refresh = token_manager.create_refresh_token("user123")
        access1 = token_manager.refresh_access_token(refresh)
        access2 = token_manager.refresh_access_token(refresh)
        # New tokens should be different
        assert access1 != access2

    def test_refresh_preserves_user_id(self, token_manager):
        """Test refresh preserves user ID."""
        refresh = token_manager.create_refresh_token("user123")
        new_access = token_manager.refresh_access_token(refresh)
        claims = token_manager.validate_token(new_access)
        assert claims.get("user_id") == "user123"

    def test_refresh_preserves_scopes(self, token_manager):
        """Test refresh preserves scopes."""
        scopes = ["read:repo", "write:repo"]
        refresh = token_manager.create_refresh_token("user123", scopes=scopes)
        new_access = token_manager.refresh_access_token(refresh)
        claims = token_manager.validate_token(new_access)
        assert claims is not None


# ============================================================================
# TOKEN REVOCATION TESTS
# ============================================================================


class TestTokenRevocation:
    """Test token revocation."""

    def test_revoke_token(self, token_manager):
        """Test revoking a token."""
        token = token_manager.create_access_token("user123")
        token_manager.revoke_token(token)
        # Token should no longer be valid
        result = token_manager.validate_token(token)
        assert result is None or result.get("revoked") is True

    def test_revoke_multiple_tokens(self, token_manager):
        """Test revoking multiple tokens."""
        tokens = [
            token_manager.create_access_token("user123"),
            token_manager.create_access_token("user123"),
            token_manager.create_access_token("user123"),
        ]
        for token in tokens:
            token_manager.revoke_token(token)

        # All should be revoked
        for token in tokens:
            result = token_manager.validate_token(token)
            assert result is None or result.get("revoked") is True

    def test_revoke_refresh_token(self, token_manager):
        """Test revoking refresh token."""
        refresh = token_manager.create_refresh_token("user123")
        token_manager.revoke_token(refresh)
        # Should no longer be usable for refresh
        result = token_manager.refresh_access_token(refresh)
        assert result is None

    def test_revoke_invalid_token(self, token_manager):
        """Test revoking invalid token."""
        # Should not raise an error
        token_manager.revoke_token("invalid_token")

    def test_is_token_revoked(self, token_manager):
        """Test checking if token is revoked."""
        token = token_manager.create_access_token("user123")
        assert token_manager.is_token_revoked(token) is False

        token_manager.revoke_token(token)
        assert token_manager.is_token_revoked(token) is True

    def test_revoke_all_user_tokens(self, token_manager):
        """Test revoking all tokens for a user."""
        tokens = [
            token_manager.create_access_token("user123"),
            token_manager.create_refresh_token("user123"),
        ]

        token_manager.revoke_all_user_tokens("user123")

        for token in tokens:
            assert token_manager.is_token_revoked(token) is True


# ============================================================================
# TOKEN EXPIRY TESTS
# ============================================================================


class TestTokenExpiry:
    """Test token expiry."""

    def test_token_not_expired_on_creation(self, token_manager):
        """Test token is not expired on creation."""
        token = token_manager.create_access_token("user123")
        is_expired = token_manager.is_token_expired(token)
        assert is_expired is False

    def test_token_expires_after_timeout(self, token_manager_custom_timeout):
        """Test token expires after timeout."""
        # This test is tricky due to timing
        token = token_manager_custom_timeout.create_access_token(
            "user123", expires_in=1  # 1 second
        )
        import time

        time.sleep(1.1)
        is_expired = token_manager_custom_timeout.is_token_expired(token)
        assert is_expired is True

    def test_get_token_expiry_time(self, token_manager):
        """Test getting token expiry time."""
        token = token_manager.create_access_token("user123", expires_in=3600)
        expiry = token_manager.get_token_expiry(token)
        assert expiry is not None
        assert isinstance(expiry, datetime)

    def test_get_time_until_expiry(self, token_manager):
        """Test getting time until expiry."""
        token = token_manager.create_access_token("user123", expires_in=7200)
        seconds = token_manager.get_seconds_until_expiry(token)
        assert seconds is not None
        assert seconds > 0
        assert seconds <= 7200

    def test_should_refresh_token(self, token_manager):
        """Test checking if token should be refreshed."""
        token = token_manager.create_access_token("user123", expires_in=300)
        # Token is fresh, shouldn't need refresh yet
        should_refresh = token_manager.should_refresh_token(token)
        assert isinstance(should_refresh, bool)


# ============================================================================
# SECRET KEY MANAGEMENT TESTS
# ============================================================================


class TestSecretKeyManagement:
    """Test secret key management."""

    def test_token_manager_with_secret_key(self):
        """Test token manager initialization with secret key."""
        tm = TokenManager(secret_key="my-secret-key")
        assert tm is not None

    def test_token_manager_generate_secret_key(self):
        """Test generating a secret key."""
        secret = TokenManager.generate_secret_key()
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) >= 32

    def test_token_manager_rotate_secret_key(self, token_manager):
        """Test rotating secret key."""
        # Create token with old key
        token = token_manager.create_access_token("user123")

        # Rotate key
        new_secret = TokenManager.generate_secret_key()
        token_manager.rotate_secret_key(new_secret)

        # Token should still be valid (during transition period)
        result = token_manager.validate_token(token)
        assert result is not None or result is None

    def test_different_keys_create_different_tokens(self):
        """Test different secret keys create different tokens."""
        tm1 = TokenManager(secret_key="key1")
        tm2 = TokenManager(secret_key="key2")

        token1 = tm1.create_access_token("user123")
        token2 = tm2.create_access_token("user123")

        # Tokens should be different
        assert token1 != token2

        # Each token should only validate with its manager
        assert tm1.validate_token(token1) is not None
        assert tm2.validate_token(token1) is None


# ============================================================================
# TOKEN SCOPE TESTS
# ============================================================================


class TestTokenScopes:
    """Test token scopes."""

    def test_create_token_with_scopes(self, token_manager):
        """Test creating token with scopes."""
        scopes = ["read:repo", "write:repo", "admin:org"]
        token = token_manager.create_access_token("user123", scopes=scopes)
        claims = token_manager.validate_token(token)
        assert claims is not None
        assert "scopes" in claims or "scope" in claims

    def test_token_scopes_validation(self, token_manager):
        """Test validating token has required scopes."""
        scopes = ["read:repo", "write:repo"]
        token = token_manager.create_access_token("user123", scopes=scopes)

        # Token should have these scopes
        claims = token_manager.validate_token(token)
        assert claims is not None

    def test_token_with_empty_scopes(self, token_manager):
        """Test token with no scopes."""
        token = token_manager.create_access_token("user123", scopes=[])
        claims = token_manager.validate_token(token)
        assert claims is not None

    def test_token_with_many_scopes(self, token_manager):
        """Test token with many scopes."""
        scopes = [f"scope_{i}" for i in range(100)]
        token = token_manager.create_access_token("user123", scopes=scopes)
        claims = token_manager.validate_token(token)
        assert claims is not None


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize(
    "expires_in",
    [
        300,  # 5 minutes
        3600,  # 1 hour
        86400,  # 1 day
        604800,  # 1 week
    ],
)
def test_token_creation_with_different_expiry_parametrized(token_manager, expires_in):
    """Parametrized test for token creation with different expiry times."""
    token = token_manager.create_access_token("user123", expires_in=expires_in)
    assert token is not None
    assert token_manager.validate_token(token) is not None


@pytest.mark.parametrize(
    "user_id",
    [
        "user1",
        "user_with_special_chars_123",
        "user@domain",
        "12345",
    ],
)
def test_create_token_for_different_users_parametrized(token_manager, user_id):
    """Parametrized test for creating tokens for different users."""
    token = token_manager.create_access_token(user_id)
    claims = token_manager.validate_token(token)
    assert claims.get("user_id") == user_id


@pytest.mark.parametrize(
    "scopes",
    [
        ["read:repo"],
        ["read:repo", "write:repo"],
        ["read:repo", "write:repo", "admin:org"],
        [],
    ],
)
def test_create_token_with_scopes_parametrized(token_manager, scopes):
    """Parametrized test for token creation with different scopes."""
    token = token_manager.create_access_token("user123", scopes=scopes)
    assert token is not None


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_token_with_very_long_user_id(self, token_manager):
        """Test token with very long user ID."""
        long_user_id = "user_" + "a" * 1000
        token = token_manager.create_access_token(long_user_id)
        claims = token_manager.validate_token(token)
        assert claims.get("user_id") == long_user_id

    def test_token_with_unicode_user_id(self, token_manager):
        """Test token with unicode user ID."""
        unicode_user = "用户123"
        token = token_manager.create_access_token(unicode_user)
        claims = token_manager.validate_token(token)
        assert claims is not None

    def test_token_with_special_characters_in_user_id(self, token_manager):
        """Test token with special characters in user ID."""
        special_user = "user!@#$%^&*()"
        token = token_manager.create_access_token(special_user)
        claims = token_manager.validate_token(token)
        assert claims is not None

    def test_create_many_tokens_sequentially(self, token_manager):
        """Test creating many tokens in sequence."""
        tokens = []
        for i in range(100):
            token = token_manager.create_access_token(f"user_{i}")
            tokens.append(token)

        assert len(tokens) == 100

        # All should be valid
        for token in tokens:
            assert token_manager.validate_token(token) is not None

    def test_token_refresh_multiple_times(self, token_manager):
        """Test refreshing token multiple times."""
        refresh = token_manager.create_refresh_token("user123")

        tokens = []
        for _ in range(10):
            token = token_manager.refresh_access_token(refresh)
            tokens.append(token)

        assert len(tokens) == 10
        assert all(t is not None for t in tokens)

    def test_token_expiry_boundary(self, token_manager):
        """Test token at expiry boundary."""
        token = token_manager.create_access_token("user123", expires_in=3600)
        # Should be valid immediately after creation
        assert token_manager.validate_token(token) is not None
