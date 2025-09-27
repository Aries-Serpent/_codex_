from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

from codex_ml.training import run_functional_training

torch = pytest.importorskip("torch")


def test_minimal_loop_honours_gradient_accumulation(monkeypatch, tmp_path: Path) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):  # type: ignore[override]
        if name in {"datasets", "transformers"}:
            raise ImportError("forced optional dependency failure")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    step_calls = 0
    original_step = torch.optim.Adam.step

    def counting_step(self, *args, **kwargs):  # type: ignore[override]
        nonlocal step_calls
        step_calls += 1
        return original_step(self, *args, **kwargs)

    monkeypatch.setattr(torch.optim.Adam, "step", counting_step)

    metrics_path = tmp_path / "metrics.ndjson"

    config = {
        "seed": 0,
        "learning_rate": 1e-3,
        "batch_size": 1,
        "max_epochs": 1,
        "gradient_accumulation": 2,
        "eval_every_epochs": 1,
        "metrics_out": str(metrics_path),
        "dataset": {
            "train_texts": ["a b", "c d", "e f", "g h"],
            "eval_texts": ["i j"],
            "format": "jsonl",
        },
    }

    result = run_functional_training(config)

    assert step_calls == 2
    assert result["metrics"], "expected metrics to be returned"

    assert metrics_path.exists()
    payloads = [
        json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines() if line
    ]
    assert any(entry.get("phase") == "train" for entry in payloads)
    assert any(entry.get("phase") == "eval" for entry in payloads)
