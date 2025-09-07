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
