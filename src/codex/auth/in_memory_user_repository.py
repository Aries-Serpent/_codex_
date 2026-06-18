"""
In-memory :class:`UserRepository` implementation (default backend).

Preserves the original ``UserStore`` behaviour: all users are held in a plain
Python ``dict`` keyed by ``user_id``.  Thread-safe via an internal
``threading.RLock``.
"""

from __future__ import annotations

import threading

from ..security_utils import sanitize_log_message
from .user_model import User
from .user_repository import UserRepository


class UserNotFoundError(Exception):
    """Raised when a user is not found in the repository."""


class InMemoryUserRepository(UserRepository):
    """Thread-safe, in-process user store backed by a plain dict.

    This is the default backend used when ``CODEX_USERSTORE_BACKEND`` is
    unset or set to ``"memory"``.  All state is lost on process restart.
    """

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._lock: threading.RLock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create(self, user: User) -> User:
        """Store *user* and return it.

        Raises:
            ValueError: If required user fields are empty or ``username`` or ``email`` already exists.
        """
        if not user.user_id:
            raise ValueError("User ID must not be empty")
        if not user.username.strip():
            raise ValueError("Username must not be empty")
        if not user.email.strip():
            raise ValueError("Email must not be empty")
        if not user.password_hash:
            raise ValueError("Password hash must not be empty")

        with self._lock:
            try:
                self.get_by_username(user.username)
                raise ValueError(
                    f"Username '{sanitize_log_message(user.username)}' is already taken"
                )
            except UserNotFoundError:
                pass
            try:
                self.get_by_email(user.email)
                raise ValueError(
                    f"Email '{sanitize_log_message(user.email)}' is already registered"
                )
            except UserNotFoundError:
                pass
            self._users[user.user_id] = user
        return user

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

    def get_by_id(self, user_id: str) -> User:
        with self._lock:
            user = self._users.get(user_id)
            if user is None:
                raise UserNotFoundError(f"User '{user_id}' not found")
            return user

    def get_by_username(self, username: str) -> User:
        username = username.strip()
        with self._lock:
            for user in self._users.values():
                if user.username == username:
                    return user
        raise UserNotFoundError(f"User with username '{username}' not found")

    def get_by_email(self, email: str) -> User:
        email = email.strip().lower()
        with self._lock:
            for user in self._users.values():
                if user.email == email:
                    return user
        raise UserNotFoundError(f"User with email '{email}' not found")

    def list_all(self) -> list[User]:
        with self._lock:
            return list(self._users.values())
