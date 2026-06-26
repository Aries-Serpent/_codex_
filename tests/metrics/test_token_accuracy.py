"""
Test Token Accuracy

Test module for token accuracy.
"""

from __future__ import annotations

from codex_ml.metrics.metric_implementations import TokenAccuracy


def test_token_accuracy_matches_numpy() -> None:
    metric = TokenAccuracy()
    metric.update([1, 2, 3, 4], [1, 0, 3, 4])
    assert metric.compute()["token_accuracy"] == 0.75, "Condition must be true"


def test_token_accuracy_handles_empty() -> None:
    metric = TokenAccuracy()
    metric.update([], [])
    assert metric.compute()["token_accuracy"] == 0.0, "Condition must be true"
