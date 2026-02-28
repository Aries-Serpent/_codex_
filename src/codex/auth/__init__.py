"""
Authentication module for Codex platform.

Provides OAuth2 authentication, MFA, token management, and production-ready
middleware with a focus on GitHub-owned services.

Production Features:
- JWT token generation and validation
- API key authentication
- OAuth2 with PKCE support
- MFA (TOTP) integration
- Rate limiting
- Session management

Usage:
    from codex.auth import TokenManager, AuthMiddleware, require_auth

    # Initialize token manager
    token_manager = TokenManager(secret_key="your-secret-key")

    # Add middleware to FastAPI
    app.add_middleware(AuthMiddleware, token_manager=token_manager)

    # Protect endpoints
    @require_auth(scopes=["read"])
    async def protected_endpoint(request):
        return {"user": request.state.user_id}
"""

from .exceptions import (
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
from .mfa_provider import BackupCode, MFAProvider, MFASecret
from .middleware import (
    APIKeyValidator,
    AuthConfig,
    AuthMethod,
    AuthMiddleware,
    AuthResult,
    RateLimiter,
    get_current_scopes,
    get_current_user,
    require_auth,
)

try:
    from .oauth_manager import OAuthConfig, OAuthManager, OAuthToken
except ImportError:  # httpx or other optional dep missing
    OAuthConfig = OAuthManager = OAuthToken = None  # type: ignore[assignment,misc]
from .token_manager import SessionInfo, TokenClaims, TokenManager, TokenType

__all__ = [
    # OAuth
    "OAuthManager",
    "OAuthToken",
    "OAuthConfig",
    # MFA
    "MFAProvider",
    "MFASecret",
    "BackupCode",
    # Token Management
    "TokenManager",
    "TokenType",
    "TokenClaims",
    "SessionInfo",
    # Middleware
    "AuthMiddleware",
    "AuthConfig",
    "AuthMethod",
    "AuthResult",
    "APIKeyValidator",
    "RateLimiter",
    "require_auth",
    "get_current_user",
    "get_current_scopes",
    # Exceptions
    "AuthError",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidTokenError",
    "TokenExpiredError",
    "TokenRevokedError",
    "InvalidCredentialsError",
    "MFARequiredError",
    "MFAVerificationError",
    "InsufficientScopesError",
    "RateLimitError",
    "OAuthError",
    "StateValidationError",
    "CodeExchangeError",
    "APIKeyError",
    "APIKeyRevokedError",
    "SessionError",
    "SessionExpiredError",
    "SessionNotFoundError",
]
