"""
Test Extended Trainer

Test module for extended trainer.
"""

# isort: skip_file

from __future__ import annotations
import pytest

pytest.importorskip("torch")

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


try:
    import torch
except (ImportError, AttributeError) as exc:  # pragma: no cover - runtime guard
    pytest.skip(f"PyTorch runtime not available: {exc}", allow_module_level=True)

import training.trainer as trainer_mod

from logging_utils import LoggingConfig

torch_data = getattr(torch, "utils", None)
if torch_data is None or not hasattr(torch_data, "data"):
    pytest.skip("torch.utils.data not available", allow_module_level=True)

DataLoader = torch_data.data.DataLoader  # type: ignore[attr-defined]
TensorDataset = torch_data.data.TensorDataset  # type: ignore[attr-defined]

TORCH_STUB = getattr(torch, "__version__", "").endswith("stub")
skip_if_stub = pytest.mark.skipif(TORCH_STUB, reason="trainer tests require real torch")


def test_extended_trainer_module_available() -> None:
    assert hasattr(trainer_mod, "ExtendedTrainer")


class RecordingOptimizer(torch.optim.SGD):
    def __init__(self, params, lr: float) -> None:
        super().__init__(params, lr=lr)
        self.step_calls = 0

    def step(self, closure=None):  # type: ignore[override]
        self.step_calls += 1
        return super().step(closure)


def _build_loaders() -> tuple[DataLoader, DataLoader]:
    inputs = torch.randn(6, 4)
    labels = torch.tensor([0, 1, 0, 1, 0, 1], dtype=torch.long)
    train_ds = TensorDataset(inputs, labels)
    val_ds = TensorDataset(inputs[:4], labels[:4])
    train_loader = DataLoader(train_ds, batch_size=2, shuffle=False)
    val_loader = DataLoader(val_ds, batch_size=2, shuffle=False)
    return train_loader, val_loader


def _accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    predictions = logits.argmax(dim=-1)
    return float((predictions == targets).float().mean().item())


@skip_if_stub
def test_extended_trainer_runs_and_checkpoints(tmp_path: Path) -> None:
    train_loader, val_loader = _build_loaders()
    model = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.ReLU(), torch.nn.Linear(8, 2))
    optimizer = RecordingOptimizer(model.parameters(), lr=0.05)
    trainer = trainer_mod.ExtendedTrainer(
        model,
        optimizer,
        train_loader,
        device="cpu",
        val_loader=val_loader,
        trainer_config=trainer_mod.TrainerConfig(epochs=2, gradient_accumulation_steps=2),
        checkpoint_config=trainer_mod.CheckpointConfig(
            directory=str(tmp_path), keep_best_k=1, maximize_metric=True
        ),
        metric_fn=_accuracy,
    )

    trainer.train()

    checkpoint_files = sorted(tmp_path.glob("*.pt"))
    assert len(checkpoint_files) == 1, "Checkpoint_files must not be empty"
    state = torch.load(
        checkpoint_files[0], map_location="cpu", weights_only=False
    )  # nosec B614 - Test checkpoint with optimizer state requires weights_only=False
    assert state["epoch"] in {1, 2}
    assert "model_state" in state, "Condition must be true"
    steps_per_epoch = len(train_loader)
    expected_steps = 2 * math.ceil(steps_per_epoch / 2)
    assert optimizer.step_calls == expected_steps, "step_calls is not valid"


@skip_if_stub
def test_evaluate_requires_metric(tmp_path: Path) -> None:
    train_loader, _ = _build_loaders()
    model = torch.nn.Linear(4, 2)
    optimizer = RecordingOptimizer(model.parameters(), lr=0.01)
    trainer = trainer_mod.ExtendedTrainer(
        model,
        optimizer,
        train_loader,
        device="cpu",
    )

    with pytest.raises(RuntimeError):
        trainer.evaluate()


@skip_if_stub
def test_trainer_seed_calls_repro(monkeypatch: pytest.MonkeyPatch) -> None:
    train_loader, _ = _build_loaders()
    model = torch.nn.Linear(4, 2)
    optimizer = RecordingOptimizer(model.parameters(), lr=0.01)
    recorded: dict[str, int] = {}

    def _record_seed(seed: int, *, deterministic: bool | None = None) -> None:
        recorded["seed"] = seed

    monkeypatch.setattr(trainer_mod, "_set_seed", _record_seed)

    trainer = trainer_mod.ExtendedTrainer(
        model,
        optimizer,
        train_loader,
        device="cpu",
        trainer_config=trainer_mod.TrainerConfig(
            epochs=1,
            seed=99,
            logging=LoggingConfig(
                enable_tensorboard=False,
                enable_mlflow=False,
                enable_fallback_metrics=False,
            ),
        ),
    )
    trainer.close()
    assert recorded["seed"] == 99, "rec is not valid"


@skip_if_stub
def test_trainer_writes_metrics_ndjson(tmp_path: Path) -> None:
    train_loader, _ = _build_loaders()
    model = torch.nn.Linear(4, 2)
    optimizer = RecordingOptimizer(model.parameters(), lr=0.05)
    metrics_path = tmp_path / "metrics.ndjson"
    trainer = trainer_mod.ExtendedTrainer(
        model,
        optimizer,
        train_loader,
        device="cpu",
        val_loader=train_loader,
        loss_fn=_accuracy,
        trainer_config=trainer_mod.TrainerConfig(
            epochs=1,
            logging=LoggingConfig(
                enable_tensorboard=False,
                enable_mlflow=False,
                enable_fallback_metrics=False,
            ),
            metrics_ndjson_path=str(metrics_path),
        ),
        metric_fn=_accuracy,
    )

    trainer.train()
    trainer.close()

    assert metrics_path.exists(), "Condition must be true"
    payload = metrics_path.read_text(encoding="utf-8")
    assert '"epoch": 1' in payload, "Condition must be true"
