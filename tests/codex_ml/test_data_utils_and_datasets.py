"""
Test Data Utils And Datasets

Test module for data utils and datasets.
"""

from pathlib import Path

from codex_ml.data import datasets
from codex_ml.data import utils as data_utils


def test_deterministic_split_is_repeatable():
    ids = [f"id-{i}" for i in range(10)]
    cfg = data_utils.SplitConfig(fraction_train=0.6, seed=42)

    train1, eval1 = data_utils.deterministic_split_ids(ids, cfg)
    train2, eval2 = data_utils.deterministic_split_ids(ids, cfg)

    assert train1 == train2, "train1 is not valid"
    assert eval1 == eval2, "eval1 is not valid"
    assert set(train1).isdisjoint(set(eval1)), "Condition must be true"
    assert len(train1) + len(eval1) == len(ids), "Train1 must not be empty"


def test_assign_split_map_contains_all_ids():
    ids = [f"id-{i}" for i in range(5)]
    cfg = data_utils.SplitConfig(fraction_train=0.5, seed=1)
    mapping = data_utils.assign_split_map(ids, cfg)
    assert set(mapping.keys()) == set(ids), "Condition must be true"
    assert set(mapping.values()) <= {"train", "eval"}


def test_dataset_registry_default_datasets(tmp_path: Path, monkeypatch):
    # Redirect data root into tmp_path/data for isolation
    data_root = tmp_path / "data"
    (data_root / "dummy").mkdir(parents=True, exist_ok=True)
    (data_root / "dummy" / "sample.txt").write_text("line1\n\nline2\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    datasets.ensure_default_datasets(data_root=data_root)

    names = datasets.list_datasets()
    assert "dummy" in names, "Condition must be true"
    spec = datasets.get_dataset_spec("dummy")
    lines = list(spec.loader(spec.root))
    assert lines == ["line1", "line2"]
