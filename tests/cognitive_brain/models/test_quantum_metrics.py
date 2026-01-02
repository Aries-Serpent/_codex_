"""
Tests for QuantumMetric ORM model and repository.

Tests CRUD operations, data validation, and query functionality.
"""

import pytest
import sqlite3
import tempfile
from datetime from pathlib import Path

from cognitive_brain.models.quantum_metrics import (
    QuantumMetric,
    QuantumMetricRepository
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE quantum_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            feature VARCHAR(50) NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            agent_id VARCHAR(100),
            metadata TEXT DEFAULT '{}',
            UNIQUE(timestamp, feature, metric_name)
        );
    """)
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def repo(temp_db):
    """Create repository with temp database."""
    return QuantumMetricRepository(db_path=temp_db)


class TestQuantumMetricModel:
    """Test QuantumMetric model class."""
    
    def test_create_basic_metric(self):
        """Test creating a basic quantum metric."""
        metric = QuantumMetric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95
        )
        
        assert metric.feature == 'superposition'
        assert metric.metric_name == 'coherence'
        assert metric.metric_value == 0.95
        assert metric.metadata == {}
        assert metric.timestamp is not None
    
    def test_invalid_feature_raises_error(self):
        """Test that invalid feature name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid feature"):
            QuantumMetric(
                feature='invalid_feature',
                metric_name='coherence',
                metric_value=0.5
            )
    
    def test_valid_features(self):
        """Test all valid feature names."""
        valid_features = ['superposition', 'entanglement', 'uncertainty', 'wave_collapse']
        
        for feature in valid_features:
            metric = QuantumMetric(
                feature=feature,
                metric_name='test',
                metric_value=1.0
            )
            assert metric.feature == feature


class TestQuantumMetricRepositoryCRUD:
    """Test repository CRUD operations."""
    
    def test_create_metric(self, repo):
        """Test inserting a new metric."""
        metric = QuantumMetric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95
        )
        
        created = repo.create(metric)
        
        assert created.id is not None
        assert created.id > 0
    
    def test_get_by_id(self, repo):
        """Test retrieving metric by ID."""
        metric = QuantumMetric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95
        )
        created = repo.create(metric)
        
        retrieved = repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.feature == 'superposition'
        assert retrieved.metric_value == 0.95
    
    def test_delete_metric(self, repo):
        """Test deleting a metric."""
        metric = QuantumMetric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95
        )
        created = repo.create(metric)
        
        deleted = repo.delete(created.id)
        assert deleted is True
        
        retrieved = repo.get_by_id(created.id)
        assert retrieved is None


class TestQuantumMetricRepositoryQueries:
    """Test repository query methods."""
    
    def test_find_by_feature(self, repo):
        """Test finding metrics by feature name."""
        # Create metrics for different features
        for i in range(3):
            repo.create(QuantumMetric(
                feature='superposition',
                metric_name='coherence',
                metric_value=0.9 + i * 0.01
            ))
        
        results = repo.find_by_feature('superposition')
        
        assert len(results) == 3
        assert all(m.feature == 'superposition' for m in results)
    
    def test_get_coherence_stats(self, repo):
        """Test getting coherence statistics."""
        # Create coherence metrics
        for value in [0.9, 0.85, 0.95, 0.88]:
            repo.create(QuantumMetric(
                feature='superposition',
                metric_name='coherence',
                metric_value=value
            ))
        
        stats = repo.get_coherence_stats('superposition')
        
        assert stats['sample_count'] == 4
        assert 0.85 <= stats['avg_coherence'] <= 0.95
        assert stats['min_coherence'] == 0.85
        assert stats['max_coherence'] == 0.95
