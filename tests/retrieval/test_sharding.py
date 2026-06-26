import pytest

"""Tests for index sharding module."""
pytest.importorskip("numpy")

from codex.retrieval.sharding import (
    ConsistentHashRing,
    ShardInfo,
    ShardManager,
    get_shard_for_id,
)


class TestConsistentHashRing:
    """Tests for ConsistentHashRing class."""

    def test_init_creates_ring(self):
        """Test ring initialization creates correct number of positions."""
        ring = ConsistentHashRing(num_shards=4, virtual_nodes=10)

        # Should have 4 shards * 10 virtual nodes = 40 positions
        assert len(ring._ring) == 40, "Collection must not be empty"
        assert ring.num_shards == 4, "num_shards is not valid"

    def test_get_shard_returns_valid_id(self):
        """Test get_shard returns valid shard IDs."""
        ring = ConsistentHashRing(num_shards=4)

        # Test various keys
        for key in ["doc-1", "doc-2", "doc-3", "article-123", "page-xyz"]:
            shard_id = ring.get_shard(key)
            assert 0 <= shard_id < 4, "0 is not valid"

    def test_get_shard_consistent(self):
        """Test same key always maps to same shard."""
        ring = ConsistentHashRing(num_shards=4)

        key = "doc-12345"
        shard_id_1 = ring.get_shard(key)
        shard_id_2 = ring.get_shard(key)
        shard_id_3 = ring.get_shard(key)

        assert shard_id_1 == shard_id_2 == shard_id_3, "shard_id_1 is not valid"

    def test_get_shard_distribution(self):
        """Test shard distribution is reasonably balanced."""
        ring = ConsistentHashRing(num_shards=4, virtual_nodes=150)

        # Generate many keys
        keys = [f"doc-{i}" for i in range(1000)]

        distribution = ring.get_shard_distribution(keys)

        # Each shard should get roughly 250 documents (±50)
        for shard_id, count in distribution.items():
            assert 200 <= count <= 300, f"Shard {shard_id} has {count} docs (expected ~250)"

    def test_add_shard(self):
        """Test adding new shard to ring."""
        ring = ConsistentHashRing(num_shards=3, virtual_nodes=10)

        initial_size = len(ring._ring)
        new_shard_id = ring.add_shard()

        assert new_shard_id == 3, "new_shard_id is not valid"
        assert ring.num_shards == 4, "num_shards is not valid"
        # Should have added 10 more positions
        assert len(ring._ring) == initial_size + 10, "Collection must not be empty"

    def test_remove_shard(self):
        """Test removing shard from ring."""
        ring = ConsistentHashRing(num_shards=4, virtual_nodes=10)

        initial_size = len(ring._ring)
        success = ring.remove_shard(2)

        assert success is True, "success is not valid"
        # Should have removed 10 positions
        assert len(ring._ring) == initial_size - 10, "Collection must not be empty"

    def test_virtual_nodes_prevent_hotspots(self):
        """Test virtual nodes provide better distribution than simple modulo."""
        ring = ConsistentHashRing(num_shards=3, virtual_nodes=100)

        keys = [f"user-{i}" for i in range(300)]
        distribution = ring.get_shard_distribution(keys)

        # Calculate standard deviation
        counts = list(distribution.values())
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        std_dev = variance**0.5

        # Standard deviation should be relatively small (< 15% of mean)
        assert std_dev < mean * 0.15, "std_dev is not valid"


class TestShardManager:
    """Tests for ShardManager class."""

    def test_init_creates_shards(self):
        """Test manager initialization creates shard info."""
        manager = ShardManager(num_shards=4)

        assert manager.num_shards == 4, "num_shards is not valid"
        assert len(manager.shards) == 4, "Collection must not be empty"
        assert all(isinstance(s, ShardInfo) for s in manager.shards.values())

    def test_route_document(self):
        """Test document routing to shards."""
        manager = ShardManager(num_shards=4)

        shard_id = manager.route_document("doc-12345")
        assert 0 <= shard_id < 4, "0 is not valid"

    def test_get_shard_info(self):
        """Test retrieving shard information."""
        manager = ShardManager(num_shards=4)

        shard_info = manager.get_shard_info(2)
        assert shard_info is not None, "shard_info must be initialized"
        assert shard_info.shard_id == 2, "shard_id is not valid"
        assert shard_info.shard_name == "shard_02", "shard_name is not valid"

    def test_get_shard_name(self):
        """Test getting shard names."""
        manager = ShardManager(num_shards=4, shard_name_prefix="index")

        name = manager.get_shard_name(1)
        assert name == "index_01", "name is not valid"

    def test_update_shard_stats(self):
        """Test updating shard statistics."""
        manager = ShardManager(num_shards=4)

        manager.update_shard_stats(0, doc_count=100, size_bytes=1024000)

        shard_info = manager.get_shard_info(0)
        assert shard_info.total_documents == 100, "total_documents is not valid"
        assert shard_info.size_bytes == 1024000, "size_bytes is not valid"

    def test_get_all_shards(self):
        """Test getting all shard information."""
        manager = ShardManager(num_shards=4)

        all_shards = manager.get_all_shards()
        assert len(all_shards) == 4, "All_shards must not be empty"
        assert all(isinstance(s, ShardInfo) for s in all_shards)

    def test_get_load_distribution(self):
        """Test load distribution calculation."""
        manager = ShardManager(num_shards=3)

        # Set different loads
        manager.update_shard_stats(0, doc_count=100, size_bytes=1000000)
        manager.update_shard_stats(1, doc_count=200, size_bytes=2000000)
        manager.update_shard_stats(2, doc_count=100, size_bytes=1000000)

        distribution = manager.get_load_distribution()

        assert distribution[0]["doc_percentage"] == 25.0, "Condition must be true"
        assert distribution[1]["doc_percentage"] == 50.0, "Condition must be true"
        assert distribution[2]["doc_percentage"] == 25.0, "Condition must be true"


class TestGetShardForId:
    """Tests for get_shard_for_id helper function."""

    def test_returns_valid_shard(self):
        """Test function returns valid shard ID."""
        shard_id = get_shard_for_id("doc-123", total_shards=4)
        assert 0 <= shard_id < 4, "0 is not valid"

    def test_consistent_hashing(self):
        """Test consistent hashing mode."""
        shard_id_1 = get_shard_for_id("doc-123", total_shards=4, use_consistent_hashing=True)
        shard_id_2 = get_shard_for_id("doc-123", total_shards=4, use_consistent_hashing=True)

        assert shard_id_1 == shard_id_2, "shard_id_1 is not valid"

    def test_simple_modulo(self):
        """Test simple modulo hashing mode."""
        shard_id_1 = get_shard_for_id("doc-123", total_shards=4, use_consistent_hashing=False)
        shard_id_2 = get_shard_for_id("doc-123", total_shards=4, use_consistent_hashing=False)

        assert shard_id_1 == shard_id_2, "shard_id_1 is not valid"
        assert 0 <= shard_id_1 < 4, "0 is not valid"


class TestShardInfo:
    """Tests for ShardInfo dataclass."""

    def test_create_shard_info(self):
        """Test creating shard info instance."""
        info = ShardInfo(shard_id=0, shard_name="shard_00", total_documents=100, size_bytes=1024000)

        assert info.shard_id == 0, "shard_id is not valid"
        assert info.shard_name == "shard_00", "shard_name is not valid"
        assert info.total_documents == 100, "total_documents is not valid"
        assert info.size_bytes == 1024000, "size_bytes is not valid"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        info = ShardInfo(shard_id=1, shard_name="shard_01", total_documents=50, size_bytes=512000)

        data = info.to_dict()

        assert data["shard_id"] == 1, "Data must not be empty"
        assert data["shard_name"] == "shard_01", "Data must not be empty"
        assert data["total_documents"] == 50, "Data must not be empty"
        assert data["size_bytes"] == 512000, "Data must not be empty"


class TestDistributionQuality:
    """Tests for distribution quality with realistic workloads."""

    def test_uuid_distribution(self):
        """Test distribution with UUID-like keys."""
        ring = ConsistentHashRing(num_shards=8, virtual_nodes=150)

        # Simulate UUIDs
        import uuid

        keys = [str(uuid.uuid4()) for _ in range(10000)]

        distribution = ring.get_shard_distribution(keys)

        # Each shard should get roughly 1250 documents
        for shard_id, count in distribution.items():
            # Allow 20% deviation
            assert 1000 <= count <= 1500, "Count must be greater than zero"

    def test_sequential_id_distribution(self):
        """Test distribution with sequential numeric IDs."""
        ring = ConsistentHashRing(num_shards=4, virtual_nodes=150)

        # Sequential IDs (common pattern)
        keys = [f"doc-{i:06d}" for i in range(1000)]

        distribution = ring.get_shard_distribution(keys)

        # Should still be reasonably balanced
        for shard_id, count in distribution.items():
            assert 200 <= count <= 300, "Count must be greater than zero"

    def test_hotspot_avoidance(self):
        """Test that virtual nodes avoid hotspots."""
        # With few virtual nodes
        ring_few = ConsistentHashRing(num_shards=4, virtual_nodes=1)
        keys = [f"key-{i}" for i in range(1000)]
        dist_few = ring_few.get_shard_distribution(keys)

        # With many virtual nodes
        ring_many = ConsistentHashRing(num_shards=4, virtual_nodes=150)
        dist_many = ring_many.get_shard_distribution(keys)

        # Calculate coefficient of variation (lower is better)
        def cv(counts):
            mean = sum(counts) / len(counts)
            variance = sum((x - mean) ** 2 for x in counts) / len(counts)
            std_dev = variance**0.5
            return std_dev / mean if mean > 0 else 0

        cv_few = cv(list(dist_few.values()))
        cv_many = cv(list(dist_many.values()))

        # More virtual nodes should give better distribution
        assert cv_many < cv_few, "cv_many is not valid"
