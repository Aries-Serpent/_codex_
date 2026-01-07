# Performance Optimization Guide

**Version:** 1.0  
**Last Updated:** Previous Cycle-11-17  
**Component:** Inference Serving & Vector Retrieval

---

## Table of Contents

1. [Overview](#overview)
2. [Request Batching](#request-batching)
3. [Response Caching](#response-caching)
4. [Retrieval Optimizations](#retrieval-optimizations)
5. [Resilience Patterns](#resilience-patterns)
6. [Performance Metrics](#performance-metrics)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers performance optimization techniques for the _codex_ inference serving and vector retrieval systems. These optimizations can significantly improve throughput, latency, and reliability.

### Key Optimizations

| Optimization | Benefit | Use Case |
|--------------|---------|----------|
| Request Batching | 2-5x throughput increase | High request volume |
| Response Caching | 50-90% latency reduction | Repeated queries |
| Query Caching | 30-70% latency reduction | Similar searches |
| Circuit Breaker | Prevents cascading failures | Unstable services |
| Retry with Backoff | Handles transient failures | Network issues |

---

## Request Batching

Request batching accumulates multiple requests and processes them together, improving throughput at the cost of slightly increased latency.

### Basic Usage

```python
from codex_ml.serving.batching import BatchingMiddleware

def process_batch(inputs):
    """Process a batch of inputs"""
    # Your model inference here
    return [model.predict(x) for x in inputs]

# Create batching middleware
batching = BatchingMiddleware(
    process_fn=process_batch,
    max_batch_size=32,      # Process up to 32 requests together
    max_wait_time=0.1,      # Wait max 100ms before flushing
)

# Process requests (automatically batched)
async def handle_request(data):
    result = await batching.process(data)
    return result
```text

### Configuration

```python
# Low latency (interactive)
batching = BatchingMiddleware(
    max_batch_size=8,
    max_wait_time=0.05,  # 50ms
)

# High throughput (batch jobs)
batching = BatchingMiddleware(
    max_batch_size=128,
    max_wait_time=0.5,  # 500ms
)

# Balanced
batching = BatchingMiddleware(
    max_batch_size=32,
    max_wait_time=0.1,  # 100ms (default)
)
```text

### Performance Metrics

```python
# Get batching metrics
metrics = batching.get_metrics()

print(f"Requests: {metrics['request_count']}")
print(f"Batches: {metrics['batch_count']}")
print(f"Avg latency: {metrics['average_latency']:.3f}s")
print(f"p95 latency: {metrics['latency_p95']:.3f}s")
print(f"Throughput: {metrics['throughput_rps']:.1f} req/s")
print(f"Avg batch size: {metrics['average_batch_size']:.1f}")
```text

### Trade-offs

**Pros:**
- Significantly improves throughput (2-5x typical)
- Better GPU utilization
- Reduces per-request overhead

**Cons:**
- Slightly increases latency (by max_wait_time)
- Requires async/await support
- Memory usage scales with batch size

---

## Response Caching

Response caching stores results of previous predictions, eliminating redundant computation for repeated queries.

### Basic Usage

```python
from codex_ml.serving.caching import ResponseCache

# Create cache
cache = ResponseCache(
    max_size=1000,      # Cache up to 1000 responses
    default_ttl=300.0,  # 5 minute TTL
)

# Cache prediction results
def predict_with_cache(input_data):
    # Check cache
    result = cache.get(input_data)
    if result is not None:
        return result
    
    # Compute result
    result = model.predict(input_data)
    
    # Store in cache
    cache.put(input_data, result)
    
    return result
```text

### Configuration

```python
# Short-lived cache (real-time data)
cache = ResponseCache(
    max_size=500,
    default_ttl=60.0,  # 1 minute
)

# Long-lived cache (static data)
cache = ResponseCache(
    max_size=5000,
    default_ttl=3600.0,  # 1 hour
)

# No expiration (until evicted)
cache = ResponseCache(
    max_size=10000,
    default_ttl=0,  # No TTL
)
```text

### Cache Metrics

```python
metrics = cache.get_metrics()

print(f"Hits: {metrics['hits']}")
print(f"Misses: {metrics['misses']}")
print(f"Hit rate: {metrics['hit_rate']:.1%}")
print(f"Evictions: {metrics['evictions']}")
print(f"Size: {metrics['total_size']}/{metrics['max_size']}")
print(f"Utilization: {metrics['memory_utilization']:.1%}")
```text

### Cache Management

```python
# Clear cache manually
cache.clear()

# Remove expired entries
removed = cache.remove_expired()
print(f"Removed {removed} expired entries")

# Check if key exists (not expired)
if input_data in cache:
    print("Cached result available")
```text

### Trade-offs

**Pros:**
- Dramatic latency reduction (50-90% for cache hits)
- Reduced computational cost
- Protects against duplicate requests

**Cons:**
- Memory usage (scales with cache size)
- Stale results (if data changes frequently)
- Cache invalidation complexity

---

## Retrieval Optimizations

Retrieval optimizations improve vector search performance through query caching and index optimizations.

### Optimized Vector Store

```python
from codex.retrieval.optimizations import OptimizedVectorStore
from codex.retrieval.stores.faiss_store import FAISSStore

# Create base store
base_store = FAISSStore(index_name="my_index")

# Wrap with optimizations
optimized_store = OptimizedVectorStore(
    store=base_store,
    enable_cache=True,
    cache_size=1000,
    cache_ttl=300.0,
    lazy_load=True,
)

# Search (automatically cached)
results = optimized_store.search(query_vector, k=10)
```text

### Batch Search

```python
# Search multiple queries efficiently
query_vectors = np.array([
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6],
    [0.7, 0.8, 0.9],
])

# Batch search with caching
results = optimized_store.search_batch(query_vectors, k=10)
```text

### Retrieval Metrics

```python
metrics = optimized_store.get_metrics()

# Retrieval metrics
print(f"Searches: {metrics['retrieval']['search_count']}")
print(f"Avg latency: {metrics['retrieval']['average_latency']:.3f}s")
print(f"p95 latency: {metrics['retrieval']['latency_p95']:.3f}s")
print(f"Throughput: {metrics['retrieval']['throughput_qps']:.1f} queries/s")

# Cache metrics
print(f"Hit rate: {metrics['cache']['hit_rate']:.1%}")
print(f"Cache size: {metrics['cache']['total_size']}")
```text

### Memory-Mapped Indices

For large indices (>100MB), enable memory-mapped file access:

```python
from codex.retrieval.optimizations import enable_memory_mapped_index
from pathlib import Path

index_path = Path(".codex/faiss/my_index.faiss")

# Check if memory mapping is recommended
should_mmap = enable_memory_mapped_index(index_path)

if should_mmap:
    print("Large index detected, using memory-mapped files")
    # FAISS will automatically use memory mapping
```text

### Trade-offs

**Pros:**
- 30-70% latency reduction for repeated queries
- Memory-efficient for large indices
- Transparent caching layer

**Cons:**
- Cache invalidation on add/delete
- Memory usage for cache
- Slightly increased complexity

---

## Resilience Patterns

Resilience patterns improve reliability and prevent cascading failures.

### Circuit Breaker

Prevents requests to a failing service, allowing time for recovery:

```python
from codex_ml.serving.resilience import CircuitBreaker, CircuitBreakerConfig

# Create circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,    # Open after 5 failures
    success_threshold=2,    # Close after 2 successes
    timeout=60.0,          # Wait 60s before retry
    half_open_max_calls=3, # Test with 3 calls
)
breaker = CircuitBreaker(config)

# Use circuit breaker
def call_external_service():
    response = requests.post("http://localhost:8080/predict", ...)
    return response.json()

try:
    result = breaker.call(call_external_service)
except Exception as e:
    print(f"Circuit breaker: {e}")
```text

### Retry with Exponential Backoff

Handle transient failures with automatic retries:

```python
from codex_ml.serving.resilience import retry_with_backoff

# Retry with exponential backoff
result = retry_with_backoff(
    call_external_service,
    max_retries=3,
    initial_delay=1.0,     # Start with 1s
    max_delay=60.0,        # Cap at 60s
    backoff_factor=2.0,    # Double each time
    exceptions=(requests.RequestException,),
)
```text

### Fallback Handler

Gracefully degrade with fallback strategies:

```python
from codex_ml.serving.resilience import FallbackHandler

def fallback_prediction():
    # Return a default or cached prediction
    return {"prediction": "default", "confidence": 0.0}

handler = FallbackHandler(
    fallback_func=fallback_prediction,
    use_cache=True,
    cache=response_cache,
)

# Call with fallback
result = handler.call_with_fallback(
    model.predict,
    fallback_key=input_data,
    input_data,
)
```text

### Combined Resilience

```python
# Combine patterns for maximum reliability
def resilient_predict(input_data):
    # 1. Check cache first
    cached = cache.get(input_data)
    if cached:
        return cached
    
    # 2. Use circuit breaker + retry
    def predict_with_retry():
        return retry_with_backoff(
            model.predict,
            max_retries=3,
            initial_delay=1.0,
            input_data,
        )
    
    try:
        result = breaker.call(predict_with_retry)
        cache.put(input_data, result)
        return result
    except Exception:
        # 3. Fallback to last known good result
        return fallback_handler.call_with_fallback(
            lambda: model.predict(input_data),
            fallback_key=input_data,
        )
```text

---

## Performance Metrics

### Comprehensive Monitoring

```python
class PerformanceMonitor:
    """Centralized performance monitoring"""
    
    def __init__(self):
        self.batching = batching_middleware
        self.cache = response_cache
        self.retrieval = optimized_store
        self.circuit_breaker = circuit_breaker
    
    def get_all_metrics(self):
        return {
            "batching": self.batching.get_metrics(),
            "cache": self.cache.get_metrics(),
            "retrieval": self.retrieval.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_state(),
        }
    
    def print_summary(self):
        metrics = self.get_all_metrics()
        
        print("=== Performance Summary ===")
        print(f"\nBatching:")
        print(f"  Throughput: {metrics['batching']['throughput_rps']:.1f} req/s")
        print(f"  Avg latency: {metrics['batching']['average_latency']:.3f}s")
        print(f"  p95 latency: {metrics['batching']['latency_p95']:.3f}s")
        
        print(f"\nCache:")
        print(f"  Hit rate: {metrics['cache']['hit_rate']:.1%}")
        print(f"  Size: {metrics['cache']['total_size']}")
        
        print(f"\nRetrieval:")
        print(f"  Throughput: {metrics['retrieval']['retrieval']['throughput_qps']:.1f} q/s")
        print(f"  p95 latency: {metrics['retrieval']['retrieval']['latency_p95']:.3f}s")
        
        print(f"\nCircuit Breaker:")
        print(f"  State: {metrics['circuit_breaker']['state']}")
        print(f"  Failures: {metrics['circuit_breaker']['failure_count']}")
```text

---

## Best Practices

### 1. Start Simple, Optimize Based on Metrics

```python
# Begin with no optimizations
results = model.predict(inputs)

# Measure performance
# Only add optimizations if needed based on metrics
```text

### 2. Choose Appropriate Batch Sizes

```python
# GPU workloads: larger batches (32-128)
batching = BatchingMiddleware(max_batch_size=64)

# CPU workloads: smaller batches (8-32)
batching = BatchingMiddleware(max_batch_size=16)

# Real-time: minimal batching
batching = BatchingMiddleware(max_batch_size=4, max_wait_time=0.02)
```text

### 3. Set Appropriate TTLs

```python
# Static data: long TTL
cache = ResponseCache(default_ttl=3600)  # 1 hour

# Dynamic data: short TTL
cache = ResponseCache(default_ttl=60)  # 1 minute

# Real-time data: no caching
# Don't use cache for time-sensitive predictions
```text

### 4. Monitor and Tune

```python
# Regular monitoring
def monitor_performance():
    metrics = monitor.get_all_metrics()
    
    # Alert on low hit rate
    if metrics['cache']['hit_rate'] < 0.3:
        logger.warning("Low cache hit rate, consider increasing cache size")
    
    # Alert on high latency
    if metrics['batching']['latency_p95'] > 1.0:
        logger.warning("High p95 latency, consider tuning batch parameters")
```text

---

## Troubleshooting

### High Latency

**Symptoms:** p95 latency > 1s

**Solutions:**
1. Reduce `max_wait_time` in batching
2. Increase cache size and TTL
3. Enable query result caching
4. Check for slow external dependencies

### Low Cache Hit Rate

**Symptoms:** Hit rate < 30%

**Solutions:**
1. Increase cache size
2. Increase cache TTL
3. Check if queries are truly repeated
4. Verify cache key generation is deterministic

### Memory Issues

**Symptoms:** High memory usage, OOM errors

**Solutions:**
1. Reduce cache max_size
2. Reduce batching max_batch_size
3. Enable memory-mapped indices for FAISS
4. Regularly call `cache.remove_expired()`

### Circuit Breaker Stuck Open

**Symptoms:** All requests rejected

**Solutions:**
1. Check if underlying service recovered
2. Manually reset: `breaker.reset()`
3. Increase `timeout` value
4. Reduce `failure_threshold`

### Batch Processing Delays

**Symptoms:** High latency variance

**Solutions:**
1. Reduce `max_wait_time`
2. Adjust `max_batch_size` to workload
3. Monitor `average_batch_size` metric
4. Consider disabling batching for low-volume

---

## Summary

### Quick Reference

| Problem | Solution | Tool |
|---------|----------|------|
| Low throughput | Enable batching | `BatchingMiddleware` |
| High latency | Enable caching | `ResponseCache` |
| Repeated queries | Query caching | `OptimizedVectorStore` |
| Service failures | Circuit breaker | `CircuitBreaker` |
| Transient errors | Retry with backoff | `retry_with_backoff` |
| Need fallback | Fallback handler | `FallbackHandler` |

### Recommended Starting Configuration

```python
# Production-ready configuration
batching = BatchingMiddleware(max_batch_size=32, max_wait_time=0.1)
cache = ResponseCache(max_size=1000, default_ttl=300.0)
optimized_store = OptimizedVectorStore(store, enable_cache=True)
breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=5, timeout=60.0))
```text

---

**For questions or issues, see the main project documentation or open an issue on GitHub.**
