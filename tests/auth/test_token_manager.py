"""
Tests for Token Manager.

Comprehensive test suite for JWT token management and session handling.
"""

import time
from unittest.mock import patch

import pytest

from src.codex.auth.token_manager import (
    TokenManager,
    TokenClaims,
    TokenType,
    SessionInfo,
)


class TestTokenType:
    """Tests for TokenType enum."""
    
    def test_token_types(self):
        """Test token type enum values."""
        assert TokenType.ACCESS.value == "access"
        assert TokenType.REFRESH.value == "refresh"
        assert TokenType.SESSION.value == "session"


class TestTokenClaims:
    """Tests for TokenClaims data structure."""
    
    def test_claims_creation(self):
        """Test token claims creation."""
        claims = TokenClaims(
            sub="user123",
            iat=time.time(),
            exp=time.time() + 900,
            type=TokenType.ACCESS,
            scope="repo user",
            jti="token123",
        )
        
        assert claims.sub == "user123"
        assert claims.type == TokenType.ACCESS
        assert claims.scope == "repo user"
        assert claims.jti == "token123"
    
    def test_claims_to_dict(self):
        """Test converting claims to dictionary."""
        now = time.time()
        claims = TokenClaims(
            sub="user123",
            iat=now,
            exp=now + 900,
            type=TokenType.ACCESS,
        )
        
        data = claims.to_dict()
        
        assert data['sub'] == "user123"
        assert data['type'] == "access"
        assert data['iat'] == now
    
    def test_claims_from_dict(self):
        """Test creating claims from dictionary."""
        now = time.time()
        data = {
            'sub': "user123",
            'iat': now,
            'exp': now + 900,
            'type': "access",
            'scope': "repo",
            'jti': "token123",
            'iss': "codex",
            'aud': "codex-api",
        }
        
        claims = TokenClaims.from_dict(data)
        
        assert claims.sub == "user123"
        assert claims.type == TokenType.ACCESS
        assert claims.scope == "repo"


class TestSessionInfo:
    """Tests for SessionInfo data structure."""
    
    def test_session_creation(self):
        """Test session info creation."""
        now = time.time()
        session = SessionInfo(
            session_id="session123",
            user_id="user123",
            created_at=now,
            last_activity=now,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            mfa_verified=True,
        )
        
        assert session.session_id == "session123"
        assert session.user_id == "user123"
        assert session.mfa_verified is True
    
    def test_session_is_active(self):
        """Test session activity check."""
        now = time.time()
        session = SessionInfo(
            session_id="session123",
            user_id="user123",
            created_at=now,
            last_activity=now,
        )
        
        assert session.is_active() is True
    
    def test_session_is_inactive(self):
        """Test inactive session detection."""
        now = time.time()
        session = SessionInfo(
            session_id="session123",
            user_id="user123",
            created_at=now - 2000,
            last_activity=now - 2000,  # 33+ minutes ago
        )
        
        assert session.is_active(timeout=1800) is False
    
    def test_session_update_activity(self):
        """Test updating session activity."""
        now = time.time()
        session = SessionInfo(
            session_id="session123",
            user_id="user123",
            created_at=now - 100,
            last_activity=now - 100,
        )
        
        old_activity = session.last_activity
        time.sleep(0.1)
        session.update_activity()
        
        assert session.last_activity > old_activity


class TestTokenManager:
    """Tests for TokenManager."""
    
    def test_initialization(self):
        """Test token manager initialization."""
        manager = TokenManager()
        
        assert manager is not None
        assert manager._secret_key is not None
        assert manager._revoked_tokens == set()
        assert manager._sessions == {}
    
    def test_initialization_with_secret(self):
        """Test token manager initialization with provided secret."""
        secret = "test_secret_key_123"
        manager = TokenManager(secret_key=secret)
        
        assert manager._secret_key == secret
    
    def test_generate_access_token(self):
        """Test access token generation."""
        manager = TokenManager()
        token = manager.generate_access_token("user123", scope="repo")
        
        assert token is not None
        assert len(token) > 0
        assert token.count('.') == 2  # JWT format: header.payload.signature
    
    def test_generate_refresh_token(self):
        """Test refresh token generation."""
        manager = TokenManager()
        token = manager.generate_refresh_token("user123")
        
        assert token is not None
        assert len(token) > 0
    
    def test_generate_session_token(self):
        """Test session token generation."""
        manager = TokenManager()
        token, session_id = manager.generate_session_token(
            "user123",
            mfa_verified=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert token is not None
        assert session_id is not None
        assert session_id in manager._sessions
        
        session = manager._sessions[session_id]
        assert session.user_id == "user123"
        assert session.mfa_verified is True
        assert session.ip_address == "192.168.1.1"
    
    def test_validate_token_valid(self):
        """Test validating a valid token."""
        manager = TokenManager()
        token = manager.generate_access_token("user123")
        
        claims = manager.validate_token(token)
        
        assert claims.sub == "user123"
        assert claims.type == TokenType.ACCESS
    
    def test_validate_token_expired(self):
        """Test validating an expired token."""
        manager = TokenManager()
        
        # Create token with negative expiry
        now = time.time()
        claims = TokenClaims(
            sub="user123",
            iat=now - 1000,
            exp=now - 100,  # Expired
            type=TokenType.ACCESS,
        )
        token = manager._encode_token(claims)
        
        with pytest.raises(ValueError, match="Token expired"):
            manager.validate_token(token)
    
    def test_validate_token_wrong_type(self):
        """Test validating token with wrong type."""
        manager = TokenManager()
        refresh_token = manager.generate_refresh_token("user123")
        
        with pytest.raises(ValueError, match="Invalid token type"):
            manager.validate_token(refresh_token, expected_type=TokenType.ACCESS)
    
    def test_validate_token_revoked(self):
        """Test validating a revoked token."""
        manager = TokenManager()
        token = manager.generate_access_token("user123")
        
        # Revoke token
        manager.revoke_token(token)
        
        # Validation should fail
        with pytest.raises(ValueError, match="Token revoked"):
            manager.validate_token(token)
    
    def test_refresh_access_token(self):
        """Test refreshing access token."""
        manager = TokenManager()
        refresh_token = manager.generate_refresh_token("user123")
        
        new_access_token = manager.refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        claims = manager.validate_token(new_access_token)
        assert claims.sub == "user123"
        assert claims.type == TokenType.ACCESS
    
    def test_refresh_access_token_invalid(self):
        """Test refreshing with invalid refresh token."""
        manager = TokenManager()
        access_token = manager.generate_access_token("user123")
        
        # Try to refresh with access token (wrong type)
        with pytest.raises(ValueError):
            manager.refresh_access_token(access_token)
    
    def test_revoke_token(self):
        """Test revoking a token."""
        manager = TokenManager()
        token = manager.generate_access_token("user123")
        
        result = manager.revoke_token(token)
        
        assert result is True
        
        # Token should now be invalid
        with pytest.raises(ValueError, match="Token revoked"):
            manager.validate_token(token)
    
    def test_revoke_session_token(self):
        """Test revoking a session token."""
        manager = TokenManager()
        token, session_id = manager.generate_session_token("user123")
        
        # Session should exist
        assert session_id in manager._sessions
        
        # Revoke token
        result = manager.revoke_token(token)
        
        assert result is True
        assert session_id not in manager._sessions
    
    def test_revoke_all_user_tokens(self):
        """Test revoking all tokens for a user."""
        manager = TokenManager()
        user_id = "user123"
        
        # Create multiple sessions
        token1, session1 = manager.generate_session_token(user_id)
        token2, session2 = manager.generate_session_token(user_id)
        token3, session3 = manager.generate_session_token("user456")
        
        # Revoke all tokens for user123
        count = manager.revoke_all_user_tokens(user_id)
        
        assert count == 2
        assert session1 not in manager._sessions
        assert session2 not in manager._sessions
        assert session3 in manager._sessions  # Different user
    
    def test_get_session(self):
        """Test getting session information."""
        manager = TokenManager()
        token, session_id = manager.generate_session_token("user123", mfa_verified=True)
        
        session = manager.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.user_id == "user123"
        assert session.mfa_verified is True
    
    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        manager = TokenManager()
        
        session = manager.get_session("nonexistent")
        
        assert session is None
    
    def test_get_user_sessions(self):
        """Test getting all sessions for a user."""
        manager = TokenManager()
        user_id = "user123"
        
        # Create multiple sessions
        token1, session1 = manager.generate_session_token(user_id)
        token2, session2 = manager.generate_session_token(user_id)
        token3, session3 = manager.generate_session_token("user456")
        
        sessions = manager.get_user_sessions(user_id)
        
        assert len(sessions) == 2
        assert all(s.user_id == user_id for s in sessions)
    
    def test_cleanup_expired_sessions(self):
        """Test cleaning up expired sessions."""
        manager = TokenManager()
        
        # Create active session
        token1, session1 = manager.generate_session_token("user123")
        
        # Create expired session
        now = time.time()
        expired_session = SessionInfo(
            session_id="expired_session",
            user_id="user456",
            created_at=now - 3000,
            last_activity=now - 3000,
        )
        manager._sessions["expired_session"] = expired_session
        
        # Clean up
        count = manager.cleanup_expired_sessions()
        
        assert count == 1
        assert session1 in manager._sessions
        assert "expired_session" not in manager._sessions
    
    def test_session_activity_update(self):
        """Test session activity is updated on token validation."""
        manager = TokenManager()
        token, session_id = manager.generate_session_token("user123")
        
        session = manager.get_session(session_id)
        original_activity = session.last_activity
        
        time.sleep(0.1)
        
        # Validate token (should update activity)
        manager.validate_token(token)
        
        session = manager.get_session(session_id)
        assert session.last_activity > original_activity


class TestTokenManagerIntegration:
    """Integration tests for token workflow."""
    
    def test_full_authentication_flow(self):
        """Test complete authentication flow with tokens."""
        manager = TokenManager()
        user_id = "user123"
        
        # Step 1: Generate access and refresh tokens
        access_token = manager.generate_access_token(user_id, scope="repo user")
        refresh_token = manager.generate_refresh_token(user_id)
        
        # Step 2: Validate access token
        claims = manager.validate_token(access_token, TokenType.ACCESS)
        assert claims.sub == user_id
        
        # Step 3: Refresh access token
        new_access_token = manager.refresh_access_token(refresh_token)
        new_claims = manager.validate_token(new_access_token, TokenType.ACCESS)
        assert new_claims.sub == user_id
        
        # Step 4: Revoke tokens
        manager.revoke_token(access_token)
        with pytest.raises(ValueError):
            manager.validate_token(access_token)
    
    def test_session_lifecycle(self):
        """Test complete session lifecycle."""
        manager = TokenManager()
        user_id = "user123"
        
        # Create session with MFA
        session_token, session_id = manager.generate_session_token(
            user_id,
            mfa_verified=True,
            ip_address="192.168.1.1"
        )
        
        # Verify session exists
        session = manager.get_session(session_id)
        assert session is not None
        assert session.mfa_verified is True
        
        # Validate token updates activity
        claims = manager.validate_token(session_token)
        assert claims.sub == user_id
        
        # Get all user sessions
        sessions = manager.get_user_sessions(user_id)
        assert len(sessions) == 1
        
        # Revoke session
        manager.revoke_token(session_token)
        assert manager.get_session(session_id) is None
    
    def test_multi_user_token_isolation(self):
        """Test token isolation between users."""
        manager = TokenManager()
        
        # Create tokens for multiple users
        user1_token = manager.generate_access_token("user1")
        user2_token = manager.generate_access_token("user2")
        
        # Validate each token
        claims1 = manager.validate_token(user1_token)
        claims2 = manager.validate_token(user2_token)
        
        assert claims1.sub == "user1"
        assert claims2.sub == "user2"
        
        # Revoke user1 tokens
        manager.revoke_token(user1_token)
        
        # User1 token should be invalid
        with pytest.raises(ValueError):
            manager.validate_token(user1_token)
        
        # User2 token should still be valid
        claims2_again = manager.validate_token(user2_token)
        assert claims2_again.sub == "user2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
