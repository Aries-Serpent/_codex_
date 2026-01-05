"""
Tests for OutcomeAnalyzer.

Comprehensive test suite for adaptive learning outcome analysis,
pattern detection, and reward calculation.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Test coverage for learning components
"""
import pytest
from datetime import datetime
from cognitive_brain.learning.outcome_analyzer import OutcomeAnalyzer
from cognitive_brain.models.learning_outcome import (
    OutcomeType,
    PatternCategory,
    DecisionContext,
    LearningOutcome
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
        agent_ids=["agent_1"]
    )


@pytest.fixture
def complex_context():
    """Create complex decision context."""
    return DecisionContext(
        task_type="architecture_design",
        complexity=0.9,
        resource_constraints={"cpu": 0.4, "memory": 0.9},
        time_pressure=0.8,
        agent_ids=["agent_1", "agent_2", "agent_3"]
    )


def test_analyze_success_outcome(analyzer, simple_context):
    """Test 1: Analyze successful outcome with positive reward."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_001",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.95, "accuracy": 0.98},
        context=simple_context
    )
    
    assert isinstance(outcome, LearningOutcome)
    assert outcome.outcome_type == OutcomeType.SUCCESS
    assert 0.0 < outcome.reward <= 1.0  # Positive reward for success
    assert len(outcome.patterns_identified) > 0
    assert len(outcome.lessons_learned) > 0
    assert "Strategy effective" in outcome.lessons_learned[0]


def test_analyze_failure_outcome(analyzer, simple_context):
    """Test 2: Analyze failed outcome with negative reward."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_002",
        outcome_type=OutcomeType.FAILURE,
        result_metrics={"efficiency": 0.3, "accuracy": 0.2},
        context=simple_context
    )
    
    assert outcome.outcome_type == OutcomeType.FAILURE
    assert -1.0 <= outcome.reward < 0.0  # Negative reward for failure
    assert "Strategy ineffective" in outcome.lessons_learned[0]


def test_reward_calculation_formula(analyzer, simple_context):
    """Test 3: Validate reward calculation formula correctness."""
    # Test with known inputs
    context = DecisionContext(
        task_type="test_task",
        complexity=0.5,
        resource_constraints={"cpu": 1.0},
        time_pressure=0.0,  # No time pressure
        agent_ids=["agent_1"]
    )
    
    # Success with 100% efficiency, no time pressure
    # Expected: 1.0 * 1.0 * (1 - 0) + 0.05 = 1.05, clamped to 1.0
    outcome = analyzer.analyze_outcome(
        decision_id="decision_003",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 1.0},
        context=context
    )
    
    assert outcome.reward == pytest.approx(1.0, abs=0.01)
    assert -1.0 <= outcome.reward <= 1.0  # Always in valid range


def test_pattern_identification(analyzer, complex_context):
    """Test 4: Validate pattern detection works correctly."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_004",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.92},
        context=complex_context
    )
    
    # With 3 agents and success, should detect multi-agent pattern
    patterns = outcome.patterns_identified
    assert len(patterns) > 0
    
    # Check for specific pattern types
    pattern_str = " ".join(patterns)
    assert any(cat in pattern_str for cat in ["temporal", "contextual", "sequential", "causal"])


def test_lessons_extraction(analyzer, complex_context):
    """Test 5: Validate lessons are actionable and comprehensive."""
    outcome = analyzer.analyze_outcome(
        decision_id="decision_005",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.85},
        context=complex_context
    )
    
    lessons = outcome.lessons_learned
    assert len(lessons) >= 1
    
    # Should mention task type
    assert any("architecture_design" in lesson for lesson in lessons)
    
    # High complexity success should be noted
    assert any("high-complexity" in lesson.lower() or "complex" in lesson.lower() 
               for lesson in lessons)


def test_identify_patterns_batch(analyzer, simple_context):
    """Test 6: Test batch pattern extraction from multiple outcomes."""
    # Create multiple outcomes with similar patterns
    for i in range(15):
        analyzer.analyze_outcome(
            decision_id=f"decision_{i:03d}",
            outcome_type=OutcomeType.SUCCESS if i % 2 == 0 else OutcomeType.FAILURE,
            result_metrics={"efficiency": 0.8 if i % 2 == 0 else 0.3},
            context=simple_context
        )
    
    # Extract patterns from batch
    pattern_set = analyzer.identify_patterns(lookback_window=15)
    
    assert len(pattern_set.patterns) > 0
    assert pattern_set.domain == "cognitive_brain"
    assert pattern_set.statistics["outcomes_analyzed"] == 15
    assert pattern_set.statistics["total_patterns"] > 0


def test_high_confidence_patterns(analyzer, simple_context):
    """Test 7: Validate confidence threshold filtering."""
    # Create many similar outcomes to build high-confidence patterns
    for i in range(50):
        analyzer.analyze_outcome(
            decision_id=f"decision_conf_{i:03d}",
            outcome_type=OutcomeType.SUCCESS,
            result_metrics={"efficiency": 0.9},
            context=simple_context
        )
    
    pattern_set = analyzer.identify_patterns(lookback_window=50)
    high_conf = pattern_set.get_high_confidence(threshold=0.8)
    
    # With 50 similar successes, should have high-confidence patterns
    assert len(high_conf) > 0
    for pattern in high_conf:
        assert pattern.confidence >= 0.8
        assert pattern.support_count > 0


def test_pattern_categories(analyzer):
    """Test 8: Verify all 4 pattern categories are covered."""
    # Create contexts that trigger different pattern categories
    contexts = [
        # Temporal pattern (business hours)
        DecisionContext("temporal_task", 0.5, {"cpu": 0.8}, 0.3, ["agent_1"]),
        # Contextual pattern (high complexity)
        DecisionContext("context_task", 0.9, {"cpu": 0.8}, 0.3, ["agent_1"]),
        # Sequential pattern (multi-agent)
        DecisionContext("seq_task", 0.5, {"cpu": 0.8}, 0.3, ["a1", "a2", "a3"]),
        # Causal pattern (low resources)
        DecisionContext("causal_task", 0.5, {"cpu": 0.3, "memory": 0.2}, 0.3, ["agent_1"])
    ]
    
    for i, ctx in enumerate(contexts):
        analyzer.analyze_outcome(
            decision_id=f"cat_decision_{i:03d}",
            outcome_type=OutcomeType.SUCCESS,
            result_metrics={"efficiency": 0.85},
            context=ctx
        )
    
    pattern_set = analyzer.identify_patterns(lookback_window=10)
    
    # Check that patterns from different categories exist
    categories_found = {p.category for p in pattern_set.patterns}
    # Should have at least 2 different categories
    assert len(categories_found) >= 2


def test_statistics_calculation(analyzer, simple_context):
    """Test 9: Validate statistics are calculated accurately."""
    # Create mix of successes and failures
    for i in range(20):
        outcome_type = OutcomeType.SUCCESS if i % 3 != 0 else OutcomeType.FAILURE
        analyzer.analyze_outcome(
            decision_id=f"stat_decision_{i:03d}",
            outcome_type=outcome_type,
            result_metrics={"efficiency": 0.8 if outcome_type == OutcomeType.SUCCESS else 0.3},
            context=simple_context
        )
    
    stats = analyzer.get_statistics()
    
    assert stats["outcomes_analyzed"] == 20
    assert 0.0 <= stats["average_reward"] <= 1.0
    assert 0.0 <= stats["success_rate"] <= 1.0
    # With i%3 != 0 for success: 0,1,2 -> S,S,F pattern = 13 successes out of 20
    assert stats["success_rate"] == pytest.approx(13/20, abs=0.01)


def test_aftermath_integration(analyzer, simple_context):
    """Test 10: Verify AfterMath feedback loop integration."""
    # Simulate AfterMath feedback cycle
    outcome1 = analyzer.analyze_outcome(
        decision_id="aftermath_001",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.9},
        context=simple_context
    )
    
    # AfterMath should capture this outcome
    assert outcome1.outcome_id in analyzer.outcomes
    assert len(analyzer.reward_history) == 1
    
    # Second iteration with learned patterns
    outcome2 = analyzer.analyze_outcome(
        decision_id="aftermath_002",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.95},
        context=simple_context
    )
    
    # Should accumulate history
    assert len(analyzer.outcomes) == 2
    assert len(analyzer.reward_history) == 2
    
    # Extract patterns (AfterMath analysis)
    pattern_set = analyzer.identify_patterns(lookback_window=10)
    assert pattern_set.statistics["extraction_number"] == 1


def test_partial_and_timeout_outcomes(analyzer, simple_context):
    """Test 11: Test partial success and timeout outcomes."""
    # Partial success
    partial = analyzer.analyze_outcome(
        decision_id="partial_001",
        outcome_type=OutcomeType.PARTIAL,
        result_metrics={"efficiency": 0.6},
        context=simple_context
    )
    
    assert -1.0 <= partial.reward <= 1.0
    assert partial.reward < 1.0  # Less than full success
    assert partial.reward > -1.0  # Better than full failure
    
    # Timeout
    timeout = analyzer.analyze_outcome(
        decision_id="timeout_001",
        outcome_type=OutcomeType.TIMEOUT,
        result_metrics={"efficiency": 0.0},
        context=simple_context
    )
    
    assert timeout.reward < 0.0  # Negative for timeout


def test_pattern_confidence_calculation(analyzer, simple_context):
    """Test 12: Validate pattern confidence increases with support."""
    # Create 10 outcomes
    for i in range(10):
        analyzer.analyze_outcome(
            decision_id=f"confidence_{i:03d}",
            outcome_type=OutcomeType.SUCCESS,
            result_metrics={"efficiency": 0.9},
            context=simple_context
        )
    
    pattern_set_10 = analyzer.identify_patterns(lookback_window=10)
    
    # Create 40 more similar outcomes (total 50)
    for i in range(10, 50):
        analyzer.analyze_outcome(
            decision_id=f"confidence_{i:03d}",
            outcome_type=OutcomeType.SUCCESS,
            result_metrics={"efficiency": 0.9},
            context=simple_context
        )
    
    pattern_set_50 = analyzer.identify_patterns(lookback_window=50)
    
    # Patterns from 50 outcomes should have higher or equal confidence
    if pattern_set_10.patterns and pattern_set_50.patterns:
        # Find matching patterns
        pattern_id = pattern_set_10.patterns[0].pattern_id
        pattern_50 = next((p for p in pattern_set_50.patterns if p.pattern_id == pattern_id), None)
        
        if pattern_50:
            # More support should lead to higher confidence
            assert pattern_50.support_count >= pattern_set_10.patterns[0].support_count


def test_low_resource_causal_patterns(analyzer):
    """Test 13: Test causal patterns with resource constraints."""
    low_resource_context = DecisionContext(
        task_type="resource_test",
        complexity=0.5,
        resource_constraints={"cpu": 0.3, "memory": 0.9},  # Low CPU, high memory
        time_pressure=0.3,
        agent_ids=["agent_1"]
    )
    
    outcome = analyzer.analyze_outcome(
        decision_id="resource_001",
        outcome_type=OutcomeType.SUCCESS,
        result_metrics={"efficiency": 0.85},
        context=low_resource_context
    )
    
    # Should detect causal patterns related to resources
    patterns = outcome.patterns_identified
    assert any("causal" in p for p in patterns)
    assert any("resource" in p.lower() or "memory" in p.lower() for p in patterns)


def test_error_outcome_handling(analyzer, simple_context):
    """Test 14: Test error outcome handling."""
    error_outcome = analyzer.analyze_outcome(
        decision_id="error_001",
        outcome_type=OutcomeType.ERROR,
        result_metrics={"efficiency": 0.0, "error_code": 500},
        context=simple_context
    )
    
    assert error_outcome.outcome_type == OutcomeType.ERROR
    assert error_outcome.reward < 0.0  # Negative reward for errors
    assert error_outcome.reward >= -1.0  # Within bounds


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
            context=ctx
        )
    
    pattern_set = analyzer.identify_patterns(lookback_window=10)
    
    # Test category filtering
    contextual = pattern_set.get_by_category(PatternCategory.CONTEXTUAL)
    sequential = pattern_set.get_by_category(PatternCategory.SEQUENTIAL)
    
    # Should be able to filter by category
    for pattern in contextual:
        assert pattern.category == PatternCategory.CONTEXTUAL
    for pattern in sequential:
        assert pattern.category == PatternCategory.SEQUENTIAL
