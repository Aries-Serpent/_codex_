"""
SQLite storage for AST analysis results.

Provides persistent storage for analysis results, enabling
incremental analysis and historical comparison.
"""

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from codex_ml.ast.core.exceptions import StorageError
from codex_ml.ast.core.node import Finding, SourceLocation


class ASTStorage:
    """SQLite storage for AST analysis results.

    Stores analysis results, findings, and metrics in a SQLite database.

    Example:
        storage = ASTStorage(Path("analysis.db"))
        storage.save_analysis("run-001", "example.py", findings)

        # Later, retrieve results
        results = storage.get_analysis("run-001")
    """

    def __init__(self, db_path: Path):
        """Initialize storage with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections.

        Yields:
            SQLite connection with row factory set

        Raises:
            StorageError: If connection fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except (IOError, OSError) as e:
                conn.rollback()
                raise StorageError(
                    f"Database operation failed: {e}", operation="transaction"
                ) from e
            finally:
                conn.close()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to connect to database: {e}", operation="connect") from e

    def _initialize_schema(self) -> None:
        """Create database schema if not exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    language TEXT,
                    node_count INTEGER,
                    finding_count INTEGER,
                    metrics TEXT,
                    status TEXT DEFAULT 'completed'
                )
            """)

            # Findings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    finding_id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    file_path TEXT,
                    line_start INTEGER,
                    line_end INTEGER,
                    column_start INTEGER,
                    column_end INTEGER,
                    analyzer TEXT,
                    metadata TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
                )
            """)

            # Nodes table (optional, for caching parsed ASTs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    name TEXT,
                    parent_id TEXT,
                    depth INTEGER,
                    line_start INTEGER,
                    line_end INTEGER,
                    metadata TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
                )
            """)

            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metadata TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
                )
            """)

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_findings_analysis ON findings(analysis_id)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_type ON findings(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_analysis ON nodes(analysis_id)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_analysis ON metrics(analysis_id)"
            )

    def save_analysis(
        self,
        analysis_id: str,
        file_path: str,
        findings: list[Finding],
        metrics: Optional[dict[str, Any]] = None,
        language: str = "python",
        node_count: int = 0,
    ) -> None:
        """Save analysis results to database.

        Args:
            analysis_id: Unique identifier for this analysis
            file_path: Path to analyzed file
            findings: List of findings from analysis
            metrics: Optional metrics dictionary
            language: Source language
            node_count: Number of AST nodes analyzed
        """
        timestamp = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Insert analysis record
            cursor.execute(
                """
                INSERT OR REPLACE INTO analyses
                (analysis_id, file_path, timestamp, language, node_count, finding_count, metrics, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,  # noqa: E501
                (
                    analysis_id,
                    file_path,
                    timestamp,
                    language,
                    node_count,
                    len(findings),
                    json.dumps(metrics or {}),
                    "completed",
                ),
            )

            # Delete existing findings for this analysis
            cursor.execute("DELETE FROM findings WHERE analysis_id = ?", (analysis_id,))

            # Insert findings
            for finding in findings:
                cursor.execute(
                    """
                    INSERT INTO findings
                    (finding_id, analysis_id, type, severity, message, file_path,
                     line_start, line_end, column_start, column_end, analyzer, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        finding.finding_id,
                        analysis_id,
                        finding.type,
                        finding.severity,
                        finding.message,
                        str(finding.location.file_path) if finding.location else None,
                        finding.location.line_start if finding.location else None,
                        finding.location.line_end if finding.location else None,
                        finding.location.column_start if finding.location else None,
                        finding.location.column_end if finding.location else None,
                        finding.analyzer,
                        json.dumps(finding.metadata),
                    ),
                )

    def get_analysis(self, analysis_id: str) -> Optional[dict[str, Any]]:
        """Get analysis record by ID.

        Args:
            analysis_id: The analysis ID to retrieve

        Returns:
            Dictionary with analysis data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analyses WHERE analysis_id = ?", (analysis_id,))
            row = cursor.fetchone()

            if row:
                return {
                    "analysis_id": row["analysis_id"],
                    "file_path": row["file_path"],
                    "timestamp": row["timestamp"],
                    "language": row["language"],
                    "node_count": row["node_count"],
                    "finding_count": row["finding_count"],
                    "metrics": json.loads(row["metrics"] or "{}"),
                    "status": row["status"],
                }
            return None

    def get_findings(
        self,
        analysis_id: Optional[str] = None,
        finding_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> list[Finding]:
        """Get findings with optional filters.

        Args:
            analysis_id: Filter by analysis ID
            finding_type: Filter by finding type
            severity: Filter by severity
            limit: Maximum number of results

        Returns:
            List of Finding objects
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM findings WHERE 1=1"
            params = []

            if analysis_id:
                query += " AND analysis_id = ?"
                params.append(analysis_id)

            if finding_type:
                query += " AND type = ?"
                params.append(finding_type)

            if severity:
                query += " AND severity = ?"
                params.append(severity)

            # Use parameterized query for limit to prevent SQL injection
            query += " LIMIT ?"
            params.append(min(max(1, limit), 10000))  # type: ignore[arg-type]  # Sanitize limit value

            cursor.execute(query, params)
            rows = cursor.fetchall()

            findings = []
            for row in rows:
                location = None
                if row["file_path"]:
                    location = SourceLocation(
                        file_path=Path(row["file_path"]),
                        line_start=row["line_start"] or 0,
                        line_end=row["line_end"] or 0,
                        column_start=row["column_start"] or 0,
                        column_end=row["column_end"] or 0,
                    )

                findings.append(
                    Finding(
                        finding_id=row["finding_id"],
                        type=row["type"],
                        severity=row["severity"],
                        message=row["message"] or "",
                        location=location,
                        analyzer=row["analyzer"] or "",
                        metadata=json.loads(row["metadata"] or "{}"),
                    )
                )

            return findings

    def list_analyses(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent analyses.

        Args:
            limit: Maximum number of results

        Returns:
            List of analysis records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()

            return [
                {
                    "analysis_id": row["analysis_id"],
                    "file_path": row["file_path"],
                    "timestamp": row["timestamp"],
                    "language": row["language"],
                    "finding_count": row["finding_count"],
                    "status": row["status"],
                }
                for row in rows
            ]

    def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis and its findings.

        Args:
            analysis_id: The analysis ID to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if exists
            cursor.execute(
                "SELECT COUNT(*) as count FROM analyses WHERE analysis_id = ?",
                (analysis_id,),
            )
            if cursor.fetchone()["count"] == 0:
                return False

            # Delete findings first
            cursor.execute("DELETE FROM findings WHERE analysis_id = ?", (analysis_id,))
            cursor.execute("DELETE FROM nodes WHERE analysis_id = ?", (analysis_id,))
            cursor.execute("DELETE FROM metrics WHERE analysis_id = ?", (analysis_id,))
            cursor.execute("DELETE FROM analyses WHERE analysis_id = ?", (analysis_id,))

            return True

    def get_statistics(self) -> dict[str, Any]:
        """Get overall storage statistics.

        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total analyses
            cursor.execute("SELECT COUNT(*) as count FROM analyses")
            stats["total_analyses"] = cursor.fetchone()["count"]

            # Total findings
            cursor.execute("SELECT COUNT(*) as count FROM findings")
            stats["total_findings"] = cursor.fetchone()["count"]

            # Findings by severity
            cursor.execute("SELECT severity, COUNT(*) as count FROM findings GROUP BY severity")
            stats["findings_by_severity"] = {
                row["severity"]: row["count"] for row in cursor.fetchall()
            }

            # Findings by type
            cursor.execute(
                "SELECT type, COUNT(*) as count FROM findings GROUP BY type ORDER BY count DESC LIMIT 10"  # noqa: E501
            )
            stats["top_finding_types"] = {row["type"]: row["count"] for row in cursor.fetchall()}

            # Recent activity
            cursor.execute(
                "SELECT date(timestamp) as date, COUNT(*) as count FROM analyses GROUP BY date(timestamp) ORDER BY date DESC LIMIT 7"  # noqa: E501
            )
            stats["recent_activity"] = {row["date"]: row["count"] for row in cursor.fetchall()}

            return stats

    def save_metric(
        self,
        analysis_id: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Save a metric value.

        Args:
            analysis_id: The analysis this metric belongs to
            metric_name: Name of the metric
            metric_value: Numeric value
            metadata: Optional additional context
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO metrics (analysis_id, metric_name, metric_value, metadata)
                VALUES (?, ?, ?, ?)
            """,
                (analysis_id, metric_name, metric_value, json.dumps(metadata or {})),
            )

    def get_metrics(
        self, analysis_id: str, metric_name: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get metrics for an analysis.

        Args:
            analysis_id: The analysis to get metrics for
            metric_name: Optional filter by metric name

        Returns:
            List of metric records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if metric_name:
                cursor.execute(
                    "SELECT * FROM metrics WHERE analysis_id = ? AND metric_name = ?",
                    (analysis_id, metric_name),
                )
            else:
                cursor.execute("SELECT * FROM metrics WHERE analysis_id = ?", (analysis_id,))

            return [
                {
                    "metric_name": row["metric_name"],
                    "metric_value": row["metric_value"],
                    "metadata": json.loads(row["metadata"] or "{}"),
                }
                for row in cursor.fetchall()
            ]

    def __repr__(self) -> str:
        return f"ASTStorage(db_path={self.db_path})"
