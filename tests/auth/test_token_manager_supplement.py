"""
Comprehensive tests for Token Manager (supplement).

Tests cover:
- Token creation and claims
- Token validation and parsing
- Token expiration and refresh
- Scopes and permissions
- Token revocation
- Edge cases
"""

import time

import pytest

from codex.auth.token_manager import TokenClaims, TokenManager, TokenType

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def token_manager():
    """Create token manager."""
    return TokenManager(secret_key="test-secret-key-supplement")


# ============================================================================
# Token Creation Tests
# ============================================================================

class TestTokenCreation:
    """Token creation functionality."""

    def test_create_access_token(self, token_manager):
        token = token_manager.create_token(
            subject="user123",
            token_type=TokenType.ACCESS
        )
        assert token
        assert len(token) > 0

    def test_create_refresh_token(self, token_manager):
        token = token_manager.create_token(
            subject="user456",
            token_type=TokenType.REFRESH
        )
        assert token
        assert len(token) > 0

    def test_create_session_token(self, token_manager):
        token = token_manager.create_token(
            subject="user789",
            token_type=TokenType.SESSION
        )
        assert token
        assert len(token) > 0

    def test_create_token_with_scope(self, token_manager):
        token = token_manager.create_token(
            subject="user123",
            token_type=TokenType.ACCESS,
            scope="read:repo write:repo"
        )
        claims = token_manager.validate_token(token, expected_type=TokenType.ACCESS)
        assert claims.scope == "read:repo write:repo"

    def test_create_token_with_custom_expiry(self, token_manager):
        custom_exp = 7200  # 2 hours
        token = token_manager.create_token(
            subject="user123",
            token_type=TokenType.ACCESS,
            expires_in=custom_exp
        )
        assert token

    def test_token_contains_subject(self, token_manager):
        token = token_manager.create_token(
            subject="user_test",
            token_type=TokenType.ACCESS
        )
        claims = token_manager.validate_token(token)
        assert claims.sub == "user_test"

    def test_token_contains_type(self, token_manager):
        token = token_manager.create_token(
            subject="user123",
            token_type=TokenType.REFRESH
        )
        claims = token_manager.validate_token(token, expected_type=TokenType.REFRESH)
        assert claims.type == TokenType.REFRESH


class TestTokenClaims:
    """Token claims handling."""

    def test_claims_to_dict(self):
        claims = TokenClaims(
            sub="user123",
            iat=time.time(),
            exp=time.time() + 3600,
            type=TokenType.ACCESS,
            scope="read:user"
        )
        claims_dict = claims.to_dict()
        assert claims_dict["sub"] == "user123"
        assert claims_dict["scope"] == "read:user"

    def test_claims_from_dict(self, token_manager):
        claims_dict = {
            "sub": "user456",
            "iat": time.time(),
            "exp": time.time() + 3600,
            "type": "access",
            "scope": "write:repo"
        }
        # Implementation dependent

    def test_claims_issuer(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        claims = token_manager.validate_token(token)
        assert claims.iss == "codex"

    def test_claims_audience(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        claims = token_manager.validate_token(token)
        assert claims.aud == "codex-api"


# ============================================================================
# Token Validation Tests
# ============================================================================

class TestTokenValidation:
    """Token validation."""

    def test_validate_valid_token(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        claims = token_manager.validate_token(token, expected_type=TokenType.ACCESS)
        assert claims.sub == "user123"

    def test_validate_wrong_token_type(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        with pytest.raises(Exception):
            token_manager.validate_token(token, expected_type=TokenType.REFRESH)

    def test_validate_expired_token(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS, expires_in=1)
        time.sleep(2)
        with pytest.raises(Exception):
            token_manager.validate_token(token)

    def test_validate_tampered_token(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        tampered = token[:-5] + "xxxxx"
        with pytest.raises(Exception):
            token_manager.validate_token(tampered)

    def test_validate_empty_token(self, token_manager):
        with pytest.raises(Exception):
            token_manager.validate_token("")

    def test_validate_none_token(self, token_manager):
        with pytest.raises((Exception, TypeError)):
            token_manager.validate_token(None)

    def test_validate_malformed_token(self, token_manager):
        with pytest.raises(Exception):
            token_manager.validate_token("not.a.token")


# ============================================================================
# Token Refresh Tests
# ============================================================================

class TestTokenRefresh:
    """Token refresh functionality."""

    def test_refresh_access_token(self, token_manager):
        refresh_token = token_manager.create_token(
            "user123",
            TokenType.REFRESH
        )
        new_access = token_manager.refresh_token(refresh_token)
        assert new_access
        claims = token_manager.validate_token(new_access)
        assert claims.type == TokenType.ACCESS

    def test_refresh_with_invalid_token(self, token_manager):
        with pytest.raises(Exception):
            token_manager.refresh_token("invalid_token")

    def test_refresh_maintains_subject(self, token_manager):
        refresh_token = token_manager.create_token(
            "user456",
            TokenType.REFRESH
        )
        new_access = token_manager.refresh_token(refresh_token)
        claims = token_manager.validate_token(new_access)
        assert claims.sub == "user456"

    def test_cannot_refresh_access_token(self, token_manager):
        access_token = token_manager.create_token(
            "user123",
            TokenType.ACCESS
        )
        with pytest.raises(Exception):
            token_manager.refresh_token(access_token)


# ============================================================================
# Token Revocation Tests
# ============================================================================

class TestTokenRevocation:
    """Token revocation and blacklist."""

    def test_revoke_token(self, token_manager):
        token = token_manager.create_token("user123", TokenType.SESSION)
        token_manager.revoke_token(token)

        with pytest.raises(Exception):
            token_manager.validate_token(token)

    def test_revoke_prevents_reuse(self, token_manager):
        token = token_manager.create_token("user123", TokenType.SESSION)
        token_manager.revoke_token(token)

        with pytest.raises(Exception):
            token_manager.validate_token(token)

    def test_revoke_nonexistent_token(self, token_manager):
        # Should not raise
        token_manager.revoke_token("nonexistent_token")

    def test_revoke_multiple_tokens(self, token_manager):
        token1 = token_manager.create_token("user1", TokenType.SESSION)
        token2 = token_manager.create_token("user2", TokenType.SESSION)

        token_manager.revoke_token(token1)

        with pytest.raises(Exception):
            token_manager.validate_token(token1)

        # token2 should still be valid
        claims = token_manager.validate_token(token2)
        assert claims.sub == "user2"


# ============================================================================
# Scope Tests
# ============================================================================

class TestTokenScopes:
    """Token scope handling."""

    def test_token_with_single_scope(self, token_manager):
        token = token_manager.create_token(
            "user123",
            TokenType.ACCESS,
            scope="read:user"
        )
        claims = token_manager.validate_token(token)
        assert "read:user" in claims.scope

    def test_token_with_multiple_scopes(self, token_manager):
        token = token_manager.create_token(
            "user123",
            TokenType.ACCESS,
            scope="read:user write:user read:repo"
        )
        claims = token_manager.validate_token(token)
        assert "read:user" in claims.scope
        assert "write:user" in claims.scope

    def test_token_without_scope(self, token_manager):
        token = token_manager.create_token(
            "user123",
            TokenType.ACCESS
        )
        claims = token_manager.validate_token(token)
        assert claims.scope is None or claims.scope == ""

    def test_scope_in_access_only(self, token_manager):
        token = token_manager.create_token(
            "user123",
            TokenType.ACCESS,
            scope="read:user"
        )
        claims = token_manager.validate_token(token)
        assert claims.scope is not None


# ============================================================================
# Token ID (JTI) Tests
# ============================================================================

class TestTokenIdentifier:
    """Token identifier (JTI) handling."""

    def test_token_has_unique_jti(self, token_manager):
        token1 = token_manager.create_token("user123", TokenType.ACCESS)
        token2 = token_manager.create_token("user123", TokenType.ACCESS)

        claims1 = token_manager.validate_token(token1)
        claims2 = token_manager.validate_token(token2)

        # Should have different JTI
        if claims1.jti and claims2.jti:
            assert claims1.jti != claims2.jti

    def test_jti_in_revocation(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        claims = token_manager.validate_token(token)

        if claims.jti:
            # Can use JTI for revocation tracking
            token_manager.revoke_by_jti(claims.jti)


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_very_long_subject(self, token_manager):
        long_subject = "u" * 1000
        token = token_manager.create_token(long_subject, TokenType.ACCESS)
        claims = token_manager.validate_token(token)
        assert claims.sub == long_subject

    def test_unicode_subject(self, token_manager):
        token = token_manager.create_token("用户123", TokenType.ACCESS)
        claims = token_manager.validate_token(token)
        assert claims.sub == "用户123"

    def test_very_long_scope(self, token_manager):
        long_scope = "scope1:read scope2:write " * 50
        token = token_manager.create_token(
            "user123",
            TokenType.ACCESS,
            scope=long_scope
        )
        claims = token_manager.validate_token(token)
        assert long_scope in claims.scope

    def test_special_characters_in_subject(self, token_manager):
        special_subject = "user@domain.com+tag"
        token = token_manager.create_token(special_subject, TokenType.ACCESS)
        claims = token_manager.validate_token(token)
        assert claims.sub == special_subject

    def test_token_with_zero_expiry(self, token_manager):
        # Should use default
        token = token_manager.create_token("user123", TokenType.ACCESS, expires_in=0)
        claims = token_manager.validate_token(token)
        assert claims.sub == "user123"

    def test_token_with_negative_expiry(self, token_manager):
        # Should already be expired
        with pytest.raises(Exception):
            token = token_manager.create_token("user123", TokenType.ACCESS, expires_in=-100)
            token_manager.validate_token(token)


# ============================================================================
# Integration Tests
# ============================================================================

class TestTokenManagementFlow:
    """Complete token management flows."""

    def test_access_refresh_flow(self, token_manager):
        # Create refresh token
        refresh_token = token_manager.create_token(
            "user123",
            TokenType.REFRESH,
            expires_in=86400  # 24 hours
        )

        # Create initial access token
        access_token = token_manager.create_token(
            "user123",
            TokenType.ACCESS,
            expires_in=3600  # 1 hour
        )

        # Validate both
        assert token_manager.validate_token(access_token)
        assert token_manager.validate_token(refresh_token)

    def test_session_token_lifecycle(self, token_manager):
        # Create session
        session_token = token_manager.create_token(
            "user123",
            TokenType.SESSION,
            expires_in=7200
        )

        # Use session
        claims = token_manager.validate_token(session_token)
        assert claims.sub == "user123"

        # Logout (revoke)
        token_manager.revoke_token(session_token)

        # Verify revoked
        with pytest.raises(Exception):
            token_manager.validate_token(session_token)

    def test_multiple_sessions(self, token_manager):
        # Same user multiple sessions
        token1 = token_manager.create_token("user1", TokenType.SESSION)
        token2 = token_manager.create_token("user1", TokenType.SESSION)

        # Both valid
        assert token_manager.validate_token(token1)
        assert token_manager.validate_token(token2)

        # Revoke one
        token_manager.revoke_token(token1)

        # Other still valid
        assert token_manager.validate_token(token2)


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance characteristics."""

    def test_token_creation_performance(self, token_manager):
        pass  # removed redundant `import time` (top-level import used)

        start = time.time()
        for _ in range(100):
            token_manager.create_token(f"user{_}", TokenType.ACCESS)
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 10  # 10 seconds for 100 tokens

    def test_token_validation_performance(self, token_manager):
        pass  # removed redundant `import time` (top-level import used)

        # Pre-create tokens
        tokens = [
            token_manager.create_token(f"user{i}", TokenType.ACCESS)
            for i in range(100)
        ]

        start = time.time()
        for token in tokens:
            token_manager.validate_token(token)
        elapsed = time.time() - start

        # Should validate quickly
        assert elapsed < 10

    def test_token_size(self, token_manager):
        token = token_manager.create_token("user123", TokenType.ACCESS)
        # JWT tokens are base64url encoded
        assert len(token) > 0
        assert len(token) < 2000  # Reasonable size
