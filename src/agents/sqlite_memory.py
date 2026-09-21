import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from cognitive_brain.base import MemoryInterface


class SQLiteMemory(MemoryInterface):
    """
    SQLite-backed persistent memory for cross-session agent state.

    Zero additional dependencies (uses stdlib sqlite3).
    """

    def __init__(self, db_path: str | Path = ".codex/agent_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize schema
        self._initialize_schema()

    def _initialize_schema(self):
        """Create tables if not exist"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)

            # Keep history of values
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(key) REFERENCES memory(key)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_updated_at
                ON memory(updated_at)
            """)

            conn.commit()

    def store(self, key: str, value: Any, metadata: Optional[dict[str, Any]] = None) -> bool:
        """
        Store value in SQLite

        Args:
            key: Unique identifier
            value: Any JSON-serializable value
            metadata: Optional metadata dict

        Returns:
            True if successful
        """
        try:
            now = datetime.now(timezone.utc).isoformat()
            value_json = json.dumps(value)
            metadata_json = json.dumps(metadata) if metadata else None

            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO memory (key, value_json, created_at, updated_at, metadata_json)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value_json = excluded.value_json,
                        updated_at = excluded.updated_at,
                        metadata_json = excluded.metadata_json
                """, (key, value_json, now, now, metadata_json))

                conn.execute("""
                    INSERT INTO memory_history (key, value_json, timestamp)
                    VALUES (?, ?, ?)
                """, (key, value_json, now))

                conn.commit()

            return True
        except Exception as e:
            print(f"❌ Error storing {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve value from SQLite

        Args:
            key: Unique identifier

        Returns:
            Deserialized value or None
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.execute(
                    "SELECT value_json FROM memory WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()

                if row:
                    return json.loads(row[0])
                return None
        except Exception as e:
            print(f"❌ Error retrieving {key}: {e}")
            return None

    def search(self, query: dict[str, Any], limit: int = 10) -> list[tuple[str, Any]]:
        """
        Search memory based on query criteria (simplified matching).
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                # We'll just retrieve all and filter in Python for simplicity
                cursor = conn.execute("SELECT key, value_json, metadata_json FROM memory")

                results = []
                for row in cursor.fetchall():
                    key = row[0]
                    value = json.loads(row[1])
                    metadata = json.loads(row[2]) if row[2] else {}

                    # Very simple filtering
                    match = True
                    for k, v in query.items():
                        if k in metadata and metadata[k] != v:
                            match = False
                        elif k not in metadata:
                            match = False

                    if match:
                        results.append((key, value))
                        if len(results) >= limit:
                            break

                return results
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []

    def delete(self, key: str) -> bool:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.execute("DELETE FROM memory WHERE key = ?", (key,))
                conn.execute("DELETE FROM memory_history WHERE key = ?", (key,))
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error deleting {key}: {e}")
            return False

    def clear(self) -> bool:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.execute("DELETE FROM memory")
                conn.execute("DELETE FROM memory_history")
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error clearing memory: {e}")
            return False

    def get_history(self, key: str, limit: int = 10) -> list[tuple[datetime, Any]]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, value_json
                    FROM memory_history
                    WHERE key = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (key, limit))

                results = []
                for row in cursor.fetchall():
                    ts = datetime.fromisoformat(row[0])
                    val = json.loads(row[1])
                    results.append((ts, val))

                return results
        except Exception as e:
            print(f"❌ Error getting history for {key}: {e}")
            return []

    def summarize_history(self, last_n: int = 5) -> str:
        """
        Generate summary of recent memory entries
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT key, updated_at
                    FROM memory
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (last_n,))

                summary = "## Memory Summary\n\n"
                for key, updated_at in cursor.fetchall():
                    summary += f"- **{key}** (updated: {updated_at})\n"

                return summary
        except Exception as e:
            print(f"❌ Error summarizing: {e}")
            return "Error generating summary"
