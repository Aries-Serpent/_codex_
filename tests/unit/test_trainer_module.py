from __future__ import annotations

from pathlib import Path

import pytest

from src.training.trainer import Trainer, TrainerLoggingConfig


class FakeTensor:
    def __init__(self, value: float) -> None:
        self.value = float(value)
        self.backward_calls = 0

    def to(self, _device: str) -> FakeTensor:
        return self

    def backward(self) -> None:
        self.backward_calls += 1

    def detach(self) -> FakeTensor:
        return self

    def cpu(self) -> FakeTensor:  # pragma: no cover - compatibility
        return self

    def item(self) -> float:
        return self.value

    def __truediv__(self, divisor: float) -> FakeTensor:
        return FakeTensor(self.value / divisor)


class FakeModel:
    def __init__(self) -> None:
        self.mode = "train"
        self.inputs_seen: list[float] = []
        self.device = "cpu"

    def to(self, device: str) -> FakeModel:
        self.device = device
        return self

    def train(self) -> None:
        self.mode = "train"

    def eval(self) -> None:
        self.mode = "eval"

    def __call__(self, inputs):
        value = next(iter(inputs.values())).value if isinstance(inputs, dict) else inputs.value
        self.inputs_seen.append(value)
        return FakeTensor(value + 1.0)

    def state_dict(self) -> dict[str, list[float]]:
        return {"inputs": list(self.inputs_seen)}

    def parameters(self):  # pragma: no cover - compatibility
        return []


class FakeOptimizer:
    def __init__(self) -> None:
        self.steps = 0

    def step(self) -> None:
        self.steps += 1

    def zero_grad(self) -> None:
        pass

    def state_dict(self) -> dict[str, int]:
        return {"steps": self.steps}


@pytest.fixture
def trainer(tmp_path: Path) -> Trainer:
    model = FakeModel()
    optimizer = FakeOptimizer()
    train_batches = [
        (FakeTensor(0.0), FakeTensor(0.0)),
        (FakeTensor(1.0), FakeTensor(1.0)),
        (FakeTensor(2.0), FakeTensor(2.0)),
        (FakeTensor(3.0), FakeTensor(3.0)),
    ]
    val_batches = [
        (FakeTensor(0.0), FakeTensor(0.0)),
        (FakeTensor(1.0), FakeTensor(1.0)),
    ]

    def loss_fn(outputs: FakeTensor, targets: FakeTensor) -> FakeTensor:
        return FakeTensor(abs(outputs.value - targets.value))

    def metric_fn(outputs: FakeTensor, targets: FakeTensor) -> float:
        return abs(outputs.value - targets.value)

    checkpoint_dir = tmp_path / "ckpts"
    logging_cfg = TrainerLoggingConfig(enable_tensorboard=False, enable_mlflow=False)
    return Trainer(
        model,
        optimizer,
        train_batches,
        val_loader=val_batches,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        gradient_accumulation_steps=2,
        checkpoint_dir=checkpoint_dir,
        keep_best_k=1,
        logging_config=logging_cfg,
    )


def test_trainer_runs_epochs(trainer: Trainer, tmp_path: Path) -> None:
    history = trainer.train(epochs=2)
    assert history["train_loss"]
    assert "val_metric" in history
    checkpoint_files = list((tmp_path / "ckpts").glob("*.pt"))
    assert len(checkpoint_files) == 1


def test_metric_mode_validation(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        Trainer(
            FakeModel(),
            FakeOptimizer(),
            [(FakeTensor(0.0), FakeTensor(0.0))],
            metric_mode="invalid",
            loss_fn=lambda outputs, targets: FakeTensor(0.0),
            checkpoint_dir=tmp_path / "ckpts",
        )
