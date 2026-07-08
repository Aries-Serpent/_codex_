"""Tests for metric registry aliases.

Validates that both "rougeL" and "rouge_l" resolve to the same offline
implementation and produce identical results.
"""

import sys
from pathlib import Path

import pytest

# Add src to path
_REPO_ROOT = Path(__file__).parent.parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def test_rouge_aliases_resolve_and_match():
    """Test that rougeL and rouge_l are aliases to the same implementation."""
    from codex_ml.metrics.registry import get_metric

    # Both keys should resolve without error
    fn_camel = get_metric("rougeL")
    fn_snake = get_metric("rouge_l")

    preds = ["the quick brown fox", "lorem ipsum dolor sit amet"]
    refs = ["the quick brown fox", "dolor sit amet lorem ipsum"]

    out_camel = fn_camel(preds, refs)
    out_snake = fn_snake(preds, refs)

    # Both should return the same result
    assert out_camel == out_snake, "out_camel is not valid"
    assert isinstance(out_camel, float)
    assert isinstance(out_snake, float)
    assert 0.0 <= out_camel <= 1.0, "0 is not valid"
    assert 0.0 <= out_snake <= 1.0, "0 is not valid"


def test_registry_lists_normalized_name():
    """Test that the registry lists the normalized (lowercase) name."""
    from codex_ml.metrics.registry import list_metrics

    # Registry normalizes names to lowercase for listing
    names = list_metrics()
    assert "rougel" in names, "Condition must be true"


def test_both_aliases_resolve_to_offline_implementation():
    """Test that both alias keys resolve to the offline implementation."""
    from codex_ml.metrics.registry import get_metric

    fn_camel = get_metric("rougeL")
    fn_snake = get_metric("rouge_l")

    # Check that the function is from the generative module (offline implementation)
    assert fn_camel.__module__ in ("codex_ml.metrics.generative", "codex_ml.metrics.registry")
    assert fn_snake.__module__ in ("codex_ml.metrics.generative", "codex_ml.metrics.registry")

    # Both should work without rouge_score dependency
    result = fn_camel(["test"], ["test"])
    assert result is not None, "result must be initialized"
    assert isinstance(result, float)
    assert result > 0.0, "result must be greater than zero"


@pytest.mark.parametrize(
    ("pred", "ref", "min_score"),
    [
        ("a b c", "a b c", 0.99),  # Perfect match
        ("a b c", "a b", 0.5),  # Partial match
        ("a b", "a b c", 0.5),  # Partial match
        ("", "a b c", 0.0),  # Empty prediction
        ("a b c", "", 0.0),  # Empty reference
    ],
)
def test_rouge_l_core_cases(pred: str, ref: str, min_score: float):
    """Test ROUGE-L on core cases using both aliases."""
    from codex_ml.metrics.registry import get_metric

    fn = get_metric("rougeL")
    score = fn([pred], [ref])
    assert isinstance(score, float)
    assert score >= min_score - 0.01, "score must be greater than zero"


def test_alias_produces_identical_results():
    """Verify both aliases produce identical results on the same inputs."""
    from codex_ml.metrics.registry import get_metric

    fn_camel = get_metric("rougeL")
    fn_snake = get_metric("rouge_l")

    # Test multiple input pairs
    test_cases = [
        (["hello world"], ["hello world"]),
        (["the cat sat"], ["the dog sat"]),
        (["foo bar baz"], ["qux quux corge"]),
    ]

    for preds, refs in test_cases:
        result_camel = fn_camel(preds, refs)
        result_snake = fn_snake(preds, refs)
        assert result_camel == result_snake, f"Results differ for {preds}, {refs}"
