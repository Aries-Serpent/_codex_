"""
Tests for authentication exceptions.

Tests all exception types in the codex.auth.exceptions module.
"""

import pytest

import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_/src')

from codex.auth.exceptions import (
    AuthError,
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
    InvalidCredentialsError,
    MFARequiredError,
    MFAVerificationError,
    InsufficientScopesError,
    RateLimitError,
    OAuthError,
    StateValidationError,
    CodeExchangeError,
    APIKeyError,
    APIKeyRevokedError,
    SessionError,
    SessionExpiredError,
    SessionNotFoundError,
)


class TestAuthError:
    """Tests for base AuthError."""
    
    def test_basic_error(self):
        """Test basic error creation."""
        error = AuthError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.code == "auth_error"
    
    def test_custom_code(self):
        """Test error with custom code."""
        error = AuthError("Custom error", code="custom_code")
        assert error.code == "custom_code"


class TestAuthenticationError:
    """Tests for AuthenticationError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()
        assert "Authentication required" in error.message
        assert error.code == "authentication_required"
    
    def test_custom_message(self):
        """Test custom error message."""
        error = AuthenticationError("Custom auth error")
        assert error.message == "Custom auth error"
    
    def test_is_auth_error(self):
        """Test inheritance from AuthError."""
        error = AuthenticationError()
        assert isinstance(error, AuthError)


class TestInvalidTokenError:
    """Tests for InvalidTokenError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = InvalidTokenError()
        assert error.message == "Invalid token"
        assert error.code == "invalid_token"
    
    def test_with_reason(self):
        """Test error with reason."""
        error = InvalidTokenError("Bad token", reason="expired signature")
        assert error.reason == "expired signature"
    
    def test_inheritance(self):
        """Test inheritance chain."""
        error = InvalidTokenError()
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, AuthError)


class TestTokenExpiredError:
    """Tests for TokenExpiredError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = TokenExpiredError()
        assert error.message == "Token expired"
        assert error.code == "token_expired"


class TestTokenRevokedError:
    """Tests for TokenRevokedError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = TokenRevokedError()
        assert error.message == "Token revoked"
        assert error.code == "token_revoked"


class TestInvalidCredentialsError:
    """Tests for InvalidCredentialsError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = InvalidCredentialsError()
        assert error.message == "Invalid credentials"
        assert error.code == "invalid_credentials"


class TestMFARequiredError:
    """Tests for MFARequiredError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = MFARequiredError()
        assert "MFA" in error.message
        assert error.code == "mfa_required"


class TestMFAVerificationError:
    """Tests for MFAVerificationError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = MFAVerificationError()
        assert "MFA" in error.message
        assert error.code == "mfa_failed"


class TestAuthorizationError:
    """Tests for AuthorizationError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = AuthorizationError()
        assert error.message == "Access denied"
        assert error.code == "access_denied"
    
    def test_is_auth_error(self):
        """Test inheritance from AuthError."""
        error = AuthorizationError()
        assert isinstance(error, AuthError)


class TestInsufficientScopesError:
    """Tests for InsufficientScopesError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = InsufficientScopesError()
        assert "permissions" in error.message.lower()
        assert error.code == "insufficient_scopes"
        assert error.required_scopes == []
    
    def test_with_scopes(self):
        """Test error with required scopes."""
        error = InsufficientScopesError(required_scopes=["read", "write"])
        assert error.required_scopes == ["read", "write"]
    
    def test_inheritance(self):
        """Test inheritance from AuthorizationError."""
        error = InsufficientScopesError()
        assert isinstance(error, AuthorizationError)


class TestRateLimitError:
    """Tests for RateLimitError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = RateLimitError()
        assert "Rate limit" in error.message
        assert error.code == "rate_limit_exceeded"
        assert error.retry_after is None
    
    def test_with_retry_after(self):
        """Test error with retry_after."""
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60


class TestOAuthError:
    """Tests for OAuthError."""
    
    def test_basic_error(self):
        """Test basic OAuth error."""
        error = OAuthError("OAuth failed")
        assert error.message == "OAuth failed"
        assert error.code == "oauth_error"
    
    def test_with_oauth_details(self):
        """Test error with OAuth error details."""
        error = OAuthError(
            "Auth failed",
            oauth_error="access_denied",
            error_description="User denied access"
        )
        assert error.oauth_error == "access_denied"
        assert error.error_description == "User denied access"


class TestStateValidationError:
    """Tests for StateValidationError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = StateValidationError()
        assert "state" in error.message.lower()
        assert error.code == "invalid_state"
    
    def test_inheritance(self):
        """Test inheritance from OAuthError."""
        error = StateValidationError()
        assert isinstance(error, OAuthError)


class TestCodeExchangeError:
    """Tests for CodeExchangeError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = CodeExchangeError()
        assert "exchange" in error.message.lower()
        assert error.code == "code_exchange_failed"


class TestAPIKeyError:
    """Tests for APIKeyError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = APIKeyError()
        assert "API key" in error.message
        assert error.code == "invalid_api_key"


class TestAPIKeyRevokedError:
    """Tests for APIKeyRevokedError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = APIKeyRevokedError()
        assert "revoked" in error.message.lower()
        assert error.code == "api_key_revoked"
    
    def test_inheritance(self):
        """Test inheritance from APIKeyError."""
        error = APIKeyRevokedError()
        assert isinstance(error, APIKeyError)


class TestSessionError:
    """Tests for SessionError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = SessionError()
        assert "Session" in error.message
        assert error.code == "session_error"


class TestSessionExpiredError:
    """Tests for SessionExpiredError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = SessionExpiredError()
        assert "expired" in error.message.lower()
        assert error.code == "session_expired"
    
    def test_inheritance(self):
        """Test inheritance from SessionError."""
        error = SessionExpiredError()
        assert isinstance(error, SessionError)


class TestSessionNotFoundError:
    """Tests for SessionNotFoundError."""
    
    def test_default_message(self):
        """Test default error message."""
        error = SessionNotFoundError()
        assert "not found" in error.message.lower()
        assert error.code == "session_not_found"
    
    def test_inheritance(self):
        """Test inheritance from SessionError."""
        error = SessionNotFoundError()
        assert isinstance(error, SessionError)


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""
    
    def test_all_inherit_from_auth_error(self):
        """Test that all exceptions inherit from AuthError."""
        exceptions = [
            AuthenticationError(),
            AuthorizationError(),
            InvalidTokenError(),
            TokenExpiredError(),
            TokenRevokedError(),
            InvalidCredentialsError(),
            MFARequiredError(),
            MFAVerificationError(),
            InsufficientScopesError(),
            RateLimitError(),
            OAuthError("test"),
            StateValidationError(),
            CodeExchangeError(),
            APIKeyError(),
            APIKeyRevokedError(),
            SessionError(),
            SessionExpiredError(),
            SessionNotFoundError(),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AuthError), f"{type(exc).__name__} should inherit from AuthError"
    
    def test_all_are_exceptions(self):
        """Test that all are proper exceptions."""
        exceptions = [
            AuthError("test"),
            AuthenticationError(),
            AuthorizationError(),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, Exception)
    
    def test_can_raise_and_catch(self):
        """Test that exceptions can be raised and caught."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Test error")
        
        with pytest.raises(AuthError):
            raise InvalidTokenError("Bad token")
