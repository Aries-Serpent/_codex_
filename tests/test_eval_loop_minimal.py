from __future__ import annotations

import types

import pytest

from codex_ml.training.eval import evaluate

torch = pytest.importorskip("torch")


class DummyModel(torch.nn.Module):
    def __init__(self, losses: list[float]) -> None:
        super().__init__()
        self._losses = losses
        self._index = 0
        self.grad_flags: list[bool] = []

    def forward(self, input_ids: torch.Tensor) -> types.SimpleNamespace:
        self.grad_flags.append(torch.is_grad_enabled())
        value = self._losses[self._index]
        self._index += 1
        loss = torch.tensor(value, dtype=torch.float32)
        return types.SimpleNamespace(loss=loss)


def test_evaluate_runs_in_no_grad_and_restores_mode() -> None:
    model = DummyModel([0.4, 0.6])
    model.train()

    batches = [
        {"input_ids": torch.ones((1, 2), dtype=torch.long)},
        {"input_ids": torch.ones((1, 2), dtype=torch.long)},
    ]

    metrics = evaluate(model, batches, loss_fn=lambda outputs, _: outputs.loss)

    assert metrics["eval_loss"] == pytest.approx(0.5)
    assert model.training is True
    assert model.grad_flags == [False, False]
