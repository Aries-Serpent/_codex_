"""
Test Classification Metrics

Test module for classification metrics.
"""

from __future__ import annotations

import pytest

from codex_ml.metrics import f1_score, mean_absolute_error, precision, recall


@pytest.mark.ml
def test_precision_recall_f1_balanced() -> None:
    preds = [1, 0, 1, 1]
    targets = [1, 0, 0, 1]
    assert precision(preds, targets) == pytest.approx(2 / 3)
    assert recall(preds, targets) == pytest.approx(1.0)
    assert f1_score(preds, targets) == pytest.approx(0.8)


@pytest.mark.ml
def test_precision_handles_zero_division() -> None:
    preds = [0, 0, 0]
    targets = [1, 0, 1]
    assert precision(preds, targets) == 0.0
    assert recall(preds, targets) == pytest.approx(0.0)
    assert f1_score(preds, targets) == 0.0


@pytest.mark.ml
def test_mean_absolute_error_is_exported_from_metrics_package() -> None:
    preds = [1.0, 2.0, 3.0]
    targets = [1.1, 1.9, 3.2]
    assert mean_absolute_error(preds, targets) == pytest.approx((0.1 + 0.1 + 0.2) / 3)


@pytest.mark.ml
def test_mean_absolute_error_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        mean_absolute_error([1.0, 2.0], [1.0])


@pytest.mark.ml
def test_mean_absolute_error_rejects_empty_inputs() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        mean_absolute_error([], [])
