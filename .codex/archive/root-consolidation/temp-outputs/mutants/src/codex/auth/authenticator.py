"""
High-level authentication service for Codex platform.

Ties together :class:`UserStore`, :class:`TokenManager`, and the optional
:class:`MFAProvider` into a single, easy-to-use :class:`Authenticator`
that covers the full login / logout / password-change lifecycle.

Typical usage::

    import os
    from codex.auth import Authenticator, UserStore, TokenManager

    store = UserStore()
    # Get secret key from environment (required in production)
    secret_key = os.getenv("AUTH_SECRET_KEY") or os.getenv("CODEX_AUTH_SECRET_KEY")
    if not secret_key:
        raise ValueError("AUTH_SECRET_KEY or CODEX_AUTH_SECRET_KEY environment variable required")
    tokens = TokenManager(secret_key=secret_key)
    auth = Authenticator(user_store=store, token_manager=tokens)

    # Register
    user = auth.register("alice", "alice@example.com", "sup3rS3cret!")

    # Login → returns LoginResult with access/refresh/session tokens
    result = auth.login("alice", "sup3rS3cret!", ip_address="10.0.0.1")

    # Logout (revokes the session token)
    auth.logout(result.session_token)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from ..security_utils import sanitize_log_message
from .exceptions import (
    MFARequiredError,
    MFAVerificationError,
)
from .mfa_provider import MFAProvider
from .token_manager import TokenManager
from .user_store import User, UserStore

logger = logging.getLogger(__name__)


@dataclass
class LoginResult:
    """Tokens returned after a successful login."""

    user_id: str
    username: str
    access_token: str
    refresh_token: str
    session_token: str
    session_id: str
    mfa_verified: bool = False
    roles: list[str] = field(default_factory=list)


class Authenticator:
    """
    High-level authentication service.

    Combines :class:`~codex.auth.user_store.UserStore`,
    :class:`~codex.auth.token_manager.TokenManager`, and optionally
    :class:`~codex.auth.mfa_provider.MFAProvider` into a cohesive API.

    Args:
        user_store: Backing store for user records.
        token_manager: JWT / session token manager.
        mfa_provider: Optional MFA provider.  When supplied, accounts that
            have MFA enrolled will be required to pass a TOTP code at login.
    """

    def __init__(
        self,
        user_store: UserStore,
        token_manager: TokenManager,
        mfa_provider: Optional[MFAProvider] = None,
    ) -> None:
        self._store = user_store
        self._tokens = token_manager
        self._mfa = mfa_provider
        # Backward-compatible public attributes used by legacy tests/callers.
        self.user_store = user_store
        self.token_manager = token_manager
        self.mfa_provider = mfa_provider

    # ------------------------------------------------------------------ #
    # Registration                                                         #
    # ------------------------------------------------------------------ #

    def register(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[list[str]] = None,
        display_name: Optional[str] = None,
    ) -> User:
        """
        Register a new user account.

        Args:
            username: Unique username (case-sensitive).
            email: Unique e-mail address (normalised to lower-case).
            password: Plain-text password — will be hashed before storage.
            roles: Initial roles (defaults to ``["user"]``).
            display_name: Optional human-readable name.

        Returns:
            The newly created :class:`~codex.auth.user_store.User`.

        Raises:
            ValueError: If username / e-mail is already taken or the
                password does not meet the minimum strength policy.
        """
        user = self._store.create_user(
            username=username,
            email=email,
            password=password,
            roles=roles,
            display_name=display_name,
        )
        logger.info("Registered new user: %s", sanitize_log_message(username))
        return user

    # ------------------------------------------------------------------ #
    # Login / logout                                                       #
    # ------------------------------------------------------------------ #

    def login(
        self,
        username_or_email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        totp_code: Optional[str] = None,
        mfa_code: Optional[str] = None,
    ) -> LoginResult:
        """
        Authenticate a user and issue tokens.

        If MFA is enrolled for the account and no *totp_code* is provided,
        :class:`~codex.auth.exceptions.MFARequiredError` is raised so the
        caller can prompt for the code and retry.

        Args:
            username_or_email: Username or e-mail address.
            password: Plain-text password.
            ip_address: Client IP address (stored in session, optional).
            user_agent: Client user-agent string (stored in session, optional).
            totp_code: 6-digit TOTP code (required when MFA is enrolled).

        Returns:
            :class:`LoginResult` containing all three token types.

        Raises:
            InvalidCredentialsError: Wrong username/password or inactive account.
            MFARequiredError: MFA is enrolled but no *totp_code* was supplied.
            MFAVerificationError: *totp_code* was supplied but is incorrect.
        """
        # Step 1 — credential check
        user = self._store.authenticate(username_or_email, password)

        # Step 2 — MFA check (only when a provider is configured)
        mfa_verified = False
        effective_totp_code = totp_code or mfa_code
        if self._mfa is not None and self._mfa.is_mfa_enabled(user.user_id):  # type: ignore[arg-type]
            if effective_totp_code is None:
                raise MFARequiredError()
            mfa_secret = self._mfa.get_secret(user.user_id)  # type: ignore[arg-type]
            is_valid_mfa = False
            if mfa_secret is not None:
                is_valid_mfa = self._mfa.verify_totp(
                    mfa_secret.secret,
                    effective_totp_code,
                    user.user_id,  # type: ignore[arg-type]
                    algorithm=mfa_secret.algorithm,
                )
                if not is_valid_mfa and mfa_secret.algorithm != "SHA1":
                    # Backward compatibility for clients/tests generating SHA1 codes.
                    is_valid_mfa = self._mfa.verify_totp(
                        mfa_secret.secret,
                        effective_totp_code,
                        user.user_id,  # type: ignore[arg-type]
                        algorithm="SHA1",
                    )
            if not is_valid_mfa:
                raise MFAVerificationError()
            mfa_verified = True

        # Step 3 — issue tokens
        scope = " ".join(user.roles)
        access_token = self._tokens.generate_access_token(user.user_id, scope=scope)  # type: ignore[arg-type]
        refresh_token = self._tokens.generate_refresh_token(user.user_id)  # type: ignore[arg-type]
        session_token, session_id = self._tokens.generate_session_token(
            user_id=user.user_id,  # type: ignore[arg-type]
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )

        logger.info(
            "Login successful: user=%s ip=%s",
            sanitize_log_message(user.username),
            sanitize_log_message(ip_address or "unknown"),
        )

        return LoginResult(
            user_id=user.user_id,  # type: ignore[arg-type]
            username=user.username,
            access_token=access_token,
            refresh_token=refresh_token,
            session_token=session_token,
            session_id=session_id,
            mfa_verified=mfa_verified,
            roles=list(user.roles),
        )

    def logout(self, session_token: str) -> bool:
        """
        Revoke a session token (logout).

        Args:
            session_token: Session token previously returned by :meth:`login`.

        Returns:
            ``True`` if the token was revoked, ``False`` if it was already
            invalid or absent.
        """
        revoked = self._tokens.revoke_token(session_token)
        if revoked:
            logger.info("Session revoked")
        return revoked

    def logout_all(self, user_id: str) -> int:
        """
        Revoke **all** active sessions for *user_id*.

        Useful after a password change or suspected account compromise.

        Args:
            user_id: Target user.

        Returns:
            Number of sessions revoked.
        """
        count = self._tokens.revoke_all_user_tokens(user_id)
        logger.info(
            "Revoked all sessions for user_id=%s (count=%d)",
            sanitize_log_message(user_id),
            count,
        )
        return count

    # ------------------------------------------------------------------ #
    # Token operations                                                     #
    # ------------------------------------------------------------------ #

    def refresh(self, refresh_token: str) -> str:
        """
        Exchange a refresh token for a new access token.

        Args:
            refresh_token: Refresh token previously returned by :meth:`login`.

        Returns:
            New access token.

        Raises:
            ValueError: If the refresh token is invalid or expired.
        """
        return self._tokens.refresh_access_token(refresh_token)

    # ------------------------------------------------------------------ #
    # Password management                                                  #
    # ------------------------------------------------------------------ #

    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
        revoke_sessions: bool = True,
    ) -> None:
        """
        Change a user's password after verifying the current one.

        Args:
            user_id: Target user.
            current_password: User's current plain-text password.
            new_password: Desired new plain-text password.
            revoke_sessions: When ``True`` (default) all existing sessions are
                revoked so other devices are forced to re-authenticate.

        Raises:
            KeyError: If *user_id* does not exist.
            InvalidCredentialsError: If *current_password* is wrong.
            ValueError: If *new_password* does not meet requirements.
        """
        user = self._store.get_user(user_id)
        if user is None:
            raise KeyError(f"User '{user_id}' not found")

        # Re-authenticate with current password
        self._store.authenticate(user.username, current_password)

        self._store.update_password(user_id, new_password)

        if revoke_sessions:
            self.logout_all(user_id)

        logger.info("User auth record updated for user_id=%s", sanitize_log_message(user_id))

    def admin_reset_password(self, user_id: str, new_password: str) -> None:
        """
        Administrative password reset — does **not** require the current password.

        All existing sessions are always revoked.

        Args:
            user_id: Target user.
            new_password: New plain-text password.

        Raises:
            KeyError: If *user_id* does not exist.
            ValueError: If *new_password* does not meet requirements.
        """
        self._store.update_password(user_id, new_password)
        self.logout_all(user_id)
        logger.info(
            "Administrator auth reset for user_id=%s",
            sanitize_log_message(user_id),
        )
