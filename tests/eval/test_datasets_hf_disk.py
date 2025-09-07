from pathlib import Path
from types import SimpleNamespace

import pytest

from codex_ml.eval.datasets import Example, load_dataset


def test_load_dataset_from_datasetdict(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    train = datasets.Dataset.from_dict({"input": ["x"], "target": ["y"]})
    val = datasets.Dataset.from_dict({"input": ["v"], "target": ["w"]})
    ds = datasets.DatasetDict({"train": train, "validation": val})
    ds_path = tmp_path / "ds"
    ds.save_to_disk(ds_path)

    # Default: prefers 'train' when available
    assert load_dataset(str(ds_path)) == [Example("x", "y")]
    # Explicit split selection
    assert load_dataset(str(ds_path), split="validation") == [Example("v", "w")]
    # Missing split raises
    with pytest.raises(ValueError):
        load_dataset(str(ds_path), split="test")


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
    # Default uses train
    assert load_dataset(str(ds_path)) == [Example("a", "b")]
    # Explicit 'test' split
    assert load_dataset(str(ds_path), split="test") == [Example("c", "d")]
