"""Database manager for Codex logging infrastructure.

Provides centralized database initialization, connection pooling, and schema management
for SQLite-based logging.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except (ImportError, AttributeError) as exc:  # pragma: no cover
    logging.getLogger(__name__).debug("SQLite patch disabled: %s", exc)

# Initialize logger early
logger = logging.getLogger(__name__)

try:
    from .config import DEFAULT_LOG_DB
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    DEFAULT_LOG_DB = Path(".codex/session_logs.db")


class DBManager:
    """Centralized database manager for Codex logging.

    Features:
    - Automatic schema initialization
    - Connection pooling support (opt-in via CODEX_SQLITE_POOL=1)
    - Thread-safe operations
    - WAL mode for better concurrency
    - Graceful connection cleanup via close_all_pools()

    Usage:
        # Basic usage
        db_manager = DBManager()
        conn = db_manager.get_connection()
        # Use connection
        db_manager.close_connection(conn)

        # Context manager (recommended)
        with db_manager.connection() as conn:
            # Use connection
            pass

        # Application shutdown
        import atexit
        atexit.register(DBManager.close_all_pools)

    Attributes:
        _logger: Class-level logger (shared across instances)
        _POOL_ENABLED: Connection pooling enabled flag
        _CONNECTION_POOL: Shared connection pool dictionary
    """

    # Class-level lock for initialization
    _INIT_LOCK = threading.RLock()
    _INITIALIZED_DBS: set[str] = set()

    # Connection pool
    _POOL_LOCK = threading.RLock()
    _CONNECTION_POOL: dict[str, list[sqlite3.Connection]] = {}
    _POOL_ENABLED = os.getenv("CODEX_SQLITE_POOL") == "1"

    # Class-level logger
    _logger = logging.getLogger(__name__)

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database (default: from env or .codex/session_logs.db)
        """
        self.db_path = self._resolve_db_path(db_path)

    def _resolve_db_path(self, db_path: Optional[Path] = None) -> Path:
        """Resolve database path from args, env, or defaults."""
        if db_path:
            return Path(db_path).resolve()

        # Check environment variables
        env_path = os.getenv("CODEX_LOG_DB_PATH") or os.getenv("CODEX_DB_PATH")
        if env_path:
            return Path(env_path).resolve()

        # Use default
        return Path(DEFAULT_LOG_DB).resolve()

    def init_schema(self) -> None:
        """Initialize database schema if not already initialized.

        Creates:
        - session_events table
        - Indexes for efficient querying
        """
        db_key = str(self.db_path)

        # Check if already initialized
        if db_key in self._INITIALIZED_DBS:
            return

        with self._INIT_LOCK:
            # Double-check after acquiring lock
            if db_key in self._INITIALIZED_DBS:
                return

            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Create schema
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL;")

                # Create session_events table
                conn.execute("""CREATE TABLE IF NOT EXISTS session_events(
                        ts REAL NOT NULL,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        message TEXT NOT NULL,
                        seq INTEGER,
                        meta TEXT
                    )""")

                # Check and add columns if missing (for schema migrations)
                cols = [r[1] for r in conn.execute("PRAGMA table_info(session_events)")]
                if "seq" not in cols:
                    conn.execute("ALTER TABLE session_events ADD COLUMN seq INTEGER")
                if "meta" not in cols:
                    conn.execute("ALTER TABLE session_events ADD COLUMN meta TEXT")

                # Create indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS session_events_sid_ts_idx "
                    "ON session_events(session_id, ts)"
                )
                conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS session_events_session_seq_idx "
                    "ON session_events(session_id, seq)"
                )

                conn.commit()
                self._INITIALIZED_DBS.add(db_key)
                self._logger.info(f"Database schema initialized: {self.db_path}")

            finally:
                conn.close()

    def get_connection(self, auto_init: bool = True) -> sqlite3.Connection:
        """Get a database connection, optionally from pool.

        Args:
            auto_init: Automatically initialize schema if not done

        Returns:
            SQLite connection
        """
        if auto_init:
            self.init_schema()

        db_key = str(self.db_path)

        # Try to get from pool if enabled
        if self._POOL_ENABLED:
            with self._POOL_LOCK:
                pool = self._CONNECTION_POOL.get(db_key, [])
                if pool:
                    conn = pool.pop()
                    # Test if connection is still valid
                    try:
                        conn.execute("SELECT 1")
                        return conn
                    except sqlite3.Error:
                        # Connection is stale, create new one
                        logger.debug("Suppressed exception in handler", exc_info=True)
        # Create new connection
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")

        return conn

    def close_connection(self, conn: sqlite3.Connection) -> None:
        """Close or return connection to pool.

        Args:
            conn: Connection to close/return
        """
        if not conn:
            return

        db_key = str(self.db_path)

        # Return to pool if enabled
        if self._POOL_ENABLED:
            with self._POOL_LOCK:
                if db_key not in self._CONNECTION_POOL:
                    self._CONNECTION_POOL[db_key] = []

                # Limit pool size to prevent resource exhaustion
                if len(self._CONNECTION_POOL[db_key]) < 10:
                    self._CONNECTION_POOL[db_key].append(conn)
                    return

        # Close if not pooling or pool is full
        try:
            conn.close()
        except sqlite3.Error as exc:
            type(exc).__name__
            self._logger.debug("Error closing connection: <ERROR_TYPE>")

    @contextmanager
    def connection(self, auto_init: bool = True) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections.

        Args:
            auto_init: Automatically initialize schema if not done

        Yields:
            SQLite connection

        Example:
            with db_manager.connection() as conn:
                cursor = conn.execute("SELECT * FROM session_events")
                rows = cursor.fetchall()
        """
        conn = self.get_connection(auto_init=auto_init)
        try:
            yield conn
        finally:
            self.close_connection(conn)

    @classmethod
    def close_all_pools(cls) -> None:
        """Close all pooled connections (for cleanup/shutdown).

        This method is typically called during application shutdown to ensure
        all database connections are properly closed and resources are released.

        Handles errors gracefully:
        - Logs errors at DEBUG level if individual connections fail to close
        - Continues closing remaining connections even if errors occur
        - Clears the connection pool dictionary after all close attempts

        Thread-safe: Uses _POOL_LOCK to prevent concurrent access.

        Example:
            # During application shutdown
            import atexit
            atexit.register(DBManager.close_all_pools)

            # Or manually
            DBManager.close_all_pools()

        Note:
            This is a classmethod that operates on the shared connection pool
            across all DBManager instances. It does not require an instance.
        """
        with cls._POOL_LOCK:
            for pool in cls._CONNECTION_POOL.values():
                for conn in pool:
                    try:
                        conn.close()
                    except sqlite3.Error as exc:
                        type(exc).__name__
                        cls._logger.debug("Error closing pooled connection: <ERROR_TYPE>")
            cls._CONNECTION_POOL.clear()


# Alias for backward compatibility
DatabaseManager = DBManager

# Global instance
db_manager = DBManager()
