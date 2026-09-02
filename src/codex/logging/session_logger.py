"""Backward-compatible session logger API.

This module exposes the canonical session logger implementation used by the
``aries_serpent_core`` package under the historical ``codex.logging`` import path.
"""

from aries_serpent_core.logging.session_logger import (
    _ALLOWED_ROLES,
    CONN_POOL,
    INITIALIZED_PATHS,
    USE_POOL,
    SessionLogger,
    fetch_messages,
    get_session_id,
    init_db,
    log_event,
    log_message,
    migrate_legacy_events,
)

__all__ = [
    "CONN_POOL",
    "INITIALIZED_PATHS",
    "SessionLogger",
    "USE_POOL",
    "_ALLOWED_ROLES",
    "fetch_messages",
    "get_session_id",
    "init_db",
    "log_event",
    "log_message",
    "migrate_legacy_events",
]
