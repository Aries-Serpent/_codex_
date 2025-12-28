# Inference Performance Optimization Guide

Strategies and techniques for optimizing ML model inference performance.

## Overview

This guide covers performance optimization techniques for production inference, including model optimization, batching strategies, caching, and hardware acceleration.

## Performance Targets

### Latency Goals

| Use Case | Target Latency | Acceptable P99 |
|----------|----------------|----------------|
| Real-time API | < 100ms | < 200ms |
| Batch Processing | < 1s per item | < 2s |
| Async Processing | < 5s | < 10s |

### Throughput Goals

- **Single GPU**: 100-1000 req/s (model dependent)
- **Multi-GPU**: Linear scaling up to 4 GPUs
- **CPU**: 10-100 req/s (for simple models)

## Model Optimization

### Quantization

**INT8 Quantization:**
```python
import torch

# Post-training quantization
model_fp32 = load_model()
model_int8 = torch.quantization.quantize_dynamic(
    model_fp32,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Results: 4x smaller, 2-4x faster
```

**Benefits:**
- 4x model size reduction
- 2-4x inference speedup
- Minimal accuracy loss (< 1%)

### Model Pruning

```python
import torch.nn.utils.prune as prune

# Structured pruning
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        prune.l1_unstructured(module, name='weight', amount=0.3)

# Remove pruning reparameterization
for module in model.modules():
    if isinstance(module, torch.nn.Linear):
        prune.remove(module, 'weight')
```

### Knowledge Distillation

Train smaller "student" model from larger "teacher":

```python
def distillation_loss(student_logits, teacher_logits, temperature=3.0):
    """Compute distillation loss."""
    soft_targets = F.softmax(teacher_logits / temperature, dim=1)
    soft_prob = F.log_softmax(student_logits / temperature, dim=1)
    
    return F.kl_div(soft_prob, soft_targets, reduction='batchmean') * (temperature ** 2)
```

## Batching Strategies

### Dynamic Batching

```python
from collections import deque
import asyncio

class DynamicBatcher:
    def __init__(self, max_batch_size=32, max_wait_ms=10):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = deque()
        self.batch_ready = asyncio.Event()
    
    async def add_request(self, data):
        """Add request to batch queue."""
        future = asyncio.Future()
        self.queue.append((data, future))
        
        if len(self.queue) >= self.max_batch_size:
            self.batch_ready.set()
        
        return await future
    
    async def process_batches(self):
        """Process batches continuously."""
        while True:
            # Wait for batch or timeout
            try:
                await asyncio.wait_for(
                    self.batch_ready.wait(),
                    timeout=self.max_wait_ms / 1000
                )
            except asyncio.TimeoutError:
                pass
            
            if self.queue:
                batch = self._create_batch()
                results = await self._process_batch(batch)
                self._return_results(batch, results)
            
            self.batch_ready.clear()
```

### Batch Size Optimization

```python
def find_optimal_batch_size(model, input_shape, device='cuda'):
    """Find optimal batch size for throughput."""
    batch_sizes = [1, 2, 4, 8, 16, 32, 64]
    best_throughput = 0
    best_batch_size = 1
    
    for bs in batch_sizes:
        try:
            dummy_input = torch.randn(bs, *input_shape).to(device)
            
            # Warmup
            for _ in range(10):
                _ = model(dummy_input)
            
            # Benchmark
            start = time.time()
            for _ in range(100):
                _ = model(dummy_input)
            duration = time.time() - start
            
            throughput = (100 * bs) / duration
            
            if throughput > best_throughput:
                best_throughput = throughput
                best_batch_size = bs
                
        except RuntimeError:  # OOM
            break
    
    return best_batch_size, best_throughput
```

## Caching Strategies

### Response Caching

```python
from functools import lru_cache
import hashlib

class PredictionCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get_cache_key(self, input_data):
        """Generate cache key from input."""
        return hashlib.sha256(
            str(input_data).encode()
        ).hexdigest()
    
    def get(self, input_data):
        """Get cached prediction."""
        key = self.get_cache_key(input_data)
        
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, input_data, prediction):
        """Cache prediction."""
        if len(self.cache) >= self.max_size:
            # LRU eviction
            self.cache.pop(next(iter(self.cache)))
        
        key = self.get_cache_key(input_data)
        self.cache[key] = prediction
    
    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
```

### Feature Caching

```python
class FeatureCache:
    """Cache expensive feature computations."""
    
    def __init__(self):
        self.cache = {}
    
    def get_features(self, input_id, compute_fn):
        """Get or compute features."""
        if input_id not in self.cache:
            self.cache[input_id] = compute_fn()
        return self.cache[input_id]
```

## Hardware Acceleration

### GPU Optimization

**Mixed Precision Training:**
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

@torch.no_grad()
def predict_fp16(model, input_data):
    """Inference with FP16 for 2x speedup."""
    with autocast():
        output = model(input_data)
    return output
```

**CUDA Streams:**
```python
import torch.cuda as cuda

# Multiple streams for parallel execution
stream1 = cuda.Stream()
stream2 = cuda.Stream()

with cuda.stream(stream1):
    output1 = model1(input1)

with cuda.stream(stream2):
    output2 = model2(input2)

cuda.synchronize()
```

### TensorRT Optimization

```python
import torch_tensorrt

# Compile model with TensorRT
trt_model = torch_tensorrt.compile(
    model,
    inputs=[torch_tensorrt.Input((1, 3, 224, 224))],
    enabled_precisions={torch.half},
    workspace_size=1 << 30
)

# 2-5x speedup for inference
```

### ONNX Runtime

```python
import onnxruntime as ort

# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=14
)

# Load with ONNX Runtime
session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

# Run inference
outputs = session.run(None, {'input': input_data.numpy()})
```

## Memory Optimization

### Gradient Checkpointing

```python
from torch.utils.checkpoint import checkpoint

class OptimizedModel(nn.Module):
    def forward(self, x):
        # Use checkpointing for memory-intensive layers
        x = checkpoint(self.layer1, x)
        x = checkpoint(self.layer2, x)
        return x
```

### Model Parallelism

```python
class ParallelModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(1000, 1000).to('cuda:0')
        self.layer2 = nn.Linear(1000, 1000).to('cuda:1')
    
    def forward(self, x):
        x = self.layer1(x.to('cuda:0'))
        x = self.layer2(x.to('cuda:1'))
        return x
```

## Profiling

### PyTorch Profiler

```python
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True
) as prof:
    model(input_data)

# Print profiling results
print(prof.key_averages().table(sort_by="cuda_time_total"))

# Export for visualization
prof.export_chrome_trace("trace.json")
```

### Bottleneck Analysis

```python
import cProfile
import pstats

def profile_inference():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run inference
    for _ in range(100):
        model.predict(sample_input)
    
    profiler.disable()
    
    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

## Load Testing

### Locust Load Test

```python
from locust import HttpUser, task, between

class InferenceUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    @task
    def predict(self):
        self.client.post(
            "/predict",
            json={"data": generate_test_data()}
        )
```

### Performance Benchmarks

```python
def benchmark_model(model, num_runs=1000):
    """Benchmark model performance."""
    latencies = []
    
    # Warmup
    for _ in range(10):
        _ = model(sample_input)
    
    # Measure
    for _ in range(num_runs):
        start = time.perf_counter()
        _ = model(sample_input)
        latency = time.perf_counter() - start
        latencies.append(latency)
    
    return {
        'mean': np.mean(latencies),
        'p50': np.percentile(latencies, 50),
        'p95': np.percentile(latencies, 95),
        'p99': np.percentile(latencies, 99)
    }
```

## Best Practices

### Optimization Checklist

- [ ] Profile before optimizing
- [ ] Set baseline metrics
- [ ] Use appropriate batch sizes
- [ ] Enable mixed precision
- [ ] Implement caching where applicable
- [ ] Use hardware acceleration
- [ ] Monitor resource utilization
- [ ] Load test before production

### Common Pitfalls

**Avoid:**
- Over-batching (increases latency)
- Excessive logging in hot path
- Synchronous I/O operations
- Memory leaks from tensor accumulation
- Sub-optimal data loading

## Resources

- [PyTorch Performance Tuning](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [TensorRT Documentation](https://docs.nvidia.com/deeplearning/tensorrt/)
- [ONNX Runtime Performance](https://onnxruntime.ai/docs/performance/)
- [Model Optimization Toolkit](https://github.com/microsoft/onnxruntime)

## Related Guides

- [Inference Monitoring](inference_monitoring.md)
- [Inference Deployment](inference_deployment.md)
- [Production ML Guide](../docs/ml_ops/production_guide.md)
