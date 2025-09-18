"""Utilities for retrieving logged messages from the session database.

Pooling is controlled by the ``CODEX_SQLITE_POOL`` environment variable with a
legacy fallback to ``CODEX_DB_POOL``. The canonical flag is evaluated for every
``get_conn`` invocation so runtime toggles take effect immediately.
"""

from __future__ import annotations

import contextlib
import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - allow running standalone
    from .config import DEFAULT_LOG_DB
except Exception:  # pragma: no cover - final fallback
    DEFAULT_LOG_DB = Path(".codex/session_logs.db")

logger = logging.getLogger(__name__)

# --- Codex patch: enable sqlite pragmas from environment (best-effort)
try:
    # use fully-qualified package import
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_auto_enable_from_env
except Exception:  # pragma: no cover - best-effort fallback

    def _codex_auto_enable_from_env() -> None:
        return None


_codex_auto_enable_from_env()

_POOL: dict[str, sqlite3.Connection] = {}


def _env_to_bool(var_name: str) -> bool:
    """Normalize environment flag values such as "1", "true", or "yes"."""

    value = os.getenv(var_name)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _configure_connection(conn: sqlite3.Connection) -> None:
    """Apply best-effort SQLite pragmas consistent with session logging."""

    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    try:
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    try:
        conn.execute("PRAGMA foreign_keys=ON;")
    except Exception:
        pass


@contextlib.contextmanager
def get_conn(db_path: str, pooled: bool | None = None):
    """Context-managed connection; pooled when enabled.

    Behavior:
    - If ``pooled`` is not ``None`` the explicit boolean wins.
    - Otherwise pooling is derived from the environment for each call so
      runtime toggles are respected.  We normalize values such as ``"1"``,
      ``"true"``, or ``"yes"`` and keep support for the legacy
      ``CODEX_DB_POOL`` variable for compatibility.
    """

    if pooled is None:
        # Evaluate the environment on every call for predictable overrides.
        sqlite_pool_raw = os.getenv("CODEX_SQLITE_POOL")
        if sqlite_pool_raw is not None:
            pooled = sqlite_pool_raw.strip().lower() in {"1", "true", "yes", "on"}
        else:
            pooled = _env_to_bool("CODEX_DB_POOL")

    _codex_auto_enable_from_env()

    if pooled:
        conn = _POOL.get(db_path)
        if conn is None:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            _codex_auto_enable_from_env()
            _configure_connection(conn)
            _POOL[db_path] = conn
        try:
            yield conn
        finally:
            pass
    else:
        conn = sqlite3.connect(db_path)
        _configure_connection(conn)
        try:
            yield conn
        finally:
            conn.close()


def _default_db_path() -> Path:
    """Resolve the default database path.

    Environment variable ``CODEX_LOG_DB_PATH`` overrides the package default.
    """

    return Path(os.getenv("CODEX_LOG_DB_PATH", str(DEFAULT_LOG_DB)))


def fetch_messages(session_id: str, db_path: Optional[Path] = None):
    """Return logged messages for ``session_id``.

    The database is initialized if missing.  If ``session_events`` has no
    entries for the provided ``session_id`` an empty list is returned without
    emitting warnings.
    """

    path = Path(db_path or _default_db_path())
    # Import lazily to avoid circular import during module initialization
    from .session_logger import init_db

    # Ensure the database and table exist before querying
    init_db(path)

    try:
        with get_conn(str(path)) as conn:
            cur = conn.execute(
                "SELECT ts, role, message FROM session_events WHERE "
                "session_id=? ORDER BY ts ASC",
                (session_id,),
            )
            return [{"ts": r[0], "role": r[1], "message": r[2]} for r in cur.fetchall()]
    except sqlite3.DatabaseError as exc:  # pragma: no cover - defensive
        logger.warning("Failed to fetch messages from %s: %s", path, exc)
        return []
