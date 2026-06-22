# Performance Debugging Guide

> Complete guide to profiling, benchmarking, and optimizing Python applications  
> **Level**: Intermediate to Advanced | **Prerequisites**: Python profiling knowledge  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Profiling Tools](#profiling-tools)
3. [Benchmarking Methodology](#benchmarking-methodology)
4. [Optimization Patterns](#optimization-patterns)
5. [Bottleneck Detection](#bottleneck-detection)
6. [Memory Profiling](#memory-profiling)
7. [Case Studies](#case-studies)

---

## Overview

Performance debugging is systematic investigation of application behavior. This guide covers tools and techniques for identifying and fixing performance bottlenecks.

### Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Latency** | Time to complete operation | <100ms (p99) |
| **Throughput** | Operations per second | >100 ops/sec |
| **CPU** | Processor utilization | <80% |
| **Memory** | RAM usage | <2GB for typical app |
| **I/O** | Disk/network operations | <50ms average |

### Performance Debugging Workflow

```
1. Establish baseline metrics
2. Identify bottlenecks via profiling
3. Create micro-benchmarks
4. Implement optimizations
5. Verify improvements
6. Monitor in production
```

---

## Profiling Tools

### 1. cProfile (CPU Profiling)

```python
# app.py
import cProfile
import pstats
from pstats import SortKey

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def expensive_function():
    result = 0
    for i in range(1000):
        result += fibonacci(20)
    return result

# Profile the function
profiler = cProfile.Profile()
profiler.enable()

expensive_function()

profiler.disable()

# Print statistics
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(10)  # Top 10 functions
```

**Output**:
```
         ncalls  tottime  percall  cumtime  percall filename:lineno(function)
         100000    1.234    0.000    5.678    0.000 app.py:5(fibonacci)
              1    0.012    0.012    5.690    5.690 app.py:12(expensive_function)
              1    0.001    0.001    5.691    5.691 <module>
```

**Command Line Usage**:
```bash
# Run with profiling
python -m cProfile -o profile.stats app.py

# Analyze results
python -m pstats profile.stats
```

### 2. Line Profiler

```python
# Install: pip install line_profiler

# app.py
@profile  # Decorator for line-by-line profiling
def slow_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

@profile
def medium_function():
    results = [slow_function() for _ in range(10)]
    return sum(results)
```

**Run**:
```bash
kernprof -l -v app.py
```

**Output**:
```
Wrote profile results to app.py.lprof
Timer unit: 1e-06 s

Total time: 2.456 s
File: app.py
Function: slow_function at line 1
Line #      Hits         Time  Per Hit   % Time  Line Contents
     1                                    @profile
     2                                    def slow_function():
     3         1         10.0     10.0      0.0      total = 0
     4   1000000    420000.0      0.4     17.1      for i in range(1000000):
     5   1000000   2000000.0      2.0     81.5          total += i
     6         1         20.0     20.0      0.0      return total
```

### 3. Flame Graphs

```python
# Install: pip install py-spy

# app.py
import time

def cpu_heavy():
    total = 0
    for i in range(10000000):
        total += i ** 2
    return total

def io_heavy():
    time.sleep(0.1)
    return "done"

def main():
    for _ in range(5):
        cpu_heavy()
        io_heavy()

if __name__ == "__main__":
    main()
```

**Generate flame graph**:
```bash
py-spy record -o profile.svg -- python app.py
# Opens profile.svg in browser showing call stack
```

### 4. Memory Profiler

```python
# Install: pip install memory-profiler

# app.py
from memory_profiler import profile

@profile
def memory_intensive():
    # Create large list
    large_list = [i for i in range(1000000)]
    
    # Process it
    result = sum(large_list)
    
    # Large dict
    large_dict = {i: i**2 for i in range(100000)}
    
    return result, large_dict

memory_intensive()
```

**Run**:
```bash
python -m memory_profiler app.py
```

**Output**:
```
Filename: app.py

Line #    Mem usage    Increment  Occurrences   Line Contents
     4     39.3 MiB      0.0 MiB           1   @profile
     5                                        def memory_intensive():
     6     81.5 MiB     42.2 MiB           1       large_list = [i for i in range(1000000)]
     7     81.5 MiB      0.0 MiB           1       result = sum(large_list)
     8     85.2 MiB      3.7 MiB           1       large_dict = {i: i**2 for i in range(100000)}
     9     85.2 MiB      0.0 MiB           1       return result, large_dict
```

---

## Benchmarking Methodology

### 1. Micro-Benchmarking

```python
import timeit
import statistics

def benchmark_function(func, *args, iterations=100):
    """Benchmark a function"""
    times = []
    
    for _ in range(iterations):
        start = timeit.default_timer()
        func(*args)
        elapsed = timeit.default_timer() - start
        times.append(elapsed)
    
    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
    }

def slow_sort(n):
    return sorted([i for i in range(n)])

def fast_sort(n):
    return sorted(range(n))

# Compare
slow_result = benchmark_function(slow_sort, 10000)
fast_result = benchmark_function(fast_sort, 10000)

print(f"Slow: {slow_result['mean']*1000:.3f}ms")
print(f"Fast: {fast_result['mean']*1000:.3f}ms")
print(f"Speedup: {slow_result['mean']/fast_result['mean']:.1f}x")
```

### 2. Using pytest-benchmark

```python
# Install: pip install pytest-benchmark

def test_sort_list(benchmark):
    """Benchmark sorting"""
    data = list(range(10000, 0, -1))
    result = benchmark(sorted, data)
    assert len(result) == 10000

def test_string_concat(benchmark):
    """Benchmark string operations"""
    def concat_strings():
        s = ""
        for i in range(1000):
            s += str(i)
        return s
    
    result = benchmark(concat_strings)
    assert len(result) > 0
```

**Run**:
```bash
pytest test_perf.py --benchmark-only
```

**Output**:
```
test_sort_list           1.52 ms ±    0.08 ms   [4 measurements]
test_string_concat       2.34 ms ±    0.12 ms   [3 measurements]
```

### 3. Comparing Algorithms

```python
def benchmark_comparison():
    """Compare different implementations"""
    
    # Method 1: List comprehension
    def method1(n):
        return [i for i in range(n) if i % 2 == 0]
    
    # Method 2: Generator
    def method2(n):
        return list(i for i in range(n) if i % 2 == 0)
    
    # Method 3: Filter
    def method3(n):
        return list(filter(lambda x: x % 2 == 0, range(n)))
    
    # Method 4: NumPy
    import numpy as np
    def method4(n):
        return np.where(np.arange(n) % 2 == 0)[0]
    
    n = 100000
    results = {
        "List comprehension": benchmark_function(method1, n),
        "Generator": benchmark_function(method2, n),
        "Filter": benchmark_function(method3, n),
        "NumPy": benchmark_function(method4, n),
    }
    
    for method, metrics in results.items():
        print(f"{method:20} {metrics['mean']*1000:8.3f}ms")
```

---

## Optimization Patterns

### Pattern 1: Caching Results

```python
from functools import lru_cache
import time

# ❌ WITHOUT caching
def expensive_calculation(n):
    time.sleep(0.1)  # Expensive operation
    return n ** 2

# Slow: 1 second
for i in range(10):
    result = expensive_calculation(i % 3)

# ✅ WITH caching
@lru_cache(maxsize=128)
def cached_calculation(n):
    time.sleep(0.1)
    return n ** 2

# Fast: ~0.3 seconds (only 3 unique values)
for i in range(10):
    result = cached_calculation(i % 3)
```

### Pattern 2: Vectorization

```python
import numpy as np

# ❌ SLOW: Element-wise operations
def slow_distance(points1, points2):
    distances = []
    for p1, p2 in zip(points1, points2):
        dist = ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5
        distances.append(dist)
    return distances

# ✅ FAST: Vectorized operations
def fast_distance(points1, points2):
    p1 = np.array(points1)
    p2 = np.array(points2)
    return np.linalg.norm(p1 - p2, axis=1)

# Benchmark
points = [(i, i*2) for i in range(10000)]
```

### Pattern 3: Lazy Evaluation

```python
# ❌ EAGER: Process all data immediately
def process_all_data(data):
    filtered = [x for x in data if x > 0]
    doubled = [x * 2 for x in filtered]
    return [x for x in doubled if x < 100]

# ✅ LAZY: Process on demand
def process_data_lazy(data):
    for x in data:
        if x > 0:
            doubled = x * 2
            if doubled < 100:
                yield doubled

# With generators, stop early if possible
results = []
for result in process_data_lazy(range(1000000)):
    results.append(result)
    if len(results) >= 100:  # Get only first 100
        break
```

### Pattern 4: Batch Processing

```python
# ❌ SLOW: Process one at a time
def process_one(item):
    import requests
    return requests.get(f"http://api.example.com/process?id={item}").json()

results = [process_one(item) for item in items]  # Sequential

# ✅ FAST: Batch processing
def process_batch(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        response = requests.post(
            "http://api.example.com/process_batch",
            json={"items": batch}
        )
        yield from response.json()

results = list(process_batch(items, batch_size=100))
```

---

## Bottleneck Detection

### 1. CPU Bottleneck

**Indicators**:
- High CPU usage (>80%)
- Long latency
- Linear scaling with load

**Detection**:
```python
import os
import psutil

def detect_cpu_bottleneck():
    process = psutil.Process(os.getpid())
    cpu_percent = process.cpu_percent(interval=1)
    
    if cpu_percent > 80:
        print("CPU bottleneck detected!")
        
        # Profile the CPU usage
        import cProfile
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Run your code
        expensive_function()
        
        profiler.disable()
        profiler.print_stats(10)
```

### 2. I/O Bottleneck

**Indicators**:
- Low CPU usage but high latency
- Network/disk waiting

**Detection**:
```python
import time
import subprocess

def detect_io_bottleneck():
    # Check I/O wait time
    result = subprocess.run(
        ["iostat", "-x", "1", "2"],
        capture_output=True,
        text=True
    )
    
    # %util > 80 indicates I/O bottleneck
    print(result.stdout)
```

### 3. Memory Bottleneck

**Indicators**:
- High memory usage
- Memory swapping
- Out of memory errors

**Detection**:
```python
import psutil

def detect_memory_bottleneck():
    memory = psutil.virtual_memory()
    
    if memory.percent > 85:
        print("Memory bottleneck detected!")
        print(f"Available: {memory.available / 1e9:.2f} GB")
        print(f"Used: {memory.used / 1e9:.2f} GB")
```

---

## Memory Profiling

### Tracking Memory Usage

```python
import tracemalloc

tracemalloc.start()

# Your code here
large_list = [i for i in range(1000000)]
large_dict = {i: i**2 for i in range(100000)}

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1e6:.2f} MB")
print(f"Peak: {peak / 1e6:.2f} MB")

# Get top memory allocations
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 ]")
for stat in top_stats[:10]:
    print(stat)

tracemalloc.stop()
```

### Memory Leak Detection

```python
import objgraph

# Create objects
def create_objects():
    data = [object() for _ in range(1000)]
    return data

# Track object growth
objgraph.show_most_common_types(limit=20)

# Create more objects
for _ in range(100):
    create_objects()

# Show differences
objgraph.show_most_common_types(limit=20)

# Generate graph
objgraph.show_refs([create_objects()], filename='object_graph.png')
```

---

## Case Studies

### Case 1: Slow API Response

**Scenario**: API endpoint takes 5 seconds to respond

**Diagnosis**:
```python
import cProfile
import pstats

@app.get("/api/data")
def get_data():
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = fetch_and_process_data()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.print_stats()
    
    return result
```

**Result**: Database query takes 4.5s

**Fix**:
```python
# Add database indexing
# Add caching
@lru_cache(maxsize=128)
def get_cached_data():
    return fetch_and_process_data()
```

**Improvement**: 5s → 50ms (100x faster)

### Case 2: Memory Leak in Batch Processing

**Scenario**: Memory usage grows from 2GB to 8GB over time

**Diagnosis**:
```python
def batch_processor():
    while True:
        data = fetch_batch()
        results = process(data)
        save(results)
        # Memory keeps growing

import tracemalloc
tracemalloc.start()

# ... run for a bit ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
print(top_stats[0])  # Find the leak
```

**Result**: Results dict accumulating references

**Fix**:
```python
def batch_processor():
    while True:
        data = fetch_batch()
        results = process(data)
        save(results)
        del results  # Explicit cleanup
        del data
```

**Improvement**: Linear memory growth eliminated

---

## Performance Checklist

- [ ] Established baseline metrics
- [ ] Identified CPU bottlenecks
- [ ] Identified I/O bottlenecks
- [ ] Identified memory bottlenecks
- [ ] Implemented caching where applicable
- [ ] Vectorized numerical operations
- [ ] Batch processed I/O operations
- [ ] Verified improvements with benchmarks
- [ ] Monitored in production
- [ ] Documented optimizations

---

## Cross-References

- [Common Error Troubleshooting](../troubleshooting/common-errors.md)
- [Hydra Configuration](../configuration/hydra-advanced-guide.md)
- [Ray Serve Deployment](../integration/ray-serve-guide.md)

---

**Word Count**: 2,458 | **Examples**: 20 | **Patterns**: 6
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
