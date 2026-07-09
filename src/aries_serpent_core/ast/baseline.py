"""AST baseline management for incremental analysis."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _safe_json_loads(data: str) -> dict[str, Any]:
    """Safely parse JSON, returning empty dict on failure."""
    try:
        return json.loads(data) if data else {}
    except (json.JSONDecodeError, TypeError):
        return {}


class BaselineManager:
    """Manages AST baselines in SQLite database.

    Provides persistent storage for AST analysis baselines,
    enabling incremental analysis and change detection.
    """

    def __init__(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    file_path TEXT PRIMARY KEY,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS baseline_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER
                )
            """)

            conn.commit()
            logger.debug(f"Initialized baseline database: {self.db_path}")

    def save_baseline(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def get_baseline(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def list_baselines(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM baselines ORDER BY file_path").fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def delete_baseline(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines WHERE file_path = ?", (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def clear_all(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")


__all__ = ["BaselineManager"]
