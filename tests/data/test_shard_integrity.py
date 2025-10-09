from __future__ import annotations

from pathlib import Path

import pytest

from src.data.manifest import DatasetManifest


def test_manifest_build_write_load_verify(tmp_path: Path):
    # Create shards
    (tmp_path / "data").mkdir()
    shard1 = tmp_path / "data" / "a.txt"
    shard2 = tmp_path / "data" / "b.txt"
    shard1.write_text("hello", encoding="utf-8")
    shard2.write_text("world", encoding="utf-8")

    rels = ["data/a.txt", "data/b.txt"]
    man = DatasetManifest.build(tmp_path, rels)
    out = tmp_path / "manifest.json"
    man.write(out)

    man2 = DatasetManifest.load(out)
    # Verify ok
    man2.verify(tmp_path)

    # Mutate a shard to trigger mismatch
    shard2.write_text("world!", encoding="utf-8")
    with pytest.raises(ValueError):
        man2.verify(tmp_path)