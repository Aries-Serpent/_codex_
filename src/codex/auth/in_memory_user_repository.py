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
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create(self, user: User) -> User:
        """Store *user* and return it.

        Raises:
            ValueError: If ``username`` or ``email`` already exists.
        """
        with self._lock:
            if self.get_by_username(user.username) is not None:
                raise ValueError(
                    f"Username '{sanitize_log_message(user.username)}' is already taken"
                )
            if self.get_by_email(user.email) is not None:
                raise ValueError(
                    f"Email '{sanitize_log_message(user.email)}' is already registered"
                )
            self._users[user.user_id] = user
        return user

    def update(self, user: User) -> User:
        """Overwrite the stored record for *user.user_id*.

        Raises:
            KeyError: If *user.user_id* is not found.
        """
        with self._lock:
            if user.user_id not in self._users:
                raise KeyError(f"User '{user.user_id}' not found")
            self._users[user.user_id] = user
        return user

    def delete(self, user_id: str) -> None:
        """Remove the record for *user_id*.

        Raises:
            KeyError: If *user_id* is not found.
        """
        with self._lock:
            if user_id not in self._users:
                raise KeyError(f"User '{user_id}' not found")
            del self._users[user_id]

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        username = username.strip()
        with self._lock:
            for user in self._users.values():
                if user.username == username:
                    return user
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        email = email.strip().lower()
        with self._lock:
            for user in self._users.values():
                if user.email == email:
                    return user
        return None

    def list_all(self) -> list[User]:
        with self._lock:
            return list(self._users.values())
