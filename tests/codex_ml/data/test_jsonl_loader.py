from __future__ import annotations

import json
from pathlib import Path

from codex_ml.data.jsonl_loader import load_jsonl


def _write_jsonl(path: Path) -> None:
    samples = [
        {"text": "hello"},
        "raw line",
        {"text": ["alpha", "beta"]},
        {"meta": "ignored"},
    ]
    with path.open("w", encoding="utf-8") as handle:
        for item in samples:
            if isinstance(item, str):
                handle.write(item + "\n")
            else:
                handle.write(json.dumps(item) + "\n")


def test_load_jsonl_split_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "dataset.jsonl"
    _write_jsonl(source)

    train_a, val_a = load_jsonl(source, seed=7, val_fraction=0.4)
    train_b, val_b = load_jsonl(source, seed=7, val_fraction=0.4)

    assert train_a == train_b
    assert val_a == val_b
    assert len(train_a) + len(val_a) == 5
    assert set(train_a).isdisjoint(set(val_a))


def test_load_jsonl_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    train, val = load_jsonl(missing)
    assert train == [] and val == []
