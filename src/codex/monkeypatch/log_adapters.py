"""
Adapter for codebases lacking log_event/log_message.
If project already defines them, the existing definitions will use pooled
sqlite via patch injection (see sqlite_patch). Otherwise, these provide a
minimal baseline.
"""
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path


def _resolve_path(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    return Path(db_path) if db_path is not None else Path(os.environ["CODEX_LOG_DB_PATH"])


def _ensure_table(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def log_event(level: str, message: str, meta: str | None = None, db_path: Path | None = None):
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events(
            ts REAL NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def log_message(
    message: str, level: str = "INFO", meta: str | None = None, db_path: Path | None = None
):
    db = _resolve_path(db_path)
    return log_event(level=level, message=message, meta=meta, db_path=db)
