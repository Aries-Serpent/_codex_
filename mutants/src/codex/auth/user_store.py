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
import re
import secrets
import threading
import time
from typing import TYPE_CHECKING, Optional

from ..security_utils import sanitize_log_message
from .exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
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
        username = self._require_non_blank(username, "Username")
        email = self._require_non_blank(email, "Email").lower()
        password = self._require_non_blank(password, "Password")

        # Validate username doesn't contain whitespace
        self._validate_username_format(username)
        self._validate_email_format(email)
        self._validate_password_strength(password)

        user = User(
            user_id=secrets.token_hex(16),
            username=username,
            email=email,
            password_hash=self._hasher.hash(password),
            roles=list(roles) if roles else ["user"],
            display_name=display_name,
        )
        try:
            self._repository.create(user)
        except ValueError as exc:
            message = str(exc)
            if "already taken" in message or "already registered" in message:
                raise UserAlreadyExistsError(message) from exc
            raise
        logger.info("User created: %s", sanitize_log_message(username))
        return user

    def update_user(self, user: User) -> User:
        """
        Update an existing user record.

        Args:
            user: The user object with updated fields.

        Returns:
            The updated :class:`User`.

        Raises:
            KeyError: If the user does not exist.
        """
        with self._lock:
            existing = self._repository.get_by_id(user.user_id)  # type: ignore[arg-type]
            if existing is None:
                raise KeyError(f"User '{user.user_id}' not found")
            user.updated_at = time.time()
            self._repository.update(user)
        logger.info("User updated: %s", sanitize_log_message(user.username))
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
        try:
            self._repository.delete(user_id)
        except (UserNotFoundError, KeyError) as exc:  # pragma: no cover - compatibility shim
            raise KeyError(f"User '{user_id}' not found") from exc

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    def get_user(self, user_id: str) -> Optional[User]:
        """Return the :class:`User` for *user_id*, or ``None``."""
        return self._repository.get_by_id(user_id)

    def get_by_user_id(self, user_id: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`get_user`."""
        return self.get_user(user_id)

    def find_by_username(self, username: str) -> Optional[User]:
        """Return the :class:`User` with *username*, or ``None``."""
        return self._repository.get_by_username(username)

    def get_by_username(self, username: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`find_by_username`."""
        return self.find_by_username(username)

    def find_by_email(self, email: str) -> Optional[User]:
        """Return the :class:`User` with *email*, or ``None``."""
        return self._repository.get_by_email(email)

    def get_by_email(self, email: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`find_by_email`."""
        return self.find_by_email(email)

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

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`get_user`."""
        return self.get_user(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`find_by_username`."""
        return self.find_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`find_by_email`."""
        return self.find_by_email(email)

    def get_all_users(self) -> list[User]:
        """Backward-compatible alias for :meth:`list_users`."""
        return self.list_users(include_inactive=True)

    def get_users_by_role(self, role: str) -> list[User]:
        """Return all users with a specific role."""
        return [u for u in self.list_users(include_inactive=True) if role in u.roles]

    def delete_user_by_username(self, username: str) -> None:
        """Delete a user by username.

        Args:
            username: Username to delete

        Raises:
            KeyError: If user with username is not found
        """
        user = self.find_by_username(username)
        if user is None:
            raise KeyError(f"User '{username}' not found")
        self.delete_user(user.user_id)  # type: ignore[arg-type]

    def verify_password(self, user: User, password: str) -> bool:
        """Verify a password against a user's stored hash.

        Args:
            user: User object
            password: Plain-text password to verify

        Returns:
            True if password matches, False otherwise
        """
        return self._hasher.verify(password, user.password_hash)

    def add_role(self, user_id: str, role: str) -> None:
        """Add a role to a user if it is not already present."""
        with self._lock:
            user = self._repository.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(f"User '{user_id}' not found")
            if role not in user.roles:
                user.roles.append(role)
                user.updated_at = time.time()
                self._repository.update(user)

    def remove_role(self, user_id: str, role: str) -> None:
        """Remove a role from a user if present."""
        with self._lock:
            user = self._repository.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(f"User '{user_id}' not found")
            if role in user.roles:
                user.roles.remove(role)
                user.updated_at = time.time()
                self._repository.update(user)

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
        try:
            identifier = self._require_non_blank(username_or_email, "Username or email")
            password = self._require_non_blank(password, "Password")
        except ValueError as e:
            # Convert validation errors to InvalidCredentialsError for consistency
            raise InvalidCredentialsError(str(e)) from e

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
    def _require_non_blank(value: Optional[str], field_name: str) -> str:
        """Validate that a required string value is present and non-blank.

        The original value is preserved so callers can keep meaningful
        leading/trailing whitespace in passwords while still rejecting
        whitespace-only inputs.
        """
        if value is None:
            raise ValueError(f"{field_name} must not be empty")
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")
        return value

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Enforce a minimum password policy.

        Requirements:
            - At least 8 characters long
            - Must contain at least one uppercase letter
            - Must contain at least one lowercase letter
            - Must contain at least one digit
            - Must contain at least one special character

        Raises:
            ValueError: If the policy is not satisfied.
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(ch.isupper() for ch in password)
        has_lower = any(ch.islower() for ch in password)
        has_digit = any(ch.isdigit() for ch in password)
        has_symbol = any(not ch.isalnum() for ch in password)

        errors = []
        if not has_upper:
            errors.append("uppercase letter")
        if not has_lower:
            errors.append("lowercase letter")
        if not has_digit:
            errors.append("digit")
        if not has_symbol:
            errors.append("special character")

        if errors:
            raise ValueError(f"Password must contain at least one {', '.join(errors)}")

    @staticmethod
    def _validate_email_format(email: str) -> None:
        """
        Validate email format.

        Args:
            email: Email address to validate.

        Raises:
            ValueError: If the email format is invalid.
        """
        # Updated email format validation pattern to support unicode characters
        # Supports unicode in both local part and domain
        # Matches: user@domain.tld, user+tag@domain, 用户@例え.jp, etc.
        email_pattern = r"^[\w._%+-]+@[\w.-]+\.[\w]{2,}$"
        if not re.match(email_pattern, email, re.UNICODE):
            raise ValueError("Invalid email format")

    @staticmethod
    def _validate_username_format(username: str) -> None:
        """
        Validate username format.

        Args:
            username: Username to validate.

        Raises:
            ValueError: If the username format is invalid (contains whitespace).
        """
        # Reject usernames with spaces or tabs
        if " " in username or "\t" in username or "\n" in username or "\r" in username:
            raise ValueError("Username cannot contain whitespace characters")
