"""
Tests for SuperpositionEngine and related classes.

Tests parallel decision evaluation, wave function collapse, coherence
monitoring, and performance characteristics.
"""

import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.superposition import (
    Decision,
    SuperpositionEngine,
    SuperpositionState,
    quantum_superposition,
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
    """Create quantum config."""
    return QuantumConfig(quantum_mode=True, superposition=True)


@pytest.fixture
def repo(temp_db):
    """Create repository."""
    return QuantumMetricRepository(db_path=temp_db)


@pytest.fixture
def monitor(config, repo):
    """Create coherence monitor."""
    return CoherenceMonitor(config=config, repository=repo)


@pytest.fixture
def engine(config, monitor):
    """Create superposition engine."""
    return SuperpositionEngine(config=config, monitor=monitor)


class TestDecision:
    """Test Decision dataclass."""

    def test_create_decision(self):
        """Test creating a decision."""
        decision = Decision(id="D1", name="Approve", evaluation_fn=lambda: 0.9)

        assert decision.id == "D1", "id is not valid"
        assert decision.name == "Approve", "name is not valid"

    def test_evaluate_decision(self):
        """Test evaluating a decision."""
        decision = Decision(id="D1", name="Test", evaluation_fn=lambda: 0.75)

        score = decision.evaluate()
        assert score == 0.75, "score is not valid"


class TestSuperpositionState:
    """Test SuperpositionState class."""

    def test_create_state(self):
        """Test creating superposition state."""
        decisions = [
            Decision("D1", "Option 1", lambda: 0.8),
            Decision("D2", "Option 2", lambda: 0.9),
            Decision("D3", "Option 3", lambda: 0.7),
        ]

        state = SuperpositionState(decisions=decisions)

        assert len(state.decisions) == 3, "Collection must not be empty"
        assert len(state.amplitudes) == 3, "Collection must not be empty"
        assert state.coherence == 1.0, "coherence is not valid"
        assert not state.evaluated, "Condition must be true"

    def test_equal_amplitudes(self):
        """Test that initial amplitudes are equal."""
        decisions = [
            Decision("D1", "A", lambda: 1.0),
            Decision("D2", "B", lambda: 1.0),
        ]

        state = SuperpositionState(decisions=decisions)

        # All amplitudes should be 1/√2 ≈ 0.707
        expected = 1.0 / (2**0.5)
        for amp in state.amplitudes:
            assert abs(amp - expected) < 0.001, "Condition must be true"

    def test_empty_decisions_raises_error(self):
        """Test that empty decisions list raises error."""
        with pytest.raises(ValueError, match="Cannot create superposition with zero decisions"):
            SuperpositionState(decisions=[])

    def test_get_decision_by_id(self):
        """Test retrieving decision by ID."""
        decisions = [
            Decision("D1", "A", lambda: 1.0),
            Decision("D2", "B", lambda: 1.0),
        ]

        state = SuperpositionState(decisions=decisions)

        decision = state.get_decision_by_id("D2")
        assert decision is not None, "decision must be initialized"
        assert decision.name == "B", "name is not valid"

    def test_to_dict(self):
        """Test converting state to dictionary."""
        decisions = [
            Decision("D1", "A", lambda: 1.0),
            Decision("D2", "B", lambda: 1.0),
        ]

        state = SuperpositionState(decisions=decisions)
        data = state.to_dict()

        assert data["num_decisions"] == 2, "Data must not be empty"
        assert "amplitudes" in data, "Data must not be empty"
        assert "coherence" in data, "Data must not be empty"


class TestSuperpositionEngine:
    """Test SuperpositionEngine class."""

    def test_create_superposition(self, engine):
        """Test creating superposition."""
        decisions = [
            Decision("D1", "Approve", lambda: 0.9),
            Decision("D2", "Reject", lambda: 0.3),
        ]

        state = engine.create_superposition(decisions)

        assert len(state.decisions) == 2, "Collection must not be empty"
        assert state.coherence == 1.0, "coherence is not valid"

    def test_create_empty_superposition_raises_error(self, engine):
        """Test that empty decisions raises error."""
        with pytest.raises(ValueError, match="Cannot create superposition with empty decisions"):
            engine.create_superposition([])

    def test_evaluate_parallel(self, engine):
        """Test parallel evaluation."""
        decisions = [
            Decision("D1", "High", lambda: 0.9),
            Decision("D2", "Medium", lambda: 0.5),
            Decision("D3", "Low", lambda: 0.1),
        ]

        state = engine.create_superposition(decisions)
        probabilities = engine.evaluate_parallel(state)

        assert len(probabilities) == 3, "Probabilities must not be empty"
        assert abs(sum(probabilities) - 1.0) < 0.001, "Condition must be true"
        assert state.evaluated, "Condition must be true"

    def test_evaluate_orders_by_score(self, engine):
        """Test that higher scores get higher probabilities."""
        decisions = [
            Decision("D1", "Best", lambda: 1.0),
            Decision("D2", "Worst", lambda: 0.1),
        ]

        state = engine.create_superposition(decisions)
        probabilities = engine.evaluate_parallel(state)

        # D1 should have much higher probability than D2
        assert probabilities[0] > probabilities[1], "Value must be greater than zero"

    def test_collapse(self, engine):
        """Test wave function collapse."""
        decisions = [
            Decision("D1", "Best", lambda: 0.95),
            Decision("D2", "Medium", lambda: 0.50),
            Decision("D3", "Worst", lambda: 0.10),
        ]

        state = engine.create_superposition(decisions)
        best_decision = engine.collapse(state)

        # Should select the highest-scoring decision
        assert best_decision.id == "D1", "id is not valid"
        assert best_decision.name == "Best", "name is not valid"

    def test_collapse_auto_evaluates(self, engine):
        """Test that collapse auto-evaluates if needed."""
        decisions = [
            Decision("D1", "A", lambda: 0.8),
            Decision("D2", "B", lambda: 0.6),
        ]

        state = engine.create_superposition(decisions)
        assert not state.evaluated, "Condition must be true"

        engine.collapse(state)
        assert state.evaluated, "Condition must be true"

    def test_get_coherence(self, engine):
        """Test getting coherence value."""
        decisions = [
            Decision("D1", "A", lambda: 0.9),
            Decision("D2", "B", lambda: 0.8),
        ]

        state = engine.create_superposition(decisions)
        coherence = engine.get_coherence(state)

        assert 0.0 <= coherence <= 1.0, "0 is not valid"


class TestParallelPerformance:
    """Test parallel execution performance."""

    def test_parallel_faster_than_sequential(self, engine):
        """Test that parallel evaluation is faster."""

        # Create decisions with artificial delay
        def slow_eval():
            time.sleep(0.05)  # 50ms delay
            return 1.0

        decisions = [Decision(f"D{i}", f"Option {i}", slow_eval) for i in range(4)]

        state = engine.create_superposition(decisions)

        start = time.time()
        engine.evaluate_parallel(state)
        parallel_time = time.time() - start

        # With 4 parallel tasks of 50ms, should take ~50ms, not 200ms
        # Allow some overhead, but should be < 150ms
        assert parallel_time < 0.15, "parallel_time is not valid"

    def test_performance_metrics(self, engine):
        """Test getting performance metrics."""
        decisions = [
            Decision("D1", "A", lambda: 0.9),
            Decision("D2", "B", lambda: 0.8),
        ]

        state = engine.create_superposition(decisions)
        engine.evaluate_parallel(state)

        metrics = engine.get_performance_metrics()

        assert "avg_time" in metrics, "Condition must be true"
        assert "total_evaluations" in metrics, "Condition must be true"
        assert metrics["total_evaluations"] == 1, "Condition must be true"


class TestCoherenceCalculation:
    """Test coherence calculation logic."""

    def test_peaked_distribution_high_coherence(self, engine):
        """Test that peaked distribution has high coherence."""
        decisions = [
            Decision("D1", "Best", lambda: 0.99),
            Decision("D2", "Bad", lambda: 0.01),
        ]

        state = engine.create_superposition(decisions)
        engine.evaluate_parallel(state)

        # Peaked distribution should have high coherence
        assert state.coherence > 0.5, "coherence must be greater than zero"

    def test_uniform_distribution_low_coherence(self, engine):
        """Test that uniform distribution has low coherence."""
        decisions = [
            Decision("D1", "A", lambda: 0.5),
            Decision("D2", "B", lambda: 0.5),
        ]

        state = engine.create_superposition(decisions)
        engine.evaluate_parallel(state)

        # Uniform distribution should have lower coherence
        assert state.coherence < 0.5, "coherence is not valid"


class TestErrorHandling:
    """Test error handling in evaluation."""

    def test_evaluation_error_fallback(self, engine):
        """Test that evaluation errors don't crash."""

        def failing_eval():
            raise RuntimeError("Evaluation failed")

        decisions = [
            Decision("D1", "Good", lambda: 0.9),
            Decision("D2", "Failing", failing_eval),
        ]

        state = engine.create_superposition(decisions)

        # Should not raise, should fall back to 0 score
        probabilities = engine.evaluate_parallel(state)

        # D1 should get all probability
        assert probabilities[0] > 0.9, "Value must be greater than zero"

    def test_all_zero_scores(self, engine):
        """Test handling of all zero scores."""
        decisions = [
            Decision("D1", "A", lambda: 0.0),
            Decision("D2", "B", lambda: 0.0),
        ]

        state = engine.create_superposition(decisions)
        probabilities = engine.evaluate_parallel(state)

        # Should give equal probabilities
        assert abs(probabilities[0] - 0.5) < 0.001, "Condition must be true"
        assert abs(probabilities[1] - 0.5) < 0.001, "Condition must be true"


class TestDecorator:
    """Test quantum_superposition decorator."""

    def test_decorator_wraps_function(self):
        """Test that decorator wraps function properly."""

        @quantum_superposition()
        def make_decision(options):
            return max(options, key=lambda x: x)

        result = make_decision([1, 5, 3])
        assert result == 5, "Result must not be empty"


class TestIntegration:
    """Integration tests for full superposition workflow."""

    def test_full_workflow(self, engine):
        """Test complete superposition workflow."""
        # 1. Create decisions
        decisions = [
            Decision("D1", "Approve", lambda: 0.90),
            Decision("D2", "Review", lambda: 0.70),
            Decision("D3", "Reject", lambda: 0.30),
        ]

        # 2. Create superposition
        state = engine.create_superposition(decisions)
        assert len(state.decisions) == 3, "Collection must not be empty"

        # 3. Evaluate in parallel
        probabilities = engine.evaluate_parallel(state)
        assert sum(probabilities) == pytest.approx(1.0), "Condition must be true"

        # 4. Collapse to best decision
        best = engine.collapse(state)
        assert best.id == "D1", "id is not valid"

        # 5. Check coherence
        coherence = engine.get_coherence(state)
        assert 0.0 <= coherence <= 1.0, "0 is not valid"
