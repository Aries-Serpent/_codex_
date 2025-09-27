from types import SimpleNamespace

import pytest

from codex_ml.metrics.evaluator import batch_metrics

try:  # pragma: no cover - torch optional in CI
    import torch
except Exception:  # pragma: no cover - skip when torch unavailable
    torch = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(torch is None, reason="requires PyTorch")


def test_token_accuracy_ignores_masked_labels() -> None:
    logits = torch.tensor(
        [
            [[0.1, 0.9], [0.7, 0.3], [0.8, 0.2]],
        ]
    )
    labels = torch.tensor([[1, -100, 1]])
    outputs = SimpleNamespace(logits=logits, loss=torch.tensor(0.0))

    metrics = batch_metrics(outputs, {"labels": labels})

    assert "token_accuracy" in metrics
    assert metrics["token_accuracy"] == pytest.approx(0.5)
