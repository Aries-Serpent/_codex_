"""
Test Eval Loop Cpu

Test module for eval loop cpu.
"""

from __future__ import annotations

import json
import math
import types

import pytest

from codex_ml.metrics.evaluator import batch_metrics
from codex_ml.training.eval import evaluate

torch = pytest.importorskip("torch")


def _make_batch(size: int = 2) -> dict[str, object]:
    return {
        "input_ids": torch.ones((size, 4), dtype=torch.long),
        "labels": torch.tensor([[1, 2, 3, 4]] * size, dtype=torch.long),
    }


class _ToyModel:
    def __init__(self) -> None:
        torch.manual_seed(0)
        self.linear = torch.nn.Linear(4, 5)
        self.loss_fn = torch.nn.CrossEntropyLoss()
        self._training = True

    def eval(self) -> None:
        self._training = False

    def train(self, mode: bool = True) -> None:  # pragma: no cover - behaviour tested indirectly
        self._training = mode

    @property
    def training(self) -> bool:
        return self._training

    def __call__(self, input_ids, labels):  # type: ignore[no-untyped-def]
        # Expand to produce per-token logits: (batch, seq_len) -> (batch, seq_len, vocab_size)
        batch_size, seq_len = input_ids.shape
        # Apply linear layer to each token position
        expanded = input_ids.float().unsqueeze(-1)  # (batch, seq_len, 1)
        # Replicate to match input dimension
        expanded = expanded.expand(batch_size, seq_len, 4)  # (batch, seq_len, 4)
        logits = self.linear(expanded)  # (batch, seq_len, 5)
        loss = self.loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
        return types.SimpleNamespace(loss=loss, logits=logits)


@pytest.mark.cpu
def test_evaluate_accumulates_cpu_metrics() -> None:
    batches = [_make_batch(), _make_batch()]
    model = _ToyModel()

    metrics = evaluate(
        model,
        batches,
        loss_fn=lambda outputs, batch: outputs.loss,
        metrics_fn=batch_metrics,
        device="cpu",
    )

    assert set(metrics) == {"eval_loss", "loss", "perplexity", "token_accuracy"}
    assert 0.0 <= metrics["token_accuracy"] <= 1.0, "0 is not valid"
    assert metrics["perplexity"] == pytest.approx(math.exp(metrics["loss"]), rel=1e-3)
    assert metrics["eval_loss"] == pytest.approx(metrics["loss"], rel=1e-6)
    assert model.training is True, "training is not valid"


@pytest.mark.cpu
def test_evaluate_handles_none_loss_gracefully() -> None:
    batches = [_make_batch()]
    model = _ToyModel()

    metrics = evaluate(
        model,
        batches,
        loss_fn=lambda _outputs, _batch: None,
        metrics_fn=batch_metrics,
        device="cpu",
    )

    # Metrics from the shim still propagate even if the explicit loss_fn returns None.
    assert set(metrics) == {"loss", "perplexity", "token_accuracy"}
    assert 0.0 <= metrics["token_accuracy"] <= 1.0, "0 is not valid"
    assert metrics["perplexity"] == pytest.approx(math.exp(metrics["loss"]), rel=1e-3)
    assert model.training is True, "training is not valid"


@pytest.mark.cpu
def test_evaluate_writes_ndjson(tmp_path) -> None:
    batches = [_make_batch()]
    model = _ToyModel()
    log_path = tmp_path / "metrics.ndjson"

    metrics = evaluate(
        model,
        batches,
        loss_fn=lambda outputs, batch: outputs.loss,
        metrics_fn=batch_metrics,
        device="cpu",
        ndjson_path=log_path,
    )

    assert log_path.exists(), "Condition must be true"
    payloads = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert len(payloads) == 1, "Payloads must not be empty"
    record = payloads[0]
    assert record["batches"] == 1, "rec is not valid"
    for key, value in metrics.items():
        assert key in record, "Condition must be true"
        assert record[key] == pytest.approx(value), "Value must be initialized"
