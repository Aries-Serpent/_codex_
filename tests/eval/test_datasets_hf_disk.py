from pathlib import Path

import pytest

from codex_ml.eval.datasets import Example, load_dataset


def test_load_dataset_from_hf_disk(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    ds = datasets.Dataset.from_dict({"input": ["x"], "target": ["y"]})
    ds_path = tmp_path / "ds"
    ds.save_to_disk(ds_path)
    examples = load_dataset(str(ds_path))
    assert examples == [Example("x", "y")]


def test_load_dataset_from_hf_disk_datasetdict(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    ds = datasets.DatasetDict(
        {
            "train": datasets.Dataset.from_dict({"input": ["a"], "target": ["b"]}),
            "test": datasets.Dataset.from_dict({"input": ["c"], "target": ["d"]}),
        }
    )
    ds_path = tmp_path / "dsdict"
    ds.save_to_disk(ds_path)
    assert load_dataset(str(ds_path)) == [Example("a", "b")]
    assert load_dataset(str(ds_path), split="test") == [Example("c", "d")]
