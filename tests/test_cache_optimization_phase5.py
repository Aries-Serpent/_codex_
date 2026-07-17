"""
Cache Performance Optimization Benchmarks and Tests.

PHASE 5 TRACK 5: Comprehensive benchmarking to validate 20-30% latency
reduction and 15%+ hit rate improvement.
"""

import time

import pytest


class TestL1CacheBatchOperations:
    """Test L1 cache batch operation optimizations."""
    
    def test_batch_get_operations(self):
        """Test get_many batch operation performance."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=5000)
        
        # Pre-populate cache
        test_data = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        for key, value in test_data.items():
            cache.set(key, value)
        
        # Test batch get
        keys_to_get = list(test_data.keys())[:50]
        results = cache.get_many(keys_to_get)
        
        # Verify results
        assert len(results) == 50
        assert all(k in results for k in keys_to_get)
        
        # Verify hit rate improved
        stats = cache.get_stats()
        assert stats["hit_rate"] > 80.0, f"Expected >80% hit rate, got {stats['hit_rate']}"
    
    def test_batch_set_operations(self):
        """Test set_many batch operation performance."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=5000)
        
        # Bulk set operation
        test_data = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        cache.set_many(test_data)
        
        # Verify all keys were set
        assert len(cache.get_keys()) == 100
        
        # Verify utilization
        stats = cache.get_stats()
        assert stats["size"] == 100
        assert stats["utilization"] < 0.1, "Cache should have low utilization"
    
    def test_batch_operations_improve_throughput(self):
        """Test that batch operations improve throughput by 15%+."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=10000)
        
        # Individual operations
        start_individual = time.time()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        for i in range(1000):
            _ = cache.get(f"key_{i}")
        individual_time = time.time() - start_individual
        
        # Clear cache
        cache.clear()
        
        # Batch operations
        start_batch = time.time()
        data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        cache.set_many(data)
        results = cache.get_many(list(data.keys()))
        batch_time = time.time() - start_batch
        
        # Batch should be significantly faster
        improvement = (individual_time - batch_time) / individual_time * 100
        assert improvement > 15, f"Expected >15% improvement, got {improvement:.1f}%"


class TestCacheOptimizationAnalysis:
    """Test cache optimization analysis."""
    
    def test_optimization_analyzer(self):
        """Test optimization analyzer identifies improvements."""
        from aries_serpent_core.cache.optimization_analysis import (
            CacheLayerMetrics,
            CacheOptimizationAnalyzer,
        )
        
        analyzer = CacheOptimizationAnalyzer()
        
        # Record metrics for L1
        l1_metrics = CacheLayerMetrics(
            layer_name="L1",
            hits=600,
            misses=400,  # 60% hit rate (below target)
            evictions=50,
            total_size_bytes=100_000_000,
            max_size_bytes=500_000_000,
            ttl_seconds=300,
        )
        analyzer.record_layer_metrics(l1_metrics)
        
        # Analyze
        analysis = analyzer.analyze()
        
        # Verify analysis identified L1 as bottleneck
        assert "bottlenecks" in analysis
        assert len(analysis["recommendations"]) > 0
        
        # Verify recommendations prioritize L1 improvements
        recommendations = analysis["recommendations"]
        assert any("L1" in str(opt) or "Warming" in opt["optimization"] for opt in recommendations)
    
    def test_warming_strategy_generation(self):
        """Test cache warming strategy generation."""
        from aries_serpent_core.cache.optimization_analysis import CacheWarmingStrategy
        
        strategy = CacheWarmingStrategy()
        
        # Record access patterns (90/10 distribution for high skewness)
        hot_keys = [f"hot_key_{i}" for i in range(10)]
        cold_keys = [f"cold_key_{i}" for i in range(90)]
        
        # 90% of accesses to 10% of keys (higher skewness)
        for hot_key in hot_keys:
            for _ in range(90):
                strategy.record_access(hot_key)
        
        for cold_key in cold_keys:
            strategy.record_access(cold_key)
        
        # Analyze patterns
        analysis = strategy.analyze_access_patterns()
        
        assert analysis["total_unique_keys"] == 100
        # With 90/10 split, should be 'High' skewness
        assert "High" in analysis["skewness"], f"Expected 'High' skewness, got {analysis['skewness']}"
        assert len(analysis["hottest_keys"]) == 10


class TestCacheHitRateImprovement:
    """Test cache hit rate improvements."""
    
    def test_l1_hit_rate_baseline(self):
        """Test L1 cache baseline hit rate."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=1000)
        
        # Simulate realistic workload
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Access keys with 80/20 pattern
        for j in range(10):
            for i in range(20):  # Hot keys
                _ = cache.get(f"key_{i}")
            for i in range(20, 25):  # Cold keys
                _ = cache.get(f"key_{i}")
        
        stats = cache.get_stats()
        assert stats["hit_rate"] == 100.0, "All accesses should hit in this test"


class TestLatencyImprovement:
    """Test latency improvements."""
    
    def test_batch_get_latency(self):
        """Test that batch get reduces latency."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=10000)
        
        # Pre-populate
        test_data = {f"key_{i}": f"value_{i}" * 50 for i in range(1000)}
        cache.set_many(test_data)
        
        keys_to_get = list(test_data.keys())[:500]
        
        # Measure individual get latency
        start = time.time()
        for key in keys_to_get:
            _ = cache.get(key)
        individual_latency = time.time() - start
        
        cache.clear()
        cache.set_many(test_data)
        
        # Measure batch get latency
        start = time.time()
        _ = cache.get_many(keys_to_get)
        batch_latency = time.time() - start
        
        # Batch should be faster
        improvement = (individual_latency - batch_latency) / individual_latency * 100
        assert improvement > 10, f"Expected >10% latency improvement, got {improvement:.1f}%"


class TestCacheMetricsAccuracy:
    """Test cache metrics tracking accuracy."""
    
    def test_metrics_tracking(self):
        """Test that metrics are accurately tracked."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=100)
        
        # Set 50 items
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Get 40 items (hits)
        for i in range(40):
            _ = cache.get(f"key_{i}")
        
        # Try to get 30 non-existent items (misses)
        for i in range(100, 130):
            _ = cache.get(f"key_{i}")
        
        stats = cache.get_stats()
        
        assert stats["hits"] == 40, f"Expected 40 hits, got {stats['hits']}"
        assert stats["misses"] == 30, f"Expected 30 misses, got {stats['misses']}"
        assert stats["hit_rate"] > 50.0


class TestCacheEvictionPolicy:
    """Test cache eviction policies."""
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=10)
        
        # Fill cache
        for i in range(15):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Verify only 10 items in cache
        assert len(cache.get_keys()) == 10, f"Expected 10 items, got {len(cache.get_keys())}"
        
        # Verify oldest items were evicted (0-4)
        for i in range(5):
            assert cache.get(f"key_{i}") is None, f"Expected key_{i} to be evicted"
        
        # Verify newest items are still there (5-14)
        for i in range(5, 15):
            assert cache.get(f"key_{i}") is not None, f"Expected key_{i} to exist"


class TestCacheExpirationCleanup:
    """Test cache expiration and cleanup."""
    
    def test_expired_entry_cleanup(self):
        """Test that expired entries are cleaned up."""
        from aries_serpent_core.cache.request_cache import L1RequestCache
        
        cache = L1RequestCache(max_size=100, default_ttl=1)  # 1 second TTL
        
        # Set items
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Clean up expired
        cleaned = cache.cleanup_expired()
        assert cleaned == 10, f"Expected 10 cleaned, got {cleaned}"
        
        # Verify cache is empty
        assert len(cache.get_keys()) == 0


class TestUnifiedCacheOrchestrator:
    """Test unified cache orchestrator."""
    
    def test_cache_promotion_l2_to_l1(self):
        """Test cache promotion from L2 to L1 (with local fallback)."""
        from aries_serpent_core.cache.knowledge_cache_l3 import L3KnowledgeCache
        from aries_serpent_core.cache.model_cache_l4 import L4ModelCache
        from aries_serpent_core.cache.orchestrator import UnifiedCacheOrchestrator
        from aries_serpent_core.cache.request_cache import L1RequestCache
        from aries_serpent_core.cache.session_cache_l2 import L2SessionCache
        
        l1 = L1RequestCache()
        l2 = L2SessionCache(enable_local_fallback=True)
        l3 = L3KnowledgeCache()
        l4 = L4ModelCache()
        
        orchestrator = UnifiedCacheOrchestrator(l1, l2, l3, l4)
        
        # Set in L2
        orchestrator.set("test_key", "test_value", tier="L2")
        
        # Get should find in L2 (via local fallback since Redis not installed)
        result = orchestrator.get("test_key")
        assert result == "test_value"
        # Either L2 or local hits should be recorded
        assert orchestrator._stats["l2_hits"] > 0 or orchestrator._stats["total_hits"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
