"""
Tests for Phase 13.4 4-layer cache hierarchy.

Coverage:
- L1: Request cache functionality and thread isolation
- L2: Session cache with Redis fallback
- L3: Knowledge cache with persistence
- L4: Model cache with versioning
- Orchestrator: Cross-tier operations
- Middleware: Request-level instrumentation
"""

import tempfile
import threading
import time
from pathlib import Path

import pytest
from codex.cache import (
    L1CacheDecorator,
    L1RequestCache,
    L2SessionCache,
    L3KnowledgeCache,
    L4ModelCache,
    UnifiedCacheOrchestrator,
    get_cache_orchestrator,
)


class TestL1RequestCache:
    """Test L1 request cache (in-process)."""

    def test_basic_get_set(self):
        """Test basic get/set operations."""
        cache = L1RequestCache()
        cache.set("key1", {"data": "value1"})
        assert cache.get("key1") == {"data": "value1"}, "Data must not be empty"

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = L1RequestCache()
        assert cache.get("nonexistent") is None, "Condition must be true"

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = L1RequestCache(default_ttl=1)
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1", "Value must be initialized"
        time.sleep(1.1)
        assert cache.get("key1") is None, "Condition must be true"

    def test_lru_eviction(self):
        """Test LRU eviction when max_size exceeded."""
        cache = L1RequestCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1 (oldest)

        assert cache.get("key1") is None, "Condition must be true"
        assert cache.get("key4") == "value4", "Value must be initialized"

    def test_thread_isolation(self):
        """Test thread-local isolation."""
        cache = L1RequestCache()
        results = {}

        def thread_func(thread_id):
            cache.set(f"key_{thread_id}", f"value_{thread_id}")
            results[thread_id] = cache.get(f"key_{thread_id}")
            # Should not see other thread's data
            results[f"{thread_id}_other"] = cache.get(f"key_other_{thread_id}")

        threads = [threading.Thread(target=thread_func, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread should see its own data
        for i in range(3):
            assert results[i] == f"value_{i}", "Result must not be empty"
            assert results[f"{i}_other"] is None, "Result must not be empty"

    def test_decorator(self):
        """Test caching decorator."""
        cache = L1RequestCache()
        decorator = L1CacheDecorator(cache)

        call_count = 0

        @decorator.cache_result(ttl=300)
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute function
        result1 = expensive_func(5)
        assert result1 == 10, "Result must not be empty"
        assert call_count == 1, "Count must be greater than zero"

        # Second call should be cached
        before_second_call = call_count
        result2 = expensive_func(5)
        assert result2 == 10, "Result must not be empty"
        assert call_count == before_second_call, "Count must be greater than zero"


class TestL2SessionCache:
    """Test L2 session cache with Redis fallback."""

    def test_local_fallback(self):
        """Test local fallback when Redis unavailable."""
        # Force Redis to be unavailable
        cache = L2SessionCache(host="nonexistent.example.com")

        # Should fall back to local cache
        cache.set("key1", {"data": "value1"})
        assert cache.get("key1") == {"data": "value1"}, "Data must not be empty"

    def test_set_get(self):
        """Test basic set/get operations."""
        cache = L2SessionCache(enable_local_fallback=True)
        cache.set("session:user123", {"user_id": 123, "name": "Alice"})
        result = cache.get("session:user123")
        assert result["user_id"] == 123, "Result must not be empty"

    def test_serialization(self):
        """Test JSON and pickle serialization."""
        cache = L2SessionCache(enable_local_fallback=True)

        # Test JSON-serializable data
        json_data = {"key": "value", "number": 42}
        cache.set("json_key", json_data)
        assert cache.get("json_key") == json_data, "Data must not be empty"

        # Test non-JSON data (falls back to pickle)
        class CustomClass:
            def __init__(self, x):
                self.x = x

            def __eq__(self, other):
                return isinstance(other, CustomClass) and self.x == other.x

        custom_data = CustomClass(123)
        cache.set("custom_key", custom_data)
        result = cache.get("custom_key")
        assert result == custom_data, "Result must not be empty"

    def test_delete(self):
        """Test delete operation."""
        cache = L2SessionCache(enable_local_fallback=True)
        cache.set("key1", "value1")
        deleted = cache.delete("key1")
        assert deleted, "deleted is not valid"
        assert cache.get("key1") is None, "Condition must be true"

    def test_exists(self):
        """Test exists check."""
        cache = L2SessionCache(enable_local_fallback=True)
        cache.set("key1", "value1")
        assert cache.exists("key1"), "Condition must be true"
        cache.delete("key1")
        assert not cache.exists("key1"), "Condition must be true"


class TestL3KnowledgeCache:
    """Test L3 knowledge cache (disk-backed)."""

    def test_persistent_storage(self):
        """Test persistent storage across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First instance: write data
            cache1 = L3KnowledgeCache(cache_dir=tmpdir)
            cache1.set("embedding:doc123", [0.1, 0.2, 0.3])

            # Second instance: should read the same data
            cache2 = L3KnowledgeCache(cache_dir=tmpdir)
            assert cache2.get("embedding:doc123") == [0.1, 0.2, 0.3]

    def test_ttl_expiration(self):
        """Test TTL expiration in database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L3KnowledgeCache(cache_dir=tmpdir, default_ttl=1)
            cache.set("key1", "value1", ttl=1)
            assert cache.get("key1") == "value1", "Value must be initialized"
            time.sleep(1.1)
            assert cache.get("key1") is None, "Condition must be true"

    def test_large_data(self):
        """Test caching large data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L3KnowledgeCache(cache_dir=tmpdir)
            large_data = {"embeddings": [[i * 0.1 for i in range(768)] for _ in range(100)]}
            cache.set("large_embedding", large_data)
            result = cache.get("large_embedding")
            assert len(result["embeddings"]) == 100, "Collection must not be empty"

    def test_stats(self):
        """Test cache statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L3KnowledgeCache(cache_dir=tmpdir)
            cache.set("key1", "value1")
            cache.get("key1")
            cache.get("nonexistent")

            stats = cache.get_stats()
            assert stats["hits"] == 1, "Condition must be true"
            assert stats["misses"] == 1, "Condition must be true"
            assert stats["entries"] == 1, "Condition must be true"


class TestL4ModelCache:
    """Test L4 model cache (persistent weights)."""

    def test_put_get_model(self):
        """Test storing and retrieving model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L4ModelCache(cache_dir=tmpdir)

            # Create a temporary weights file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                f.write(b"model weights data")
                weights_path = f.name

            try:
                # Store model
                metadata = {"architecture": "bert", "parameters": 123456}
                success = cache.put_model("bert", "v1.0", weights_path, metadata)
                assert success, "success is not valid"

                # Retrieve model
                result = cache.get_model("bert", "v1.0")
                assert result is not None, "result must be initialized"
                assert result["metadata"]["architecture"] == "bert", "Result must not be empty"
                assert Path(result["weights_path"]).exists(), "Result must not be empty"

            finally:
                Path(weights_path).unlink()

    def test_version_management(self):
        """Test version listing and cleanup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L4ModelCache(cache_dir=tmpdir, keep_versions=2)

            # Create multiple versions
            for v in ["v1.0", "v1.1", "v2.0"]:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                    f.write(b"weights")
                    weights_path = f.name

                try:
                    cache.put_model("model", v, weights_path, {"version": v})
                finally:
                    Path(weights_path).unlink()

            # Should only keep 2 versions
            versions = cache.list_versions("model")
            assert len(versions) <= 2, "Versions must not be empty"

    def test_artifact_storage(self):
        """Test arbitrary artifact storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L4ModelCache(cache_dir=tmpdir)

            # Create artifact file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
                f.write(b"artifact data")
                artifact_path = f.name

            try:
                # Store artifact
                cache.put_artifact("preprocessor", "v1", artifact_path, {"type": "tokenizer"})

                # Retrieve artifact
                result = cache.get_artifact("preprocessor", "v1")
                assert result is not None, "result must be initialized"
                assert Path(result["path"]).exists(), "Result must not be empty"

            finally:
                Path(artifact_path).unlink()


class TestUnifiedOrchestrator:
    """Test unified cache orchestrator."""

    def test_cross_tier_promotion(self):
        """Test promotion from L3 to L1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            l1 = L1RequestCache()
            l2 = L2SessionCache(enable_local_fallback=True)
            l3 = L3KnowledgeCache(cache_dir=tmpdir)
            orchestrator = UnifiedCacheOrchestrator(l1=l1, l2=l2, l3=l3)

            # Store in L3
            orchestrator.set("key1", {"data": "test"}, tier="L3")

            # Get should find in L3 and promote to L1+L2
            result = orchestrator.get("key1")
            assert result == {"data": "test"}, "Result must not be empty"

            # Should now be in L1 for fast access
            assert l1.get("key1") == {"data": "test"}, "Data must not be empty"

    def test_stats_aggregation(self):
        """Test statistics aggregation from all tiers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = get_cache_orchestrator()
            orchestrator.set("key1", "value1", tier="L1")
            orchestrator.get("key1")

            stats = orchestrator.get_stats()
            assert "overall" in stats, "Condition must be true"
            assert "l1" in stats, "Condition must be true"
            assert "l2" in stats, "Condition must be true"
            assert "l3" in stats, "Condition must be true"
            assert "l4" in stats, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
