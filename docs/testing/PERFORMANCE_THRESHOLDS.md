# Performance Thresholds Documentation

## Overview

This document explains the performance thresholds used throughout the Codex codebase, with a focus on the Rust swarm engine performance tests. These thresholds are designed to catch catastrophic performance regressions while remaining stable across different execution environments.

## Rust Swarm Engine Thresholds

### Current Threshold: 200 tasks/second

**Location**: `rust_swarm/swarm_engine.rs` - `test_high_throughput()`

**Rationale**: This conservative threshold (200 tasks/s) is intentionally set for CI environments to avoid flaky tests while still catching severe performance regressions.

### Expected Performance by Environment

| Environment | Expected Range | Notes |
|------------|----------------|-------|
| **Local Development** | 5,000 - 15,000 tasks/s | Modern desktop/laptop with dedicated resources |
| **Production** | 3,000 - 10,000 tasks/s | Server-grade hardware with optimized configuration |
| **CI (GitHub Actions)** | 200 - 2,000 tasks/s | Shared runners with variable CPU availability |
| **CI (Self-hosted)** | 1,000 - 5,000 tasks/s | Dedicated runners with consistent performance |

### CI Environment Considerations

GitHub Actions shared runners experience significant performance variability due to:

1. **Resource Contention**: Multiple jobs competing for CPU/memory on shared hosts
2. **Network Latency**: Variable network performance affecting I/O operations
3. **Thermal Throttling**: CPU frequency scaling under load
4. **Platform Differences**: Different CPU architectures (x86_64, ARM) and generations
5. **Background Services**: System processes consuming resources

### Threshold Selection Strategy

The 200 tasks/s threshold was chosen to:

- ✅ **Catch catastrophic regressions**: A drop below 200 tasks/s indicates a severe performance issue (>95% regression from baseline)
- ✅ **Avoid false positives**: Minimizes flaky test failures due to CI environment variability
- ✅ **Maintain CI stability**: Tests pass consistently across different runner types and load conditions
- ✅ **Signal critical issues**: While permissive, still alerts on fundamental algorithmic or architectural problems

### What This Threshold Does NOT Catch

⚠️ **Important Limitations**:

- **Moderate regressions** (20-50% slowdown): A drop from 5,000 to 2,500 tasks/s would still pass
- **Incremental degradation**: Gradual performance decay over time
- **Environment-specific issues**: Problems that only manifest on high-performance hardware

### Recommended Improvements

For better regression detection, consider:

1. **Environment-specific thresholds** via `cfg` attributes:
   ```rust
   #[cfg(ci_environment)]
   const THRESHOLD: f64 = 200.0;
   
   #[cfg(not(ci_environment))]
   const THRESHOLD: f64 = 2000.0;
   ```

2. **Statistical baseline tracking**:
   - Store historical performance metrics
   - Alert when current run is >2 standard deviations below mean
   - Adapt baseline automatically based on runner performance

3. **Tiered thresholds**:
   - **Critical**: 200 tasks/s (test fails - catastrophic regression)
   - **Warning**: 1,000 tasks/s (log warning - investigate)
   - **Optimal**: 5,000+ tasks/s (expected for production)

4. **Separate benchmark suite**:
   - Run performance benchmarks on dedicated hardware
   - Track trends over time with visualization
   - Use tools like `criterion` for statistical rigor

## Other Performance Thresholds

### Token Processing (Python)

**Location**: `tests/test_auth/test_token_manager.py`

- **Token generation**: < 100ms per token (typical: 10-20ms)
- **Token validation**: < 50ms per validation (typical: 5-10ms)
- **Encryption/decryption**: < 200ms per operation (typical: 50-100ms)

### MFA Verification (Python)

**Location**: `tests/test_auth/test_mfa_provider.py`

- **TOTP generation**: < 10ms (typical: 1-2ms)
- **TOTP verification**: < 10ms (typical: 1-2ms)
- **QR code generation**: < 500ms (typical: 100-200ms)

### OAuth Flow (Python)

**Location**: `tests/test_auth/test_oauth_provider.py`

- **Authorization URL generation**: < 50ms (typical: 5-10ms)
- **Token exchange**: < 2s (network-dependent, including GitHub API call)
- **Token refresh**: < 2s (network-dependent)

## Monitoring Performance

### During Development

```bash
# Run Rust benchmarks
cd rust_swarm
cargo bench

# Run Python performance tests
pytest tests/test_auth/ -v --benchmark-only
```

### In CI

Performance metrics are logged in test output:
```
Test throughput: 8543 tasks/s (PASS - above 200 tasks/s threshold)
```

Review logs to identify performance trends over time.

### Production Monitoring

For production deployments:

1. **Enable metrics collection**: Use tools like Prometheus, Datadog, or CloudWatch
2. **Set up alerts**: Alert when performance drops below 50% of baseline
3. **Track percentiles**: Monitor p50, p95, p99 latencies
4. **Correlate with deployments**: Identify commits that introduce regressions

## Updating Thresholds

### When to Update

Update thresholds when:

- **Hardware changes**: Moving to different CI runners or production servers
- **Algorithm improvements**: Legitimate performance gains that raise the baseline
- **Architecture changes**: Fundamental redesigns that change performance characteristics
- **Toolchain updates**: Rust/Python version upgrades that affect performance

### How to Update

1. **Gather data**: Run tests 20-30 times in target environment
2. **Calculate statistics**: Compute mean, median, standard deviation
3. **Set threshold**: Use `mean - 3*stddev` or `p5` (5th percentile) as threshold
4. **Document change**: Update this file with rationale and new baseline
5. **Monitor**: Watch for false positives/negatives after update

### Update Process

```bash
# Run multiple iterations
for i in {1..20}; do
    cargo test --release test_high_throughput -- --nocapture | grep "throughput"
done > performance_data.txt

# Analyze results
python scripts/analyze_performance_thresholds.py performance_data.txt

# Update threshold in code
# Edit rust_swarm/swarm_engine.rs
# Edit this documentation
```

## Historical Baselines

| Date | Threshold | Environment | Rationale |
|------|-----------|-------------|-----------|
| 2024-01-15 | 5,000 tasks/s | Original implementation | Initial baseline from development machine |
| 2026-01-16 | 200 tasks/s | GitHub Actions shared runners | Adjusted for CI stability after flaky test analysis |

## References

- [Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Criterion.rs Benchmarking](https://github.com/bheisler/criterion.rs)
- [GitHub Actions Runner Specs](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)

## Contact

For questions about performance thresholds:
- **Owner**: @mbaetiong
- **Last Updated**: 2026-01-16
- **Document Version**: 1.0
