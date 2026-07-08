"""Smoke tests for codex_ml CSV dataset loader."""

from __future__ import annotations

from pathlib import Path

from codex_ml.data.loaders.csv import load_csv_dataset


def test_load_csv_dataset(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("text,target\nhello,yes\nworld,no\n", encoding="utf-8")

    dataset = load_csv_dataset(
        csv_path, text_column="text", target_column="target", cache_dir=tmp_path / "cache"
    )
    assert "train" in dataset, "Data must not be empty"
    assert isinstance(dataset["train"], list)
    assert sum(len(v) for v in dataset.values()) == 2, "V must not be empty"
