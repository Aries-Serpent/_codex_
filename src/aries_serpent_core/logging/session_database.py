"""
SessionDatabase: Core database operations and connection management.

Provides:
- Database connection pooling
- Schema initialization and management
- Database optimization
- Low-level CRUD operations
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, Optional


@dataclass
class CacheEntry:
    """Represents a cached query result with TTL."""

    data: Any
    timestamp: float

    def is_expired(self, ttl: int = 300) -> bool:
        """Check if cache entry has expired (default TTL: 5 minutes)."""
        return time.time() - self.timestamp > ttl


class SessionDatabase:
    """
    Core SQLite database operations for session tracking.

    Implements:
    - Thread-safe connection management
    - Schema initialization and validation
    - Database optimization
    - Result caching with TTL
    - Connection pooling
    """

    def __init__(self, db_path: str = ".codex/sessions.db") -> None:
        """
        Initialize database connection pool and ensure schema.

        Args:
            db_path: Path to SQLite database file. Created if doesn't exist.

        Raises:
            sqlite3.Error: If schema initialization fails.
        """
        self.db_path = db_path
        self._lock = threading.RLock()
        self._cache: dict[str, CacheEntry] = {}
        self._cache_ttl = 300  # 5 minutes
        self._ensure_schema()
        self._optimize_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for thread-safe database connections.

        Yields:
            sqlite3.Connection: Database connection with row factory set.

        Features:
        - Automatic connection cleanup
        - Row factory set for dict-like access
        - 10-second connection timeout
        """
        conn = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Public context manager for safe database access."""

        with self._get_connection() as conn:
            yield conn

    def _ensure_schema(self) -> None:
        """
        Create database schema if it doesn't exist.

        Loads and executes session_schema.sql from .codex directory.
        Creates all tables and indices for optimal query performance.

        Raises:
            sqlite3.Error: If schema initialization fails.
            FileNotFoundError: If schema file not found.
        """
        schema_path = Path(__file__).resolve().parents[3] / ".codex" / "session_schema.sql"

        if not schema_path.exists():
            # Fallback: create schema inline if file not found
            self._create_inline_schema()
            return

        with open(schema_path, "r") as f:
            schema_sql = f.read()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            conn.commit()

        self._ensure_schema_columns()

    def _ensure_schema_columns(self) -> None:
        """Add missing session columns for older databases created from the legacy schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            existing = {
                row[1] for row in cursor.execute("PRAGMA table_info(sessions)").fetchall()
            }
            required_columns = {
                "lane_bucket": "TEXT",
                "checkpoint_state": "TEXT",
                "budget_remaining": "REAL",
                "estimated_cost": "REAL",
                "cost_score": "REAL",
                "tool_name": "TEXT",
                "tool_complete_call_id": "TEXT",
                "usage_input_tokens": "INTEGER",
                "usage_output_tokens": "INTEGER",
                "credits": "REAL",
                "blockers": "TEXT",
                "checkpoint_markers": "TEXT",
            }
            for column_name, column_type in required_columns.items():
                if column_name not in existing:
                    cursor.execute(
                        f"ALTER TABLE sessions ADD COLUMN {column_name} {column_type}"
                    )
            conn.commit()

    def _create_inline_schema(self) -> None:
        """Create schema using inline SQL (fallback method)."""
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
            lane_bucket TEXT,
            checkpoint_state TEXT,
            budget_remaining REAL,
            estimated_cost REAL,
            cost_score REAL,
            tool_name TEXT,
            tool_complete_call_id TEXT,
            usage_input_tokens INTEGER,
            usage_output_tokens INTEGER,
            credits REAL,
            blockers TEXT,
            checkpoint_markers TEXT,
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
            event_type TEXT NOT NULL CHECK (event_type IN ('start', 'pattern_applied', 'check_passed', 'check_failed', 'error', 'complete')),
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

        with self._get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def _optimize_db(self) -> None:
        """Optimize database settings and structure."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA optimize")
            conn.commit()

    def _invalidate_cache(self) -> None:
        """Clear all cached query results."""
        with self._lock:
            self._cache.clear()

    def insert_session(self, session: dict[str, Any]) -> bool:
        """
        Insert new session into database.

        Args:
            session: Dictionary with keys: session_id, pr_number, branch,
                    timestamp, git_sha, status, agent_name, duration_minutes

        Returns:
            bool: True if insertion successful, False otherwise.

        Raises:
            ValueError: If required fields missing or invalid.
            sqlite3.IntegrityError: If session_id already exists.
        """
        # Validate required fields
        required_fields = ["session_id", "status", "timestamp"]
        for field in required_fields:
            if field not in session:
                raise ValueError(f"Missing required field: {field}")

        # Validate status value
        valid_statuses = {"pending", "in-progress", "complete", "failed"}
        if session.get("status") not in valid_statuses:
            raise ValueError(
                f"Invalid status: {session['status']}. Must be one of {valid_statuses}"
            )

        self._invalidate_cache()

        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    # Insert into sessions table
                    cursor.execute(
                        """
                        INSERT INTO sessions
                        (session_id, pr_number, branch, timestamp, git_sha, status, agent_name, duration_minutes,
                         lane_bucket, checkpoint_state, budget_remaining, estimated_cost, cost_score,
                         tool_name, tool_complete_call_id, usage_input_tokens, usage_output_tokens,
                         credits, blockers, checkpoint_markers)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,  # noqa: E501
                        (
                            session["session_id"],
                            session.get("pr_number"),
                            session.get("branch"),
                            session["timestamp"],
                            session.get("git_sha"),
                            session["status"],
                            session.get("agent_name"),
                            session.get("duration_minutes"),
                            session.get("lane_bucket"),
                            session.get("checkpoint_state"),
                            session.get("budget_remaining"),
                            session.get("estimated_cost"),
                            session.get("cost_score"),
                            session.get("tool_name"),
                            session.get("tool_complete_call_id"),
                            session.get("usage_input_tokens"),
                            session.get("usage_output_tokens"),
                            session.get("credits"),
                            session.get("blockers"),
                            session.get("checkpoint_markers"),
                        ),
                    )

                    # Insert outcomes if provided
                    if "outcomes" in session:
                        outcomes = session["outcomes"]
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO session_outcomes
                            (session_id, ci_checks_green, ci_checks_red, ci_checks_total,
                             test_coverage, linting_errors, linting_warnings)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                session["session_id"],
                                outcomes.get("ci_checks_green", 0),
                                outcomes.get("ci_checks_red", 0),
                                outcomes.get("ci_checks_total", 0),
                                outcomes.get("test_coverage"),
                                outcomes.get("linting_errors", 0),
                                outcomes.get("linting_warnings", 0),
                            ),
                        )

                    # Insert metadata if provided
                    if "metadata" in session:
                        for key, value in session["metadata"].items():
                            cursor.execute(
                                """
                                INSERT OR REPLACE INTO session_metadata (session_id, key, value)
                                VALUES (?, ?, ?)
                                """,
                                (session["session_id"], key, str(value)),
                            )

                    # Persist lane-aware metadata on the session's metadata table even when
                    # the primary sessions table doesn't expose a dedicated column for it.
                    lane_metadata = {
                        key: value
                        for key, value in session.items()
                        if key
                        in {
                            "lane_bucket",
                            "checkpoint_state",
                            "budget_remaining",
                            "estimated_cost",
                            "cost_score",
                            "task_id",
                            "last_successful_stage",
                            "resume_from_checkpoint_id",
                            "checkpoint_markers",
                            "blockers",
                            "usage_input_tokens",
                            "usage_output_tokens",
                            "credits",
                        }
                        and value is not None
                    }
                    for key, value in lane_metadata.items():
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO session_metadata (session_id, key, value)
                            VALUES (?, ?, ?)
                            """,
                            (session["session_id"], key, str(value)),
                        )

                    # Insert patterns if provided
                    if "patterns" in session:
                        for pattern in session["patterns"]:
                            cursor.execute(
                                """
                                INSERT INTO session_patterns (session_id, pattern_id, pattern_name, success)
                                VALUES (?, ?, ?, ?)
                                """,  # noqa: E501
                                (
                                    session["session_id"],
                                    pattern.get("pattern_id"),
                                    pattern.get("pattern_name"),
                                    pattern.get("success", True),
                                ),
                            )

                    conn.commit()
                    return True

            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    raise ValueError(f"Session ID {session['session_id']} already exists") from e
                raise
            except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
                raise sqlite3.Error(f"Failed to insert session: {e}") from e

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get single session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session dictionary or None if not found.

        Performance:
            - O(1) lookup via PRIMARY KEY
        """
        cache_key = f"session_{session_id}"

        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if not entry.is_expired(self._cache_ttl):
                    return entry.data

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                result = dict(row) if row else None

            if result:
                self._cache[cache_key] = CacheEntry(result, time.time())

        return result

    def get_session_with_details(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get session with all related details (metadata, patterns, outcomes, events).

        Args:
            session_id: Unique session identifier

        Returns:
            Session dictionary with nested details or None if not found.
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get metadata
            cursor.execute(
                "SELECT key, value FROM session_metadata WHERE session_id = ?",
                (session_id,),
            )
            metadata = {row[0]: row[1] for row in cursor.fetchall()}
            session["metadata"] = metadata

            # Get patterns
            cursor.execute(
                "SELECT pattern_id, pattern_name, success FROM session_patterns WHERE session_id = ?",  # noqa: E501
                (session_id,),
            )
            patterns = [dict(row) for row in cursor.fetchall()]
            session["patterns"] = patterns

            # Get outcomes
            cursor.execute(
                "SELECT * FROM session_outcomes WHERE session_id = ?",
                (session_id,),
            )
            outcomes_row = cursor.fetchone()
            session["outcomes"] = dict(outcomes_row) if outcomes_row else {}

            # Get events
            cursor.execute(
                "SELECT event_type, event_details, timestamp FROM session_events WHERE session_id = ? ORDER BY timestamp DESC",  # noqa: E501
                (session_id,),
            )
            events = [dict(row) for row in cursor.fetchall()]
            session["events"] = events

        return session

    def update_session_status(self, session_id: str, new_status: str) -> bool:
        """
        Update session status.

        Args:
            session_id: Session identifier
            new_status: New status value

        Returns:
            True if update successful, False if session not found.

        Raises:
            ValueError: If status invalid.
        """
        valid_statuses = {"pending", "in-progress", "complete", "failed"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")

        self._invalidate_cache()

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",  # noqa: E501
                    (new_status, session_id),
                )
                conn.commit()
                return cursor.rowcount > 0

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session and all related data.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully, False if not found.
        """
        self._invalidate_cache()

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0

    def vacuum(self) -> None:
        """Optimize database size and performance."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("VACUUM")
                cursor.execute("PRAGMA optimize")
                conn.commit()

    def get_connection_info(self) -> dict[str, Any]:
        """Get information about database connection and settings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get journal mode
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]

            # Get cache size
            cursor.execute("PRAGMA cache_size")
            cache_size = cursor.fetchone()[0]

            # Get synchronous setting
            cursor.execute("PRAGMA synchronous")
            synchronous = cursor.fetchone()[0]

            # Get foreign keys setting
            cursor.execute("PRAGMA foreign_keys")
            foreign_keys = cursor.fetchone()[0]

            # Get database size
            db_file = Path(self.db_path)
            db_size = db_file.stat().st_size if db_file.exists() else 0

            return {
                "db_path": self.db_path,
                "journal_mode": journal_mode,
                "cache_size": cache_size,
                "synchronous": synchronous,
                "foreign_keys": bool(foreign_keys),
                "db_size_bytes": db_size,
                "cache_ttl": self._cache_ttl,
                "cached_queries": len(self._cache),
            }
