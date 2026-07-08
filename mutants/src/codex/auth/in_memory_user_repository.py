"""
In-memory :class:`UserRepository` implementation (default backend).

Preserves the original ``UserStore`` behaviour: all users are held in a plain
Python ``dict`` keyed by ``user_id``.  Thread-safe via an internal
``threading.RLock``.
"""

from __future__ import annotations

import threading
from typing import Optional

from ..security_utils import sanitize_log_message
from .exceptions import UserNotFoundError
from .user_model import User
from .user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """Thread-safe, in-process user store backed by a plain dict.

    This is the default backend used when ``CODEX_USERSTORE_BACKEND`` is
    unset or set to ``"memory"``.  All state is lost on process restart.
    """

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._lock: threading.RLock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Private helpers (must be called with self._lock already held)       #
    # ------------------------------------------------------------------ #

    def _find_by_username(self, username: str) -> Optional[User]:
        """Return the user with *username*, or ``None`` (lock must be held)."""
        username = username.strip()
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def _find_by_email(self, email: str) -> Optional[User]:
        """Return the user with *email*, or ``None`` (lock must be held)."""
        email = email.strip().lower()
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create(self, user: User) -> User:
        """Store *user* and return it.

        Raises:
            ValueError: If required user fields are empty or ``username`` or ``email`` already exists.
        """  # noqa: E501
        if not user.user_id:
            raise ValueError("User ID must not be empty")
        if not user.username.strip():
            raise ValueError("Username must not be empty")
        if not user.email.strip():
            raise ValueError("Email must not be empty")
        if not user.password_hash:
            raise ValueError("Password hash must not be empty")

        with self._lock:
            if self._find_by_username(user.username) is not None:
                raise ValueError(
                    f"Username '{sanitize_log_message(user.username)}' is already taken"
                )
            if self._find_by_email(user.email) is not None:
                raise ValueError(
                    f"Email '{sanitize_log_message(user.email)}' is already registered"
                )
            self._users[user.user_id] = user
        return user

    def create_user(self, user: User) -> User:
        """Alias for :meth:`create` for backward compatibility."""
        return self.create(user)

    def update(self, user: User) -> User:
        """Overwrite the stored record for *user.user_id*.

        Raises:
            UserNotFoundError: If *user.user_id* is not found.
        """
        with self._lock:
            if user.user_id not in self._users:
                raise UserNotFoundError(f"User '{user.user_id}' not found")
            self._users[user.user_id] = user
        return user

    def delete(self, user_id: str) -> None:
        """Remove the record for *user_id*.

        Raises:
            UserNotFoundError: If *user_id* is not found.
        """
        with self._lock:
            if user_id not in self._users:
                raise UserNotFoundError(f"User '{user_id}' not found")
            del self._users[user_id]

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        with self._lock:
            return self._find_by_username(username)

    def get_by_email(self, email: str) -> Optional[User]:
        with self._lock:
            return self._find_by_email(email)

    def list_all(self) -> list[User]:
        with self._lock:
            return list(self._users.values())

    def list_users(self) -> list[User]:
        """Alias for :meth:`list_all` for backward compatibility."""
        return self.list_all()

    def get_user_count(self) -> int:
        """Return the total number of users in the repository."""
        with self._lock:
            return len(self._users)

    # Legacy backward-compatibility methods using the new names
    def get_user(self, user_id: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`get_by_id`."""
        return self.get_by_id(user_id)

    def get_by_user_id(self, user_id: str) -> Optional[User]:
        """Backward-compatible alias for :meth:`get_by_id`."""
        return self.get_by_id(user_id)

    def delete_user(self, user_id: str) -> None:
        """Backward-compatible alias for :meth:`delete`."""
        return self.delete(user_id)

    def update_user(self, user: User) -> User:
        """Backward-compatible alias for :meth:`update`."""
        return self.update(user)
