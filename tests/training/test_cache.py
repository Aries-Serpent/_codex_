"""Tests for src.training.cache module.

Phase 6 tests covering:
- TokenCache class
- Batch caching and flushing
- Manifest generation
- Batch iteration
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Guard numpy import
np = pytest.importorskip("numpy")


class TestTokenCache:
    """Tests for TokenCache class."""

    @pytest.fixture
    def cache(self, tmp_path):
        """Create a TokenCache instance."""
        from src.training.cache import TokenCache
        return TokenCache(out_dir=tmp_path, rows_per_shard=10)

    @pytest.fixture
    def sample_batch(self):
        """Create a sample batch for testing."""
        return {
            "input_ids": np.array([[1, 2, 3], [4, 5, 6]]),
            "attention_mask": np.array([[1, 1, 1], [1, 1, 0]]),
        }

    def test_cache_creation(self, cache, tmp_path):
        """Test TokenCache creates output directory."""
        assert cache.out_dir == tmp_path
        assert cache.out_dir.exists()

    def test_cache_creates_manifest(self, cache, tmp_path):
        """Test TokenCache creates manifest.json."""
        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.exists()

    def test_manifest_has_rows_per_shard(self, cache, tmp_path):
        """Test manifest contains rows_per_shard."""
        manifest_path = tmp_path / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        assert manifest["rows_per_shard"] == 10

    def test_add_batch_buffers_data(self, cache, sample_batch):
        """Test add_batch adds to buffer."""
        cache.add_batch(sample_batch)
        assert len(cache._buffer) == 1
        assert cache._buffer_rows == 2  # 2 rows in sample_batch

    def test_flush_creates_shard(self, cache, sample_batch, tmp_path):
        """Test flush creates shard file."""
        cache.add_batch(sample_batch)
        cache._flush()
        
        shard_path = tmp_path / "shard_00000.npz"
        assert shard_path.exists()

    def test_flush_updates_manifest(self, cache, sample_batch, tmp_path):
        """Test flush updates manifest with shard info."""
        cache.add_batch(sample_batch)
        cache._flush()
        
        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert len(manifest["shards"]) == 1
        assert manifest["shards"][0]["path"] == "shard_00000.npz"
        assert manifest["shards"][0]["rows"] == 2

    def test_flush_clears_buffer(self, cache, sample_batch):
        """Test flush clears buffer."""
        cache.add_batch(sample_batch)
        cache._flush()
        
        assert len(cache._buffer) == 0
        assert cache._buffer_rows == 0

    def test_auto_flush_at_threshold(self, cache, tmp_path):
        """Test auto-flush when buffer reaches rows_per_shard."""
        # Add batches until threshold
        for i in range(6):  # 6 * 2 = 12 rows > 10 threshold
            batch = {
                "input_ids": np.array([[i, i, i], [i+1, i+1, i+1]]),
            }
            cache.add_batch(batch)
        
        # Should have created at least one shard
        shard_path = tmp_path / "shard_00000.npz"
        assert shard_path.exists()

    def test_finalize_flushes_remaining(self, cache, sample_batch, tmp_path):
        """Test finalize flushes any remaining buffered data."""
        cache.add_batch(sample_batch)
        cache.finalize()
        
        shard_path = tmp_path / "shard_00000.npz"
        assert shard_path.exists()

    def test_finalize_on_empty_buffer(self, cache):
        """Test finalize with empty buffer does nothing."""
        cache.finalize()  # Should not raise

    def test_shard_incrementing(self, cache, tmp_path):
        """Test shard index increments."""
        for i in range(3):
            batch = {
                "input_ids": np.arange(15).reshape(5, 3),  # 5 rows
            }
            cache.add_batch(batch)
            cache.add_batch(batch)  # 10 rows total
        
        cache.finalize()
        
        # Should have multiple shards
        shards = list(tmp_path.glob("shard_*.npz"))
        assert len(shards) >= 2


class TestTokenCacheIterBatches:
    """Tests for TokenCache.iter_batches static method."""

    @pytest.fixture
    def populated_cache(self, tmp_path):
        """Create a cache with some data."""
        from src.training.cache import TokenCache
        
        cache = TokenCache(out_dir=tmp_path, rows_per_shard=5)
        
        batch = {
            "input_ids": np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
            "attention_mask": np.array([[1, 1, 1], [1, 1, 0], [1, 0, 0]]),
        }
        cache.add_batch(batch)
        cache.finalize()
        
        return tmp_path

    def test_iter_batches_yields_dicts(self, populated_cache):
        """Test iter_batches yields dictionaries."""
        from src.training.cache import TokenCache
        
        batches = list(TokenCache.iter_batches(populated_cache))
        assert len(batches) >= 1
        assert isinstance(batches[0], dict)

    def test_iter_batches_preserves_keys(self, populated_cache):
        """Test iter_batches preserves batch keys."""
        from src.training.cache import TokenCache
        
        batches = list(TokenCache.iter_batches(populated_cache))
        assert "input_ids" in batches[0]
        assert "attention_mask" in batches[0]

    def test_iter_batches_yields_numpy_arrays(self, populated_cache):
        """Test iter_batches yields numpy arrays."""
        from src.training.cache import TokenCache
        
        batches = list(TokenCache.iter_batches(populated_cache))
        assert isinstance(batches[0]["input_ids"], np.ndarray)

    def test_iter_batches_empty_cache(self, tmp_path):
        """Test iter_batches with empty cache."""
        from src.training.cache import TokenCache
        
        cache = TokenCache(out_dir=tmp_path, rows_per_shard=10)
        cache.finalize()
        
        batches = list(TokenCache.iter_batches(tmp_path))
        assert len(batches) == 0
