from pathlib import Path

from codex_ml.data_utils import split_dataset, stream_texts


def test_split_dataset_deterministic():
    texts = [f"sample-{i}" for i in range(10)]
    train1, val1 = split_dataset(texts, train_ratio=0.8, seed=123)
    train2, val2 = split_dataset(texts, train_ratio=0.8, seed=123)
    assert train1 == train2
    assert val1 == val2
    assert len(train1) == 8
    assert len(val1) == 2


def test_split_dataset_cache(tmp_path: Path):
    texts = [f"sample-{i}" for i in range(6)]
    cache = tmp_path / "split.json"
    train1, val1 = split_dataset(texts, train_ratio=0.5, seed=1, cache_path=cache)
    # Alter input; cache should be invalidated due to data hash mismatch
    texts[0] = "changed"
    train2, val2 = split_dataset(texts, train_ratio=0.5, seed=1, cache_path=cache)
    assert (train1, val1) != (train2, val2)
    assert cache.exists()


def test_stream_texts(tmp_path: Path):
    content = "HelloWorld"
    file_path = tmp_path / "data.txt"
    file_path.write_text(content)
    chunks = list(stream_texts(file_path, chunk_size=3))
    assert "".join(chunks) == content
    assert all(len(c) <= 3 for c in chunks)
