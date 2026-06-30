"""
Token Manager for Codex platform.

Handles JWT token generation, validation, rotation, and session management
with focus on security and GitHub integration.

Minimum Python version: 3.9+ (uses built-in generic types)
"""

import json
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from ..security_utils import sanitize_log_message


class TokenType(Enum):
    """Token types."""

    ACCESS = "access"
    REFRESH = "refresh"
    SESSION = "session"


@dataclass
class TokenClaims:
    """JWT token claims."""

    sub: str  # Subject (user ID)
    iat: float  # Issued at
    exp: float  # Expiration
    type: TokenType  # Token type
    scope: Optional[str] = None  # Permissions/scopes
    jti: Optional[str] = None  # Token ID
    iss: str = "codex"  # Issuer
    aud: str = "codex-api"  # Audience

    def to_dict(self) -> dict[str, Any]:
        """Convert claims to dictionary."""
        return {
            "sub": self.sub,
            "iat": self.iat,
            "exp": self.exp,
            "type": self.type.value,
            "scope": self.scope,
            "jti": self.jti,
            "iss": self.iss,
            "aud": self.aud,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TokenClaims":
        """Create claims from dictionary."""
        return cls(
            sub=data["sub"],
            iat=data["iat"],
            exp=data["exp"],
            type=TokenType(data["type"]),
            scope=data.get("scope"),
            jti=data.get("jti"),
            iss=data.get("iss", "codex"),
            aud=data.get("aud", "codex-api"),
        )


@dataclass
class SessionInfo:
    """User session information."""

    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    mfa_verified: bool = False

    def is_active(self, timeout: int = 1800) -> bool:
        """Check if session is still active (default 30 minutes)."""
        return (time.time() - self.last_activity) < timeout

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()


class TokenManager:
    """
    Token manager for authentication and session management.

    Provides JWT-like token generation and validation without external
    dependencies. In production, consider using PyJWT library.
    """

    # Token expiration times (in seconds)
    ACCESS_TOKEN_EXPIRY = 900  # 15 minutes
    REFRESH_TOKEN_EXPIRY = 604800  # 7 days
    SESSION_TOKEN_EXPIRY = 2592000  # 30 days

    def __init__(
        self,
        secret_key: Optional[str] = None,
        access_token_timeout: Optional[int] = None,
        refresh_token_timeout: Optional[int] = None,
        session_token_timeout: Optional[int] = None,
    ):
        """
        Initialize token manager.

        Args:
            secret_key: Secret key for signing tokens.
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via
                       environment variable or secure configuration.
            access_token_timeout: Optional legacy override for access-token expiry.
            refresh_token_timeout: Optional legacy override for refresh-token expiry.
            session_token_timeout: Optional legacy override for session-token expiry.

        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings

            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning,
            )
            secret_key = secrets.token_urlsafe(64)

        self._secret_key = secret_key
        self._revoked_tokens: set[str] = set()  # Use Redis in production
        self._sessions: dict[str, SessionInfo] = {}  # Use database in production
        self._access_token_expiry = (
            self.ACCESS_TOKEN_EXPIRY if access_token_timeout is None else access_token_timeout
        )
        self._refresh_token_expiry = (
            self.REFRESH_TOKEN_EXPIRY if refresh_token_timeout is None else refresh_token_timeout
        )
        self._session_token_expiry = (
            self.SESSION_TOKEN_EXPIRY if session_token_timeout is None else session_token_timeout
        )

    def _encode_token(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).

        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.

        Args:
            claims: Token claims

        Returns:
            Encoded token string
        """
        import base64
        import hashlib
        import hmac

        # Create header
        header = {
            "typ": "JWT",
            "alg": "HS256",
        }

        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")

        payload_b64 = (
            base64.urlsafe_b64encode(json.dumps(claims.to_dict(), default=str).encode())
            .decode()
            .rstrip("=")
        )

        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(self._secret_key.encode(), message.encode(), hashlib.sha256).digest()

        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        # Combine all parts
        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def _decode_token(self, token: str) -> TokenClaims:
        """
        Decode and verify token.

        Args:
            token: Encoded token string

        Returns:
            Decoded token claims

        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hashlib
        import hmac

        try:
            # Split token parts
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid token format")

            header_b64, payload_b64, signature_b64 = parts

            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(), message.encode(), hashlib.sha256
            ).digest()

            # Add padding if needed
            signature_b64_padded = signature_b64 + "=" * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)

            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")

            # Decode payload
            payload_b64_padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())

            # Create claims
            return TokenClaims.from_dict(payload)

        except (ValueError, TypeError) as e:
            error_msg = sanitize_log_message(f"Token decode failed: {e!s}")
            raise ValueError(error_msg) from e

    def generate_access_token(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.

        Args:
            user_id: User identifier
            scope: Optional permissions scope

        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)

        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self._access_token_expiry,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )

        return self._encode_token(claims)

    def generate_refresh_token(self, user_id: str) -> str:
        """
        Generate refresh token.

        Args:
            user_id: User identifier

        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)

        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self._refresh_token_expiry,
            type=TokenType.REFRESH,
            jti=jti,
        )

        return self._encode_token(claims)

    def create_access_token(
        self,
        user_id: str,
        scope: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> str:
        """Backward-compatible alias for :meth:`generate_access_token`."""
        if expires_in is not None:
            return self.create_token(
                user_id,
                TokenType.ACCESS,
                expires_in=expires_in,
                scope=scope,
            )
        return self.generate_access_token(user_id, scope=scope)

    def create_refresh_token(
        self,
        user_id: str,
        expires_in: Optional[int] = None,
    ) -> str:
        """Backward-compatible alias for :meth:`generate_refresh_token`."""
        if expires_in is not None:
            return self.create_token(user_id, TokenType.REFRESH, expires_in=expires_in)
        return self.generate_refresh_token(user_id)

    def generate_session_token(
        self,
        user_id: str,
        mfa_verified: bool = False,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Generate session token and create session.

        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)

        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )

        self._sessions[session_id] = session

        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self._session_token_expiry,
            type=TokenType.SESSION,
            jti=session_id,
        )

        token = self._encode_token(claims)
        return token, session_id

    def validate_token(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.

        Args:
            token: Token to validate
            expected_type: Expected token type (optional)

        Returns:
            Validated token claims

        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)

        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")

        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(
                f"Invalid token type: expected {expected_type.value}, got {claims.type.value}"
            )

        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")

        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")

            # Update activity
            session.update_activity()

        return claims

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token

        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, TokenType.REFRESH)

        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)

    def refresh_token(self, refresh_token: str) -> str:
        """Backward-compatible alias for :meth:`refresh_access_token`."""
        return self.refresh_access_token(refresh_token)

    def create_token(
        self,
        user_id: str,
        token_type: TokenType,
        expires_in: Optional[int] = None,
        scope: Optional[str] = None,
    ) -> str:
        """Create a token with optional custom expiry for compatibility."""
        now = time.time()
        expiry_map = {
            TokenType.ACCESS: self._access_token_expiry,
            TokenType.REFRESH: self._refresh_token_expiry,
            TokenType.SESSION: self._session_token_expiry,
        }
        if token_type not in expiry_map:
            raise ValueError(f"Unsupported token type: {token_type!r}")
        jti = secrets.token_urlsafe(16)
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + (expires_in if expires_in is not None else expiry_map[token_type]),
            type=token_type,
            scope=scope,
            jti=jti,
        )
        if token_type == TokenType.SESSION:
            self._sessions[jti] = SessionInfo(
                session_id=jti,
                user_id=user_id,
                created_at=now,
                last_activity=now,
            )
        return self._encode_token(claims)

    def create_session_token(self, user_id: str, **kwargs) -> str:
        """Backward-compatible wrapper for :meth:`generate_session_token`.

        Returns only the token (not the tuple).
        """
        token, _ = self.generate_session_token(user_id, **kwargs)
        return token

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token.

        Args:
            token: Token to revoke

        Returns:
            True if token was revoked
        """
        try:
            # Handle None or empty token gracefully
            if token is None or not isinstance(token, str):
                return False

            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)

                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]

                return True
        except (ValueError, AttributeError, TypeError):
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False

        return False

    def revoke_by_jti(self, jti: str) -> bool:
        """
        Revoke a token by its JTI (JWT ID).

        Args:
            jti: Token ID to revoke

        Returns:
            True if token was revoked, False if JTI is invalid
        """
        # Validate JTI to prevent memory exhaustion attacks
        if not jti or not isinstance(jti, str):
            return False

        # Enforce reasonable max length (256 bytes is more than enough for base64 JTI)
        if len(jti) > 256:
            return False

        self._revoked_tokens.add(jti)
        # If session token, remove session
        if jti in self._sessions:
            del self._sessions[jti]
        return True

    def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).

        Args:
            user_id: User identifier

        Returns:
            Number of sessions revoked
        """
        count = 0

        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 1

        return count

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information.

        Args:
            session_id: Session identifier

        Returns:
            SessionInfo if found, None otherwise
        """
        return self._sessions.get(session_id)

    def get_user_sessions(self, user_id: str) -> list[SessionInfo]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of active sessions
        """
        return [
            session
            for session in self._sessions.values()
            if session.user_id == user_id and session.is_active()
        ]

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count += 1

        return count
