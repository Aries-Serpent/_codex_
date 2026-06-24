"""
FastAPI authentication routes for the Codex platform.

Exposes the :class:`~codex.auth.authenticator.Authenticator` service
over HTTP with ``/auth/register``, ``/auth/login``, ``/auth/logout``,
and ``/auth/refresh`` endpoints.

Environment variables:
    CODEX_AUTH_SECRET:  JWT signing key.  **Required** in production;
        falls back to an insecure default only for local development.

Usage::

    from fastapi import FastAPI
    from codex.api.auth_routes import create_auth_router

    app = FastAPI()
    router = create_auth_router()
    app.include_router(router)
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from codex.auth.authenticator import Authenticator, LoginResult
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore
from codex.security_utils import sanitize_log_message

logger = logging.getLogger(__name__)

# Simple e-mail pattern — intentionally permissive but catches obvious junk.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _safe_log_value(value: object) -> str:
    """Normalize user-controlled values before logging."""
    return sanitize_log_message(str(value) if value is not None else "unknown")


# ---------------------------------------------------------------------------
# Simple per-endpoint rate limiter (no external deps)
# ---------------------------------------------------------------------------


class _EndpointRateLimiter:
    """Lightweight in-memory sliding-window rate limiter for auth endpoints."""

    def __init__(
        self,
        requests_per_window: int = 20,
        window_seconds: int = 60,
    ) -> None:
        self._max = requests_per_window
        self._window = window_seconds
        self._counters: dict[str, list[float]] = {}

    def check(self, key: str) -> bool:
        """Return *True* if the request is allowed, *False* otherwise."""
        now = time.time()
        cutoff = now - self._window
        bucket = self._counters.setdefault(key, [])
        # Prune expired entries
        self._counters[key] = bucket = [t for t in bucket if t > cutoff]
        if len(bucket) >= self._max:
            return False
        bucket.append(now)
        return True

    @property
    def window(self) -> int:
        return self._window


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """Request body for ``POST /auth/register``.

    Attributes:
        username: Unique username (1–150 characters).
        email: Valid e-mail address (3–254 characters).
        password: Plain-text password (8–128 characters); hashed before storage.
        roles: Optional initial roles (defaults to ``["user"]``).
        display_name: Optional human-readable display name.
    """

    username: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    roles: Optional[list[str]] = None
    display_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid e-mail address format")
        return v.lower().strip()


class RegisterResponse(BaseModel):
    """Response for ``POST /auth/register``."""

    user_id: str
    username: str
    email: str
    roles: list[str]


class LoginRequest(BaseModel):
    """Request body for ``POST /auth/login``.

    Attributes:
        username_or_email: Username or e-mail address.
        password: Plain-text password.
        totp_code: Optional 6-digit TOTP code when MFA is enrolled.
    """

    username_or_email: str = Field(..., min_length=1, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)
    totp_code: Optional[str] = None


class LoginResponse(BaseModel):
    """Response for ``POST /auth/login``.

    Contains three JWT tokens (access, refresh, session) plus user metadata.
    """

    user_id: str
    username: str
    access_token: str
    refresh_token: str
    session_token: str
    session_id: str
    mfa_verified: bool
    roles: list[str]


class LogoutRequest(BaseModel):
    """Request body for ``POST /auth/logout``."""

    session_token: str


class LogoutResponse(BaseModel):
    """Response for ``POST /auth/logout``."""

    revoked: bool


class RefreshRequest(BaseModel):
    """Request body for ``POST /auth/refresh``."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response for ``POST /auth/refresh``."""

    access_token: str


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------


def _get_default_secret() -> str:
    """Get a default JWT secret from environment or generate one for development."""
    import secrets

    # Try environment variable first
    env_secret = os.environ.get("CODEX_AUTH_SECRET")
    if env_secret:
        return env_secret

    # Generate a secure random secret for development
    logger.warning(
        "CODEX_AUTH_SECRET not set. Generating temporary development secret. "
        "Set CODEX_AUTH_SECRET environment variable for persistent key."
    )
    return secrets.token_urlsafe(32)


def create_auth_router(
    authenticator: Authenticator | None = None,
    *,
    secret_key: str | None = None,
    prefix: str = "/auth",
    login_rate_limit: int = 10,
    register_rate_limit: int = 5,
    default_rate_limit: int = 20,
) -> APIRouter:
    """Build and return a :class:`~fastapi.APIRouter` with auth endpoints.

    Parameters
    ----------
    authenticator:
        Pre-configured :class:`Authenticator` instance.  When ``None``
        (the default) a fresh in-memory authenticator is created using
        *secret_key*.
    secret_key:
        JWT secret used when *authenticator* is ``None``.  Falls back to
        ``CODEX_AUTH_SECRET`` env-var, then to a development-only default.
    prefix:
        URL prefix for all auth routes (default ``/auth``).
    login_rate_limit:
        Max login attempts per IP per minute (default 10).
    register_rate_limit:
        Max registration attempts per IP per minute (default 5).
    default_rate_limit:
        Max requests per IP per minute for other auth endpoints (default 20).

    Error responses
    ---------------
    * **400** — Validation error (duplicate user, weak password, bad e-mail).
    * **401** — Invalid credentials or expired/invalid token.
    * **403** — MFA required or MFA verification failed.
    * **422** — Request body validation error (Pydantic).
    * **429** — Rate limit exceeded.
    """
    if authenticator is None:
        resolved_secret = secret_key or _get_default_secret()
        store = UserStore()
        tokens = TokenManager(secret_key=resolved_secret)
        authenticator = Authenticator(user_store=store, token_manager=tokens)

    auth = authenticator
    router = APIRouter(prefix=prefix, tags=["auth"])

    # Per-endpoint rate limiters (keyed by client IP)
    _login_limiter = _EndpointRateLimiter(login_rate_limit, 60)
    _register_limiter = _EndpointRateLimiter(register_rate_limit, 60)
    _default_limiter = _EndpointRateLimiter(default_rate_limit, 60)

    def _get_client_ip(request: Request) -> str:
        return request.client.host if request.client else "unknown"

    def _enforce_rate_limit(limiter: _EndpointRateLimiter, request: Request) -> None:
        ip = _get_client_ip(request)
        if not limiter.check(ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(limiter.window)},
            )

    # ---- register --------------------------------------------------------

    @router.post("/register", response_model=RegisterResponse, status_code=201)
    async def register(body: RegisterRequest, request: Request) -> RegisterResponse:
        """Create a new user account."""
        _enforce_rate_limit(_register_limiter, request)
        try:
            user = auth.register(
                username=body.username,
                email=body.email,
                password=body.password,
                roles=body.roles,
                display_name=body.display_name,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        ip = request.client.host if request.client else "unknown"
        logger.info(
            "User registered: %s from %s", _safe_log_value(user.username), _safe_log_value(ip)
        )

        return RegisterResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            roles=list(user.roles),
        )

    # ---- login -----------------------------------------------------------

    @router.post("/login", response_model=LoginResponse)
    async def login(body: LoginRequest, request: Request) -> LoginResponse:
        """Authenticate and receive access / refresh / session tokens."""
        _enforce_rate_limit(_login_limiter, request)
        ip_address: str | None = None
        if request.client:
            ip_address = request.client.host
        user_agent = request.headers.get("user-agent")

        try:
            result: LoginResult = auth.login(
                username_or_email=body.username_or_email,
                password=body.password,
                ip_address=ip_address,
                user_agent=user_agent,
                totp_code=body.totp_code,
            )
        except (ConnectionError, TimeoutError) as exc:
            code = getattr(exc, "code", "")
            if code == "mfa_required":
                logger.info("MFA required for login attempt from %s", _safe_log_value(ip_address))
                raise HTTPException(status_code=403, detail="MFA verification required") from exc
            if code == "mfa_failed":
                logger.warning("MFA verification failed from %s", _safe_log_value(ip_address))
                raise HTTPException(status_code=403, detail="MFA verification failed") from exc
            if hasattr(exc, "code"):
                logger.warning(
                    "Login failed from %s: %s", _safe_log_value(ip_address), type(exc).__name__
                )
                raise HTTPException(status_code=401, detail="Invalid credentials") from exc
            # Not an auth-domain exception — log and re-raise as 500
            exc_type = type(exc).__name__
            logger.error(
                "Unexpected error during login from %s: %s", _safe_log_value(ip_address), exc_type
            )
            raise

        logger.info(
            "Login success: user=%s from %s",
            _safe_log_value(result.username),
            _safe_log_value(ip_address),
        )

        return LoginResponse(
            user_id=result.user_id,
            username=result.username,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            session_token=result.session_token,
            session_id=result.session_id,
            mfa_verified=result.mfa_verified,
            roles=result.roles,
        )

    # ---- logout ----------------------------------------------------------

    @router.post("/logout", response_model=LogoutResponse)
    async def logout(body: LogoutRequest, request: Request) -> LogoutResponse:
        """Revoke the given session token."""
        _enforce_rate_limit(_default_limiter, request)
        revoked = auth.logout(body.session_token)
        if revoked:
            logger.info("Session revoked")
        return LogoutResponse(revoked=revoked)

    # ---- refresh ---------------------------------------------------------

    @router.post("/refresh", response_model=RefreshResponse)
    async def refresh(body: RefreshRequest, request: Request) -> RefreshResponse:
        """Exchange a refresh token for a new access token."""
        _enforce_rate_limit(_default_limiter, request)
        try:
            new_token = auth.refresh(body.refresh_token)
        except (ConnectionError, TimeoutError) as exc:
            if isinstance(exc, ValueError) or hasattr(exc, "code"):
                logger.warning("Session refresh rejected: %s", type(exc).__name__)
                raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
            logger.error("Unexpected auth refresh error: %s", type(exc).__name__)
            raise

        return RefreshResponse(access_token=new_token)

    # ---- CSRF token (for cookie-based auth flows) ------------------------

    @router.get("/csrf-token")
    async def csrf_token(request: Request) -> dict[str, str]:
        """Return a fresh CSRF token for cookie-based auth flows.

        Clients using cookie-based authentication should call this endpoint
        first and include the returned token in subsequent mutating requests
        via the ``X-CSRF-Token`` header.
        """
        import secrets as _secrets

        token = _secrets.token_urlsafe(32)
        return {"csrf_token": token}

    return router
