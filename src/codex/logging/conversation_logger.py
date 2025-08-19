"""High-level conversation logging wrapper.

Provides start_session, log_message, and end_session helpers that forward to
``codex.logging.session_logger.log_event``. All helpers accept an optional
``db_path`` to override the default SQLite database location.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Callable, Optional

from . import session_logger


def start_session(session_id: str, db_path: Optional[str] = None) -> None:
    """Record the start of a session."""
    session_logger.log_event(
        session_id, "system", "session_start", Path(db_path) if db_path else None
    )


def log_message(
    session_id: str,
    role: str,
    text: str,
    db_path: Optional[str] = None,
) -> None:
    """Log a user/assistant/system message."""
    session_logger.log_event(session_id, role, text, Path(db_path) if db_path else None)


def end_session(session_id: str, db_path: Optional[str] = None) -> None:
    """Record the end of a session."""
    session_logger.log_event(
        session_id, "system", "session_end", Path(db_path) if db_path else None
    )


def _cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["start", "message", "end"], required=True)
    parser.add_argument(
        "--session-id", dest="sid", default=os.getenv("CODEX_SESSION_ID", "")
    )
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
        from src.codex.logging.session_hooks import session as session_ctx
    except Exception:  # pragma: no cover - helper optional
        session_ctx = None
    if session_ctx:
        with session_ctx():
            _cli()
    else:
        _cli()
