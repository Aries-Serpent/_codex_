# Performance Tuning Guide

**Version**: 1.4.0  
**Last Updated**: 2024-12-09

---

## Overview

Optimize audit pipeline v1.4.0 performance for different scenarios:
- Large codebases (>10,000 files)
- Frequent runs (CI/pre-commit)
- Resource-constrained environments

---

## Quick Wins

### 1. Use Fast Path

Skip non-essential stages:

```bash
# Skips S2 (facets), S5 (gaps), S7 (manifest)
make space-audit-fast

# Equivalent to:
python scripts/space_traversal/audit_runner.py run --skip S2,S5,S7
```

**Time Savings**: 30-40% faster

---

### 2. Disable Expensive Features

```yaml
# workflow.yaml
scoring:
  coverage:
    enabled: false  # Skip coverage if not needed
  dup:
    heuristic: "simple"  # Use fast mode
```

**Time Savings**: 40-60% faster for large evidence sets

---

### 3. Run Specific Stages

```bash
# Only run scoring (if context_index cached)
python scripts/space_traversal/audit_runner.py stage S4

# Or chain specific stages
python scripts/space_traversal/audit_runner.py stage S3
python scripts/space_traversal/audit_runner.py stage S4
```

---

## Optimization Strategies

### For Large Codebases (>10,000 files)

**Problem**: Token-similarity becomes slow with many files

**Solution 1**: Reduce max_pairwise

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 500      # Reduced from 1000
    max_tokens_per_file: 500  # Reduced from 1000
```

**Solution 2**: Use simple heuristic for large capabilities

```yaml
scoring:
  dup:
    heuristic: "simple"  # Fallback to fast O(n) mode
```

**Solution 3**: Filter evidence files

```python
# In custom detector
def detect(file_index):
    # Limit evidence to most relevant files
    evidence = find_evidence(file_index)
    evidence = evidence[:100]  # Cap at 100 files
    return {"evidence_files": evidence, ...}
```

---

### For Frequent Runs (CI/Pre-commit)

**Problem**: Full audit too slow for every commit

**Solution 1**: Cache context index

```bash
# First run (full)
python scripts/space_traversal/audit_runner.py run

# Subsequent runs (skip S1 if no file changes)
if ! git diff --name-only HEAD~1 | grep -q "src/"; then
    echo "No source changes, using cached context"
    python scripts/space_traversal/audit_runner.py stage S3
    python scripts/space_traversal/audit_runner.py stage S4
    python scripts/space_traversal/audit_runner.py stage S6
fi
```

**Solution 2**: Incremental audits

```bash
# Only audit changed capabilities
git diff --name-only HEAD~1 | \
  xargs python scripts/detect_affected_capabilities.py | \
  xargs python scripts/audit_subset.py
```

**Solution 3**: Use fast path

```bash
# Pre-commit hook
make space-audit-fast
```

---

### For Resource-Constrained Environments

**Problem**: High memory usage with token-similarity

**Solution 1**: Reduce token limits

```yaml
scoring:
  dup:
    max_tokens_per_file: 500  # Reduce from 1000
    max_pairwise: 500
```

**Solution 2**: Disable coverage

```yaml
scoring:
  coverage:
    enabled: false
```

**Solution 3**: Run in batches

```bash
# Process capabilities in batches
for batch in {1..10}; do
    python scripts/audit_runner.py stage S4 --capability-batch $batch
done
```

---

## Benchmark Results

### Baseline Configuration

| Codebase Size | Files | Full Audit | Fast Path | Simple Dup | No Coverage |
|---------------|-------|------------|-----------|------------|-------------|
| Small | 1,000 | 15s | 8s | 12s | 13s |
| Medium | 5,000 | 60s | 30s | 45s | 50s |
| Large | 10,000 | 180s | 90s | 120s | 150s |
| X-Large | 50,000 | 900s | 450s | 600s | 750s |

**Environment**: Ubuntu 22.04, Python 3.12, 8 cores, 16GB RAM

---

### Token-Similarity Performance

| max_pairwise | Evidence Files | Time | Memory |
|--------------|----------------|------|--------|
| 100 | 50 | 2s | 100MB |
| 500 | 50 | 5s | 200MB |
| 1000 (default) | 50 | 8s | 300MB |
| 5000 | 50 | 30s | 800MB |
| 1000 | 200 | 45s | 800MB |

---

## Configuration Recommendations

### Development Environment

**Goal**: Fast feedback, comprehensive analysis

```yaml
# workflow.yaml
scoring:
  coverage:
    enabled: true
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 1000
    max_tokens_per_file: 1000
```

**Run**: `make space-audit`

---

### CI Environment

**Goal**: Balance speed and accuracy

```yaml
# workflow.yaml
scoring:
  coverage:
    enabled: true
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 500  # Reduced for speed
    max_tokens_per_file: 500
```

**Run**: `make space-audit-fast`

---

### Pre-commit Hook

**Goal**: Minimal delay, basic validation

```yaml
# workflow.yaml
scoring:
  coverage:
    enabled: false  # Skip coverage check
  dup:
    heuristic: "simple"  # Fast mode
```

**Run**: `make space-audit-fast`

---

### Production Audit (Nightly)

**Goal**: Maximum accuracy

```yaml
# workflow.yaml
scoring:
  coverage:
    enabled: true
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 5000  # High accuracy
    max_tokens_per_file: 2000
```

**Run**: `python scripts/space_traversal/audit_runner.py run`

---

## Monitoring Performance

### Time Each Stage

```bash
time python scripts/space_traversal/audit_runner.py stage S1
time python scripts/space_traversal/audit_runner.py stage S2
time python scripts/space_traversal/audit_runner.py stage S3
time python scripts/space_traversal/audit_runner.py stage S4
time python scripts/space_traversal/audit_runner.py stage S5
time python scripts/space_traversal/audit_runner.py stage S6
time python scripts/space_traversal/audit_runner.py stage S7
```

### Profile with cProfile

```bash
python -m cProfile -o audit.prof scripts/space_traversal/audit_runner.py run

# Analyze profile
python -c "import pstats; p = pstats.Stats('audit.prof'); p.sort_stats('cumulative'); p.print_stats(20)"
```

### Memory Profiling

```bash
pip install memory_profiler

python -m memory_profiler scripts/space_traversal/audit_runner.py run
```

---

## Advanced Optimizations

### 1. Parallel Stage Execution

Some stages can run in parallel:

```bash
# S1 and S2 are independent after initial setup
python scripts/space_traversal/audit_runner.py stage S1 &
python scripts/space_traversal/audit_runner.py stage S2 &
wait

# Then continue
python scripts/space_traversal/audit_runner.py stage S3
```

### 2. Cache Coverage Map

```bash
# Generate once, reuse multiple times
if [ ! -f audit_artifacts/coverage_map.json ]; then
    pytest --cov=src --cov-report=xml
    python scripts/space_traversal/coverage_ingest.py coverage.xml
fi

# Run audit (uses cached coverage)
make space-audit
```

### 3. Distributed Execution

```bash
# Split capabilities across workers
python scripts/split_capabilities.py 4 | \
  xargs -P 4 -I {} python scripts/audit_capability_subset.py {}

# Merge results
python scripts/merge_audit_results.py
```

---

## Troubleshooting Performance Issues

### Audit Takes Too Long

**Diagnose**:
```bash
# Run with verbose mode to see stage timing
python scripts/space_traversal/audit_runner.py run --verbose 2>&1 | grep "Stage S"
```

**Common Causes**:
- Token-similarity with large evidence sets (reduce max_pairwise)
- Many capabilities (use fast path)
- Large files (reduce max_tokens_per_file)

---

### High Memory Usage

**Diagnose**:
```bash
# Monitor memory during run
/usr/bin/time -v python scripts/space_traversal/audit_runner.py run
```

**Solutions**:
- Reduce max_tokens_per_file
- Disable coverage if not needed
- Run capabilities in batches

---

### CPU at 100%

This is **expected** during token-similarity computation (CPU-intensive).

**Solutions**:
- Use simple heuristic for fast runs
- Reduce max_pairwise
- Accept the CPU usage (it's doing work!)

---

## Best Practices

1. **Start with defaults**, profile, then optimize
2. **Use fast path** for pre-commit, full audit for nightly
3. **Cache expensive operations** (coverage generation, context index)
4. **Monitor performance** over time
5. **Balance accuracy vs speed** based on use case

---

## See Also

- [Configuration Guide](./Configuration_v1.4.0.md) - Configuration options
- [Troubleshooting Guide](./Troubleshooting_v1.4.0.md) - Common issues
- [API Reference](./API_Reference_v1.4.0.md) - Module documentation
- [Integration Examples](./Integration_Examples.md) - CI/CD setups
