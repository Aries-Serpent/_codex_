"""
Abstract base interface for UserStore persistence backends.

Provides the ``UserRepository`` ABC that all concrete storage backends must
implement.  Concrete implementations include:

- :class:`~codex.auth.in_memory_user_repository.InMemoryUserRepository`
  — default in-process store (preserves current behaviour)
- :class:`~codex.auth.sqlite_user_repository.SQLiteUserRepository`
  — durable single-node SQLite store (``CODEX_USERSTORE_BACKEND=sqlite``)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .user_model import User


class UserRepository(ABC):
    """Abstract interface for user persistence.

    All mutating operations MUST be thread-safe (each concrete class is
    responsible for its own synchronisation).
    """

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def create(self, user: User) -> User:
        """Persist a new user record and return it.

        Args:
            user: Fully populated :class:`~codex.auth.user_store.User`
                (password already hashed).

        Returns:
            The persisted user (may be the same object or a new instance).

        Raises:
            ValueError: If ``username`` or ``email`` already exists.
        """

    @abstractmethod
    def update(self, user: User) -> User:
        """Persist changes to an existing user record.

        Args:
            user: User with updated fields.  ``user_id`` must already exist.

        Returns:
            The updated user.

        Raises:
            KeyError: If ``user.user_id`` is not found.
        """

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """Permanently remove the user record identified by *user_id*.

        Args:
            user_id: Target user.

        Raises:
            KeyError: If *user_id* is not found.
        """

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        """Return the user with *user_id*, or ``None`` if not found."""

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Return the user with *username*, or ``None`` if not found."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Return the user with *email*, or ``None`` if not found."""

    @abstractmethod
    def list_all(self) -> list[User]:
        """Return all user records (active and inactive)."""

    def list(self) -> list[User]:
        """Backward-compatible alias for :meth:`list_all`."""
        return self.list_all()
