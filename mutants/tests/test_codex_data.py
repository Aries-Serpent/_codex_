"""
Test Codex Data

Test module for codex data.
"""

from pathlib import Path
import json

from codex_ml.codex_data import DataConfig, load_dataset


def test_load_dataset_deterministic(tmp_path: Path) -> None:
    data_path = tmp_path / "dataset.jsonl"
    records = [{"id": idx, "text": f"row-{idx}"} for idx in range(10)]
    data_path.write_text("\n".join([json.dumps(r) for r in records]), encoding="utf-8")

    cfg = DataConfig(dataset_path=data_path, seed=7, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2)
    first = load_dataset(cfg)
    second = load_dataset(cfg)

    assert first.train == second.train
    assert first.val == second.val
    assert first.test == second.test
    assert second.from_cache is True


def test_load_dataset_cache_hit(tmp_path: Path) -> None:
    data_path = tmp_path / "dataset.txt"
    data_path.write_text("\n".join([f"line-{i}" for i in range(12)]), encoding="utf-8")

    cfg = DataConfig(dataset_path=data_path, seed=1, cache_dir=tmp_path / "cache")
    first = load_dataset(cfg)
    cache_file = first.cache_path
    assert cache_file is not None and cache_file.exists()

    # Remove the source file to ensure the cache is used on subsequent calls
    data_path.unlink()
    cached = load_dataset(cfg)

    assert cached.from_cache is True
    assert cached.train == first.train
    assert cached.val == first.val
    assert cached.test == first.test
    assert cache_file.exists()


def test_load_dataset_invalidation_on_change(tmp_path: Path) -> None:
    data_path = tmp_path / "dataset.jsonl"
    initial_records = [{"id": idx, "text": f"row-{idx}"} for idx in range(5)]
    data_path.write_text("\n".join([json.dumps(r) for r in initial_records]), encoding="utf-8")

    cfg = DataConfig(dataset_path=data_path, cache_dir=tmp_path / "cache")
    first = load_dataset(cfg)
    assert first.cache_path is not None

    # Modify the dataset to force a checksum change
    updated_records = initial_records + [{"id": 99, "text": "new"}]
    data_path.write_text("\n".join([json.dumps(r) for r in updated_records]), encoding="utf-8")

    refreshed = load_dataset(cfg)
    assert refreshed.cache_path is not None
    assert refreshed.cache_path != first.cache_path
    assert refreshed.from_cache is False

    # Changing the loader version also invalidates the cache
    cfg.loader_version = "2.0"
    versioned = load_dataset(cfg)
    assert versioned.cache_path is not None
    assert versioned.cache_path != refreshed.cache_path
