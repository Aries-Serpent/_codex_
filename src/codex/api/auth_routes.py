"""
FastAPI authentication routes for the Codex platform.

Exposes the :class:`~codex.auth.authenticator.Authenticator` service
over HTTP with ``/auth/register``, ``/auth/login``, ``/auth/logout``,
and ``/auth/refresh`` endpoints.

Usage::

    from fastapi import FastAPI
    from codex.api.auth_routes import create_auth_router

    app = FastAPI()
    router = create_auth_router()
    app.include_router(router)
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from codex.auth.authenticator import Authenticator, LoginResult
from codex.auth.exceptions import (
    AuthError,
    InvalidCredentialsError,
    MFARequiredError,
    MFAVerificationError,
)
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """Request body for ``POST /auth/register``."""

    username: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    roles: Optional[List[str]] = None
    display_name: Optional[str] = None


class RegisterResponse(BaseModel):
    """Response for ``POST /auth/register``."""

    user_id: str
    username: str
    email: str
    roles: List[str]


class LoginRequest(BaseModel):
    """Request body for ``POST /auth/login``."""

    username_or_email: str = Field(..., min_length=1, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)
    totp_code: Optional[str] = None


class LoginResponse(BaseModel):
    """Response for ``POST /auth/login``."""

    user_id: str
    username: str
    access_token: str
    refresh_token: str
    session_token: str
    session_id: str
    mfa_verified: bool
    roles: List[str]


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

_DEFAULT_SECRET = "codex-auth-change-me-in-production"  # nosec B105


def create_auth_router(
    authenticator: Authenticator | None = None,
    *,
    secret_key: str = _DEFAULT_SECRET,
    prefix: str = "/auth",
) -> APIRouter:
    """Build and return a :class:`~fastapi.APIRouter` with auth endpoints.

    Parameters
    ----------
    authenticator:
        Pre-configured :class:`Authenticator` instance.  When ``None``
        (the default) a fresh in-memory authenticator is created using
        *secret_key*.
    secret_key:
        JWT secret used when *authenticator* is ``None``.
    prefix:
        URL prefix for all auth routes (default ``/auth``).
    """
    if authenticator is None:
        store = UserStore()
        tokens = TokenManager(secret_key=secret_key)
        authenticator = Authenticator(user_store=store, token_manager=tokens)

    auth = authenticator
    router = APIRouter(prefix=prefix, tags=["auth"])

    # ---- register --------------------------------------------------------

    @router.post("/register", response_model=RegisterResponse, status_code=201)
    async def register(body: RegisterRequest) -> RegisterResponse:
        """Create a new user account."""
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
        except MFARequiredError as exc:
            raise HTTPException(status_code=403, detail=exc.message) from exc
        except MFAVerificationError as exc:
            raise HTTPException(status_code=403, detail=exc.message) from exc
        except InvalidCredentialsError as exc:
            raise HTTPException(status_code=401, detail=exc.message) from exc
        except AuthError as exc:
            raise HTTPException(status_code=401, detail=exc.message) from exc

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
    async def logout(body: LogoutRequest) -> LogoutResponse:
        """Revoke the given session token."""
        revoked = auth.logout(body.session_token)
        return LogoutResponse(revoked=revoked)

    # ---- refresh ---------------------------------------------------------

    @router.post("/refresh", response_model=RefreshResponse)
    async def refresh(body: RefreshRequest) -> RefreshResponse:
        """Exchange a refresh token for a new access token."""
        try:
            new_token = auth.refresh(body.refresh_token)
        except (ValueError, AuthError) as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        return RefreshResponse(access_token=new_token)

    return router
