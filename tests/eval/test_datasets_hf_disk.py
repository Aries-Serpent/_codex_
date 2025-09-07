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


def test_load_datasetdict_default_and_split(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    dd = datasets.DatasetDict(
        {
            "train": datasets.Dataset.from_dict({"input": ["a"], "target": ["a"]}),
            "test": datasets.Dataset.from_dict({"input": ["b"], "target": ["b"]}),
        }
    )
    dd_path = tmp_path / "dd"
    dd.save_to_disk(dd_path)
    # default uses train
    examples = load_dataset(str(dd_path))
    assert examples == [Example("a", "a")]
    # explicit split
    test_examples = load_dataset(str(dd_path), split="test")
    assert test_examples == [Example("b", "b")]
    with pytest.raises(ValueError):
        load_dataset(str(dd_path), split="missing")
