"""
Tests for OAuth Manager.

Comprehensive test suite for GitHub OAuth2 flow with PKCE.
"""

import time
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.codex.auth.oauth_manager import (
    OAuthManager,
    OAuthConfig,
    OAuthToken,
)


class TestOAuthToken:
    """Tests for OAuthToken data structure."""
    
    def test_token_creation(self):
        """Test token creation with all fields."""
        token = OAuthToken(
            access_token="gho_test123",
            token_type="bearer",
            expires_in=3600,
            refresh_token="ghr_refresh123",
            scope="repo user",
        )
        
        assert token.access_token == "gho_test123"
        assert token.token_type == "bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "ghr_refresh123"
        assert token.scope == "repo user"
        assert token.created_at > 0
    
    def test_token_expiry_check(self):
        """Test token expiry validation."""
        # Create expired token
        token = OAuthToken(
            access_token="gho_test123",
            token_type="bearer",
            expires_in=60,  # 1 minute
            created_at=time.time() - 120,  # 2 minutes ago
        )
        
        assert token.is_expired() is True
    
    def test_token_not_expired(self):
        """Test token not expired validation."""
        token = OAuthToken(
            access_token="gho_test123",
            token_type="bearer",
            expires_in=3600,  # 1 hour
        )
        
        assert token.is_expired() is False
    
    def test_token_expiry_with_buffer(self):
        """Test token expiry with buffer time."""
        # Token expires in 4 minutes, but buffer is 5 minutes
        token = OAuthToken(
            access_token="gho_test123",
            token_type="bearer",
            expires_in=240,  # 4 minutes
            created_at=time.time(),
        )
        
        # Should be considered expired with default 5-minute buffer
        assert token.is_expired(buffer_seconds=300) is True


class TestOAuthConfig:
    """Tests for OAuthConfig data structure."""
    
    def test_config_creation(self):
        """Test OAuth config creation."""
        config = OAuthConfig(
            provider_name="github",
            client_id="test_client_id",
            client_secret="test_secret",
            authorization_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            redirect_uri="http://localhost:8000/callback",
            scope="repo user",
            use_pkce=True,
        )
        
        assert config.provider_name == "github"
        assert config.client_id == "test_client_id"
        assert config.use_pkce is True


class TestOAuthManager:
    """Tests for OAuthManager."""
    
    def test_initialization(self):
        """Test OAuth manager initialization."""
        manager = OAuthManager()
        assert manager is not None
        assert manager._state_store == {}
        assert manager._token_store == {}
    
    def test_create_github_config(self):
        """Test GitHub config creation."""
        manager = OAuthManager()
        config = manager.create_github_config(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8000/callback",
            scope="repo",
        )
        
        assert config.provider_name == "github"
        assert config.authorization_url == manager.GITHUB_AUTH_URL
        assert config.token_url == manager.GITHUB_TOKEN_URL
        assert config.use_pkce is True
    
    def test_generate_state(self):
        """Test state generation for CSRF protection."""
        manager = OAuthManager()
        state1 = manager._generate_state()
        state2 = manager._generate_state()
        
        # States should be unique
        assert state1 != state2
        # States should be reasonable length
        assert len(state1) > 30
    
    def test_generate_code_verifier(self):
        """Test PKCE code verifier generation."""
        manager = OAuthManager()
        verifier1 = manager._generate_code_verifier()
        verifier2 = manager._generate_code_verifier()
        
        # Verifiers should be unique
        assert verifier1 != verifier2
        # Verifiers should be reasonable length
        assert len(verifier1) > 40
    
    def test_generate_code_challenge(self):
        """Test PKCE code challenge generation."""
        manager = OAuthManager()
        verifier = "test_verifier_123"
        challenge = manager._generate_code_challenge(verifier)
        
        # Challenge should be generated
        assert challenge is not None
        assert len(challenge) > 0
        # Same verifier should produce same challenge
        assert challenge == manager._generate_code_challenge(verifier)
    
    def test_initiate_flow(self):
        """Test OAuth flow initiation."""
        manager = OAuthManager()
        config = manager.create_github_config(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8000/callback",
        )
        
        result = manager.initiate_flow(config)
        
        assert 'auth_url' in result
        assert 'state' in result
        assert manager.GITHUB_AUTH_URL in result['auth_url']
        assert 'client_id=test_id' in result['auth_url']
        assert 'code_challenge' in result['auth_url']
        assert result['state'] in manager._state_store
    
    def test_initiate_flow_without_config(self):
        """Test flow initiation without config raises error."""
        manager = OAuthManager()
        
        with pytest.raises(ValueError, match="OAuth configuration is required"):
            manager.initiate_flow()
    
    def test_validate_state_valid(self):
        """Test state validation with valid state."""
        manager = OAuthManager()
        config = manager.create_github_config(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8000/callback",
        )
        
        result = manager.initiate_flow(config)
        state = result['state']
        
        assert manager.validate_state(state) is True
    
    def test_validate_state_invalid(self):
        """Test state validation with invalid state."""
        manager = OAuthManager()
        
        assert manager.validate_state("invalid_state") is False
    
    def test_validate_state_expired(self):
        """Test state validation with expired state."""
        manager = OAuthManager()
        state = "test_state"
        manager._state_store[state] = {
            'created_at': time.time() - 1000,  # 16+ minutes ago
            'config': Mock(),
            'code_verifier': 'test',
        }
        
        assert manager.validate_state(state) is False
        assert state not in manager._state_store
    
    @patch('src.codex.auth.oauth_manager.httpx.Client')
    def test_exchange_code_success(self, mock_client_class):
        """Test successful code exchange for token."""
        # Setup
        manager = OAuthManager()
        config = manager.create_github_config(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8000/callback",
        )
        
        # Initiate flow to get state
        flow_result = manager.initiate_flow(config)
        state = flow_result['state']
        code = "test_auth_code"
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'gho_test123',
            'token_type': 'bearer',
            'expires_in': 3600,
            'refresh_token': 'ghr_refresh123',
            'scope': 'repo user',
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Execute
        token = manager.exchange_code(code, state)
        
        # Verify
        assert token.access_token == 'gho_test123'
        assert token.token_type == 'bearer'
        assert token.expires_in == 3600
        assert token.refresh_token == 'ghr_refresh123'
        assert state not in manager._state_store  # State should be consumed
    
    def test_exchange_code_invalid_state(self):
        """Test code exchange with invalid state."""
        manager = OAuthManager()
        
        with pytest.raises(ValueError, match="Invalid or expired state"):
            manager.exchange_code("test_code", "invalid_state")
    
    @patch('src.codex.auth.oauth_manager.httpx.Client')
    def test_refresh_token_success(self, mock_client_class):
        """Test successful token refresh."""
        # Setup
        manager = OAuthManager()
        config = manager.create_github_config(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8000/callback",
        )
        manager.config = config
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'gho_new_token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'refresh_token': 'ghr_new_refresh',
            'scope': 'repo user',
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Execute
        token = manager.refresh_token("ghr_old_refresh")
        
        # Verify
        assert token.access_token == 'gho_new_token'
        assert token.refresh_token == 'ghr_new_refresh'
    
    @patch('src.codex.auth.oauth_manager.httpx.Client')
    def test_get_github_user(self, mock_client_class):
        """Test getting GitHub user information."""
        # Setup
        manager = OAuthManager()
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            'login': 'testuser',
            'id': 123456,
            'name': 'Test User',
            'email': 'test@example.com',
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Execute
        user = manager.get_github_user("gho_test_token")
        
        # Verify
        assert user['login'] == 'testuser'
        assert user['id'] == 123456
        assert user['email'] == 'test@example.com'
    
    def test_revoke_token(self):
        """Test token revocation."""
        manager = OAuthManager()
        
        # Add token to store
        token = OAuthToken(
            access_token="gho_test123",
            token_type="bearer",
            expires_in=3600,
        )
        manager._token_store["token_id"] = token
        
        # Revoke
        result = manager.revoke_token("gho_test123")
        
        # Verify
        assert result is True
        assert "token_id" not in manager._token_store
    
    def test_revoke_token_not_found(self):
        """Test revoking non-existent token."""
        manager = OAuthManager()
        
        result = manager.revoke_token("gho_nonexistent")
        
        assert result is False


class TestOAuthManagerIntegration:
    """Integration tests for OAuth flow."""
    
    @patch('src.codex.auth.oauth_manager.httpx.Client')
    def test_full_oauth_flow(self, mock_client_class):
        """Test complete OAuth flow from start to user info."""
        # Setup
        manager = OAuthManager()
        config = manager.create_github_config(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8000/callback",
        )
        
        # Step 1: Initiate flow
        flow_result = manager.initiate_flow(config)
        assert 'auth_url' in flow_result
        assert 'state' in flow_result
        state = flow_result['state']
        
        # Step 2: Mock code exchange
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            'access_token': 'gho_test123',
            'token_type': 'bearer',
            'expires_in': 3600,
            'scope': 'repo user',
        }
        mock_token_response.raise_for_status = Mock()
        
        # Step 3: Mock user info
        mock_user_response = Mock()
        mock_user_response.json.return_value = {
            'login': 'testuser',
            'id': 123456,
        }
        mock_user_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.return_value = mock_token_response
        mock_client.__enter__.return_value.get.return_value = mock_user_response
        mock_client_class.return_value = mock_client
        
        # Execute exchange
        token = manager.exchange_code("test_code", state)
        assert token.access_token == 'gho_test123'
        
        # Get user info
        user = manager.get_github_user(token.access_token)
        assert user['login'] == 'testuser'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
