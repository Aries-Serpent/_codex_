"""Smoke tests for codex_ml JSONL dataset loader."""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.data.loaders.jsonl import load_jsonl_dataset


def test_load_jsonl_dataset(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "sample.jsonl"
    records = [
        {"text": "alpha", "target": "A"},
        {"input": "beta", "target": "B"},
        {"text": "gamma", "input": "g", "target": "G"},
    ]
    jsonl_path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    dataset = load_jsonl_dataset(
        jsonl_path, cache_dir=tmp_path / "cache", split=(0.6, 0.2, 0.2), seed=1
    )
    assert set(dataset.keys()) == {"train", "val", "test"}
    assert sum(len(v) for v in dataset.values()) == 3, "V must not be empty"
