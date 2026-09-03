"""
Thread-safe Session Database Wrapper (Phase 6)

Wraps SessionDB with comprehensive concurrency protection:
- Connection pooling with per-thread connections
- RLock for write operations
- Read operations use read-write lock for Faiss
- Deadlock recovery with exponential backoff
- Monitoring and metrics collection
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Any, Generator, Optional

from .concurrency import (
    DeadlockRecovery,
    LockMetrics,
    SQLiteConnectionPool,
    log_error,
    save_metrics,
)

logger = logging.getLogger(__name__)


class ThreadSafeSessionDB:
    """
    Thread-safe wrapper around SessionDB for Phase 6 concurrency.

    Features:
    - Connection pooling (max 20 per-thread connections)
    - RLock for write operations
    - WAL mode for concurrent access
    - 30-second transaction timeout
    - Deadlock recovery with exponential backoff
    - Lock contention monitoring
    - Comprehensive error logging
    """

    def __init__(
        self,
        db_path: str = ".codex/sessions.db",
        max_connections: int = 20,
        timeout: float = 30.0,
        metrics_path: str = ".codex/concurrency_metrics.json",
        errors_path: str = ".codex/concurrency_errors.log",
    ):
        """Initialize thread-safe session DB."""
        self.db_path = db_path
        self.metrics_path = metrics_path
        self.errors_path = errors_path

        # Concurrency primitives
        self._connection_pool = SQLiteConnectionPool(
            db_path=db_path,
            max_connections=max_connections,
            timeout=timeout,
            wal_mode=True,
        )
        self._write_lock = threading.RLock()
        self._metrics = LockMetrics()

        # Ensure schema exists
        self._ensure_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get thread-local connection from pool."""
        conn = self._connection_pool.get_connection()
        try:
            yield conn
        except sqlite3.OperationalError as e:
            type(e).__name__
            logger.error("Database error: <ERROR_TYPE>")
            log_error(e, "database_operation", self.errors_path)
            raise

    @contextmanager
    def _write_operation(self) -> Generator[None, None, None]:
        """Context manager for write operations with lock."""
        start_time = time.time()
        acquired = False

        try:
            acquired = self._write_lock.acquire(timeout=30)
            if not acquired:
                raise TimeoutError("Write lock timeout (30s)")

            self._metrics.lock_held_count += 1
            yield

        finally:
            wait_ms = (time.time() - start_time) * 1000
            self._metrics.add_wait_time(wait_ms)

            if acquired:
                self._write_lock.release()

    def _ensure_schema(self) -> None:
        """Create schema if it doesn't exist."""
        try:
            conn = self._connection_pool.get_connection()
            cursor = conn.cursor()

            # Check if sessions table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            if cursor.fetchone():
                return  # Schema already exists

            # Create schema
            schema_sql = """
            PRAGMA foreign_keys = ON;
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;
            PRAGMA cache_size = -64000;

            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                pr_number INTEGER,
                branch TEXT,
                timestamp TEXT,
                git_sha TEXT,
                status TEXT NOT NULL CHECK (status IN ('pending', 'in-progress', 'complete', 'failed')),
                agent_name TEXT,
                duration_minutes INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id)
            );

            CREATE TABLE IF NOT EXISTS session_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                UNIQUE(session_id, key)
            );

            CREATE TABLE IF NOT EXISTS session_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                pattern_id TEXT NOT NULL,
                pattern_name TEXT,
                success BOOLEAN DEFAULT 1,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS session_outcomes (
                session_id TEXT PRIMARY KEY,
                ci_checks_green INTEGER DEFAULT 0,
                ci_checks_red INTEGER DEFAULT 0,
                ci_checks_total INTEGER DEFAULT 0,
                test_coverage REAL,
                linting_errors INTEGER DEFAULT 0,
                linting_warnings INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS session_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_timestamp_status ON sessions(timestamp DESC, status);
            CREATE INDEX IF NOT EXISTS idx_pr_number_branch ON sessions(pr_number, branch);
            CREATE INDEX IF NOT EXISTS idx_agent_name ON sessions(agent_name);
            CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id);
            CREATE INDEX IF NOT EXISTS idx_created_at ON sessions(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_metadata_session_key ON session_metadata(session_id, key);
            CREATE INDEX IF NOT EXISTS idx_patterns_session ON session_patterns(session_id);
            CREATE INDEX IF NOT EXISTS idx_events_session_time ON session_events(session_id, timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_outcomes_session ON session_outcomes(session_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_status_created ON sessions(status, created_at DESC);
            """  # noqa: E501

            conn.executescript(schema_sql)
            conn.commit()
            logger.info(f"Schema initialized for {self.db_path}")

        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error("Schema initialization failed: <ERROR_TYPE>")
            log_error(e, "schema_init", self.errors_path)
            raise

    def insert_session(self, session: dict[str, Any]) -> bool:
        """Insert session with write lock and deadlock recovery."""

        def _insert() -> bool:
            with self._write_operation():
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO sessions
                        (session_id, pr_number, branch, timestamp, git_sha, status, agent_name, duration_minutes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,  # noqa: E501
                        (
                            session.get("session_id"),
                            session.get("pr_number"),
                            session.get("branch"),
                            session.get("timestamp"),
                            session.get("git_sha"),
                            session.get("status", "pending"),
                            session.get("agent_name"),
                            session.get("duration_minutes"),
                        ),
                    )
                    conn.commit()
            return True

        try:
            return DeadlockRecovery.retry_with_backoff(_insert, max_retries=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error("Failed to insert session: <ERROR_TYPE>")
            log_error(e, "insert_session", self.errors_path)
            return False

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get session by ID (thread-safe read)."""

        def _get() -> Optional[dict[str, Any]]:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

        try:
            return DeadlockRecovery.retry_with_backoff(_get, max_retries=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error(f"Failed to get session {session_id}: <ERROR_TYPE>")
            log_error(e, "get_session", self.errors_path)
            return None

    def query_sessions(
        self,
        status: Optional[str] = None,
        agent_name: Optional[str] = None,
        days: int = 7,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query sessions with optional filters (thread-safe read)."""

        def _query() -> list[dict[str, Any]]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Build query
                query = "SELECT * FROM sessions WHERE 1=1"
                params: list[Any] = []

                if status:
                    query += " AND status = ?"
                    params.append(status)

                if agent_name:
                    query += " AND agent_name = ?"
                    params.append(agent_name)

                # Date filter
                query += " AND datetime(created_at) > datetime('now', '-' || ? || ' days')"
                params.append(days)

                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]

        try:
            return DeadlockRecovery.retry_with_backoff(_query, max_retries=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error("Failed to query sessions: <ERROR_TYPE>")
            log_error(e, "query_sessions", self.errors_path)
            return []

    def update_session_status(self, session_id: str, new_status: str) -> bool:
        """Update session status (thread-safe write)."""

        def _update() -> bool:
            with self._write_operation():
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE sessions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",  # noqa: E501
                        (new_status, session_id),
                    )
                    conn.commit()
                    return cursor.rowcount > 0

        try:
            return DeadlockRecovery.retry_with_backoff(_update, max_retries=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error(f"Failed to update session {session_id}: <ERROR_TYPE>")
            log_error(e, "update_session_status", self.errors_path)
            return False

    def search_sessions(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """Search sessions by query string (thread-safe read)."""

        def _search() -> list[dict[str, Any]]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Search across multiple columns
                search_query = "%{}%".format(query)
                cursor.execute(
                    """
                    SELECT * FROM sessions
                    WHERE agent_name LIKE ? OR branch LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (search_query, search_query, limit),
                )
                return [dict(row) for row in cursor.fetchall()]

        try:
            return DeadlockRecovery.retry_with_backoff(_search, max_retries=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error("Failed to search sessions: <ERROR_TYPE>")
            log_error(e, "search_sessions", self.errors_path)
            return []

    def archive_session(self, session_id: str, reason: str = "archive") -> bool:
        """Archive session (thread-safe write with exclusive lock)."""

        def _archive() -> bool:
            with self._write_operation():
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    # Mark session as archived
                    cursor.execute(
                        """
                        UPDATE sessions
                        SET status = 'archived', updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = ?
                        """,
                        (session_id,),
                    )

                    # Add archive metadata
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO session_metadata
                        (session_id, key, value)
                        VALUES (?, 'archive_reason', ?)
                        """,
                        (session_id, reason),
                    )

                    conn.commit()
                    return cursor.rowcount > 0

        try:
            return DeadlockRecovery.retry_with_backoff(_archive, max_retries=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error(f"Failed to archive session {session_id}: <ERROR_TYPE>")
            log_error(e, "archive_session", self.errors_path)
            return False

    def get_metrics(self) -> dict[str, Any]:
        """Get current lock metrics."""
        return self._metrics.to_dict()

    def save_metrics(self) -> None:
        """Save metrics to JSON file."""
        metrics_dict = {
            "timestamp": time.time(),
            "db_path": self.db_path,
            "connection_pool": self._connection_pool.metrics.to_dict(),
            "write_lock": self._metrics.to_dict(),
        }
        save_metrics(metrics_dict, self.metrics_path)  # type: ignore[arg-type]

    def cleanup(self) -> None:
        """Clean up connection pool without relying on __del__."""
        pool = getattr(self, "_connection_pool", None)
        if pool is None:
            return
        try:
            pool.cleanup_all()
            logger.info("Connection pool cleaned up")
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error("Error during cleanup: <ERROR_TYPE>")
            log_error(e, "cleanup", self.errors_path)

    def close(self) -> None:
        """Explicit lifecycle hook for responsible cleanup."""
        self.cleanup()

    def __enter__(self) -> "ThreadSafeSessionDB":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.cleanup()
