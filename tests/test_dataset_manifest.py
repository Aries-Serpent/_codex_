import json
from pathlib import Path

import pytest

from codex_ml.data.split_utils import split_dataset
from ingestion.utils import write_manifest


@pytest.mark.xfail(reason="write_manifest depends on git repo", strict=False)
def test_write_manifest(tmp_path: Path):
    path = write_manifest("sample", ["src"], 42, {"train": 10}, tmp_path)
    data = json.loads(path.read_text())
    assert data["name"] == "sample" and data["seed"] == 42
    assert "commit" in data


def test_split_dataset_writes_manifest(tmp_path: Path):
    dataset = tmp_path / "records.jsonl"
    dataset.write_text('{"x": 1}\n{"x": 2}\n{"x": 3}\n{"x": 4}\n', encoding="utf-8")

    splits = split_dataset(dataset, splits=(0.5, 0.25, 0.25), seed=13)
    manifest_path = dataset.parent / f"{dataset.name}.splits.checksum.json"
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {splits.train.name, splits.val.name, splits.test.name}
    assert expected.issubset(data.keys())
