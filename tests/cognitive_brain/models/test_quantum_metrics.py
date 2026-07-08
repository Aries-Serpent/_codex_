"""
Tests for QuantumMetric ORM model and repository.

Tests CRUD operations, data validation, and query functionality.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cognitive_brain.models.quantum_metrics import (
    QuantumMetric,
    QuantumMetricRepository,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
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
        metric = QuantumMetric(feature="superposition", metric_name="coherence", metric_value=0.95)

        assert metric.feature == "superposition", "feature is not valid"
        assert metric.metric_name == "coherence", "metric_name is not valid"
        assert metric.metric_value == 0.95, "Value must be initialized"
        assert metric.metadata == {}, "Data must not be empty"
        assert metric.timestamp is not None, "timestamp must be initialized"

    def test_invalid_feature_raises_error(self):
        """Test that invalid feature name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid feature"):
            QuantumMetric(feature="invalid_feature", metric_name="coherence", metric_value=0.5)

    def test_valid_features(self):
        """Test all valid feature names."""
        valid_features = [
            "superposition",
            "entanglement",
            "uncertainty",
            "wave_collapse",
        ]

        for feature in valid_features:
            metric = QuantumMetric(feature=feature, metric_name="test", metric_value=1.0)
            assert metric.feature == feature, "feature is not valid"


class TestQuantumMetricRepositoryCRUD:
    """Test repository CRUD operations."""

    def test_create_metric(self, repo):
        """Test inserting a new metric."""
        metric = QuantumMetric(feature="superposition", metric_name="coherence", metric_value=0.95)

        created = repo.create(metric)

        assert created.id is not None, "id must be initialized"
        assert created.id > 0, "id must be greater than zero"

    def test_get_by_id(self, repo):
        """Test retrieving metric by ID."""
        metric = QuantumMetric(feature="superposition", metric_name="coherence", metric_value=0.95)
        created = repo.create(metric)

        retrieved = repo.get_by_id(created.id)

        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.id == created.id, "id is not valid"
        assert retrieved.feature == "superposition", "feature is not valid"
        assert retrieved.metric_value == 0.95, "Value must be initialized"

    def test_delete_metric(self, repo):
        """Test deleting a metric."""
        metric = QuantumMetric(feature="superposition", metric_name="coherence", metric_value=0.95)
        created = repo.create(metric)

        deleted = repo.delete(created.id)
        assert deleted is True, "deleted is not valid"

        retrieved = repo.get_by_id(created.id)
        assert retrieved is None, "retrieved is not valid"


class TestQuantumMetricRepositoryQueries:
    """Test repository query methods."""

    def test_find_by_feature(self, repo):
        """Test finding metrics by feature name."""
        # Create metrics for different features
        for i in range(3):
            repo.create(
                QuantumMetric(
                    feature="superposition",
                    metric_name="coherence",
                    metric_value=0.9 + i * 0.01,
                )
            )

        results = repo.find_by_feature("superposition")

        assert len(results) == 3, "Results must not be empty"
        assert all(m.feature == "superposition" for m in results), "Result must not be empty"

    def test_get_coherence_stats(self, repo):
        """Test getting coherence statistics."""
        # Create coherence metrics
        for value in [0.9, 0.85, 0.95, 0.88]:
            repo.create(
                QuantumMetric(feature="superposition", metric_name="coherence", metric_value=value)
            )

        stats = repo.get_coherence_stats("superposition")

        assert stats["sample_count"] == 4, "Count must be greater than zero"
        assert 0.85 <= stats["avg_coherence"] <= 0.95, "85 is not valid"
        assert stats["min_coherence"] == 0.85, "Condition must be true"
        assert stats["max_coherence"] == 0.95, "Condition must be true"


class TestBatchInsert:
    """Test batch_insert() functionality for Sprint 1 optimization."""

    def test_batch_insert_empty_list(self, repo):
        """Test batch_insert() with 0 metrics (empty list)."""
        metrics = repo.batch_insert([])
        assert metrics == [], "metrics is not valid"

    def test_batch_insert_single_metric(self, repo):
        """Test batch_insert() with 1 metric."""
        metric = QuantumMetric(
            feature="superposition",
            metric_name="coherence",
            metric_value=0.95,
            agent_id="test-agent-1",
        )

        results = repo.batch_insert([metric])

        assert len(results) == 1, "Results must not be empty"
        assert results[0].id is not None, "id must be initialized"
        assert results[0].id > 0, "id must be greater than zero"
        assert results[0].feature == "superposition", "Result must not be empty"
        assert results[0].metric_value == 0.95, "Result must not be empty"

    def test_batch_insert_ten_metrics(self, repo):
        """Test batch_insert() with 10 metrics."""
        metrics = [
            QuantumMetric(
                feature="superposition",
                metric_name="coherence",
                metric_value=0.9 + i * 0.01,
                agent_id=f"test-agent-{i}",
            )
            for i in range(10)
        ]

        results = repo.batch_insert(metrics)

        assert len(results) == 10, "Results must not be empty"
        assert all(m.id is not None for m in results), "id must be initialized"

        # Verify all metrics persisted to database
        for metric in results:
            retrieved = repo.get_by_id(metric.id)
            assert retrieved is not None, "retrieved must be initialized"
            assert retrieved.feature == "superposition", "feature is not valid"
            assert retrieved.metric_name == "coherence", "metric_name is not valid"

    def test_batch_insert_hundred_metrics(self, repo):
        """Test batch_insert() with 100 metrics."""
        metrics = [
            QuantumMetric(
                feature="entanglement",
                metric_name="error_rate",
                metric_value=0.01 + i * 0.0001,
                agent_id=f"agent-{i}",
            )
            for i in range(100)
        ]

        results = repo.batch_insert(metrics)

        assert len(results) == 100, "Results must not be empty"
        assert all(m.id is not None for m in results), "id must be initialized"

        # Verify sample of metrics persisted
        assert repo.get_by_id(results[0].id) is not None, "Value must be initialized"
        assert repo.get_by_id(results[50].id) is not None, "Value must be initialized"
        assert repo.get_by_id(results[99].id) is not None, "Value must be initialized"

    def test_batch_insert_ids_sequential(self, repo):
        """Test that batch_insert() assigns IDs sequentially."""
        metrics = [
            QuantumMetric(
                feature="uncertainty",
                metric_name=f"latency_p99_{i}",  # Unique metric name to avoid constraint
                metric_value=100.0 + i,
            )
            for i in range(20)
        ]

        results = repo.batch_insert(metrics)

        # Check IDs are sequential
        first_id = results[0].id
        for i, metric in enumerate(results):
            assert metric.id == first_id + i, "id is not valid"

    def test_batch_insert_all_persisted(self, repo):
        """Test that all metrics from batch_insert() are persisted to database."""
        metrics = [
            QuantumMetric(
                feature="wave_collapse",
                metric_name=f"accuracy_{i}",  # Unique metric name to avoid constraint
                metric_value=0.85 + i * 0.001,
                metadata={"test_id": i},
            )
            for i in range(50)
        ]

        results = repo.batch_insert(metrics)

        # Verify every single metric is in database
        for result in results:
            retrieved = repo.get_by_id(result.id)
            assert retrieved is not None, "retrieved must be initialized"
            assert "accuracy_" in retrieved.metric_name, "Condition must be true"
            assert retrieved.metadata.get("test_id") is not None, "Value must be initialized"

    def test_batch_insert_backward_compatibility(self, repo):
        """Test backward compatibility - create() still works after batch_insert()."""
        # First do batch insert
        batch_metrics = [
            QuantumMetric(feature="superposition", metric_name="coherence", metric_value=0.9)
            for _ in range(5)
        ]
        repo.batch_insert(batch_metrics)

        # Then use traditional create()
        single_metric = QuantumMetric(
            feature="superposition", metric_name="coherence", metric_value=0.95
        )
        created = repo.create(single_metric)

        assert created.id is not None, "id must be initialized"
        retrieved = repo.get_by_id(created.id)
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.metric_value == 0.95, "Value must be initialized"

    def test_batch_insert_mixed_features(self, repo):
        """Test batch_insert() with multiple feature types."""
        metrics = [
            QuantumMetric(feature="superposition", metric_name="coherence", metric_value=0.9),
            QuantumMetric(feature="entanglement", metric_name="error_rate", metric_value=0.02),
            QuantumMetric(feature="uncertainty", metric_name="latency_p99", metric_value=150.0),
            QuantumMetric(feature="wave_collapse", metric_name="accuracy", metric_value=0.88),
        ]

        results = repo.batch_insert(metrics)

        assert len(results) == 4, "Results must not be empty"
        assert results[0].feature == "superposition", "Result must not be empty"
        assert results[1].feature == "entanglement", "Result must not be empty"
        assert results[2].feature == "uncertainty", "Result must not be empty"
        assert results[3].feature == "wave_collapse", "Result must not be empty"
