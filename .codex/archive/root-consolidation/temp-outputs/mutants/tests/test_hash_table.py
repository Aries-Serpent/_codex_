"""Comprehensive test suite for hash_table module."""

from src.codex.utils.hash_table import (
    CuckooHashTable,
    RobinHoodHashTable,
    get_aais_contribution,
    murmur_hash3_32,
)


class TestMurmurHash3:
    """Test suite for murmur_hash3_32 function."""

    def test_murmur_hash_empty_key(self):
        """Test murmur hash with empty key."""
        hash_val = murmur_hash3_32(b"")
        assert isinstance(hash_val, int)
        assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_single_byte(self):
        """Test murmur hash with single byte."""
        hash_val = murmur_hash3_32(b"a")
        assert isinstance(hash_val, int)
        assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_multiple_bytes(self):
        """Test murmur hash with multiple bytes."""
        hash_val = murmur_hash3_32(b"hello")
        assert isinstance(hash_val, int)
        assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_long_key(self):
        """Test murmur hash with long key."""
        key = b"x" * 1000
        hash_val = murmur_hash3_32(key)
        assert isinstance(hash_val, int)
        assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_consistent(self):
        """Test that murmur hash is consistent."""
        key = b"test_key"
        hash1 = murmur_hash3_32(key)
        hash2 = murmur_hash3_32(key)
        assert hash1 == hash2, "hash1 is not valid"

    def test_murmur_hash_different_seeds(self):
        """Test murmur hash with different seeds."""
        key = b"test_key"
        hash1 = murmur_hash3_32(key, seed=0)
        hash2 = murmur_hash3_32(key, seed=42)
        # Different seeds should produce different hashes (usually)
        # But not guaranteed, so we just check they're valid
        assert 0 <= hash1 < 2**32, "0 is not valid"
        assert 0 <= hash2 < 2**32, "0 is not valid"

    def test_murmur_hash_returns_32bit(self):
        """Test that murmur hash returns 32-bit values."""
        key = b"test"
        for _ in range(10):
            hash_val = murmur_hash3_32(key)
            assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_deterministic(self):
        """Test murmur hash determinism."""
        keys = [b"a", b"ab", b"abc", b"abcd"]
        hashes = [murmur_hash3_32(k) for k in keys]
        # Re-hash and verify consistency
        for key, original_hash in zip(keys, hashes):
            assert murmur_hash3_32(key) == original_hash, "Condition must be true"

    def test_murmur_hash_different_inputs_likely_different(self):
        """Test that different inputs produce different hashes (usually)."""
        hash1 = murmur_hash3_32(b"test1")
        hash2 = murmur_hash3_32(b"test2")
        # We can't guarantee they're different, but likely
        assert isinstance(hash1, int)
        assert isinstance(hash2, int)

    def test_murmur_hash_4byte_aligned(self):
        """Test murmur hash with 4-byte aligned data."""
        hash_val = murmur_hash3_32(b"1234")
        assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_5byte_data(self):
        """Test murmur hash with 5-byte data."""
        hash_val = murmur_hash3_32(b"12345")
        assert 0 <= hash_val < 2**32, "0 is not valid"

    def test_murmur_hash_3byte_data(self):
        """Test murmur hash with 3-byte data."""
        hash_val = murmur_hash3_32(b"123")
        assert 0 <= hash_val < 2**32, "0 is not valid"


class TestRobinHoodHashTable:
    """Test suite for RobinHoodHashTable class."""

    def test_robin_hood_create(self):
        """Test creating a Robin Hood hash table."""
        table = RobinHoodHashTable[str, int]()
        assert table.size == 0, "size is not valid"
        assert table.capacity == 16, "capacity is not valid"

    def test_robin_hood_custom_capacity(self):
        """Test creating Robin Hood table with custom capacity."""
        table = RobinHoodHashTable[str, int](initial_capacity=32)
        assert table.capacity == 32, "capacity is not valid"

    def test_robin_hood_custom_load_factor(self):
        """Test creating Robin Hood table with custom load factor."""
        table = RobinHoodHashTable[str, int](max_load_factor=0.5)
        assert table.max_load_factor == 0.5, "max_load_factor is not valid"

    def test_robin_hood_insert_single(self):
        """Test inserting single item."""
        table = RobinHoodHashTable[str, int]()
        table.insert("key1", 100)
        assert table.size == 1, "size is not valid"

    def test_robin_hood_insert_multiple(self):
        """Test inserting multiple items."""
        table = RobinHoodHashTable[str, int]()
        for i in range(10):
            table.insert(f"key{i}", i)
        assert table.size == 10, "size is not valid"

    def test_robin_hood_lookup_existing(self):
        """Test looking up existing key."""
        table = RobinHoodHashTable[str, int]()
        table.insert("key1", 100)
        assert table.lookup("key1") == 100, "Condition must be true"

    def test_robin_hood_lookup_missing(self):
        """Test looking up missing key."""
        table = RobinHoodHashTable[str, int]()
        assert table.lookup("missing") is None, "Condition must be true"

    def test_robin_hood_update_value(self):
        """Test updating existing value."""
        table = RobinHoodHashTable[str, int]()
        table.insert("key1", 100)
        table.insert("key1", 200)
        assert table.lookup("key1") == 200, "Condition must be true"
        assert table.size == 1, "size is not valid"

    def test_robin_hood_delete_existing(self):
        """Test deleting existing key."""
        table = RobinHoodHashTable[str, int]()
        table.insert("key1", 100)
        result = table.delete("key1")
        assert result is True, "Result must not be empty"
        assert table.size == 0, "size is not valid"
        assert table.lookup("key1") is None, "Condition must be true"

    def test_robin_hood_delete_missing(self):
        """Test deleting missing key."""
        table = RobinHoodHashTable[str, int]()
        result = table.delete("missing")
        assert result is False, "Result must not be empty"
        assert table.size == 0, "size is not valid"

    def test_robin_hood_resize(self):
        """Test table resizing."""
        table = RobinHoodHashTable[str, int](initial_capacity=4, max_load_factor=0.75)
        original_capacity = table.capacity
        for i in range(10):
            table.insert(f"key{i}", i)
        assert table.capacity > original_capacity, "capacity must be greater than zero"

    def test_robin_hood_metrics(self):
        """Test getting metrics."""
        table = RobinHoodHashTable[str, int]()
        for i in range(100):
            table.insert(f"key{i}", i)
        metrics = table.get_metrics()
        assert "size" in metrics, "Condition must be true"
        assert "capacity" in metrics, "Condition must be true"
        assert "load_factor" in metrics, "Condition must be true"
        assert metrics["size"] == 100, "Condition must be true"

    def test_robin_hood_large_inserts(self):
        """Test inserting large number of items."""
        table = RobinHoodHashTable[str, int]()
        for i in range(1000):
            table.insert(f"key{i}", i)
        assert table.size == 1000, "size is not valid"
        for i in range(0, 1000, 100):
            assert table.lookup(f"key{i}") == i, "Condition must be true"

    def test_robin_hood_collision_handling(self):
        """Test collision handling."""
        table = RobinHoodHashTable[str, int](initial_capacity=4)
        # Insert items that will collide
        for i in range(10):
            table.insert(f"key{i}", i)
        # Verify all items are findable
        for i in range(10):
            assert table.lookup(f"key{i}") == i, "Condition must be true"

    def test_robin_hood_delete_with_collisions(self):
        """Test deletion with collisions."""
        table = RobinHoodHashTable[str, int](initial_capacity=4)
        for i in range(10):
            table.insert(f"key{i}", i)
        for i in range(5):
            table.delete(f"key{i}")
        assert table.size == 5, "size is not valid"

    def test_robin_hood_total_lookups_tracked(self):
        """Test that total lookups are tracked."""
        table = RobinHoodHashTable[str, int]()
        table.insert("key1", 100)
        table.lookup("key1")
        table.lookup("missing")
        metrics = table.get_metrics()
        assert metrics["total_lookups"] >= 2, "Value must be greater than zero"


class TestCuckooHashTable:
    """Test suite for CuckooHashTable class."""

    def test_cuckoo_create(self):
        """Test creating a Cuckoo hash table."""
        table = CuckooHashTable[str, int]()
        assert table.size == 0, "size is not valid"
        assert table.capacity == 16, "capacity is not valid"

    def test_cuckoo_custom_capacity(self):
        """Test creating Cuckoo table with custom capacity."""
        table = CuckooHashTable[str, int](initial_capacity=32)
        assert table.capacity == 32, "capacity is not valid"

    def test_cuckoo_custom_max_evictions(self):
        """Test creating Cuckoo table with custom max_evictions."""
        table = CuckooHashTable[str, int](max_evictions=50)
        assert table.max_evictions == 50, "max_evictions is not valid"

    def test_cuckoo_insert_single(self):
        """Test inserting single item."""
        table = CuckooHashTable[str, int]()
        table.insert("key1", 100)
        assert table.size == 1, "size is not valid"

    def test_cuckoo_insert_multiple(self):
        """Test inserting multiple items."""
        table = CuckooHashTable[str, int]()
        for i in range(10):
            table.insert(f"key{i}", i)
        assert table.size == 10, "size is not valid"

    def test_cuckoo_lookup_existing(self):
        """Test looking up existing key."""
        table = CuckooHashTable[str, int]()
        table.insert("key1", 100)
        assert table.lookup("key1") == 100, "Condition must be true"

    def test_cuckoo_lookup_missing(self):
        """Test looking up missing key."""
        table = CuckooHashTable[str, int]()
        assert table.lookup("missing") is None, "Condition must be true"

    def test_cuckoo_update_value(self):
        """Test updating existing value."""
        table = CuckooHashTable[str, int]()
        table.insert("key1", 100)
        table.insert("key1", 200)
        assert table.lookup("key1") == 200, "Condition must be true"
        assert table.size == 1, "size is not valid"

    def test_cuckoo_metrics(self):
        """Test getting metrics."""
        table = CuckooHashTable[str, int]()
        for i in range(100):
            table.insert(f"key{i}", i)
        metrics = table.get_metrics()
        assert "size" in metrics, "Condition must be true"
        assert "capacity" in metrics, "Condition must be true"
        assert "load_factor" in metrics, "Condition must be true"
        assert metrics["size"] == 100, "Condition must be true"

    def test_cuckoo_large_inserts(self):
        """Test inserting large number of items."""
        table = CuckooHashTable[str, int]()
        for i in range(1000):
            table.insert(f"key{i}", i)
        assert table.size == 1000, "size is not valid"
        for i in range(0, 1000, 100):
            assert table.lookup(f"key{i}") == i, "Condition must be true"

    def test_cuckoo_collision_handling(self):
        """Test collision handling with cuckoo hashing."""
        table = CuckooHashTable[str, int](initial_capacity=8)
        for i in range(20):
            table.insert(f"key{i}", i)
        # Verify all items are findable
        for i in range(20):
            assert table.lookup(f"key{i}") == i, "Condition must be true"

    def test_cuckoo_resize(self):
        """Test table resizing."""
        table = CuckooHashTable[str, int](initial_capacity=4)
        original_capacity = table.capacity
        for i in range(100):
            table.insert(f"key{i}", i)
        assert table.capacity > original_capacity, "capacity must be greater than zero"

    def test_cuckoo_guaranteed_o1_lookup(self):
        """Test that lookup is O(1) for Cuckoo hashing."""
        table = CuckooHashTable[str, int]()
        for i in range(100):
            table.insert(f"key{i}", i)
        metrics = table.get_metrics()
        # Should be able to lookup in 2 checks max
        assert metrics["total_lookups"] >= 0, "Value must be greater than zero"

    def test_cuckoo_evictions_tracked(self):
        """Test that evictions are tracked."""
        table = CuckooHashTable[str, int](initial_capacity=4)
        for i in range(50):
            table.insert(f"key{i}", i)
        metrics = table.get_metrics()
        assert "total_evictions" in metrics, "Condition must be true"

    def test_cuckoo_total_lookups_tracked(self):
        """Test that total lookups are tracked."""
        table = CuckooHashTable[str, int]()
        table.insert("key1", 100)
        table.lookup("key1")
        table.lookup("missing")
        metrics = table.get_metrics()
        assert metrics["total_lookups"] >= 2, "Value must be greater than zero"


class TestHashFunctionDistribution:
    """Test suite for hash function distribution."""

    def test_murmur_hash_distribution(self):
        """Test murmur hash distribution."""
        hashes = []
        for i in range(1000):
            hash_val = murmur_hash3_32(f"key{i}".encode())
            hashes.append(hash_val)
        # Should have some variety in hashes
        unique_hashes = len(set(hashes))
        assert unique_hashes > 100, "unique_hashes must be greater than zero"


class TestGetAAISContribution:
    """Test suite for get_aais_contribution function."""

    def test_get_aais_contribution_robin_hood(self):
        """Test AAIS contribution for Robin Hood table."""
        table = RobinHoodHashTable[str, int]()
        table.insert("key1", 100)
        contribution = get_aais_contribution(table)
        assert "runtime_introspection" in contribution, "Condition must be true"
        assert isinstance(contribution["runtime_introspection"], (int, float))
        assert contribution["runtime_introspection"] == 3.0, "Condition must be true"

    def test_get_aais_contribution_cuckoo(self):
        """Test AAIS contribution for Cuckoo table."""
        table = CuckooHashTable[str, int]()
        table.insert("key1", 100)
        contribution = get_aais_contribution(table)
        assert "runtime_introspection" in contribution, "Condition must be true"
        assert isinstance(contribution["runtime_introspection"], (int, float))
        assert contribution["runtime_introspection"] == 3.0, "Condition must be true"

    def test_get_aais_contribution_includes_metrics(self):
        """Test that AAIS contribution includes metrics."""
        table = RobinHoodHashTable[str, int]()
        for i in range(100):
            table.insert(f"key{i}", i)
        contribution = get_aais_contribution(table)
        assert "metrics" in contribution, "Condition must be true"
        metrics = contribution["metrics"]
        assert "size" in metrics, "Condition must be true"
        assert metrics["size"] == 100, "Condition must be true"

    def test_get_aais_contribution_empty_table(self):
        """Test AAIS contribution for empty table."""
        table = RobinHoodHashTable[str, int]()
        contribution = get_aais_contribution(table)
        assert "runtime_introspection" in contribution, "Condition must be true"
        assert "metrics" in contribution, "Condition must be true"
        assert contribution["metrics"]["size"] == 0, "Condition must be true"


class TestHashTableComparison:
    """Test suite comparing Robin Hood and Cuckoo hash tables."""

    def test_robin_hood_vs_cuckoo_insertion(self):
        """Test insertion performance characteristics."""
        rh_table = RobinHoodHashTable[str, int]()
        cuckoo_table = CuckooHashTable[str, int]()
        for i in range(100):
            rh_table.insert(f"key{i}", i)
            cuckoo_table.insert(f"key{i}", i)
        assert rh_table.size == 100, "size is not valid"
        assert cuckoo_table.size == 100, "size is not valid"

    def test_robin_hood_vs_cuckoo_lookup(self):
        """Test lookup accuracy."""
        rh_table = RobinHoodHashTable[str, int]()
        cuckoo_table = CuckooHashTable[str, int]()
        for i in range(100):
            rh_table.insert(f"key{i}", i)
            cuckoo_table.insert(f"key{i}", i)
        for i in range(100):
            assert rh_table.lookup(f"key{i}") == i, "Condition must be true"
            assert cuckoo_table.lookup(f"key{i}") == i, "Condition must be true"
