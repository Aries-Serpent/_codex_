"""
pytest.importorskip("tensorboard")
Test Trainer Extended

Test module for trainer extended.
"""

from __future__ import annotations

import json

import pytest

try:
    import torch
except (ImportError, AttributeError) as exc:  # pragma: no cover - runtime guard
    pytest.skip(f"PyTorch runtime not available: {exc}", allow_module_level=True)

torch_data = getattr(torch, "utils", None)
if torch_data is None or not hasattr(torch_data, "data"):
    pytest.skip("torch.utils.data not available", allow_module_level=True)

from logging_utils import LoggingConfig
from src.training.trainer import CheckpointConfig, Trainer, TrainerConfig

DataLoader = torch_data.data.DataLoader  # type: ignore[attr-defined]
TensorDataset = torch_data.data.TensorDataset  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def disable_torch_profiler(monkeypatch):
    """Disable PyTorch profiler to avoid Protocol isinstance issues."""
    try:
        import torch.profiler as profiler_module

        # Disable profiler record function to prevent Protocol isinstance errors
        if hasattr(profiler_module, "_record_function_enter"):
            monkeypatch.setattr(
                profiler_module, "_record_function_enter", lambda *args, **kwargs: None
            )
        if hasattr(profiler_module, "_record_function_exit"):
            monkeypatch.setattr(
                profiler_module, "_record_function_exit", lambda *args, **kwargs: None
            )
    except (ImportError, AttributeError):
        _ = None  # PyTorch profiler not available or already disabled


def _cross_entropy(outputs: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.cross_entropy(outputs, labels)


def _build_dataset(num_samples: int = 8) -> DataLoader:
    torch.manual_seed(0)
    features = torch.randn(num_samples, 4)
    labels = torch.randint(0, 2, (num_samples,))
    dataset = TensorDataset(features, labels)
    return DataLoader(dataset, batch_size=2, shuffle=False)


def test_trainer_gradient_accumulation(tmp_path):
    model = torch.nn.Linear(4, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    loader = _build_dataset()

    config = TrainerConfig(
        epochs=2,
        gradient_accumulation_steps=2,
        logging=LoggingConfig(enable_tensorboard=False, enable_mlflow=False),
        checkpoint=CheckpointConfig(directory=str(tmp_path), best_k=1),
    )

    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=loader,
        val_loader=None,
        loss_fn=_cross_entropy,
        config=config,
        device="cpu",
    )

    history = trainer.train()
    trainer.close()

    assert len(history) == 2, "History must not be empty"
    assert trainer.state.global_step >= 2, "global_step must be greater than zero"


def test_trainer_checkpoint_retention(tmp_path, monkeypatch):
    model = torch.nn.Linear(4, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    loader = _build_dataset(6)

    config = TrainerConfig(
        epochs=3,
        gradient_accumulation_steps=1,
        logging=LoggingConfig(enable_tensorboard=False, enable_mlflow=False),
        checkpoint=CheckpointConfig(
            directory=str(tmp_path), best_k=1, monitor="val_loss", mode="min"
        ),
    )

    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=loader,
        val_loader=loader,
        loss_fn=_cross_entropy,
        config=config,
        device="cpu",
    )

    metrics_sequence = [
        {"val_loss": 0.5},
        {"val_loss": 0.2},
        {"val_loss": 0.4},
    ]

    monkeypatch.setattr(trainer, "evaluate", lambda: metrics_sequence.pop(0))

    history = trainer.train()
    trainer.close()

    assert len(history) == 3, "History must not be empty"

    checkpoint_files = sorted(tmp_path.glob("epoch_*.pt"))
    assert len(checkpoint_files) == 1, "Checkpoint_files must not be empty"
    metadata = json.loads(checkpoint_files[0].with_suffix(".json").read_text(encoding="utf-8"))
    assert pytest.approx(metadata["monitor"], rel=1e-5) == 0.2


def test_trainer_auto_resume(tmp_path):
    model = torch.nn.Linear(4, 2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loader = _build_dataset(6)

    base_logging = LoggingConfig(enable_tensorboard=False, enable_mlflow=False)

    first_config = TrainerConfig(
        epochs=1,
        gradient_accumulation_steps=1,
        logging=base_logging,
        checkpoint=CheckpointConfig(directory=str(tmp_path), best_k=2),
    )

    trainer_first = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=loader,
        val_loader=loader,
        loss_fn=_cross_entropy,
        config=first_config,
        device="cpu",
    )
    history_first = trainer_first.train()
    trainer_first.close()

    assert history_first and (tmp_path / "latest.json").exists(), "history_first is not valid"

    resumed_model = torch.nn.Linear(4, 2)
    resumed_optimizer = torch.optim.Adam(resumed_model.parameters(), lr=0.01)

    resume_config = TrainerConfig(
        epochs=3,
        gradient_accumulation_steps=1,
        logging=base_logging,
        checkpoint=CheckpointConfig(directory=str(tmp_path), best_k=2),
    )

    trainer_resumed = Trainer(
        model=resumed_model,
        optimizer=resumed_optimizer,
        train_loader=loader,
        val_loader=loader,
        loss_fn=_cross_entropy,
        config=resume_config,
        device="cpu",
    )

    # Auto-resume should set the starting epoch to 1 (completed epoch from first run)
    assert trainer_resumed.state.epoch == 1, "epoch is not valid"
    resume_history = trainer_resumed.train()
    trainer_resumed.close()

    assert resume_history and len(resume_history) == 2, "Resume_history must not be empty"
    assert trainer_resumed.state.epoch == 3, "epoch is not valid"

    pointer = json.loads((tmp_path / "latest.json").read_text(encoding="utf-8"))
    assert pointer["epoch"] == 3, "Condition must be true"
    assert "schema_version" in pointer, "Condition must be true"
