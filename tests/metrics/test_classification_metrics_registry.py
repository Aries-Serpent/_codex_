from __future__ import annotations

import pytest

from codex_ml.metrics import registry


def test_accuracy_metric() -> None:
    metric = registry.get("accuracy")
    value = metric([0, 1, 2, 2], [0, 2, 2, 2])
    assert value == pytest.approx(0.75)


def test_precision_recall_macro() -> None:
    precision = registry.get("precision")
    recall = registry.get("recall")
    preds = ["spam", "ham", "spam", "spam"]
    targets = ["spam", "spam", "ham", "spam"]
    assert 0.0 <= precision(preds, targets) <= 1.0
    assert 0.0 <= recall(preds, targets) <= 1.0


def test_f1_macro_handles_empty_inputs() -> None:
    metric = registry.get("f1_macro")
    assert metric([], []) == 0.0
