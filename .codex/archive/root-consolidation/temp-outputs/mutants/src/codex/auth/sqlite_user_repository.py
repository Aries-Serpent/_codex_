"""
SQLite-backed :class:`UserRepository` for durable single-node deployments.

Activate by setting ``CODEX_USERSTORE_BACKEND=sqlite`` (and optionally
``CODEX_USERSTORE_DB_PATH=/path/to/users.db``).

Thread-safety: all public methods are protected by an internal
``threading.RLock`` so multiple threads (e.g. multiple uvicorn worker
threads sharing the same DB file) can safely call any method concurrently.

Write-ahead logging (WAL) is enabled for better concurrent read performance.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional

from ..security_utils import sanitize_log_message
from .user_model import User
from .user_repository import UserRepository

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    email        TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 1,
    roles        TEXT NOT NULL DEFAULT '["user"]',
    display_name TEXT,
    created_at   REAL NOT NULL,
    updated_at   REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email    ON users (email);
"""


def _row_to_user(row: sqlite3.Row) -> User:
    """Convert a database row to a :class:`User` dataclass."""
    return User(
        user_id=row["id"],
        username=row["username"],
        email=row["email"],
        password_hash=row["password_hash"],
        is_active=bool(row["is_active"]),
        roles=json.loads(row["roles"]),
        display_name=row["display_name"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class SQLiteUserRepository(UserRepository):
    """Thread-safe SQLite backend for single-node deployments.

    Args:
        db_path: Path to the SQLite database file, or ``":memory:"`` for a
            purely in-process database (useful for testing).
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path: str = str(db_path)
        self._lock: threading.RLock = threading.RLock()
        # Cache a single connection so that :memory: databases are shared
        # across all method calls on this instance.
        self._conn: sqlite3.Connection = self._make_conn()
        self._init_schema()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _make_conn(self) -> sqlite3.Connection:
        """Create a new SQLite connection with WAL mode and row factory."""
        conn = sqlite3.connect(self._db_path, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _get_conn(self) -> sqlite3.Connection:
        """Return the cached connection (same connection for the lifetime of this instance)."""
        return self._conn

    def _get_connection(self) -> sqlite3.Connection:
        """Alias for :meth:`_get_conn` for backward compatibility."""
        return self._get_conn()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()

    def _init_schema(self) -> None:
        with self._lock, self._get_conn() as conn:
            conn.executescript(_SCHEMA)

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create(self, user: User) -> User:
        """Persist *user* to the database.

        Raises:
            ValueError: If ``username`` or ``email`` already exists.
        """
        with self._lock, self._get_conn() as conn:
            try:
                conn.execute(
                    """
                        INSERT INTO users
                            (id, username, email, password_hash, is_active,
                             roles, display_name, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                    (
                        user.user_id,
                        user.username,
                        user.email,
                        user.password_hash,
                        int(user.is_active),
                        json.dumps(user.roles),
                        user.display_name,
                        user.created_at,
                        user.updated_at,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                msg = str(exc).lower()
                if "username" in msg:
                    raise ValueError(
                        f"Username '{sanitize_log_message(user.username)}' is already taken"
                    ) from exc
                if "email" in msg:
                    raise ValueError(
                        f"Email '{sanitize_log_message(user.email)}' is already registered"
                    ) from exc
                raise ValueError(str(exc)) from exc
        return user

    def create_user(self, user: User) -> User:
        """Alias for :meth:`create` for backward compatibility."""
        return self.create(user)

    def update(self, user: User) -> User:
        """Update an existing user record.

        Raises:
            KeyError: If ``user.user_id`` is not found.
        """
        with self._lock, self._get_conn() as conn:
            cursor = conn.execute(
                """
                    UPDATE users SET
                        username      = ?,
                        email         = ?,
                        password_hash = ?,
                        is_active     = ?,
                        roles         = ?,
                        display_name  = ?,
                        updated_at    = ?
                    WHERE id = ?
                    """,
                (
                    user.username,
                    user.email,
                    user.password_hash,
                    int(user.is_active),
                    json.dumps(user.roles),
                    user.display_name,
                    time.time(),
                    user.user_id,
                ),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"User '{user.user_id}' not found")
        return user

    def delete(self, user_id: str) -> None:
        """Remove the user record.

        Raises:
            KeyError: If *user_id* is not found.
        """
        with self._lock, self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cursor.rowcount == 0:
                raise KeyError(f"User '{user_id}' not found")

    # ------------------------------------------------------------------ #
    # Read / query operations                                              #
    # ------------------------------------------------------------------ #

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._lock, self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_to_user(row) if row else None

    def get_by_username(self, username: str) -> Optional[User]:
        username = username.strip()
        with self._lock, self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return _row_to_user(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        email = email.strip().lower()
        with self._lock, self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return _row_to_user(row) if row else None

    def list_all(self) -> list[User]:
        with self._lock, self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
        return [_row_to_user(r) for r in rows]

    def list_users(self) -> list[User]:
        """Alias for :meth:`list_all` for backward compatibility."""
        return self.list_all()

    def get_user_count(self) -> int:
        """Return the total number of users in the database."""
        with self._lock, self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
        return row["count"] if row else 0
