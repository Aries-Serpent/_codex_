"""High-level conversation logging wrapper.

Provides start_session, log_message, and end_session helpers that forward to
``codex.logging.session_logger.log_event``. All helpers accept an optional
``db_path`` to override the default SQLite database location.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path
from typing import Any, Callable, Optional

from . import session_logger
from .session_logger import _default_db_path


def _connect(path: str):
    cx = sqlite3.connect(path, check_same_thread=False)
    # Enable WAL for one-writer/many-readers (creates a '-wal' sidecar file).
    try:
        cx.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    return cx


def _ensure_wal(db_path: Optional[str]) -> str:
    path = db_path or str(_default_db_path())
    with _connect(path):
        pass
    return path


def _connect(path: str) -> sqlite3.Connection:
    cx = sqlite3.connect(path, check_same_thread=False)
    # Enable WAL for one-writer/many-readers (creates a '-wal' sidecar file).
    try:
        cx.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    return cx


def start_session(session_id: str, db_path: Optional[str] = None) -> None:
    """Record the start of a session."""
    path = _ensure_wal(db_path)
    session_logger.log_event(session_id, "system", "session_start", Path(path) if path else None)


def log_message(
    session_id: str,
    role: str,
    text: str,
    db_path: Optional[str] = None,
) -> None:
    """Log a user/assistant/system message."""
    path = _ensure_wal(db_path)
    session_logger.log_event(session_id, role, text, Path(path) if path else None)


def end_session(session_id: str, db_path: Optional[str] = None) -> None:
    """Record the end of a session."""
    path = _ensure_wal(db_path)
    session_logger.log_event(session_id, "system", "session_end", Path(path) if path else None)


def _cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["start", "message", "end"], required=True)
    parser.add_argument("--session-id", dest="sid", default=os.getenv("CODEX_SESSION_ID", ""))
    parser.add_argument("--role", default="system")
    parser.add_argument("--message", default="")
    parser.add_argument("--db-path", dest="db_path", default=None)
    args = parser.parse_args()

    sid = args.sid or os.getenv("CODEX_SESSION_ID") or ""
    if args.event == "start":
        start_session(sid, db_path=args.db_path)
    elif args.event == "end":
        end_session(sid, db_path=args.db_path)
    else:
        log_message(sid, args.role, args.message, db_path=args.db_path)


if __name__ == "__main__":
    session_ctx: Optional[Callable[[], Any]]
    try:
        from .session_hooks import session as session_ctx
    except Exception:  # pragma: no cover - helper optional
        session_ctx = None
    if session_ctx:
        with session_ctx():
            _cli()
    else:
        _cli()
