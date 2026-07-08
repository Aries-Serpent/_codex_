"""
Test Metrics Token Accuracy

Test module for metrics token accuracy.
"""

from types import SimpleNamespace

import pytest

from codex_ml.metrics.evaluator import batch_metrics

pytestmark = pytest.mark.requires_torch

torch = pytest.importorskip("torch")


def test_token_accuracy_ignores_masked_labels() -> None:
    logits = torch.tensor(
        [
            [[0.1, 0.9], [0.7, 0.3], [0.8, 0.2]],
        ]
    )
    labels = torch.tensor([[1, -100, 1]])
    outputs = SimpleNamespace(logits=logits, loss=torch.tensor(0.0))

    metrics = batch_metrics(outputs, {"labels": labels})

    assert "token_accuracy" in metrics, "Condition must be true"
    assert metrics["token_accuracy"] == pytest.approx(0.5), "Condition must be true"
