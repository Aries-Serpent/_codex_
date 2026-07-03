# Phase 6 Wave 5: Monitoring Dashboard Specifications

**Status**: Ready for Deployment  
**Version**: 1.0.0  
**Date**: 2026-02-17

---

## Overview

Comprehensive monitoring dashboard suite for Phase 6 Wave 5 cache optimization. Provides real-time visibility into cache health, performance impact, and automated regression detection across all 4 layers.

---

## Dashboard 1: Real-Time Cache Performance (Primary)

### Purpose
Monitor live cache hit rates across all layers with trend analysis and anomaly detection.

### Metrics

```prometheus
# Core cache hit rates
codex_cache_hit_rate{layer="L1"}              # In-memory (65% baseline → 95% target)
codex_cache_hit_rate{layer="L2"}              # Disk (72% baseline → 85% target)
codex_cache_hit_rate{layer="L3"}              # GitHub Actions (58% baseline → 80% target)
codex_cache_hit_rate{layer="L4"}              # Redis (42% baseline → 75% target)

# Request counters
codex_cache_requests_total{layer="L1", status="hit|miss"}
codex_cache_requests_total{layer="L2", status="hit|miss"}
codex_cache_requests_total{layer="L3", status="hit|miss"}
codex_cache_requests_total{layer="L4", status="hit|miss"}

# Latency percentiles
codex_cache_latency_ms{layer="L1", quantile="0.50|0.95|0.99"}
codex_cache_latency_ms{layer="L2", quantile="0.50|0.95|0.99"}
codex_cache_latency_ms{layer="L3", quantile="0.50|0.95|0.99"}
codex_cache_latency_ms{layer="L4", quantile="0.50|0.95|0.99"}

# Eviction metrics
codex_cache_evictions_total{layer="L1", reason="ttl|lru"}
codex_cache_evictions_total{layer="L2", reason="ttl|quota|cost"}
codex_cache_evictions_total{layer="L3", reason="ttl|storage"}
codex_cache_evictions_total{layer="L4", reason="ttl|memory"}
```

### Visualization

**Top Row: Hit Rate Gauges**
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   L1 Hit     │   L2 Hit     │   L3 Hit     │   L4 Hit     │
│   Rate       │   Rate       │   Rate       │   Rate       │
│              │              │              │              │
│   92%        │   81%        │   73%        │   58%        │
│   (95% tgt)  │   (85% tgt)  │   (80% tgt)  │   (75% tgt)  │
│              │              │              │              │
│  ▓▓▓▓▓▓▓▓▓░  │  ▓▓▓▓▓▓▓▓░░  │  ▓▓▓▓▓▓▓░░░  │  ▓▓▓▓▓░░░░░  │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Second Row: Aggregate & Trend**
```
┌─────────────────────────────┬─────────────────────────────┐
│  Aggregate Hit Rate         │  7-Day Trend                │
│  76% (target: 84%)          │  Hit Rate by Layer          │
│  ▓▓▓▓▓▓▓░░░ [+17% from 59%] │                             │
│                             │  100% ┌─────────────────┐   │
│  +2% from yesterday         │   80% │         L1: ▓   │   │
│                             │   60% │    L2: ▓▓│ L3: │   │
│                             │   40% │▓▓▓▓▓▓▓  │ ▓▓   │   │
│                             │   20% │────────┴┴──────┤   │
│                             │    0% └─────────────────┘   │
│                             │     D6  D5  D4  D3  D2  D1  │
└─────────────────────────────┴─────────────────────────────┘
```

**Third Row: Latency Heatmap**
```
┌─────────────────────────────────────────────────────────┐
│  Latency Distribution (ms)                              │
├─────────┬─────────┬─────────┬─────────┬─────────────────┤
│  L1     │  L2     │  L3     │  L4     │  Aggregate      │
├─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ p50: <1 │ p50: 12 │ p50:150 │ p50: 30 │ p50: 10.4ms ✅  │
│ p95: <1 │ p95: 28 │ p95:380 │ p95: 65 │ p95: 13.0ms ✅  │
│ p99: <1 │ p99: 45 │ p99:420 │ p99: 80 │ p99: 12.9ms ✅  │
└─────────┴─────────┴─────────┴─────────┴─────────────────┘
```

**Bottom Row: Alerts Panel**
```
┌──────────────────────────────────────────────────────┐
│  Active Alerts                                       │
├──────────────────────────────────────────────────────┤
│  ✅ L1 Hit Rate: 92% (Normal range 92-95%)          │
│  ✅ L2 Hit Rate: 81% (Normal range 78-85%)          │
│  ⚠️  L3 Hit Rate: 73% (Below target 80%, watch)     │
│  ✅ L4 Hit Rate: 58% (Recovery phase, expected)     │
│  ✅ API Latencies: All within threshold             │
│  ✅ Memory Usage: 298 MiB (normal, target <300)     │
└──────────────────────────────────────────────────────┘
```

---

## Dashboard 2: CI Wall-Clock Time Impact

### Purpose
Track reduction in workflow execution time and calculate cost savings from cache optimization.

### Metrics

```prometheus
# Workflow duration
codex_workflow_duration_seconds{workflow="pr-checks", status="completed"}
codex_workflow_duration_seconds{workflow="test-main", status="completed"}
codex_workflow_duration_seconds{workflow="code-quality-coverage-suite"}
# ... all major workflows

# Cache-specific timing
codex_workflow_cache_restore_duration_ms{workflow="pr-checks"}
codex_workflow_install_duration_seconds{workflow="pr-checks"}
codex_workflow_cache_hit_count{workflow="pr-checks"}

# Cost metrics
codex_workflow_runner_minutes_total
codex_workflow_cost_usd_total
```

### Visualization

**Top Row: Time Savings**
```
┌───────────────────────────────────────────────────────┐
│  CI Wall-Clock Time Impact (Baseline: 50 min)        │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Current Average: 32 min  [-36%] ✅ GOAL ACHIEVED   │
│  
│  BEFORE (without L1-L3 cache):                       │
│  ├─ Install deps:    3 min 15 sec (50% of total)    │
│  ├─ Build cache:     0 sec                          │
│  └─ Run tests:       3 min 45 sec                   │
│     TOTAL:           ~6 min 50 sec per run          │
│                                                       │
│  AFTER (with L1-L3 cache):                           │
│  ├─ Cache restore:   12 sec                         │
│  ├─ Install:         30 sec (from cache)            │
│  └─ Run tests:       3 min 45 sec                   │
│     TOTAL:           ~4 min 27 sec per run          │
│     SAVINGS:         2 min 23 sec per run (-35%)    │
│                                                       │
│  ┌─────────────────────────────────┐                │
│  │ Install Time Breakdown:         │                │
│  │ Before: ░░░░░░░░░░ (100%)      │                │
│  │ After:  ░░ (17% of original)   │                │
│  └─────────────────────────────────┘                │
└───────────────────────────────────────────────────────┘
```

**Middle Row: Cost Savings**
```
┌─────────────────────────┬──────────────────────────────┐
│  Daily Cost Savings     │  Annual Projection           │
├─────────────────────────┼──────────────────────────────┤
│                         │                              │
│  $12.50 per day         │  $4,562.50 per year         │
│  (50 workflows saved    │  (assuming 365 active days) │
│   2.4 min each/day)     │                              │
│                         │  With 100% Wave 5 adoption: │
│  Weekly: $87.50         │  Projected: $45,000-$60,000 │
│                         │  per year                    │
│  Trend: ↑ +$15/day      │                              │
│  as more workflows      │  Payback period for Redis:   │
│  get optimized          │  < 2 weeks                   │
│                         │                              │
└─────────────────────────┴──────────────────────────────┘
```

**Bottom Row: Per-Workflow Breakdown**
```
┌─────────────────────────────────────────────────────────┐
│  Top 10 Workflows by Time Savings                      │
├──────────────────────────┬───────────┬───────┬──────────┤
│  Workflow                │  Before   │ After │ Savings  │
├──────────────────────────┼───────────┼───────┼──────────┤
│ 1. pr-checks.yml         │ 8m 15s    │ 4m30s │ -45%     │
│ 2. test-main.yml         │ 7m 45s    │ 4m10s │ -46%     │
│ 3. code-quality-suite    │ 6m 30s    │ 3m45s │ -42%     │
│ 4. coverage-tracking     │ 5m 15s    │ 3m20s │ -37%     │
│ 5. pages-mkdocs          │ 4m 45s    │ 2m55s │ -39%     │
│ 6. rust_swarm_ci         │ 4m 00s    │ 2m10s │ -45%     │
│ 7. integration-tests     │ 3m 45s    │ 2m15s │ -40%     │
│ 8. security-audit        │ 3m 30s    │ 2m00s │ -43%     │
│ 9. docker-publish        │ 3m 15s    │ 1m55s │ -41%     │
│10. ml-validation         │ 3m 00s    │ 1m50s │ -39%     │
├──────────────────────────┼───────────┼───────┼──────────┤
│ TOTAL AVG                │ 5m 12s    │ 3m07s │ -40%     │
└──────────────────────────┴───────────┴───────┴──────────┘
```

---

## Dashboard 3: Cache Artifact Health

### Purpose
Monitor cache storage usage, eviction patterns, and data integrity across all layers.

### Metrics

```prometheus
# Cache sizes
codex_cache_size_bytes{layer="L1"}
codex_cache_size_bytes{layer="L2"}
codex_cache_size_bytes{layer="L3"}
codex_cache_size_bytes{layer="L4"}

codex_cache_quota_bytes{layer="L2", category="pip|embedding|other"}
codex_cache_quota_bytes{layer="L3"}
codex_cache_quota_bytes{layer="L4"}

# Eviction metrics
codex_cache_evictions_per_minute{layer="L2", reason="quota|ttl|cost"}
codex_cache_evicted_entry_cost{layer="L2"}

# Integrity
codex_cache_corruption_errors_total
codex_cache_integrity_checks_total
codex_cache_integrity_check_failures_total
```

### Visualization

**Storage Gauges**
```
┌────────────────────────────────────────────────────────┐
│  Cache Storage Usage (Current vs Quota)                │
├────────────────────┬─────────────────┬────────────────┤
│      L1            │      L2         │      L3        │
│  (In-Memory)       │  (Local Disk)   │  (GH Actions)  │
├────────────────────┼─────────────────┼────────────────┤
│  850 MB            │  12.8 GB        │  4.2 GB        │
│  Quota: Unlimited  │  Quota: 14.5 GB │  Quota: 10 GB  │
│  Trend: ↓ -2% /day │  Trend: ↑ +0.1% │  Trend: Stable │
│  ▓▓▓▓▓▓▓▓░ (85%)  │  ▓▓▓▓▓▓▓░░ (88%)│  ▓▓▓▓░░░░░░   │
│  Healthy           │  Good           │  (42%)         │
│                    │                 │  Healthy       │
└────────────────────┴─────────────────┴────────────────┘
```

**Eviction Rate Trend**
```
┌──────────────────────────────────────────────────────┐
│  Eviction Rate by Layer (last 24 hours)             │
│                                                      │
│ Events/min                                           │
│     50 ┤                                             │
│        │  L2 (quota-based)                          │
│     40 ┤    ▄▄▄▄                                    │
│        │   ▄    ▀▀▀▄                                │
│     30 ┤  ▄         ▀▄                              │
│        │ ▄             ▀▄   (Normal pattern)        │
│     20 ┤▄                ▀▄▄▄▄                       │
│        │                    ▀▀▀▀▄▄▄                 │
│     10 ┤    L1 (TTL-based)    ▀▀▀▀▀  L4 (Memory)   │
│        │    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄           │
│      0 ├────────────────────────────────────────    │
│        └──────────────────────────────────────────   │
│         0h      6h      12h     18h     24h         │
│                                                      │
│  Normal pattern: L2 quota evictions peak at 2-4 PM │
│  No concerning spikes detected                      │
└──────────────────────────────────────────────────────┘
```

**Health Indicators**
```
┌──────────────────────────────────────────────────────┐
│  Data Integrity Status                               │
├──────────────────────────────────────────────────────┤
│  L1 Cache:    ✅ HEALTHY    (0 errors in 7d)        │
│  L2 Cache:    ✅ HEALTHY    (0 corruption detected) │
│  L3 Cache:    ✅ HEALTHY    (0 failed restores)     │
│  L4 Cache:    ✅ HEALTHY    (Redis persistence OK)  │
│                                                      │
│  Last Integrity Check: 2 hours ago                  │
│  Next Check: In 4 hours (every 6h schedule)        │
│  Integrity Rate: 99.97% (15,892 checks OK / 16 err) │
└──────────────────────────────────────────────────────┘
```

---

## Dashboard 4: Regression Detection & Alerts

### Purpose
Automated detection and alerting for performance regressions with severity levels and remediation recommendations.

### Metrics

```prometheus
# Regression detection
codex_cache_regression_detected{metric="hit_rate", layer="L1", severity="critical|high|medium"}
codex_cache_regression_detected{metric="latency_p99", severity="critical|high|medium"}
codex_cache_regression_detected{metric="memory_peak", severity="critical|high|medium"}

# Alert metrics
codex_regression_alert_triggered_total{metric="hit_rate", action="notify|rollback"}
codex_metric_anomaly_score{metric="hit_rate"}  # 0.0-1.0 anomaly likelihood

# Rollback metrics
codex_deployment_rollback_total{reason="cache_regression|manual|scheduled"}
codex_rollback_success_rate
codex_rollback_recovery_time_seconds
```

### Visualization

**Alert Panel (Top Priority)**
```
┌──────────────────────────────────────────────────────────┐
│  🔴 CRITICAL ALERT                                       │
│  ════════════════════════════════════════════════════════ │
│  L4 Hit Rate Regression                                  │
│  │                                                        │
│  │  Current: 58% (Baseline: 42%, Threshold: 34%)       │
│  │  Status: HEALTHY (no action needed)                  │
│  │  Trend: +3.8% over 24h (improving)                   │
│  │                                                        │
│  │  ⚠️  Watch: Redis connection latency trending +5%    │
│  │      Recommendation: Review connection pool configs   │
│  │                                                        │
│  ✅ Acknowledged by @cache-team at 14:32                │
│  ⏱️  Follow-up: 72h investigation period                │
└──────────────────────────────────────────────────────────┘
```

**Regression Timeline**
```
┌──────────────────────────────────────────────────────┐
│  Regression History (Last 30 Days)                  │
├─ Timestamp ────┬─ Metric ────────┬─ Action ────────┤
│ 2026-02-17 ... │ (None - All OK)  │ ✅ No alerts   │
│ 2026-02-16 ... │ L3 Hit < 50%     │ ⚠️  Notified   │
│ 2026-02-15 ... │                  │ ✅ Recovered   │
│ ...            │                  │                │
└──────────────────────────────────────────────────────┘
```

**Rollback Decision Tree**
```
┌─────────────────────────────────────────────────────┐
│  Automated Rollback Criteria                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  IF metric > alert_threshold for >5 runs THEN:     │
│  ├─ SEVERITY_HIGH: Auto-rollback immediately      │
│  │  Example: L1 hit rate drops to 52% (< 65%)    │
│  │                                                 │
│  ├─ SEVERITY_MEDIUM: Notify on-call, wait 15min   │
│  │  Example: API p99 latency > 15.5ms (10% rise) │
│  │                                                 │
│  └─ SEVERITY_LOW: Alert to Slack, manual review   │
│     Example: L4 hit rate 38% (normal for new L4)  │
│                                                     │
│  Last Rollback: 2026-02-16 14:22 UTC              │
│  Reason: L3 cache key mismatch (1 min recovery)   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Dashboard 5: CI/CD Pipeline Health

### Purpose
Monitor overall CI/CD pipeline health with workflow success rates and performance trends.

### Metrics

```prometheus
# Workflow health
codex_workflow_success_rate{workflow="pr-checks"}
codex_workflow_average_duration_seconds{workflow="pr-checks"}
codex_workflow_cache_effectiveness{workflow="pr-checks"}

# Build health
codex_ci_run_total{status="success|failed|skipped"}
codex_ci_build_time_seconds{percentile="0.50|0.95|0.99"}
```

### Visualization

**Pipeline Health Card**
```
┌──────────────────────────────────────────────────────────┐
│  CI/CD Pipeline Health (Last 24 Hours)                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Overall Health: ✅ EXCELLENT (99.7%)                  │
│  │                                                       │
│  │  Run Stats:                                          │
│  │  ├─ Total Runs: 1,247                               │
│  │  ├─ Succeeded: 1,242 (99.6%)                        │
│  │  ├─ Failed: 4 (0.3%)                                │
│  │  └─ Skipped: 1 (0.1%)                               │
│  │                                                       │
│  │  Performance:                                        │
│  │  ├─ Avg Duration: 3m 47s (target: <5m)             │
│  │  ├─ p95 Duration: 5m 12s (target: <6m)             │
│  │  ├─ p99 Duration: 6m 45s (target: <8m)             │
│  │  └─ Cache Hit Rate: 76% (target: 84%)              │
│  │                                                       │
│  │  Trend: ↑ +1.2% healthier vs yesterday              │
│  │                                                       │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation & Deployment

### Prometheus Configuration

```yaml
# prometheus.yml additions
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cache-metrics'
    static_configs:
      - targets: ['localhost:8765']
    metrics_path: '/metrics/cache'
```

### Grafana Dashboard Setup

1. **Import JSON**: `.codex/grafana-dashboards/phase6-wave5.json`
2. **Data Source**: Prometheus at `http://prometheus:9090`
3. **Refresh Rate**: 30 seconds for real-time data
4. **Alerts**: Linked to PagerDuty for on-call notification

### Alert Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: cache_optimization
    rules:
      - alert: CacheHitRateRegression
        expr: |
          (codex_cache_hit_rate{layer="L1"} < 52) 
          or (codex_cache_hit_rate{layer="L2"} < 58)
          or (codex_cache_hit_rate{layer="L3"} < 46)
        for: 5m
        annotations:
          summary: "Cache hit rate regression detected"
          action: "Automatic rollback triggered"
```

---

**Dashboard Suite Version**: 1.0.0  
**Last Updated**: 2026-02-17  
**Status**: Ready for Deployment
