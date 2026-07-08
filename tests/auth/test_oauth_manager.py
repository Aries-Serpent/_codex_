"""
Unit tests for oauth_manager module.

Tests cover:
- OAuth flow initialization
- Token exchange
- Authorization code handling
- Scope validation
- Error handling and exceptions
"""

from datetime import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    datetime,
    timedelta,
    timezone,
)
from unittest.mock import MagicMock, patch

import pytest  # pragma: allowlist secret

from src.codex.auth.oauth_manager import (
    OAuthConfig,
    OAuthException,
    OAuthManager,
    OAuthToken,
)


class TestOAuthManager:
    """Test suite for OAuthManager."""

    @pytest.fixture
    def oauth_config(self):
        """Create a test OAuth configuration."""
        return OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://localhost:8000/callback",
            authorization_url="https://oauth.example.com/authorize",
            token_url="https://oauth.example.com/token",
            scopes=["read:user", "repo"],
        )

    @pytest.fixture
    def oauth_manager(self, oauth_config):
        """Create a test OAuth manager."""
        return OAuthManager(oauth_config)

    def test_oauth_manager_initialization(self, oauth_manager, oauth_config):
        """Test OAuth manager initialization."""
        assert oauth_manager.config == oauth_config, "config is not valid"
        assert oauth_manager.config.client_id == "test_client_id", "client_id is not valid"
        assert oauth_manager.config.scopes == ["read:user", "repo"]

    def test_get_authorization_url(self, oauth_manager):
        """Test authorization URL generation."""
        auth_url = oauth_manager.get_authorization_url(state="test_state")

        assert "client_id=test_client_id" in auth_url, "Condition must be true"
        assert "redirect_uri=https" in auth_url, "Condition must be true"
        assert "state=test_state" in auth_url, "Condition must be true"
        assert "scope=read" in auth_url or "scope=" in auth_url, "Condition must be true"

    def test_get_authorization_url_with_custom_scopes(self, oauth_manager):
        """Test authorization URL with custom scopes."""
        custom_scopes = ["read:user"]
        auth_url = oauth_manager.get_authorization_url(state="test_state", scopes=custom_scopes)

        assert "state=test_state" in auth_url, "Condition must be true"
        assert oauth_manager.config.client_id in auth_url, "Condition must be true"

    @patch("requests.post")
    def test_exchange_code_for_token(self, mock_post, oauth_manager):
        """Test exchanging authorization code for token."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read:user repo",
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        token = oauth_manager.exchange_code_for_token("auth_code_123")

        assert token.access_token == "test_token", "access_token is not valid"
        assert token.token_type == "Bearer", "token_type is not valid"
        assert token.expires_in == 3600, "expires_in is not valid"

    @patch("requests.post")
    def test_exchange_code_with_invalid_code(self, mock_post, oauth_manager):
        """Test exchanging invalid authorization code."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_code"}
        mock_post.return_value = mock_response

        with pytest.raises(OAuthException):
            oauth_manager.exchange_code_for_token("invalid_code")

    @patch("requests.post")
    def test_exchange_code_with_network_error(self, mock_post, oauth_manager):
        """Test exchanging code with network error."""
        mock_post.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            oauth_manager.exchange_code_for_token("auth_code_123")

    def test_token_expiration_check(self, oauth_manager):
        """Test token expiration checking."""
        token = OAuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_in=7200,  # 2 hours - well above the 300s buffer
        )

        assert not token.is_expired(), "Condition must be true"

    def test_token_is_expired(self, oauth_manager):
        """Test expired token detection."""
        token = OAuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_in=-1,  # Already expired
            expires_at=datetime.now() - timedelta(seconds=1),
        )

        assert token.is_expired(), "Condition must be true"

    def test_scope_validation(self, oauth_manager):
        """Test scope validation."""
        valid_scopes = ["read:user", "repo"]
        assert oauth_manager.validate_scopes(valid_scopes), "Condition must be true"

    def test_scope_validation_empty(self, oauth_manager):
        """Test empty scope validation."""
        with pytest.raises((ValueError, OAuthException)):
            oauth_manager.validate_scopes([])

    def test_oauth_config_validation(self, oauth_config):
        """Test OAuth config validation."""
        assert oauth_config.client_id, "Condition must be true"
        assert oauth_config.client_secret, "Condition must be true"
        assert oauth_config.redirect_uri, "Condition must be true"
        assert oauth_config.authorization_url, "Condition must be true"
        assert oauth_config.token_url, "Condition must be true"

    def test_oauth_config_missing_client_id(self):
        """Test OAuth config with missing client ID."""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            OAuthConfig(
                client_id="",  # Empty client ID
                client_secret="secret",
                redirect_uri="https://localhost",
                authorization_url="https://oauth.example.com/authorize",
                token_url="https://oauth.example.com/token",
            )

    @patch("httpx.Client")
    def test_refresh_token(self, mock_client_class, oauth_manager):
        """Test token refresh."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        old_token = OAuthToken(
            access_token="old_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh_123",
        )

        new_token = oauth_manager.refresh_token(old_token)

        assert new_token.access_token == "new_token", "access_token is not valid"
        assert new_token.token_type == "Bearer", "token_type is not valid"

    def test_state_parameter_generation(self, oauth_manager):
        """Test state parameter generation for CSRF protection."""
        state1 = oauth_manager.generate_state()
        state2 = oauth_manager.generate_state()

        assert state1 != state2, "state1 is not valid"
        assert len(state1) > 10, "State1 must not be empty"
        assert len(state2) > 10, "State2 must not be empty"

    def test_state_parameter_validation(self, oauth_manager):
        """Test state parameter validation."""
        state = oauth_manager.generate_state()
        assert oauth_manager.validate_state(state, state)

    def test_state_parameter_validation_failure(self, oauth_manager):
        """Test state parameter validation failure."""
        state1 = oauth_manager.generate_state()
        state2 = oauth_manager.generate_state()

        assert not oauth_manager.validate_state(state1, state2)

    @patch("requests.post")
    def test_exchange_code_response_parsing(self, mock_post, oauth_manager):
        """Test parsing of token exchange response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read:user repo",
            "refresh_token": "refresh_123",
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        token = oauth_manager.exchange_code_for_token("auth_code_123")

        assert token.access_token == "test_token", "access_token is not valid"
        assert token.refresh_token == "refresh_123", "refresh_token is not valid"

    def test_oauth_exception_handling(self):
        """Test OAuth exception handling."""
        with pytest.raises(OAuthException):
            raise OAuthException("Test error")

    @patch("requests.post")
    def test_exchange_code_with_missing_token_in_response(self, mock_post, oauth_manager):
        """Test handling of malformed token response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "token_type": "Bearer",
            "expires_in": 3600,
            # Missing access_token
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with pytest.raises((KeyError, ValueError, OAuthException)):
            oauth_manager.exchange_code_for_token("auth_code_123")


class TestOAuthToken:
    """Test suite for OAuthToken."""

    def test_oauth_token_creation(self):
        """Test OAuthToken creation."""
        token = OAuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )

        assert token.access_token == "test_token", "access_token is not valid"
        assert token.token_type == "Bearer", "token_type is not valid"
        assert token.expires_in == 3600, "expires_in is not valid"

    def test_oauth_token_with_refresh_token(self):
        """Test OAuthToken with refresh token."""
        token = OAuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh_123",
        )

        assert token.refresh_token == "refresh_123", "refresh_token is not valid"

    def test_oauth_token_expiration_datetime(self):
        """Test OAuthToken expiration datetime calculation."""
        token = OAuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )

        assert token.expires_at is not None, "expires_at must be initialized"
        assert token.expires_at > datetime.now(timezone.utc), "expires_at must be greater than zero"


class TestOAuthEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def oauth_config(self):
        """Create a test OAuth configuration."""
        return OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://localhost:8000/callback",
            authorization_url="https://oauth.example.com/authorize",
            token_url="https://oauth.example.com/token",
            scopes=["read:user", "repo"],
        )

    def test_authorization_url_with_special_characters(self, oauth_config):
        """Test authorization URL with special characters in state."""
        oauth_manager = OAuthManager(oauth_config)
        state = "state_with_special_chars_!@#$%"
        auth_url = oauth_manager.get_authorization_url(state=state)

        assert "state=" in auth_url, "Condition must be true"

    def test_authorization_url_encoding(self, oauth_config):
        """Test that authorization URL is properly encoded."""
        oauth_manager = OAuthManager(oauth_config)
        auth_url = oauth_manager.get_authorization_url(state="test state with spaces")

        # Should be URL encoded
        assert "test%20state%20with%20spaces" in auth_url or "test+state+with+spaces" in auth_url

    @patch("requests.post")
    def test_token_exchange_with_large_token(self, mock_post, oauth_config):
        """Test token exchange with very large token value."""
        oauth_manager = OAuthManager(oauth_config)

        large_token = "x" * 10000
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": large_token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        token = oauth_manager.exchange_code_for_token("auth_code_123")
        assert len(token.access_token) == 10000, "Collection must not be empty"

    def test_config_with_unicode_values(self):
        """Test OAuth config with Unicode values."""
        config = OAuthConfig(
            client_id="test_client_id_🔐",
            client_secret="test_secret_🔑",
            redirect_uri="https://localhost:8000/callback",
            authorization_url="https://oauth.example.com/authorize",
            token_url="https://oauth.example.com/token",
            scopes=["read:user", "repo"],
        )

        assert "🔐" in config.client_id, "Condition must be true"
