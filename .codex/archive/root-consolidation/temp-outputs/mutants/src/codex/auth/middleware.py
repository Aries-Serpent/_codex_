"""
Production Authentication Middleware for Codex platform.

Provides FastAPI/Starlette middleware for authentication and authorization.
Supports JWT, API key, and OAuth authentication methods.

Usage:
    from codex.auth.middleware import AuthMiddleware, require_auth

    app = FastAPI()
    app.add_middleware(AuthMiddleware, token_manager=token_manager)

    @app.get("/protected")
    @require_auth(scopes=["read"])
    async def protected_endpoint(request: Request):
        return {"user": request.state.user}
"""

import hashlib
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Optional

from ..security_utils import sanitize_log_message
from .token_manager import TokenClaims, TokenManager

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Supported authentication methods."""

    JWT = "jwt"
    API_KEY = "api_key"  # pragma: allowlist secret
    OAUTH = "oauth"
    NONE = "none"


@dataclass
class AuthConfig:
    """Authentication middleware configuration."""

    enabled: bool = True
    default_method: AuthMethod = AuthMethod.JWT
    api_key_header: str = "X-API-Key"
    bearer_header: str = "Authorization"
    allowed_methods: set[AuthMethod] = field(
        default_factory=lambda: {AuthMethod.JWT, AuthMethod.API_KEY}
    )
    exempt_paths: set[str] = field(default_factory=lambda: {"/health", "/ready", "/metrics"})
    exempt_prefixes: list[str] = field(default_factory=list)
    rate_limit_requests: int = 100  # per minute
    rate_limit_window: int = 60  # seconds


@dataclass
class AuthResult:
    """Authentication result."""

    authenticated: bool
    method: AuthMethod
    user_id: Optional[str] = None
    claims: Optional[TokenClaims] = None
    scopes: set[str] = field(default_factory=set)
    error: Optional[str] = None


class APIKeyValidator:
    """API key validation with secure HMAC-SHA256 hashing."""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.

        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.

        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: dict[str, dict[str, Any]] = {}  # hash -> key_info

        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")  # type: ignore[assignment]
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    # SECURITY: Use a generated development key instead of hardcoded value
                    import secrets

                    self._secret_key = secrets.token_urlsafe(32)
                    logger.info(
                        "Generated development secret key. Set AUTH_SECRET_KEY env var to override."
                    )
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; logger.info(secrets.token_urlsafe(32))'"  # noqa: E501
                    )

    def _compute_hmac(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.

        Args:
            api_key: The API key to hash

        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()

    def register_key(
        self,
        key_hash: str,
        user_id: str,
        scopes: Optional[list[str]] = None,
        name: str = "default",
    ) -> None:
        """
        Register an API key.

        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }

    def validate_key(self, api_key: str) -> Optional[dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.

        Args:
            api_key: The API key to validate

        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)

        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["last_used"] = time.time()
            return key_info

        return None

    def hash_api_key(self, api_key: str) -> str:
        """
        Hash an API key using HMAC-SHA256.

        Use this method when registering API keys to get the secure hash.

        Args:
            api_key: The API key to hash

        Returns:
            HMAC-SHA256 hash of the API key
        """
        return self._compute_hmac(api_key)

    def revoke_key(self, key_hash: str) -> bool:
        """
        Revoke an API key.

        Args:
            key_hash: Hash of the key to revoke

        Returns:
            True if key was revoked
        """
        if key_hash in self._keys:
            del self._keys[key_hash]
            return True
        return False


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_window: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = requests_per_window
        self._window_seconds = window_seconds
        self._counters: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed.

        Args:
            key: Rate limit key (e.g., user ID or IP)

        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds

        if key not in self._counters:
            self._counters[key] = []

        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]

        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False

        # Record request
        self._counters[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests in current window.

        Args:
            key: Rate limit key

        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds

        if key not in self._counters:
            return self._requests_per_window

        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window - current_count)

    def cleanup(self) -> int:
        """
        Clean up old entries.

        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0

        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1

        return cleaned


class AuthMiddleware:
    """
    Production authentication middleware.

    Integrates with FastAPI/Starlette to provide request authentication.
    Supports JWT tokens, API keys, and OAuth tokens.

    Example:
        import os
        from codex.auth.middleware import AuthMiddleware
        from codex.auth.token_manager import TokenManager

        app = FastAPI()
        secret_key = os.getenv("AUTH_SECRET_KEY") or os.getenv("CODEX_AUTH_SECRET_KEY")
        if not secret_key:
            raise ValueError("AUTH_SECRET_KEY or CODEX_AUTH_SECRET_KEY environment variable required")
        token_manager = TokenManager(secret_key=secret_key)
        app.add_middleware(AuthMiddleware, token_manager=token_manager)
    """

    def __init__(
        self,
        app,
        token_manager: TokenManager,
        config: Optional[AuthConfig] = None,
        api_key_validator: Optional[APIKeyValidator] = None,
    ) -> None:
        """
        Initialize authentication middleware.

        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests, self.config.rate_limit_window
        )

    async def __call__(self, scope, receive, send) -> None:
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        if any(path.startswith(prefix) for prefix in self.config.exempt_prefixes):
            await self.app(scope, receive, send)
            return

        if not self.config.enabled:
            await self.app(scope, receive, send)
            return

        # Extract headers
        headers = dict(scope.get("headers", []))

        # Authenticate request
        auth_result = self._authenticate(headers)

        # Store auth result in scope
        scope["auth"] = auth_result

        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return

        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return

        # Continue to app
        await self.app(scope, receive, send)

    def _authenticate(self, headers: dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.

        Args:
            headers: Request headers

        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])

        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)

        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided",
        )

    def _authenticate_jwt(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])

            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}",
            )

    def _authenticate_api_key(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)

        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )

        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(authenticated=False, method=AuthMethod.API_KEY, error="Invalid API key")

    async def _send_unauthorized(self, send, error: Optional[str] = None) -> None:
        """Send 401 Unauthorized response."""
        import json

        body = json.dumps(
            {"error": "Unauthorized", "detail": error or "Authentication required"}
        ).encode()

        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"www-authenticate", b"Bearer"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )

    async def _send_rate_limited(self, send) -> None:
        """Send 429 Too Many Requests response."""
        import json

        body = json.dumps(
            {
                "error": "Too Many Requests",
                "detail": "Rate limit exceeded. Please try again later.",
            }
        ).encode()

        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", str(self.config.rate_limit_window).encode()),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )


def require_auth(scopes: Optional[list[str]] = None, methods: Optional[list[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.

    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods

    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes or [])
    allowed_methods = set(methods or list(AuthMethod))

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = request.scope.get("auth")

            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException

                raise HTTPException(status_code=401, detail="Authentication required")

            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException

                raise HTTPException(status_code=401, detail="Invalid authentication method")

            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException

                raise HTTPException(status_code=403, detail="Insufficient permissions")

            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def get_current_user(request) -> Optional[str]:
    """
    Get current authenticated user from request.

    Args:
        request: FastAPI/Starlette request object

    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = request.scope.get("auth")
    if auth_result and auth_result.authenticated:
        return auth_result.user_id
    return None


def get_current_scopes(request) -> set[str]:
    """
    Get current user's scopes from request.

    Args:
        request: FastAPI/Starlette request object

    Returns:
        Set of scopes
    """
    auth_result = request.scope.get("auth")
    if auth_result and auth_result.authenticated:
        return auth_result.scopes
    return set()
