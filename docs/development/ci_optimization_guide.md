# CI Workflow Optimization Guide

## Overview

This guide documents the CI/CD optimization strategies implemented for the _codex_ repository to achieve fast, reliable automated validation.

## Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Post-merge validation | ≤ 10 min | ~8 min | ✅ |
| Documentation validation | ≤ 5 min | ~3 min | ✅ |
| PR validation (fast track) | ≤ 15 min | ~12 min | ✅ |

## Optimization Strategies

### 1. Dependency Caching

**Implementation**: Uses GitHub Actions `cache` action

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .pytest_cache
    key: ${{ runner.os }}-pytest-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pytest-
```

**Benefits**:
- Reduces pip install time from ~2min to ~10s on cache hit
- Improves reliability (less network dependency)
- Faster feedback for developers

**Cache Strategy**:
- **Key**: OS + dependency files hash
- **Restore keys**: Fallback to partial matches
- **Invalidation**: Automatic on dependency changes

### 2. Test Parallelization

**Implementation**: Matrix strategy + job parallelization

```yaml
strategy:
  fail-fast: false
  matrix:
    test-group: [config, unit, integration]
```

**Benefits**:
- Runs test groups in parallel on separate runners
- Reduces wall-clock time from 9min to 3min
- Isolates failures (fail-fast: false allows all to complete)

**Test Groups**:
- **config**: Configuration and schema tests (~1min)
- **unit**: Core unit tests (~2min)
- **smoke**: Quick smoke tests (~30s)

### 3. Workflow Jobs Optimization

**Job Dependencies**:
```text
validate-imports (2min)
  ├─> test-core (parallel, 3min)
  ├─> test-smoke (parallel, 1min)
  ├─> lint-check (parallel, 1min)
  └─> modernization-scan (parallel, 2min)
```

**Total Time**: max(3, 1, 1, 2) + 2 = **5 minutes** (worst case)

### 4. Timeout Management

All jobs have explicit timeouts to prevent hanging:

```yaml
jobs:
  validate-imports:
    timeout-minutes: 5
  test-core:
    timeout-minutes: 5
  test-smoke:
    timeout-minutes: 3
```

**Benefits**:
- Prevents stuck jobs from blocking queue
- Early failure detection
- Predictable runtime

## Monitoring & Metrics

### Tracking CI Performance

**GitHub Actions Insights**:
- Navigate to Actions tab > Workflow > Analytics
- Monitor: duration trends, success rate, runner utilization

**Key Metrics to Track**:
1. **Average duration** per workflow
2. **Cache hit rate** (check logs for "Cache restored from key")
3. **Failure rate** by job
4. **Queue time** (time waiting for runner)

### Alert Thresholds

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Workflow duration | > 15 min | Investigate slow jobs |
| Cache hit rate | < 80% | Review cache key strategy |
| Failure rate | > 10% | Review flaky tests |
| Queue time | > 5 min | Consider runner scaling |

## Best Practices

### For Developers

**When Adding Tests**:
- Use appropriate markers (`@pytest.mark.slow`, `@pytest.mark.smoke`)
- Keep smoke tests fast (< 1 second each)
- Avoid network calls in unit tests

**When Updating Dependencies**:
- Expect cache miss on first run
- Subsequent runs will be fast
- pyproject.toml changes invalidate cache

**When CI is Slow**:
1. Check which job is slow (parallel jobs show individual times)
2. Look for cache misses in logs
3. Check if tests are marked correctly
4. Review recent dependency changes

### For Maintainers

**Cache Maintenance**:
- Caches auto-expire after 7 days of no access
- Manual cache clearing: Settings > Actions > Caches
- Monitor total cache size (quota: 10GB per repo)

**Runner Configuration**:
- Current: ubuntu-latest (2-core, 7GB RAM)
- For heavy workloads: Consider self-hosted runners
- Matrix: Use fail-fast: false for independence

**Workflow Updates**:
- Test changes locally with `act` (GitHub Actions locally)
- Use continue-on-error: true for non-critical jobs
- Set appropriate timeouts

## Troubleshooting

### Slow CI Runs

**Symptoms**: Workflow takes > 15 minutes

**Diagnosis**:
```bash
# Check individual job times in GitHub UI
# Look for "Cache not found" in logs
# Check test duration with pytest --durations=10
```

**Solutions**:
1. Verify cache keys are correct
2. Add more test parallelization
3. Move slow tests to separate workflow
4. Use pytest-xdist for parallel test execution

### Cache Issues

**Symptoms**: Every run shows "Cache not found"

**Diagnosis**:
- Check cache key template
- Verify dependency files exist
- Check file hash consistency

**Solutions**:
```yaml
# Use more stable keys
key: ${{ runner.os }}-deps-v1-${{ hashFiles('**/requirements*.txt') }}

# Add restore-keys for partial matches
restore-keys: |
  ${{ runner.os }}-deps-v1-
  ${{ runner.os }}-deps-
```

### Flaky Tests

**Symptoms**: Tests pass/fail intermittently

**Diagnosis**:
- Run tests multiple times: `pytest --count=10`
- Check for timing dependencies
- Review test isolation

**Solutions**:
- Mark as flaky: `@pytest.mark.flaky(reruns=3)`
- Fix root cause (preferred)
- Skip on CI: `@pytest.mark.skip(reason="flaky")`

## Advanced Optimization

### Conditional Execution

Run jobs only when relevant files change:

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - '!**/*.md'  # Exclude markdown
```

### Artifact Caching

Cache build artifacts between jobs:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/

- uses: actions/download-artifact@v4
  with:
    name: dist
```

### Docker Layer Caching

For Docker-based workflows:

```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Future Improvements

**Short-term** (next sprint):
- [ ] Add pytest-xdist for parallel test execution
- [ ] Implement test splitting by timing data
- [ ] Add workflow run analytics dashboard

**Medium-term** (next quarter):
- [ ] Evaluate self-hosted runners for heavy workloads
- [ ] Implement smart test selection (run only affected tests)
- [ ] Add performance regression detection

**Long-term** (future):
- [ ] Full CI/CD pipeline optimization
- [ ] Predictive caching based on PR patterns
- [ ] Auto-scaling runner infrastructure

## References

- [GitHub Actions Cache Documentation](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices-for-github-actions)
- [pytest-xdist for parallel execution](https://github.com/pytest-dev/pytest-xdist)

---

**Last Updated**: 2025-11-07  
**Maintained By**: DevOps Team  
**Review Cycle**: Monthly
