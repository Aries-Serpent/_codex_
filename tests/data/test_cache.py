"""Tests for dataset caching utilities."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from codex_ml.data.cache import cache_records, derive_key, load_cached_records


def test_derive_key():
    """Test key derivation produces consistent hashes."""
    key1 = derive_key("dataset", "split", "seed")
    key2 = derive_key("dataset", "split", "seed")
    
    assert key1 == key2
    assert len(key1) == 16
    assert isinstance(key1, str)
    
    # Different inputs produce different keys
    key3 = derive_key("dataset", "split", "different")
    assert key3 != key1


def test_cache_roundtrip():
    """Test caching and loading records."""
    records = [
        {"text": "hello", "label": 0},
        {"text": "world", "label": 1},
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        key = derive_key("test_dataset", "train", "42")
        
        # Cache records
        path = cache_records(records, cache_dir=tmpdir, key=key)
        
        assert path.exists()
        assert path.name.endswith(".jsonl")
        assert path.parent == Path(tmpdir)
        
        # Load cached records
        loaded = load_cached_records(tmpdir, key)
        
        assert loaded is not None
        assert len(loaded) == 2
        assert loaded[0]["text"] == "hello"
        assert loaded[1]["label"] == 1


def test_load_cached_records_missing():
    """Test loading non-existent cache returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        key = derive_key("nonexistent", "test")
        loaded = load_cached_records(tmpdir, key)
        
        assert loaded is None


def test_cache_records_creates_directory():
    """Test cache_records creates cache directory if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "nested" / "cache"
        assert not cache_dir.exists()
        
        records = [{"text": "test"}]
        key = derive_key("test")
        
        path = cache_records(records, cache_dir=cache_dir, key=key)
        
        assert cache_dir.exists()
        assert path.exists()


def test_cache_empty_records():
    """Test caching empty list of records."""
    with tempfile.TemporaryDirectory() as tmpdir:
        key = derive_key("empty")
        path = cache_records([], cache_dir=tmpdir, key=key)
        
        assert path.exists()
        
        loaded = load_cached_records(tmpdir, key)
        assert loaded is not None
        assert len(loaded) == 0
