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
from pathlib import Path
from typing import Any, Callable, Optional

_log_event: Callable[[str, str, str, Path | None], Any]
try:
    from .logging.session_logger import (
        log_event as _log_event,  # type: ignore[assignment]
    )
except Exception:  # pragma: no cover - fallback to adapter
    try:  # pragma: no cover - best effort
        from .monkeypatch.log_adapters import (
            log_event as _log_event,  # type: ignore[assignment]
        )
    except Exception:  # pragma: no cover - last resort no-op

        def _log_event(
            session_id: str, role: str, message: str, db_path: Path | None = None
        ) -> None:
            return None


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
        path = Path(self.db_path) if self.db_path else None
        _log_event(self.session_id, "system", "session_start", path)
        return self

    def log_user(self, message: str) -> None:
        """Record an inbound user message."""
        path = Path(self.db_path) if self.db_path else None
        _log_event(self.session_id, "user", message, path)

    def log_assistant(self, message: str) -> None:
        """Record an outbound assistant message."""
        path = Path(self.db_path) if self.db_path else None
        _log_event(self.session_id, "assistant", message, path)

    def __exit__(self, exc_type, exc, tb) -> None:
        """Context manager exit protocol.

        Args:
            exc_type: Exception type if an exception occurred, else None.
            exc: Exception instance if an exception occurred, else None.
            tb: Traceback object if an exception occurred, else None.

        Returns:
            None. (The method does not suppress exceptions.)
        """
        path = Path(self.db_path) if self.db_path else None
        _log_event(self.session_id, "system", "session_end", path)
        os.environ.pop("CODEX_SESSION_ID", None)
