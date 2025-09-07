from pathlib import Path

import pytest

from codex_ml.eval.datasets import Example, load_dataset


def test_load_dataset_from_datasetdict(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    train = datasets.Dataset.from_dict({"input": ["x"], "target": ["y"]})
    val = datasets.Dataset.from_dict({"input": ["v"], "target": ["w"]})
    ds = datasets.DatasetDict({"train": train, "validation": val})
    ds_path = tmp_path / "ds"
    ds.save_to_disk(ds_path)
    assert load_dataset(str(ds_path)) == [Example("x", "y")]
    assert load_dataset(str(ds_path), split="validation") == [Example("v", "w")]
    with pytest.raises(ValueError):
        load_dataset(str(ds_path), split="test")
