"""
SQLite-based metrics database for RAG analytics.

Tracks query performance, cache hits, index statistics, and usage patterns.
"""

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class QueryMetric:
    """Single query metric record."""

    timestamp: str
    query: str
    index_name: str
    tenant_id: str
    top_k: int
    latency_ms: float
    cache_hit: bool
    num_results: int
    avg_score: float


class MetricsDatabase:
    """SQLite database for RAG metrics storage and retrieval."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize metrics database.

        Args:
            db_path: Path to SQLite database file. If None, uses default.
        """
        if db_path is None:
            db_path = Path.home() / ".codex" / "rag_metrics.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query TEXT NOT NULL,
                    index_name TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    top_k INTEGER NOT NULL,
                    latency_ms REAL NOT NULL,
                    cache_hit INTEGER NOT NULL,
                    num_results INTEGER NOT NULL,
                    avg_score REAL NOT NULL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON query_metrics(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_index_name
                ON query_metrics(index_name)
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS index_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    index_name TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    num_chunks INTEGER NOT NULL,
                    embedding_dim INTEGER NOT NULL,
                    size_mb REAL NOT NULL
                )
            """)

            conn.commit()

    def log_query(self, metric: QueryMetric) -> None:
        """
        Log a query metric.

        Args:
            metric: Query metric to log
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO query_metrics
                (timestamp, query, index_name, tenant_id, top_k,
                 latency_ms, cache_hit, num_results, avg_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metric.timestamp,
                    metric.query,
                    metric.index_name,
                    metric.tenant_id,
                    metric.top_k,
                    metric.latency_ms,
                    1 if metric.cache_hit else 0,
                    metric.num_results,
                    metric.avg_score,
                ),
            )
            conn.commit()

    def get_stats(self, index_name: Optional[str] = None, hours: int = 24) -> dict[str, Any]:
        """
        Get aggregate statistics.

        Args:
            index_name: Filter by index name (None for all)
            hours: Time window in hours

        Returns:
            Dictionary with aggregate stats
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT
                    COUNT(*) as total_queries,
                    AVG(latency_ms) as avg_latency,
                    MIN(latency_ms) as min_latency,
                    MAX(latency_ms) as max_latency,
                    SUM(cache_hit) * 100.0 / COUNT(*) as cache_hit_rate,
                    AVG(num_results) as avg_results,
                    AVG(avg_score) as avg_score
                FROM query_metrics
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
            """
            params = [hours]

            if index_name:
                query += " AND index_name = ?"
                params.append(index_name)  # type: ignore[arg-type]

            cursor = conn.execute(query, params)
            row = cursor.fetchone()

            return {
                "total_queries": row[0] or 0,
                "avg_latency_ms": round(row[1] or 0, 2),
                "min_latency_ms": round(row[2] or 0, 2),
                "max_latency_ms": round(row[3] or 0, 2),
                "cache_hit_rate": round(row[4] or 0, 2),
                "avg_results": round(row[5] or 0, 2),
                "avg_score": round(row[6] or 0, 4),
            }

    def get_percentiles(
        self, index_name: Optional[str] = None, hours: int = 24
    ) -> dict[str, float]:
        """
        Calculate latency percentiles.

        Args:
            index_name: Filter by index name
            hours: Time window in hours

        Returns:
            Dictionary with p50, p95, p99 latency
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT latency_ms
                FROM query_metrics
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
            """
            params = [hours]

            if index_name:
                query += " AND index_name = ?"
                params.append(index_name)  # type: ignore[arg-type]

            query += " ORDER BY latency_ms"

            cursor = conn.execute(query, params)
            latencies = [row[0] for row in cursor.fetchall()]

            if not latencies:
                return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

            n = len(latencies)
            return {
                "p50": latencies[int(n * 0.50)],
                "p95": latencies[int(n * 0.95)],
                "p99": latencies[int(n * 0.99)],
            }

    def export_to_json(self, output_path: Path, hours: int = 24) -> None:
        """
        Export metrics to JSON file.

        Args:
            output_path: Path to output JSON file
            hours: Time window in hours
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, query, index_name, tenant_id, top_k,
                       latency_ms, cache_hit, num_results, avg_score
                FROM query_metrics
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """,
                (hours,),
            )

            metrics = []
            for row in cursor.fetchall():
                metrics.append(
                    {
                        "timestamp": row[0],
                        "query": row[1],
                        "index_name": row[2],
                        "tenant_id": row[3],
                        "top_k": row[4],
                        "latency_ms": row[5],
                        "cache_hit": bool(row[6]),
                        "num_results": row[7],
                        "avg_score": row[8],
                    }
                )

            with open(output_path, "w") as f:
                json.dump(metrics, f, indent=2)
