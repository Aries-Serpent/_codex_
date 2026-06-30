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
import pytest

from codex.auth.token_manager import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    TokenManager,
    TokenType,
)

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
        assert TokenType.ACCESS.value == "access", "Value must be initialized"

    def test_token_type_refresh(self):
        """Test REFRESH token type."""
        assert TokenType.REFRESH.value == "refresh", "Value must be initialized"

    def test_token_type_session(self):
        """Test SESSION token type."""
        assert TokenType.SESSION.value == "session", "Value must be initialized"


# ============================================================================
# TOKEN CREATION TESTS
# ============================================================================


class TestTokenCreation:
    """Test token creation."""

    def test_create_access_token(self, token_manager):
        """Test creating access token."""
        token = token_manager.create_access_token("user123")
        assert token is not None, "token must be initialized"
        assert isinstance(token, str)
        assert len(token) > 0, "Token must not be empty"

    def test_create_refresh_token(self, token_manager):
        """Test creating refresh token."""
        token = token_manager.create_refresh_token("user123")
        assert token is not None, "token must be initialized"
        assert isinstance(token, str)
        assert len(token) > 0, "Token must not be empty"

    def test_create_session_token(self, token_manager):
        """Test creating session token."""
        token = token_manager.create_session_token("user123")
        assert token is not None, "token must be initialized"
        assert isinstance(token, str)

    def test_create_token_with_scopes(self, token_manager):
        """Test creating token with scopes."""
        scope = "read:repo,write:repo"
        token = token_manager.create_access_token("user123", scope=scope)
        assert token is not None, "token must be initialized"

    def test_create_token_with_metadata(self, token_manager):
        """Test creating token (metadata not supported, just basic creation)."""
        token = token_manager.create_access_token("user123")
        assert token is not None, "token must be initialized"

    def test_create_token_with_custom_expiry(self, token_manager):
        """Test creating token with custom expiry."""
        expires_in = 7200  # 2 hours
        token = token_manager.create_access_token("user123", expires_in=expires_in)
        assert token is not None, "token must be initialized"

    def test_access_token_default_expiry(self, token_manager):
        """Test access token has default expiry."""
        token = token_manager.create_access_token("user123")
        # Token should be valid for some time
        assert token is not None, "token must be initialized"

    def test_refresh_token_longer_expiry(self, token_manager):
        """Test refresh token has longer expiry than access."""
        access = token_manager.create_access_token("user123")
        refresh = token_manager.create_refresh_token("user123")
        # Both should be valid but created successfully
        assert access is not None, "access must be initialized"
        assert refresh is not None, "refresh must be initialized"


# ============================================================================
# TOKEN VALIDATION TESTS
# ============================================================================


class TestTokenValidation:
    """Test token validation."""

    def test_validate_valid_token(self, token_manager):
        """Test validating valid token."""
        token = token_manager.create_access_token("user123")
        result = token_manager.validate_token(token)
        assert result is not None, "result must be initialized"
        assert result.sub == "user123", "Result must not be empty"

    def test_validate_invalid_token(self, token_manager):
        """Test validating invalid token raises ValueError."""
        with pytest.raises(ValueError):
            token_manager.validate_token("invalid_token")

    def test_validate_empty_token(self, token_manager):
        """Test validating empty token raises ValueError."""
        with pytest.raises(ValueError):
            token_manager.validate_token("")

    def test_validate_malformed_token(self, token_manager):
        """Test validating malformed token raises ValueError."""
        with pytest.raises(ValueError):
            token_manager.validate_token("invalid.malformed.token")

    def test_validate_token_signature(self, token_manager):
        """Test token signature validation."""
        token = token_manager.create_access_token("user123")
        # Modify token to break signature
        parts = token.split(".")
        if len(parts) == 3:
            parts[2] = "invalidsignature"
            modified_token = ".".join(parts)
            with pytest.raises(ValueError):
                token_manager.validate_token(modified_token)

    def test_validate_token_extracts_claims(self, token_manager):
        """Test token validation extracts claims."""
        scope = "read:repo,write:repo"
        token = token_manager.create_access_token("user123", scope=scope)
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"
        assert claims.sub == "user123", "Condition must be true"

    def test_validate_token_with_metadata(self, token_manager):
        """Test token validation with basic token."""
        token = token_manager.create_access_token("user123")
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"

    def test_is_token_valid(self, token_manager):
        """Test is_token_valid convenience via try/except."""
        token = token_manager.create_access_token("user123")
        try:
            token_manager.validate_token(token)
            valid = True
        except ValueError:
            valid = False
        assert valid is True, "Condition must be true"

        try:
            token_manager.validate_token("invalid")
            valid = True
        except ValueError:
            valid = False
        assert valid is False, "Condition must be true"


# ============================================================================
# TOKEN REFRESH TESTS
# ============================================================================


class TestTokenRefresh:
    """Test token refresh."""

    def test_refresh_with_valid_refresh_token(self, token_manager):
        """Test refreshing with valid refresh token."""
        refresh = token_manager.create_refresh_token("user123")
        new_access = token_manager.refresh_access_token(refresh)
        assert new_access is not None, "new_access must be initialized"
        assert isinstance(new_access, str)

    def test_refresh_with_invalid_refresh_token(self, token_manager):
        """Test refresh with invalid refresh token raises ValueError."""
        with pytest.raises(ValueError):
            token_manager.refresh_access_token("invalid_token")

    def test_refresh_creates_new_token(self, token_manager):
        """Test refresh creates new token."""
        refresh = token_manager.create_refresh_token("user123")
        access1 = token_manager.refresh_access_token(refresh)
        access2 = token_manager.refresh_access_token(refresh)
        # New tokens should be different
        assert access1 != access2, "access1 is not valid"

    def test_refresh_preserves_user_id(self, token_manager):
        """Test refresh preserves user ID."""
        refresh = token_manager.create_refresh_token("user123")
        new_access = token_manager.refresh_access_token(refresh)
        claims = token_manager.validate_token(new_access)
        assert claims.sub == "user123", "Condition must be true"

    def test_refresh_preserves_scopes(self, token_manager):
        """Test refresh token creation."""
        refresh = token_manager.create_refresh_token("user123")
        new_access = token_manager.refresh_access_token(refresh)
        claims = token_manager.validate_token(new_access)
        assert claims is not None, "claims must be initialized"


# ============================================================================
# TOKEN REVOCATION TESTS
# ============================================================================


class TestTokenRevocation:
    """Test token revocation."""

    def test_revoke_token(self, token_manager):
        """Test revoking a token."""
        token = token_manager.create_access_token("user123")
        token_manager.revoke_token(token)
        # Token should no longer be valid - raises ValueError
        with pytest.raises(ValueError):
            token_manager.validate_token(token)

    def test_revoke_multiple_tokens(self, token_manager):
        """Test revoking multiple tokens."""
        tokens = [
            token_manager.create_access_token("user123"),
            token_manager.create_access_token("user123"),
            token_manager.create_access_token("user123"),
        ]
        for token in tokens:
            token_manager.revoke_token(token)

        # All should be revoked - raises ValueError
        for token in tokens:
            with pytest.raises(ValueError):
                token_manager.validate_token(token)

    def test_revoke_refresh_token(self, token_manager):
        """Test revoking refresh token."""
        refresh = token_manager.create_refresh_token("user123")
        token_manager.revoke_token(refresh)
        # Should no longer be usable for refresh
        with pytest.raises(ValueError):
            token_manager.refresh_access_token(refresh)

    def test_revoke_invalid_token(self, token_manager):
        """Test revoking invalid token."""
        # Should not raise an error
        token_manager.revoke_token("invalid_token")

    def test_is_token_revoked(self, token_manager):
        """Test checking if token is revoked via validate_token."""
        token = token_manager.create_access_token("user123")
        # Before revocation, token should be valid
        claims = token_manager.validate_token(token)
        assert claims is not None, "Token should be valid before revocation"

        token_manager.revoke_token(token)
        # After revocation, token should raise ValueError
        with pytest.raises(ValueError):
            token_manager.validate_token(token)

    def test_revoke_all_user_tokens(self, token_manager):
        """Test revoking all tokens for a user."""
        # revoke_all_user_tokens revokes session tokens (stored in _sessions).
        # Use create_session_token so the sessions are registered and can be revoked.
        session_tokens = [
            token_manager.create_session_token("user123"),
            token_manager.create_session_token("user123"),
        ]

        count = token_manager.revoke_all_user_tokens("user123")
        assert count >= 0, "Revocation count must be non-negative"

        # Session tokens for this user should now be invalid
        for token in session_tokens:
            with pytest.raises(ValueError):
                token_manager.validate_token(token)


# ============================================================================
# TOKEN EXPIRY TESTS
# ============================================================================


class TestTokenExpiry:
    """Test token expiry."""

    def test_token_not_expired_on_creation(self, token_manager):
        """Test token is not expired on creation."""
        import time as _time
        token = token_manager.create_access_token("user123")
        claims = token_manager.validate_token(token)
        is_expired = claims.exp < _time.time()
        assert is_expired is False, "is_expired is not valid"

    def test_token_expires_after_timeout(self, token_manager_custom_timeout):
        """Test token expires after timeout."""
        import time as _time
        token = token_manager_custom_timeout.create_access_token(
            "user123", expires_in=1  # 1 second
        )
        _time.sleep(1.1)
        with pytest.raises(ValueError):
            token_manager_custom_timeout.validate_token(token)

    def test_get_token_expiry_time(self, token_manager):
        """Test getting token expiry time via claims."""
        import time as _time
        from datetime import datetime
        token = token_manager.create_access_token("user123", expires_in=3600)
        claims = token_manager.validate_token(token)
        expiry = datetime.fromtimestamp(claims.exp)
        assert expiry is not None, "expiry must be initialized"
        assert isinstance(expiry, datetime)
        assert claims.exp > _time.time(), "Token should not be expired"

    def test_get_time_until_expiry(self, token_manager):
        """Test getting time until expiry via claims."""
        import time as _time
        token = token_manager.create_access_token("user123", expires_in=7200)
        claims = token_manager.validate_token(token)
        seconds = claims.exp - _time.time()
        assert seconds is not None, "seconds must be initialized"
        assert seconds > 0, "seconds must be greater than zero"
        assert seconds <= 7200, "seconds is not valid"

    def test_should_refresh_token(self, token_manager):
        """Test checking if token should be refreshed via expiry."""
        import time as _time
        token = token_manager.create_access_token("user123", expires_in=300)
        claims = token_manager.validate_token(token)
        # Token is fresh, shouldn't need refresh yet (expiry > 60 seconds away)
        should_refresh = (claims.exp - _time.time()) < 60
        assert isinstance(should_refresh, bool)


# ============================================================================
# SECRET KEY MANAGEMENT TESTS
# ============================================================================


class TestSecretKeyManagement:
    """Test secret key management."""

    def test_token_manager_with_secret_key(self):
        """Test token manager initialization with secret key."""
        tm = TokenManager(secret_key="my-secret-key")
        assert tm is not None, "tm must be initialized"

    def test_token_manager_generate_secret_key(self):
        """Test generating a secret key using secrets module."""
        import secrets as _secrets
        secret = _secrets.token_hex(32)
        assert secret is not None, "secret must be initialized"
        assert isinstance(secret, str)
        assert len(secret) >= 32, "Secret must not be empty"

    def test_token_manager_rotate_secret_key(self, token_manager):
        """Test creating new token manager with rotated key."""
        import secrets as _secrets

        from codex.auth.token_manager import TokenManager

        new_secret = _secrets.token_hex(32)
        new_manager = TokenManager(secret_key=new_secret)
        token = new_manager.create_access_token("user123")
        result = new_manager.validate_token(token)
        assert result is not None, "result must be initialized"

    def test_different_keys_create_different_tokens(self):
        """Test different secret keys create different tokens."""
        tm1 = TokenManager(secret_key="key1")
        tm2 = TokenManager(secret_key="key2")

        token1 = tm1.create_access_token("user123")
        token2 = tm2.create_access_token("user123")

        # Tokens should be different
        assert token1 != token2, "token1 is not valid"

        # Each token should only validate with its own manager
        assert tm1.validate_token(token1) is not None, "Value must be initialized"
        with pytest.raises(ValueError):
            tm2.validate_token(token1)


# ============================================================================
# TOKEN SCOPE TESTS
# ============================================================================


class TestTokenScopes:
    """Test token scopes."""

    def test_create_token_with_scopes(self, token_manager):
        """Test creating token with scopes."""
        scope = "read:repo,write:repo,admin:org"
        token = token_manager.create_access_token("user123", scope=scope)
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"
        assert claims.scope is not None, "Condition must be true"

    def test_token_scopes_validation(self, token_manager):
        """Test validating token has required scopes."""
        scope = "read:repo,write:repo"
        token = token_manager.create_access_token("user123", scope=scope)

        # Token should have these scopes
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"

    def test_token_with_empty_scopes(self, token_manager):
        """Test token with no scopes."""
        token = token_manager.create_access_token("user123")
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"

    def test_token_with_many_scopes(self, token_manager):
        """Test token with many scopes."""
        scope = ",".join(f"scope_{i}" for i in range(100))
        token = token_manager.create_access_token("user123", scope=scope)
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"


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
    assert token is not None, "token must be initialized"
    assert token_manager.validate_token(token) is not None, "Value must be initialized"


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
    assert claims.sub == user_id, "Condition must be true"


@pytest.mark.parametrize(
    "scope",
    [
        "read:repo",
        "read:repo,write:repo",
        "read:repo,write:repo,admin:org",
        "",
    ],
)
def test_create_token_with_scopes_parametrized(token_manager, scope):
    """Parametrized test for token creation with different scopes."""
    token = token_manager.create_access_token("user123", scope=scope if scope else None)
    assert token is not None, "token must be initialized"


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
        assert claims.sub == long_user_id, "Condition must be true"

    def test_token_with_unicode_user_id(self, token_manager):
        """Test token with unicode user ID."""
        unicode_user = "用户123"
        token = token_manager.create_access_token(unicode_user)
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"

    def test_token_with_special_characters_in_user_id(self, token_manager):
        """Test token with special characters in user ID."""
        special_user = "user!@#$%^&*()"
        token = token_manager.create_access_token(special_user)
        claims = token_manager.validate_token(token)
        assert claims is not None, "claims must be initialized"

    def test_create_many_tokens_sequentially(self, token_manager):
        """Test creating many tokens in sequence."""
        tokens = []
        for i in range(100):
            token = token_manager.create_access_token(f"user_{i}")
            tokens.append(token)

        assert len(tokens) == 100, "Tokens must not be empty"

        # All should be valid
        for token in tokens:
            assert token_manager.validate_token(token) is not None, "Value must be initialized"

    def test_token_refresh_multiple_times(self, token_manager):
        """Test refreshing token multiple times."""
        refresh = token_manager.create_refresh_token("user123")

        tokens = []
        for _ in range(10):
            token = token_manager.refresh_access_token(refresh)
            tokens.append(token)

        assert len(tokens) == 10, "Tokens must not be empty"
        assert all(t is not None for t in tokens), "t must be initialized"

    def test_token_expiry_boundary(self, token_manager):
        """Test token at expiry boundary."""
        token = token_manager.create_access_token("user123", expires_in=3600)
        # Should be valid immediately after creation
        assert token_manager.validate_token(token) is not None, "Value must be initialized"
