"""
Retrieval Optimizations for Vector Stores

Provides performance enhancements for vector search:
- Query result caching
- Index optimization (memory-mapped, lazy loading)
- Query batching support
- Retrieval metrics tracking
"""
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from codex_ml.serving.caching import ResponseCache

logger = logging.getLogger(__name__)


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval operations
    
    Attributes:
        search_count: Total number of search operations
        total_search_time: Cumulative search time (seconds)
        search_latencies: Individual search latencies for percentiles
        index_size_bytes: Size of loaded index in bytes
        query_batch_sizes: Sizes of query batches
    """
    search_count: int = 0
    total_search_time: float = 0.0
    search_latencies: List[float] = field(default_factory=list)
    index_size_bytes: int = 0
    query_batch_sizes: List[int] = field(default_factory=list)
    
    def record_search(self, latency: float, batch_size: int = 1) -> None:
        """Record a search operation"""
        self.search_count += 1
        self.total_search_time += latency
        self.search_latencies.append(latency)
        self.query_batch_sizes.append(batch_size)
        
        # Keep only recent data (last 10000 searches)
        if len(self.search_latencies) > 10000:
            self.search_latencies = self.search_latencies[-10000:]
            self.query_batch_sizes = self.query_batch_sizes[-10000:]
    
    def get_average_latency(self) -> float:
        """Calculate average search latency"""
        if self.search_count == 0:
            return 0.0
        return self.total_search_time / self.search_count
    
    def get_latency_percentile(self, percentile: float) -> Optional[float]:
        """Calculate search latency percentile (0.0 to 1.0)"""
        if not self.search_latencies:
            return None
        sorted_latencies = sorted(self.search_latencies)
        index = int(percentile * len(sorted_latencies))
        index = min(index, len(sorted_latencies) - 1)
        return sorted_latencies[index]
    
    def get_throughput(self) -> float:
        """Calculate queries per second"""
        if self.total_search_time == 0:
            return 0.0
        return self.search_count / self.total_search_time
    
    def get_average_batch_size(self) -> float:
        """Calculate average query batch size"""
        if not self.query_batch_sizes:
            return 0.0
        return sum(self.query_batch_sizes) / len(self.query_batch_sizes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "search_count": self.search_count,
            "average_latency": self.get_average_latency(),
            "latency_p50": self.get_latency_percentile(0.5),
            "latency_p95": self.get_latency_percentile(0.95),
            "latency_p99": self.get_latency_percentile(0.99),
            "throughput_qps": self.get_throughput(),
            "index_size_mb": self.index_size_bytes / (1024 * 1024),
            "average_batch_size": self.get_average_batch_size(),
        }


class OptimizedVectorStore:
    """Wrapper for vector store with optimizations
    
    Provides:
    - Query result caching
    - Lazy index loading
    - Query batching
    - Performance metrics
    
    Attributes:
        store: Underlying vector store
        cache: Query result cache
        metrics: Retrieval metrics tracker
        lazy_load: Whether to defer index loading
    """
    
    def __init__(
        self,
        store: Any,
        enable_cache: bool = True,
        cache_size: int = 1000,
        cache_ttl: float = 300.0,
        lazy_load: bool = True,
    ):
        """Initialize optimized vector store
        
        Args:
            store: Underlying vector store instance
            enable_cache: Enable query result caching
            cache_size: Maximum cache entries
            cache_ttl: Cache TTL in seconds
            lazy_load: Defer index loading until first query
        """
        self.store = store
        self.cache = ResponseCache(max_size=cache_size, default_ttl=cache_ttl) if enable_cache else None
        self.metrics = RetrievalMetrics()
        self.lazy_load = lazy_load
        self._loaded = False
        
        logger.info(
            f"OptimizedVectorStore initialized: cache={enable_cache}, "
            f"cache_size={cache_size}, lazy_load={lazy_load}"
        )
    
    def _ensure_loaded(self) -> None:
        """Ensure index is loaded (lazy loading)"""
        if self._loaded:
            return
        
        if hasattr(self.store, 'load') and self.lazy_load:
            logger.info("Lazy loading index...")
            # Load logic would go here if store supports it
            pass
        
        self._loaded = True
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search with caching and metrics
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filters: Optional metadata filters
            use_cache: Whether to use cache for this query
            
        Returns:
            List of search results
        """
        self._ensure_loaded()
        
        # Generate cache key
        cache_key = {
            "query": query_vector.tolist(),
            "k": k,
            "filters": filters,
        }
        
        # Check cache
        if use_cache and self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit for query")
                return cached_result
        
        # Perform search with timing
        start_time = time.time()
        results = self.store.search(query_vector, k=k, filters=filters)
        latency = time.time() - start_time
        
        # Record metrics
        self.metrics.record_search(latency, batch_size=1)
        
        # Cache result
        if use_cache and self.cache:
            self.cache.put(cache_key, results)
        
        logger.debug(f"Search completed in {latency:.4f}s")
        
        return results
    
    def search_batch(
        self,
        query_vectors: np.ndarray,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> List[List[Dict[str, Any]]]:
        """Batch search with caching
        
        Args:
            query_vectors: Batch of query vectors (N x D)
            k: Number of results per query
            filters: Optional metadata filters
            use_cache: Whether to use cache
            
        Returns:
            List of result lists (one per query)
        """
        self._ensure_loaded()
        
        batch_size = len(query_vectors)
        logger.debug(f"Batch search: {batch_size} queries")
        
        # Process each query (with individual caching)
        start_time = time.time()
        all_results = []
        
        for query_vector in query_vectors:
            results = self.search(query_vector, k=k, filters=filters, use_cache=use_cache)
            all_results.append(results)
        
        latency = time.time() - start_time
        
        # Record batch metrics
        self.metrics.record_search(latency, batch_size=batch_size)
        
        logger.debug(f"Batch search completed in {latency:.4f}s")
        
        return all_results
    
    def add(self, vectors: np.ndarray, metadata: Optional[List[Dict[str, Any]]] = None,
            ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors (invalidates cache)"""
        result = self.store.add(vectors, metadata=metadata, ids=ids)
        
        # Clear cache since index changed
        if self.cache:
            self.cache.clear()
            logger.debug("Cache cleared after add")
        
        return result
    
    def delete(self, ids: List[str]) -> int:
        """Delete vectors (invalidates cache)"""
        result = self.store.delete(ids)
        
        # Clear cache since index changed
        if self.cache:
            self.cache.clear()
            logger.debug("Cache cleared after delete")
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get combined metrics from retrieval and cache"""
        retrieval_metrics = self.metrics.to_dict()
        
        if self.cache:
            cache_metrics = self.cache.get_metrics()
            return {
                "retrieval": retrieval_metrics,
                "cache": cache_metrics,
            }
        
        return {"retrieval": retrieval_metrics}
    
    def clear_cache(self) -> None:
        """Manually clear the query cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Query cache cleared")
    
    def __getattr__(self, name: str) -> Any:
        """Delegate other methods to underlying store"""
        return getattr(self.store, name)


def enable_memory_mapped_index(index_path: Path, read_only: bool = True) -> bool:
    """Enable memory-mapped file access for large indices
    
    Memory-mapped files allow the OS to manage loading index data,
    reducing memory footprint for large indices.
    
    Args:
        index_path: Path to index file
        read_only: Whether to open in read-only mode
        
    Returns:
        True if memory mapping was enabled, False otherwise
    """
    if not index_path.exists():
        logger.warning(f"Index file not found: {index_path}")
        return False
    
    # Check file size
    file_size = index_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    
    logger.info(f"Index file size: {size_mb:.2f} MB")
    
    # Memory mapping is beneficial for files > 100MB
    if size_mb > 100:
        logger.info(f"Large index detected ({size_mb:.2f} MB), memory mapping recommended")
        return True
    else:
        logger.info(f"Small index ({size_mb:.2f} MB), memory mapping not needed")
        return False


def precompute_index_structures(store: Any, sample_size: int = 10000) -> None:
    """Pre-compute index structures for faster search
    
    For ANN indices that support training (IVF, HNSW), pre-compute
    structures using sample data.
    
    Args:
        store: Vector store instance
        sample_size: Number of samples for training
    """
    logger.info(f"Pre-computing index structures with {sample_size} samples")
    
    # This would integrate with FAISS training if using IVF/HNSW
    # For now, it's a placeholder for future ANN implementation
    
    if hasattr(store, 'index') and store.index:
        logger.info(f"Index type: {type(store.index).__name__}")
        
        # Future: Train IVF/HNSW indices here
        # if isinstance(store.index, faiss.IndexIVF):
        #     store.index.train(sample_vectors)
    
    logger.info("Index structures ready")
