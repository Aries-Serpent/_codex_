from pathlib import Path

from codex_ml.data.loader import load_dataset


def test_load_ndjson(tmp_path):
    src = Path("tests/fixtures/data/sample.jsonl")
    data1 = load_dataset(src, cache_dir=tmp_path)
    assert data1 == ["alpha", "beta"]
    # second call should load from cache
    data2 = load_dataset(src, cache_dir=tmp_path)
    assert data1 == data2


def test_load_csv(tmp_path):
    src = Path("tests/fixtures/data/sample.csv")
    data = load_dataset(src, cache_dir=tmp_path)
    assert data == ["hello", "world"]
