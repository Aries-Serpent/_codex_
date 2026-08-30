"""
Test Make Splits

Test module for make splits.
"""

from __future__ import annotations

import json

from codex_ml.data.make_splits import write_splits


def test_write_splits_creates_manifest(tmp_path):
    items = [f"item-{i}" for i in range(100)]
    out_dir = tmp_path / "splits"
    write_splits(items, out_dir, seed=123, ratios=(0.8, 0.1, 0.1), overwrite=True)

    train = (out_dir / "train.txt").read_text(encoding="utf-8").splitlines()
    val = (out_dir / "val.txt").read_text(encoding="utf-8").splitlines()
    test = (out_dir / "test.txt").read_text(encoding="utf-8").splitlines()

    assert len(train) + len(val) + len(test) == len(items), "Train must not be empty"

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["seed"] == 123, "Condition must be true"
    assert manifest["counts"]["train"] == len(train), "Train must not be empty"
    assert manifest["dataset_hash"], "Data must not be empty"
