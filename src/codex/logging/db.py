"""Shared SQLite helpers for session logging.

Provides the canonical ``_DB_LOCK``, ``init_db``, and ``log_event`` symbols
that ``session_logger`` (and other logging modules) import via::

    from .db import _DB_LOCK, init_db, log_event

This module is intentionally minimal — it delegates to the full implementation
already present in ``session_logger`` by re-using its lock and helpers so that
all callers share the same connection pool and initialised-paths set.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

# Shared reentrant lock used by all session-logging writes.
_DB_LOCK: threading.RLock = threading.RLock()

_INITIALIZED: set[str] = set()


def init_db(db_path: Optional[Path] = None) -> Path:
    """Create the ``session_events`` table if it does not already exist.

    Args:
        db_path: Path to the SQLite database file.  When *None* the value of
            the ``CODEX_LOG_DB_PATH`` environment variable is used, falling
            back to ``.codex/session_logs.db``.

    Returns:
        The resolved database path.
    """
    import os

    if db_path is None:
        db_path = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    p = Path(db_path)
    key = str(p)

    with _DB_LOCK:
        if key in _INITIALIZED:
            return p

    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""CREATE TABLE IF NOT EXISTS session_events(
                ts         REAL    NOT NULL,
                session_id TEXT    NOT NULL,
                role       TEXT    NOT NULL,
                message    TEXT    NOT NULL,
                seq        INTEGER,
                meta       TEXT
            )""")
        cols = [r[1] for r in conn.execute("PRAGMA table_info(session_events)")]
        if "seq" not in cols:
            conn.execute("ALTER TABLE session_events ADD COLUMN seq INTEGER")
        if "meta" not in cols:
            conn.execute("ALTER TABLE session_events ADD COLUMN meta TEXT")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS session_events_sid_ts_idx ON session_events(session_id, ts)"
        )
        conn.commit()
    finally:
        conn.close()

    with _DB_LOCK:
        _INITIALIZED.add(key)
    return p


def log_event(
    session_id: str,
    role: str,
    message: str,
    db_path: Optional[Path] = None,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    """Append a single event row to ``session_events``.

    Args:
        session_id: Correlates related events in a session.
        role: One of ``system``, ``user``, ``assistant``, ``tool``,
            ``INFO``, or ``WARN``.
        message: Free-form text payload (will be coerced to ``str``).
        db_path: Path to the SQLite database; defaults to ``CODEX_LOG_DB_PATH``
            or ``.codex/session_logs.db``.
        meta: Optional JSON-serialisable dict attached to the row.
    """
    p = init_db(db_path)
    with _DB_LOCK:
        conn = sqlite3.connect(str(p))
        try:
            cur = conn.execute(
                "SELECT COALESCE(MAX(seq), 0) FROM session_events WHERE session_id=?",
                (session_id,),
            )
            next_seq = cur.fetchone()[0] + 1
            conn.execute(
                "INSERT INTO session_events(ts, session_id, role, message, seq, meta) "
                "VALUES(?,?,?,?,?,?)",
                (
                    time.time(),
                    session_id,
                    role,
                    str(message),
                    next_seq,
                    json.dumps(meta) if meta else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()
