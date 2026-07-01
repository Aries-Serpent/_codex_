"""
Tests for OutcomeAnalyzer.

Comprehensive test suite for adaptive learning outcome analysis,
pattern detection, and reward calculation.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Test coverage for learning components
"""

import pytest

pytest.importorskip("numpy")

from cognitive_brain.learning.outcome_analyzer import OutcomeAnalyzer
from cognitive_brain.models.learning_outcome import (
    DecisionContext,
    LearningOutcome,
    OutcomeType,
    PatternCategory,
)


@pytest.fixture
def analyzer():
    """Create fresh OutcomeAnalyzer for each test."""
    return OutcomeAnalyzer()


@pytest.fixture
def simple_context():
    """Create simple decision context."""
    return DecisionContext(
        task_type="code_review",
        complexity=0.5,
        resource_constraints={"cpu": 0.7, "memory": 0.6},
        time_pressure=0.3,
        agent_ids=["agent_1"],
    )


@pytest.fixture
def complex_context():
    """Create complex decision context."""
    return DecisionContext(
        task_type="architecture_design",
        complexity=0.9,
        resource_constraints={"cpu": 0.4, "memory": 0.9},
        time_pressure=0.8,
        agent_ids=["agent_1", "agent_2", "agent_3"],
    )


def test_analyze_success_outcome(analyzer, simple_context):
    """Test 1: Analyze successful outcome with positive reward."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_001",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.95, "accuracy": 0.98},
        context=simple_context,
    )

    assert isinstance(outcome, LearningOutcome)
    assert outcome.outcome_type == OutcomeType.SUCCESS, "outcome_type is not valid"
    assert 0.0 < outcome.reward <= 1.0, "0 is not valid"
    assert len(outcome.patterns_identified) > 0, "Collection must not be empty"
    assert len(outcome.lessons_learned) > 0, "Collection must not be empty"
    assert "Strategy effective" in outcome.lessons_learned[0], "Condition must be true"


def test_analyze_failure_outcome(analyzer, simple_context):
    """Test 2: Analyze failed outcome with negative reward."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_002",
        outcome_type=OutcomeType.FAILURE,
        result_metrics={"efficiency": 0.3, "accuracy": 0.2},
        context=simple_context,
    )

    assert outcome.outcome_type == OutcomeType.FAILURE, "outcome_type is not valid"
    assert -1.0 <= outcome.reward < 0.0, "0 is not valid"
    assert "Strategy ineffective" in outcome.lessons_learned[0], "Condition must be true"


def test_reward_calculation_formula(analyzer, simple_context):
    """Test 3: Validate reward calculation formula correctness."""
    # Test with known inputs
    context = DecisionContext(
        task_type="test_task",
        complexity=0.5,
        resource_constraints={"cpu": 1.0},
        time_pressure=0.0,  # No time pressure
        agent_ids=["agent_1"],
    )

    # Success with 100% efficiency, no time pressure
    # Expected: 1.0 * 1.0 * (1 - 0) + 0.05 = 1.05, clamped to 1.0
    outcome = analyzer.analyze_outcome(
        decision_id="decision_003",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 1.0},
        context=context,
    )

    assert outcome.reward == pytest.approx(1.0, abs=0.01)
    assert -1.0 <= outcome.reward <= 1.0, "0 is not valid"


def test_pattern_identification(analyzer, complex_context):
    """Test 4: Validate pattern detection works correctly."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_004",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.92},
        context=complex_context,
    )

    # With 3 agents and success, should detect multi-agent pattern
    patterns = outcome.patterns_identified
    assert len(patterns) > 0, "Patterns must not be empty"

    # Check for specific pattern types
    pattern_str = " ".join(patterns)
    assert any(cat in pattern_str for cat in ["temporal", "contextual", "sequential", "causal"])


def test_lessons_extraction(analyzer, complex_context):
    """Test 5: Validate lessons are actionable and comprehensive."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_005",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.85},
        context=complex_context,
    )

    lessons = outcome.lessons_learned
    assert len(lessons) >= 1, "Lessons must not be empty"

    # Should mention task type
    assert any("architecture_design" in lesson for lesson in lessons), "Condition must be true"

    # High complexity success should be noted
    # Fixed malformed assertion: assert any(...)
    assert any("resource" in p.lower() or "memory" in p.lower() for p in patterns), "Condition must be true"


def test_error_outcome_handling(analyzer, simple_context):
    """Test 14: Test error outcome handling."""
    error_outcome = analyzer.analyze_outcome(
        decision_id="error_001",
        outcome_type=OutcomeType.ERROR,
        result_metrics={"efficiency": 0.0, "error_code": 500},
        context=simple_context,
    )

    assert error_outcome.outcome_type == OutcomeType.ERROR, "Error should be raised or set"
    assert error_outcome.reward < 0.0, "Error should be raised or set"
    assert error_outcome.reward >= -1.0, "reward must be greater than zero"


def test_get_patterns_by_category(analyzer, simple_context):
    """Test 15: Test pattern filtering by category."""
    # Create diverse outcomes
    contexts = [
        DecisionContext("task_1", 0.9, {"cpu": 0.8}, 0.3, ["agent_1"]),  # High complexity
        DecisionContext("task_2", 0.5, {"cpu": 0.3}, 0.3, ["a1", "a2", "a3"]),  # Multi-agent
        DecisionContext("task_3", 0.5, {"cpu": 0.8}, 0.3, ["agent_1"]),  # Regular
    ]

    for i, ctx in enumerate(contexts):
        analyzer.analyze_outcome(
            decision_id=f"filter_{i:03d}",
            outcome_type=OutcomeType.SUCCESS,
            result_metrics={"efficiency": 0.85},
            context=ctx,
        )

    pattern_set = analyzer.identify_patterns(lookback_window=10)

    # Test category filtering
    contextual = pattern_set.get_by_category(PatternCategory.CONTEXTUAL)
    sequential = pattern_set.get_by_category(PatternCategory.SEQUENTIAL)

    # Should be able to filter by category
    for pattern in contextual:
        assert pattern.category == PatternCategory.CONTEXTUAL, "category is not valid"
    for pattern in sequential:
        assert pattern.category == PatternCategory.SEQUENTIAL, "category is not valid"
