import pytest

pytest.importorskip("mlflow")
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# """
# 
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# from functools import lru_cache
# 
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# 
# 
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# 
# 
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# 
# 
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# class TestStableChecksum:
# class TestStableChecksum:
#     """Tests for _stable_checksum_of_seq_repr function."""
#     def test_checksum_consistency(self):
#     def test_checksum_consistency(self):
#         """Test checksum is consistent across calls."""
#         seq = [1, 2, 3, "a", "b"]
#         result1 = data_utils._stable_checksum_of_seq_repr(seq)
#         result2 = data_utils._stable_checksum_of_seq_repr(seq)
# 
#         assert result1 == result2, "Result must not be empty"
# 
#     def test_checksum_different_for_different_sequences(self):
#     def test_checksum_different_for_different_sequences(self):
#         """Test different sequences produce different checksums."""
#         seq1 = [1, 2, 3]
#         seq2 = [1, 2, 4]
#         assert data_utils._stable_checksum_of_seq_repr(, "Data must not be empty"
#             seq1
#         ) != data_utils._stable_checksum_of_seq_repr(seq2)
# 
#     def test_checksum_empty_sequence(self):
#     def test_checksum_empty_sequence(self):
#         """Test checksum for empty sequence."""
#         result = data_utils._stable_checksum_of_seq_repr([])
#         assert isinstance(result, str)
#         assert len(result) == 64, "Result must not be empty"


class TestSplitDataset:
    """Tests for split_dataset function."""

    def test_basic_split_sequence(self):
        """Test basic split of a sequence."""
        items = list(range(100))
        train, val = data_utils.split_dataset(items, train_ratio=0.8, seed=42)

        assert len(train) == 80, "Train must not be empty"
        assert len(val) == 20, "Val must not be empty"
        assert len(set(train) | set(val)) == 100, "Collection must not be empty"

    def test_basic_split_mapping(self):
        """Test split of a mapping."""
        items = {f"key_{i}": i for i in range(100)}
        train, val = data_utils.split_dataset(items, train_ratio=0.9, seed=42)

        assert len(train) == 90, "Train must not be empty"
        assert len(val) == 10, "Val must not be empty"

    def test_split_determinism(self):
        """Test split is deterministic with same seed."""
        items = list(range(50))

        train1, val1 = data_utils.split_dataset(items, train_ratio=0.8, seed=123)
        train2, val2 = data_utils.split_dataset(items, train_ratio=0.8, seed=123)

        assert train1 == train2, "train1 is not valid"
        assert val1 == val2, "val1 is not valid"

    def test_split_different_seeds(self):
        """Test different seeds produce different splits."""
        items = list(range(50))

        train1, _ = data_utils.split_dataset(items, train_ratio=0.8, seed=1)
        train2, _ = data_utils.split_dataset(items, train_ratio=0.8, seed=2)

        # Different seeds should produce different orderings
        assert train1 != train2, "train1 is not valid"

    def test_split_empty_sequence(self):
        """Test split of empty sequence."""
        train, val = data_utils.split_dataset([], train_ratio=0.8, seed=42)

        assert train == [], "train is not valid"
        assert val == [], "val is not valid"

    def test_split_ratio_zero(self):
        """Test split with zero train ratio."""
        items = list(range(10))
        train, val = data_utils.split_dataset(items, train_ratio=0.0, seed=42)

        assert len(train) == 0, "Train must not be empty"
        assert len(val) == 10, "Val must not be empty"

    def test_split_ratio_one(self):
        """Test split with train ratio of 1.0."""
        items = list(range(10))
        train, val = data_utils.split_dataset(items, train_ratio=1.0, seed=42)

        assert len(train) == 10, "Train must not be empty"
        assert len(val) == 0, "Val must not be empty"

    def test_split_invalid_ratio_negative(self):
        """Test split with invalid negative ratio."""
        with pytest.raises(ValueError, match="train_ratio must be within"):
            data_utils.split_dataset([1, 2, 3], train_ratio=-0.1, seed=42)

    def test_split_invalid_ratio_greater_than_one(self):
        """Test split with invalid ratio > 1."""
        with pytest.raises(ValueError, match="train_ratio must be within"):
            data_utils.split_dataset([1, 2, 3], train_ratio=1.1, seed=42)

    def test_split_with_cache(self):
        """Test split with cache persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "split_cache.json"
            items = list(range(20))

            # First call - creates cache
            train1, val1 = data_utils.split_dataset(
                items, train_ratio=0.8, seed=42, cache_path=cache_path
            )

            assert cache_path.exists(), "Condition must be true"

            # Second call - uses cache
            train2, val2 = data_utils.split_dataset(
                items, train_ratio=0.8, seed=42, cache_path=cache_path
            )

            assert train1 == train2, "train1 is not valid"
            assert val1 == val2, "val1 is not valid"

            # Verify cache structure
            cache_data = json.loads(cache_path.read_text())
            assert "length" in cache_data, "Data must not be empty"
            assert "seed" in cache_data, "Data must not be empty"
            assert "train_ratio" in cache_data, "Data must not be empty"
            assert "train_idx" in cache_data, "Data must not be empty"
            assert "val_idx" in cache_data, "Data must not be empty"

    def test_split_cache_invalidated_by_length(self):
        """Test cache is invalidated when data length changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "split_cache.json"

            # First call with 20 items
            items1 = list(range(20))
            train1, _val1 = data_utils.split_dataset(
                items1, train_ratio=0.8, seed=42, cache_path=cache_path
            )

            # Second call with different length - cache should be invalidated
            items2 = list(range(30))
            train2, _val2 = data_utils.split_dataset(
                items2, train_ratio=0.8, seed=42, cache_path=cache_path
            )

            assert len(train1) == 16, "Train1 must not be empty"
            assert len(train2) == 24, "Train2 must not be empty"


class TestSplitTexts:
    """Tests for split_texts function."""

    def test_basic_text_split(self):
        """Test basic split of text items."""
        texts = [f"text_{i}" for i in range(100)]
        train, val = data_utils.split_texts(texts, train_ratio=0.8, seed=42)

        assert len(train) == 80, "Train must not be empty"
        assert len(val) == 20, "Val must not be empty"
        assert all(isinstance(t, str) for t in train)
        assert all(isinstance(t, str) for t in val)

    def test_text_split_determinism(self):
        """Test text split is deterministic."""
        texts = ["hello", "world", "test", "data", "sample"]

        train1, val1 = data_utils.split_texts(texts, train_ratio=0.8, seed=123)
        train2, val2 = data_utils.split_texts(texts, train_ratio=0.8, seed=123)

        assert train1 == train2, "train1 is not valid"
        assert val1 == val2, "val1 is not valid"


class TestDeterministicShuffle:
    """Tests for deterministic_shuffle fallback."""

    def test_shuffle_determinism(self):
        """Test fallback shuffle is deterministic."""
        items = list(range(20))

        result1 = data_utils.deterministic_shuffle(items, seed=42)
        result2 = data_utils.deterministic_shuffle(items, seed=42)

        assert result1 == result2, "Result must not be empty"

    def test_shuffle_different_seeds(self):
        """Test different seeds produce different orders."""
        items = list(range(20))

        result1 = data_utils.deterministic_shuffle(items, seed=1)
        result2 = data_utils.deterministic_shuffle(items, seed=2)

        assert result1 != result2, "Result must not be empty"

    def test_shuffle_preserves_elements(self):
        """Test shuffle preserves all elements."""
        items = [1, 2, 3, 4, 5]
        result = data_utils.deterministic_shuffle(items, seed=42)

        assert sorted(result) == sorted(items), "Result must not be empty"


class TestRequireTorch:
    """Tests for _require_torch helper."""

    def test_require_torch_when_available(self):
        """Test _require_torch passes when torch is available."""
        try:
            # Should not raise
            data_utils._require_torch()
        except ModuleNotFoundError:
            pytest.skip("torch not available")

    @patch("training.data_utils.torch", None)
    def test_require_torch_when_unavailable(self):
        """Test _require_torch raises when torch is unavailable."""
        with pytest.raises(ModuleNotFoundError, match="torch is required"):
            data_utils._require_torch()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_split_single_item(self):
        """Test split with single item."""
        items = [42]
        train, val = data_utils.split_dataset(items, train_ratio=0.5, seed=42)

        # With one item and 0.5 ratio, we get 0 train items
        assert len(train) + len(val) == 1, "Train must not be empty"

    def test_split_preserves_types(self):
        """Test split preserves item types."""

        class CustomItem:
            def __init__(self, value):
                self.value = value

        items = [CustomItem(i) for i in range(10)]
        train, val = data_utils.split_dataset(items, train_ratio=0.8, seed=42)

        assert all(isinstance(item, CustomItem) for item in train)
        assert all(isinstance(item, CustomItem) for item in val)

    def test_split_with_strings(self):
        """Test split with string items."""
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        train, val = data_utils.split_dataset(items, train_ratio=0.8, seed=42)

        assert len(train) == 4, "Train must not be empty"
        assert len(val) == 1, "Val must not be empty"
        assert all(isinstance(item, str) for item in train + val)
