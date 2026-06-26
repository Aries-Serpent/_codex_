"""
Tests for CoherenceMonitor class.

Tests metric recording, alert triggering, and automatic rollback functionality.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import (
    AlertLevel,
    AlertThreshold,
    CoherenceMonitor,
)
from cognitive_brain.quantum.config import QuantumConfig


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

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
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def config():
    """Create test quantum config."""
    return QuantumConfig(quantum_mode=True, superposition=True, entanglement=True)


@pytest.fixture
def repo(temp_db):
    """Create repository."""
    return QuantumMetricRepository(db_path=temp_db)


@pytest.fixture
def monitor(config, repo):
    """Create coherence monitor with small batch size for testing."""
    # Use batch_size=1 for backward compatibility with existing tests
    return CoherenceMonitor(config=config, repository=repo, batch_size=1)


class TestAlertThreshold:
    """Test AlertThreshold class."""

    def test_less_than_critical(self):
        """Test less_than comparison triggers critical alert."""
        threshold = AlertThreshold(
            metric_name="coherence",
            warning_threshold=0.5,
            critical_threshold=0.3,
            comparison="less_than",
        )

        assert threshold.check(0.2) == AlertLevel.CRITICAL, "Condition must be true"
        assert threshold.check(0.4) == AlertLevel.WARNING, "Condition must be true"
        assert threshold.check(0.6) is None, "Condition must be true"

    def test_greater_than_critical(self):
        """Test greater_than comparison triggers critical alert."""
        threshold = AlertThreshold(
            metric_name="error_rate",
            warning_threshold=0.05,
            critical_threshold=0.10,
            comparison="greater_than",
        )

        assert threshold.check(0.15) == AlertLevel.CRITICAL, "Condition must be true"
        assert threshold.check(0.07) == AlertLevel.WARNING, "Condition must be true"
        assert threshold.check(0.02) is None, "Condition must be true"


class TestCoherenceMonitorBasics:
    """Test basic CoherenceMonitor functionality."""

    def test_initialization(self, monitor):
        """Test monitor initializes correctly."""
        assert monitor.config is not None, "config must be initialized"
        assert monitor.repository is not None, "repository must be initialized"
        assert len(monitor.thresholds) == 4, "Collection must not be empty"
        assert not monitor.is_rollback_triggered, "Condition must be true"

    def test_record_metric(self, monitor):
        """Test recording a metric."""
        metric = monitor.record_metric(
            feature="superposition",
            metric_name="coherence",
            metric_value=0.95,
            agent_id="test-agent",
        )

        assert metric.id is not None, "id must be initialized"
        assert metric.feature == "superposition", "feature is not valid"
        assert metric.metric_value == 0.95, "Value must be initialized"

    def test_record_multiple_metrics(self, monitor):
        """Test recording multiple metrics."""
        for i in range(5):
            monitor.record_metric(
                feature="superposition",
                metric_name="coherence",
                metric_value=0.9 + i * 0.01,
            )

        health = monitor.get_feature_health("superposition")
        assert health["coherence"]["samples"] == 5, "Condition must be true"


class TestAlertTriggering:
    """Test alert triggering logic."""

    def test_critical_coherence_alert(self, monitor):
        """Test critical alert triggers on low coherence."""
        monitor.record_metric(
            feature="superposition",
            metric_name="coherence",
            metric_value=0.2,  # Below 0.3 critical threshold
        )

        alerts = monitor.get_active_alerts()
        assert len(alerts) > 0, "Alerts must not be empty"
        assert alerts[0].level == AlertLevel.CRITICAL, "level is not valid"

    def test_warning_error_rate_alert(self, monitor):
        """Test warning alert triggers on high error rate."""
        monitor.record_metric(
            feature="entanglement",
            metric_name="error_rate",
            metric_value=0.06,  # Above 0.05 warning threshold
        )

        alerts = monitor.get_active_alerts(level=AlertLevel.WARNING)
        assert len(alerts) > 0, "Alerts must not be empty"

    def test_no_alert_on_healthy_metrics(self, monitor):
        """Test no alerts trigger for healthy metrics."""
        monitor.record_metric(feature="superposition", metric_name="coherence", metric_value=0.95)

        alerts = monitor.get_active_alerts()
        assert len(alerts) == 0, "Alerts must not be empty"


class TestAutomaticRollback:
    """Test automatic rollback functionality."""

    def test_rollback_triggered_on_critical_alert(self, monitor):
        """Test rollback triggers on critical alert."""
        monitor.record_metric(
            feature="superposition",
            metric_name="coherence",
            metric_value=0.1,  # Critical
        )

        assert monitor.is_rollback_triggered, "monit is not valid"

    def test_rollback_not_triggered_on_warning(self, monitor):
        """Test rollback doesn't trigger on warning alert."""
        monitor.record_metric(
            feature="superposition",
            metric_name="coherence",
            metric_value=0.4,  # Warning but not critical
        )

        assert not monitor.is_rollback_triggered, "Condition must be true"

    def test_reset_rollback_flag(self, monitor):
        """Test resetting rollback flag."""
        # Trigger rollback
        monitor.record_metric(feature="superposition", metric_name="coherence", metric_value=0.1)
        assert monitor.is_rollback_triggered, "monit is not valid"

        # Reset
        monitor.reset_rollback_flag()
        assert not monitor.is_rollback_triggered, "Condition must be true"


class TestHealthMonitoring:
    """Test feature health monitoring."""

    def test_get_feature_health(self, monitor):
        """Test getting feature health status."""
        # Record some metrics
        for value in [0.9, 0.85, 0.95]:
            monitor.record_metric(
                feature="superposition", metric_name="coherence", metric_value=value
            )

        health = monitor.get_feature_health("superposition")

        assert health["feature"] == "superposition", "Condition must be true"
        assert health["coherence"]["samples"] == 3, "Condition must be true"
        assert health["health_status"] in ["healthy", "degraded", "critical"]

    def test_healthy_status(self, monitor):
        """Test healthy status assessment."""
        monitor.record_metric(feature="superposition", metric_name="coherence", metric_value=0.95)

        health = monitor.get_feature_health("superposition")
        assert health["health_status"] == "healthy", "Condition must be true"

    def test_critical_status(self, monitor):
        """Test critical status assessment."""
        monitor.record_metric(feature="superposition", metric_name="coherence", metric_value=0.2)

        health = monitor.get_feature_health("superposition")
        assert health["health_status"] == "critical", "Condition must be true"


class TestAlertManagement:
    """Test alert management operations."""

    def test_get_active_alerts_by_feature(self, monitor):
        """Test filtering alerts by feature."""
        monitor.record_metric("superposition", "coherence", 0.1)
        monitor.record_metric("entanglement", "coherence", 0.1)
        monitor.flush_batch()

        sup_alerts = monitor.get_active_alerts(feature="superposition")
        assert all(a.feature == "superposition" for a in sup_alerts), "feature is not valid"

    def test_clear_all_alerts(self, monitor):
        """Test clearing all alerts."""
        monitor.record_metric("superposition", "coherence", 0.1)
        monitor.flush_batch()
        assert len(monitor.get_active_alerts()) > 0, "Collection must not be empty"

        cleared = monitor.clear_alerts()
        assert cleared > 0, "cleared must be greater than zero"
        assert len(monitor.get_active_alerts()) == 0, "Collection must not be empty"


class TestCoherenceMonitorBatching:
    """Test CoherenceMonitor batching functionality (Sprint 1)."""

    def test_internal_batching_buffer(self, config, repo):
        """Test internal _pending_metrics buffer exists and works."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=10)

        # Record 5 metrics (below batch_size)
        for i in range(5):
            monitor.record_metric(
                feature="superposition", metric_name="coherence", metric_value=0.9 + i * 0.01
            )

        # Check buffer has 5 pending metrics
        assert len(monitor._pending_metrics) == 5, "Collection must not be empty"

        # Metrics should NOT be in database yet
        metrics_in_db = repo.find_by_feature("superposition")
        assert len(metrics_in_db) == 0, "Metrics_in_db must not be empty"

    def test_auto_flush_at_batch_size(self, config, repo):
        """Test auto-flush at batch_size threshold (default 100)."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=10)

        # Record exactly batch_size metrics
        for i in range(10):
            monitor.record_metric(
                feature="superposition", metric_name="coherence", metric_value=0.9
            )

        # Buffer should be empty (auto-flushed)
        assert len(monitor._pending_metrics) == 0, "Collection must not be empty"

        # All 10 metrics should be in database
        metrics_in_db = repo.find_by_feature("superposition")
        assert len(metrics_in_db) == 10, "Metrics_in_db must not be empty"

    def test_manual_flush_batch(self, config, repo):
        """Test manual flush_batch() method."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=100)

        # Record 20 metrics (below batch_size, won't auto-flush)
        for i in range(20):
            monitor.record_metric(
                feature="entanglement", metric_name="error_rate", metric_value=0.01
            )

        # Metrics should be pending
        assert len(monitor._pending_metrics) == 20, "Collection must not be empty"

        # Manually flush
        flushed_count = monitor.flush_batch()

        assert flushed_count == 20, "Count must be greater than zero"
        assert len(monitor._pending_metrics) == 0, "Collection must not be empty"

        # All 20 metrics should be in database
        metrics_in_db = repo.find_by_feature("entanglement")
        assert len(metrics_in_db) == 20, "Metrics_in_db must not be empty"

    def test_metrics_persisted_after_flush(self, config, repo):
        """Test that metrics are actually persisted to database after flush."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=50)

        # Record 30 metrics with specific values
        for i in range(30):
            monitor.record_metric(
                feature="uncertainty",
                metric_name="latency_p99",
                metric_value=100.0 + i,
                agent_id=f"agent-{i}",
            )

        # Flush
        monitor.flush_batch()

        # Verify all metrics in database with correct values
        metrics_in_db = repo.find_by_feature("uncertainty", limit=50)
        assert len(metrics_in_db) == 30, "Metrics_in_db must not be empty"

        # Check specific values
        values = [m.metric_value for m in metrics_in_db]
        assert min(values) >= 100.0, "Value must be greater than zero"
        assert max(values) < 130.0, "Value must be initialized"

    def test_backward_compatibility_existing_code(self, config, repo):
        """Test backward compatibility - existing code without flush_batch() still works."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=5)

        # Existing code pattern: record metrics until auto-flush
        for i in range(15):
            monitor.record_metric(
                feature="superposition", metric_name="coherence", metric_value=0.9
            )

        # Should have auto-flushed three times (at 5, 10, and 15), with 0 pending
        assert len(monitor._pending_metrics) == 0, "Collection must not be empty"

        # All 15 should be in database
        metrics_in_db = repo.find_by_feature("superposition", limit=50)
        assert len(metrics_in_db) == 15, "Metrics_in_db must not be empty"

    def test_flush_batch_returns_zero_when_empty(self, config, repo):
        """Test flush_batch() returns 0 when buffer is empty."""
        monitor = CoherenceMonitor(config=config, repository=repo)

        # Flush empty buffer
        count = monitor.flush_batch()
        assert count == 0, "Count must be greater than zero"

    def test_multiple_flushes(self, config, repo):
        """Test multiple flush operations work correctly."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=100)

        # First batch
        for i in range(10):
            monitor.record_metric("superposition", "coherence", 0.9)
        count1 = monitor.flush_batch()
        assert count1 == 10, "Count must be greater than zero"

        # Second batch
        for i in range(15):
            monitor.record_metric("superposition", "coherence", 0.85)
        count2 = monitor.flush_batch()
        assert count2 == 15, "Count must be greater than zero"

        # Total in database
        metrics_in_db = repo.find_by_feature("superposition", limit=50)
        assert len(metrics_in_db) == 25, "Metrics_in_db must not be empty"

    def test_batching_with_alert_triggering(self, config, repo):
        """Test that alert checking works even before batch flush."""
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=100)

        # Record critical metric (should trigger alert before DB persist)
        monitor.record_metric(
            feature="superposition", metric_name="coherence", metric_value=0.1  # Critical threshold
        )

        # Alert should be triggered even though not flushed to DB
        alerts = monitor.get_active_alerts()
        assert len(alerts) > 0, "Alerts must not be empty"
        assert alerts[0].level == AlertLevel.CRITICAL, "level is not valid"

    def test_custom_batch_size(self, config, repo):
        """Test custom batch_size parameter works."""
        # Use small batch size for testing
        monitor = CoherenceMonitor(config=config, repository=repo, batch_size=3)

        # Record 2 metrics (below threshold)
        monitor.record_metric("superposition", "coherence", 0.9)
        monitor.record_metric("superposition", "coherence", 0.92)
        assert len(monitor._pending_metrics) == 2, "Collection must not be empty"

        # Record 3rd metric (at threshold, should auto-flush)
        monitor.record_metric("superposition", "coherence", 0.95)
        assert len(monitor._pending_metrics) == 0, "Collection must not be empty"

        # All 3 in database
        metrics_in_db = repo.find_by_feature("superposition")
        assert len(metrics_in_db) == 3, "Metrics_in_db must not be empty"
