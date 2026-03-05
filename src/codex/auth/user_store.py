"""
User model and storage for Codex platform.

Provides a User dataclass, PBKDF2-SHA256 password hasher, and an in-memory
UserStore that can be swapped out for a persistent backend.

Security notes:
    - Passwords are stored as PBKDF2-HMAC-SHA256 hashes (600 000 iterations).
    - Each password has a unique 32-byte random salt.
    - Timing-safe comparison is used for password verification.
    - For production use replace the in-memory UserStore with a database-backed
      implementation.
"""

import hashlib
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..security_utils import sanitize_log_message
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidCredentialsError,
)

logger = logging.getLogger(__name__)

# PBKDF2 parameters — increasing ITERATIONS raises cost for attackers.
_PBKDF2_HASH = "sha256"
_PBKDF2_ITERATIONS = 600_000
_SALT_BYTES = 32
_HASH_BYTES = 32


@dataclass
class User:
    """Immutable user identity record."""

    user_id: str
    username: str
    email: str
    password_hash: str  # "<salt_hex>:<hash_hex>"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    is_active: bool = True
    roles: List[str] = field(default_factory=lambda: ["user"])
    display_name: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Convenience                                                          #
    # ------------------------------------------------------------------ #

    def has_role(self, role: str) -> bool:
        """Return True if the user has *role*."""
        return role in self.roles

    def to_dict(self) -> Dict:
        """Serialise to a dict, omitting the password hash."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "roles": list(self.roles),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PasswordHasher:
    """
    Secure PBKDF2-SHA256 password hasher.

    Uses only the Python standard library so no additional packages are
    required.
    """

    def __init__(
        self,
        iterations: int = _PBKDF2_ITERATIONS,
        salt_bytes: int = _SALT_BYTES,
        hash_bytes: int = _HASH_BYTES,
    ) -> None:
        self._iterations = iterations
        self._salt_bytes = salt_bytes
        self._hash_bytes = hash_bytes

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def hash(self, password: str) -> str:
        """
        Hash *password* and return ``"<salt_hex>:<hash_hex>"``.

        Args:
            password: Plain-text password.

        Returns:
            Salted hash string suitable for storage.

        Raises:
            ValueError: If *password* is empty.
        """
        if not password:
            raise ValueError("Password must not be empty")

        salt = os.urandom(self._salt_bytes)
        digest = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH,
            password.encode("utf-8"),
            salt,
            self._iterations,
            dklen=self._hash_bytes,
        )
        return f"{salt.hex()}:{digest.hex()}"

    def verify(self, password: str, stored_hash: str) -> bool:
        """
        Verify *password* against *stored_hash*.

        Uses :func:`hmac.compare_digest` to avoid timing side-channels.

        Args:
            password: Plain-text password to check.
            stored_hash: Value previously returned by :meth:`hash`.

        Returns:
            ``True`` if the password matches, ``False`` otherwise.
        """
        try:
            salt_hex, hash_hex = stored_hash.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(hash_hex)
        except (ValueError, AttributeError):
            # Malformed hash — treat as verification failure
            return False

        digest = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH,
            password.encode("utf-8"),
            salt,
            self._iterations,
            dklen=self._hash_bytes,
        )
        # Constant-time comparison
        import hmac as _hmac  # noqa: PLC0415 (local import intentional)
        return _hmac.compare_digest(digest, expected)


class UserStore:
    """
    In-memory user repository.

    All lookups are O(n) except by user_id which is O(1).
    For production, replace with a persistent, indexed store.

    Thread-safety: not thread-safe by default.  Wrap with a lock if
    the store is shared across threads.
    """

    def __init__(self, hasher: Optional[PasswordHasher] = None) -> None:
        self._hasher = hasher or PasswordHasher()
        self._users: Dict[str, User] = {}  # user_id -> User

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[List[str]] = None,
        display_name: Optional[str] = None,
    ) -> User:
        """
        Register a new user.

        Args:
            username: Unique username.
            email: Unique e-mail address.
            password: Plain-text password (will be hashed).
            roles: Initial roles (defaults to ``["user"]``).
            display_name: Optional human-readable name.

        Returns:
            The newly created :class:`User`.

        Raises:
            ValueError: If username or e-mail is already taken, or if any
                required field is empty.
            ValueError: If *password* does not meet minimum requirements.
        """
        username = username.strip()
        email = email.strip().lower()

        if not username:
            raise ValueError("Username must not be empty")
        if not email:
            raise ValueError("Email must not be empty")
        if not password:
            raise ValueError("Password must not be empty")

        self._validate_password_strength(password)

        if self.find_by_username(username) is not None:
            raise ValueError(f"Username '{sanitize_log_message(username)}' is already taken")
        if self.find_by_email(email) is not None:
            raise ValueError(f"Email '{sanitize_log_message(email)}' is already registered")

        user = User(
            user_id=secrets.token_hex(16),
            username=username,
            email=email,
            password_hash=self._hasher.hash(password),
            roles=list(roles) if roles else ["user"],
            display_name=display_name,
        )
        self._users[user.user_id] = user
        logger.info("User created: %s", sanitize_log_message(username))
        return user

    def update_password(self, user_id: str, new_password: str) -> None:
        """
        Replace the stored password for *user_id*.

        Args:
            user_id: Target user.
            new_password: New plain-text password.

        Raises:
            KeyError: If *user_id* does not exist.
            ValueError: If *new_password* does not meet requirements.
        """
        user = self._require_user(user_id)
        self._validate_password_strength(new_password)
        user.password_hash = self._hasher.hash(new_password)
        user.updated_at = time.time()

    def deactivate_user(self, user_id: str) -> None:
        """
        Mark user as inactive (soft-delete).

        Args:
            user_id: Target user.

        Raises:
            KeyError: If *user_id* does not exist.
        """
        user = self._require_user(user_id)
        user.is_active = False
        user.updated_at = time.time()
        logger.info("User deactivated: %s", sanitize_log_message(user.username))

    def delete_user(self, user_id: str) -> None:
        """
        Permanently remove a user record.

        Args:
            user_id: Target user.

        Raises:
            KeyError: If *user_id* does not exist.
        """
        self._require_user(user_id)
        del self._users[user_id]

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    def get_user(self, user_id: str) -> Optional[User]:
        """Return the :class:`User` for *user_id*, or ``None``."""
        return self._users.get(user_id)

    def find_by_username(self, username: str) -> Optional[User]:
        """Return the :class:`User` with *username*, or ``None``."""
        username = username.strip()
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def find_by_email(self, email: str) -> Optional[User]:
        """Return the :class:`User` with *email*, or ``None``."""
        email = email.strip().lower()
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def list_users(self, include_inactive: bool = False) -> List[User]:
        """
        Return all users.

        Args:
            include_inactive: If ``False`` (default) only active users are
                returned.
        """
        if include_inactive:
            return list(self._users.values())
        return [u for u in self._users.values() if u.is_active]

    # ------------------------------------------------------------------ #
    # Authentication helper                                                #
    # ------------------------------------------------------------------ #

    def authenticate(self, username_or_email: str, password: str) -> User:
        """
        Verify credentials and return the matching :class:`User`.

        Looks up the user by username first, then by e-mail.

        Args:
            username_or_email: Username or e-mail address.
            password: Plain-text password.

        Returns:
            The authenticated :class:`User`.

        Raises:
            InvalidCredentialsError: If the credentials are wrong or the
                account is not active.
        """
        # Normalise
        identifier = username_or_email.strip()

        user = self.find_by_username(identifier)
        if user is None:
            user = self.find_by_email(identifier)

        if user is None or not user.is_active:
            # Use a dummy hash comparison to avoid timing oracle
            self._hasher.verify(password, "00" * _SALT_BYTES + ":" + "00" * _HASH_BYTES)
            raise InvalidCredentialsError("Invalid username/email or password")

        if not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError("Invalid username/email or password")

        return user

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _require_user(self, user_id: str) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise KeyError(f"User '{user_id}' not found")
        return user

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Enforce a minimum password policy.

        Requirements:
            - At least 8 characters.

        Raises:
            ValueError: If the policy is not satisfied.
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
