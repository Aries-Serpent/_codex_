"""
Test Data Utils

Test module for data utils.
"""

import json
from pathlib import Path

from codex_ml.data_utils import split_dataset, stream_texts


def test_split_dataset_deterministic():
    texts = [f"sample-{i}" for i in range(10)]
    train1, val1 = split_dataset(texts, train_ratio=0.8, seed=123)
    train2, val2 = split_dataset(texts, train_ratio=0.8, seed=123)
    assert train1 == train2, "train1 is not valid"
    assert val1 == val2, "val1 is not valid"
    assert len(train1) == 8, "Train1 must not be empty"
    assert len(val1) == 2, "Val1 must not be empty"


def test_split_dataset_cache(tmp_path: Path):
    texts = [f"sample-{i}" for i in range(6)]
    cache = tmp_path / "split.json"
    train1, val1 = split_dataset(texts, train_ratio=0.5, seed=1, cache_path=cache)
    # Reusing with unchanged input should hit cache deterministically
    train2, val2 = split_dataset(texts, train_ratio=0.5, seed=1, cache_path=cache)
    assert (train1, val1) == (train2, val2)
    # Alter input; cache should be invalidated due to checksum mismatch
    texts[0] = "changed"
    train3, val3 = split_dataset(texts, train_ratio=0.5, seed=1, cache_path=cache)
    assert (train3, val3) != (train1, val1)
    assert cache.exists(), "Condition must be true"
    data = json.loads(cache.read_text())
    assert "checksum" in data, "Data must not be empty"


def test_stream_texts(tmp_path: Path):
    content = "HelloWorld"
    file_path = tmp_path / "data.txt"
    file_path.write_text(content)
    chunks = list(stream_texts(file_path, chunk_size=3))
    assert "".join(chunks) == content, "Content must not be empty"
    assert all(len(c) <= 3 for c in chunks), "C must not be empty"
