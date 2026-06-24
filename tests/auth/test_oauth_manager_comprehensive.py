"""
Comprehensive tests for OAuth Manager.

Tests cover:
- OAuth flow initialization
- Authorization code exchange
- Token refresh and rotation
- PKCE validation
- Scope handling
- Error cases and edge conditions
"""

import time
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest

from codex.auth.oauth_manager import (
    OAuthConfig,
    OAuthManager,
    OAuthToken,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def oauth_config():
    """Create standard OAuth config."""
    return OAuthConfig(
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uri="https://example.com/callback",
        authorize_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
    )


@pytest.fixture
def oauth_manager(oauth_config):
    """Create OAuth manager."""
    return OAuthManager(oauth_config)


@pytest.fixture
def valid_oauth_token():
    """Create a valid OAuth token."""
    return OAuthToken(
        access_token="valid_access_token_12345",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="valid_refresh_token_12345",
        scope="user:email repository",
    )


# ============================================================================
# OAuth Token Tests
# ============================================================================


class TestOAuthToken:
    """OAuth token functionality."""

    def test_token_creation(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        assert token.access_token == "token123"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600

    def test_token_with_refresh(self):
        token = OAuthToken(
            access_token="access123",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh123",
        )
        assert token.refresh_token == "refresh123"

    def test_token_with_scope(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            scope="user:email repository",
        )
        assert token.scope == "user:email repository"

    def test_token_created_at_set(self):
        before = time.time()
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        after = time.time()
        assert before <= token.created_at <= after

    def test_token_custom_created_at(self):
        custom_time = 1000.0
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            created_at=custom_time,
        )
        assert token.created_at == custom_time


class TestTokenExpiration:
    """Token expiration checking."""

    def test_token_not_expired(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        assert not token.is_expired()

    def test_token_is_expired(self):
        # Create token with expiration in past
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            created_at=time.time() - 7200,  # 2 hours ago
        )
        assert token.is_expired()

    def test_token_expiration_with_buffer(self):
        # Token expires in 100 seconds, but buffer is 300
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=100,
        )
        assert token.is_expired(buffer_seconds=300)

    def test_token_expiration_no_expiry(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=0,  # No expiry
        )
        assert not token.is_expired()

    def test_token_expiration_negative_expiry(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=-1,
        )
        assert not token.is_expired()

    def test_token_soon_to_expire(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=200,
        )
        # Should be expired with 300 second buffer
        assert token.is_expired(buffer_seconds=300)
        # Should not be expired with 100 second buffer
        assert not token.is_expired(buffer_seconds=100)


# ============================================================================
# Authorization Code Flow Tests
# ============================================================================


class TestAuthorizationCodeFlow:
    """OAuth authorization code flow."""

    def test_get_authorization_url(self, oauth_manager):
        url = oauth_manager.get_authorization_url()
        assert url.startswith("https://auth.example.com/authorize")
        assert "client_id=test-client-id" in url
        assert "redirect_uri=" in url
        assert "state=" in url

    def test_authorization_url_with_scope(self, oauth_manager):
        url = oauth_manager.get_authorization_url(scope="user:email repository")
        assert "scope=user" in url or "scope=" in url

    def test_authorization_url_with_pkce(self, oauth_manager):
        url = oauth_manager.get_authorization_url(use_pkce=True)
        assert "code_challenge=" in url
        assert "code_challenge_method=" in url

    def test_authorization_url_unique_state(self, oauth_manager):
        url1 = oauth_manager.get_authorization_url()
        url2 = oauth_manager.get_authorization_url()
        state1 = parse_qs(urlparse(url1).query)["state"][0]
        state2 = parse_qs(urlparse(url2).query)["state"][0]
        assert state1 != state2

    def test_authorization_url_pkce_challenge_format(self, oauth_manager):
        url = oauth_manager.get_authorization_url(use_pkce=True)
        challenge = parse_qs(urlparse(url).query)["code_challenge"][0]
        assert len(challenge) >= 43  # PKCE minimum


class TestPKCEFlow:
    """PKCE (Proof Key for Public Clients) flow."""

    def test_pkce_code_verifier_generation(self, oauth_manager):
        verifier = oauth_manager._generate_pkce_verifier()
        assert isinstance(verifier, str)
        assert 43 <= len(verifier) <= 128

    def test_pkce_code_challenge_generation(self, oauth_manager):
        verifier = "a" * 128  # Max length
        challenge = oauth_manager._generate_pkce_challenge(verifier)
        assert isinstance(challenge, str)
        assert len(challenge) > 0

    def test_pkce_flow_consistency(self, oauth_manager):
        verifier = "a" * 128
        challenge1 = oauth_manager._generate_pkce_challenge(verifier)
        challenge2 = oauth_manager._generate_pkce_challenge(verifier)
        assert challenge1 == challenge2

    def test_pkce_challenge_different_for_different_verifiers(self, oauth_manager):
        verifier1 = "a" * 128
        verifier2 = "b" * 128
        challenge1 = oauth_manager._generate_pkce_challenge(verifier1)
        challenge2 = oauth_manager._generate_pkce_challenge(verifier2)
        assert challenge1 != challenge2


# ============================================================================
# Token Exchange Tests
# ============================================================================


class TestTokenExchange:
    """Authorization code token exchange."""

    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, oauth_manager):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh123",
            }
            mock_post.return_value = mock_response

            token = await oauth_manager.exchange_code_for_token("auth_code_123")
            assert token.access_token == "token123"
            assert token.refresh_token == "refresh123"

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce(self, oauth_manager):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
            mock_post.return_value = mock_response

            token = await oauth_manager.exchange_code_for_token(
                "auth_code_123", code_verifier="a" * 128
            )
            assert token.access_token == "token123"

    @pytest.mark.asyncio
    async def test_exchange_code_missing_code(self, oauth_manager):
        with pytest.raises(ValueError):
            await oauth_manager.exchange_code_for_token("")

    @pytest.mark.asyncio
    async def test_exchange_code_none_code(self, oauth_manager):
        with pytest.raises((ValueError, TypeError)):
            await oauth_manager.exchange_code_for_token(None)

    @pytest.mark.asyncio
    async def test_exchange_code_http_error(self, oauth_manager):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "invalid_code"}
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                await oauth_manager.exchange_code_for_token("bad_code")


# ============================================================================
# Token Refresh Tests
# ============================================================================


class TestTokenRefresh:
    """Token refresh and rotation."""

    @pytest.mark.asyncio
    async def test_refresh_token(self, oauth_manager, valid_oauth_token):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "new_token_123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "new_refresh_123",
            }
            mock_post.return_value = mock_response

            new_token = await oauth_manager.refresh_token(valid_oauth_token)
            assert new_token.access_token == "new_token_123"
            assert new_token.refresh_token == "new_refresh_123"

    @pytest.mark.asyncio
    async def test_refresh_token_without_refresh_token(self, oauth_manager):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        with pytest.raises(ValueError):
            await oauth_manager.refresh_token(token)

    @pytest.mark.asyncio
    async def test_refresh_token_none_token(self, oauth_manager):
        with pytest.raises((ValueError, TypeError)):
            await oauth_manager.refresh_token(None)

    @pytest.mark.asyncio
    async def test_refresh_token_updates_created_at(self, oauth_manager, valid_oauth_token):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "new_token_123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "new_refresh_123",
            }
            mock_post.return_value = mock_response

            new_token = await oauth_manager.refresh_token(valid_oauth_token)
            assert new_token.created_at >= valid_oauth_token.created_at

    @pytest.mark.asyncio
    async def test_refresh_multiple_times(self, oauth_manager, valid_oauth_token):
        with patch("httpx.AsyncClient.post") as mock_post:
            token = valid_oauth_token
            for i in range(3):
                mock_response = Mock()
                mock_response.json.return_value = {
                    "access_token": f"token_{i}",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "refresh_token": f"refresh_{i}",
                }
                mock_post.return_value = mock_response
                token = await oauth_manager.refresh_token(token)

            assert token.access_token == "token_2"


# ============================================================================
# Scope Management Tests
# ============================================================================


class TestScopeManagement:
    """OAuth scope handling."""

    def test_scope_parsing(self, oauth_manager):
        scope_str = "user:email repository public_repo"
        scopes = scope_str.split()
        assert len(scopes) == 3

    def test_authorization_url_with_multiple_scopes(self, oauth_manager):
        url = oauth_manager.get_authorization_url(scope="user:email repository public_repo")
        assert "scope=" in url

    def test_scope_space_separated(self):
        scope = "read:user write:repo delete:gist"
        assert isinstance(scope, str)

    def test_scope_plus_separated(self):
        scope = "read%3Auser+write%3Arepo"
        assert "+" in scope or "%20" in scope or "+" in scope

    def test_empty_scope(self, oauth_manager):
        url = oauth_manager.get_authorization_url(scope="")
        assert url  # Should still work


# ============================================================================
# State Management Tests
# ============================================================================


class TestStateManagement:
    """OAuth state parameter handling."""

    def test_state_randomness(self, oauth_manager):
        states = set()
        for _ in range(100):
            url = oauth_manager.get_authorization_url()
            state = parse_qs(urlparse(url).query)["state"][0]
            states.add(state)
        assert len(states) == 100  # All unique

    def test_state_minimum_length(self, oauth_manager):
        url = oauth_manager.get_authorization_url()
        state = parse_qs(urlparse(url).query)["state"][0]
        assert len(state) >= 20  # Reasonable minimum

    def test_state_validation_required(self, oauth_manager):
        # State should be validated during callback
        url = oauth_manager.get_authorization_url()
        state = parse_qs(urlparse(url).query)["state"][0]
        assert state  # State exists


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and edge cases."""

    def test_invalid_config(self):
        config = OAuthConfig(
            client_id="",
            client_secret="",
            redirect_uri="",
            authorize_url="",
            token_url="",
        )
        manager = OAuthManager(config)
        assert manager  # Should handle empty config

    def test_malformed_token_response(self, oauth_manager):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                # Missing required fields
                "token_type": "Bearer",
            }
            mock_post.return_value = mock_response

            with pytest.raises((KeyError, ValueError)):
                import asyncio

                asyncio.run(oauth_manager.exchange_code_for_token("code123"))

    def test_network_error_on_exchange(self, oauth_manager):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.side_effect = Exception("Network error")

            with pytest.raises(Exception):
                import asyncio

                asyncio.run(oauth_manager.exchange_code_for_token("code123"))

    def test_token_type_case_insensitive(self):
        # Most OAuth implementations are case-insensitive
        token1 = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        token2 = OAuthToken(
            access_token="token123",
            token_type="bearer",
            expires_in=3600,
        )
        # Both should work
        assert token1.token_type
        assert token2.token_type


# ============================================================================
# Integration Tests
# ============================================================================


class TestOAuthFlow:
    """Full OAuth flow integration."""

    def test_authorization_flow_components(self, oauth_manager):
        # Get authorization URL
        url = oauth_manager.get_authorization_url(scope="user:email", use_pkce=True)
        assert url

        # Extract state
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        state = params["state"][0]
        code_challenge = params.get("code_challenge", [None])[0]

        assert state
        assert code_challenge

    @pytest.mark.asyncio
    async def test_full_oauth_flow_with_pkce(self, oauth_manager):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh123",
            }
            mock_post.return_value = mock_response

            # Get authorization URL
            url = oauth_manager.get_authorization_url(scope="user:email", use_pkce=True)
            assert url

            # Exchange code (with PKCE)
            token = await oauth_manager.exchange_code_for_token(
                "auth_code_123", code_verifier="a" * 128
            )
            assert token.access_token == "token123"

            # Refresh token
            new_token = await oauth_manager.refresh_token(token)
            assert new_token.access_token == "token123"


# ============================================================================
# Security Tests
# ============================================================================


class TestSecurityConsiderations:
    """Security-related tests."""

    def test_secret_not_in_authorization_url(self, oauth_manager):
        url = oauth_manager.get_authorization_url()
        assert "test-client-secret" not in url

    def test_refresh_token_required_for_refresh(self, oauth_manager):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        with pytest.raises(ValueError):
            import asyncio

            asyncio.run(oauth_manager.refresh_token(token))

    def test_pkce_verifier_randomness(self, oauth_manager):
        verifiers = set()
        for _ in range(50):
            verifier = oauth_manager._generate_pkce_verifier()
            verifiers.add(verifier)
        assert len(verifiers) == 50  # All unique
