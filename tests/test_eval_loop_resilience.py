"""Regression tests for the evaluation helper's error handling."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from codex_ml.training.eval import evaluate

torch = pytest.importorskip("torch")


class _ConstantLossModel(torch.nn.Module):
    """Simple module that exposes `.loss` for evaluation tests."""

    def __init__(self, value: float = 0.25) -> None:
        super().__init__()
        self.training = True
        self._value = torch.tensor(value)

    def eval(self):  # type: ignore[override]
        self.training = False
        return self

    def train(self, mode: bool = True):  # type: ignore[override]
        self.training = mode
        return self

    def forward(self, **_: object):  # type: ignore[override]
        return SimpleNamespace(loss=self._value)


def test_evaluate_returns_only_loss_when_metrics_failures() -> None:
    batches = [
        {"input_ids": torch.ones((1, 2), dtype=torch.long)},
        {"input_ids": torch.zeros((1, 2), dtype=torch.long)},
    ]
    model = _ConstantLossModel()

    def _boom(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("metrics exploded")

    metrics = evaluate(
        model,
        batches,
        loss_fn=lambda outputs, _batch: outputs.loss,
        metrics_fn=_boom,
        device="cpu",
    )

    assert metrics == {"eval_loss": pytest.approx(0.25)}
    assert model.training is True


def test_evaluate_handles_empty_dataloader() -> None:
    model = _ConstantLossModel()

    metrics = evaluate(
        model,
        [],
        loss_fn=lambda outputs, _batch: outputs.loss,
        device="cpu",
    )

    assert metrics == {}
    assert model.training is True
