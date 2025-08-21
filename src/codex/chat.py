"""Simple chat session helper that logs messages via ``log_event``.

This module provides a ``ChatSession`` context manager that initializes
``SessionLogger`` on entry, records user and assistant messages, and ensures
the session is closed on exit. The current session ID is propagated via the
``CODEX_SESSION_ID`` environment variable so that other components can access it
consistently.

Example
-------
>>> from src.codex.chat import ChatSession
>>> with ChatSession("demo") as chat:
...     chat.log_user("hi")
...     chat.log_assistant("hello")
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

from src.codex.logging.session_logger import log_event


class ChatSession:
    """Context manager for logging a chat conversation.

    Parameters
    ----------
    session_id:
        Optional explicit session identifier. If omitted, uses the existing
        ``CODEX_SESSION_ID`` environment variable or generates a new UUID4.
    db_path:
        Optional path to the SQLite database.
    """

    def __init__(
        self, session_id: Optional[str] = None, db_path: Optional[str] = None
    ) -> None:
        sid = session_id or os.getenv("CODEX_SESSION_ID") or str(uuid.uuid4())
        self.session_id = sid
        self.db_path = db_path

    def __enter__(self) -> ChatSession:
        os.environ["CODEX_SESSION_ID"] = self.session_id
        db = self.db_path
        path = Path(db) if db else None
        log_event(self.session_id, "system", "session_start", db_path=path)
        return self

    def log_user(self, message: str) -> None:
        """Record an inbound user message."""
        role = "user"
        db = self.db_path
        path = Path(db) if db else None
        log_event(self.session_id, role, message, db_path=path)

    def log_assistant(self, message: str) -> None:
        """Record an outbound assistant message."""
        role = "assistant"
        db = self.db_path
        path = Path(db) if db else None
        log_event(self.session_id, role, message, db_path=path)

    def __exit__(self, exc_type, exc, tb) -> None:
        """Context manager exit protocol.

        Args:
            exc_type: Exception type if an exception occurred, else None.
            exc: Exception instance if an exception occurred, else None.
            tb: Traceback object if an exception occurred, else None.

        Returns:
            None. (The method does not suppress exceptions.)
        """
        db = self.db_path
        path = Path(db) if db else None
        log_event(self.session_id, "system", "session_end", db_path=path)
        os.environ.pop("CODEX_SESSION_ID", None)
