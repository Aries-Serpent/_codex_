"""
User model and storage for Codex platform.

Provides a User dataclass, PBKDF2-SHA256 password hasher, and a UserStore
facade that delegates persistence to a pluggable :class:`UserRepository`
backend.

Backends:
    - :class:`~codex.auth.in_memory_user_repository.InMemoryUserRepository`
      — default; data lost on process restart (preserves legacy behaviour)
    - :class:`~codex.auth.sqlite_user_repository.SQLiteUserRepository`
      — durable SQLite; set ``CODEX_USERSTORE_BACKEND=sqlite``

Security notes:
    - Passwords are stored as PBKDF2-HMAC-SHA256 hashes (600 000 iterations).
    - Each password has a unique 32-byte random salt.
    - Timing-safe comparison is used for password verification.
    - For production use set CODEX_USERSTORE_BACKEND=sqlite and configure
      CODEX_USERSTORE_DB_PATH to a persistent file path.
"""

import logging
import os
import secrets
import threading
import time
from typing import TYPE_CHECKING, Optional

from ..security_utils import sanitize_log_message
from .exceptions import (
    InvalidCredentialsError,
)
from .user_model import (  # User + PasswordHasher live here to break cyclic imports
    _HASH_BYTES,
    _SALT_BYTES,
    PasswordHasher,
    User,
)

if TYPE_CHECKING:
    from .user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserStore:
    """
    Facade over a pluggable :class:`~codex.auth.user_repository.UserRepository`.

    The backend is selected at construction time via the *repository*
    parameter.  When no repository is supplied the backend is chosen from the
    ``CODEX_USERSTORE_BACKEND`` environment variable:

    ``CODEX_USERSTORE_BACKEND=memory`` (default)
        In-memory dict — data is lost on restart.  Identical to the legacy
        behaviour.

    ``CODEX_USERSTORE_BACKEND=sqlite``
        Durable SQLite file.  Path is read from ``CODEX_USERSTORE_DB_PATH``
        (defaults to ``codex_users.db`` in the current working directory).

    Thread-safety: all public methods delegate to the underlying repository
    which is responsible for its own synchronisation.  The legacy ``_lock``
    attribute is preserved for backward-compatibility with any code that
    accesses it directly (it is no longer used internally).
    """

    def __init__(
        self,
        hasher: Optional[PasswordHasher] = None,
        repository: "Optional[UserRepository]" = None,
    ) -> None:
        self._hasher = hasher or PasswordHasher()
        if repository is not None:
            self._repository: UserRepository = repository
        else:
            backend = os.environ.get("CODEX_USERSTORE_BACKEND", "memory").lower()
            if backend == "sqlite":
                from .sqlite_user_repository import SQLiteUserRepository

                db_path = os.environ.get("CODEX_USERSTORE_DB_PATH", "codex_users.db")
                self._repository = SQLiteUserRepository(db_path)
            else:
                from .in_memory_user_repository import InMemoryUserRepository

                self._repository = InMemoryUserRepository()
        # Backward-compatibility shim: expose _lock even though it is no longer
        # used internally (the repository manages its own locking).
        self._lock: threading.RLock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[list[str]] = None,
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

        user = User(
            user_id=secrets.token_hex(16),
            username=username,
            email=email,
            password_hash=self._hasher.hash(password),
            roles=list(roles) if roles else ["user"],
            display_name=display_name,
        )
        self._repository.create(user)
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
        self._validate_password_strength(new_password)
        with self._lock:
            user = self._repository.get_by_id(user_id)
            if user is None:
                raise KeyError(f"User '{user_id}' not found")
            user.password_hash = self._hasher.hash(new_password)
            user.updated_at = time.time()
            self._repository.update(user)

    def deactivate_user(self, user_id: str) -> None:
        """
        Mark user as inactive (soft-delete).

        Args:
            user_id: Target user.

        Raises:
            KeyError: If *user_id* does not exist.
        """
        with self._lock:
            user = self._repository.get_by_id(user_id)
            if user is None:
                raise KeyError(f"User '{user_id}' not found")
            user.is_active = False
            user.updated_at = time.time()
            self._repository.update(user)
        logger.info("User deactivated: %s", sanitize_log_message(user.username))

    def delete_user(self, user_id: str) -> None:
        """
        Permanently remove a user record.

        Args:
            user_id: Target user.

        Raises:
            KeyError: If *user_id* does not exist.
        """
        self._repository.delete(user_id)

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    def get_user(self, user_id: str) -> Optional[User]:
        """Return the :class:`User` for *user_id*, or ``None``."""
        return self._repository.get_by_id(user_id)

    def find_by_username(self, username: str) -> Optional[User]:
        """Return the :class:`User` with *username*, or ``None``."""
        return self._repository.get_by_username(username)

    def find_by_email(self, email: str) -> Optional[User]:
        """Return the :class:`User` with *email*, or ``None``."""
        return self._repository.get_by_email(email)

    def list_users(self, include_inactive: bool = False) -> list[User]:
        """
        Return all users.

        Args:
            include_inactive: If ``False`` (default) only active users are
                returned.
        """
        users = self._repository.list_all()
        if include_inactive:
            return users
        return [u for u in users if u.is_active]

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
        """Return user by id; raises ``KeyError`` if not found.

        .. deprecated::
            The internal lock is no longer used here; callers should use
            :meth:`get_user` directly.
        """
        user = self._repository.get_by_id(user_id)
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
