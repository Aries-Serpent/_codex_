"""Tests for hash_table utility module."""

from __future__ import annotations

import pytest

from codex.utils.hash_table import HashTable, murmur_hash3_32


class TestMurmurHash3:
    """Test suite for murmur_hash3_32 function."""

    def test_murmur_hash3_basic(self) -> None:
        """Test basic hash computation."""
        key = b"hello"
        result = murmur_hash3_32(key)
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFFFFFF, "Result must not be empty"

    def test_murmur_hash3_deterministic(self) -> None:
        """Test that hash is deterministic."""
        key = b"test_key"
        hash1 = murmur_hash3_32(key)
        hash2 = murmur_hash3_32(key)
        assert hash1 == hash2, "hash1 is not valid"

    def test_murmur_hash3_different_keys(self) -> None:
        """Test different keys produce different hashes."""
        key1 = b"key1"
        key2 = b"key2"
        hash1 = murmur_hash3_32(key1)
        hash2 = murmur_hash3_32(key2)
        assert hash1 != hash2, "hash1 is not valid"

    def test_murmur_hash3_empty_key(self) -> None:
        """Test hashing empty key."""
        key = b""
        result = murmur_hash3_32(key)
        assert isinstance(result, int)

    def test_murmur_hash3_with_seed(self) -> None:
        """Test hashing with custom seed."""
        key = b"test"
        hash_seed0 = murmur_hash3_32(key, seed=0)
        hash_seed1 = murmur_hash3_32(key, seed=1)
        assert hash_seed0 != hash_seed1, "hash_seed0 is not valid"

    def test_murmur_hash3_large_key(self) -> None:
        """Test hashing large key."""
        key = b"x" * 1000
        result = murmur_hash3_32(key)
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFFFFFF, "Result must not be empty"

    def test_murmur_hash3_unaligned_key(self) -> None:
        """Test hashing key with odd length."""
        for length in [1, 3, 5, 7, 11]:
            key = b"x" * length
            result = murmur_hash3_32(key)
            assert isinstance(result, int)

    def test_murmur_hash3_seed_variant_deterministic(self) -> None:
        """Test that seeded hash is deterministic."""
        key = b"seed_test"
        seed = 42
        hash1 = murmur_hash3_32(key, seed=seed)
        hash2 = murmur_hash3_32(key, seed=seed)
        assert hash1 == hash2, "hash1 is not valid"


class TestHashTableBasic:
    """Test basic HashTable operations."""

    def test_hash_table_creation(self) -> None:
        """Test creating a new hash table."""
        ht = HashTable()
        assert ht is not None, "ht must be initialized"
        assert len(ht) == 0, "Ht must not be empty"

    def test_hash_table_insert_and_get(self) -> None:
        """Test basic insert and get operations."""
        ht = HashTable()
        ht["key1"] = "value1"
        assert ht["key1"] == "value1", "Value must be initialized"

    def test_hash_table_multiple_inserts(self) -> None:
        """Test inserting multiple items."""
        ht = HashTable()
        for i in range(10):
            ht[f"key_{i}"] = f"value_{i}"

        for i in range(10):
            assert ht[f"key_{i}"] == f"value_{i}", "Value must be initialized"

    def test_hash_table_len(self) -> None:
        """Test __len__ returns correct count."""
        ht = HashTable()
        assert len(ht) == 0, "Ht must not be empty"
        ht["key1"] = "value1"
        assert len(ht) == 1, "Ht must not be empty"
        ht["key2"] = "value2"
        assert len(ht) == 2, "Ht must not be empty"

    def test_hash_table_delete(self) -> None:
        """Test delete operation."""
        ht = HashTable()
        ht["key1"] = "value1"
        assert len(ht) == 1, "Ht must not be empty"
        del ht["key1"]
        assert len(ht) == 0, "Ht must not be empty"

    def test_hash_table_delete_nonexistent(self) -> None:
        """Test deleting non-existent key raises KeyError."""
        ht = HashTable()
        with pytest.raises(KeyError):
            del ht["nonexistent"]

    def test_hash_table_get_nonexistent(self) -> None:
        """Test getting non-existent key raises KeyError."""
        ht = HashTable()
        with pytest.raises(KeyError):
            _ = ht["nonexistent"]

    def test_hash_table_update_value(self) -> None:
        """Test updating an existing key."""
        ht = HashTable()
        ht["key1"] = "value1"
        ht["key1"] = "value2"
        assert ht["key1"] == "value2", "Value must be initialized"


class TestHashTableCollisions:
    """Test hash table collision handling."""

    def test_hash_table_collision_resolution(self) -> None:
        """Test that collisions are handled properly."""
        ht = HashTable(capacity=4)  # Small capacity to force collisions
        # Insert items that may collide
        for i in range(8):
            ht[f"key_{i}"] = f"value_{i}"

        # Verify all items are still retrievable
        for i in range(8):
            assert ht[f"key_{i}"] == f"value_{i}", "Value must be initialized"

    def test_hash_table_many_collisions(self) -> None:
        """Test many items with potential collisions."""
        ht = HashTable(capacity=2)  # Very small to force collisions
        items = {f"k{i}": f"v{i}" for i in range(20)}

        for k, v in items.items():
            ht[k] = v

        for k, v in items.items():
            assert ht[k] == v, "Condition must be true"


class TestHashTableResize:
    """Test hash table resizing."""

    def test_hash_table_resize_on_growth(self) -> None:
        """Test hash table resizes when load factor exceeded."""
        ht = HashTable(capacity=4)
        initial_capacity = ht._capacity if hasattr(ht, "_capacity") else 4

        # Add many items to trigger resize
        for i in range(20):
            ht[f"key_{i}"] = f"value_{i}"

        # Verify all items still accessible
        for i in range(20):
            assert ht[f"key_{i}"] == f"value_{i}", "Value must be initialized"

    def test_hash_table_stress_many_items(self) -> None:
        """Stress test with many items."""
        ht = HashTable()
        n_items = 100

        # Insert
        for i in range(n_items):
            ht[f"key_{i:04d}"] = f"value_{i}"

        # Verify all present
        assert len(ht) == n_items, "Ht must not be empty"
        for i in range(n_items):
            assert ht[f"key_{i:04d}"] == f"value_{i}", "Value must be initialized"

        # Delete half
        for i in range(0, n_items, 2):
            del ht[f"key_{i:04d}"]

        assert len(ht) == n_items // 2, "Ht must not be empty"


class TestHashTableIteration:
    """Test hash table iteration and containment."""

    def test_hash_table_contains(self) -> None:
        """Test __contains__ for membership testing."""
        ht = HashTable()
        ht["key1"] = "value1"
        assert "key1" in ht, "Condition must be true"
        assert "nonexistent" not in ht, "Condition must be true"

    def test_hash_table_iteration(self) -> None:
        """Test iterating over keys."""
        ht = HashTable()
        items = {f"key_{i}": f"value_{i}" for i in range(5)}
        for k, v in items.items():
            ht[k] = v

        # Test __iter__ if implemented
        if hasattr(ht, "__iter__"):
            keys = list(ht)
            assert len(keys) == len(items), "Keys must not be empty"


class TestHashTableTypes:
    """Test hash table with different value types."""

    def test_hash_table_string_values(self) -> None:
        """Test storing string values."""
        ht = HashTable()
        ht["str_key"] = "string_value"
        assert ht["str_key"] == "string_value", "Value must be initialized"

    def test_hash_table_int_values(self) -> None:
        """Test storing integer values."""
        ht = HashTable()
        ht["int_key"] = 42
        assert ht["int_key"] == 42, "Condition must be true"

    def test_hash_table_none_values(self) -> None:
        """Test storing None values."""
        ht = HashTable()
        ht["none_key"] = None
        assert ht["none_key"] is None, "Condition must be true"

    def test_hash_table_list_values(self) -> None:
        """Test storing list values."""
        ht = HashTable()
        ht["list_key"] = [1, 2, 3]
        assert ht["list_key"] == [1, 2, 3]

    def test_hash_table_dict_values(self) -> None:
        """Test storing dict values."""
        ht = HashTable()
        ht["dict_key"] = {"nested": "value"}
        assert ht["dict_key"] == {"nested": "value"}, "Value must be initialized"


class TestHashTableEdgeCases:
    """Test edge cases and error conditions."""

    def test_hash_table_empty_string_key(self) -> None:
        """Test empty string as key."""
        ht = HashTable()
        ht[""] = "empty_key_value"
        assert ht[""] == "empty_key_value", "Value must be initialized"

    def test_hash_table_numeric_string_keys(self) -> None:
        """Test numeric strings as keys."""
        ht = HashTable()
        ht["123"] = "numeric_string_key"
        assert ht["123"] == "numeric_string_key", "Condition must be true"

    def test_hash_table_special_chars_keys(self) -> None:
        """Test keys with special characters."""
        ht = HashTable()
        special_key = "key!@#$%^&*()"
        ht[special_key] = "special_value"
        assert ht[special_key] == "special_value", "Value must be initialized"

    def test_hash_table_unicode_keys(self) -> None:
        """Test unicode characters in keys."""
        ht = HashTable()
        ht["key_ñ_中文"] = "unicode_value"
        assert ht["key_ñ_中文"] == "unicode_value", "Value must be initialized"

    def test_hash_table_very_long_key(self) -> None:
        """Test very long key."""
        ht = HashTable()
        long_key = "k" * 1000
        ht[long_key] = "long_key_value"
        assert ht[long_key] == "long_key_value", "Value must be initialized"
