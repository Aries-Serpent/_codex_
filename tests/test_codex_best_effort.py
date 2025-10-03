"""Regression tests for Codex orchestration helpers."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from codex_task_sequence import setup_mlflow_tracking
from configs.base_config import BASE_TRAINING_CONFIG, get_base_training_config

ROOT = Path(__file__).resolve().parents[1]

try:  # Optional dependency for evaluation helper tests
    import torch
    from torch.utils.data import DataLoader
except Exception:  # pragma: no cover - torch may be unavailable
    torch = None  # type: ignore
    DataLoader = None  # type: ignore


def test_base_config_returns_copy() -> None:
    cfg = get_base_training_config()
    cfg["model_name"] = "modified"
    assert BASE_TRAINING_CONFIG["model_name"] != "modified"


@pytest.mark.skipif(torch is None or DataLoader is None, reason="PyTorch not available")
def test_evaluate_batches_runs() -> None:
    from training.functional_training import evaluate_batches

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
    metrics = evaluate_batches(
        _ToyModel(),
        loader,
        lambda data: {"avg": float(data[0].mean())},
        device=torch.device("cpu"),
    )
    assert "loss" in metrics
    assert "avg" in metrics


def test_gradient_accumulation_snippet_present() -> None:
    text = (ROOT / "training" / "functional_training.py").read_text(encoding="utf-8")
    assert "loss_t = loss_t / cfg.grad_accum" in text
    assert "(step + 1) % cfg.grad_accum" in text


def test_setup_mlflow_tracking_dry_run(tmp_path) -> None:
    assert setup_mlflow_tracking(tmp_path / "mlruns", dry_run=True) is False


def test_setup_mlflow_tracking_file_uri(tmp_path, monkeypatch) -> None:
    import codex_task_sequence as cts

    state = {"uri": ""}

    class _DummyMLflow(types.SimpleNamespace):
        def set_tracking_uri(self, uri: str) -> None:  # type: ignore[override]
            state["uri"] = uri

        def get_tracking_uri(self) -> str:  # type: ignore[override]
            return state["uri"]

    monkeypatch.setitem(sys.modules, "mlflow", _DummyMLflow())
    monkeypatch.setattr(
        cts,
        "bootstrap_offline_tracking",
        lambda force=True: f"file://{(tmp_path / 'mlruns').resolve()}",
    )
    try:
        result = setup_mlflow_tracking(tmp_path / "mlruns", dry_run=False)
    finally:
        sys.modules.pop("mlflow", None)
    assert result is True
    assert state["uri"].startswith("file://")
    assert (tmp_path / "mlruns").exists()
