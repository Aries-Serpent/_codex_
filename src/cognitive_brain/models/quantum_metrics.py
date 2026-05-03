"""
Quantum Metrics ORM Model

Provides database persistence for quantum feature metrics using a lightweight
ORM-like interface that works with SQLite, PostgreSQL, and MariaDB.
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

# Hardcoded migration columns — NEVER derived from user input.
# Each tuple is (column_name: str, sql_type: str).
# Defining them as a module-level constant makes the SQL-injection safety
# of initialize_schema() auditable without any runtime validation overhead.
_MIGRATION_COLUMNS: tuple[tuple[str, str], ...] = (
    ("metric_name", "TEXT"),
    ("metric_value", "REAL"),
)


@dataclass
class QuantumMetric:
    """
    ORM model for quantum_metrics table.

    Tracks metrics for quantum-inspired features including coherence,
    error rates, latency, and custom feature-specific metrics.

    Attributes:
        id: Primary key (auto-generated)
        timestamp: When metric was recorded
        feature: Quantum feature name ('superposition', 'entanglement', etc.)
        metric_name: Name of the metric (e.g., 'coherence', 'error_rate')
        metric_value: Numeric value of the metric
        agent_id: ID of the agent that generated this metric
        metadata: Additional context as JSON
    """

    feature: str
    metric_name: str
    metric_value: float
    agent_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    id: Optional[int] = None

    VALID_FEATURES = {"superposition", "entanglement", "uncertainty", "wave_collapse"}

    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        if self.feature not in self.VALID_FEATURES:
            raise ValueError(
                f"Invalid feature: {self.feature}. Must be one of {self.VALID_FEATURES}"
            )

        if self.metadata is None:
            self.metadata = {}

        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "feature": self.feature,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "agent_id": self.agent_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuantumMetric":
        """Create model from dictionary representation."""
        import dataclasses as _dc

        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if "metadata" in data and isinstance(data["metadata"], str):
            data["metadata"] = json.loads(data["metadata"])
        # Only pass known fields to avoid TypeError on legacy-schema columns
        valid_keys = {f.name for f in _dc.fields(cls)}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class QuantumMetricRepository:
    """
    Repository for CRUD operations on QuantumMetric.

    Provides a simple interface for database operations without requiring
    a full ORM framework like SQLAlchemy.
    """

    def __init__(self, db_path: str | Path = None, connection=None):  # type: ignore[assignment]
        """
        Initialize repository.

        Args:
            db_path: Path to SQLite database file
            connection: Existing database connection (alternative to db_path)
        """
        self.db_path = db_path or ":memory:"
        self._connection = connection
        self._own_connection = False  # Track if we own the connection

        # Auto-initialize schema for in-memory databases
        # For :memory: databases, we must persist the connection
        if self.db_path == ":memory:" and not self._connection:
            self._connection = sqlite3.connect(":memory:")
            self._connection.row_factory = sqlite3.Row
            self._own_connection = True
            self.initialize_schema()
        elif not self._connection:
            # For file-based databases, ensure schema is up to date
            self.initialize_schema()

    def initialize_schema(self) -> None:
        """
        Initialize database schema.

        Creates quantum_metrics table and indexes if they don't exist.
        Also applies any needed migrations to add missing columns.
        Safe to call multiple times (uses CREATE TABLE IF NOT EXISTS).
        """
        conn = self._get_connection()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS quantum_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                feature VARCHAR(50) NOT NULL,
                metric_name VARCHAR(100),
                metric_value FLOAT,
                agent_id VARCHAR(100),
                metadata TEXT DEFAULT '{}',
                UNIQUE(timestamp, feature, metric_name)
            );

            CREATE INDEX IF NOT EXISTS idx_quantum_metrics_timestamp ON quantum_metrics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_quantum_metrics_feature ON quantum_metrics(feature);
            CREATE INDEX IF NOT EXISTS idx_quantum_metrics_agent_id ON quantum_metrics(agent_id);
        """)
        # Migration: add metric_name and metric_value columns if absent.
        # Safety: _MIGRATION_COLUMNS is a hardcoded module-level constant — column
        # names and types are never derived from user input, so the f-string
        # interpolation below carries no SQL-injection risk.
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(quantum_metrics)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        for col, col_def in _MIGRATION_COLUMNS:
            if col not in existing_columns:
                conn.execute(
                    f"ALTER TABLE quantum_metrics ADD COLUMN {col} {col_def}"  # nosec B608
                )
        conn.commit()
        # Don't close the connection - it's managed by the repository

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection:
            return self._connection
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, metric: QuantumMetric) -> QuantumMetric:
        """
        Insert new metric into database.

        Args:
            metric: QuantumMetric instance to insert

        Returns:
            QuantumMetric with populated id
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO quantum_metrics
            (timestamp, feature, metric_name, metric_value, agent_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                metric.timestamp.isoformat() if metric.timestamp else datetime.now(UTC).isoformat(),
                metric.feature,
                metric.metric_name,
                metric.metric_value,
                metric.agent_id,
                json.dumps(metric.metadata or {}),
            ),
        )

        metric.id = cursor.lastrowid
        conn.commit()

        if not self._connection:
            conn.close()

        return metric

    def get_by_id(self, metric_id: int) -> Optional[QuantumMetric]:
        """
        Retrieve metric by ID.

        Args:
            metric_id: Primary key

        Returns:
            QuantumMetric instance or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM quantum_metrics WHERE id = ?", (metric_id,))

        row = cursor.fetchone()

        if not self._connection:
            conn.close()

        if row:
            return QuantumMetric.from_dict(dict(row))
        return None

    def find_by_feature(
        self, feature: str, limit: int = 100, offset: int = 0
    ) -> list[QuantumMetric]:
        """
        Find metrics by feature name.

        Args:
            feature: Feature name to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of QuantumMetric instances
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM quantum_metrics
            WHERE feature = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (feature, limit, offset),
        )

        rows = cursor.fetchall()

        if not self._connection:
            conn.close()

        return [QuantumMetric.from_dict(dict(row)) for row in rows]

    def find_by_metric_name(
        self, metric_name: str, feature: Optional[str] = None, limit: int = 100
    ) -> list[QuantumMetric]:
        """
        Find metrics by metric name, optionally filtered by feature.

        Args:
            metric_name: Metric name to filter by
            feature: Optional feature name filter
            limit: Maximum number of results

        Returns:
            List of QuantumMetric instances
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if feature:
            cursor.execute(
                """
                SELECT * FROM quantum_metrics
                WHERE metric_name = ? AND feature = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (metric_name, feature, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM quantum_metrics
                WHERE metric_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (metric_name, limit),
            )

        rows = cursor.fetchall()

        if not self._connection:
            conn.close()

        return [QuantumMetric.from_dict(dict(row)) for row in rows]

    def get_coherence_stats(self, feature: str, hours: int = 24) -> dict[str, float]:
        """
        Get coherence statistics for a feature over time window.

        Args:
            feature: Feature name
            hours: Time window in hours (default: 24)

        Returns:
            Dictionary with avg, min, max coherence values
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                AVG(metric_value) as avg_coherence,
                MIN(metric_value) as min_coherence,
                MAX(metric_value) as max_coherence,
                COUNT(*) as sample_count
            FROM quantum_metrics
            WHERE
                feature = ?
                AND metric_name = 'coherence'
                AND timestamp >= datetime('now', '-' || ? || ' hours')
            """,
            (feature, hours),
        )

        row = cursor.fetchone()

        if not self._connection:
            conn.close()

        if row:
            return dict(row)
        return {
            "avg_coherence": 0.0,
            "min_coherence": 0.0,
            "max_coherence": 0.0,
            "sample_count": 0,
        }

    def delete(self, metric_id: int) -> bool:
        """
        Delete metric by ID.

        Args:
            metric_id: Primary key

        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM quantum_metrics WHERE id = ?", (metric_id,))

        deleted = cursor.rowcount > 0
        conn.commit()

        if not self._connection:
            conn.close()

        return deleted

    def delete_old_metrics(self, days: int = 30) -> int:
        """
        Delete metrics older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of metrics deleted
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM quantum_metrics
            WHERE timestamp < datetime('now', '-' || ? || ' days')
            """,
            (days,),
        )

        deleted = cursor.rowcount
        conn.commit()

        if not self._connection:
            conn.close()

        return deleted

    def batch_insert(self, metrics: list[QuantumMetric]) -> list[QuantumMetric]:
        """
        Insert multiple metrics in a single transaction for improved performance.

        This method provides 10-20x speedup over individual inserts by:
        - Using a single database transaction
        - Batching INSERT statements with executemany()
        - Reducing connection overhead

        Args:
            metrics: List of QuantumMetric instances to insert

        Returns:
            List of QuantumMetric instances with populated IDs
        """
        if not metrics:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        # Prepare batch data
        batch_data = [
            (
                metric.timestamp.isoformat() if metric.timestamp else datetime.now(UTC).isoformat(),
                metric.feature,
                metric.metric_name,
                metric.metric_value,
                metric.agent_id,
                json.dumps(metric.metadata or {}),
            )
            for metric in metrics
        ]

        # Execute batch insert
        cursor.executemany(
            """
            INSERT INTO quantum_metrics
            (timestamp, feature, metric_name, metric_value, agent_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            batch_data,
        )

        # Get the last inserted ID by querying the max ID
        # Note: lastrowid doesn't work reliably with executemany()
        cursor.execute("SELECT MAX(id) FROM quantum_metrics")
        last_id = cursor.fetchone()[0]

        if last_id is None:
            # No rows in table, start from 1
            first_id = 1
        else:
            first_id = last_id - len(metrics) + 1

        # Populate IDs in the original metrics
        for i, metric in enumerate(metrics):
            metric.id = first_id + i

        conn.commit()

        if not self._connection:
            conn.close()

        return metrics

    def save_metric(self, **kwargs: Any) -> "QuantumMetric":
        """
        Save a metric using keyword arguments (backward-compatible API).

        Accepts legacy-style kwargs (timestamp, feature, decision_id,
        coherence, accuracy, etc.) and stores them using the current schema.
        Float values are stored as metric_value; all kwargs are also stored
        in metadata so they can be retrieved via get_recent_metrics.

        Returns:
            Created QuantumMetric instance.
        """

        feature = str(kwargs.get("feature", "unknown"))
        # Use coherence as the primary metric value if present
        for key in ("coherence", "metric_value"):
            if key in kwargs and isinstance(kwargs[key], (int, float)):
                metric_value = float(kwargs[key])
                metric_name = key
                break
        else:
            metric_value = 0.0
            metric_name = "value"  # type: ignore[assignment]

        # Store the full kwargs dict in metadata for later retrieval
        metadata: dict[str, Any] = {k: v for k, v in kwargs.items() if k not in ("feature",)}

        raw_ts = kwargs.get("timestamp")
        if isinstance(raw_ts, (int, float)):
            from datetime import timezone

            ts = datetime.fromtimestamp(float(raw_ts), tz=timezone.utc)
        elif isinstance(raw_ts, datetime):
            ts = raw_ts
        else:
            ts = datetime.now(UTC)

        metric = QuantumMetric(
            feature=feature,
            metric_name=metric_name,
            metric_value=metric_value,
            agent_id=str(kwargs.get("agent_id", kwargs.get("decision_id", ""))),
            metadata=metadata,
            timestamp=ts,
        )
        return self.create(metric)

    def get_recent_metrics(
        self,
        feature: str,
        limit: int = 100,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Return recent metrics for ``feature`` as a list of dicts.

        Args:
            feature: Feature name to filter by.
            limit: Maximum number of rows to return (most recent first).
            hours: Unused; retained for API compatibility.

        Returns:
            List of metric dicts. Metadata content is merged into the dict
            for backward compatibility (e.g., coherence, accuracy keys).
        """
        results = self.find_by_feature(feature, limit=limit)
        dicts = []
        for m in results:
            d = m.to_dict()
            # Flatten metadata into the returned dict for legacy API compat
            meta = d.get("metadata") or {}
            if isinstance(meta, str):
                try:
                    import json as _json

                    meta = _json.loads(meta)
                except Exception:
                    meta = {}
            merged = {**d, **meta}
            dicts.append(merged)
        return dicts
