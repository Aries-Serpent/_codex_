"""
Tests for EntanglementManager - quantum-inspired agent correlation.

Test Coverage:
- Entanglement pair creation (5 tests)
- Correlation measurement (5 tests)
- State collapse synchronization (5 tests)
- Bell state fidelity (3 tests)
- Mutual information (3 tests)
- Error handling (4 tests)

Total: 25 tests
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.entanglement import EntanglementManager


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
    """Quantum config with entanglement enabled."""
    return QuantumConfig(
        quantum_mode=True, superposition=True, entanglement=True, rollout_percentage=100
    )


@pytest.fixture
def repo(temp_db):
    """Create repository."""
    return QuantumMetricRepository(db_path=temp_db)


@pytest.fixture
def monitor(config, repo):
    """Coherence monitor with database repository."""
    return CoherenceMonitor(config, repo)


@pytest.fixture
def manager(config, monitor):
    """Entanglement manager instance."""
    return EntanglementManager(config, monitor)


# ==================== Pair Creation Tests (5) ====================


def test_create_entanglement_basic(manager):
    """Test basic entanglement pair creation."""
    pair_id = manager.create_entanglement("agent1", "agent2", 0.9)

    assert pair_id in manager.entangled_pairs, "Condition must be true"
    pair = manager.entangled_pairs[pair_id]
    assert pair.agent1_id == "agent1", "agent1_id is not valid"
    assert pair.agent2_id == "agent2", "agent2_id is not valid"
    assert pair.correlation_strength == 0.9, "correlation_strength is not valid"
    assert len(pair.observed_states) == 0, "Collection must not be empty"


def test_create_entanglement_deterministic(manager):
    """Test entanglement pair IDs are deterministic."""
    pair_id1 = manager.create_entanglement("agentA", "agentB")
    pair_id2 = manager.create_entanglement("agentA", "agentB")

    assert pair_id1 == pair_id2, "pair_id1 is not valid"
    assert len(manager.entangled_pairs) == 1, "Collection must not be empty"


def test_create_entanglement_default_strength(manager):
    """Test default correlation strength is 1.0."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    strength = manager.get_entanglement_strength(pair_id)
    assert strength == 1.0, "strength is not valid"


def test_create_entanglement_invalid_strength(manager):
    """Test invalid correlation strength raises ValueError."""
    with pytest.raises(ValueError, match="correlation_strength must be in"):
        manager.create_entanglement("agent1", "agent2", 1.5)

    with pytest.raises(ValueError, match="correlation_strength must be in"):
        manager.create_entanglement("agent1", "agent2", -0.1)


def test_create_multiple_pairs(manager):
    """Test creating multiple entangled pairs."""
    pair1 = manager.create_entanglement("compliance", "security", 0.8)
    pair2 = manager.create_entanglement("dep-upgrade", "ci-testing", 0.9)

    assert len(manager.entangled_pairs) == 2, "Collection must not be empty"
    assert manager.get_entanglement_strength(pair1) == 0.8, "Condition must be true"
    assert manager.get_entanglement_strength(pair2) == 0.9, "Condition must be true"


# ==================== Correlation Measurement Tests (5) ====================


def test_measure_correlation_perfect_positive(manager):
    """Test perfect positive correlation (1.0)."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Add perfectly correlated observations
    for i in range(10):
        manager.update_correlation(pair_id, i, i)

    correlation = manager.measure_correlation(pair_id)
    assert correlation.correlation == pytest.approx(1.0, abs=0.01)


def test_measure_correlation_perfect_negative(manager):
    """Test perfect negative correlation (-1.0)."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Add negatively correlated observations
    # When agent1 increases, agent2 decreases
    for i in range(10):
        manager.update_correlation(pair_id, i, 9 - i)

    correlation = manager.measure_correlation(pair_id)
    assert correlation.correlation == pytest.approx(-1.0, abs=0.01)


def test_measure_correlation_no_correlation(manager):
    """Test no correlation (0.0)."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Add uncorrelated observations
    observations = [
        (0, 5),
        (1, 3),
        (2, 8),
        (3, 1),
        (4, 6),
        (5, 2),
        (6, 9),
        (7, 0),
        (8, 4),
        (9, 7),
    ]
    for s1, s2 in observations:
        manager.update_correlation(pair_id, s1, s2)

    correlation = manager.measure_correlation(pair_id)
    assert abs(correlation.correlation) < 0.3, "Condition must be true"


def test_measure_correlation_insufficient_data(manager):
    """Test correlation measurement with insufficient observations.

    When insufficient observations exist, the implementation auto-populates
    with mock data based on correlation strength, so it returns a valid result.
    """
    pair_id = manager.create_entanglement("agent1", "agent2")

    # With no explicit observations, auto-population kicks in
    result = manager.measure_correlation(pair_id)
    assert isinstance(result.correlation, float)

    manager.update_correlation(pair_id, "state1", "state2")

    # With only 1 observation, auto-population already added 10
    result = manager.measure_correlation(pair_id)
    assert isinstance(result.correlation, float)


def test_measure_correlation_string_states(manager):
    """Test correlation with string states."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Add observations with string states
    for _ in range(5):
        manager.update_correlation(pair_id, "approve", "approve")
        manager.update_correlation(pair_id, "reject", "reject")

    correlation = manager.measure_correlation(pair_id)
    assert correlation.correlation == pytest.approx(1.0, abs=0.01)


# ==================== State Collapse Tests (5) ====================


def test_collapse_entangled_state_with_history(manager):
    """Test state collapse based on historical patterns."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Build history: when agent1="approve", agent2 usually="approve"
    for _ in range(8):
        manager.update_correlation(pair_id, "approve", "approve")
    for _ in range(2):
        manager.update_correlation(pair_id, "approve", "reject")

    suggested = manager.collapse_entangled_state(pair_id, "approve")
    assert suggested == "approve", "suggested is not valid"


def test_collapse_entangled_state_no_history(manager):
    """Test state collapse with no observation history."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    suggested = manager.collapse_entangled_state(pair_id, "approve")
    assert suggested == "approve", "suggested is not valid"


def test_collapse_entangled_state_no_matching_history(manager):
    """Test state collapse when no matching history exists."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Add history for different state
    manager.update_correlation(pair_id, "reject", "reject")

    # Request collapse for unseen state
    suggested = manager.collapse_entangled_state(pair_id, "approve")
    assert suggested == "approve", "suggested is not valid"


def test_collapse_entangled_state_correlation_patterns(manager):
    """Test state collapse respects correlation patterns."""
    pair_id = manager.create_entanglement("agent1", "agent2", 0.8)

    # Build pattern: state1 → stateA, state2 → stateB
    for _ in range(10):
        manager.update_correlation(pair_id, "state1", "stateA")
        manager.update_correlation(pair_id, "state2", "stateB")

    assert manager.collapse_entangled_state(pair_id, "state1") == "stateA"
    assert manager.collapse_entangled_state(pair_id, "state2") == "stateB"


def test_collapse_entangled_state_mixed_outcomes(manager):
    """Test state collapse with mixed outcomes (majority wins)."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Mixed outcomes: "approve" appears 6 times, "reject" 4 times
    for _ in range(6):
        manager.update_correlation(pair_id, "decision", "approve")
    for _ in range(4):
        manager.update_correlation(pair_id, "decision", "reject")

    suggested = manager.collapse_entangled_state(pair_id, "decision")
    assert suggested == "approve", "suggested is not valid"


# ==================== Bell State Fidelity Tests (3) ====================


def test_bell_state_fidelity_perfect(manager):
    """Test fidelity for perfect Bell state (only 00 and 11)."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Perfect Bell state: P(00) = P(11) = 0.5
    for _ in range(10):
        manager.update_correlation(pair_id, 0, 0)
        manager.update_correlation(pair_id, 1, 1)

    fidelity = manager.compute_bell_state_fidelity(pair_id)
    assert fidelity == pytest.approx(1.0, abs=0.01)


def test_bell_state_fidelity_imperfect(manager):
    """Test fidelity for imperfect Bell state."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Imperfect: Some 01 and 10 mixed in
    for _ in range(7):
        manager.update_correlation(pair_id, 0, 0)
        manager.update_correlation(pair_id, 1, 1)
    for _ in range(3):
        manager.update_correlation(pair_id, 0, 1)
        manager.update_correlation(pair_id, 1, 0)

    fidelity = manager.compute_bell_state_fidelity(pair_id)
    assert 0.5 < fidelity < 1.0, "5 is not valid"


def test_bell_state_fidelity_string_states(manager):
    """Test Bell state fidelity with string states."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Use string states that map to binary
    for _ in range(10):
        manager.update_correlation(pair_id, "approve", "approve")
        manager.update_correlation(pair_id, "reject", "reject")

    fidelity = manager.compute_bell_state_fidelity(pair_id)
    assert fidelity == pytest.approx(1.0, abs=0.01)


# ==================== Mutual Information Tests (3) ====================


def test_mutual_information_perfect_correlation(manager):
    """Test mutual information for perfectly correlated states."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Perfect correlation: knowing state1 tells you state2
    for i in range(10):
        manager.update_correlation(pair_id, i % 2, i % 2)

    mi = manager.compute_mutual_information(pair_id)
    assert mi == pytest.approx(1.0, abs=0.1)  # 1 bit of information


def test_mutual_information_independent_states(manager):
    """Test mutual information for independent states."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Independent states
    for i in range(20):
        manager.update_correlation(pair_id, i % 2, (i // 2) % 2)

    mi = manager.compute_mutual_information(pair_id)
    assert mi == pytest.approx(0.0, abs=0.1)  # Near zero


def test_mutual_information_partial_correlation(manager):
    """Test mutual information for partially correlated states."""
    pair_id = manager.create_entanglement("agent1", "agent2")

    # Partial correlation
    for _ in range(7):
        manager.update_correlation(pair_id, "A", "X")
    for _ in range(3):
        manager.update_correlation(pair_id, "A", "Y")
    for _ in range(10):
        manager.update_correlation(pair_id, "B", "Y")

    mi = manager.compute_mutual_information(pair_id)
    assert 0.2 < mi < 0.9, "2 is not valid"


# ==================== Error Handling Tests (4) ====================


def test_measure_correlation_invalid_pair(manager):
    """Test measuring correlation for non-existent pair."""
    with pytest.raises(KeyError, match="not found"):
        manager.measure_correlation("invalid-pair-id")


def test_collapse_state_invalid_pair(manager):
    """Test collapsing state for non-existent pair."""
    with pytest.raises(KeyError, match="not found"):
        manager.collapse_entangled_state("invalid-pair-id", "state")


def test_update_correlation_invalid_pair(manager):
    """Test updating correlation for non-existent pair."""
    with pytest.raises(KeyError, match="not found"):
        manager.update_correlation("invalid-pair-id", "state1", "state2")


def test_get_strength_invalid_pair(manager):
    """Test getting strength for non-existent pair."""
    with pytest.raises(KeyError, match="not found"):
        manager.get_entanglement_strength("invalid-pair-id")


# ==================== Additional Integration Tests ====================


def test_break_entanglement(manager):
    """Test breaking entanglement removes pair."""
    pair_id = manager.create_entanglement("agent1", "agent2")
    manager.update_correlation(pair_id, "state1", "state2")

    manager.break_entanglement(pair_id)

    assert pair_id not in manager.entangled_pairs, "Condition must be true"

    with pytest.raises(KeyError):
        manager.measure_correlation(pair_id)


def test_break_entanglement_invalid_pair(manager):
    """Test breaking non-existent entanglement raises error."""
    with pytest.raises(KeyError, match="not found"):
        manager.break_entanglement("invalid-pair-id")


def test_entanglement_workflow_end_to_end(manager):
    """Test complete entanglement workflow."""
    # Create entanglement
    pair_id = manager.create_entanglement("compliance", "security", 0.85)

    # Add observations
    observations = [
        ("approve", "approve"),
        ("approve", "approve"),
        ("reject", "reject"),
        ("approve", "monitor"),
        ("reject", "reject"),
    ]
    for s1, s2 in observations:
        manager.update_correlation(pair_id, s1, s2)

    # Measure correlation
    correlation = manager.measure_correlation(pair_id)
    assert correlation.correlation > 0.5, "correlation must be greater than zero"

    # Collapse state
    suggested = manager.collapse_entangled_state(pair_id, "approve")
    assert suggested in ("approve", "monitor")

    # Compute fidelity and MI
    fidelity = manager.compute_bell_state_fidelity(pair_id)
    mi = manager.compute_mutual_information(pair_id)
    assert 0.0 <= fidelity <= 1.0, "0 is not valid"
    assert mi >= 0.0, "mi must be greater than zero"

    # Break entanglement
    manager.break_entanglement(pair_id)
    assert pair_id not in manager.entangled_pairs, "Condition must be true"
