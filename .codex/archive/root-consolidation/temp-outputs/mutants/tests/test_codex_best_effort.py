"""Regression tests for Codex orchestration helpers."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

import cli.task_sequence as task_sequence
import configs.base_config as base_config

ROOT = Path(__file__).resolve().parents[1]

try:  # Optional dependency for evaluation helper tests
    import torch
    from torch.utils.data import DataLoader
except ImportError:  # pragma: no cover - torch may be unavailable
    torch = None  # type: ignore
    DataLoader = None  # type: ignore


def test_base_config_returns_copy() -> None:
    cfg = base_config.get_base_training_config()
    cfg["model_name"] = "modified"
    assert base_config.BASE_TRAINING_CONFIG["model_name"] != "modified", "Condition must be true"


@pytest.mark.skipif(torch is None or DataLoader is None, reason="PyTorch not available")
def test_evaluate_batches_runs() -> None:
    functional_training = importlib.import_module("src.training.functional_training")

    class _ToyDataset(torch.utils.data.Dataset):
        def __len__(self) -> int:
            return 2

        def __getitem__(self, index: int):
            tensor = torch.ones(2, dtype=torch.float32) * (index + 1)
            return {"input_ids": tensor.clone(), "labels": tensor.clone()}

    class _ToyModel(torch.nn.Module):
        def forward(self, input_ids, labels):  # type: ignore[override]
            return {
                "logits": input_ids,
                "loss": torch.nn.functional.mse_loss(input_ids, labels),
            }

    loader = DataLoader(_ToyDataset(), batch_size=1)
    metrics = functional_training.evaluate_batches(
        _ToyModel(),
        loader,
        lambda data: {"avg": float(data[0].mean())},
        device=torch.device("cpu"),
    )
    assert "loss" in metrics, "Condition must be true"
    assert "avg" in metrics, "Condition must be true"


def test_gradient_accumulation_snippet_present() -> None:
    text = (ROOT / "src" / "training" / "functional_training.py").read_text(encoding="utf-8")
    assert "loss_t = loss_t / cfg.grad_accum" in text, "Condition must be true"
    assert "(step + 1) % cfg.grad_accum" in text, "Condition must be true"


def test_setup_mlflow_tracking_dry_run(tmp_path) -> None:
    assert task_sequence.setup_mlflow_tracking(tmp_path / "mlruns", dry_run=True) is False


def test_setup_mlflow_tracking_file_uri(tmp_path, monkeypatch) -> None:
    state = {"uri": ""}

    class _DummyMLflow(types.SimpleNamespace):
        def set_tracking_uri(self, uri: str) -> None:  # type: ignore[override]
            state["uri"] = uri

        def get_tracking_uri(self) -> str:  # type: ignore[override]
            return state["uri"]

    monkeypatch.setitem(sys.modules, "mlflow", _DummyMLflow())
    monkeypatch.setattr(
        task_sequence,
        "bootstrap_offline_tracking",
        lambda force=True: f"file://{(tmp_path / 'mlruns').resolve()}",
    )
    try:
        result = task_sequence.setup_mlflow_tracking(tmp_path / "mlruns", dry_run=False)
    finally:
        sys.modules.pop("mlflow", None)
    assert result is True, "Result must not be empty"
    assert state["uri"].startswith("file://"), "Condition must be true"
    assert (tmp_path / "mlruns").exists(), "Condition must be true"
