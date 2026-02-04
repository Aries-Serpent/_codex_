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

from .oauth_manager import OAuthManager, OAuthToken, OAuthConfig
from .mfa_provider import MFAProvider, MFASecret, BackupCode
from .token_manager import TokenManager, TokenType, TokenClaims, SessionInfo
from .middleware import (
    AuthMiddleware,
    AuthConfig,
    AuthMethod,
    AuthResult,
    APIKeyValidator,
    RateLimiter,
    require_auth,
    get_current_user,
    get_current_scopes,
)
from .exceptions import (
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
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
