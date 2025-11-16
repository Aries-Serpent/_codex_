from __future__ import annotations

import pytest

from codex_ml.metrics.registry import get_metric


def test_registry_exposes_basic_classification_metrics() -> None:
    preds = [0, 1, 2, 1]
    targets = [0, 2, 2, 1]

    accuracy = get_metric("accuracy")
    precision = get_metric("precision")
    recall = get_metric("recall")
    f1_macro = get_metric("f1_macro")

    assert accuracy(preds, targets) == pytest.approx(0.75)
    assert precision(preds, targets) == pytest.approx(5 / 6)
    assert recall(preds, targets) == pytest.approx(5 / 6)
    assert f1_macro(preds, targets) == pytest.approx(7 / 9)
