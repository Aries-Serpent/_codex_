from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import pytest

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional
    np = None  # type: ignore[assignment]


def _build_dummy_dataset(torch):
    class DummyDataset(torch.utils.data.Dataset):
        def __len__(self) -> int:
            return 4

        def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
            ids = torch.randint(0, 10, (4,), dtype=torch.long)
            return {
                "input_ids": ids,
                "attention_mask": torch.ones_like(ids),
                "labels": torch.zeros_like(ids),
            }

    return DummyDataset()


def test_evaluate_dataloader_runs() -> None:
    torch = pytest.importorskip("torch")
    from training.functional_training import TrainCfg, evaluate_dataloader

    dataset = _build_dummy_dataset(torch)
    loader = torch.utils.data.DataLoader(dataset, batch_size=2)

    class TinyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = torch.nn.Embedding(10, 4)
            self.lm_head = torch.nn.Linear(4, 10)

        def forward(self, input_ids, attention_mask=None, labels=None):  # type: ignore[override]
            hidden = self.embedding(input_ids)
            logits = self.lm_head(hidden)
            loss = None
            if labels is not None:
                loss_fn = torch.nn.CrossEntropyLoss()
                loss = loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
            return types.SimpleNamespace(loss=loss, logits=logits)

    model = TinyModel()
    cfg = TrainCfg(limit_val_batches=None)
    device = torch.device("cpu")
    metrics = evaluate_dataloader(model, loader, cfg, device)
    assert metrics.get("num_batches", 0) > 0


def test_gradient_accumulation_optimizer_steps(monkeypatch) -> None:
    torch = pytest.importorskip("torch")
    from training.functional_training import TrainCfg, run_custom_trainer

    dataset = _build_dummy_dataset(torch)
    step_counter = {"steps": 0}

    class DummyOptimizer:
        def __init__(self, params, lr=0.001, weight_decay=0.0):
            self.params = list(params)

        def zero_grad(self, set_to_none: bool = True) -> None:  # noqa: D401
            for param in self.params:
                if param.grad is not None:
                    param.grad.zero_()

        def step(self) -> None:
            step_counter["steps"] += 1

        def state_dict(self):  # pragma: no cover - compatibility
            return {}

        def load_state_dict(self, state):  # pragma: no cover - compatibility
            return

    def fake_adamw(params, lr=0.001, weight_decay=0.0):
        return DummyOptimizer(params, lr=lr, weight_decay=weight_decay)

    monkeypatch.setattr("training.functional_training.torch.optim.AdamW", fake_adamw)
    monkeypatch.setattr("training.functional_training.clip_grad_norm_", lambda *a, **k: None)
    monkeypatch.setattr("training.functional_training.save_checkpoint", lambda *a, **k: None)

    class TinyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = torch.nn.Embedding(10, 4)
            self.lm_head = torch.nn.Linear(4, 10)

        def forward(self, input_ids, attention_mask=None, labels=None):  # type: ignore[override]
            hidden = self.embedding(input_ids)
            logits = self.lm_head(hidden)
            loss_fn = torch.nn.MSELoss()
            loss = loss_fn(logits.float(), torch.zeros_like(logits.float()))
            return types.SimpleNamespace(loss=loss, logits=logits)

    cfg = TrainCfg(
        epochs=1,
        batch_size=2,
        grad_accum=2,
        lr=1e-3,
        save_every=0,
        patience=5,
        limit_train_batches=4,
        max_steps=4,
    )
    run_custom_trainer(TinyModel(), None, dataset, None, cfg)
    assert step_counter["steps"] == 2


def test_base_config_module_loads() -> None:
    base = pytest.importorskip("configs.base_config")
    assert isinstance(getattr(base, "BASE_CONFIG", {}), dict)
    assert "gradient_accumulation_steps" in base.BASE_CONFIG


def test_mlflow_optional(monkeypatch) -> None:
    from codex_task_sequence import setup_mlflow_tracking

    monkeypatch.setitem(sys.modules, "mlflow", None)
    assert setup_mlflow_tracking(Path("mlruns"), dry_run=True) is False


def test_setup_mlflow_tracking_enforces_file_uri(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from codex_task_sequence import setup_mlflow_tracking

    recorded: dict[str, str] = {}

    class _DummyMlflow:
        def set_tracking_uri(self, uri: str) -> None:  # pragma: no cover - trivial
            recorded["uri"] = uri

    monkeypatch.setitem(sys.modules, "mlflow", _DummyMlflow())
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)

    assert setup_mlflow_tracking(tmp_path / "mlruns", dry_run=False) is True
    assert recorded["uri"].startswith("file:")
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")
    assert Path(os.environ["CODEX_MLFLOW_LOCAL_DIR"]).resolve() == (tmp_path / "mlruns").resolve()
