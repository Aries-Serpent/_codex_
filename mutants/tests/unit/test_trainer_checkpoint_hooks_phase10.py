from __future__ import annotations

import pytest

pytest.importorskip("tensorboard")

import json
from contextlib import nullcontext
from pathlib import Path

from src.training import trainer as trainer_module
from src.training.trainer import CheckpointConfig, Trainer, TrainerConfig


class FakeTensor:
    def __init__(self, value: float) -> None:
        self.value = float(value)

    def to(self, _device: str):
        return self

    def backward(self) -> None:
        return None

    def detach(self):
        return self

    def cpu(self):
        return self

    def item(self) -> float:
        return self.value

    def __truediv__(self, divisor: float):
        return FakeTensor(self.value / divisor)


class FakeModel:
    def to(self, _device: str):
        return self

    def train(self) -> None:
        return None

    def eval(self) -> None:
        return None

    def __call__(self, inputs):
        value = next(iter(inputs.values())).value if isinstance(inputs, dict) else inputs.value
        return FakeTensor(value + 1.0)

    def state_dict(self) -> dict[str, float]:
        return {"v": 1.0}

    def parameters(self):
        return []


class FakeOptimizer:
    def __init__(self) -> None:
        self.steps = 0

    def step(self) -> None:
        self.steps += 1

    def zero_grad(self, **_kwargs) -> None:
        return None

    def state_dict(self) -> dict[str, int]:
        return {"steps": self.steps}

    def load_state_dict(self, _state):
        return None


@pytest.fixture(autouse=True)
def enable_torch_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_ALLOW_TORCH_STUB", "1")


def _build_trainer(cfg: TrainerConfig) -> Trainer:
    return Trainer(
        FakeModel(),
        FakeOptimizer(),
        [(FakeTensor(0.0), FakeTensor(0.0)), (FakeTensor(1.0), FakeTensor(1.0))],
        val_loader=[(FakeTensor(0.0), FakeTensor(0.0))],
        loss_fn=lambda outputs, labels: FakeTensor(abs(outputs.value - labels.value)),
        config=cfg,
    )


def test_train_mixed_precision_uses_autocast(monkeypatch):
    calls: list[bool] = []

    def fake_autocast(*, enabled: bool = False):
        calls.append(enabled)
        return nullcontext()

    monkeypatch.setattr(trainer_module, "autocast", fake_autocast)
    trainer = _build_trainer(TrainerConfig(epochs=1, mixed_precision=True))
    trainer.train()
    assert calls and all(calls), "calls is not valid"


def test_checkpoint_pointer_written_with_mocked_torch_save(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(trainer_module, "_HAS_REAL_TORCH", True)

    def fake_save(_payload, path):
        Path(path).write_text("checkpoint", encoding="utf-8")

    monkeypatch.setattr(trainer_module.torch, "save", fake_save)

    cfg = TrainerConfig(
        epochs=1, checkpoint=CheckpointConfig(directory=str(tmp_path / "ckpts"), best_k=1)
    )
    trainer = _build_trainer(cfg)
    trainer.train()
    latest = tmp_path / "ckpts" / "latest.json"
    assert latest.exists(), "Condition must be true"
    payload = json.loads(latest.read_text(encoding="utf-8"))
    assert payload["path"].endswith(".pt"), "Condition must be true"
