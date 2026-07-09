"""
Archive Manager: Handles archiving, retrieval, and lifecycle management of sessions.

This module provides:
- Archive session extraction and storage to Parquet
- Archive retrieval with transparent access
- Retention policy enforcement
- Archive index maintenance
- LRU caching for frequently accessed archives
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)


@dataclass
class ArchivedSession:
    """Represents an archived session record."""

    session_id: str
    archive_location: str
    file_size_bytes: int
    timestamp: str
    created_at: str
    retrieval_time_ms: float = 0.0


class ArchiveManager:
    """
    Manages session archiving, retrieval, and retention lifecycle.

    Features:
    - Archive sessions to Parquet format
    - Retrieve archived sessions from cold storage
    - Transparent access (same interface as active sessions)
    - LRU cache for frequent access
    - Retention policy enforcement
    - Archive index maintenance
    """

    def __init__(
        self,
        db_path: str = ".codex/sessions.db",
        archive_dir: str = ".codex/archive/sessions",
        cache_size_mb: int = 10,
    ):
        """
        Initialize ArchiveManager.

        Args:
            db_path: Path to SQLite database
            archive_dir: Base directory for archived sessions
            cache_size_mb: LRU cache size in MB
        """
        self.db_path = db_path
        self.archive_dir = Path(archive_dir)
        self.cache_size_mb = cache_size_mb
        self.archive_index_path = Path(".codex/archive/sessions_archive_index.json")
        self.retention_log_path = Path(".codex/archive/retention_log.json")

        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._cache_size_bytes = 0

    def archive_session(self, session_id: str) -> Optional[ArchivedSession]:
        """
        Archive a session from active database to Parquet.

        Args:
            session_id: Session ID to archive

        Returns:
            ArchivedSession record if successful, None otherwise
        """
        try:
            # Extract session data
            session_data = self._extract_session(session_id)
            if not session_data:
                logger.warning(f"Session not found: {session_id}")
                return None

            # Determine archive location
            created_at = session_data.get("created_at", datetime.now().isoformat())
            archive_path = self._get_archive_path(session_id, created_at)

            # Write to Parquet
            if pd is None:
                logger.error("pandas is required for archiving")
                return None

            archive_path.parent.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame([session_data])
            df.to_parquet(archive_path, compression="snappy", index=False)

            file_size = archive_path.stat().st_size

            # Update SQLite metadata
            self._update_archive_metadata(session_id, str(archive_path), datetime.now().isoformat())

            # Create record
            archive_record = ArchivedSession(
                session_id=session_id,
                archive_location=str(archive_path),
                file_size_bytes=file_size,
                timestamp=created_at,
                created_at=str(time.time()),
            )

            logger.info(f"Archived session {session_id} ({file_size} bytes)")
            return archive_record

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Error archiving session {session_id}: <ERROR_TYPE>")
            return None

    def get_archived_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve archived session from cold storage.

        Implements transparent access with caching:
        - First check LRU cache (<50ms if cached)
        - Then load from Parquet (<500ms cold)
        - Returns same structure as active sessions

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session dict if found, None otherwise
        """
        start_time = time.time()

        # Check cache
        if session_id in self._cache:
            session_data, cache_time = self._cache[session_id]
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"Retrieved {session_id} from cache in {elapsed_ms:.1f}ms")
            return session_data

        try:
            # Query SQLite for archive location
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT archive_location FROM sessions
                WHERE session_id = ? AND archive_status = 'archived'
                """,
                (session_id,),
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                return None

            archive_location = result["archive_location"]

            # Load from Parquet
            if pd is None:
                logger.error("pandas is required for retrieval")
                return None

            archive_path = Path(archive_location)
            if not archive_path.exists():
                logger.warning(f"Archive file not found: {archive_location}")
                return None

            df = pd.read_parquet(archive_path)

            # Convert to dict, handling numpy types and arrays
            session_row = df.iloc[0]
            session_data = {}
            for col, val in session_row.items():
                # Handle different value types
                if val is None or (isinstance(val, float) and pd.isna(val)):
                    session_data[col] = None
                elif isinstance(val, (list, tuple)):
                    # If it's a list/tuple, convert items
                    session_data[col] = [v.item() if hasattr(v, "item") else v for v in val]
                elif hasattr(val, "item"):  # numpy scalar
                    try:
                        session_data[col] = val.item()
                    except (TypeError, ValueError):
                        session_data[col] = str(val)
                else:
                    session_data[col] = val

            # Add to cache
            self._add_to_cache(session_id, session_data)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"Retrieved {session_id} from cold storage in {elapsed_ms:.1f}ms")

            return session_data

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.error(f"Error retrieving archived session {session_id}: <ERROR_TYPE>")
            return None

    def identify_archive_candidates(self, days: int = 90) -> list[str]:
        """
        Identify sessions older than threshold for archiving.

        Args:
            days: Sessions older than this many days are candidates (default: 90)

        Returns:
            List of session IDs to archive
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute(
                """
                SELECT session_id FROM sessions
                WHERE archive_status = 'active'
                AND created_at < ?
                AND status != 'in-progress'
                ORDER BY created_at DESC
                """,
                (cutoff_date,),
            )

            candidates = [row["session_id"] for row in cursor.fetchall()]
            conn.close()

            logger.info(f"Found {len(candidates)} archive candidates (>= {days} days old)")
            return candidates

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.error("Error identifying archive candidates: <ERROR_TYPE>")
            return []

    def purge_old_archives(self, iterations: int = 30) -> dict[str, Any]:
        """
        Purge archived sessions older than retention threshold.

        Implements retention policy: Delete if >30 iterations old.

        Args:
            iterations: Iterations to retain (default: 30)

        Returns:
            Purge report with deleted sessions and bytes freed
        """
        report = {
            "deleted_sessions": [],
            "total_bytes_freed": 0,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Load archive index
            if not self.archive_index_path.exists():
                logger.warning("Archive index not found")
                return report

            with open(self.archive_index_path) as f:
                index_data = json.load(f)

            cutoff_time = time.time() - (iterations * 86400)  # iterations in seconds

            for archived_session in index_data.get("sessions", []):
                created_at_ts = float(archived_session.get("created_at", 0))

                if created_at_ts < cutoff_time:
                    session_id = archived_session["session_id"]
                    archive_location = archived_session["archive_location"]
                    file_size = archived_session.get("file_size_bytes", 0)

                    # Delete Parquet file
                    archive_path = Path(archive_location)
                    if archive_path.exists():
                        archive_path.unlink()
                        report["total_bytes_freed"] += file_size

                    # Update SQLite
                    self._mark_session_deleted(session_id)

                    report["deleted_sessions"].append(  # type: ignore[attr-defined]
                        {
                            "session_id": session_id,
                            "archive_location": archive_location,
                            "file_size_bytes": file_size,
                        }
                    )

                    logger.info(f"Purged archived session {session_id}")

            # Log retention action
            self._log_retention_action(report)

            logger.info(
                f"Purged {len(report['deleted_sessions'])} sessions, "  # type: ignore[arg-type]
                f"freed {report['total_bytes_freed']} bytes"
            )
            return report

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.error("Error purging old archives: <ERROR_TYPE>")
            return report

    def update_archive_index(self) -> dict[str, Any]:
        """
        Rebuild archive index from current archive directory.

        Returns:
            Updated archive index dictionary
        """
        try:
            sessions = []
            total_size = 0

            # Scan archive directory
            for parquet_file in self.archive_dir.rglob("*.parquet"):
                try:
                    session_id = parquet_file.stem
                    file_size = parquet_file.stat().st_size
                    total_size += file_size

                    # Extract timestamp from filename or Parquet metadata
                    stat_result = parquet_file.stat()
                    created_at = stat_result.st_mtime

                    sessions.append(
                        {
                            "session_id": session_id,
                            "archive_location": str(parquet_file),
                            "file_size_bytes": file_size,
                            "timestamp": datetime.fromtimestamp(created_at).isoformat() + "Z",
                            "created_at": str(created_at),
                        }
                    )
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.warning(f"Error processing {parquet_file}: <ERROR_TYPE>")
                    continue

            # Build index
            index = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "sessions": sorted(sessions, key=lambda x: x["created_at"]),  # type: ignore[arg-type,return-value]
                "statistics": {
                    "total_sessions": len(sessions),
                    "total_size_mb": total_size / (1024 * 1024),
                    "retention_policy": "Delete archives >30 iterations old",
                    "archive_format": "Parquet (snappy compressed)",
                    "partitioning": "YYYY/MM/ by creation_date",
                },
            }

            # Write index
            self.archive_index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.archive_index_path, "w") as f:
                json.dump(index, f, indent=2)

            logger.info(
                f"Updated archive index: {len(sessions)} sessions, "
                f"{total_size / (1024 * 1024):.2f} MB"
            )
            return index

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.error("Error updating archive index: <ERROR_TYPE>")
            return {"sessions": [], "statistics": {}}

    # Private methods
    def _extract_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """Extract session data from SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            session_row = cursor.fetchone()

            if not session_row:
                conn.close()
                return None

            session_data = dict(session_row)

            # Also fetch related metadata, events, outcomes
            cursor.execute("SELECT * FROM session_metadata WHERE session_id = ?", (session_id,))
            metadata_rows = cursor.fetchall()
            session_data["metadata"] = [dict(row) for row in metadata_rows]

            cursor.execute("SELECT * FROM session_events WHERE session_id = ?", (session_id,))
            event_rows = cursor.fetchall()
            session_data["events"] = [dict(row) for row in event_rows]

            cursor.execute("SELECT * FROM session_outcomes WHERE session_id = ?", (session_id,))
            outcome_row = cursor.fetchone()
            if outcome_row:
                session_data["outcomes"] = dict(outcome_row)

            conn.close()
            return session_data

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Error extracting session {session_id}: <ERROR_TYPE>")
            return None

    def _get_archive_path(self, session_id: str, created_at: str) -> Path:
        """Determine archive path based on creation date."""
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            dt = datetime.now()

        year = dt.strftime("%Y")
        month = dt.strftime("%m")

        return self.archive_dir / year / month / f"{session_id}.parquet"

    def _update_archive_metadata(
        self, session_id: str, archive_location: str, archive_timestamp: str
    ) -> None:
        """Update SQLite with archive metadata."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

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
        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Error updating archive metadata for {session_id}: <ERROR_TYPE>")

    def _mark_session_deleted(self, session_id: str) -> None:
        """Mark session as deleted in SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE sessions
                SET archive_status = 'deleted', status = 'deleted'
                WHERE session_id = ?
                """,
                (session_id,),
            )

            conn.commit()
            conn.close()
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.error(f"Error marking session deleted: {session_id}: <ERROR_TYPE>")

    def _add_to_cache(self, session_id: str, session_data: dict[str, Any]) -> None:
        """Add session to LRU cache."""
        data_size = len(json.dumps(session_data))

        # Check if adding would exceed cache size
        if self._cache_size_bytes + data_size > self.cache_size_mb * 1024 * 1024:
            # Remove oldest entry
            if self._cache:
                oldest_id = min(self._cache.keys(), key=lambda k: self._cache[k][1])
                old_size = len(json.dumps(self._cache[oldest_id][0]))
                del self._cache[oldest_id]
                self._cache_size_bytes -= old_size

        self._cache[session_id] = (session_data, time.time())
        self._cache_size_bytes += data_size

    def _log_retention_action(self, report: dict[str, Any]) -> None:
        """Log retention/purge actions."""
        try:
            retention_log = {"version": "1.0", "created": datetime.now().isoformat()}

            if self.retention_log_path.exists():
                with open(self.retention_log_path) as f:
                    retention_log = json.load(f)

            if "cleanups" not in retention_log:
                retention_log["cleanups"] = []  # type: ignore[assignment]

            retention_log["cleanups"].append(report)  # type: ignore[attr-defined]

            self.retention_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.retention_log_path, "w") as f:
                json.dump(retention_log, f, indent=2)

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error("Error logging retention action: <ERROR_TYPE>")
