from pathlib import Path

import pytest

from codex_ml.config import DataConfig, ShardConfig
from codex_ml.data.loader import (
    CacheManifest,
    load_dataset,
    prepare_data_from_config,
    seeded_shuffle,
    stream_texts,
    take_n,
)


def test_stream_texts_newline_and_sharding(tmp_path: Path) -> None:
    path = tmp_path / "data.txt"
    path.write_text("a\r\nb\n\rc\n", encoding="utf-8")
    first = list(stream_texts(path, newline="unix", shard_index=0, shard_total=2))
    second = list(stream_texts(path, newline="unix", shard_index=1, shard_total=2))
    assert first == ["a", "c"]
    assert second == ["b"]


def test_load_dataset_creates_manifest(tmp_path: Path) -> None:
    path = tmp_path / "data.txt"
    path.write_text("x\ny\n", encoding="utf-8")
    cache_dir = tmp_path / "cache"
    data = load_dataset(path, cache_dir=cache_dir, newline="unix")
    assert data == ["x", "y"]
    manifests = list(cache_dir.glob("*.manifest.json"))
    assert manifests, "expected manifest file"
    manifest = CacheManifest.load(manifests[0])
    assert manifest is not None
    assert manifest.num_records == 2


def test_prepare_data_from_config(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.txt"
    dataset.write_text("\n".join(["a", "b", "c", "d", "e"]) + "\n", encoding="utf-8")
    cfg = DataConfig(
        source_path=str(dataset),
        cache_dir=str(tmp_path / "cache"),
        manifest_path=str(tmp_path / "cache" / "manifest.json"),
        split_ratios={"train": 0.6, "validation": 0.2, "test": 0.2},
        shuffle_seed=1,
        shard=ShardConfig(index=0, total=1),
    )
    result = prepare_data_from_config(cfg)
    assert Path(result["manifest"]).exists()
    splits = result["splits"]
    assert {"train", "validation", "test"} <= splits.keys()
    counts = {name: meta["count"] for name, meta in splits.items()}
    assert counts["train"] == 3
    assert counts["validation"] + counts["test"] == 2


def test_take_n_strict(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        take_n([], 1, strict=True)


@pytest.mark.parametrize("seed", [0, 1])
def test_seeded_shuffle_deterministic(seed: int) -> None:
    items = [1, 2, 3, 4]
    assert seeded_shuffle(items, seed) == seeded_shuffle(items, seed)
