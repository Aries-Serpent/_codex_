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

import os
import sqlite3

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except Exception:
    pass
import threading
import time
import uuid
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    _shared_log_event = None
    _shared_init_db = None
    _shared_DB_LOCK = None

# ------------------------------------
# Local, minimal fallbacks (if needed)
# ------------------------------------
_DB_LOCK = _shared_DB_LOCK or threading.RLock()

# Module-level tracker for initialized database paths
INITIALIZED_PATHS: set[str] = set()


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
                   message TEXT NOT NULL
               )"""
        )
        conn.commit()
    finally:
        conn.close()
    return p


def _fallback_log_event(
    session_id: str, role: str, message: str, db_path: Optional[Path] = None
):
    p = init_db(db_path)
    conn = sqlite3.connect(p)
    try:
        conn.execute(
            "INSERT INTO session_events(ts, session_id, role, message) VALUES(?,?,?,?)",
            (time.time(), session_id, role, message),
        )
        conn.commit()
    finally:
        conn.close()


def log_event(session_id: str, role: str, message: str, db_path: Optional[Path] = None):
    """Delegate to shared log_event if available, otherwise fallback."""
    if _shared_log_event is not None:
        return _shared_log_event(session_id, role, message, db_path=db_path)
    return _fallback_log_event(session_id, role, message, db_path=db_path)


_ALLOWED_ROLES = {"system", "user", "assistant", "tool", "INFO", "WARN"}


def get_session_id() -> str:
    return os.getenv("CODEX_SESSION_ID") or str(uuid.uuid4())


def fetch_messages(
    session_id: str, db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    path = Path(db_path or _default_db_path())
    return _fetch_messages_mod.fetch_messages(session_id, db_path=path)


def log_message(session_id: str, role: str, message, db_path: Optional[Path] = None):
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
        log_event(session_id, role, text, db_path=path)


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

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            log_event(
                self.session_id,
                "system",
                f"session_end (exc={exc_type.__name__}: {exc})",
                db_path=self.db_path,
            )
        else:
            log_event(self.session_id, "system", "session_end", db_path=self.db_path)

    def log(self, role: str, message):
        log_message(self.session_id, role, message, db_path=self.db_path)
