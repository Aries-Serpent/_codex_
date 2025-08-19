"""
Adapter for codebases lacking log_event/log_message.
If project already defines them, the existing definitions will use pooled
sqlite via patch injection (see sqlite_patch). Otherwise, these provide a
minimal baseline.
"""
import os, sqlite3, time

_DB_PATH = os.getenv("CODEX_SQLITE_DB", "codex_data.sqlite3")


def _ensure_table(path: str) -> None:
    """Create generic app_log table if it doesn't exist."""

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in (
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    ):
        conn.close()


def _ensure_session_table(path: str) -> None:
    """Create session_events table expected by tests if missing."""

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events(
            ts REAL NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in (
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    ):
        conn.close()


def log_event(level: str, message: str, meta: str | None = None, db_path: str | None = None):
    """Insert a log record into ``app_log`` table.

    Args:
        level: Severity level string.
        message: Text message to store.
        meta: Optional metadata string.
        db_path: Override SQLite database path; defaults to ``_DB_PATH``.
    """

    path = db_path or _DB_PATH
    _ensure_table(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log(ts, level, message, meta) VALUES(?,?,?,?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in (
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    ):
        conn.close()


def log_message(
    session_id: str,
    role: str,
    message: str,
    db_path: str | None = None,
):
    """Store a session event in ``session_events`` table."""

    path = db_path or _DB_PATH
    _ensure_session_table(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO session_events(ts, session_id, role, message) VALUES(?,?,?,?)",
        (time.time(), session_id, role, message),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in (
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    ):
        conn.close()
