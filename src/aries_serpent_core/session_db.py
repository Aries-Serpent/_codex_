"""
Session Database Manager with Archive Support

Phase 5: Archive Implementation
- Handle active and archived sessions transparently
- Archive to Parquet with directory-based partitioning
- Retrieve with optional caching
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

try:
    import pandas as pd
    import pyarrow.parquet as pq

    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    pd = None
    pq = None

from codex.logging.structured_logger import logger


class SessionDB:
    """Session database with archive support"""

    def __init__(
        self, db_path: str = ".codex/sessions.db", archive_dir: str = ".codex/archive/sessions"
    ):
        self.db_path = db_path
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._cache: dict[str, Any] = {}  # LRU-like cache (simple dict)
        self.cache_max_size = 10 * 1024 * 1024  # 10 MB
        self.cache_current_size = 0

    def _init_db(self) -> None:
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create sessions table with archive fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                pr_number INTEGER,
                branch TEXT,
                timestamp TEXT,
                git_sha TEXT,
                status TEXT NOT NULL CHECK (status IN ('pending', 'in-progress', 'complete', 'failed', 'archived', 'deleted')),
                archive_status TEXT DEFAULT 'active' CHECK (archive_status IN ('active', 'archived', 'deleted')),
                archive_location TEXT,
                archive_timestamp TEXT,
                agent_name TEXT,
                duration_minutes INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)  # noqa: E501

        # Create session metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                UNIQUE(session_id, key)
            )
        """)

        # Create session events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            )
        """)

        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_archive_status ON sessions(archive_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON sessions(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON sessions(timestamp)")

        conn.commit()
        conn.close()

    def archive_session(self, session_id: str, session_data: dict[str, Any]) -> str:
        """Archive a session to Parquet storage

        Args:
            session_id: Session ID
            session_data: Session data dict

        Returns:
            Path to archived session file
        """
        if not PARQUET_AVAILABLE:
            raise ImportError("pandas and pyarrow required for archiving")

        # Extract timestamp from session data
        timestamp_str = session_data.get("timestamp", datetime.utcnow().isoformat())

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            timestamp = datetime.utcnow()

        # Create partition path: YYYY/MM/
        year = timestamp.strftime("%Y")
        month = timestamp.strftime("%m")
        partition_dir = self.archive_dir / year / month
        partition_dir.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame for Parquet
        df = pd.DataFrame([session_data])

        # Write Parquet file
        archive_path = partition_dir / f"{session_id}.parquet"
        df.to_parquet(str(archive_path), compression="snappy")

        # Update database
        try:
            archive_location = str(archive_path.relative_to(Path.cwd()))
        except ValueError:
            # If relative_to fails, use the path as-is
            archive_location = str(archive_path)
        self._update_archive_status(session_id, archive_location)

        logger.info(f"Archived session {session_id} to {archive_location}")
        return str(archive_path)

    def _update_archive_status(self, session_id: str, archive_location: str) -> None:
        """Update session archive status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        archive_timestamp = datetime.utcnow().isoformat()
        cursor.execute(
            """
            UPDATE sessions
            SET archive_status = 'archived',
                archive_location = ?,
                archive_timestamp = ?
            WHERE session_id = ?
        """,
            (archive_location, archive_timestamp, session_id),
        )

        conn.commit()
        conn.close()

    def get_session(self, session_id: str, use_cache: bool = True) -> Optional[dict[str, Any]]:
        """Get session (from cache, DB, or archive)

        Args:
            session_id: Session ID
            use_cache: Use cache for archived sessions

        Returns:
            Session data dict or None
        """
        # Check cache first
        if use_cache and session_id in self._cache:
            return self._cache[session_id]

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        row_dict = dict(row)

        # If archived, load from Parquet
        if row_dict.get("archive_status") == "archived":
            archive_location = row_dict.get("archive_location")
            if archive_location and PARQUET_AVAILABLE:
                try:
                    df = pd.read_parquet(archive_location)
                    if len(df) > 0:
                        session_data = df.iloc[0].to_dict()

                        # Cache if space available
                        if use_cache:
                            self._cache_session(session_id, session_data)

                        return session_data
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.error(f"Error loading archived session {session_id}: <ERROR_TYPE>")

        return row_dict

    def _cache_session(self, session_id: str, session_data: dict[str, Any]) -> None:
        """Cache session with size limit"""
        # Simple size estimation
        data_size = len(json.dumps(session_data).encode("utf-8"))

        # Check if we need to evict
        while self.cache_current_size + data_size > self.cache_max_size and self._cache:
            # Simple FIFO eviction
            evict_key = next(iter(self._cache))
            evict_size = len(json.dumps(self._cache[evict_key]).encode("utf-8"))
            del self._cache[evict_key]
            self.cache_current_size -= evict_size

        self._cache[session_id] = session_data
        self.cache_current_size += data_size

    def get_archive_candidates(self, days: int = 90) -> list[str]:
        """Get list of session IDs older than N days

        Args:
            days: Age threshold in days

        Returns:
            List of session IDs to archive
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cursor.execute(
            """
            SELECT session_id
            FROM sessions
            WHERE archive_status = 'active'
            AND created_at < ?
            ORDER BY created_at ASC
        """,
            (cutoff_date,),
        )

        candidates = [row[0] for row in cursor.fetchall()]
        conn.close()

        return candidates

    def mark_deleted(self, session_id: str) -> None:
        """Mark session as deleted (for retention policy)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE sessions
            SET archive_status = 'deleted'
            WHERE session_id = ?
        """,
            (session_id,),
        )

        conn.commit()
        conn.close()

        # Remove from cache
        if session_id in self._cache:
            del self._cache[session_id]

    def cleanup_old_archives(self, max_iterations: int = 30) -> int:
        """Delete archived sessions older than max_iterations

        Args:
            max_iterations: Maximum number of iterations to keep
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate cutoff date (30 iterations ~ 30 days assuming 1 per day)
        cutoff_date = (datetime.utcnow() - timedelta(days=max_iterations)).isoformat()

        cursor.execute(
            """
            SELECT session_id, archive_location
            FROM sessions
            WHERE archive_status = 'archived'
            AND archive_timestamp < ?
        """,
            (cutoff_date,),
        )

        old_sessions = cursor.fetchall()
        deleted_count = 0

        for session_id, archive_location in old_sessions:
            try:
                # Delete Parquet file
                if archive_location and Path(archive_location).exists():
                    Path(archive_location).unlink()

                # Mark as deleted in database
                self.mark_deleted(session_id)
                deleted_count += 1
            except (IOError, OSError) as e:
                type(e).__name__
                logger.error(f"Error deleting archive {session_id}: <ERROR_TYPE>")

        conn.close()
        logger.info(f"Cleaned up {deleted_count} old archives (>30 iterations)")
        return deleted_count

    def get_archive_stats(self) -> dict[str, Any]:
        """Get archive statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE archive_status = 'active'")
        active_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE archive_status = 'archived'")
        archived_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE archive_status = 'deleted'")
        deleted_count = cursor.fetchone()[0]

        cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM sessions")
        date_range = cursor.fetchone()

        conn.close()

        # Calculate total archive size
        total_size = 0
        for parquet_file in self.archive_dir.rglob("*.parquet"):
            total_size += parquet_file.stat().st_size

        return {
            "active_sessions": active_count,
            "archived_sessions": archived_count,
            "deleted_sessions": deleted_count,
            "total_archive_size_mb": total_size / (1024 * 1024),
            "oldest_session": date_range[0],
            "newest_session": date_range[1],
            "cache_size_mb": self.cache_current_size / (1024 * 1024),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = SessionDB()
    stats = db.get_archive_stats()
    logger.info(f"Archive Stats: {json.dumps(stats, indent=2, default=str)}")
