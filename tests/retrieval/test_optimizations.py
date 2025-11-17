"""Tests for retrieval optimizations"""
import time
import numpy as np
import pytest
from unittest.mock import Mock, MagicMock
from src.codex.retrieval.optimizations import (
    OptimizedVectorStore,
    RetrievalMetrics,
    enable_memory_mapped_index,
    precompute_index_structures,
)


class TestRetrievalMetrics:
    """Test retrieval metrics tracking"""
    
    def test_initialization(self):
        """Test metrics initialization"""
        metrics = RetrievalMetrics()
        assert metrics.search_count == 0
        assert metrics.total_search_time == 0.0
        assert len(metrics.search_latencies) == 0
        assert metrics.index_size_bytes == 0
    
    def test_record_search(self):
        """Test recording search operations"""
        metrics = RetrievalMetrics()
        metrics.record_search(0.1, batch_size=1)
        metrics.record_search(0.2, batch_size=5)
        metrics.record_search(0.15, batch_size=1)
        
        assert metrics.search_count == 3
        assert metrics.total_search_time == 0.45
        assert len(metrics.search_latencies) == 3
        assert len(metrics.query_batch_sizes) == 3
    
    def test_average_latency(self):
        """Test average latency calculation"""
        metrics = RetrievalMetrics()
        metrics.record_search(0.1)
        metrics.record_search(0.2)
        metrics.record_search(0.3)
        
        assert metrics.get_average_latency() == 0.2
    
    def test_latency_percentiles(self):
        """Test latency percentile calculation"""
        metrics = RetrievalMetrics()
        latencies = [0.1, 0.2, 0.3, 0.4, 0.5]
        for lat in latencies:
            metrics.record_search(lat)
        
        # p50 should be around 0.3
        p50 = metrics.get_latency_percentile(0.5)
        assert 0.25 <= p50 <= 0.35
        
        # p95 should be close to 0.5
        p95 = metrics.get_latency_percentile(0.95)
        assert 0.45 <= p95 <= 0.5
    
    def test_throughput(self):
        """Test throughput calculation"""
        metrics = RetrievalMetrics()
        metrics.record_search(0.1)
        metrics.record_search(0.1)
        metrics.record_search(0.1)
        
        # 3 searches in 0.3s = 10 qps
        throughput = metrics.get_throughput()
        assert 9.0 <= throughput <= 11.0
    
    def test_average_batch_size(self):
        """Test average batch size calculation"""
        metrics = RetrievalMetrics()
        metrics.record_search(0.1, batch_size=1)
        metrics.record_search(0.1, batch_size=5)
        metrics.record_search(0.1, batch_size=10)
        
        # (1+5+10)/3 = 5.33
        avg_batch = metrics.get_average_batch_size()
        assert 5.0 <= avg_batch <= 5.5
    
    def test_to_dict(self):
        """Test metrics dictionary conversion"""
        metrics = RetrievalMetrics()
        metrics.record_search(0.1, batch_size=2)
        metrics.index_size_bytes = 1024 * 1024  # 1 MB
        
        metrics_dict = metrics.to_dict()
        assert "search_count" in metrics_dict
        assert "average_latency" in metrics_dict
        assert "latency_p50" in metrics_dict
        assert "latency_p95" in metrics_dict
        assert "latency_p99" in metrics_dict
        assert "throughput_qps" in metrics_dict
        assert "index_size_mb" in metrics_dict
        assert "average_batch_size" in metrics_dict
        
        assert metrics_dict["search_count"] == 1
        assert metrics_dict["index_size_mb"] == 1.0


class TestOptimizedVectorStore:
    """Test optimized vector store wrapper"""
    
    def test_initialization(self):
        """Test store initialization"""
        mock_store = Mock()
        optimized = OptimizedVectorStore(
            store=mock_store,
            enable_cache=True,
            cache_size=100,
            lazy_load=True,
        )
        
        assert optimized.store == mock_store
        assert optimized.cache is not None
        assert optimized.lazy_load is True
        assert not optimized._loaded
    
    def test_initialization_without_cache(self):
        """Test store initialization without cache"""
        mock_store = Mock()
        optimized = OptimizedVectorStore(
            store=mock_store,
            enable_cache=False,
        )
        
        assert optimized.cache is None
    
    def test_search_with_cache(self):
        """Test search with caching enabled"""
        mock_store = Mock()
        mock_store.search = Mock(return_value=[{"id": "1", "score": 0.9}])
        
        optimized = OptimizedVectorStore(store=mock_store, enable_cache=True)
        
        query = np.array([1.0, 2.0, 3.0])
        
        # First search (cache miss)
        result1 = optimized.search(query, k=5)
        assert result1 == [{"id": "1", "score": 0.9}]
        assert mock_store.search.call_count == 1
        
        # Second search (cache hit)
        result2 = optimized.search(query, k=5)
        assert result2 == [{"id": "1", "score": 0.9}]
        assert mock_store.search.call_count == 1  # Not called again
        
        # Check metrics
        metrics = optimized.get_metrics()
        assert metrics["retrieval"]["search_count"] == 2
        assert metrics["cache"]["hits"] == 1
        assert metrics["cache"]["misses"] == 1
    
    def test_search_without_cache(self):
        """Test search with caching disabled"""
        mock_store = Mock()
        mock_store.search = Mock(return_value=[{"id": "1", "score": 0.9}])
        
        optimized = OptimizedVectorStore(store=mock_store, enable_cache=False)
        
        query = np.array([1.0, 2.0, 3.0])
        
        # Both searches should hit the store
        result1 = optimized.search(query, k=5)
        result2 = optimized.search(query, k=5)
        
        assert mock_store.search.call_count == 2
    
    def test_search_batch(self):
        """Test batch search"""
        mock_store = Mock()
        mock_store.search = Mock(return_value=[{"id": "1", "score": 0.9}])
        
        optimized = OptimizedVectorStore(store=mock_store, enable_cache=True)
        
        queries = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
        ])
        
        results = optimized.search_batch(queries, k=5)
        
        assert len(results) == 3
        assert all(len(r) == 1 for r in results)  # Each query returns 1 result
        
        # Should have called search 3 times (once per query)
        assert mock_store.search.call_count == 3
        
        # Check metrics
        metrics = optimized.get_metrics()
        assert metrics["retrieval"]["search_count"] == 4  # 3 individual + 1 batch
    
    def test_add_clears_cache(self):
        """Test that adding vectors clears cache"""
        mock_store = Mock()
        mock_store.search = Mock(return_value=[{"id": "1"}])
        mock_store.add = Mock(return_value=["new_id"])
        
        optimized = OptimizedVectorStore(store=mock_store, enable_cache=True)
        
        # Populate cache
        query = np.array([1.0, 2.0, 3.0])
        optimized.search(query)
        
        # Add vectors (should clear cache)
        vectors = np.array([[1.0, 2.0, 3.0]])
        optimized.add(vectors)
        
        # Verify cache was cleared
        assert len(optimized.cache) == 0
    
    def test_delete_clears_cache(self):
        """Test that deleting vectors clears cache"""
        mock_store = Mock()
        mock_store.search = Mock(return_value=[{"id": "1"}])
        mock_store.delete = Mock(return_value=1)
        
        optimized = OptimizedVectorStore(store=mock_store, enable_cache=True)
        
        # Populate cache
        query = np.array([1.0, 2.0, 3.0])
        optimized.search(query)
        
        # Delete vectors (should clear cache)
        optimized.delete(["id1"])
        
        # Verify cache was cleared
        assert len(optimized.cache) == 0
    
    def test_clear_cache(self):
        """Test manual cache clearing"""
        mock_store = Mock()
        mock_store.search = Mock(return_value=[{"id": "1"}])
        
        optimized = OptimizedVectorStore(store=mock_store, enable_cache=True)
        
        # Populate cache
        query = np.array([1.0, 2.0, 3.0])
        optimized.search(query)
        
        assert len(optimized.cache) > 0
        
        # Clear cache manually
        optimized.clear_cache()
        
        assert len(optimized.cache) == 0
    
    def test_method_delegation(self):
        """Test that unknown methods are delegated to underlying store"""
        mock_store = Mock()
        mock_store.some_custom_method = Mock(return_value="custom_result")
        
        optimized = OptimizedVectorStore(store=mock_store)
        
        result = optimized.some_custom_method()
        assert result == "custom_result"
        mock_store.some_custom_method.assert_called_once()


class TestMemoryMappedIndex:
    """Test memory-mapped index utilities"""
    
    def test_nonexistent_file(self, tmp_path):
        """Test with nonexistent file"""
        index_path = tmp_path / "nonexistent.index"
        result = enable_memory_mapped_index(index_path)
        assert result is False
    
    def test_small_file(self, tmp_path):
        """Test with small file (< 100MB)"""
        index_path = tmp_path / "small.index"
        index_path.write_bytes(b"x" * (50 * 1024 * 1024))  # 50 MB
        
        result = enable_memory_mapped_index(index_path)
        assert result is False  # Not recommended for small files
    
    def test_large_file(self, tmp_path):
        """Test with large file (> 100MB)"""
        index_path = tmp_path / "large.index"
        index_path.write_bytes(b"x" * (150 * 1024 * 1024))  # 150 MB
        
        result = enable_memory_mapped_index(index_path)
        assert result is True  # Recommended for large files


class TestPrecomputeIndexStructures:
    """Test index structure pre-computation"""
    
    def test_with_index(self):
        """Test with store that has an index"""
        mock_store = Mock()
        mock_store.index = MagicMock()
        
        # Should not raise exception
        precompute_index_structures(mock_store, sample_size=100)
    
    def test_without_index(self):
        """Test with store that has no index"""
        mock_store = Mock()
        mock_store.index = None
        
        # Should not raise exception
        precompute_index_structures(mock_store, sample_size=100)
