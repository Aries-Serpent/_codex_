from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from codex.training import TrainCfg, run_custom_trainer


torch = pytest.importorskip("torch")


class _TinyDataset(torch.utils.data.Dataset):
    def __init__(self) -> None:
        self._inputs = torch.linspace(0.0, 1.0, steps=2, dtype=torch.float32).unsqueeze(-1)

    def __len__(self) -> int:
        return len(self._inputs)

    def __getitem__(self, index: int):  # type: ignore[override]
        x = self._inputs[index]
        y = x + 1.0
        mask = torch.ones_like(x)
        return {"input_ids": x.clone(), "attention_mask": mask, "labels": y.clone()}


class _TinyModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(1, 1)

    def forward(self, input_ids=None, attention_mask=None, labels=None):  # type: ignore[override]
        preds = self.linear(input_ids)
        loss = torch.nn.functional.mse_loss(preds, labels)
        return types.SimpleNamespace(loss=loss, logits=preds)


def test_run_custom_trainer_logs_metadata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "codex_ml.logging.run_metadata.current_commit", lambda: "cafebabe", raising=False
    )

    cfg = TrainCfg()
    cfg.epochs = 1
    cfg.batch_size = 1
    cfg.log_dir = str(tmp_path)
    cfg.checkpoint_dir = str(tmp_path / "checkpoints")
    cfg.deterministic = True
    cfg.log_system_metrics = False

    dataset = _TinyDataset()
    model = _TinyModel()

    monkeypatch.setattr(
        "training.functional_training._codex_logging_bootstrap", lambda *a, **k: {}, raising=False
    )
    monkeypatch.setattr(
        "training.functional_training._codex_log_all", lambda *a, **k: None, raising=False
    )

    run_custom_trainer(model, None, dataset, None, cfg)

    metrics_path = tmp_path / "metrics.ndjson"
    payloads = [
        json.loads(line)
        for line in metrics_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    metadata = payloads[0]
    assert metadata["phase"] == "metadata"
    assert metadata["git_commit"] == "cafebabe"
    assert metadata.get("train_examples") == len(dataset)
    assert metadata.get("log_formats") == ["ndjson"]
