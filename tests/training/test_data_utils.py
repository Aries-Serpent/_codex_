"""
Tests for training.data_utils module.

This module contains tests for data splitting, shuffling, and dataset utilities.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestStableChecksum:
    """Tests for _stable_checksum_of_seq_repr function."""

    def test_checksum_consistency(self):
        """Test checksum is consistent across calls."""
        from training.data_utils import _stable_checksum_of_seq_repr
        
        seq = [1, 2, 3, "a", "b"]
        
        result1 = _stable_checksum_of_seq_repr(seq)
        result2 = _stable_checksum_of_seq_repr(seq)
        
        assert result1 == result2

    def test_checksum_different_for_different_sequences(self):
        """Test different sequences produce different checksums."""
        from training.data_utils import _stable_checksum_of_seq_repr
        
        seq1 = [1, 2, 3]
        seq2 = [1, 2, 4]
        
        assert _stable_checksum_of_seq_repr(seq1) != _stable_checksum_of_seq_repr(seq2)

    def test_checksum_empty_sequence(self):
        """Test checksum for empty sequence."""
        from training.data_utils import _stable_checksum_of_seq_repr
        
        result = _stable_checksum_of_seq_repr([])
        
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest length


class TestSplitDataset:
    """Tests for split_dataset function."""

    def test_basic_split_sequence(self):
        """Test basic split of a sequence."""
        from training.data_utils import split_dataset
        
        items = list(range(100))
        train, val = split_dataset(items, train_ratio=0.8, seed=42)
        
        assert len(train) == 80
        assert len(val) == 20
        assert len(set(train) | set(val)) == 100  # No overlap

    def test_basic_split_mapping(self):
        """Test split of a mapping."""
        from training.data_utils import split_dataset
        
        items = {f"key_{i}": i for i in range(100)}
        train, val = split_dataset(items, train_ratio=0.9, seed=42)
        
        assert len(train) == 90
        assert len(val) == 10

    def test_split_determinism(self):
        """Test split is deterministic with same seed."""
        from training.data_utils import split_dataset
        
        items = list(range(50))
        
        train1, val1 = split_dataset(items, train_ratio=0.8, seed=123)
        train2, val2 = split_dataset(items, train_ratio=0.8, seed=123)
        
        assert train1 == train2
        assert val1 == val2

    def test_split_different_seeds(self):
        """Test different seeds produce different splits."""
        from training.data_utils import split_dataset
        
        items = list(range(50))
        
        train1, _ = split_dataset(items, train_ratio=0.8, seed=1)
        train2, _ = split_dataset(items, train_ratio=0.8, seed=2)
        
        # Different seeds should produce different orderings
        assert train1 != train2

    def test_split_empty_sequence(self):
        """Test split of empty sequence."""
        from training.data_utils import split_dataset
        
        train, val = split_dataset([], train_ratio=0.8, seed=42)
        
        assert train == []
        assert val == []

    def test_split_ratio_zero(self):
        """Test split with zero train ratio."""
        from training.data_utils import split_dataset
        
        items = list(range(10))
        train, val = split_dataset(items, train_ratio=0.0, seed=42)
        
        assert len(train) == 0
        assert len(val) == 10

    def test_split_ratio_one(self):
        """Test split with train ratio of 1.0."""
        from training.data_utils import split_dataset
        
        items = list(range(10))
        train, val = split_dataset(items, train_ratio=1.0, seed=42)
        
        assert len(train) == 10
        assert len(val) == 0

    def test_split_invalid_ratio_negative(self):
        """Test split with invalid negative ratio."""
        from training.data_utils import split_dataset
        
        with pytest.raises(ValueError, match="train_ratio must be within"):
            split_dataset([1, 2, 3], train_ratio=-0.1, seed=42)

    def test_split_invalid_ratio_greater_than_one(self):
        """Test split with invalid ratio > 1."""
        from training.data_utils import split_dataset
        
        with pytest.raises(ValueError, match="train_ratio must be within"):
            split_dataset([1, 2, 3], train_ratio=1.1, seed=42)

    def test_split_with_cache(self):
        """Test split with cache persistence."""
        from training.data_utils import split_dataset
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "split_cache.json"
            items = list(range(20))
            
            # First call - creates cache
            train1, val1 = split_dataset(items, train_ratio=0.8, seed=42, cache_path=cache_path)
            
            assert cache_path.exists()
            
            # Second call - uses cache
            train2, val2 = split_dataset(items, train_ratio=0.8, seed=42, cache_path=cache_path)
            
            assert train1 == train2
            assert val1 == val2
            
            # Verify cache structure
            cache_data = json.loads(cache_path.read_text())
            assert "length" in cache_data
            assert "seed" in cache_data
            assert "train_ratio" in cache_data
            assert "train_idx" in cache_data
            assert "val_idx" in cache_data

    def test_split_cache_invalidated_by_length(self):
        """Test cache is invalidated when data length changes."""
        from training.data_utils import split_dataset
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "split_cache.json"
            
            # First call with 20 items
            items1 = list(range(20))
            train1, val1 = split_dataset(items1, train_ratio=0.8, seed=42, cache_path=cache_path)
            
            # Second call with different length - cache should be invalidated
            items2 = list(range(30))
            train2, val2 = split_dataset(items2, train_ratio=0.8, seed=42, cache_path=cache_path)
            
            assert len(train1) == 16
            assert len(train2) == 24  # New split, not from cache


class TestSplitTexts:
    """Tests for split_texts function."""

    def test_basic_text_split(self):
        """Test basic split of text items."""
        from training.data_utils import split_texts
        
        texts = [f"text_{i}" for i in range(100)]
        train, val = split_texts(texts, train_ratio=0.8, seed=42)
        
        assert len(train) == 80
        assert len(val) == 20
        assert all(isinstance(t, str) for t in train)
        assert all(isinstance(t, str) for t in val)

    def test_text_split_determinism(self):
        """Test text split is deterministic."""
        from training.data_utils import split_texts
        
        texts = ["hello", "world", "test", "data", "sample"]
        
        train1, val1 = split_texts(texts, train_ratio=0.8, seed=123)
        train2, val2 = split_texts(texts, train_ratio=0.8, seed=123)
        
        assert train1 == train2
        assert val1 == val2


class TestDeterministicShuffle:
    """Tests for deterministic_shuffle fallback."""

    def test_shuffle_determinism(self):
        """Test fallback shuffle is deterministic."""
        from training.data_utils import deterministic_shuffle
        
        items = list(range(20))
        
        result1 = deterministic_shuffle(items, seed=42)
        result2 = deterministic_shuffle(items, seed=42)
        
        assert result1 == result2

    def test_shuffle_different_seeds(self):
        """Test different seeds produce different orders."""
        from training.data_utils import deterministic_shuffle
        
        items = list(range(20))
        
        result1 = deterministic_shuffle(items, seed=1)
        result2 = deterministic_shuffle(items, seed=2)
        
        assert result1 != result2

    def test_shuffle_preserves_elements(self):
        """Test shuffle preserves all elements."""
        from training.data_utils import deterministic_shuffle
        
        items = [1, 2, 3, 4, 5]
        result = deterministic_shuffle(items, seed=42)
        
        assert sorted(result) == sorted(items)


class TestRequireTorch:
    """Tests for _require_torch helper."""

    def test_require_torch_when_available(self):
        """Test _require_torch passes when torch is available."""
        try:
            import torch
            from training.data_utils import _require_torch
            
            # Should not raise
            _require_torch()
        except ModuleNotFoundError:
            pytest.skip("torch not available")

    @patch('training.data_utils.torch', None)
    def test_require_torch_when_unavailable(self):
        """Test _require_torch raises when torch is unavailable."""
        # Re-import to get patched version
        import importlib
        import training.data_utils
        importlib.reload(training.data_utils)
        
        if training.data_utils.torch is None:
            with pytest.raises(ModuleNotFoundError, match="torch is required"):
                training.data_utils._require_torch()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_split_single_item(self):
        """Test split with single item."""
        from training.data_utils import split_dataset
        
        items = [42]
        train, val = split_dataset(items, train_ratio=0.5, seed=42)
        
        # With one item and 0.5 ratio, we get 0 train items
        assert len(train) + len(val) == 1

    def test_split_preserves_types(self):
        """Test split preserves item types."""
        from training.data_utils import split_dataset
        
        class CustomItem:
            def __init__(self, value):
                self.value = value
        
        items = [CustomItem(i) for i in range(10)]
        train, val = split_dataset(items, train_ratio=0.8, seed=42)
        
        assert all(isinstance(item, CustomItem) for item in train)
        assert all(isinstance(item, CustomItem) for item in val)

    def test_split_with_strings(self):
        """Test split with string items."""
        from training.data_utils import split_dataset
        
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        train, val = split_dataset(items, train_ratio=0.8, seed=42)
        
        assert len(train) == 4
        assert len(val) == 1
        assert all(isinstance(item, str) for item in train + val)
