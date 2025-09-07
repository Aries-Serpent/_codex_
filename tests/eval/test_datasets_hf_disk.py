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
    examples = load_dataset(str(ds_path))
    assert examples == [Example("x", "y")]


def test_load_dataset_from_hf_disk_datasetdict(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    dd = datasets.DatasetDict(
        {
            "train": datasets.Dataset.from_dict({"input": ["a"], "target": ["b"]}),
            "test": datasets.Dataset.from_dict({"input": ["c"], "target": ["d"]}),
        }
    )
    ds_path = tmp_path / "dsdd"
    dd.save_to_disk(ds_path)
    train_examples = load_dataset(str(ds_path))
    assert train_examples == [Example("a", "b")]
    test_examples = load_dataset(str(ds_path), hf_split="test")
    assert test_examples == [Example("c", "d")]
