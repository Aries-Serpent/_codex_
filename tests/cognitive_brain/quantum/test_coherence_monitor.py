"""
Tests for CoherenceMonitor class.

Tests metric recording, alert triggering, and automatic rollback functionality.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.coherence_monitor import (
    CoherenceMonitor,
    Alert,
    AlertLevel,
    AlertThreshold
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
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
    return QuantumConfig(
        quantum_mode=True,
        superposition=True,
        entanglement=True
    )


@pytest.fixture
def repo(temp_db):
    """Create repository."""
    return QuantumMetricRepository(db_path=temp_db)


@pytest.fixture
def monitor(config, repo):
    """Create coherence monitor."""
    return CoherenceMonitor(config=config, repository=repo)


class TestAlertThreshold:
    """Test AlertThreshold class."""
    
    def test_less_than_critical(self):
        """Test less_than comparison triggers critical alert."""
        threshold = AlertThreshold(
            metric_name='coherence',
            warning_threshold=0.5,
            critical_threshold=0.3,
            comparison='less_than'
        )
        
        assert threshold.check(0.2) == AlertLevel.CRITICAL
        assert threshold.check(0.4) == AlertLevel.WARNING
        assert threshold.check(0.6) is None
    
    def test_greater_than_critical(self):
        """Test greater_than comparison triggers critical alert."""
        threshold = AlertThreshold(
            metric_name='error_rate',
            warning_threshold=0.05,
            critical_threshold=0.10,
            comparison='greater_than'
        )
        
        assert threshold.check(0.15) == AlertLevel.CRITICAL
        assert threshold.check(0.07) == AlertLevel.WARNING
        assert threshold.check(0.02) is None


class TestCoherenceMonitorBasics:
    """Test basic CoherenceMonitor functionality."""
    
    def test_initialization(self, monitor):
        """Test monitor initializes correctly."""
        assert monitor.config is not None
        assert monitor.repository is not None
        assert len(monitor.thresholds) == 4
        assert not monitor.is_rollback_triggered
    
    def test_record_metric(self, monitor):
        """Test recording a metric."""
        metric = monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95,
            agent_id='test-agent'
        )
        
        assert metric.id is not None
        assert metric.feature == 'superposition'
        assert metric.metric_value == 0.95
    
    def test_record_multiple_metrics(self, monitor):
        """Test recording multiple metrics."""
        for i in range(5):
            monitor.record_metric(
                feature='superposition',
                metric_name='coherence',
                metric_value=0.9 + i * 0.01
            )
        
        health = monitor.get_feature_health('superposition')
        assert health['coherence']['samples'] == 5


class TestAlertTriggering:
    """Test alert triggering logic."""
    
    def test_critical_coherence_alert(self, monitor):
        """Test critical alert triggers on low coherence."""
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.2  # Below 0.3 critical threshold
        )
        
        alerts = monitor.get_active_alerts()
        assert len(alerts) > 0
        assert alerts[0].level == AlertLevel.CRITICAL
    
    def test_warning_error_rate_alert(self, monitor):
        """Test warning alert triggers on high error rate."""
        monitor.record_metric(
            feature='entanglement',
            metric_name='error_rate',
            metric_value=0.06  # Above 0.05 warning threshold
        )
        
        alerts = monitor.get_active_alerts(level=AlertLevel.WARNING)
        assert len(alerts) > 0
    
    def test_no_alert_on_healthy_metrics(self, monitor):
        """Test no alerts trigger for healthy metrics."""
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95
        )
        
        alerts = monitor.get_active_alerts()
        assert len(alerts) == 0


class TestAutomaticRollback:
    """Test automatic rollback functionality."""
    
    def test_rollback_triggered_on_critical_alert(self, monitor):
        """Test rollback triggers on critical alert."""
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.1  # Critical
        )
        
        assert monitor.is_rollback_triggered
    
    def test_rollback_not_triggered_on_warning(self, monitor):
        """Test rollback doesn't trigger on warning alert."""
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.4  # Warning but not critical
        )
        
        assert not monitor.is_rollback_triggered
    
    def test_reset_rollback_flag(self, monitor):
        """Test resetting rollback flag."""
        # Trigger rollback
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.1
        )
        assert monitor.is_rollback_triggered
        
        # Reset
        monitor.reset_rollback_flag()
        assert not monitor.is_rollback_triggered


class TestHealthMonitoring:
    """Test feature health monitoring."""
    
    def test_get_feature_health(self, monitor):
        """Test getting feature health status."""
        # Record some metrics
        for value in [0.9, 0.85, 0.95]:
            monitor.record_metric(
                feature='superposition',
                metric_name='coherence',
                metric_value=value
            )
        
        health = monitor.get_feature_health('superposition')
        
        assert health['feature'] == 'superposition'
        assert health['coherence']['samples'] == 3
        assert health['health_status'] in ['healthy', 'degraded', 'critical']
    
    def test_healthy_status(self, monitor):
        """Test healthy status assessment."""
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.95
        )
        
        health = monitor.get_feature_health('superposition')
        assert health['health_status'] == 'healthy'
    
    def test_critical_status(self, monitor):
        """Test critical status assessment."""
        monitor.record_metric(
            feature='superposition',
            metric_name='coherence',
            metric_value=0.2
        )
        
        health = monitor.get_feature_health('superposition')
        assert health['health_status'] == 'critical'


class TestAlertManagement:
    """Test alert management operations."""
    
    def test_get_active_alerts_by_feature(self, monitor):
        """Test filtering alerts by feature."""
        monitor.record_metric('superposition', 'coherence', 0.1)
        monitor.record_metric('entanglement', 'coherence', 0.1)
        
        sup_alerts = monitor.get_active_alerts(feature='superposition')
        assert all(a.feature == 'superposition' for a in sup_alerts)
    
    def test_clear_all_alerts(self, monitor):
        """Test clearing all alerts."""
        monitor.record_metric('superposition', 'coherence', 0.1)
        assert len(monitor.get_active_alerts()) > 0
        
        cleared = monitor.clear_alerts()
        assert cleared > 0
        assert len(monitor.get_active_alerts()) == 0
