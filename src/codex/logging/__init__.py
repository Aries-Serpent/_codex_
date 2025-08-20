"""Logging utilities for codex package."""

from pathlib import Path
from typing import Optional

from .fetch_messages import DEFAULT_LOG_DB as _DEFAULT_LOG_DB
from .fetch_messages import fetch_messages as _fetch_messages

DEFAULT_LOG_DB = _DEFAULT_LOG_DB


def fetch_messages(session_id: str, db_path: Optional[Path] = None):
    """Wrapper exposing :func:`fetch_messages.fetch_messages` at package level."""

    path = Path(db_path or DEFAULT_LOG_DB)
    return _fetch_messages(session_id, db_path=path)


__all__ = ["fetch_messages", "DEFAULT_LOG_DB"]
