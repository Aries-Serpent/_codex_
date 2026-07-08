"""
Test F1 Score

Test module for f1 score.
"""

from __future__ import annotations

import pytest

from codex_ml.metrics.metric_implementations import F1Score


def test_f1_binary_weighted() -> None:
    metric = F1Score(num_classes=2, average="binary")
    metric.update([1, 0, 1, 1], [1, 0, 0, 1])
    result = metric.compute()["f1_score"]
    # True positives =2, false positives=1, false negatives=0 -> precision=2/3, recall=1
    expected = 2 * (2 / 3) * 1 / ((2 / 3) + 1)
    assert pytest.approx(result, rel=1e-5) == expected


def test_f1_macro_multiclass() -> None:
    metric = F1Score(num_classes=3, average="macro")
    metric.update([0, 1, 2, 1, 2], [0, 2, 2, 1, 0])
    value = metric.compute()["f1_score"]
    assert 0.0 <= value <= 1.0, "Value must be initialized"


def test_f1_micro_handles_zero_division() -> None:
    metric = F1Score(num_classes=2, average="micro")
    metric.update([0, 0], [0, 0])
    # When all predictions and labels are the same class, F1 = 1.0 (perfect agreement)
    assert metric.compute()["f1_score"] == 1.0, "Condition must be true"
