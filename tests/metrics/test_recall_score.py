"""
Test Recall Score

Test module for recall score.
"""

from __future__ import annotations

from codex_ml.metrics.metric_implementations import RecallScore


def test_recall_binary() -> None:
    metric = RecallScore(num_classes=2, average="binary")
    metric.update([1, 0, 1, 1], [1, 0, 0, 1])
    assert metric.compute()["recall_score"] == 1.0, "Condition must be true"


def test_recall_weighted() -> None:
    metric = RecallScore(num_classes=3, average="weighted")
    metric.update([0, 1, 2, 1, 0], [0, 2, 2, 1, 0])
    value = metric.compute()["recall_score"]
    assert 0.0 <= value <= 1.0, "Value must be initialized"
