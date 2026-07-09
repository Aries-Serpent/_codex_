# Performance Tuning Guide

**Version:** 0.1.0  
**Last Updated:** 2026-07-09  
**Audience:** MLOps, Performance Engineers, DevOps

---

## Table of Contents

1. [Caching Strategies](#caching-strategies)
2. [Batch Inference](#batch-inference)
3. [Async Processing](#async-processing)
4. [Resource Allocation](#resource-allocation)
5. [Monitoring](#monitoring)

---

## Caching Strategies

### Multi-Layer Cache

Codex implements 4-layer caching for optimal performance:

```python
from codex.ml import CachedInferencePipeline

pipeline = CachedInferencePipeline(
    model="bert-base",
    cache_layers={
        "http": True,          # HTTP 304 Not Modified responses
        "model": True,         # Model output cache
        "data": True,          # Embedding cache
        "compute": True        # Intermediate results cache
    },
    ttl_seconds=3600           # Time-to-live: 1 hour
)

# Repeated inference hits cache
results1 = pipeline(["Hello world"], batch_size=1)
results2 = pipeline(["Hello world"], batch_size=1)  # Cached!
```

### Cache Configuration

```yaml
# cache_config.yaml
cache:
  layers:
    http:
      enabled: true
      ttl_seconds: 1800        # 30 minutes
      max_size_mb: 100
    model:
      enabled: true
      ttl_seconds: 3600        # 1 hour
      max_size_mb: 500
    data:
      enabled: true
      ttl_seconds: 7200        # 2 hours
      max_size_mb: 1000
    compute:
      enabled: true
      ttl_seconds: 600         # 10 minutes
      max_size_mb: 200
```

### Cache Hit Rate Optimization

```python
# Monitor cache hit rate
from codex.ml import CacheMonitor

monitor = CacheMonitor()
hit_rate = monitor.get_hit_rate()
print(f"Cache hit rate: {hit_rate:.1%}")

# Target: 70-90% for production

# If hit rate is low:
# 1. Increase cache TTL
# 2. Pre-load common queries
# 3. Increase cache size
```

---

## Batch Inference

### Optimal Batch Size

```python
from codex.ml import InferencePipeline

pipeline = InferencePipeline("bert-base")
texts = load_texts("data/test.txt")  # 1000 texts

# Benchmark different batch sizes
results = {}
for batch_size in [1, 8, 16, 32, 64, 128]:
    start = time.time()
    predictions = pipeline(texts, batch_size=batch_size)
    elapsed = time.time() - start
    
    throughput = len(texts) / elapsed
    results[batch_size] = {
        'latency_ms': (elapsed / len(texts)) * 1000,
        'throughput': throughput,
        'memory_mb': get_memory_usage()
    }

# Find optimal batch size
optimal_bs = max(results, key=lambda bs: results[bs]['throughput'])
print(f"Optimal batch size: {optimal_bs}")
print(f"Throughput: {results[optimal_bs]['throughput']:.0f} samples/sec")
```

### Performance Metrics by Batch Size

| Batch Size | Latency | Throughput | Memory | Notes |
|------------|---------|-----------|--------|-------|
| 1 | 150ms | 6 samples/s | 256MB | Minimum throughput |
| 8 | 80ms | 100 samples/s | 512MB | Balanced |
| 16 | 60ms | 266 samples/s | 1GB | Good throughput |
| 32 | 50ms | 640 samples/s | 2GB | **Recommended** |
| 64 | 45ms | 1428 samples/s | 4GB | High throughput |
| 128 | 50ms | 2560 samples/s | 8GB | Risk of OOM |

### Adaptive Batch Sizing

```python
from codex.ml import AdaptiveInferencePipeline

pipeline = AdaptiveInferencePipeline("bert-base")

# Automatically adjusts batch size based on:
# - Available memory
# - Queue depth
# - Latency targets
# - Throughput requirements

results = pipeline(texts)  # Optimal batch size chosen automatically
```

---

## Async Processing

### Non-Blocking Inference

```python
import asyncio
from codex.ml import AsyncInferencePipeline

async def score_async(texts):
    pipeline = AsyncInferencePipeline("bert-base")
    results = await pipeline(texts, batch_size=32)
    return results

# Run async
results = asyncio.run(score_async(texts))
```

### I/O-Bound Optimization

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Use thread pool for I/O operations
with ThreadPoolExecutor(max_workers=4) as executor:
    loop = asyncio.get_event_loop()
    
    tasks = [
        loop.run_in_executor(executor, fetch_data, url)
        for url in urls
    ]
    
    results = await asyncio.gather(*tasks)
```

---

## Resource Allocation

### CPU Tuning

```python
import os

# Set number of threads
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'

# Verify
from codex.ml import get_resource_info
info = get_resource_info()
print(f"Allocated CPUs: {info.cpu_count}")
```

### GPU Optimization

```python
import torch

# Check GPU availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPUs: {torch.cuda.device_count()}")

# Set GPU device
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Create pipeline on GPU
from codex.ml import InferencePipeline
pipeline = InferencePipeline("bert-base", device=device)

# Monitor GPU memory
print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
print(f"GPU memory reserved: {torch.cuda.memory_reserved(0) / 1e9:.1f}GB")
print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1e9:.1f}GB")

# Clear GPU memory if needed
torch.cuda.empty_cache()
```

### Memory Optimization

```python
# Use smaller model
from codex.ml import InferencePipeline

# Full-size model: 350MB
# model = InferencePipeline("bert-base-uncased")

# Distilled model: 65MB (10x smaller)
pipeline = InferencePipeline("distilbert-base-uncased")

# TinyBERT: 15MB (23x smaller, slightly less accurate)
# pipeline = InferencePipeline("distilbert-base-multilingual-cased")
```

---

## Monitoring

### Prometheus Metrics

```python
from codex.ml import MetricsCollector

collector = MetricsCollector()

# Latency histogram (in milliseconds)
# codex_inference_latency_ms_bucket
# codex_inference_latency_ms_count
# codex_inference_latency_ms_sum

# Throughput gauge (samples/second)
# codex_inference_throughput_samples_per_sec

# Cache hit rate (0-1)
# codex_cache_hit_rate

# Error rate
# codex_error_rate_total
```

### Performance Dashboard

Create Grafana dashboard with key metrics:

- **Latency (p50, p95, p99)**
  - Target: <100ms p95
  - Alert: >200ms p95

- **Throughput**
  - Target: >100 samples/sec
  - Alert: <50 samples/sec

- **Cache Hit Rate**
  - Target: >70%
  - Alert: <50%

- **Error Rate**
  - Target: <0.1%
  - Alert: >1%

### Logging for Performance Analysis

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Enable performance logging
logger = logging.getLogger('codex.ml.performance')

# Logs include:
# - Batch size used
# - Latency per batch
# - Cache hit/miss
# - Memory usage
# - GPU utilization
```

---

## Performance Tuning Checklist

- [ ] Batch size optimized (target: 32)
- [ ] Cache layers enabled (target: >70% hit rate)
- [ ] GPU enabled (if available)
- [ ] Async processing configured
- [ ] Resource limits set
- [ ] Monitoring enabled
- [ ] Baseline metrics recorded
- [ ] SLA targets defined

---

**Last Updated:** 2026-07-09  
**Support:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
