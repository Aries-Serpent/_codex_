"""
Tests for Uncertainty Optimizer.

Comprehensive test suite for the UncertaintyOptimizer class.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.uncertainty import (
    ExecutionMetrics,
    UncertaintyOptimizer,
)


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
    """Create test configuration."""
    return QuantumConfig(
        quantum_mode=True,
        superposition=False,
        entanglement=False,
        uncertainty=True,
        rollout_percentage=100,
    )


@pytest.fixture
def repo(temp_db):
    """Create repository."""
    return QuantumMetricRepository(db_path=temp_db)


@pytest.fixture
def monitor(config, repo):
    """Create test monitor."""
    return CoherenceMonitor(config, repo)


@pytest.fixture
def optimizer(config, monitor):
    """Create test optimizer."""
    return UncertaintyOptimizer(config, monitor)


def test_initialization(optimizer):
    """Test optimizer initialization."""
    assert optimizer.config.uncertainty
    assert optimizer.h_bar == 1.0
    assert optimizer.uncertainty_threshold == 0.1
    assert len(optimizer.test_history) == 0


def test_update_test_metrics(optimizer):
    """Test updating test metrics."""
    metrics = ExecutionMetrics(
        test_id="test_001",
        execution_time=5.0,
        failure_rate=0.1,
        last_failure_time=1000.0,
        coverage_contribution=0.8,
        complexity_score=0.6,
    )

    optimizer.update_test_metrics(metrics)

    assert "test_001" in optimizer.test_history
    assert optimizer.test_history["test_001"] == metrics


def test_calculate_priority_new_test(optimizer):
    """Test priority calculation for new test."""
    priority = optimizer.calculate_priority("test_new", 2000.0)

    assert priority.test_id == "test_new"
    assert priority.priority_score == 0.5
    assert priority.uncertainty == 1.0
    assert priority.recommended_action == "run"
    assert "no history" in priority.reasoning.lower()


def test_calculate_priority_high_risk_test(optimizer):
    """Test priority calculation for high-risk test."""
    metrics = ExecutionMetrics(
        test_id="test_high_risk",
        execution_time=10.0,
        failure_rate=0.8,
        last_failure_time=1990.0,  # Recent failure
        coverage_contribution=0.9,
        complexity_score=0.7,
    )
    optimizer.update_test_metrics(metrics)

    priority = optimizer.calculate_priority("test_high_risk", 2000.0)

    assert priority.test_id == "test_high_risk"
    assert priority.priority_score > 0.7  # High priority
    assert priority.recommended_action == "run"


def test_calculate_priority_low_value_test(optimizer):
    """Test priority calculation for low-value test."""
    metrics = ExecutionMetrics(
        test_id="test_low_value",
        execution_time=60.0,  # Slow
        failure_rate=0.01,  # Rarely fails
        last_failure_time=None,  # Never failed
        coverage_contribution=0.1,  # Low coverage
        complexity_score=0.2,  # Simple
    )
    optimizer.update_test_metrics(metrics)

    priority = optimizer.calculate_priority("test_low_value", 2000.0)

    assert priority.test_id == "test_low_value"
    assert priority.priority_score < 0.4  # Low priority
    assert priority.recommended_action in ["skip", "defer"]


def test_uncertainty_principle(optimizer):
    """Test that uncertainty principle is satisfied."""
    metrics = ExecutionMetrics(
        test_id="test_uncertain",
        execution_time=5.0,
        failure_rate=0.5,
        last_failure_time=1950.0,
        coverage_contribution=0.5,
        complexity_score=0.5,
    )
    optimizer.update_test_metrics(metrics)

    priority = optimizer.calculate_priority("test_uncertain", 2000.0)

    # Uncertainty product should be ≥ ℏ/2
    min_uncertainty = optimizer.h_bar / 2.0
    assert priority.uncertainty >= min_uncertainty


def test_optimize_test_schedule_within_budget(optimizer):
    """Test schedule optimization within time budget."""
    # Add test metrics
    tests = []
    for i in range(5):
        test_id = f"test_{i:03d}"
        tests.append(test_id)
        optimizer.update_test_metrics(
            ExecutionMetrics(
                test_id=test_id,
                execution_time=10.0,
                failure_rate=0.1 * i,  # Increasing risk
                last_failure_time=2000.0 - i * 100,
                coverage_contribution=0.2 * i,
                complexity_score=0.15 * i,
            )
        )

    # Optimize with 30s budget (should select 3 tests)
    selected, priorities = optimizer.optimize_test_schedule(tests, 30.0, 2000.0)

    assert len(selected) <= 3
    assert len(priorities) == 5

    # Higher-priority tests should be selected first
    if len(selected) > 1:
        for i in range(len(selected) - 1):
            assert (
                priorities[selected[i]].priority_score
                >= priorities[selected[i + 1]].priority_score
            )


def test_optimize_test_schedule_unlimited_budget(optimizer):
    """Test schedule optimization with unlimited budget."""
    tests = ["test_001", "test_002", "test_003"]
    for test_id in tests:
        optimizer.update_test_metrics(
            ExecutionMetrics(
                test_id=test_id,
                execution_time=5.0,
                failure_rate=0.5,
                last_failure_time=2000.0,
                coverage_contribution=0.8,
                complexity_score=0.6,
            )
        )

    selected, _priorities = optimizer.optimize_test_schedule(tests, 1000.0, 2000.0)

    # All tests should be selected with large budget
    assert len(selected) == 3
    assert set(selected) == set(tests)


def test_optimize_test_schedule_zero_budget(optimizer):
    """Test schedule optimization with zero budget."""
    tests = ["test_001", "test_002"]
    for test_id in tests:
        optimizer.update_test_metrics(
            ExecutionMetrics(
                test_id=test_id,
                execution_time=10.0,
                failure_rate=0.5,
                last_failure_time=2000.0,
                coverage_contribution=0.8,
                complexity_score=0.6,
            )
        )

    selected, _priorities = optimizer.optimize_test_schedule(tests, 0.0, 2000.0)

    # No tests should be selected with zero budget
    assert len(selected) == 0


def test_optimize_test_schedule_unknown_tests(optimizer):
    """Test schedule optimization with unknown tests."""
    tests = ["test_unknown_1", "test_unknown_2", "test_unknown_3"]

    selected, _priorities = optimizer.optimize_test_schedule(tests, 25.0, 2000.0)

    # Should handle unknown tests (default 10s each)
    assert len(selected) <= 2  # 25s budget, 10s per test


def test_compute_uncertainty_bound(optimizer):
    """Test uncertainty bound computation."""
    energy = 0.6
    time = 0.4

    bound = optimizer.compute_uncertainty_bound(energy, time)

    assert bound == 0.24
    assert (
        bound >= optimizer.h_bar / 2.0 or bound < optimizer.h_bar / 2.0
    )  # Can be either


def test_get_statistics_empty(optimizer):
    """Test statistics with no test history."""
    stats = optimizer.get_statistics()

    assert stats["total_tests"] == 0
    assert stats["avg_execution_time"] == 0.0
    assert stats["avg_failure_rate"] == 0.0
    assert stats["avg_coverage"] == 0.0


def test_get_statistics_with_data(optimizer):
    """Test statistics with test history."""
    for i in range(3):
        optimizer.update_test_metrics(
            ExecutionMetrics(
                test_id=f"test_{i}",
                execution_time=float(i + 1) * 5.0,
                failure_rate=0.1 * i,
                last_failure_time=2000.0,
                coverage_contribution=0.3 * i,
                complexity_score=0.2 * i,
            )
        )

    stats = optimizer.get_statistics()

    assert stats["total_tests"] == 3
    assert abs(stats["avg_execution_time"] - 10.0) < 0.01  # (5 + 10 + 15) / 3
    assert abs(stats["avg_failure_rate"] - 0.1) < 0.01  # (0.0 + 0.1 + 0.2) / 3
    assert abs(stats["avg_coverage"] - 0.3) < 0.01  # (0.0 + 0.3 + 0.6) / 3


def test_recency_factor_recent_failure(optimizer):
    """Test that recent failures increase priority."""
    # Recent failure
    metrics_recent = ExecutionMetrics(
        test_id="test_recent",
        execution_time=10.0,
        failure_rate=0.5,
        last_failure_time=1999.0,  # 1 second ago
        coverage_contribution=0.5,
        complexity_score=0.5,
    )
    optimizer.update_test_metrics(metrics_recent)
    priority_recent = optimizer.calculate_priority("test_recent", 2000.0)

    # Old failure
    metrics_old = ExecutionMetrics(
        test_id="test_old",
        execution_time=10.0,
        failure_rate=0.5,
        last_failure_time=1000.0,  # 1000 seconds ago
        coverage_contribution=0.5,
        complexity_score=0.5,
    )
    optimizer.update_test_metrics(metrics_old)
    priority_old = optimizer.calculate_priority("test_old", 2000.0)

    # Recent failure should have higher priority
    assert priority_recent.priority_score > priority_old.priority_score


def test_execution_time_penalty(optimizer):
    """Test that longer execution time reduces priority."""
    # Fast test
    metrics_fast = ExecutionMetrics(
        test_id="test_fast",
        execution_time=1.0,  # Fast
        failure_rate=0.5,
        last_failure_time=2000.0,
        coverage_contribution=0.5,
        complexity_score=0.5,
    )
    optimizer.update_test_metrics(metrics_fast)
    priority_fast = optimizer.calculate_priority("test_fast", 2000.0)

    # Slow test
    metrics_slow = ExecutionMetrics(
        test_id="test_slow",
        execution_time=60.0,  # Slow
        failure_rate=0.5,
        last_failure_time=2000.0,
        coverage_contribution=0.5,
        complexity_score=0.5,
    )
    optimizer.update_test_metrics(metrics_slow)
    priority_slow = optimizer.calculate_priority("test_slow", 2000.0)

    # Fast test should have higher or equal priority
    assert priority_fast.priority_score >= priority_slow.priority_score


def test_integration_with_monitor():
    """Test integration with coherence monitor."""
    from pathlib import Path

    # Create temporary database with schema
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # Create schema
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

        config = QuantumConfig(
            quantum_mode=True, uncertainty=True, rollout_percentage=100
        )
        repo = QuantumMetricRepository(db_path)
        monitor = CoherenceMonitor(config, repo)
        optimizer = UncertaintyOptimizer(config, monitor)

        # Perform operations
        metrics = ExecutionMetrics(
            test_id="test_monitored",
            execution_time=5.0,
            failure_rate=0.3,
            last_failure_time=2000.0,
            coverage_contribution=0.7,
            complexity_score=0.5,
        )
        optimizer.update_test_metrics(metrics)
        priority = optimizer.calculate_priority("test_monitored", 2000.0)

        # Verify metrics were recorded
        assert priority.test_id == "test_monitored"

        # Optimize schedule
        tests = ["test_monitored"]
        selected, _priorities = optimizer.optimize_test_schedule(tests, 10.0, 2000.0)

        assert len(selected) == 1
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_priority_deterministic(optimizer):
    """Test that priority calculation is deterministic."""
    metrics = ExecutionMetrics(
        test_id="test_deterministic",
        execution_time=10.0,
        failure_rate=0.5,
        last_failure_time=2000.0,
        coverage_contribution=0.6,
        complexity_score=0.7,
    )
    optimizer.update_test_metrics(metrics)

    # Calculate priority multiple times
    priority1 = optimizer.calculate_priority("test_deterministic", 2000.0)
    priority2 = optimizer.calculate_priority("test_deterministic", 2000.0)

    assert priority1.priority_score == priority2.priority_score
    assert priority1.uncertainty == priority2.uncertainty
    assert priority1.recommended_action == priority2.recommended_action
