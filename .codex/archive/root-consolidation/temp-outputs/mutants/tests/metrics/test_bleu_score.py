"""
Test Bleu Score

Test module for bleu score.
"""

from __future__ import annotations

from codex_ml.metrics.metric_implementations import BLEUScore


def test_bleu_perfect_match() -> None:
    metric = BLEUScore(n_gram=2)
    metric.update([["hello", "world"]], [["hello", "world"]])
    result = metric.compute()
    # Use pytest.approx for floating point comparison
    import pytest

    assert result["bleu_score"] == pytest.approx(1.0), "Result must not be empty"
    assert result["brevity_penalty"] == pytest.approx(1.0), "Result must not be empty"


def test_bleu_handles_no_overlap() -> None:
    metric = BLEUScore(n_gram=2)
    metric.update([["foo", "bar"]], [["baz", "qux"]])
    result = metric.compute()["bleu_score"]
    assert result == 0.0, "Result must not be empty"
