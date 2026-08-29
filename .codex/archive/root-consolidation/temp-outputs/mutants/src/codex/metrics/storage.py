"""
Metric Storage Module

Provides dual storage (JSON + SQLite) for duplication metrics with
historical tracking and query capabilities.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from .duplication import DuplicationRatio

logger = logging.getLogger(__name__)

# Default storage locations
DEFAULT_JSON_DIR = Path(".codex/metrics/json")
DEFAULT_SQLITE_PATH = Path(".codex/metrics/duplication.db")


class MetricStorage:
    """Dual storage backend for duplication metrics"""

    def __init__(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """)

            # Duplicate blocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """)

            # Occurrences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """)

            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """)

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def save(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id  # type: ignore[assignment]

        return result

    def _save_json(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def _save_sqlite(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id  # type: ignore[return-value]

        finally:
            conn.close()

    def load_latest(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute("""
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def query_history(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()
