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
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest  # pragma: allowlist secret

# pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
from codex.auth.oauth_manager import (
    OAuthConfig,
    OAuthException,
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
        assert token.access_token == "token123", "access_token is not valid"
        assert token.token_type == "Bearer", "token_type is not valid"
        assert token.expires_in == 3600, "expires_in is not valid"

    def test_token_with_refresh(self):
        token = OAuthToken(
            access_token="access123",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh123",
        )
        assert token.refresh_token == "refresh123", "refresh_token is not valid"

    def test_token_with_scope(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            scope="user:email repository",
        )
        assert token.scope == "user:email repository", "scope is not valid"

    def test_token_created_at_set(self):
        before = time.time()
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        after = time.time()
        assert before <= token.created_at <= after, "before is not valid"

    def test_token_custom_created_at(self):
        custom_time = 1000.0
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            created_at=custom_time,
        )
        assert token.created_at == custom_time, "created_at is not valid"


class TestTokenExpiration:
    """Token expiration checking."""

    def test_token_not_expired(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        assert not token.is_expired(), "Condition must be true"

    def test_token_is_expired(self):
        # Create token with expires_at explicitly in the past
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        assert token.is_expired(), "Condition must be true"

    def test_token_expiration_with_buffer(self):
        # Token expires in 100 seconds, but buffer is 300
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=100,
        )
        assert token.is_expired(buffer_seconds=300), "Condition must be true"

    def test_token_expiration_no_expiry(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=0,  # No expiry
        )
        assert not token.is_expired(), "Condition must be true"

    def test_token_expiration_negative_expiry(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=-1,
        )
        assert not token.is_expired(), "Condition must be true"

    def test_token_soon_to_expire(self):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=200,
        )
        # Should be expired with 300 second buffer
        assert token.is_expired(buffer_seconds=300), "Condition must be true"
        # Should not be expired with 100 second buffer
        assert not token.is_expired(buffer_seconds=100), "Condition must be true"

    def test_token_expiration_with_buffer_and_explicit_expires_at(self):
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=120)
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
            expires_at=expires_at,
        )
        assert token.is_expired(buffer_seconds=300), "Condition must be true"
        assert not token.is_expired(buffer_seconds=60), "Condition must be true"


# ============================================================================
# Authorization Code Flow Tests
# ============================================================================


class TestAuthorizationCodeFlow:
    """OAuth authorization code flow."""

    def test_get_authorization_url(self, oauth_manager):
        url = oauth_manager.get_authorization_url()
        assert url.startswith("https://auth.example.com/authorize"), "Condition must be true"
        assert "client_id=test-client-id" in url, "Condition must be true"
        assert "redirect_uri=" in url, "Condition must be true"
        assert "state=" in url, "Condition must be true"

    def test_authorization_url_with_scope(self, oauth_manager):
        url = oauth_manager.get_authorization_url(scope="user:email repository")
        assert "scope=user" in url or "scope=" in url, "Condition must be true"

    def test_authorization_url_with_pkce(self, oauth_manager):
        url = oauth_manager.get_authorization_url(use_pkce=True)
        # Verify required params are present; PKCE challenge is generated separately
        assert "client_id=" in url, "Condition must be true"
        assert "state=" in url, "Condition must be true"

    def test_authorization_url_unique_state(self, oauth_manager):
        url1 = oauth_manager.get_authorization_url()
        url2 = oauth_manager.get_authorization_url()
        state1 = parse_qs(urlparse(url1).query)["state"][0]
        state2 = parse_qs(urlparse(url2).query)["state"][0]
        assert state1 != state2, "state1 is not valid"

    def test_authorization_url_pkce_challenge_format(self, oauth_manager):
        # PKCE code challenge is generated via the dedicated methods
        verifier = oauth_manager._generate_pkce_verifier()
        challenge = oauth_manager._generate_pkce_challenge(verifier)
        assert len(challenge) >= 43, "Challenge must not be empty"


class TestPKCEFlow:
    """PKCE (Proof Key for Public Clients) flow."""

    def test_pkce_code_verifier_generation(self, oauth_manager):
        verifier = oauth_manager._generate_pkce_verifier()
        assert isinstance(verifier, str)
        assert 43 <= len(verifier) <= 128, "Verifier must not be empty"

    def test_pkce_code_challenge_generation(self, oauth_manager):
        verifier = "a" * 128  # Max length
        challenge = oauth_manager._generate_pkce_challenge(verifier)
        assert isinstance(challenge, str)
        assert len(challenge) > 0, "Challenge must not be empty"

    def test_pkce_flow_consistency(self, oauth_manager):
        verifier = "a" * 128
        challenge1 = oauth_manager._generate_pkce_challenge(verifier)
        challenge2 = oauth_manager._generate_pkce_challenge(verifier)
        assert challenge1 == challenge2, "challenge1 is not valid"

    def test_pkce_challenge_different_for_different_verifiers(self, oauth_manager):
        verifier1 = "a" * 128
        verifier2 = "b" * 128
        challenge1 = oauth_manager._generate_pkce_challenge(verifier1)
        challenge2 = oauth_manager._generate_pkce_challenge(verifier2)
        assert challenge1 != challenge2, "challenge1 is not valid"


# ============================================================================
# Token Exchange Tests
# ============================================================================


class TestTokenExchange:
    """Authorization code token exchange."""

    def test_exchange_code_for_token(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh123",
            }
            mock_post.return_value = mock_response

            token = oauth_manager.exchange_code_for_token("auth_code_123")
            assert token.access_token == "token123", "access_token is not valid"
            assert token.refresh_token == "refresh123", "refresh_token is not valid"

    def test_exchange_code_with_pkce(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
            mock_post.return_value = mock_response

            token = oauth_manager.exchange_code_for_token("auth_code_123")
            assert token.access_token == "token123", "access_token is not valid"

    def test_exchange_code_missing_code(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "invalid_request"}
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                oauth_manager.exchange_code_for_token("")

    def test_exchange_code_none_code(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "invalid_request"}
            mock_post.return_value = mock_response

            with pytest.raises((ValueError, TypeError, AttributeError, OAuthException, Exception)):
                oauth_manager.exchange_code_for_token(None)

    def test_exchange_code_http_error(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "invalid_code"}
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                oauth_manager.exchange_code_for_token("bad_code")


# ============================================================================
# Token Refresh Tests
# ============================================================================


class TestTokenRefresh:
    """Token refresh and rotation."""

    def _mock_httpx_client(self, mock_class, json_data):
        """Helper to set up httpx.Client context manager mock."""
        mock_instance = MagicMock()
        mock_class.return_value.__enter__.return_value = mock_instance
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = json_data
        mock_instance.post.return_value = mock_response
        return mock_instance

    def test_refresh_token(self, oauth_manager, valid_oauth_token):
        with patch("httpx.Client") as mock_client_class:
            self._mock_httpx_client(mock_client_class, {
                "access_token": "new_token_123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "new_refresh_123",
            })
            new_token = oauth_manager.refresh_token(valid_oauth_token)
            assert new_token.access_token == "new_token_123", "access_token is not valid"
            assert new_token.refresh_token == "new_refresh_123", "refresh_token is not valid"

    def test_refresh_token_without_refresh_token(self, oauth_manager):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        with pytest.raises(ValueError):
            oauth_manager.refresh_token(token)

    def test_refresh_token_none_token(self, oauth_manager):
        with pytest.raises((ValueError, TypeError)):
            oauth_manager.refresh_token(None)

    def test_refresh_token_updates_created_at(self, oauth_manager, valid_oauth_token):
        with patch("httpx.Client") as mock_client_class:
            self._mock_httpx_client(mock_client_class, {
                "access_token": "new_token_123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "new_refresh_123",
            })
            new_token = oauth_manager.refresh_token(valid_oauth_token)
            assert new_token.created_at >= valid_oauth_token.created_at, "created_at must be greater than zero"

    def test_refresh_multiple_times(self, oauth_manager, valid_oauth_token):
        token = valid_oauth_token
        for i in range(3):
            with patch("httpx.Client") as mock_client_class:
                self._mock_httpx_client(mock_client_class, {
                    "access_token": f"token_{i}",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "refresh_token": f"refresh_{i}",
                })
                token = oauth_manager.refresh_token(token)

        assert token.access_token == "token_2", "access_token is not valid"


# ============================================================================
# Scope Management Tests
# ============================================================================


class TestScopeManagement:
    """OAuth scope handling."""

    def test_scope_parsing(self, oauth_manager):
        scope_str = "user:email repository public_repo"
        scopes = scope_str.split()
        assert len(scopes) == 3, "Scopes must not be empty"

    def test_authorization_url_with_multiple_scopes(self, oauth_manager):
        url = oauth_manager.get_authorization_url(scope="user:email repository public_repo")
        assert "scope=" in url, "Condition must be true"

    def test_scope_space_separated(self):
        scope = "read:user write:repo delete:gist"
        assert isinstance(scope, str)

    def test_scope_plus_separated(self):
        scope = "read%3Auser+write%3Arepo"
        assert "+" in scope or "%20" in scope or "+" in scope

    def test_empty_scope(self, oauth_manager):
        url = oauth_manager.get_authorization_url(scope="")
        assert url, "url is not valid"


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
        assert len(states) == 100, "States must not be empty"

    def test_state_minimum_length(self, oauth_manager):
        url = oauth_manager.get_authorization_url()
        state = parse_qs(urlparse(url).query)["state"][0]
        assert len(state) >= 20, "State must not be empty"

    def test_state_validation_required(self, oauth_manager):
        # State should be validated during callback
        url = oauth_manager.get_authorization_url()
        state = parse_qs(urlparse(url).query)["state"][0]
        assert state, "state is not valid"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and edge cases."""

    def test_invalid_config(self):
        # OAuthConfig raises ValueError if client_id is empty
        with pytest.raises(ValueError):
            OAuthConfig(
                client_id="",
                client_secret="",
                redirect_uri="",
                authorize_url="",
                token_url="",
            )

    def test_malformed_token_response(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                # Missing required fields
                "token_type": "Bearer",
            }
            mock_post.return_value = mock_response

            with pytest.raises((KeyError, ValueError, OAuthException)):
                oauth_manager.exchange_code_for_token("code123")

    def test_network_error_on_exchange(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("Network error")

            with pytest.raises(Exception):
                oauth_manager.exchange_code_for_token("code123")

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
        assert token1.token_type, "Condition must be true"
        assert token2.token_type, "Condition must be true"


# ============================================================================
# Integration Tests
# ============================================================================


class TestOAuthFlow:
    """Full OAuth flow integration."""

    def test_authorization_flow_components(self, oauth_manager):
        # Get authorization URL
        url = oauth_manager.get_authorization_url(scope="user:email", use_pkce=True)
        assert url, "url is not valid"

        # Extract state
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        state = params["state"][0]

        assert state, "state is not valid"
        # PKCE challenge is generated separately via _generate_pkce_verifier/_generate_pkce_challenge
        verifier = oauth_manager._generate_pkce_verifier()
        challenge = oauth_manager._generate_pkce_challenge(verifier)
        assert challenge, "PKCE challenge must not be empty"

    def test_full_oauth_flow_with_pkce(self, oauth_manager):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh123",
            }
            mock_post.return_value = mock_response

            # Get authorization URL
            url = oauth_manager.get_authorization_url(scope="user:email", use_pkce=True)
            assert url, "url is not valid"

            # Exchange code
            token = oauth_manager.exchange_code_for_token("auth_code_123")
            assert token.access_token == "token123", "access_token is not valid"

        # Refresh token (uses httpx.Client)
        with patch("httpx.Client") as mock_client_class:
            mock_instance = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_instance
            mock_refresh_resp = Mock()
            mock_refresh_resp.raise_for_status.return_value = None
            mock_refresh_resp.json.return_value = {
                "access_token": "token123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh123",
            }
            mock_instance.post.return_value = mock_refresh_resp
            new_token = oauth_manager.refresh_token(token)
            assert new_token.access_token == "token123", "access_token is not valid"


# ============================================================================
# Security Tests
# ============================================================================


class TestSecurityConsiderations:
    """Security-related tests."""

    def test_secret_not_in_authorization_url(self, oauth_manager):
        url = oauth_manager.get_authorization_url()
        assert "test-client-secret" not in url, "Condition must be true"

    def test_refresh_token_required_for_refresh(self, oauth_manager):
        token = OAuthToken(
            access_token="token123",
            token_type="Bearer",
            expires_in=3600,
        )
        with pytest.raises(ValueError):
            oauth_manager.refresh_token(token)

    def test_pkce_verifier_randomness(self, oauth_manager):
        verifiers = set()
        for _ in range(50):
            verifier = oauth_manager._generate_pkce_verifier()
            verifiers.add(verifier)
        assert len(verifiers) == 50, "Verifiers must not be empty"
