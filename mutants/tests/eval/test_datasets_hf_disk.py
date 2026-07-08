"""
Test Datasets Hf Disk

Test module for datasets hf disk.
"""

from pathlib import Path

import pytest

pytest.importorskip("datasets")

from codex_ml.eval.datasets import DatasetBundle, Example, load_dataset


def test_load_dataset_from_datasetdict(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    train = datasets.Dataset.from_dict({"input": ["x"], "target": ["y"]})
    val = datasets.Dataset.from_dict({"input": ["v"], "target": ["w"]})
    ds = datasets.DatasetDict({"train": train, "validation": val})
    ds_path = tmp_path / "ds"
    ds.save_to_disk(ds_path)
    bundle = load_dataset(str(ds_path))  # nosec B615 - Local dataset file path (safe)
    assert isinstance(bundle, DatasetBundle)
    assert bundle.examples == [Example("x", "y")]
    assert len(bundle.dataset_hash) == 64, "Collection must not be empty"


def test_load_dataset_from_hf_disk_datasetdict(tmp_path: Path):
    datasets = pytest.importorskip("datasets")
    ds = datasets.DatasetDict(
        {
            "train": datasets.Dataset.from_dict({"input": ["a"], "target": ["b"]}),
            "test": datasets.Dataset.from_dict({"input": ["c"], "target": ["d"]}),
        }
    )
    ds_path = tmp_path / "dsdd"
    ds.save_to_disk(ds_path)
    train_examples = load_dataset(str(ds_path))  # nosec B615 - Local dataset file path (safe)
    assert isinstance(train_examples, DatasetBundle)
    assert train_examples.examples == [Example("a", "b")]
    assert len(train_examples.dataset_hash) == 64, "Collection must not be empty"
    test_examples = load_dataset(
        str(ds_path), hf_split="test"
    )  # nosec B615 - Local dataset file path (safe)
    assert isinstance(test_examples, DatasetBundle)
    assert test_examples.examples == [Example("c", "d")]
    assert len(test_examples.dataset_hash) == 64, "Collection must not be empty"
