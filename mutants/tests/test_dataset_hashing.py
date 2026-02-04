"""
Test Dataset Hashing

Test module for dataset hashing.
"""

from pathlib import Path

from src.training.datasets import cache_texts, compute_dataset_hash


def test_compute_dataset_hash_stable():
    items = ["a", "b"]
    h1 = compute_dataset_hash(items)
    h2 = compute_dataset_hash(list(reversed(items))[::-1])
    assert h1 == h2


def test_cache_texts_writes_file(tmp_path: Path):
    items = ["hello", "world"]
    path = cache_texts(items, tmp_path, name="sample")
    assert path.exists()
    contents = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == len(items)
