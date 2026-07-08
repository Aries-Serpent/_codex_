"""
Tests for RAG CachedRetriever and LRUCache classes

Comprehensive test coverage for caching functionality in retriever.py
"""

import tempfile
import time
from pathlib import Path

import pytest

# Conditional imports for RAG dependencies - safely handled at test runtime
try:
    from codex.rag.indexer import build_index_from_files
    from codex.rag.retriever import CachedRetriever, LRUCache

    RAG_RETRIEVER_AVAILABLE = True
except ImportError:
    RAG_RETRIEVER_AVAILABLE = False

# sentence_transformers is required at execution time even when the module import succeeds
if RAG_RETRIEVER_AVAILABLE:
    pytest.importorskip("sentence_transformers", reason="sentence_transformers not installed")

pytestmark = pytest.mark.skipif(
    not RAG_RETRIEVER_AVAILABLE,
    reason="RAG retriever dependencies (sentence_transformers, faiss) not installed",
)

# Guard for tests that require real SentenceTransformer models on CPU
try:
    import torch as _torch

    _cuda_available = _torch.cuda.is_available()
except (ImportError, RuntimeError):
    _cuda_available = False

_skip_real_st_models = pytest.mark.skipif(
    not _cuda_available,
    reason="SentenceTransformer real model tests may fail on CPU-only runners",
)


class TestLRUCache:
    """Tests for LRUCache class"""

    def test_initialization(self):
        """Test LRU cache initialization"""
        cache = LRUCache(maxsize=100)

        assert cache.maxsize == 100, "maxsize is not valid"
        assert len(cache.cache) == 0, "Collection must not be empty"
        assert cache.hits == 0, "hits is not valid"
        assert cache.misses == 0, "misses is not valid"

    def test_get_miss(self):
        """Test cache miss on get"""
        cache = LRUCache()

        result = cache.get("nonexistent")

        assert result is None, "Result must not be empty"
        assert cache.misses == 1, "misses is not valid"
        assert cache.hits == 0, "hits is not valid"

    def test_put_and_get_hit(self):
        """Test putting value and getting cache hit"""
        cache = LRUCache()

        cache.put("key1", "value1")
        result = cache.get("key1")

        assert result == "value1", "Result must not be empty"
        assert cache.hits == 1, "hits is not valid"
        assert cache.misses == 0, "misses is not valid"

    def test_put_updates_existing(self):
        """Test that putting existing key updates value"""
        cache = LRUCache()

        cache.put("key1", "value1")
        cache.put("key1", "value2")
        result = cache.get("key1")

        assert result == "value2", "Result must not be empty"
        assert len(cache.cache) == 1, "Collection must not be empty"

    def test_lru_eviction(self):
        """Test LRU eviction when maxsize exceeded"""
        cache = LRUCache(maxsize=3)

        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        assert len(cache.cache) == 3, "Collection must not be empty"

        # Add one more - should evict key1 (oldest)
        cache.put("key4", "value4")

        assert len(cache.cache) == 3, "Collection must not be empty"
        assert cache.get("key1") is None, "Condition must be true"
        assert cache.get("key2") == "value2", "Value must be initialized"
        assert cache.get("key3") == "value3", "Value must be initialized"
        assert cache.get("key4") == "value4", "Value must be initialized"

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

        assert cache.get("key1") == "value1", "Value must be initialized"
        assert cache.get("key2") is None, "Condition must be true"
        assert cache.get("key3") == "value3", "Value must be initialized"
        assert cache.get("key4") == "value4", "Value must be initialized"

    def test_clear(self):
        """Test clearing cache"""
        cache = LRUCache()

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.get("key1")
        cache.get("nonexistent")

        assert len(cache.cache) > 0, "Collection must not be empty"
        assert cache.hits > 0, "hits must be greater than zero"
        assert cache.misses > 0, "misses must be greater than zero"

        cache.clear()

        assert len(cache.cache) == 0, "Collection must not be empty"
        assert cache.hits == 0, "hits is not valid"
        assert cache.misses == 0, "misses is not valid"

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

        assert stats["size"] == 3, "Condition must be true"
        assert stats["maxsize"] == 100, "Condition must be true"
        assert stats["hits"] == 2, "Condition must be true"
        assert stats["misses"] == 2, "Condition must be true"
        assert stats["hit_rate"] == 0.5, "Condition must be true"

    def test_get_stats_empty_cache(self):
        """Test statistics on empty cache"""
        cache = LRUCache()

        stats = cache.get_stats()

        assert stats["size"] == 0, "Condition must be true"
        assert stats["hits"] == 0, "Condition must be true"
        assert stats["misses"] == 0, "Condition must be true"
        assert stats["hit_rate"] == 0.0, "Condition must be true"


@_skip_real_st_models
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

        assert retriever is not None, "retriever must be initialized"
        assert retriever.cache_ttl == 3600, "cache_ttl is not valid"
        assert retriever.normalize_queries is True, "normalize_queries is not valid"
        assert retriever.query_cache.maxsize == 500, "maxsize is not valid"
        assert len(retriever.cache_timestamps) == 0, "Collection must not be empty"

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

        assert normalized1 == normalized2, "normalized1 is not valid"
        assert normalized1 == "python programming", "normalized1 is not valid"

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

        assert normalized == q, "normalized is not valid"

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
        assert key1 == key2, "key1 is not valid"

        # Different queries should produce different keys
        key3 = retriever._make_cache_key("Machine learning", top_k=5, min_score=0.7)
        assert key1 != key3, "key1 is not valid"

        # Different parameters should produce different keys
        key4 = retriever._make_cache_key("Python programming", top_k=10, min_score=0.7)
        assert key1 != key4, "key1 is not valid"

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

        assert key1 == key2, "key1 is not valid"

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
        assert len(results1) > 0, "Results1 must not be empty"
        assert retriever.query_cache.misses == 1, "misses is not valid"
        assert retriever.query_cache.hits == 0, "hits is not valid"

        # Second query - cache hit
        results2 = retriever.query_with_cache(query, top_k=3)
        assert results1 == results2, "Result must not be empty"
        assert retriever.query_cache.hits == 1, "hits is not valid"
        assert retriever.query_cache.misses == 1, "misses is not valid"

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
        assert len(results1) <= 3, "Results1 must not be empty"

        # Query with top_k=5 - should be cache miss
        results2 = retriever.query_with_cache(query, top_k=5)
        assert len(results2) <= 5, "Results2 must not be empty"

        # Should have 2 misses (different params)
        assert retriever.query_cache.misses == 2, "misses is not valid"

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
        assert not retriever._is_cache_valid(cache_key), "Condition must be true"

        # Add to cache
        retriever.cache_timestamps[cache_key] = time.time()

        # Should be valid immediately
        assert retriever._is_cache_valid(cache_key), "Condition must be true"

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should now be invalid
        assert not retriever._is_cache_valid(cache_key), "Condition must be true"

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
        retriever.query_with_cache(query, top_k=3)
        assert retriever.query_cache.misses == 1, "misses is not valid"

        # Wait for expiration
        time.sleep(1.1)

        # Second query after expiration - should be cache miss
        retriever.query_with_cache(query, top_k=3)
        assert retriever.query_cache.misses == 2, "misses is not valid"

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

        assert len(retriever.query_cache.cache) > 0, "Collection must not be empty"
        assert len(retriever.cache_timestamps) > 0, "Collection must not be empty"

        # Clear cache
        retriever.clear_cache()

        assert len(retriever.query_cache.cache) == 0, "Collection must not be empty"
        assert len(retriever.cache_timestamps) == 0, "Collection must not be empty"

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

        assert stats["ttl"] == 3600, "Condition must be true"
        assert stats["normalize_queries"] is True, "Condition must be true"
        assert stats["size"] == 2, "Condition must be true"
        assert stats["hits"] == 1, "Condition must be true"
        assert stats["misses"] == 2, "Condition must be true"
        assert stats["valid_entries"] == 2, "Condition must be true"
        assert stats["hit_rate"] == 1.0 / 3.0, "Condition must be true"

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

        assert len(retriever.query_cache.cache) == 2, "Collection must not be empty"
        assert len(retriever.cache_timestamps) == 2, "Collection must not be empty"

        # Wait for expiration
        time.sleep(1.1)

        # Manually invalidate expired
        retriever.invalidate_expired()

        # Expired entries should be removed
        assert len(retriever.query_cache.cache) == 0, "Collection must not be empty"
        assert len(retriever.cache_timestamps) == 0, "Collection must not be empty"

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
        assert results1 == results2, "Result must not be empty"
        assert retriever.query_cache.hits == 1, "hits is not valid"

        # Different min_score should miss cache
        retriever.query_with_cache(query, top_k=5, min_score=0.7)
        assert retriever.query_cache.misses == 2, "misses is not valid"

    def test_cache_stats_with_no_activity(self, sample_index):
        """Test cache stats with no queries"""
        retriever = CachedRetriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        stats = retriever.get_cache_stats()

        assert stats["size"] == 0, "Condition must be true"
        assert stats["hits"] == 0, "Condition must be true"
        assert stats["misses"] == 0, "Condition must be true"
        assert stats["valid_entries"] == 0, "Condition must be true"
        assert stats["hit_rate"] == 0.0, "Condition must be true"

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

        assert results1 == results2, "Result must not be empty"
        assert retriever.query_cache.hits == 1, "hits is not valid"
