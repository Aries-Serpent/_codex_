"""Simple chat session helper that logs messages via SessionLogger.

This module provides a ``ChatSession`` context manager that initializes
``SessionLogger`` on entry, captures user and assistant messages, and ensures
the session is closed on exit. The current session ID is propagated via the
``CODEX_SESSION_ID`` environment variable so that other components can access it
consistently.
"""

from __future__ import annotations

import os
import uuid
from typing import Optional

from .logging import conversation_logger as _cl


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
        self._prev_sid: Optional[str] = None

    def __enter__(self) -> ChatSession:
        self._prev_sid = os.getenv("CODEX_SESSION_ID")
        os.environ["CODEX_SESSION_ID"] = self.session_id
        _cl.start_session(self.session_id, db_path=self.db_path)
        return self

    def log_user(self, message: str) -> None:
        """Record an inbound user message."""
        _cl.log_message(self.session_id, "user", message, db_path=self.db_path)

    def log_assistant(self, message: str) -> None:
        """Record an outbound assistant message."""
        _cl.log_message(self.session_id, "assistant", message, db_path=self.db_path)

    def __exit__(self, exc_type, exc, tb) -> None:
        _cl.end_session(self.session_id, db_path=self.db_path)
        if self._prev_sid is None:
            os.environ.pop("CODEX_SESSION_ID", None)
        else:
            os.environ["CODEX_SESSION_ID"] = self._prev_sid
