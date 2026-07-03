import pytest

from src.codex.auth.exceptions import (
    APIKeyError,
    APIKeyRevokedError,
    AuthenticationError,
    AuthError,
    AuthorizationError,
    CodeExchangeError,
    InsufficientScopesError,
    InvalidCredentialsError,
    InvalidTokenError,
    MFARequiredError,
    MFAVerificationError,
    OAuthError,
    RateLimitError,
    SessionError,
    SessionExpiredError,
    SessionNotFoundError,
    StateValidationError,
    TokenExpiredError,
    TokenRevokedError,
)


class TestAuthError:
    """Tests for base AuthError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = AuthError("Something went wrong")
        assert str(error) == "Something went wrong", "Error should be raised or set"
        assert error.message == "Something went wrong", "Error should be raised or set"
        assert error.code == "auth_error", "Error should be raised or set"

    def test_custom_code(self):
        """Test error with custom code."""
        error = AuthError("Custom error", code="custom_code")
        assert error.code == "custom_code", "Error should be raised or set"


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()
        assert "Authentication required" in error.message, "Error should be raised or set"
        assert error.code == "authentication_required", "Error should be raised or set"

    def test_custom_message(self):
        """Test custom error message."""
        error = AuthenticationError("Custom auth error")
        assert error.message == "Custom auth error", "Error should be raised or set"

    def test_is_auth_error(self):
        """Test inheritance from AuthError."""
        error = AuthenticationError()
        assert isinstance(error, AuthError)


class TestInvalidTokenError:
    """Tests for InvalidTokenError."""

    def test_default_message(self):
        """Test default error message."""
        error = InvalidTokenError()
        assert error.message == "Invalid token", "Error should be raised or set"
        assert error.code == "invalid_token", "Error should be raised or set"

    def test_with_reason(self):
        """Test error with reason."""
        error = InvalidTokenError("Bad token", reason="expired signature")
        assert error.reason == "expired signature", "Error should be raised or set"

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
        assert error.message == "Token expired", "Error should be raised or set"
        assert error.code == "token_expired", "Error should be raised or set"


class TestTokenRevokedError:
    """Tests for TokenRevokedError."""

    def test_default_message(self):
        """Test default error message."""
        error = TokenRevokedError()
        assert error.message == "Token revoked", "Error should be raised or set"
        assert error.code == "token_revoked", "Error should be raised or set"


class TestInvalidCredentialsError:
    """Tests for InvalidCredentialsError."""

    def test_default_message(self):
        """Test default error message."""
        error = InvalidCredentialsError()
        assert error.message == "Invalid credentials", "Error should be raised or set"
        assert error.code == "invalid_credentials", "Error should be raised or set"


class TestMFARequiredError:
    """Tests for MFARequiredError."""

    def test_default_message(self):
        """Test default error message."""
        error = MFARequiredError()
        assert "MFA" in error.message, "Error should be raised or set"
        assert error.code == "mfa_required", "Error should be raised or set"


class TestMFAVerificationError:
    """Tests for MFAVerificationError."""

    def test_default_message(self):
        """Test default error message."""
        error = MFAVerificationError()
        assert "MFA" in error.message, "Error should be raised or set"
        assert error.code == "mfa_failed", "Error should be raised or set"


class TestAuthorizationError:
    """Tests for AuthorizationError."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthorizationError()
        assert error.message == "Access denied", "Error should be raised or set"
        assert error.code == "access_denied", "Error should be raised or set"

    def test_is_auth_error(self):
        """Test inheritance from AuthError."""
        error = AuthorizationError()
        assert isinstance(error, AuthError)


class TestInsufficientScopesError:
    """Tests for InsufficientScopesError."""

    def test_default_message(self):
        """Test default error message."""
        error = InsufficientScopesError()
        assert "permissions" in error.message.lower(), "Error should be raised or set"
        assert error.code == "insufficient_scopes", "Error should be raised or set"
        assert error.required_scopes == [], "Error should be raised or set"

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
        assert "Rate limit" in error.message, "Error should be raised or set"
        assert error.code == "rate_limit_exceeded", "Error should be raised or set"
        assert error.retry_after is None, "Error should be raised or set"

    def test_with_retry_after(self):
        """Test error with retry_after."""
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60, "Error should be raised or set"


class TestOAuthError:
    """Tests for OAuthError."""

    def test_basic_error(self):
        """Test basic OAuth error."""
        error = OAuthError("OAuth failed")
        assert error.message == "OAuth failed", "Error should be raised or set"
        assert error.code == "oauth_error", "Error should be raised or set"

    def test_with_oauth_details(self):
        """Test error with OAuth error details."""
        error = OAuthError(
            "Auth failed", oauth_error="access_denied", error_description="User denied access"
        )
        assert error.oauth_error == "access_denied", "Error should be raised or set"
        assert error.error_description == "User denied access", "Error should be raised or set"


class TestStateValidationError:
    """Tests for StateValidationError."""

    def test_default_message(self):
        """Test default error message."""
        error = StateValidationError()
        assert "state" in error.message.lower(), "Error should be raised or set"
        assert error.code == "invalid_state", "Error should be raised or set"

    def test_inheritance(self):
        """Test inheritance from OAuthError."""
        error = StateValidationError()
        assert isinstance(error, OAuthError)


class TestCodeExchangeError:
    """Tests for CodeExchangeError."""

    def test_default_message(self):
        """Test default error message."""
        error = CodeExchangeError()
        assert "exchange" in error.message.lower(), "Error should be raised or set"
        assert error.code == "code_exchange_failed", "Error should be raised or set"


class TestAPIKeyError:
    """Tests for APIKeyError."""

    def test_default_message(self):
        """Test default error message."""
        error = APIKeyError()
        assert "API key" in error.message, "Error should be raised or set"
        assert error.code == "invalid_api_key", "Error should be raised or set"


class TestAPIKeyRevokedError:
    """Tests for APIKeyRevokedError."""

    def test_default_message(self):
        """Test default error message."""
        error = APIKeyRevokedError()
        assert "revoked" in error.message.lower(), "Error should be raised or set"
        assert error.code == "api_key_revoked", "Error should be raised or set"

    def test_inheritance(self):
        """Test inheritance from APIKeyError."""
        error = APIKeyRevokedError()
        assert isinstance(error, APIKeyError)


class TestSessionError:
    """Tests for SessionError."""

    def test_default_message(self):
        """Test default error message."""
        error = SessionError()
        assert "Session" in error.message, "Error should be raised or set"
        assert error.code == "session_error", "Error should be raised or set"


class TestSessionExpiredError:
    """Tests for SessionExpiredError."""

    def test_default_message(self):
        """Test default error message."""
        error = SessionExpiredError()
        assert "expired" in error.message.lower(), "Error should be raised or set"
        assert error.code == "session_expired", "Error should be raised or set"

    def test_inheritance(self):
        """Test inheritance from SessionError."""
        error = SessionExpiredError()
        assert isinstance(error, SessionError)


class TestSessionNotFoundError:
    """Tests for SessionNotFoundError."""

    def test_default_message(self):
        """Test default error message."""
        error = SessionNotFoundError()
        assert "not found" in error.message.lower(), "Error should be raised or set"
        assert error.code == "session_not_found", "Error should be raised or set"

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

        def _raise_authentication() -> None:
            raise AuthenticationError("Test error")

        def _raise_invalid_token() -> None:
            raise InvalidTokenError("Bad token")

        with pytest.raises(AuthenticationError):
            _raise_authentication()

        with pytest.raises(AuthError):
            _raise_invalid_token()
