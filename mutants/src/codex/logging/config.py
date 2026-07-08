"""Configuration defaults for Codex logging helpers.

Environment variables:

``CODEX_LOG_DB_PATH``
    Override default SQLite path for session events.
``CODEX_SQLITE_POOL``
    If set to ``"1"``, reuse SQLite connections for logging.
"""

from pathlib import Path

# Default location for session logs database
DEFAULT_LOG_DB = Path(".codex/session_logs.db")
