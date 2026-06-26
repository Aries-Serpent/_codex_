"""
Tests for reasoning evaluation metrics
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codex_ml.eval.reasoning_metrics import (
    calculate_consistency,
    calculate_critique_density,
    calculate_explanation_depth,
    calculate_judge_disagreement,
    calculate_latency_delta,
    calculate_trace_coverage,
    calculate_win_rate,
    evaluate_reasoning,
)


def test_win_rate_basic():
    """Test basic win rate calculation"""
    preds = ["This is a detailed answer", "Short"]
    refs = ["This is good", "Also short"]

    rate = calculate_win_rate(preds, refs)
    assert 0.0 <= rate <= 1.0, "0 is not valid"


def test_win_rate_empty():
    """Test win rate with empty inputs"""
    assert calculate_win_rate([], []) == 0.0
    assert calculate_win_rate(["test"], []) == 0.0


def test_critique_density():
    """Test critique density calculation"""
    responses = [
        "Let me explain step by step: First, because X, therefore Y.",
        "Simple answer.",
    ]

    density = calculate_critique_density(responses)
    assert 0.0 <= density <= 1.0, "0 is not valid"
    assert density > 0.0, "density must be greater than zero"


def test_critique_density_structured():
    """Test critique density with structured responses"""
    responses = ["""
        Let me solve this step by step:
        1. First step
        2. Second step
        Therefore, the answer is X.

        For example, consider Y.
        However, note that Z.
        """]

    density = calculate_critique_density(responses)
    assert density > 0.5, "density must be greater than zero"


def test_latency_delta():
    """Test latency delta calculation"""
    latencies = [100, 200, 300, 150, 250]
    baseline = [120, 220, 320, 170, 270]

    delta = calculate_latency_delta(latencies, baseline)
    assert isinstance(delta, float)


def test_latency_empty():
    """Test latency with empty input"""
    assert calculate_latency_delta([]) == 0.0, "Condition must be true"


def test_judge_disagreement():
    """Test judge disagreement calculation"""
    # High agreement
    ratings_agree = [[0.8, 0.82, 0.79], [0.5, 0.52, 0.51]]
    disagreement_low = calculate_judge_disagreement(ratings_agree)

    # High disagreement
    ratings_disagree = [[0.2, 0.8, 0.5], [0.1, 0.9, 0.5]]
    disagreement_high = calculate_judge_disagreement(ratings_disagree)

    assert disagreement_low < disagreement_high, "disagreement_low is not valid"


def test_trace_coverage():
    """Test trace coverage calculation"""
    responses = [
        "First, do A. Then, do B. Finally, do C.",
        "Just do it.",
    ]

    coverage = calculate_trace_coverage(responses)
    assert 0.0 <= coverage <= 1.0, "0 is not valid"


def test_trace_coverage_with_required_steps():
    """Test trace coverage with required steps"""
    responses = ["First analyze X, then compute Y"]
    required = [["analyze", "compute"]]

    coverage = calculate_trace_coverage(responses, required)
    assert coverage == 1.0, "coverage is not valid"


def test_trace_coverage_empty_required_steps():
    """Test trace coverage with empty required steps"""
    responses = ["Some response"]
    required = [[]]  # Empty required steps

    coverage = calculate_trace_coverage(responses, required)
    assert coverage == 0.0, "coverage is not valid"


def test_explanation_depth():
    """Test explanation depth calculation"""
    responses = [
        """
        Let me derive this:
        - Because A
        - Therefore B
        - Thus C

        Proof:
        1. Start with X
          1.1. Sub-step
        2. Derive Y
        """,
        "Simple answer",
    ]

    depth = calculate_explanation_depth(responses)
    assert 0.0 <= depth <= 1.0, "0 is not valid"
    assert depth > 0.0, "depth must be greater than zero"


def test_consistency():
    """Test consistency calculation"""
    # Consistent responses
    consistent = ["X is true. X leads to Y."]
    score_good = calculate_consistency(consistent)

    # Potentially inconsistent
    inconsistent = ["X is true but X is false."]
    score_bad = calculate_consistency(inconsistent)

    assert score_good > score_bad, "score_good must be greater than zero"


def test_evaluate_reasoning_comprehensive():
    """Test comprehensive reasoning evaluation"""
    preds = ["Step 1: A. Therefore B. For example, C."]
    refs = ["The answer is B"]

    metrics = evaluate_reasoning(preds, refs)

    assert hasattr(metrics, "win_rate")
    assert hasattr(metrics, "critique_density")
    assert hasattr(metrics, "trace_coverage")
    assert 0.0 <= metrics.win_rate <= 1.0, "0 is not valid"
    assert 0.0 <= metrics.critique_density <= 1.0, "0 is not valid"


def test_evaluate_reasoning_with_optional_args():
    """Test evaluation with all optional arguments"""
    preds = ["Answer with reasoning"]
    refs = ["Reference answer"]
    baseline = ["Baseline answer"]
    latencies = [150.0]
    judges = [[0.8, 0.75, 0.85]]

    metrics = evaluate_reasoning(
        preds, refs, baseline_predictions=baseline, latencies=latencies, judge_ratings=judges
    )

    assert metrics.latency_p95 > 0, "latency_p95 must be greater than zero"
    assert metrics.judge_disagreement >= 0, "judge_disagreement must be greater than zero"


def test_division_by_zero_safety():
    """Test that division by zero is handled safely"""
    # Empty responses
    assert calculate_critique_density([]) == 0.0, "Condition must be true"
    assert calculate_trace_coverage([]) == 0.0, "Condition must be true"
    assert calculate_explanation_depth([]) == 0.0, "Condition must be true"
    assert calculate_consistency([]) == 0.0, "Condition must be true"

    # Empty required steps
    assert calculate_trace_coverage(["test"], [[]]) == 0.0


if __name__ == "__main__":
    # Run all tests
    test_win_rate_basic()
    print("✓ test_win_rate_basic")

    test_win_rate_empty()
    print("✓ test_win_rate_empty")

    test_critique_density()
    print("✓ test_critique_density")

    test_critique_density_structured()
    print("✓ test_critique_density_structured")

    test_latency_delta()
    print("✓ test_latency_delta")

    test_latency_empty()
    print("✓ test_latency_empty")

    test_judge_disagreement()
    print("✓ test_judge_disagreement")

    test_trace_coverage()
    print("✓ test_trace_coverage")

    test_trace_coverage_with_required_steps()
    print("✓ test_trace_coverage_with_required_steps")

    test_trace_coverage_empty_required_steps()
    print("✓ test_trace_coverage_empty_required_steps")

    test_explanation_depth()
    print("✓ test_explanation_depth")

    test_consistency()
    print("✓ test_consistency")

    test_evaluate_reasoning_comprehensive()
    print("✓ test_evaluate_reasoning_comprehensive")

    test_evaluate_reasoning_with_optional_args()
    print("✓ test_evaluate_reasoning_with_optional_args")

    test_division_by_zero_safety()
    print("✓ test_division_by_zero_safety")

    print("\n✅ All reasoning metrics tests passed!")
