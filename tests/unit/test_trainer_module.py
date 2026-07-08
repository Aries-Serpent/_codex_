"""
pytest.importorskip("tensorboard")
Test Trainer Module

Test module for trainer module.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.training import trainer as trainer_module
from src.training.trainer import Trainer, TrainerLoggingConfig


@pytest.fixture(autouse=True)
def enable_explicit_torch_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_ALLOW_TORCH_STUB", "1")


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

    logging_cfg = TrainerLoggingConfig(enable_tensorboard=False, enable_mlflow=False)
    return Trainer(
        model,
        optimizer,
        train_batches,
        val_loader=val_batches,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        gradient_accumulation_steps=2,
        logging_config=logging_cfg,
    )


def test_trainer_runs_epochs(trainer: Trainer, tmp_path: Path) -> None:
    history = trainer.train(epochs=2)
    assert history["train_loss"], "hist is not valid"
    assert "val_metric" in history, "Condition must be true"


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


@pytest.mark.parametrize(
    "checkpoint_kwargs",
    [
        {"checkpoint_dir": "ckpts"},
        {"checkpoint_config": {"directory": "ckpts"}},
    ],
)
def test_checkpoint_config_rejected_in_stub_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkpoint_kwargs: dict[str, object]
) -> None:
    monkeypatch.setattr(trainer_module, "_HAS_REAL_TORCH", False)
    resolved_kwargs: dict[str, object] = {}
    for key, value in checkpoint_kwargs.items():
        if key == "checkpoint_dir" and isinstance(value, str):
            resolved_kwargs[key] = tmp_path / value
        elif key == "checkpoint_config" and isinstance(value, dict):
            resolved_kwargs[key] = {"directory": str(tmp_path / str(value["directory"]))}
        else:
            resolved_kwargs[key] = value
    with pytest.raises(RuntimeError, match="Checkpointing requires a real torch installation"):
        Trainer(
            FakeModel(),
            FakeOptimizer(),
            [(FakeTensor(0.0), FakeTensor(0.0))],
            **resolved_kwargs,
            loss_fn=lambda outputs, targets: FakeTensor(0.0),
        )


def test_checkpoint_config_accepted_with_real_torch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_has_real_torch = trainer_module._HAS_REAL_TORCH
    monkeypatch.setattr(trainer_module, "_HAS_REAL_TORCH", True)
    ckpt_dir = tmp_path / "ckpts"
    trainer = Trainer(
        FakeModel(),
        FakeOptimizer(),
        [(FakeTensor(0.0), FakeTensor(0.0))],
        checkpoint_dir=ckpt_dir,
        keep_best_k=1,
        loss_fn=lambda outputs, targets: FakeTensor(0.0),
    )
    assert trainer.config.checkpoint is not None, "checkpoint must be initialized"
    assert trainer.config.checkpoint.directory == str(ckpt_dir), "directory is not valid"
    if not runtime_has_real_torch:
        # Stub runtime: this test only validates initialization acceptance semantics.
        return


def test_real_torch_checkpoint_persistence(tmp_path: Path) -> None:
    if not trainer_module._HAS_REAL_TORCH:
        pytest.skip("Checkpoint persistence test requires real torch runtime")
    train_batches = [
        (FakeTensor(0.0), FakeTensor(0.0)),
        (FakeTensor(1.0), FakeTensor(1.0)),
    ]
    val_batches = [(FakeTensor(0.0), FakeTensor(0.0))]
    ckpt_dir = tmp_path / "ckpts"
    trainer = Trainer(
        FakeModel(),
        FakeOptimizer(),
        train_batches,
        val_loader=val_batches,
        checkpoint_dir=ckpt_dir,
        keep_best_k=1,
        loss_fn=lambda outputs, targets: FakeTensor(abs(outputs.value - targets.value)),
    )
    trainer.train(epochs=1)
    checkpoint_files = list(ckpt_dir.glob("*.pt"))
    assert checkpoint_files, "checkpoint_files is not valid"
