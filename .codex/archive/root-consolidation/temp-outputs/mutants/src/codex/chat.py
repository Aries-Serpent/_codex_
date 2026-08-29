"""Chat session logging and context management.

This module provides the ChatSession context manager for tracking and logging
conversation state during multi-turn interactions with users and assistants.

Classes:
    ChatSession: Context manager for managing a logged chat conversation.

Examples:
    >>> from codex.chat import ChatSession
    >>> with ChatSession("my-session-id") as session:
    ...     session.log_user("Hello, world!")
    ...     session.log_assistant("Hello! How can I help?")
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from codex.logging.session_logger import log_event

logger = logging.getLogger(__name__)


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

    def __init__(self, session_id: Optional[str] = None, db_path: Optional[str] = None) -> None:
        sid = session_id or os.getenv("CODEX_SESSION_ID") or str(uuid.uuid4())
        self.session_id = sid
        self.db_path = db_path
        self._previous_session_id: Optional[str] = None

    @property
    def _path(self) -> Optional[Path]:
        """Return the db_path as a ``Path``, or ``None`` if unset."""
        return Path(self.db_path) if self.db_path else None

    def __enter__(self) -> ChatSession:
        self._previous_session_id = os.environ.get("CODEX_SESSION_ID")
        os.environ["CODEX_SESSION_ID"] = self.session_id
        log_event(self.session_id, "system", "session_start", db_path=self._path)
        return self

    def log_user(self, message: str) -> None:
        """Record an inbound user message."""
        log_event(self.session_id, "user", message, db_path=self._path)

    def log_assistant(self, message: str) -> None:
        """Record an outbound assistant message."""
        log_event(self.session_id, "assistant", message, db_path=self._path)

    def __exit__(self, exc_type, exc, tb) -> None:
        """Context manager exit protocol.

        Args:
            exc_type: Exception type if an exception occurred, else None.
            exc: Exception instance if an exception occurred, else None.
            tb: Traceback object if an exception occurred, else None.

        Returns:
            None. (The method does not suppress exceptions.)
        """
        try:
            log_event(self.session_id, "system", "session_end", db_path=self._path)
        finally:
            # Always restore the previous session identifier even if logging fails
            if self._previous_session_id is None:
                os.environ.pop("CODEX_SESSION_ID", None)
            else:
                os.environ["CODEX_SESSION_ID"] = self._previous_session_id
            self._previous_session_id = None
