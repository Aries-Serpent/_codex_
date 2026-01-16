"""
Authentication exceptions for Codex platform.

Provides specific exception types for authentication and authorization errors.
"""

from typing import Optional


class AuthError(Exception):
    """Base authentication error."""
    
    def __init__(self, message: str, code: str = "auth_error"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.code = code


class AuthenticationError(AuthError):
    """Authentication failed (401)."""
    
    def __init__(self, message: str = "Authentication required", 
                 code: str = "authentication_required"):
        super().__init__(message, code)


class InvalidTokenError(AuthenticationError):
    """Token is invalid or malformed."""
    
    def __init__(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, "invalid_token")
        self.reason = reason


class TokenExpiredError(AuthenticationError):
    """Token has expired."""
    
    def __init__(self, message: str = "Token expired"):
        super().__init__(message, "token_expired")


class TokenRevokedError(AuthenticationError):
    """Token has been revoked."""
    
    def __init__(self, message: str = "Token revoked"):
        super().__init__(message, "token_revoked")


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials provided."""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "invalid_credentials")


class MFARequiredError(AuthenticationError):
    """MFA verification is required."""
    
    def __init__(self, message: str = "MFA verification required"):
        super().__init__(message, "mfa_required")


class MFAVerificationError(AuthenticationError):
    """MFA verification failed."""
    
    def __init__(self, message: str = "MFA verification failed"):
        super().__init__(message, "mfa_failed")


class AuthorizationError(AuthError):
    """Authorization failed (403)."""
    
    def __init__(self, message: str = "Access denied", 
                 code: str = "access_denied"):
        super().__init__(message, code)


class InsufficientScopesError(AuthorizationError):
    """Required scopes not present."""
    
    def __init__(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = required_scopes or []


class RateLimitError(AuthError):
    """Rate limit exceeded (429)."""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded")
        self.retry_after = retry_after


class OAuthError(AuthError):
    """OAuth-specific error."""
    
    def __init__(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error or "oauth_error")
        self.oauth_error = oauth_error
        self.error_description = error_description


class StateValidationError(OAuthError):
    """OAuth state validation failed."""
    
    def __init__(self, message: str = "Invalid state parameter"):
        super().__init__(message, "invalid_state")


class CodeExchangeError(OAuthError):
    """OAuth code exchange failed."""
    
    def __init__(self, message: str = "Code exchange failed"):
        super().__init__(message, "code_exchange_failed")


class APIKeyError(AuthError):
    """API key error."""
    
    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, "invalid_api_key")


class APIKeyRevokedError(APIKeyError):
    """API key has been revoked."""
    
    def __init__(self, message: str = "API key revoked"):
        super().__init__(message)
        self.code = "api_key_revoked"


class SessionError(AuthError):
    """Session-related error."""
    
    def __init__(self, message: str = "Session error", code: str = "session_error"):
        super().__init__(message, code)


class SessionExpiredError(SessionError):
    """Session has expired."""
    
    def __init__(self, message: str = "Session expired"):
        super().__init__(message, "session_expired")


class SessionNotFoundError(SessionError):
    """Session not found."""
    
    def __init__(self, message: str = "Session not found"):
        super().__init__(message, "session_not_found")
