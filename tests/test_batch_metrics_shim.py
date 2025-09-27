from __future__ import annotations

import types

import pytest

from codex_ml.metrics.evaluator import batch_metrics


class _Outputs(types.SimpleNamespace):
    pass


torch = pytest.importorskip("torch")


def test_batch_metrics_produces_expected_keys() -> None:
    torch.manual_seed(42)
    logits = torch.randn(2, 3, 5)
    labels = torch.randint(0, 5, (2, 3))

    outputs = _Outputs(loss=torch.tensor(0.5), logits=logits)
    metrics = batch_metrics(outputs, {"labels": labels})

    assert set(metrics) >= {"loss", "perplexity", "token_accuracy"}
    assert metrics["loss"] == pytest.approx(0.5, rel=1e-6)
    assert metrics["perplexity"] == pytest.approx(torch.exp(torch.tensor(0.5)).item(), rel=1e-6)
    assert 0.0 <= metrics["token_accuracy"] <= 1.0
