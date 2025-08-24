"""Session logging utilities for Codex.

Provides:
- `SessionLogger`: context manager logging session_start/session_end via
  `log_event`.
- `log_message(session_id, role, message, db_path=None)`:
  validated message logging helper.

If the repo already defines `log_event`, `init_db`, and `_DB_LOCK` under
`codex.logging`, we import and use them. Otherwise we fall back to local,
minimal implementations (scoped in this file) to preserve end-to-end behavior
without polluting global API.

Roles allowed: system|user|assistant|tool|INFO|WARN.

This module is intentionally small and self-contained; it does NOT activate any
GitHub Actions or external services.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except Exception as exc:  # pragma: no cover - defensive
    logging.getLogger(__name__).debug("sqlite auto setup failed: %s", exc)

_fetch_messages_mod = import_module(".fetch_messages", __package__)

try:  # pragma: no cover - allow running standalone
    from .config import DEFAULT_LOG_DB
except Exception:  # pragma: no cover - fallback when not a package
    DEFAULT_LOG_DB = Path(".codex/session_logs.db")

# -------------------------------
# Attempt to import shared helpers
# -------------------------------
try:
    # Expected existing helpers (preferred)
    from .db import _DB_LOCK as _shared_DB_LOCK
    from .db import init_db as _shared_init_db
    from .db import log_event as _shared_log_event
except Exception:
    _shared_DB_LOCK = None
    _shared_init_db = None
    try:  # Fallback: rely on monkeypatch adapters
        from codex.monkeypatch.log_adapters import log_event as _shared_log_event
    except Exception:  # pragma: no cover - nothing available
        _shared_log_event = None

# ------------------------------------
# Local, minimal fallbacks (if needed)
# ------------------------------------
_DB_LOCK = _shared_DB_LOCK or threading.RLock()

# Module-level tracker for initialized database paths
INITIALIZED_PATHS: set[str] = set()

# Optional SQLite connection pool keyed by database path
USE_POOL = os.getenv("CODEX_SQLITE_POOL") == "1"
CONN_POOL: Dict[str, sqlite3.Connection] = {}


def _close_pool() -> None:
    for conn in list(CONN_POOL.values()):
        try:
            conn.close()
        except sqlite3.Error as exc:  # pragma: no cover - defensive
            logging.getLogger(__name__).debug("pool close failed: %s", exc)
    CONN_POOL.clear()


if USE_POOL:
    atexit.register(_close_pool)


def _default_db_path() -> Path:
    """Return default database path, honoring environment variable at call time."""
    return Path(os.getenv("CODEX_LOG_DB_PATH", str(DEFAULT_LOG_DB)))


def init_db(db_path: Optional[Path] = None):
    """Initialize SQLite table for session events if absent."""
    p = Path(db_path or _default_db_path())
    key = str(p)
    if key in INITIALIZED_PATHS:
        return p  # already initialized (no-op)
    INITIALIZED_PATHS.add(key)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS session_events(
                   ts REAL NOT NULL,
                   session_id TEXT NOT NULL,
                   role TEXT NOT NULL,
                   message TEXT NOT NULL,
                   seq INTEGER,
                   meta TEXT
               )"""
        )
        cols = [r[1] for r in conn.execute("PRAGMA table_info(session_events)")]
        if "seq" not in cols:
            conn.execute("ALTER TABLE session_events ADD COLUMN seq INTEGER")
        if "meta" not in cols:
            conn.execute("ALTER TABLE session_events ADD COLUMN meta TEXT")
        # Index `session_id` and `ts` for faster queries and pruning operations.
        conn.execute(
            "CREATE INDEX IF NOT EXISTS session_events_sid_ts_idx "
            "ON session_events(session_id, ts)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS session_events_session_seq_idx "
            "ON session_events(session_id, seq)"
        )
        conn.commit()
    finally:
        conn.close()
    return p


def _fallback_log_event(
    session_id: str,
    role: str,
    message: str,
    db_path: Optional[Path] = None,
    meta: Optional[Dict[str, Any]] = None,
):
    p = init_db(db_path)
    key = str(p)
    if USE_POOL:
        conn = CONN_POOL.get(key)
        if conn is None:
            conn = sqlite3.connect(p, check_same_thread=False)
            CONN_POOL[key] = conn
    else:
        conn = sqlite3.connect(p)
    try:
        cur = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) FROM session_events WHERE session_id=?",
            (session_id,),
        )
        next_seq = cur.fetchone()[0] + 1
        conn.execute(
            "INSERT INTO session_events("
            "ts, session_id, role, message, seq, meta) "
            "VALUES(?,?,?,?,?,?)",
            (
                time.time(),
                session_id,
                role,
                message,
                next_seq,
                json.dumps(meta) if meta else None,
            ),
        )
        conn.commit()
    except Exception:
        if USE_POOL:
            try:
                conn.close()
            except sqlite3.Error as exc:  # pragma: no cover - defensive
                logging.getLogger(__name__).debug("pool conn close failed: %s", exc)
            CONN_POOL.pop(key, None)
        raise
    finally:
        if not USE_POOL:
            conn.close()


def log_event(
    session_id: str,
    role: str,
    message: str,
    db_path: Optional[Path] = None,
    meta: Optional[Dict[str, Any]] = None,
):
    """Delegate to shared log_event if available, otherwise fallback."""
    if _shared_log_event is not None:
        if (
            getattr(_shared_log_event, "__module__", "")
            == "codex.monkeypatch.log_adapters"
        ):
            _fallback_log_event(session_id, role, message, db_path=db_path, meta=meta)
            try:
                _shared_log_event(session_id, role, message, db_path=db_path, meta=meta)
            except TypeError:
                _shared_log_event(session_id, role, message, db_path=db_path)
            return
        try:
            _shared_log_event(session_id, role, message, db_path=db_path, meta=meta)
        except TypeError:
            _shared_log_event(session_id, role, message, db_path=db_path)
        return
    return _fallback_log_event(session_id, role, message, db_path=db_path, meta=meta)


_ALLOWED_ROLES = {"system", "user", "assistant", "tool", "INFO", "WARN"}


def get_session_id() -> str:
    """Return current session ID, generating and persisting if absent.

    If ``CODEX_SESSION_ID`` is not set, a new UUID is generated, stored in the
    process environment, and returned. Subsequent calls in the same process will
    return the same value.
    """

    sid = os.getenv("CODEX_SESSION_ID")
    if sid:
        return sid
    sid = str(uuid.uuid4())
    os.environ["CODEX_SESSION_ID"] = sid
    return sid


def fetch_messages(
    session_id: str, db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    path = Path(db_path or _default_db_path())
    return _fetch_messages_mod.fetch_messages(session_id, db_path=path)


def log_message(
    session_id: str,
    role: str,
    message,
    db_path: Optional[Path] = None,
    meta: Optional[Dict[str, Any]] = None,
):
    """Validate role, normalize message to string, ensure DB init, and write.

    Args:
        session_id: Correlates related events.
        role: One of {system,user,assistant,tool,INFO,WARN}.
        message: Any object; will be coerced to str().
        db_path: Optional path (Path/str). If None, uses CODEX_LOG_DB_PATH or
            DEFAULT_LOG_DB.

    Usage:
        >>> from codex.logging.session_logger import log_message
        >>> log_message("S1", "user", "hi there")
    """
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"invalid role {role!r}; expected one of {_ALLOWED_ROLES}")
    text = message if isinstance(message, str) else str(message)
    path = Path(db_path) if db_path else _default_db_path()
    init_db(path)
    with _DB_LOCK:
        log_event(session_id, role, text, db_path=path, meta=meta)


@dataclass
class SessionLogger:
    """Context manager for session-scoped logging.

    Example:
        >>> from codex.logging.session_logger import SessionLogger
        >>> with SessionLogger(session_id="dev-session") as sl:
        ...     sl.log("user", "hi")
        ...     sl.log("assistant", "hello")
    """

    session_id: str
    db_path: Optional[Path] = None

    def __enter__(self) -> "SessionLogger":
        log_event(self.session_id, "system", "session_start", db_path=self.db_path)
        return self

    def __exit__(self, exc_type, exc, tb) -> Literal[False]:
        try:
            if exc_type is not None:
                log_event(
                    self.session_id,
                    "system",
                    f"session_end (exc={exc_type.__name__}: {exc})",
                    db_path=self.db_path,
                )
            else:
                log_event(
                    self.session_id,
                    "system",
                    "session_end",
                    db_path=self.db_path,
                )
        except Exception:
            import logging

            logging.exception("session_end DB log failed")
        return False

    def log(self, role: str, message):
        log_message(self.session_id, role, message, db_path=self.db_path)


def migrate_legacy_events(db_path: Optional[Path] = None) -> None:
    """Backfill ``seq`` for rows missing it and remove duplicate start/end events."""

    path = init_db(db_path)
    conn = sqlite3.connect(path)
    try:
        conn.execute("BEGIN")
        # Backfill seq for rows lacking it
        cur = conn.execute(
            "SELECT DISTINCT session_id FROM session_events WHERE seq IS NULL"
        )
        for (sid,) in cur.fetchall():
            max_seq = conn.execute(
                "SELECT COALESCE(MAX(seq),0) FROM session_events WHERE session_id=?",
                (sid,),
            ).fetchone()[0]
            rows = conn.execute(
                "SELECT rowid FROM session_events WHERE session_id=? "
                "AND seq IS NULL ORDER BY ts",
                (sid,),
            ).fetchall()
            for row in rows:
                max_seq += 1
                conn.execute(
                    "UPDATE session_events SET seq=? WHERE rowid=?", (max_seq, row[0])
                )
        # Remove duplicate start/end events
        cur = conn.execute(
            "SELECT DISTINCT session_id FROM session_events "
            "WHERE message IN ('session_start','session_end')"
        )
        for (sid,) in cur.fetchall():
            start_ids = [
                r[0]
                for r in conn.execute(
                    "SELECT rowid FROM session_events WHERE session_id=? "
                    "AND message='session_start' ORDER BY ts",
                    (sid,),
                ).fetchall()
            ]
            for rid in start_ids[1:]:
                conn.execute("DELETE FROM session_events WHERE rowid=?", (rid,))
            end_ids = [
                r[0]
                for r in conn.execute(
                    "SELECT rowid FROM session_events WHERE session_id=? "
                    "AND message='session_end' ORDER BY ts DESC",
                    (sid,),
                ).fetchall()
            ]
            for rid in end_ids[1:]:
                conn.execute("DELETE FROM session_events WHERE rowid=?", (rid,))
        conn.commit()
    finally:
        conn.close()
