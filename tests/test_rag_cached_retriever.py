"""
Tests for RAG CachedRetriever and LRUCache classes

Comprehensive test coverage for caching functionality in retriever.py
"""

import tempfile
import time
from pathlib import Path

import pytest

# Skip tests if dependencies not available
pytest.importorskip("sentence_transformers")
pytest.importorskip("faiss")

from codex.rag.indexer import build_index_from_files
from codex.rag.retriever import CachedRetriever, LRUCache


class TestLRUCache:
    """Tests for LRUCache class"""

    def test_initialization(self):
        """Test LRU cache initialization"""
        cache = LRUCache(maxsize=100)
        
        assert cache.maxsize == 100
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_get_miss(self):
        """Test cache miss on get"""
        cache = LRUCache()
        
        result = cache.get("nonexistent")
        
        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0

    def test_put_and_get_hit(self):
        """Test putting value and getting cache hit"""
        cache = LRUCache()
        
        cache.put("key1", "value1")
        result = cache.get("key1")
        
        assert result == "value1"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_put_updates_existing(self):
        """Test that putting existing key updates value"""
        cache = LRUCache()
        
        cache.put("key1", "value1")
        cache.put("key1", "value2")
        result = cache.get("key1")
        
        assert result == "value2"
        assert len(cache.cache) == 1

    def test_lru_eviction(self):
        """Test LRU eviction when maxsize exceeded"""
        cache = LRUCache(maxsize=3)
        
        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        assert len(cache.cache) == 3
        
        # Add one more - should evict key1 (oldest)
        cache.put("key4", "value4")
        
        assert len(cache.cache) == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_lru_ordering_with_access(self):
        """Test that accessing items updates LRU order"""
        cache = LRUCache(maxsize=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add new item - should evict key2 (now oldest)
        cache.put("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Still present
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_clear(self):
        """Test clearing cache"""
        cache = LRUCache()
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.get("key1")
        cache.get("nonexistent")
        
        assert len(cache.cache) > 0
        assert cache.hits > 0
        assert cache.misses > 0
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_get_stats(self):
        """Test cache statistics"""
        cache = LRUCache(maxsize=100)
        
        # Add some entries
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Make some hits and misses
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("key4")  # Miss
        cache.get("key5")  # Miss
        
        stats = cache.get_stats()
        
        assert stats["size"] == 3
        assert stats["maxsize"] == 100
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 0.5  # 2 hits out of 4 total

    def test_get_stats_empty_cache(self):
        """Test statistics on empty cache"""
        cache = LRUCache()
        
        stats = cache.get_stats()
        
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0


class TestCachedRetriever:
    """Tests for CachedRetriever class"""

    @pytest.fixture
    def sample_index(self):
        """Create a sample index for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create sample files
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()
            
            files = []
            contents = [
                "Python is a high-level programming language. " * 20,
                "Machine learning uses algorithms to learn from data. " * 20,
                "Docker is a containerization platform. " * 20,
            ]
            
            for i, content in enumerate(contents):
                file_path = docs_dir / f"doc{i}.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)
            
            # Build index
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=files,
                index_name="test_docs",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=300,
                overlap=50,
            )
            
            yield {
                "index_dir": str(index_dir),
                "index_name": "test_docs",
                "tenant_id": "test",
            }

    def test_cached_retriever_initialization(self, sample_index):
        """Test cached retriever initialization"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            cache_ttl=3600,
            cache_maxsize=500,
            normalize_queries=True,
        )
        
        assert retriever is not None
        assert retriever.cache_ttl == 3600
        assert retriever.normalize_queries is True
        assert retriever.query_cache.maxsize == 500
        assert len(retriever.cache_timestamps) == 0

    def test_query_normalization(self, sample_index):
        """Test query normalization"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            normalize_queries=True,
        )
        
        # Test normalization
        q1 = "  Python   Programming  "
        q2 = "python programming"
        
        normalized1 = retriever._normalize_query(q1)
        normalized2 = retriever._normalize_query(q2)
        
        assert normalized1 == normalized2
        assert normalized1 == "python programming"

    def test_query_normalization_disabled(self, sample_index):
        """Test that normalization can be disabled"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            normalize_queries=False,
        )
        
        q = "  Python   Programming  "
        normalized = retriever._normalize_query(q)
        
        assert normalized == q  # Should be unchanged

    def test_cache_key_generation(self, sample_index):
        """Test cache key generation"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        # Same query should produce same key
        key1 = retriever._make_cache_key("Python programming", top_k=5, min_score=0.7)
        key2 = retriever._make_cache_key("Python programming", top_k=5, min_score=0.7)
        assert key1 == key2
        
        # Different queries should produce different keys
        key3 = retriever._make_cache_key("Machine learning", top_k=5, min_score=0.7)
        assert key1 != key3
        
        # Different parameters should produce different keys
        key4 = retriever._make_cache_key("Python programming", top_k=10, min_score=0.7)
        assert key1 != key4

    def test_cache_key_with_normalization(self, sample_index):
        """Test that normalized queries produce same cache keys"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            normalize_queries=True,
        )
        
        # These should produce the same key after normalization
        key1 = retriever._make_cache_key("  Python   Programming  ", top_k=5, min_score=None)
        key2 = retriever._make_cache_key("python programming", top_k=5, min_score=None)
        
        assert key1 == key2

    def test_cache_hit(self, sample_index):
        """Test cache hit on repeated query"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            cache_ttl=3600,
        )
        
        query = "Python programming"
        
        # First query - cache miss
        results1 = retriever.query_with_cache(query, top_k=3)
        assert len(results1) > 0
        assert retriever.query_cache.misses == 1
        assert retriever.query_cache.hits == 0
        
        # Second query - cache hit
        results2 = retriever.query_with_cache(query, top_k=3)
        assert results1 == results2
        assert retriever.query_cache.hits == 1
        assert retriever.query_cache.misses == 1

    def test_cache_miss_different_params(self, sample_index):
        """Test cache miss with different parameters"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        query = "Python programming"
        
        # Query with top_k=3
        results1 = retriever.query_with_cache(query, top_k=3)
        assert len(results1) <= 3
        
        # Query with top_k=5 - should be cache miss
        results2 = retriever.query_with_cache(query, top_k=5)
        assert len(results2) <= 5
        
        # Should have 2 misses (different params)
        assert retriever.query_cache.misses == 2

    def test_cache_validity_check(self, sample_index):
        """Test cache validity based on TTL"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            cache_ttl=1,  # 1 second TTL
        )
        
        cache_key = retriever._make_cache_key("test", top_k=5, min_score=None)
        
        # Initially invalid (not in cache)
        assert not retriever._is_cache_valid(cache_key)
        
        # Add to cache
        retriever.cache_timestamps[cache_key] = time.time()
        
        # Should be valid immediately
        assert retriever._is_cache_valid(cache_key)
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should now be invalid
        assert not retriever._is_cache_valid(cache_key)

    def test_cache_expiration(self, sample_index):
        """Test that expired cache entries cause cache miss"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            cache_ttl=1,  # 1 second TTL
        )
        
        query = "Python programming"
        
        # First query
        results1 = retriever.query_with_cache(query, top_k=3)
        assert retriever.query_cache.misses == 1
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Second query after expiration - should be cache miss
        results2 = retriever.query_with_cache(query, top_k=3)
        assert retriever.query_cache.misses == 2

    def test_clear_cache(self, sample_index):
        """Test clearing cache"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        # Perform some queries
        retriever.query_with_cache("Python", top_k=3)
        retriever.query_with_cache("Machine learning", top_k=3)
        
        assert len(retriever.query_cache.cache) > 0
        assert len(retriever.cache_timestamps) > 0
        
        # Clear cache
        retriever.clear_cache()
        
        assert len(retriever.query_cache.cache) == 0
        assert len(retriever.cache_timestamps) == 0

    def test_get_cache_stats(self, sample_index):
        """Test getting cache statistics"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            cache_ttl=3600,
            cache_maxsize=1000,
            normalize_queries=True,
        )
        
        # Perform some queries
        retriever.query_with_cache("Python", top_k=3)
        retriever.query_with_cache("Python", top_k=3)  # Hit
        retriever.query_with_cache("Machine learning", top_k=3)
        
        stats = retriever.get_cache_stats()
        
        assert stats["ttl"] == 3600
        assert stats["normalize_queries"] is True
        assert stats["size"] == 2  # Two unique queries
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["valid_entries"] == 2
        assert stats["hit_rate"] == 1.0 / 3.0

    def test_invalidate_expired(self, sample_index):
        """Test manual invalidation of expired entries"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
            cache_ttl=1,  # 1 second TTL
        )
        
        # Add some queries
        retriever.query_with_cache("Python", top_k=3)
        retriever.query_with_cache("Machine learning", top_k=3)
        
        assert len(retriever.query_cache.cache) == 2
        assert len(retriever.cache_timestamps) == 2
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Manually invalidate expired
        retriever.invalidate_expired()
        
        # Expired entries should be removed
        assert len(retriever.query_cache.cache) == 0
        assert len(retriever.cache_timestamps) == 0

    def test_cache_with_min_score(self, sample_index):
        """Test caching with min_score parameter"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        query = "Python programming"
        
        # Query with min_score
        results1 = retriever.query_with_cache(query, top_k=5, min_score=0.5)
        
        # Same query should hit cache
        results2 = retriever.query_with_cache(query, top_k=5, min_score=0.5)
        assert results1 == results2
        assert retriever.query_cache.hits == 1
        
        # Different min_score should miss cache
        results3 = retriever.query_with_cache(query, top_k=5, min_score=0.7)
        assert retriever.query_cache.misses == 2

    def test_cache_stats_with_no_activity(self, sample_index):
        """Test cache stats with no queries"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        stats = retriever.get_cache_stats()
        
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["valid_entries"] == 0
        assert stats["hit_rate"] == 0.0

    def test_cache_with_special_characters(self, sample_index):
        """Test caching with special characters in query"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        query = "Python: what's the @difference between [] and {}?"
        
        # Should handle special characters without errors
        results1 = retriever.query_with_cache(query, top_k=3)
        results2 = retriever.query_with_cache(query, top_k=3)
        
        assert results1 == results2
        assert retriever.query_cache.hits == 1
