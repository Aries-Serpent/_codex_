"""File-based memory storage backends.

Provides JSONL and SQLite implementations of the MemoryProtocol.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys as _sys
from pathlib import Path
from typing import Any
from uuid import UUID

from .protocol import MemoryEntry, MemoryProtocol, MemoryQuery

logger = logging.getLogger(__name__)

# Platform guard: fcntl is POSIX-only.  On Windows we fall back to a no-op
# lock so the backend still functions (single-process writes are safe;
# multi-process concurrent writes on Windows simply skip advisory locking).
if _sys.platform != "win32":
    import fcntl as _fcntl

    _HAS_FCNTL = True
else:
    _fcntl = None  # type: ignore[assignment]
    _HAS_FCNTL = False
    logger.warning(
        "fcntl unavailable on Windows — MemoryBackend file-locking disabled "
        "(safe for single-process use; avoid concurrent multi-process writes)."
    )


def _flock(fd: int, mode: str) -> None:
    """Portable advisory file lock helper.

    On POSIX uses ``fcntl.flock``; on Windows (no fcntl) is a no-op.
    ``mode`` is one of ``'ex'`` (exclusive), ``'sh'`` (shared), ``'un'`` (unlock).
    """
    if not _HAS_FCNTL:
        return  # Windows: skip advisory locking
    _map = {"ex": _fcntl.LOCK_EX, "sh": _fcntl.LOCK_SH, "un": _fcntl.LOCK_UN}
    _fcntl.flock(fd, _map[mode])


class JSONLMemoryBackend(MemoryProtocol):
    """File-based memory storage using JSONL format.

    Simple, human-readable storage suitable for small to medium memory sets.
    Each line is a JSON object representing one memory entry.

    Args:
        storage_path: Path to the JSONL file
    """

    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(self.storage_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)

    def store(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            _flock(f.fileno(), "ex")
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                _flock(f.fileno(), "un")

    def retrieve(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {type(e).__name__}")
                    logger.warning(f"Skipping invalid memory entry: {type(e).__name__}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[: query.limit]

    def delete(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False

        # Read with shared lock
        with open(self.storage_path, encoding="utf-8") as f:
            _flock(f.fileno(), "sh")
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                _flock(f.fileno(), "un")

        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                _flock(f.fileno(), "ex")
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    _flock(f.fileno(), "un")

        return found

    def clear_session(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0

        entries = []
        deleted_count = 0

        # Read with shared lock
        with open(self.storage_path, encoding="utf-8") as f:
            _flock(f.fileno(), "sh")
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                _flock(f.fileno(), "un")

        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                _flock(f.fileno(), "ex")
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    _flock(f.fileno(), "un")

        return deleted_count

    def get_stats(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}

        entry_count = 0
        with open(self.storage_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1

        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }


class SQLiteMemoryBackend(MemoryProtocol):
    """SQLite-based memory storage for better query performance.

    Provides indexed queries and better scalability than JSONL.
    Suitable for production use with thousands of memories.

    Args:
        db_path: Path to the SQLite database file
    """

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)

        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()

    def store(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith("+00:00") and not timestamp_str.endswith("Z"):
                # Add UTC timezone if missing
                from datetime import datetime, timezone

                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()

            conn.execute(
                """
                INSERT OR REPLACE INTO memories
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()

    def retrieve(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []

        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)

        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)

        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())

        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)  # type: ignore[arg-type]

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)

            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict(
                        {
                            "id": row["id"],
                            "content": json.loads(row["content"]),
                            "timestamp": row["timestamp"],
                            "agent_id": row["agent_id"],
                            "session_id": row["session_id"],
                            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                            "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                        }
                    )
                )

            return entries

    def delete(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0

    def clear_session(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]

            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
