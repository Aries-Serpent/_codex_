# Performance Optimization

This prompt guides AI Agents through identifying and resolving performance bottlenecks.

## Context

Use this prompt when performance issues are identified or to proactively optimize code.

## Prompt Template

```
I need help optimizing performance in the Codex repository.

**Performance Issue:**
- Component: [training / inference / data processing / etc.]
- Symptom: [slow execution / high memory / CPU usage]
- Current metrics: [time / memory / throughput]
- Target metrics: [desired improvement]

**Analysis Steps:**

1. **Measure Current Performance**
   ```bash
   # Profile Python code
   python -m cProfile -o profile.stats script.py
   python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
   
   # Memory profiling
   python -m memory_profiler script.py
   
   # Time specific functions
   python -m timeit -s "from module import function" "function(args)"
   ```

2. **Identify Bottlenecks**
   
   **Common Bottlenecks:**
   - I/O operations (file, network, database)
   - Inefficient algorithms (O(n²) vs O(n log n))
   - Unnecessary computations in loops
   - Memory allocations
   - Missing caching
   - Synchronous operations that could be async

3. **Optimization Strategies**

   **Algorithm Optimization:**
   ```python
   # Before: O(n²)
   for i in range(len(data)):
       for j in range(len(data)):
           if data[i] == data[j]:
               # ...
   
   # After: O(n) using set
   unique = set(data)
   for item in unique:
       # ...
   ```

   **Vectorization:**
   ```python
   # Before: Loop
   result = []
   for x in data:
       result.append(x * 2 + 1)
   
   # After: NumPy vectorization
   import numpy as np
   data_np = np.array(data)
   result = data_np * 2 + 1
   ```

   **Caching:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def expensive_function(arg):
       # Expensive computation
       return result
   ```

   **Async I/O:**
   ```python
   # Before: Synchronous
   def fetch_data(urls):
       return [requests.get(url) for url in urls]
   
   # After: Async
   import asyncio
   import aiohttp
   
   async def fetch_data(urls):
       async with aiohttp.ClientSession() as session:
           tasks = [session.get(url) for url in urls]
           return await asyncio.gather(*tasks)
   ```

   **Batch Processing:**
   ```python
   # Before: Process one at a time
   for item in items:
       process(item)
       save(item)
   
   # After: Batch processing
   for batch in chunks(items, batch_size=100):
       processed = [process(item) for item in batch]
       save_batch(processed)
   ```

4. **Memory Optimization**

   **Generator Instead of List:**
   ```python
   # Before: Loads all in memory
   def read_large_file(path):
       return [line for line in open(path)]
   
   # After: Generator
   def read_large_file(path):
       for line in open(path):
           yield line.strip()
   ```

   **Release Resources:**
   ```python
   # Use context managers
   with open(file) as f:
       data = f.read()
   # File automatically closed
   
   # Clear large variables
   del large_data
   gc.collect()
   ```

5. **Codex-Specific Optimizations**

   **Use Performance Module:**
   ```python
   from scripts.space_traversal.performance import (
       cache_result,
       batch_process,
       profile_function
   )
   
   @cache_result(ttl=3600)
   @profile_function
   def expensive_audit_operation(data):
       # Implementation
       pass
   ```

   **Leverage Existing Cache:**
   ```python
   # Check if performance.py cache exists
   from scripts.space_traversal.performance import get_cache_stats
   stats = get_cache_stats()
   ```

6. **Benchmark and Verify**
   ```bash
   # Before optimization
   python -m timeit -n 100 "from module import func; func()"
   
   # After optimization
   python -m timeit -n 100 "from module import func_optimized; func_optimized()"
   
   # Compare results
   # Ensure correctness hasn't changed
   pytest tests/test_module.py -v
   ```

7. **Document Optimization**
   ```python
   def optimized_function(data):
       """
       Process data efficiently using vectorization.
       
       Performance: ~10x faster than previous implementation
       Memory: Reduces peak usage by 50%
       
       Optimization applied: 2024-12-11
       Benchmark: 1000 items in 0.05s (was 0.5s)
       """
       # Implementation
   ```

**Profiling Tools:**

```bash
# Install profiling tools
pip install memory_profiler line_profiler py-spy

# CPU profiling with py-spy
py-spy record -o profile.svg -- python script.py

# Line-by-line profiling
kernprof -l -v script.py

# Memory profiling
mprof run script.py
mprof plot
```

**Performance Checklist:**

- [ ] Identified bottleneck using profiling
- [ ] Measured current performance baseline
- [ ] Applied appropriate optimization technique
- [ ] Benchmarked improvement
- [ ] Verified correctness with tests
- [ ] Documented optimization and metrics
- [ ] Checked for edge cases
- [ ] Considered maintainability vs performance trade-off

**Warning Signs:**

- Premature optimization (optimize only proven bottlenecks)
- Sacrificing code clarity for minimal gains
- Missing test coverage for optimized code
- Not measuring actual improvement
- Over-optimizing non-critical paths

**Repository-Specific Notes:**

For Codex:
- Check `scripts/space_traversal/performance.py` for utilities
- Use existing caching mechanisms
- Profile audit pipeline if slow
- Consider batch operations for large datasets
- Leverage deterministic caching when possible
```

## Examples

### Example 1: Slow Audit Pipeline

```
Issue: Audit taking 5 minutes for 500 files
Analysis: Sequential file processing
Solution: Parallel processing with multiprocessing
Result: Reduced to 1 minute (5x improvement)
```

### Example 2: High Memory Usage

```
Issue: 4GB memory for loading capability scores
Analysis: Loading all data at once
Solution: Stream processing with generators
Result: Peak memory reduced to 400MB (10x improvement)
```

### Example 3: Slow Test Suite

```
Issue: 1000 tests taking 10 minutes
Analysis: Duplicate fixture setup
Solution: Use session-scoped fixtures
Result: Reduced to 3 minutes (3.3x improvement)
```

## Best Practices

1. **Measure First**: Always profile before optimizing
2. **Test After**: Verify correctness after every optimization
3. **Document**: Record metrics and rationale
4. **Iterate**: Start with biggest bottlenecks
5. **Balance**: Consider maintainability vs performance

## Related Prompts

- [Test Failure Debugging](./test-failure-debugging.md)


## References

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [cProfile documentation](https://docs.python.org/3/library/profile.html)
- [Codex performance utilities](../../scripts/space_traversal/performance.py)
