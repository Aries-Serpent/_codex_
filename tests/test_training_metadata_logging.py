from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

from codex_ml.training import run_functional_training


torch = pytest.importorskip("torch")


def test_run_functional_training_records_metadata(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):  # type: ignore[override]
        if name in {"datasets", "transformers"}:
            raise ImportError("forced optional dependency failure")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(
        "codex_ml.logging.run_metadata.current_commit", lambda: "deadbeef", raising=False
    )

    metrics_path = tmp_path / "metrics.ndjson"
    config = {
        "seed": 123,
        "learning_rate": 1e-3,
        "batch_size": 1,
        "max_epochs": 1,
        "gradient_accumulation": 1,
        "metrics_out": str(metrics_path),
        "dataset": {
            "train_texts": ["alpha beta", "gamma delta"],
            "eval_texts": ["epsilon zeta"],
            "format": "jsonl",
        },
    }

    run_functional_training(config)

    lines = [
        json.loads(line)
        for line in metrics_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    metadata = lines[0]
    assert metadata["phase"] == "metadata"
    assert metadata["git_commit"] == "deadbeef"
    assert metadata["seed"] == 123
    assert metadata.get("train_examples") == 2
    assert metadata.get("eval_examples") in {0, 1}
    assert metadata.get("log_formats") == ["ndjson"]
    assert "datasets" in metadata.get("missing_optional", [])
    assert "transformers" in metadata.get("missing_optional", [])
