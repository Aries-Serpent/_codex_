"""Archive Database Module

This module provides low-level database operations for the archive backend,
including connection management, schema initialization, and transaction handling.

Classes:
    ArchiveDatabase: Database initialization and connection management

Author: Codex Team
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import sqlalchemy as sa
except (ImportError, ModuleNotFoundError, ValueError, TypeError):  # pragma: no cover
    sa = None

from . import schema  # noqa: E402
from .util import ensure_directory  # noqa: E402

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass

Params = dict[str, Any]


class ArchiveDatabase:
    """Manages database connections, transactions, and schema for archive backend."""

    def __init__(self, backend: str, url: str, *, apply_schema: bool = True) -> None:
        """Initialize database connection for the given backend.

        Args:
            backend: Database backend type ('sqlite', 'postgres', 'mariadb')
            url: Database connection URL
            apply_schema: Whether to apply schema on initialization

        Raises:
            RuntimeError: If sqlalchemy is required but not installed
        """
        self.backend = backend
        self.url = url
        self._conn: sqlite3.Connection | None = None
        self._engine: Any | None = None

        if self.backend == "sqlite":
            path = self._sqlite_path(self.url)
            ensure_directory(path.parent)
            self._conn = sqlite3.connect(str(path))
            self._conn.row_factory = sqlite3.Row
        else:
            if sa is None:  # pragma: no cover - informative guard
                raise RuntimeError(
                    "sqlalchemy is required for non-sqlite archive backends. "
                    "Install sqlalchemy>=2.0"
                )
            self._engine = sa.create_engine(self.url, future=True)

        if apply_schema:
            self.ensure_schema()

    def ensure_schema(self) -> None:
        """Apply the schema bundle for the configured backend."""
        statements = schema.statements_for(self.backend)
        with self._transaction() as execute:
            for statement in statements:
                execute(statement)

    @contextmanager
    def _transaction(self) -> Iterator[Callable[[str, Params | None, bool, bool], Any]]:
        """Context manager for database transactions.

        Yields a callable that executes SQL statements within a transaction.
        """
        if self.backend == "sqlite":
            if self._conn is None:
                raise RuntimeError("SQLite connection is not initialised")
            cursor = self._conn.cursor()
            try:

                def execute_sql(
                    sql: str,
                    params: Params | None = None,
                    fetchone: bool = False,
                    fetchall: bool = False,
                ) -> Any:
                    return self._sqlite_execute(cursor, sql, params, fetchone, fetchall)

                yield execute_sql
                self._conn.commit()
            except (ValueError, TypeError, RuntimeError):
                logger.warning("Exception occurred", exc_info=True)
                self._conn.rollback()
                raise
            finally:
                cursor.close()
        else:
            if self._engine is None:
                raise RuntimeError("SQLAlchemy engine is not initialised")
            with self._engine.begin() as connection:

                def execute_sql(
                    sql: str,
                    params: Params | None = None,
                    fetchone: bool = False,
                    fetchall: bool = False,
                ) -> Any:
                    return self._sqlalchemy_execute(connection, sql, params, fetchone, fetchall)

                yield execute_sql

    def _sqlite_execute(
        self,
        cursor: sqlite3.Cursor,
        sql: str,
        params: Params | None,
        fetchone: bool,
        fetchall: bool,
    ) -> Any:
        """Execute SQL statement on SQLite connection."""
        parameters = params or {}
        cursor.execute(sql, parameters)
        if fetchone:
            row = cursor.fetchone()
            return dict(row) if row is not None else None
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        return None

    def _sqlalchemy_execute(
        self,
        connection: Any,
        sql: str,
        params: Params | None,
        fetchone: bool,
        fetchall: bool,
    ) -> Any:
        """Execute SQL statement on SQLAlchemy connection."""
        statement = sa.text(sql)
        result = connection.execute(statement, params or {})
        if fetchone:
            row = result.mappings().first()
            return dict(row) if row is not None else None
        if fetchall:
            return [dict(row) for row in result.mappings().all()]
        return None

    def _sqlite_path(self, url: str) -> Path:
        """Parse SQLite URL and extract path using proper URL parsing (CWE-20 fix)."""
        parsed = urlparse(url)

        # Handle sqlite:// or sqlite:/// scheme
        if parsed.scheme == "sqlite":
            # Reconstruct path from netloc + path to handle both:
            # - sqlite://relative/db.sqlite (netloc='relative', path='/db.sqlite')
            # - sqlite:///./.codex/archive.sqlite (netloc='', path='/./.codex/archive.sqlite')
            full_path = parsed.netloc + parsed.path

            if not full_path:
                # Fallback to treating as bare path if no scheme
                path = url
            else:
                # Strip leading slash only for relative-style paths (not absolute paths)
                # Absolute paths (starting with /) or Windows drive letters (C:) stay as-is
                if full_path.startswith("/./"):
                    # Relative path with ./ prefix: strip the leading /
                    path = full_path[1:]
                elif full_path.startswith("/") and not (len(full_path) > 2 and full_path[2] == ":"):
                    # Absolute path (starts with / but not Windows C:/ style)
                    path = full_path
                else:
                    path = full_path
        else:
            # No scheme detected, treat as bare path
            path = url

        return Path(path).expanduser().resolve()
