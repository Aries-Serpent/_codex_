"""
Quantum Metrics ORM Model

Provides database persistence for quantum feature metrics using a lightweight
ORM-like interface that works with SQLite, PostgreSQL, and MariaDB.
"""

import json
import sqlite3
from datetime import datetime, UTC
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


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
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    id: Optional[int] = None
    
    VALID_FEATURES = {'superposition', 'entanglement', 'uncertainty', 'wave_collapse'}
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        if self.feature not in self.VALID_FEATURES:
            raise ValueError(
                f"Invalid feature: {self.feature}. "
                f"Must be one of {self.VALID_FEATURES}"
            )
        
        if self.metadata is None:
            self.metadata = {}
        
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'feature': self.feature,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'agent_id': self.agent_id,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuantumMetric':
        """Create model from dictionary representation."""
        data = data.copy()
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)


class QuantumMetricRepository:
    """
    Repository for CRUD operations on QuantumMetric.
    
    Provides a simple interface for database operations without requiring
    a full ORM framework like SQLAlchemy.
    """
    
    def __init__(self, db_path: Union[str, Path] = None, connection=None):
        """
        Initialize repository.
        
        Args:
            db_path: Path to SQLite database file
            connection: Existing database connection (alternative to db_path)
        """
        self.db_path = db_path or ':memory:'
        self._connection = connection
    
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
            )
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
        
        cursor.execute(
            "SELECT * FROM quantum_metrics WHERE id = ?",
            (metric_id,)
        )
        
        row = cursor.fetchone()
        
        if not self._connection:
            conn.close()
        
        if row:
            return QuantumMetric.from_dict(dict(row))
        return None
    
    def find_by_feature(
        self,
        feature: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[QuantumMetric]:
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
            (feature, limit, offset)
        )
        
        rows = cursor.fetchall()
        
        if not self._connection:
            conn.close()
        
        return [QuantumMetric.from_dict(dict(row)) for row in rows]
    
    def find_by_metric_name(
        self,
        metric_name: str,
        feature: Optional[str] = None,
        limit: int = 100
    ) -> List[QuantumMetric]:
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
                (metric_name, feature, limit)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM quantum_metrics 
                WHERE metric_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (metric_name, limit)
            )
        
        rows = cursor.fetchall()
        
        if not self._connection:
            conn.close()
        
        return [QuantumMetric.from_dict(dict(row)) for row in rows]
    
    def get_coherence_stats(self, feature: str, hours: int = 24) -> Dict[str, float]:
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
            (feature, hours)
        )
        
        row = cursor.fetchone()
        
        if not self._connection:
            conn.close()
        
        if row:
            return dict(row)
        return {'avg_coherence': None, 'min_coherence': None, 
                'max_coherence': None, 'sample_count': 0}
    
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
        
        cursor.execute(
            "DELETE FROM quantum_metrics WHERE id = ?",
            (metric_id,)
        )
        
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
            (days,)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        
        if not self._connection:
            conn.close()
        
        return deleted
