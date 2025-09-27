import math
from types import SimpleNamespace

import pytest

from codex_ml.metrics.evaluator import batch_metrics
from codex_ml.training.eval import evaluate

try:  # pragma: no cover - torch optional in CI
    import torch
except Exception:  # pragma: no cover - skip when torch unavailable
    torch = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(torch is None, reason="requires PyTorch")


def test_evaluate_averages_batch_metrics() -> None:
    if torch is None:
        pytest.skip("requires PyTorch")

    class DummyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.training = True

        def eval(self):  # type: ignore[override]
            self.training = False
            return self

        def train(self, mode: bool = True):  # type: ignore[override]
            self.training = mode
            return self

        def forward(self, input_ids=None, labels=None, loss_scale=None):  # type: ignore[override]
            vocab = 4
            logits = torch.zeros((*labels.shape, vocab), dtype=torch.float32)
            for b in range(labels.shape[0]):
                for t in range(labels.shape[1]):
                    token = int(labels[b, t].item())
                    if token >= 0:
                        logits[b, t, token] = 5.0
                    else:
                        logits[b, t, 0] = 1.0
            loss = loss_scale.float().mean()
            return SimpleNamespace(logits=logits, loss=loss)

    model = DummyModel()
    batches = [
        {
            "input_ids": torch.tensor([[0, 1, 2]], dtype=torch.long),
            "labels": torch.tensor([[0, -100, 1]], dtype=torch.long),
            "loss_scale": torch.tensor(0.5),
        },
        {
            "input_ids": torch.tensor([[1, 2, 3]], dtype=torch.long),
            "labels": torch.tensor([[1, -100, 1]], dtype=torch.long),
            "loss_scale": torch.tensor(0.7),
        },
    ]

    metrics = evaluate(
        model,
        batches,
        loss_fn=lambda outputs, _batch: outputs.loss,
        device="cpu",
        metrics_fn=batch_metrics,
    )

    assert metrics["eval_loss"] == pytest.approx(0.6)
    expected_perplexity = (math.exp(0.5) + math.exp(0.7)) / 2.0
    assert metrics["perplexity"] == pytest.approx(expected_perplexity)
    assert metrics["token_accuracy"] == pytest.approx(1.0)
