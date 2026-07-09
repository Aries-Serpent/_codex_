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
    import os
    from codex.auth import TokenManager, AuthMiddleware, require_auth

    # Initialize token manager with secret from environment
    secret_key = os.getenv("AUTH_SECRET_KEY") or os.getenv("CODEX_AUTH_SECRET_KEY")
    if not secret_key:
        raise ValueError("AUTH_SECRET_KEY or CODEX_AUTH_SECRET_KEY environment variable required")
    token_manager = TokenManager(secret_key=secret_key)

    # Add middleware to FastAPI
    app.add_middleware(AuthMiddleware, token_manager=token_manager)

    # Protect endpoints
    @require_auth(scopes=["read"])
    async def protected_endpoint(request):
        return {"user": request.state.user_id}
"""

from .authenticator import Authenticator, LoginResult
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
from .github_app import (
    GitHubApp,
    GitHubAppConfig,
    InstallationToken,
    WebhookVerifier,
    build_app_manifest,
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
    OAuthConfig = OAuthManager = OAuthToken = None  # type: ignore[misc,assignment]
from .token_manager import SessionInfo, TokenClaims, TokenManager, TokenType
from .user_store import PasswordHasher, User, UserStore

__all__ = [
    # Authenticator (high-level service)
    "Authenticator",
    "LoginResult",
    # GitHub App
    "GitHubApp",
    "GitHubAppConfig",
    "InstallationToken",
    "WebhookVerifier",
    "build_app_manifest",
    # User store
    "User",
    "PasswordHasher",
    "UserStore",
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
