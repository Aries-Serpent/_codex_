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

    # Default: prefer 'train' when available
    assert load_dataset(str(ds_path)) == [Example("x", "y")]

    # Explicit split selection
    assert load_dataset(str(ds_path), split="validation") == [Example("v", "w")]

    # Missing split raises with helpful message
    with pytest.raises(ValueError):
        load_dataset(str(ds_path), split="test")


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


def test_load_remote_dataset_selects_first_split(monkeypatch: pytest.MonkeyPatch):
    datasets = pytest.importorskip("datasets")
    dd = datasets.DatasetDict(
        {"validation": datasets.Dataset.from_dict({"input": ["v"], "target": ["v"]})}
    )

    class FakeBuilder:
        def __init__(self) -> None:
            self.info = SimpleNamespace(splits={"validation": None})

    def fake_load_dataset_builder(name_or_path):
        assert name_or_path == "dummy"
        return FakeBuilder()

    def fake_load_dataset(name_or_path, *, split=None):
        assert name_or_path == "dummy"
        assert split == "validation"
        return dd[split]

    monkeypatch.setattr(
        "codex_ml.eval.datasets.hf_load_dataset_builder", fake_load_dataset_builder
    )
    monkeypatch.setattr("codex_ml.eval.datasets.hf_load_dataset", fake_load_dataset)
    examples = load_dataset("dummy", split=None)
    assert examples == [Example("v", "v")]
