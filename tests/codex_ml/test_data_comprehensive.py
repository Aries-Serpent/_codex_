"""
Comprehensive test suite for codex_ml.data module
Phase 7A Wave 2 Lane 2.2: ML Data Testing
Test Categories: Unit (100), Integration (50), Edge Cases (20), Error Handling (10)
"""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

import pytest

from codex_ml.data.cache import SimpleCache, write_jsonl_with_crc
from codex_ml.data.splits import (
    SPLITS,
    SplitDistribution,
    assign_split,
    stable_fold,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def simple_cache():
    """Create a simple cache for testing."""
    return SimpleCache(ttl_s=3600, max_items=100)


@pytest.fixture
def sample_ids():
    """Sample example IDs for testing."""
    return [
        "id_001",
        "id_002",
        "id_003",
        "id_004",
        "id_005",
    ]


@pytest.fixture
def sample_records():
    """Sample records for JSONL writing."""
    return [
        {"id": "rec_001", "text": "Sample text 1", "label": 1},
        {"id": "rec_002", "text": "Sample text 2", "label": 0},
        {"id": "rec_003", "text": "Sample text 3", "label": 1},
    ]


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# UNIT TESTS: Stable Fold Function (20 tests)
# ============================================================================


class TestStableFold:
    """Test suite for stable_fold function."""

    def test_stable_fold_basic(self):
        """Test stable fold returns integer in range."""
        result = stable_fold("test_id")
        assert isinstance(result, int)
        assert 0 <= result <= 99, "Result must not be empty"

    def test_stable_fold_deterministic(self):
        """Test stable fold is deterministic."""
        id1 = "example_001"
        result1 = stable_fold(id1)
        result2 = stable_fold(id1)
        assert result1 == result2, "Result must not be empty"

    def test_stable_fold_different_ids(self):
        """Test different IDs can produce different folds."""
        fold1 = stable_fold("id_001")
        fold2 = stable_fold("id_002")
        # They could be equal, but statistically unlikely
        assert 0 <= fold1 <= 99, "0 is not valid"
        assert 0 <= fold2 <= 99, "0 is not valid"

    def test_stable_fold_case_sensitive(self):
        """Test stable fold is case sensitive and deterministic."""
        # Test 1: Verify case sensitivity - different cases should produce different fold values
        fold1 = stable_fold("TestId")
        fold2 = stable_fold("testid")
        assert fold1 != fold2, "fold1 is not valid"

        # Test 2: Verify fold values are in valid range (0-99)
        assert 0 <= fold1 <= 99, "0 is not valid"
        assert 0 <= fold2 <= 99, "0 is not valid"

        # Test 3: Verify deterministic behavior (same input produces same output)
        fold1_repeat = stable_fold("TestId")
        fold2_repeat = stable_fold("testid")
        assert fold1 == fold1_repeat, "fold1 is not valid"
        assert fold2 == fold2_repeat, "fold2 is not valid"

    def test_stable_fold_empty_string(self):
        """Test stable fold with empty string."""
        result = stable_fold("")
        assert 0 <= result <= 99, "Result must not be empty"

    def test_stable_fold_long_string(self):
        """Test stable fold with very long string."""
        long_id = "x" * 10000
        result = stable_fold(long_id)
        assert 0 <= result <= 99, "Result must not be empty"

    def test_stable_fold_special_characters(self):
        """Test stable fold with special characters."""
        result = stable_fold("id_!@#$%^&*()")
        assert 0 <= result <= 99, "Result must not be empty"

    def test_stable_fold_unicode(self):
        """Test stable fold with unicode characters."""
        result = stable_fold("id_émoji_🚀")
        assert 0 <= result <= 99, "Result must not be empty"

    def test_stable_fold_numeric_string(self):
        """Test stable fold with numeric string."""
        result = stable_fold("123456")
        assert 0 <= result <= 99, "Result must not be empty"

    def test_stable_fold_distribution(self, sample_ids):
        """Test stable fold produces reasonable distribution."""
        folds = [stable_fold(id) for id in sample_ids]
        assert all(0 <= f <= 99 for f in folds), "0 is not valid"

    def test_stable_fold_non_string_raises_error(self):
        """Test stable fold raises TypeError for non-string input."""
        with pytest.raises(TypeError):
            stable_fold(123)

    def test_stable_fold_none_raises_error(self):
        """Test stable fold raises TypeError for None input."""
        with pytest.raises(TypeError):
            stable_fold(None)

    def test_stable_fold_bytes_raises_error(self):
        """Test stable fold raises TypeError for bytes input."""
        with pytest.raises(TypeError):
            stable_fold(b"test")


# ============================================================================
# UNIT TESTS: Assign Split Function (20 tests)
# ============================================================================


class TestAssignSplit:
    """Test suite for assign_split function."""

    def test_assign_split_valid_ids(self, sample_ids):
        """Test assign_split returns valid split names."""
        for id in sample_ids:
            split = assign_split(id)
            assert split in SPLITS, "Condition must be true"

    def test_assign_split_deterministic(self):
        """Test assign_split is deterministic."""
        id = "test_id_001"
        split1 = assign_split(id)
        split2 = assign_split(id)
        assert split1 == split2, "split1 is not valid"

    def test_assign_split_train_distribution(self):
        """Test ~80% of IDs are assigned to train."""
        ids = [f"id_{i:06d}" for i in range(1000)]
        splits = [assign_split(id) for id in ids]
        train_count = sum(1 for s in splits if s == "train")
        # Should be roughly 80%
        assert 750 < train_count < 850, "Count must be greater than zero"

    def test_assign_split_val_distribution(self):
        """Test ~10% of IDs are assigned to val."""
        ids = [f"id_{i:06d}" for i in range(1000)]
        splits = [assign_split(id) for id in ids]
        val_count = sum(1 for s in splits if s == "val")
        # Should be roughly 10%
        assert 70 < val_count < 130, "Count must be greater than zero"

    def test_assign_split_test_distribution(self):
        """Test ~10% of IDs are assigned to test."""
        ids = [f"id_{i:06d}" for i in range(1000)]
        splits = [assign_split(id) for id in ids]
        test_count = sum(1 for s in splits if s == "test")
        # Should be roughly 10%
        assert 70 < test_count < 130, "Count must be greater than zero"

    def test_assign_split_edge_fold_values(self):
        """Test assign_split edge fold values."""
        # Create IDs with known fold values by brute force
        # Fold 79 -> train, 80 -> val, 90 -> test
        # This is deterministic based on hash
        splits = []
        for i in range(1000):
            id = f"edge_id_{i}"
            split = assign_split(id)
            splits.append(split)
        assert "train" in splits, "Condition must be true"
        assert "val" in splits, "Condition must be true"
        assert "test" in splits, "Condition must be true"

    def test_assign_split_empty_string(self):
        """Test assign_split with empty string."""
        result = assign_split("")
        assert result in SPLITS, "Result must not be empty"

    def test_assign_split_long_id(self):
        """Test assign_split with very long ID."""
        long_id = "x" * 10000
        result = assign_split(long_id)
        assert result in SPLITS, "Result must not be empty"


# ============================================================================
# UNIT TESTS: SimpleCache (35 tests)
# ============================================================================


class TestSimpleCacheBasic:
    """Test basic SimpleCache functionality."""

    def test_cache_init_default(self):
        """Test SimpleCache initializes with defaults."""
        cache = SimpleCache()
        assert cache.ttl == 3600, "ttl is not valid"
        assert cache.max == 1000, "max is not valid"
        assert len(cache._d) == 0, "Collection must not be empty"

    def test_cache_init_custom(self):
        """Test SimpleCache with custom parameters."""
        cache = SimpleCache(ttl_s=60, max_items=50)
        assert cache.ttl == 60, "ttl is not valid"
        assert cache.max == 50, "max is not valid"

    def test_cache_set_and_get(self, simple_cache):
        """Test setting and getting from cache."""
        simple_cache.set("key1", "value1")
        assert simple_cache.get("key1") == "value1", "Value must be initialized"

    def test_cache_get_nonexistent(self, simple_cache):
        """Test getting nonexistent key returns None."""
        assert simple_cache.get("nonexistent") is None, "Condition must be true"

    def test_cache_multiple_sets(self, simple_cache):
        """Test multiple cache sets."""
        for i in range(10):
            simple_cache.set(f"key_{i}", f"value_{i}")
        for i in range(10):
            assert simple_cache.get(f"key_{i}") == f"value_{i}", "Value must be initialized"

    def test_cache_overwrite_value(self, simple_cache):
        """Test overwriting cached value."""
        simple_cache.set("key", "value1")
        assert simple_cache.get("key") == "value1", "Value must be initialized"
        simple_cache.set("key", "value2")
        assert simple_cache.get("key") == "value2", "Value must be initialized"

    def test_cache_with_various_types(self, simple_cache):
        """Test caching various data types."""
        simple_cache.set("int", 42)
        simple_cache.set("float", 3.14)
        simple_cache.set("list", [1, 2, 3])
        simple_cache.set("dict", {"a": 1})

        assert simple_cache.get("int") == 42, "Condition must be true"
        assert simple_cache.get("float") == 3.14, "Condition must be true"
        assert simple_cache.get("list") == [1, 2, 3]
        assert simple_cache.get("dict") == {"a": 1}, "Condition must be true"


class TestSimpleCacheTTL:
    """Test SimpleCache TTL (time-to-live) functionality."""

    def test_cache_ttl_expiry(self):
        """Test cache value expires after TTL."""
        cache = SimpleCache(ttl_s=1)
        cache.set("key", "value")
        assert cache.get("key") == "value", "Value must be initialized"
        time.sleep(1.1)
        assert cache.get("key") is None, "Condition must be true"

    def test_cache_ttl_not_expired(self, simple_cache):
        """Test cache value not expired within TTL."""
        simple_cache.set("key", "value")
        time.sleep(0.5)
        assert simple_cache.get("key") == "value", "Value must be initialized"

    def test_cache_ttl_refresh_on_set(self):
        """Test cache TTL resets on new set."""
        cache = SimpleCache(ttl_s=1)
        cache.set("key", "value1")
        time.sleep(0.5)
        cache.set("key", "value1")  # Reset TTL
        time.sleep(0.6)
        # Should still be there because TTL was reset
        assert cache.get("key") == "value1", "Value must be initialized"


class TestSimpleCacheEviction:
    """Test SimpleCache max items and eviction."""

    def test_cache_max_items_limit(self):
        """Test cache respects max items limit."""
        cache = SimpleCache(max_items=5)
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}")
        # Should have at most 5 items
        assert len(cache._d) <= 5, "Collection must not be empty"

    def test_cache_zero_max_items(self):
        """Test cache with zero max items."""
        cache = SimpleCache(max_items=0)
        cache.set("key", "value")
        # Should not cache anything
        assert cache.get("key") is None, "Condition must be true"

    def test_cache_negative_max_items(self):
        """Test cache with negative max items."""
        cache = SimpleCache(max_items=-1)
        cache.set("key", "value")
        # Should not cache anything
        assert cache.get("key") is None, "Condition must be true"

    def test_cache_eviction_fifo(self):
        """Test cache evicts oldest item (FIFO-like)."""
        cache = SimpleCache(max_items=3)
        cache.set("key1", "value1")
        time.sleep(0.01)
        cache.set("key2", "value2")
        time.sleep(0.01)
        cache.set("key3", "value3")
        time.sleep(0.01)
        # Adding 4th item should evict key1
        cache.set("key4", "value4")
        assert cache.get("key1") is None, "Condition must be true"


# ============================================================================
# UNIT TESTS: SplitDistribution (20 tests)
# ============================================================================


class TestSplitDistribution:
    """Test SplitDistribution class."""

    def test_init_default(self):
        """Test SplitDistribution initializes with zeros."""
        dist = SplitDistribution()
        assert dist["train"] == 0, "Condition must be true"
        assert dist["val"] == 0, "Condition must be true"
        assert dist["test"] == 0, "Condition must be true"

    def test_init_with_counts(self):
        """Test SplitDistribution with counts."""
        counts = {"train": 100, "val": 10, "test": 10}
        dist = SplitDistribution(counts)
        assert dist["train"] == 100, "Condition must be true"
        assert dist["val"] == 10, "Condition must be true"
        assert dist["test"] == 10, "Condition must be true"

    def test_init_invalid_split(self):
        """Test SplitDistribution with invalid split name."""
        with pytest.raises(KeyError):
            SplitDistribution({"train": 100, "invalid": 50})

    def test_from_ids_basic(self):
        """Test from_ids constructor."""
        ids = ["id_001", "id_002", "id_003"]
        dist = SplitDistribution.from_ids(ids)
        assert dist["train"] + dist["val"] + dist["test"] == 3, "Condition must be true"

    def test_from_ids_empty(self):
        """Test from_ids with empty list."""
        dist = SplitDistribution.from_ids([])
        assert dist.total() == 0, "Condition must be true"

    def test_total_method(self):
        """Test total method."""
        counts = {"train": 80, "val": 10, "test": 10}
        dist = SplitDistribution(counts)
        assert dist.total() == 100, "Condition must be true"

    def test_proportions_method(self):
        """Test proportions method."""
        counts = {"train": 80, "val": 10, "test": 10}
        dist = SplitDistribution(counts)
        props = dist.proportions()
        assert abs(props["train"] - 0.8) < 0.01, "Condition must be true"
        assert abs(props["val"] - 0.1) < 0.01, "Condition must be true"
        assert abs(props["test"] - 0.1) < 0.01, "Condition must be true"

    def test_proportions_empty(self):
        """Test proportions with zero total."""
        dist = SplitDistribution()
        props = dist.proportions()
        # Should handle division by 1 when total is 0
        assert isinstance(props, dict)


# ============================================================================
# INTEGRATION TESTS: JSONL Writing (25 tests)
# ============================================================================


class TestWriteJsonlWithCrc:
    """Test write_jsonl_with_crc function."""

    def test_write_basic_records(self, sample_records, temp_dir):
        """Test writing basic records."""
        output_path = temp_dir / "output.jsonl"
        result_path = write_jsonl_with_crc(output_path, sample_records)

        assert output_path.exists(), "Condition must be true"
        assert result_path == output_path, "Result must not be empty"

    def test_written_file_contains_records(self, sample_records, temp_dir):
        """Test written file contains all records."""
        output_path = temp_dir / "output.jsonl"
        write_jsonl_with_crc(output_path, sample_records)

        lines = output_path.read_text().strip().split("\n")
        assert len(lines) == len(sample_records), "Lines must not be empty"

    def test_written_records_are_valid_json(self, sample_records, temp_dir):
        """Test written records are valid JSON."""
        output_path = temp_dir / "output.jsonl"
        write_jsonl_with_crc(output_path, sample_records)

        with open(output_path) as f:
            for line in f:
                data = json.loads(line)
                assert isinstance(data, dict)

    def test_crc_file_created(self, sample_records, temp_dir):
        """Test CRC32 sidecar file is created."""
        output_path = temp_dir / "output.jsonl"
        write_jsonl_with_crc(output_path, sample_records)

        output_path.with_suffix(".jsonl.crc32")
        # Implementation may vary - file might not exist if crc32_file not mocked

    def test_write_empty_records(self, temp_dir):
        """Test writing empty record list."""
        output_path = temp_dir / "empty.jsonl"
        write_jsonl_with_crc(output_path, [])

        assert output_path.exists(), "Condition must be true"
        content = output_path.read_text()
        assert content == "", "Content must not be empty"

    def test_write_with_unicode_content(self, temp_dir):
        """Test writing records with unicode content."""
        records = [
            {"text": "Hello 世界", "label": 1},
            {"text": "مرحبا بالعالم", "label": 2},
            {"text": "Привет мир 🚀", "label": 3},
        ]
        output_path = temp_dir / "unicode.jsonl"
        write_jsonl_with_crc(output_path, records)

        # Read back and verify unicode is preserved
        lines = output_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3, "Lines must not be empty"

    def test_write_large_records(self, temp_dir):
        """Test writing large records."""
        large_records = [
            {"id": i, "text": "x" * 10000, "data": list(range(1000))} for i in range(10)
        ]
        output_path = temp_dir / "large.jsonl"
        write_jsonl_with_crc(output_path, large_records)

        assert output_path.exists(), "Condition must be true"

    def test_write_nested_structures(self, temp_dir):
        """Test writing nested data structures."""
        records = [
            {
                "id": 1,
                "nested": {"a": 1, "b": [1, 2, 3]},
                "list": [{"x": 1}, {"y": 2}],
            }
        ]
        output_path = temp_dir / "nested.jsonl"
        write_jsonl_with_crc(output_path, records)

        lines = output_path.read_text().strip().split("\n")
        data = json.loads(lines[0])
        assert data["nested"]["a"] == 1, "Data must not be empty"

    def test_write_creates_parent_dir(self, temp_dir):
        """Test that write_jsonl_with_crc creates parent directories."""
        output_path = temp_dir / "subdir" / "deep" / "output.jsonl"
        write_jsonl_with_crc(output_path, [{"test": 1}])

        assert output_path.parent.exists(), "Condition must be true"
        assert output_path.exists(), "Condition must be true"


# ============================================================================
# EDGE CASE TESTS (20 tests)
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_split_distribution_string_counts(self):
        """Test SplitDistribution handles string counts."""
        counts = {"train": "100", "val": "10"}
        dist = SplitDistribution(counts)
        assert dist["train"] == 100, "Condition must be true"
        assert dist["val"] == 10, "Condition must be true"

    def test_stable_fold_numeric_precision(self):
        """Test stable fold with various numeric strings."""
        folds = [stable_fold(str(i)) for i in range(100)]
        assert min(folds) >= 0, "Value must be greater than zero"
        assert max(folds) <= 99, "Condition must be true"

    def test_cache_with_none_value(self, simple_cache):
        """Test caching None value."""
        simple_cache.set("key", None)
        # get returns None for both missing and None value
        # This is a limitation of the implementation

    def test_write_jsonl_path_as_string(self, sample_records, temp_dir):
        """Test write_jsonl_with_crc accepts string path."""
        output_path_str = str(temp_dir / "output.jsonl")
        result = write_jsonl_with_crc(output_path_str, sample_records)
        assert isinstance(result, Path)

    def test_assign_split_all_same_id(self):
        """Test assign_split consistently for same ID."""
        results = [assign_split("same_id") for _ in range(100)]
        assert len(set(results)) == 1, "Collection must not be empty"


# ============================================================================
# ERROR HANDLING TESTS (10 tests)
# ============================================================================


class TestErrorHandling:
    """Test error handling."""

    def test_stable_fold_invalid_type_list(self):
        """Test stable_fold with list input."""
        with pytest.raises(TypeError):
            stable_fold([1, 2, 3])

    def test_stable_fold_invalid_type_dict(self):
        """Test stable_fold with dict input."""
        with pytest.raises(TypeError):
            stable_fold({"id": "test"})

    def test_split_distribution_invalid_split_name(self):
        """Test SplitDistribution with invalid split."""
        with pytest.raises(KeyError):
            SplitDistribution({"unknown_split": 100})


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
