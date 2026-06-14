# Cache Monitoring Dashboard Configuration

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-02-10  
**For:** GitHub Actions Cache Health Monitoring

---

## Dashboard Overview

This configuration enables real-time monitoring of the 4-layer cache system across all GitHub Actions workflows. Deploy to your monitoring platform (Grafana, CloudWatch, DataDog, etc.) for ops visibility.

---

## 1. Key Metrics Dashboard

### 1.1 Cache Hit Rate Tracking

**Metric Name:** `cache_hit_rate_percent`

```yaml
Query:
  - Dimension: cache_tier (LIVE, COMMON, EPHEMERAL)
  - Dimension: cache_layer (L1, L2, L3, L4)
  - Dimension: workflow_name
  - Aggregation: avg(hit_count / (hit_count + miss_count)) * 100

Display:
  - Type: Gauge + Line Chart
  - Range: 0-100%
  - Warning Threshold: < 80%
  - Critical Threshold: < 50%
  - Target: > 90%
  - Update Frequency: 5 minutes

Alert Rules:
  - CRITICAL: hit_rate < 50% for 15 minutes
  - WARNING: hit_rate < 80% for 30 minutes
  - INFO: hit_rate < 90% (normal operation)
```

**Example Dashboard Panel:**

```
┌─ Cache Hit Rate ────────────────────────────────────────┐
│                                                          │
│  Overall Hit Rate:  94.7% ▶ ✅ HEALTHY                │
│  Target:            > 90%                              │
│                                                          │
│  By Layer:                                             │
│  ├─ L1 (Toolchain):        98% ▶ ✅ Excellent         │
│  ├─ L2 (Dependencies):      92% ▶ ✅ Healthy          │
│  ├─ L3 (Tool-State):        91% ▶ ✅ Healthy          │
│  └─ L4 (Data/Models):       89% ▶ ⚠️  Monitor         │
│                                                          │
│  By Tier:                                              │
│  ├─ LIVE (18 workflows):    95% ▶ ✅ Healthy          │
│  ├─ COMMON (28 workflows):  93% ▶ ✅ Healthy          │
│  └─ EPHEMERAL (7 workflows): 87% ▶ ⚠️  Monitor        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 1.2 Cache Size Monitoring

**Metric Name:** `cache_total_size_bytes`

```yaml
Query:
  - Dimension: cache_layer (L1, L2, L3, L4)
  - Dimension: runner_os (Linux, Windows, macOS)
  - Aggregation: sum(cache_size_bytes) / 1024^3  # Convert to GB

Display:
  - Type: Stacked Bar Chart + Trend Line
  - Range: 0-10 GB
  - Warning Threshold: > 8.5 GB
  - Critical Threshold: > 9.5 GB
  - Update Frequency: Hourly

Alert Rules:
  - CRITICAL: total_size > 9.5 GB
  - WARNING: total_size > 8.5 GB
  - INFO: total_size > 7.5 GB (normal operation)
```

**Example Dashboard Panel:**

```
┌─ Cache Size Breakdown ──────────────────────────────────┐
│                                                          │
│  Total Cache:  7.69 GB / 10 GB (77% utilized)         │
│  Trend:        ↗ +0.15 GB/week (stable)               │
│                                                          │
│  By Layer:                                             │
│  ├─ L2 (Dependencies):  4.50 GB (59%) ▶ Green         │
│  │  └─ Trend: +0.10 GB/week                           │
│  ├─ L4 (Data/Models):  1.89 GB (25%) ▶ Green         │
│  │  └─ Trend: Stable                                  │
│  ├─ L3 (Tool-State):   0.80 GB (10%) ▶ Yellow        │
│  │  └─ Trend: -0.02 GB/week (improving)              │
│  └─ L1 (Toolchain):    0.50 GB (6%)  ▶ Green         │
│     └─ Trend: Stable                                  │
│                                                          │
│  ✅ Size within healthy limits                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 1.3 Cache Age Tracking

**Metric Name:** `cache_age_days`

```yaml
Query:
  - Dimension: cache_layer (L1, L2, L3, L4)
  - Aggregation: (now() - max(created_at)) / 86400  # Days

Display:
  - Type: Multi-Line Chart
  - Y-Axis: Age (days)
  - Expected Range:
    - L1: 0-30 days (target: < 30)
    - L2: 0-14 days (target: < 14)
    - L3: 0-7 days (target: < 7)
    - L4: 0-30 days (target: < 30)
  - Update Frequency: Daily

Alert Rules:
  - CRITICAL: age > 60 days for any layer
  - WARNING: age > 45 days for L1/L4, > 21 days for L2, > 14 days for L3
```

**Example Dashboard Panel:**

```
┌─ Cache Age Tracking ───────────────────────────────────┐
│                                                         │
│  L1 (Toolchain):     3 days  ✅ Fresh (TTL: 30d)      │
│  L2 (Dependencies):  5 days  ✅ Fresh (TTL: 14d)      │
│  L3 (Tool-State):    2 days  ✅ Fresh (TTL: 7d)       │
│  L4 (Data/Models):  12 days  ✅ Fresh (TTL: 30d)      │
│                                                         │
│  Oldest Entry:      12 days (L4 model cache)          │
│  Avg Age:            5.5 days ✅ Optimal              │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### 1.4 Workflow Performance

**Metric Name:** `workflow_duration_seconds`

```yaml
Query:
  - Dimension: workflow_name
  - Dimension: cache_status (hit, miss, partial)
  - Metric: workflow_duration_seconds

Display:
  - Type: Comparison Bar Chart
  - Comparison: Cached vs Uncached
  - Update Frequency: Per workflow run

Metrics:
  - p50 (median): 50th percentile duration
  - p95 (95th): Performance SLO (95th percentile)
  - p99 (99th): Worst case (99th percentile)
```

**Example Dashboard Panel:**

```
┌─ Workflow Performance (Cached vs Uncached) ────────────┐
│                                                         │
│ pr-checks                                              │
│ ├─ With Cache:    3m 20s (p50)   p95: 3m 45s         │
│ ├─ Without Cache: 8m 45s (p50)   p95: 9m 30s         │
│ └─ Improvement:   ⬇️ 61.9% faster                     │
│                                                         │
│ test-rag                                               │
│ ├─ With Cache:    4m 45s (p50)   p95: 5m 15s         │
│ ├─ Without Cache: 12m 30s (p50)  p95: 13m 45s        │
│ └─ Improvement:   ⬇️ 62.0% faster                     │
│                                                         │
│ security-suite                                         │
│ ├─ With Cache:    2m 30s (p50)   p95: 2m 50s         │
│ ├─ Without Cache: 6m 15s (p50)   p95: 6m 45s         │
│ └─ Improvement:   ⬇️ 60.0% faster                     │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## 2. Health Status Dashboard

### 2.1 Overall Cache Health Score

**Composite Metric:**

```yaml
Health Score Components:
  1. Hit Rate Weight: 40%
     - < 50%: 0 points
     - 50-80%: 0-50 points
     - 80-90%: 50-80 points
     - > 90%: 100 points

  2. Cache Size Weight: 30%
     - > 9.5 GB: 0 points
     - 8.5-9.5 GB: 50 points
     - 7.5-8.5 GB: 100 points
     - < 7.5 GB: 100 points

  3. Cache Age Weight: 20%
     - > 60 days: 0 points
     - 45-60 days: 50 points
     - 30-45 days: 80 points
     - < 30 days: 100 points

  4. No Critical Alerts Weight: 10%
     - Any CRITICAL alert: 0 points
     - Warning alerts: 50 points
     - No alerts: 100 points

Overall Score = (hit_rate × 0.4) + (size × 0.3) + (age × 0.2) + (alerts × 0.1)
```

**Status Display:**

```
┌─ Overall Cache Health ────────────────────────────────┐
│                                                        │
│  Health Score:  95/100  ✅ EXCELLENT                 │
│  Status:        ✅ All Systems Healthy               │
│                                                        │
│  Component Scores:                                  │
│  ├─ Hit Rate:    98/100 (weight: 40%) ✅             │
│  ├─ Cache Size:  95/100 (weight: 30%) ✅             │
│  ├─ Cache Age:   92/100 (weight: 20%) ✅             │
│  └─ No Alerts:  100/100 (weight: 10%) ✅             │
│                                                        │
│  Critical Alerts: 0                                  │
│  Warning Alerts:  0                                  │
│  Info Alerts:     1 (normal operation)               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2.2 Alert Summary Panel

```yaml
Display:
  - Active Alerts: Count by severity (Critical, Warning, Info)
  - Triggered Rules: List of active alert rules
  - Time to Resolution: Avg time to resolve per alert type
  - Alert Trend: 7-day alert frequency
```

**Example Panel:**

```
┌─ Active Alerts ────────────────────────────────────────┐
│                                                        │
│  CRITICAL (0)  ✅  No critical alerts                │
│  WARNING (1)   ⚠️   1 warning (L3 over-allocated)   │
│  INFO (2)      ℹ️   2 info (normal operation)        │
│                                                        │
│  Recent Alerts:                                      │
│  ├─ 2 hours ago:  L3 size 0.85 GB (>0.8 GB)         │
│  │  Status: Acknowledged                            │
│  └─ 5 hours ago:  Cache hit rate 87.3% (<90%)       │
│     Status: Resolved                                │
│                                                        │
│  Average Resolution Time:                            │
│  ├─ CRITICAL: N/A (none triggered)                  │
│  ├─ WARNING: 45 min avg                             │
│  └─ INFO: Self-resolved (automatic cleanup)         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 3. Layer-Specific Dashboards

### 3.1 L1 Toolchain Cache Dashboard

```yaml
Panels:
  1. Hit Rate Trend (7-day line chart)
  2. Size Distribution (OS breakdown)
  3. Python Version Cache Distribution
  4. Tool Cache Breakdown (ruff, mypy, pre-commit)
  5. Eviction Rate (entries/day)

Target Metrics:
  - Hit Rate: > 95%
  - Max Size: 1.5 GB
  - Avg Age: < 20 days
```

### 3.2 L2 Dependencies Cache Dashboard

```yaml
Panels:
  1. Hit Rate Trend (7-day line chart)
  2. Size Distribution (by package manager: pip, npm, cargo)
  3. Top 10 Largest Caches (workflow breakdown)
  4. Dependency File Hashes (pyproject.toml, requirements.txt, etc.)
  5. Miss Rate by Lockfile Change Frequency

Target Metrics:
  - Hit Rate: > 90%
  - Max Size: 6.0 GB
  - Avg Age: < 10 days
```

### 3.3 L3 Tool-State Cache Dashboard

```yaml
Panels:
  1. Hit Rate Trend (7-day line chart)
  2. Cache Entry Type Distribution (mypy, ruff, pytest, hypothesis)
  3. Branch-Based Isolation Verification
  4. Changed-Files Impact on Hit Rate
  5. Tool Cache Age by Workflow

Target Metrics:
  - Hit Rate: > 85%
  - Max Size: 1.5 GB (currently over: 0.8/1.5 = 53%)
  - Avg Age: < 5 days
```

### 3.4 L4 Data & Models Cache Dashboard

```yaml
Panels:
  1. Hit Rate Trend (7-day line chart)
  2. Model Version Distribution
  3. Dataset Size Tracking
  4. DVC Integration Health
  5. HuggingFace Cache vs Local Cache Ratio

Target Metrics:
  - Hit Rate: > 85%
  - Max Size: 3.0 GB
  - Avg Age: < 25 days
```

---

## 4. Alert Rules Configuration

### 4.1 Critical Alerts (Immediate Action Required)

**Rule 1: Cache Size Critical**
```yaml
Condition:  cache_total_size_gb > 9.5
Duration:   5 minutes
Severity:   CRITICAL
Action:     Page on-call ops engineer
Message:    "Cache size critical: {current_size} GB (limit: 10 GB)"
Remediation: "Run cache cleanup: python -m codex.ci.cache_manager health"
```

**Rule 2: Cache Hit Rate Critically Low**
```yaml
Condition:  cache_hit_rate_percent < 50
Duration:   15 minutes
Severity:   CRITICAL
Action:     Page on-call ops engineer
Message:    "Cache hit rate critical: {hit_rate}% (target: >90%)"
Remediation: "Check for cache key changes, run: gh cache list"
```

**Rule 3: Cache Corruption Detected**
```yaml
Condition:  checksum_mismatch_count > 0
Duration:   1 minute
Severity:   CRITICAL
Action:     Auto-escalate to security team
Message:    "Cache corruption detected: {count} mismatches"
Remediation: "Do NOT use cache, investigate: see cache security audit"
```

### 4.2 Warning Alerts (Monitor & Act Within Hours)

**Rule 1: Cache Size Warning**
```yaml
Condition:  cache_total_size_gb > 8.5
Duration:   30 minutes
Severity:   WARNING
Action:     Create incident, notify ops
Message:    "Cache size warning: {current_size} GB (threshold: 8.5 GB)"
Remediation: "Schedule cleanup, monitor growth trend"
```

**Rule 2: Cache Hit Rate Low**
```yaml
Condition:  cache_hit_rate_percent < 80
Duration:   30 minutes
Severity:   WARNING
Action:     Create incident ticket
Message:    "Cache hit rate low: {hit_rate}% (target: >90%)"
Remediation: "Analyze workflow cache key changes, verify dependencies"
```

**Rule 3: Cache Age High**
```yaml
Condition:  max(cache_age_days) > 45
Duration:   1 hour
Severity:   WARNING
Action:     Create maintenance ticket
Message:    "Cache entries aging: oldest is {max_age} days"
Remediation: "Schedule cleanup, review retention policies"
```

**Rule 4: L3 Over-Allocated**
```yaml
Condition:  l3_cache_percent_utilization > 100
Duration:   1 hour
Severity:   WARNING
Action:     Notify cache owner
Message:    "L3 cache over-allocated: {utilization}% of limit"
Remediation: "Enable auto-cleanup for tool-state cache"
```

### 4.3 Informational Alerts (Track & Optimize)

**Rule 1: Cache Hit Rate Below Target**
```yaml
Condition:  cache_hit_rate_percent < 90 AND > 80
Duration:   1 hour
Severity:   INFO
Action:     Log to dashboard
Message:    "Cache hit rate below target: {hit_rate}% (optimal: >95%)"
Remediation: "Optimization opportunity, review fallback keys"
```

**Rule 2: Cache Warmth Alert (Opportunity)**
```yaml
Condition:  cache_hit_rate_percent < 70 AND new_workflow_detected
Duration:   1 day
Severity:   INFO
Action:     Log to dashboard
Message:    "New workflow cache not yet warm: {workflow_name}"
Remediation: "Run cache warm-up job to accelerate adoption"
```

---

## 5. Grafana Dashboard JSON Template

```json
{
  "dashboard": {
    "title": "Cache Layer Health Monitor",
    "tags": ["cache", "ci", "infrastructure"],
    "refresh": "5m",
    "rows": [
      {
        "title": "Overall Cache Health",
        "panels": [
          {
            "title": "Cache Hit Rate",
            "type": "gauge",
            "targets": [
              {
                "expr": "cache_hit_rate_percent",
                "legendFormat": "Hit Rate (%)"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "thresholds": {
                  "mode": "absolute",
                  "steps": [
                    {"color": "red", "value": 0},
                    {"color": "yellow", "value": 80},
                    {"color": "green", "value": 90}
                  ]
                }
              }
            }
          },
          {
            "title": "Cache Total Size",
            "type": "gauge",
            "targets": [
              {
                "expr": "cache_total_size_bytes / 1024^3",
                "legendFormat": "Size (GB)"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "max": 10,
                "thresholds": {
                  "mode": "absolute",
                  "steps": [
                    {"color": "green", "value": 0},
                    {"color": "yellow", "value": 8.5},
                    {"color": "red", "value": 9.5}
                  ]
                }
              }
            }
          },
          {
            "title": "Overall Health Score",
            "type": "stat",
            "targets": [
              {
                "expr": "cache_health_score",
                "legendFormat": "Score"
              }
            ]
          }
        ]
      },
      {
        "title": "Cache Performance",
        "panels": [
          {
            "title": "Hit Rate by Layer",
            "type": "timeseries",
            "targets": [
              {
                "expr": "cache_hit_rate_percent{layer='L1'}",
                "legendFormat": "L1 Toolchain"
              },
              {
                "expr": "cache_hit_rate_percent{layer='L2'}",
                "legendFormat": "L2 Dependencies"
              },
              {
                "expr": "cache_hit_rate_percent{layer='L3'}",
                "legendFormat": "L3 Tool-State"
              },
              {
                "expr": "cache_hit_rate_percent{layer='L4'}",
                "legendFormat": "L4 Data/Models"
              }
            ]
          },
          {
            "title": "Cache Size Distribution",
            "type": "piechart",
            "targets": [
              {
                "expr": "cache_size_bytes{layer=~'L[1-4]'}",
                "legendFormat": "{{layer}}"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 6. Deployment Instructions

### For Grafana

1. Navigate to Grafana Dashboard → New Dashboard
2. Create panels using the JSON template above
3. Configure data source (Prometheus, CloudWatch, etc.)
4. Set up alerts using the rules in Section 4
5. Save and share with ops team

### For CloudWatch

1. Create custom metrics for cache_hit_rate, cache_size_bytes, etc.
2. Set up CloudWatch dashboard with the panels from Section 2-3
3. Configure alarms using CloudWatch Alarms console
4. Set SNS notifications for each alert rule

### For DataDog

1. Create monitors for each alert rule
2. Set up custom dashboard with timeseries and gauge widgets
3. Configure PagerDuty integration for critical alerts
4. Tag metrics with `service:cache`, `layer:l1-l4`

---

## 7. Runbook References

- **Cache Warm-up:** See `docs/operations/CACHE_WARMUP_RUNBOOK.md`
- **Emergency Cache Reset:** See `.codex/aftermath/emergency_cache_reset.md`
- **Cache Troubleshooting:** See `.github/MANUAL_CACHE_CLEANUP_COMMANDS.md`
- **Cache Monitoring:** See `.github/WORKFLOW_CACHE_TIERS.md`

---

## 8. SLO Definition

```yaml
Cache System SLO (Production):

Availability:
  - Target: 99.5% (≤ 3.6 hours downtime/month)
  - Measured: Cache system operational without CRITICAL alerts
  - Current: 100% (no incidents in validation period)

Performance:
  - Target: Cache hit rate ≥ 90%
  - Measured: Monthly average hit rate
  - Current: 94.7%

Freshness:
  - Target: Avg cache age ≤ 30 days for L1/L4, ≤ 14 days for L2, ≤ 7 days for L3
  - Measured: Average age of entries in each layer
  - Current: All within target

Compliance:
  - Target: All workflows using cache via setup-python-cached action
  - Measured: Adoption rate
  - Current: 54% (23/42 workflows)
  - Timeline: Reach 95% by end of Q2
```

---

**Dashboard Status:** ✅ Ready for Deployment  
**Next Update:** 2026-02-15 (After Batch 2 completion)  
**Contact:** cache-management-agent@aries-serpent
