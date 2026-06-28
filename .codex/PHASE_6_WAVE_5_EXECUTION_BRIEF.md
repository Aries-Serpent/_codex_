# 🚀 PHASE 6 WAVE 5: Cache & Performance Optimization Execution Brief

**Status**: Ready for Staged Rollout  
**Authority**: @mbaetiong (Full Autonomous Execution)  
**Timeline**: 3-4 week staged rollout (after Waves 1-4 stabilization)  
**Expected Impact**: +25% aggregate cache hit rate, 40-60% CI time reduction, $45K-$60K annual savings

---

## Executive Summary

Phase 6 Wave 5 executes comprehensive 4-layer cache optimization to improve hit rates from **59% → 84% (+25%)** and reduce CI wall-clock time by **40-60%** (120-180 seconds per workflow).

**Target Metrics**:
- L1 (In-Memory): 65% → 95% hit rate (+30% gap closure)
- L2 (Local Disk): 72% → 85% hit rate (+13% gap closure)
- L3 (GitHub Actions): 58% → 80% hit rate, 100% workflow adoption
- L4 (Cloud/Redis): 42% → 75% hit rate (+33% gap closure)
- **Aggregate**: 59% → 84% hit rate (+25% improvement)

**Annual Impact**: $45K-$60K cost savings, 300+ weekly org minutes saved

---

## 🏗️ Layer-by-Layer Optimization Strategy

### Layer 1: In-Process Memory Cache (L1)

**Current**: 65% hit rate, <1ms latency, 100K+ ops/sec  
**Target**: 95% hit rate (+30% gap)  
**Timeline**: Week 1 (3-5 days implementation + 2-3 days stabilization)

**Critical Issues**:
- ❌ Short 1-hour TTL reduces reuse (-10% impact)
- ❌ Lazy eviction only, no background cleanup (-8%)
- ❌ Lock contention under concurrent load (-5%)
- ❌ No hot/warm/cold segment separation (-7%)

**Implementation Tasks**:

| Task | Description | Effort | Impact |
|------|-------------|--------|--------|
| L1-1: Segmented LRU | Split cache into hot/warm/cold with independent TTLs | 2-3 days | +15% |
| L1-2: Adaptive TTL | Sliding window TTL based on access frequency | 1-2 days | +10% |
| L1-3: Cache Warming | Pre-warm L1 with frequent embeddings at startup | 1-2 days | +5% |
| L1-4: Background Eviction | Async eviction thread to reduce lock contention | 1 day | +3% |
| L1-5: Monitoring | Expose hit/miss/eviction metrics | 1 day | Observability |

**Code Changes**:
```python
# src/codex/cache/layer1_memory_cache.py
# - Replace OrderedDict with SegmentedLRU (hot/warm/cold)
# - Implement adaptive TTL calculator
# - Add background eviction thread
# - Export prometheus metrics

# tests/cache/test_layer1_segmented.py
# - Test segment migration on TTL expiry
# - Test cache warming functionality
# - Benchmark lock contention reduction
# - Performance regression test suite
```

**Success Criteria**:
- ✅ L1 hit rate ≥ 92% (over 1-hour window)
- ✅ Segment migration latency < 100μs median
- ✅ Background eviction CPU < 2%
- ✅ No regression in p99 access latency (< 1ms)

---

### Layer 2: Local Disk Cache (L2)

**Current**: 72% hit rate, 5-50ms latency, 1K-10K ops/sec, 10GB capacity  
**Target**: 85% hit rate (+13% gap)  
**Timeline**: Week 1-2 (overlaps L1, 4-7 days)

**Critical Issues**:
- ❌ Aggressive 10% eviction on full (+15% hit rate impact)
- ❌ No disk quotas (unchecked growth) (-5%)
- ❌ JSON serialization overhead (-4% latency)
- ❌ Thread contention on cache writes (-3%)

**Implementation Tasks**:

| Task | Description | Effort | Impact |
|------|-------------|--------|--------|
| L2-1: Cost-Aware Eviction | Track generation cost, evict low-cost first | 2-3 days | +8% |
| L2-2: Disk Quotas | Enforce per-category limits (8GB pip + 5GB embedding) | 1-2 days | +5% |
| L2-3: Binary Format | Replace JSON with numpy binary serialization | 2-3 days | +4% latency |
| L2-4: RWLock | Switch from Lock to RWLock for concurrent reads | 1 day | +2% throughput |
| L2-5: Quota Monitor | Hourly quota enforcement job | 1 day | Prevents overflow |

**Success Criteria**:
- ✅ L2 hit rate ≥ 80% (over 24-hour window)
- ✅ Disk usage stays within 14.5GB quota
- ✅ Read latency p99 < 50ms from warm cache
- ✅ Eviction latency < 1 second per entry

---

### Layer 3: GitHub Actions Build Cache (L3)

**Current**: 58% hit rate, 100-500ms latency, 12% adoption (5/42 workflows)  
**Target**: 80% hit rate, 100% adoption (42/42 workflows)  
**Timeline**: Week 2-3 (5-10 days)

**Critical Issues**:
- ❌ Only 12% adoption — **37 workflows missing** (-22% impact)
- ❌ Non-standardized cache keys (-8% hit rate)
- ❌ Missing 3-layer fallback chain (-5%)
- ❌ No cache hit/miss metrics (-8% observability)
- ❌ Pre-commit cache not leveraged (-10%)

**Implementation Tasks**:

| Task | Description | Effort | Impact |
|------|-------------|--------|--------|
| L3-1: Workflow Migration | Migrate all 37 workflows to standardized config | 3-5 days | +15% |
| L3-2: 3-Layer Fallback | exact-hash → workflow-os → os-only restore chain | 2-3 days | +8% |
| L3-3: Dependency Hashing | Add dependency file hash to cache keys | 1-2 days | +5% accuracy |
| L3-4: Health Monitoring | Add hit/miss metrics collection | 2-3 days | Observability |
| L3-5: Pre-Commit Cache | Enable pre-commit hook cache | 2-3 days | +10% adoption |
| L3-6: Cache Warming | Cache warming job before main jobs | 1-2 days | +3% |

**Workflows to Migrate** (Priority Order):
1. **High-Impact** (frequent): `pr-checks.yml`, `test-main.yml`, `code-quality-coverage-suite.yml`
2. **Medium-Impact** (daily): `pages-mkdocs.yml`, `rust_swarm_ci.yml`, `coverage-tracking.yml`
3. **Standard** (regular): All remaining 32 workflows
4. **Scheduled** (nightly): Optimization/analytics workflows

**Cache Key Standard**:
```yaml
key: ${{ runner.os }}-${{ github.workflow }}-dep-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt', '**/Cargo.lock') }}
restore-keys: |
  ${{ runner.os }}-${{ github.workflow }}-dep-
  ${{ runner.os }}-dep-
```

**Success Criteria**:
- ✅ 42/42 workflows (100%) using standardized config
- ✅ L3 hit rate ≥ 78%
- ✅ Cache restore time < 500ms (p95)
- ✅ No workflow failures due to cache corruption
- ✅ Pre-commit cache hit rate ≥ 85%

---

### Layer 4: Cloud/Redis Distributed Cache (L4)

**Current**: 42% hit rate, 20-80ms latency, 100-1K ops/sec  
**Target**: 75% hit rate (+33% gap)  
**Timeline**: Week 3-4 (infrastructure + 5-7 days)

**Critical Issues**:
- ❌ Silent connection failures (no logging) (-20% availability)
- ❌ No health metrics exposed (-15% observability)
- ❌ No circuit breaker (-10% reliability)
- ❌ Fixed 1-hour TTL wastes hot/cold distinction (-8%)

**Implementation Tasks**:

| Task | Description | Effort | Impact |
|------|-------------|--------|--------|
| L4-1: Circuit Breaker | Exponential backoff + fallback to L2 after 5 failures | 2-3 days | +10% |
| L4-2: Health Metrics | Expose Redis INFO metrics (clients, memory, evictions) | 1-2 days | Observability |
| L4-3: Connection Pool | Optimize pool size and timeout settings | 1-2 days | +3% latency |
| L4-4: Adaptive TTL | Cost-aware TTL based on generation cost | 2 days | +5% |
| L4-5: Compression | Compress entries > 10KB | 1-2 days | +2% memory |
| L4-6: Monitoring | Build Redis health dashboard + alerts | 2-3 days | Observability |

**Success Criteria**:
- ✅ L4 hit rate ≥ 72% (over 7-day window)
- ✅ Availability ≥ 99.5% (circuit breaker prevents cascades)
- ✅ Fallback to L2 within 100ms on Redis failure
- ✅ p99 latency ≤ 80ms
- ✅ No data loss on Redis restart (persistence enabled)

---

## 📊 Performance Baseline & Targets

### Current Baseline (Phase 5 Lane 5.5B)

**API Performance**:
- p50: 10.4ms ✅
- p95: 13.0ms ✅
- p99: 12.9ms ✅
- Memory peak: 313.7 MiB
- Throughput: 95 RPS

**Cache Performance**:
- L1: 65% (target: 95%)
- L2: 72% (target: 85%)
- L3: 58% (target: 80%, adoption: 12% → 100%)
- L4: 42% (target: 75%)
- **Aggregate**: 59% → 84% target

**CI Impact**:
- Install time: 50-70% of build
- With optimization: 10-20%
- **Savings**: 120-180 seconds per workflow
- **Annual cost savings**: $45K-$60K

### 6-Month Targets (End of Phase 6)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| L1 Hit Rate | 65% | 92% | +27% |
| L2 Hit Rate | 72% | 82% | +10% |
| L3 Hit Rate | 58% | 78% | +20% |
| L4 Hit Rate | 42% | 70% | +28% |
| **Aggregate** | 59% | 80.5% | +21.5% |
| API p50 | 10.4ms | <10ms | -0.4ms |
| API p95 | 13.0ms | <12ms | -1.0ms |
| API p99 | 12.9ms | <15ms | +2.1ms |
| Memory peak | 313.7 MiB | <300 MiB | -13.7 MiB |
| Throughput | 95 RPS | 140 RPS | +45 RPS |
| CI install time | ~3min | ~30sec | -82% |

### 12-Month Stretch Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| L1 Hit Rate | >98% | Hot/warm/cold + warming |
| L2 Hit Rate | >88% | Cost-aware eviction + quotas |
| L3 Hit Rate | >85% | 3-layer fallback + warming |
| L4 Hit Rate | >92% | Circuit breaker + adaptive TTL |
| **Aggregate** | >88% | Network effects across all |
| API p50 | <8ms | Most requests from L1 |
| API p95 | <10ms | p95 uses L2/L3 fallback |
| API p99 | <12ms | p99 with L4 latency |
| Throughput | 200+ RPS | Improved concurrency |
| CI install | 5-10% | Full L3 adoption |

### Regression Detection Thresholds

**Alert Triggers** (>20% regression from baseline):

| Metric | Baseline | Alert Threshold |
|--------|----------|-----------------|
| L1 Hit Rate | 65% | <52% (immediate investigation) |
| L2 Hit Rate | 72% | <58% (immediate) |
| L3 Hit Rate | 58% | <46% (immediate) |
| L4 Hit Rate | 42% | <34% (immediate) |
| API p50 | 10.4ms | >12.5ms |
| API p95 | 13.0ms | >15.6ms |
| API p99 | 12.9ms | >15.5ms |
| Memory peak | 313.7 MiB | >376.4 MiB |
| CI wall-clock | 45min | >54min |

**Automated Rollback**: If any metric exceeds threshold for >5 consecutive runs → automatic rollback

---

## 🎯 Staged Rollout Procedure

### Phase A: Development Environment (Days 1-3)

**Scope**: Local dev machines and CI test environment  
**Risk**: Low (isolated from production)

**Day 1: L1 Enablement**
- Deploy segmented LRU + adaptive TTL to test
- Monitor: L1 hit rate should reach 80%+
- Validate: No p99 latency regression
- **Success**: L1 hit rate ≥ 78% sustained for 2 hours

**Day 1-2: L2 Optimization**
- Deploy cost-aware eviction + disk quotas
- Monitor: L2 hit rate should reach 78%+
- Validate: Disk usage stays within 14.5GB
- **Success**: L2 hit rate ≥ 76%, disk controlled

**Day 2-3: L1+L2 Integration**
- Test L1 → L2 fallback performance
- Monitor: Aggregate hit rate should reach 85%+
- Validate: Fallback latency p95 < 50ms
- **Success**: Combined hit rate ≥ 85%, no conflicts

**Validation Checklist**:
- [ ] L1 hit rate ≥ 78% sustained
- [ ] L2 hit rate ≥ 76% sustained
- [ ] Combined L1+L2 hit rate ≥ 85%
- [ ] No new exceptions in logs
- [ ] Memory usage stable (4-hour test)
- [ ] Test suite 100% green

**Rollback**: Revert to baseline if any criterion fails

---

### Phase B: Staging Environment (Days 4-7)

**Scope**: Staging CI pipelines, non-critical workflows  
**Risk**: Medium (closer to production)

**Day 4: L1+L2 Promotion**
- Promote from dev to staging
- Monitor: Maintain L1+L2 hit rate ≥ 85%
- Validate: 100 CI runs without regression
- **Success**: Hit rate stability across 100 runs

**Day 4-5: L3 Workflow Migration (Phase 1)**
- Migrate first 10 workflows to standardized config
- Monitor: L3 hit rate should reach 60%+
- Validate: Cache restore time < 500ms (p95)
- **Success**: 10/10 workflows cached, no collisions

**Day 5-6: L3 Workflow Migration (Phase 2)**
- Migrate next 20 workflows
- Monitor: L3 hit rate should reach 65%+
- Validate: 30/42 adoption (71%)
- **Success**: 30/42 workflows adopted, no issues

**Day 6-7: L3 Completion**
- Migrate final 12 workflows
- Monitor: L3 hit rate should reach 70%+
- Validate: 42/42 adoption (100%)
- **Success**: Full adoption, aggregate ≥ 77%

**Validation Checklist**:
- [ ] L1+L2 hit rate maintained ≥ 85%
- [ ] L3 adoption reaches 100% (42/42)
- [ ] L3 hit rate reaches 70%+
- [ ] Aggregate hit rate (L1+L2+L3) ≥ 77%
- [ ] No cache corruption detected
- [ ] CI time reduced 30-40% vs baseline

**Rollback**: If L3 hit rate < 50%, revert workflows while investigating

---

### Phase C: Production Rollout (Days 8-14)

**Scope**: All production CI workflows  
**Risk**: High (production impact)

**Days 8-9: L1+L2+L3 Promotion**
- Promote to production (staged over 24 hours)
- Monitor: Watch for CI regression
- Validate: Aggregate hit rate ≥ 75%
- **Success**: No CI failures from cache changes

**Days 8-11: L4 Infrastructure**
- Deploy Redis cluster (3 nodes minimum)
- Test network connectivity from CI runners
- Configure persistence and monitoring
- **Success**: Redis ready, health checks passing

**Days 11-12: L4 Circuit Breaker**
- Deploy circuit breaker in "observe" mode
- Monitor: Track Redis failures, latencies
- Validate: Log failures but don't trigger
- **Success**: 0 cascading failures over 48 hours

**Days 13-14: L4 Active Mode**
- Switch circuit breaker to "active" mode
- Monitor: Should see fallback < 1% of requests
- Validate: L4 hit rate reaches 55%+, trending to 70%
- **Success**: L4 operational, < 1% failure rate

**Production Monitoring Dashboard**:
```
CACHE PERFORMANCE DASHBOARD (Real-Time)
─────────────────────────────────────
L1 Hit Rate: 92% (target: 95%) ▓▓▓▓▓▓▓▓▓░
L2 Hit Rate: 81% (target: 85%) ▓▓▓▓▓▓▓▓░░
L3 Hit Rate: 73% (target: 80%) ▓▓▓▓▓▓▓░░░ [42/42]
L4 Hit Rate: 58% (target: 75%) ▓▓▓▓▓░░░░░ [OK]
─────────────────────────────────────
AGGREGATE: 76% (target: 84%) ▓▓▓▓▓▓▓░░░ [+17%]
─────────────────────────────────────
CI Time: 32min (baseline: 50min) ↓ -36%
API p50: 9.8ms (target: <10ms) ✅
API p95: 12.2ms (target: <12ms) ✅
API p99: 14.1ms (target: <15ms) ✅
Memory: 298 MiB (target: <300) ✅
─────────────────────────────────────
Alerts: None | Last: 2h ago (L3 lag)
```

**Production Validation Checklist**:
- [ ] Aggregate cache hit rate ≥ 76% sustained
- [ ] L1-L3 hit rates maintained (no regression)
- [ ] L4 operational with circuit breaker
- [ ] CI success rate ≥ 99.5% (no cache failures)
- [ ] API latency within threshold
- [ ] Memory usage stable
- [ ] Monitoring alerts functioning
- [ ] Rollback capability tested

---

## 📈 Monitoring Dashboard Specifications

### Dashboard 1: Cache Hit Rate by Layer

**Prometheus Metrics**:
```prometheus
codex_cache_hit_rate{layer="L1"}
codex_cache_hit_rate{layer="L2"}
codex_cache_hit_rate{layer="L3"}
codex_cache_hit_rate{layer="L4"}

codex_cache_requests_total{layer="L1", status="hit|miss"}
codex_cache_latency_ms{layer="L1", quantile="0.50|0.95|0.99"}
```

**Visualization**:
- Gauge charts for each layer's hit rate
- Line chart showing 7-day trend
- Stacked bar chart for latencies (p50/p95/p99)
- Red alert highlighting if < target - 15%

### Dashboard 2: CI Wall-Clock Time Impact

**Metrics**:
```prometheus
codex_workflow_duration_seconds{workflow="pr-checks"}
codex_workflow_cache_time_percent{workflow="pr-checks"}
codex_workflow_install_duration_seconds{workflow="pr-checks"}
```

**Visualization**:
- Stacked bar showing install time % of total
- Before/after comparison
- Cost savings calculation ($USD per day)
- Org-wide impact (weekly minutes saved)

### Dashboard 3: Artifact Health Status

**Metrics**:
```prometheus
codex_cache_size_bytes{layer="L1|L2|L3|L4"}
codex_cache_evictions_total{layer="L2", reason="quota|ttl"}
codex_cache_corruption_errors_total
codex_cache_integrity_checks_failed_total
```

**Visualization**:
- Storage gauge vs quota for L2/L3/L4
- Eviction rate trend line
- Color-coded health indicators
- Alert panel for corruption

### Dashboard 4: Automated Rollback Triggers

**Metrics**:
```prometheus
codex_cache_regression_detected{metric="hit_rate", layer="L1"}
codex_deployment_rollback_total{reason="cache_regression"}
codex_cache_circuit_breaker_state{service="redis"}
```

**Visualization**:
- Large red panels for regression alerts
- Rollback history timeline
- Circuit breaker status indicator
- Manual override capability

---

## ✅ Success Criteria & Acceptance

### Per-Layer Acceptance Criteria

**L1 (In-Process Memory)**:
- ✅ Hit rate ≥ 92% over 24 hours
- ✅ Segment migration latency < 100μs (p99)
- ✅ Eviction thread CPU < 2%
- ✅ No p99 latency regression (< 1ms)
- ✅ Memory overhead < 5% increase

**L2 (Local Disk)**:
- ✅ Hit rate ≥ 80% over 24 hours
- ✅ Disk usage within 14.5GB quota
- ✅ Read latency p99 < 50ms
- ✅ Eviction latency < 1 second
- ✅ Binary serialization compatibility verified

**L3 (GitHub Actions)**:
- ✅ Adoption ≥ 95% (40/42 workflows minimum)
- ✅ Hit rate ≥ 75% over 7 days
- ✅ Cache restore < 500ms (p95)
- ✅ Zero workflow failures from cache issues
- ✅ Pre-commit cache hit rate ≥ 80%

**L4 (Redis)**:
- ✅ Availability ≥ 99.5%
- ✅ Hit rate ≥ 70% over 7 days
- ✅ Fallback to L2 within 100ms
- ✅ p99 latency ≤ 80ms
- ✅ Data persistence enabled and tested

### Overall Wave Success Criteria

- ✅ **Aggregate hit rate**: 59% → 76%+ (Phase C target: 76%, Phase target: 80%+)
- ✅ **CI time reduction**: 40-60% (120-180 seconds per workflow)
- ✅ **API latency**: No regression (p50 <10ms, p95 <12ms, p99 <15ms)
- ✅ **Memory**: Stable and predictable (<300 MiB peak)
- ✅ **Monitoring**: All dashboards functional with 0 blind spots
- ✅ **Regression detection**: Automated alerts working, 0 false positives
- ✅ **Rollback**: Tested and validated at each phase

---

## 📅 Timeline & Dependencies

### Critical Path

```
Week 1: L1 + L2 Enablement
├─ Days 1-3: Development environment (L1 + L2)
├─ Days 4-5: Staging environment (L1 + L2 promotion)
└─ Days 6-7: Production readiness (testing)

Week 2: L3 Migration
├─ Days 8-9: Phase 1 (10 workflows)
├─ Days 10-11: Phase 2 (20 workflows)
└─ Days 12-14: Phase 3 (12 workflows)

Week 3-4: L4 Infrastructure
├─ Days 15-18: Redis deployment + health checks
├─ Days 19-20: Circuit breaker enablement
└─ Days 21-28: Monitoring + optimization

Total: 4 weeks to full Wave 5 rollout
```

### Dependencies & Blockers

**Must Complete Before L1+L2 Promotion**:
- [ ] All Layer 1 code merged to main
- [ ] All Layer 2 code merged to main
- [ ] Combined test suite 100% green
- [ ] Performance baseline confirmed

**Must Complete Before L3 Migration**:
- [ ] L1+L2 stable in staging for 48 hours
- [ ] Standardized cache key format approved
- [ ] .github/actions/setup-python-cache updated
- [ ] scripts/ci/cache_adoption_report.py ready

**Must Complete Before L4 Deployment**:
- [ ] Redis infrastructure provisioned
- [ ] Network connectivity verified
- [ ] Monitoring endpoint accessible
- [ ] Circuit breaker code reviewed and tested

### Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Cache corruption in L3 | Low | High | Comprehensive testing, gradual rollout |
| Redis unavailability | Medium | Medium | Circuit breaker with L2 fallback |
| Lock contention in L1 | Medium | Low | Background eviction thread + RWLock |
| Disk quota exceeded in L2 | Low | Medium | Quota monitoring + automated cleanup |
| Regression in API latency | Low | High | Comprehensive regression test suite |

---

## 📞 Escalation & Support

**Phase Lead**: @mbaetiong (Full Authority)

**On-Call Support**:
- **Cache Issues**: Tag @cache-team in #infrastructure-alerts
- **CI/Workflow Issues**: Escalate to @workflow-team
- **Redis Issues**: Page @infra-oncall if availability < 99%
- **Performance Regression**: Page @perf-team, trigger incident

**Status Updates**:
- Daily standup in #phase-6-wave-5 during active rollout
- Weekly metrics report to @mbaetiong
- Immediate notification on threshold breaches

---

## 🔄 Rollback Plan

### Automatic Rollback Triggers

- Any metric exceeds alert threshold for >5 consecutive runs
- CI success rate drops below 99.5%
- Cache corruption detected (integrity check fails)
- Redis unavailability > 5 minutes without fallback

### Manual Rollback Procedure

1. **Identify**: Which layer(s) showing issues
2. **Isolate**: Disable affected layer while keeping others
3. **Fallback**: All traffic redirected to previous stable layer
4. **Notify**: Post incident in #phase-6-wave-5
5. **Preserve**: Keep cache state for post-mortem
6. **Investigate**: Root cause analysis within 24 hours
7. **Reattempt**: After fix validated in isolated environment

---

## 📝 Phase 6 Wave 5 Sign-Off

This execution brief is ready for staged rollout.

**Prepared By**: Copilot Cache Management Agent  
**Date**: 2026-02-17  
**Authority**: @mbaetiong (Approved for autonomous execution)  
**Review Status**: ✅ Ready for implementation

**Next Steps**:
1. Wait for Phase 6 Waves 1-4 stabilization
2. Trigger Phase A (Development Environment) rollout
3. Monitor metrics per staged procedure
4. Progress through Phases B and C with checkpoints

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-02-17  
**Revision**: Phase 6 Wave 5 Ready-State
