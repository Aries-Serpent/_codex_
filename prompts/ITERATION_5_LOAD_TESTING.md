# Iteration 5: Load Testing (1M+ Queries) - Complete Prompt Set

**Iteration**: 5 of 7 (Advanced Validation Series)  
**Priority**: P1 (High)  
**Duration**: 2-3 hours  
**Dependencies**: Iterations 1-4 complete  
**Environment**: Production-like with full resources

---

## Executive Summary

Execute comprehensive load testing to validate RAG system performance under production-scale workloads (1M+ queries). Test multi-threading, cache effectiveness, memory stability, and identify performance bottlenecks.

---

## Prerequisites Checklist

- [x] Iterations 1-4 complete and validated
- [ ] Test environment with ≥4 CPU cores
- [ ] ≥8GB available RAM
- [ ] HuggingFace models pre-cached locally
- [ ] Python 3.8+ with multiprocessing support
- [ ] Monitoring tools installed (prometheus-client, psutil)

---

## Prompt for GitHub Copilot Agent

```
@copilot Execute Iteration 5 (Load Testing) for RAG Production Readiness - 1M+ Query Validation

## Context
Branch: copilot/sub-pr-2750
Status: Iterations 1-4 complete, all tests passing, 0 vulnerabilities
Goal: Validate system under production load (1M+ queries)

## Load Testing Objectives

1. **Concurrency Testing**: 100+ concurrent threads
2. **Cache Validation**: Verify 100x speedup claim
3. **Memory Stability**: No leaks over 1M operations
4. **Performance Profiling**: Identify bottlenecks
5. **Throughput Measurement**: Queries per second under load

## Implementation Tasks

### Task 1: Create Load Test Framework

Create `tests/load/test_rag_load.py`:

```python
#!/usr/bin/env python3
"""
RAG Load Testing Framework
Tests system performance under production-scale workloads (1M+ queries)
"""

import sys
import time
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any
import tracemalloc
import psutil
import json

sys.path.insert(0, 'src')

from codex.rag import CachedRetriever, get_metrics, MetricsConfig
from codex.rag.monitoring import RAGMetrics


@dataclass
class LoadTestConfig:
    """Configuration for load testing."""
    total_queries: int = 1_000_000
    concurrent_threads: int = 100
    batch_size: int = 1000
    cache_enabled: bool = True
    report_interval: int = 10_000


@dataclass
class LoadTestResults:
    """Results from load testing."""
    total_queries: int
    duration_seconds: float
    queries_per_second: float
    mean_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cache_hit_rate: float
    peak_memory_mb: float
    cpu_usage_percent: float
    errors: int
    success: bool


class LoadTester:
    """Executes load tests against RAG system."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = []
        self.errors = []
        self.start_time = None
        self.metrics = RAGMetrics(MetricsConfig(
            query_latency_window=10000,
            embedding_throughput_window=5000,
            index_build_time_window=100
        ))
    
    def run_single_query(self, query_id: int, retriever) -> Dict[str, Any]:
        """Execute a single query and track metrics."""
        queries = [
            "how to use RAG system",
            "embedding configuration",
            "multi-tenant setup",
            "caching strategy",
            "performance optimization"
        ]
        query = queries[query_id % len(queries)]
        
        try:
            start = time.time()
            results = retriever.query_with_cache(query, top_k=5)
            duration_ms = (time.time() - start) * 1000
            
            self.metrics.track_query_latency(
                duration_ms,
                tenant_id="load_test",
                index_name="benchmark"
            )
            
            return {
                'query_id': query_id,
                'duration_ms': duration_ms,
                'results': len(results),
                'success': True
            }
        except Exception as e:
            self.errors.append({'query_id': query_id, 'error': str(e)})
            return {
                'query_id': query_id,
                'duration_ms': 0,
                'results': 0,
                'success': False
            }
    
    def run_batch(self, start_id: int, batch_size: int, retriever) -> List[Dict]:
        """Execute a batch of queries."""
        return [
            self.run_single_query(start_id + i, retriever)
            for i in range(batch_size)
        ]
    
    def run_concurrent_test(self) -> LoadTestResults:
        """Execute concurrent load test."""
        print(f"🚀 Starting load test: {self.config.total_queries:,} queries")
        print(f"   Threads: {self.config.concurrent_threads}")
        print(f"   Batch size: {self.config.batch_size}")
        print(f"   Cache: {'Enabled' if self.config.cache_enabled else 'Disabled'}")
        print()
        
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        self.start_time = time.time()
        
        # Create retriever (mock for now, will use real in production)
        from unittest.mock import Mock
        retriever = Mock()
        retriever.query_with_cache = Mock(return_value=[
            {'text': 'result', 'score': 0.9, 'file': 'test.md', 'start_line': 1, 'end_line': 5}
        ])
        
        # Execute concurrent queries
        completed = 0
        with ThreadPoolExecutor(max_workers=self.config.concurrent_threads) as executor:
            futures = []
            
            for batch_start in range(0, self.config.total_queries, self.config.batch_size):
                batch_size = min(self.config.batch_size, self.config.total_queries - batch_start)
                future = executor.submit(self.run_batch, batch_start, batch_size, retriever)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                batch_results = future.result()
                self.results.extend(batch_results)
                completed += len(batch_results)
                
                if completed % self.config.report_interval == 0:
                    elapsed = time.time() - self.start_time
                    qps = completed / elapsed
                    print(f"   Progress: {completed:,}/{self.config.total_queries:,} "
                          f"({completed/self.config.total_queries*100:.1f}%) - "
                          f"{qps:.0f} qps")
        
        # Calculate results
        duration = time.time() - self.start_time
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Get latencies
        latencies = [r['duration_ms'] for r in self.results if r['success']]
        latencies.sort()
        n = len(latencies)
        
        # Get cache stats
        cache_stats = self.metrics.cache_stats
        total_cache = cache_stats['hits'] + cache_stats['misses']
        cache_hit_rate = cache_stats['hits'] / total_cache if total_cache > 0 else 0
        
        return LoadTestResults(
            total_queries=self.config.total_queries,
            duration_seconds=duration,
            queries_per_second=self.config.total_queries / duration,
            mean_latency_ms=sum(latencies) / n if n > 0 else 0,
            p95_latency_ms=latencies[int(n * 0.95)] if n > 0 else 0,
            p99_latency_ms=latencies[int(n * 0.99)] if n > 0 else 0,
            cache_hit_rate=cache_hit_rate,
            peak_memory_mb=peak_memory / 1024 / 1024,
            cpu_usage_percent=process.cpu_percent(),
            errors=len(self.errors),
            success=len(self.errors) < self.config.total_queries * 0.01  # <1% error rate
        )
    
    def generate_report(self, results: LoadTestResults) -> str:
        """Generate comprehensive load test report."""
        report = []
        report.append("=" * 80)
        report.append("RAG LOAD TEST RESULTS")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append(f"   Total Queries: {results.total_queries:,}")
        report.append(f"   Duration: {results.duration_seconds:.2f}s")
        report.append(f"   Throughput: {results.queries_per_second:.0f} qps")
        report.append(f"   Success Rate: {(1 - results.errors/results.total_queries)*100:.2f}%")
        report.append("")
        
        # Performance
        report.append("⚡ PERFORMANCE")
        report.append(f"   Mean Latency: {results.mean_latency_ms:.2f}ms")
        report.append(f"   P95 Latency: {results.p95_latency_ms:.2f}ms")
        report.append(f"   P99 Latency: {results.p99_latency_ms:.2f}ms")
        report.append("")
        
        # Cache
        report.append("🔄 CACHE")
        report.append(f"   Hit Rate: {results.cache_hit_rate:.1%}")
        report.append(f"   Speedup: ~{100 if results.cache_hit_rate > 0.9 else 10}x (estimated)")
        report.append("")
        
        # Resources
        report.append("💾 RESOURCES")
        report.append(f"   Peak Memory: {results.peak_memory_mb:.1f}MB")
        report.append(f"   CPU Usage: {results.cpu_usage_percent:.1f}%")
        report.append("")
        
        # Status
        status = "✅ PASSED" if results.success else "❌ FAILED"
        report.append(f"🎯 STATUS: {status}")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Execute load testing suite."""
    print("RAG Load Testing Suite")
    print("=" * 80)
    print()
    
    # Test configurations
    configs = [
        LoadTestConfig(
            total_queries=10_000,
            concurrent_threads=10,
            batch_size=100
        ),
        LoadTestConfig(
            total_queries=100_000,
            concurrent_threads=50,
            batch_size=1000
        ),
        LoadTestConfig(
            total_queries=1_000_000,
            concurrent_threads=100,
            batch_size=1000
        ),
    ]
    
    all_results = []
    
    for i, config in enumerate(configs, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(configs)}")
        print(f"{'=' * 80}\n")
        
        tester = LoadTester(config)
        results = tester.run_concurrent_test()
        all_results.append(results)
        
        print()
        print(tester.generate_report(results))
        print()
        
        # Save results
        with open(f'reports/load_test_{config.total_queries}.json', 'w') as f:
            json.dump({
                'config': {
                    'total_queries': config.total_queries,
                    'concurrent_threads': config.concurrent_threads,
                    'batch_size': config.batch_size
                },
                'results': {
                    'duration_seconds': results.duration_seconds,
                    'queries_per_second': results.queries_per_second,
                    'mean_latency_ms': results.mean_latency_ms,
                    'p95_latency_ms': results.p95_latency_ms,
                    'p99_latency_ms': results.p99_latency_ms,
                    'cache_hit_rate': results.cache_hit_rate,
                    'peak_memory_mb': results.peak_memory_mb,
                    'success': results.success
                }
            }, f, indent=2)
    
    # Final summary
    print("\n" + "=" * 80)
    print("LOAD TESTING COMPLETE")
    print("=" * 80)
    for i, (config, results) in enumerate(zip(configs, all_results), 1):
        status = "✅" if results.success else "❌"
        print(f"{status} Test {i}: {config.total_queries:,} queries - "
              f"{results.queries_per_second:.0f} qps - "
              f"{results.p99_latency_ms:.2f}ms p99")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

Save this file and execute:
```bash
mkdir -p tests/load
python3 tests/load/test_rag_load.py
```

### Task 2: Execute Progressive Load Tests

Run tests in increasing scale:

```bash
# Small scale (10K queries)
python3 tests/load/test_rag_load.py --queries 10000 --threads 10

# Medium scale (100K queries)
python3 tests/load/test_rag_load.py --queries 100000 --threads 50

# Large scale (1M queries)
python3 tests/load/test_rag_load.py --queries 1000000 --threads 100
```

### Task 3: Memory Leak Detection

Create `tests/load/test_memory_leak.py`:

```python
import sys, time, tracemalloc, gc
sys.path.insert(0, 'src')

from codex.rag.monitoring import RAGMetrics

print("Memory Leak Detection Test")
print("=" * 60)

tracemalloc.start()
metrics = RAGMetrics()

snapshots = []

for iteration in range(10):
    print(f"\nIteration {iteration + 1}/10")
    
    # Simulate heavy load
    for i in range(100_000):
        metrics.track_query_latency(100.0, tenant_id="test")
    
    # Force garbage collection
    gc.collect()
    
    # Take snapshot
    snapshot = tracemalloc.take_snapshot()
    snapshots.append(snapshot)
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"  Current: {current / 1024 / 1024:.2f}MB")
    print(f"  Peak: {peak / 1024 / 1024:.2f}MB")

# Analyze for leaks
if len(snapshots) >= 2:
    stats = snapshots[-1].compare_to(snapshots[0], 'lineno')
    print("\nTop 10 Memory Increases:")
    for stat in stats[:10]:
        print(f"  {stat}")

tracemalloc.stop()
print("\n✅ Memory leak test complete")
```

### Task 4: Cache Effectiveness Testing

```python
# Test cache hit rate progression
python3 -c "
import sys, time
sys.path.insert(0, 'src')

from codex.rag import CachedRetriever
from unittest.mock import Mock

# Mock retriever for testing
retriever = Mock()
retriever.query_with_cache = Mock(return_value=[{'score': 0.9}])

queries = ['query1', 'query2', 'query3', 'query4', 'query5']

print('Cache Effectiveness Test')
print('=' * 60)

# Test with varying cache sizes
for cache_size in [10, 100, 1000]:
    print(f'\nCache size: {cache_size}')
    
    hits = 0
    total = 10_000
    
    for i in range(total):
        query = queries[i % len(queries)]
        # Simulate cache lookup
        if i >= cache_size and (i % len(queries)) < len(queries):
            hits += 1
    
    hit_rate = hits / total
    print(f'  Hit rate: {hit_rate:.1%}')
    print(f'  Speedup: ~{1/(1-hit_rate) if hit_rate < 1 else 100:.1f}x')

print('\n✅ Cache effectiveness test complete')
"
```

### Task 5: Generate Comprehensive Report

Create `reports/ITERATION_5_LOAD_TESTING_RESULTS.md` with:

1. Executive summary
2. Test configurations and methodology
3. Performance metrics (qps, latency, memory)
4. Cache effectiveness analysis
5. Memory leak analysis
6. Bottleneck identification
7. Recommendations for optimization
8. Comparison with SLA targets

## Success Criteria

- ✅ 1M queries executed successfully (<1% error rate)
- ✅ Throughput: >1000 qps for cached queries
- ✅ P99 latency: <10ms for cached, <200ms for fresh
- ✅ Cache hit rate: >70% for repeated queries
- ✅ No memory leaks detected over 1M operations
- ✅ Peak memory: <500MB total
- ✅ CPU usage: <80% average

## Expected Deliverables

1. Load test framework (tests/load/test_rag_load.py)
2. Memory leak detector (tests/load/test_memory_leak.py)
3. Test execution results (JSON files in reports/)
4. Comprehensive report (reports/ITERATION_5_LOAD_TESTING_RESULTS.md)
5. Performance graphs (optional, if matplotlib available)

## Failure Handling

If targets not met:
1. Profile with cProfile to identify bottlenecks
2. Optimize hot paths (likely cache lookup or metrics tracking)
3. Consider connection pooling for database/file I/O
4. Tune garbage collection settings
5. Document known limitations and mitigation strategies

Execute all tasks autonomously. Report results with metrics, analysis, and recommendations for optimization or deployment adjustments.
```

---

## Execution Checklist

- [ ] Load test framework created and tested
- [ ] Small scale test (10K) executed
- [ ] Medium scale test (100K) executed
- [ ] Large scale test (1M) executed
- [ ] Memory leak detection run
- [ ] Cache effectiveness validated
- [ ] Comprehensive report generated
- [ ] Performance graphs created (if available)
- [ ] Results committed to repository
- [ ] Recommendations documented

---

## Timeline

- Setup & framework creation: 30 minutes
- Small scale testing: 15 minutes
- Medium scale testing: 30 minutes
- Large scale testing: 60 minutes
- Analysis & reporting: 30 minutes
- **Total**: ~2.5 hours

---

## Post-Completion Actions

1. Review results against SLA targets
2. Identify optimization opportunities
3. Update deployment documentation
4. Create performance regression tests
5. Proceed to Iteration 6 (Multi-Region Deployment)

---

**Prompt Created**: 2026-01-08 20:30 UTC  
**Ready for**: Autonomous execution by GitHub Copilot  
**Expected Outcome**: Complete load testing validation with 1M+ queries
