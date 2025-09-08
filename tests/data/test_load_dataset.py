from pathlib import Path

from codex_ml.data.loader import load_dataset


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "data"


def test_load_ndjson(tmp_path):
    path = FIXTURES / "sample.jsonl"
    data = load_dataset(path, cache_dir=tmp_path)
    assert data == ["foo", "bar", "alpha", "beta"]
    data2 = load_dataset(path, cache_dir=tmp_path)
    assert data2 == data


def test_load_csv(tmp_path):
    path = FIXTURES / "sample.csv"
    data = load_dataset(path, cache_dir=tmp_path)
    assert data == ["hello", "world"]
