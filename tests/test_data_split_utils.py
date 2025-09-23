from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.data.split_utils import SplitPaths, split_dataset


def _write_jsonl_proper(path: Path, count: int) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for i in range(count):
            handle.write(json.dumps({"prompt": f"p{i}", "completion": f"c{i}"}) + "\n")


def test_split_dataset_shapes(tmp_path: Path) -> None:
    source = tmp_path / "data.jsonl"
    _write_jsonl_proper(source, 20)
    splits = split_dataset(source, (0.7, 0.2, 0.1), seed=123)
    assert isinstance(splits, SplitPaths)
    assert splits.train.exists()
    assert splits.val.exists()
    assert splits.test.exists()
    train_lines = splits.train.read_text().strip().splitlines()
    val_lines = splits.val.read_text().strip().splitlines()
    test_lines = splits.test.read_text().strip().splitlines()
    assert len(train_lines) == 14
    assert len(val_lines) == 4
    assert len(test_lines) == 2
    all_lines = train_lines + val_lines + test_lines
    assert len(set(all_lines)) == len(all_lines)


def test_split_dataset_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "dataset.jsonl"
    _write_jsonl_proper(source, 12)
    first = split_dataset(source, (0.6, 0.2, 0.2), seed=7)
    second = split_dataset(source, (0.6, 0.2, 0.2), seed=7)
    assert first.train.read_text() == second.train.read_text()
    assert first.val.read_text() == second.val.read_text()
    assert first.test.read_text() == second.test.read_text()


def test_split_dataset_invalid_ratio(tmp_path: Path) -> None:
    source = tmp_path / "data.jsonl"
    _write_jsonl_proper(source, 5)
    with pytest.raises(ValueError):
        split_dataset(source, (0.5, 0.5, 0.5))
    with pytest.raises(ValueError):
        split_dataset(source, (0.9, 0.1, 0.0), seed=1)
