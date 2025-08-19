"""Utilities for retrieving logged messages from the session database."""

from __future__ import annotations

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

    conn = sqlite3.connect(path)
    try:
        cur = conn.execute(
            "SELECT ts, role, message FROM session_events WHERE "
            "session_id=? ORDER BY ts ASC",
            (session_id,),
        )
        return [{"ts": r[0], "role": r[1], "message": r[2]} for r in cur.fetchall()]
    except sqlite3.DatabaseError as exc:  # pragma: no cover - defensive
        logger.warning("Failed to fetch messages from %s: %s", path, exc)
        return []
    finally:
        conn.close()
