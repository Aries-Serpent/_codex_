# Phase 6 Wave 5: Layer-Specific Implementation Tasks

**Status**: Ready for Development  
**Version**: 1.0.0  
**Date**: 2026-02-17

---

## Overview

Detailed task breakdown for each cache layer optimization. Includes code changes, testing requirements, acceptance criteria, and dependencies.

---

## 🎯 Layer 1: In-Process Memory Cache

### L1-1: Segmented LRU Implementation

**Objective**: Implement hot/warm/cold segment architecture to improve hit rate by 15%

**Tasks**:
1. Create `SegmentedLRU` class in `src/codex/cache/lru_segmented.py`
   - Inherit from `OrderedDict` base
   - Implement 3 segments: hot (20% size), warm (50%), cold (30%)
   - Segment-aware eviction policies (cold evicts first)
   - Configurable TTL per segment

2. Update `src/codex/cache/layer1_memory_cache.py`
   - Replace `OrderedDict` with `SegmentedLRU`
   - Add segment migration logic (TTL → hot → warm → cold)
   - Implement segment statistics tracking

3. Testing (`tests/cache/test_layer1_segmented.py`)
   - Test segment allocation (20/50/30 ratio)
   - Test promotion from cold → warm → hot
   - Test TTL-based expiration per segment
   - Benchmark: Verify segment migration < 100μs p99

**Code Template**:
```python
# src/codex/cache/lru_segmented.py
class SegmentedLRU:
    def __init__(self, capacity: int, hot_ratio: float = 0.2, warm_ratio: float = 0.5):
        self.capacity = capacity
        self.hot = OrderedDict()      # Smallest, most active
        self.warm = OrderedDict()     # Medium
        self.cold = OrderedDict()     # Largest, least active
        self.size_hot = int(capacity * hot_ratio)
        self.size_warm = int(capacity * warm_ratio)
        self.size_cold = capacity - self.size_hot - self.size_warm
    
    def get(self, key: str) -> Any:
        # Check all segments, promote if found
        value = self._get_and_promote(key)
        return value
    
    def _get_and_promote(self, key: str) -> Any:
        # Promotion logic: cold → warm → hot
        # Track access frequency
        pass
```

**Success Criteria**:
- ✅ L1 hit rate improves from 65% → 78%+
- ✅ Segment migration latency < 100μs (p99)
- ✅ No memory overhead > 5%
- ✅ Backward compatible with existing cache interface

---

### L1-2: Adaptive TTL Implementation

**Objective**: Implement sliding window TTL to improve hit rate by 10%

**Tasks**:
1. Create `AdaptiveTTL` calculator in `src/codex/cache/ttl_adaptive.py`
   - Track access frequency per key
   - Calculate optimal TTL based on access patterns
   - Implement exponential moving average (EMA) for frequency

2. Update cache eviction logic
   - Use adaptive TTL instead of fixed 1-hour TTL
   - TTL range: 30 minutes (cold) to 4 hours (hot)

3. Testing (`tests/cache/test_layer1_adaptive_ttl.py`)
   - Test TTL calculation accuracy
   - Test frequency tracking
   - Benchmark: Verify no overhead on get/put operations

**Success Criteria**:
- ✅ L1 hit rate improves from 78% → 88%+
- ✅ Average TTL matches access patterns
- ✅ No performance regression on cache operations

---

### L1-3: Cache Warming at Startup

**Objective**: Pre-populate L1 with frequently accessed embeddings (+5% hit rate)

**Tasks**:
1. Create `CacheWarmingJob` in `src/codex/cache/warming.py`
   - Load top-N most-accessed embeddings from L2 disk cache
   - Warm L1 at application startup
   - Track warming metrics (items loaded, time, success rate)

2. Configuration
   - Warming dataset: Store top 1000 embeddings list
   - Update at end of each day
   - Configurable via `CACHE_WARMING_ENABLED` env var

3. Testing
   - Verify top-N embeddings loaded correctly
   - Verify warming doesn't block startup (async)
   - Benchmark: Warming should complete within 2 seconds

**Success Criteria**:
- ✅ L1 hit rate improves from 88% → 92%+
- ✅ Startup time increase < 3 seconds
- ✅ Warming succeeds > 99% of time

---

### L1-4: Background Eviction Thread

**Objective**: Reduce lock contention by moving eviction off critical path (-5% latency impact)

**Tasks**:
1. Implement background eviction in `src/codex/cache/layer1_memory_cache.py`
   - Spawn background thread on cache creation
   - Queue expired keys for async eviction
   - Use lock-free queue (multiprocessing.Queue or threading.Queue with timeout)

2. Thread lifecycle
   - Start on cache init
   - Shutdown gracefully on app termination
   - Monitor thread health (detect stalls)

3. Testing
   - Verify thread doesn't consume >2% CPU
   - Verify no race conditions on eviction
   - Benchmark: Verify lock contention reduced

**Success Criteria**:
- ✅ Background eviction CPU < 2% sustained
- ✅ No race conditions detected (thread-safety tests)
- ✅ Lock contention reduced by >30%

---

### L1-5: Prometheus Metrics Export

**Objective**: Expose L1 metrics for observability

**Tasks**:
1. Create metrics in `src/codex/cache/metrics.py`
   - `codex_cache_hit_rate{layer="L1"}`
   - `codex_cache_requests_total{layer="L1", status="hit|miss"}`
   - `codex_cache_latency_ms{layer="L1", quantile="0.50|0.95|0.99"}`
   - `codex_cache_evictions_total{layer="L1", reason="ttl|lru|segment"}`
   - `codex_cache_segment_size_bytes{segment="hot|warm|cold"}`

2. Integration
   - Export metrics via `/metrics/cache` endpoint
   - Scrape interval: 15 seconds

**Success Criteria**:
- ✅ All metrics exported and collecting data
- ✅ No performance overhead from metrics collection

---

## 🎯 Layer 2: Local Disk Cache

### L2-1: Cost-Aware Eviction

**Objective**: Evict low-cost entries before high-cost ones (+8% hit rate)

**Tasks**:
1. Implement cost tracking in `src/codex/cache/layer2_disk_cache.py`
   - Track embedding generation cost (compute time + memory)
   - Store cost metadata in cache index
   - Implement cost-aware eviction policy

2. Eviction order
   - Sort entries by cost/age ratio
   - Evict low-cost, old entries first
   - Preserve high-cost recent entries

3. Testing
   - Verify eviction order matches cost expectations
   - Benchmark: Cost calculation overhead < 1ms

**Success Criteria**:
- ✅ L2 hit rate improves from 72% → 80%+
- ✅ High-cost entries retained longer
- ✅ Eviction overhead < 1% of cache time

---

### L2-2: Disk Quota Management

**Objective**: Enforce disk quotas to prevent unchecked growth (+5% hit rate stability)

**Tasks**:
1. Implement `QuotaManager` in `src/codex/cache/quota_manager.py`
   - Define categories: pip (8GB), embedding (5GB), other (1.5GB)
   - Monitor disk usage per category
   - Enforce quotas with automated cleanup

2. Cleanup job
   - Run hourly
   - Remove excess entries by category
   - Trigger when usage > 90% of quota

3. Configuration
   - Store quotas in `config/cache_quotas.yaml`
   - Allow runtime adjustment via API

**Success Criteria**:
- ✅ Total disk usage stays within 14.5GB
- ✅ Per-category quotas enforced
- ✅ Cleanup latency < 30 seconds

---

### L2-3: Binary Serialization

**Objective**: Replace JSON with numpy binary format (+4% latency improvement)

**Tasks**:
1. Update serialization in `src/codex/cache/layer2_disk_cache.py`
   - Use `numpy.save()` for float arrays
   - Use pickle for complex objects (fallback to JSON if needed)
   - Compress with zlib

2. Backward compatibility
   - Detect old JSON format on read
   - Auto-migrate to binary format on write
   - Test roundtrip correctness

3. Testing
   - Verify serialization correctness (numpy roundtrip)
   - Benchmark: Latency reduction 4-10ms vs JSON
   - Test concurrent read/write with mixed formats

**Success Criteria**:
- ✅ Read latency reduced by 4-10ms
- ✅ 100% backward compatibility with old data
- ✅ Serialization correctness verified

---

### L2-4: RWLock for Concurrent Reads

**Objective**: Improve read throughput with read-write lock (+2% throughput)

**Tasks**:
1. Replace `threading.Lock` with `threading.RWLock`
   - Import from `readerwriterlock` package (or implement)
   - Update all cache operations

2. Operation classification
   - Readers: `get`, `exists`, `stat`
   - Writers: `put`, `delete`, `evict`

3. Testing
   - Benchmark: 10 concurrent readers
   - Verify no starvation of writers
   - Test high contention scenario

**Success Criteria**:
- ✅ Read throughput improved by 2-5%
- ✅ Write latency unaffected
- ✅ No writer starvation observed

---

### L2-5: Quota Monitoring

**Objective**: Monitor and report on quota usage

**Tasks**:
1. Add metrics
   - `codex_cache_quota_used_bytes{category="pip|embedding|other"}`
   - `codex_cache_quota_available_bytes{category="pip|embedding|other"}`

2. Daily reports
   - Track quota usage trends
   - Alert if usage > 80% quota

**Success Criteria**:
- ✅ Metrics exported and accessible
- ✅ Alerts working for quota threshold

---

## 🎯 Layer 3: GitHub Actions Build Cache

### L3-1: Workflow Migration (37 workflows)

**Objective**: Migrate all 42 workflows to standardized cache config (+15% adoption)

**Workflows** (Priority Order):
- **Week 1**: pr-checks, test-main, code-quality-coverage-suite (3/42 = 7%)
- **Week 2**: pages-mkdocs, rust_swarm_ci, coverage-tracking, security-audit, integration-tests (8/42 = 19%)
- **Week 3**: All remaining 34 workflows

**Tasks per Workflow**:
1. Update cache configuration
2. Standardize cache key format
3. Test cache hit rate in staging
4. Promote to production

**Success Criteria**:
- ✅ 42/42 workflows migrated (100%)
- ✅ L3 hit rate ≥ 78%
- ✅ Zero workflow failures from cache

---

### L3-2: 3-Layer Fallback Chain

**Objective**: Implement exact-hash → workflow-os → os-only restore keys (+8% hit rate)

**Tasks**:
1. Update `.github/actions/setup-python-cache/action.yml`
   ```yaml
   - uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-${{ github.workflow }}-dep-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt', '**/Cargo.lock') }}
       restore-keys: |
         ${{ runner.os }}-${{ github.workflow }}-dep-
         ${{ runner.os }}-dep-
   ```

2. Testing
   - Verify exact-hash hits when dependencies unchanged
   - Verify fallback to workflow-os on dependency change
   - Verify final fallback to os-only

**Success Criteria**:
- ✅ 3-layer fallback working correctly
- ✅ Hit rate improves by 8%

---

### L3-3: Dependency Hashing

**Objective**: Add dependency file hashing to cache keys (+5% accuracy)

**Tasks**:
1. Include all dependency files in hash
   - `pyproject.toml`, `requirements*.txt` (Python)
   - `Cargo.lock` (Rust)
   - `package-lock.json` (Node)
   - `uv.lock`, `poetry.lock` (if present)

2. Hash computation
   - Use `hashFiles()` GitHub Actions function
   - Include OS in hash

**Success Criteria**:
- ✅ Cache keys include all dependency files
- ✅ Cache invalidates on any dependency change

---

### L3-4: Cache Health Monitoring

**Objective**: Add hit/miss metrics collection (+8% observability)

**Tasks**:
1. Add metrics step to each workflow
   ```yaml
   - name: Report Cache Metrics
     run: |
       echo "CACHE_HIT=${{ steps.cache.outputs.cache-hit }}" >> $GITHUB_OUTPUT
       echo "WORKFLOW=${{ github.workflow }}" >> $GITHUB_OUTPUT
   ```

2. Metrics collection
   - Send to metrics API
   - Track per workflow
   - Dashboard aggregation

**Success Criteria**:
- ✅ Cache hit rates visible in dashboard
- ✅ Per-workflow metrics available

---

### L3-5: Pre-Commit Cache

**Objective**: Enable pre-commit hook cache (+10% adoption)

**Tasks**:
1. Update workflows to cache pre-commit
   ```yaml
   key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
   ```

2. Verify pre-commit cache hits
3. Measure impact on CI time

**Success Criteria**:
- ✅ Pre-commit cache hit rate ≥ 80%
- ✅ Pre-commit hooks run 2-3x faster from cache

---

### L3-6: Cache Warming Job

**Objective**: Pre-warm cache for faster initial restores (+3% hit rate)

**Tasks**:
1. Create cache warming workflow job
   - Runs before main jobs
   - Downloads and extracts cache artifacts
   - Pre-populates GitHub Actions cache

**Success Criteria**:
- ✅ Warming job completes < 2 minutes
- ✅ First cache restore benefits from warming

---

## 🎯 Layer 4: Cloud/Redis Distributed Cache

### L4-1: Circuit Breaker Implementation

**Objective**: Implement resilience pattern with exponential backoff (+10% availability)

**Tasks**:
1. Create `CircuitBreaker` class in `src/codex/cache/circuit_breaker.py`
   - States: closed (normal), open (failing), half-open (testing)
   - Exponential backoff: 1s → 2s → 4s → 8s
   - Timeout after 5 consecutive failures

2. Update Redis client wrapper
   - Wrap redis.Redis with CircuitBreaker
   - On open: fallback to L2
   - On half-open: test with single request

3. Testing
   - Test state transitions
   - Test fallback to L2 on failure
   - Benchmark: Failover latency < 100ms

**Code Template**:
```python
# src/codex/cache/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.state = "closed"  # closed, open, half-open
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure = None
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if self._timeout_expired():
                self.state = "half-open"
            else:
                raise CircuitBreakerOpen()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.state = "closed"
        self.failure_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
```

**Success Criteria**:
- ✅ L4 availability ≥ 99.5%
- ✅ Failover latency < 100ms
- ✅ No cascading failures observed

---

### L4-2: Health Metrics Export

**Objective**: Expose Redis health metrics (-15% observability gap)

**Tasks**:
1. Create Redis health monitor in `src/codex/cache/redis_health_monitor.py`
   - Poll Redis INFO every 30 seconds
   - Track connection health
   - Expose metrics

2. Metrics
   - `codex_redis_connected_clients`
   - `codex_redis_used_memory_bytes`
   - `codex_redis_evicted_keys_total`
   - `codex_redis_connection_latency_ms`
   - `codex_cache_circuit_breaker_state`

3. Alerts
   - Alert if latency > 100ms
   - Alert if memory > 80% capacity

**Success Criteria**:
- ✅ All metrics exported
- ✅ Alerts triggering on threshold breach

---

### L4-3: Connection Pool Optimization

**Objective**: Optimize pool size and timeouts (+3% latency improvement)

**Tasks**:
1. Benchmark connection pool sizes
   - Test pool size: 5, 10, 20, 50
   - Measure latency and throughput

2. Configure optimal settings
   - Pool size: Recommended 10-20 (tuned to workload)
   - Connection timeout: 5 seconds
   - Socket timeout: 10 seconds

3. Testing
   - Benchmark latency distribution
   - Test connection exhaustion handling

**Success Criteria**:
- ✅ Connection latency p99 < 80ms
- ✅ Throughput optimized for workload

---

### L4-4: Adaptive TTL

**Objective**: Use cost-aware TTL like L2 (+5% hit rate)

**Tasks**:
1. Implement adaptive TTL for Redis
   - Track entry generation cost
   - Set TTL proportional to cost
   - Range: 1 hour (cheap) to 7 days (expensive)

2. Testing
   - Verify TTL matches cost expectations
   - Benchmark: No performance overhead

**Success Criteria**:
- ✅ L4 hit rate improves from 42% → 70%+
- ✅ High-cost entries retained longer

---

### L4-5: Compression for Large Entries

**Objective**: Compress entries > 10KB to save memory (+2% efficiency)

**Tasks**:
1. Add compression logic in cache put/get
   - Compress if size > 10KB
   - Use zlib or brotli
   - Track compression ratio

2. Testing
   - Verify roundtrip correctness
   - Benchmark: Compression latency
   - Measure storage savings

**Success Criteria**:
- ✅ Storage efficiency improved by 2-5%
- ✅ Decompression latency < 5ms

---

### L4-6: Monitoring Dashboard

**Objective**: Build Redis health dashboard with alerts

**Tasks**:
1. Create Grafana dashboard
   - Redis memory usage
   - Connection count
   - Key evictions
   - Circuit breaker state

2. Alerts
   - Memory > 80% capacity
   - Connection latency > 100ms
   - Eviction rate spike

**Success Criteria**:
- ✅ Dashboard showing real-time metrics
- ✅ Alerts working and routed to on-call

---

## 📋 Implementation Timeline

### Week 1: L1 + L2 Foundation
- **Days 1-2**: L1-1 (Segmented LRU)
- **Days 1-2**: L1-2 (Adaptive TTL)
- **Day 3**: L1-3 (Cache Warming)
- **Day 3**: L1-4 (Background Eviction)
- **Day 4**: L1-5 (Prometheus Metrics)
- **Days 2-3**: L2-1 (Cost-Aware Eviction)
- **Days 3-4**: L2-2 (Disk Quotas)
- **Days 4-5**: L2-3 (Binary Serialization)
- **Day 5**: L2-4 (RWLock)
- **Day 5**: L2-5 (Quota Monitoring)

### Week 2: L3 Workflow Migration
- **Days 6-7**: L3-1 Phase 1 (10 workflows)
- **Days 7-8**: L3-1 Phase 2 (20 workflows)
- **Days 9-10**: L3-1 Phase 3 (12 workflows)
- **Days 8-9**: L3-2 (3-Layer Fallback)
- **Days 9-10**: L3-3 (Dependency Hashing)
- **Days 10-11**: L3-4 (Health Monitoring)
- **Days 11-12**: L3-5 (Pre-Commit Cache)
- **Day 12**: L3-6 (Cache Warming)

### Week 3-4: L4 Infrastructure
- **Days 13-16**: Redis deployment + health checks
- **Days 17-18**: L4-1 (Circuit Breaker)
- **Days 18-19**: L4-2 (Health Metrics)
- **Days 19-20**: L4-3 (Connection Pool)
- **Days 20-21**: L4-4 (Adaptive TTL)
- **Days 21-22**: L4-5 (Compression)
- **Days 22-28**: L4-6 (Monitoring + Optimization)

---

**Implementation Version**: 1.0.0  
**Last Updated**: 2026-02-17  
**Status**: Ready for Development
