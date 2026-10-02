# Phase 4 Custom Images: Benchmarking & Performance Plan

**Status:** MEASUREMENT STRATEGY APPROVED  
**Baseline Collection:** Week 1 (Canary Phase)  
**Full Analysis:** Week 2  
**Authority:** @mbaetiong D-tier autonomous

---

## Executive Summary

This document defines the comprehensive performance benchmarking strategy for Phase 4 Custom Images rollout. We will measure **execution time**, **resource consumption**, **network I/O**, and **cost efficiency** using industry-standard metrics and automated dashboard queries.

**Expected Improvements:**
- ⏱️ 40-50% setup time reduction
- 💾 50%+ network I/O reduction  
- 💰 30-40% cost savings
- ✅ 99.5%+ reliability (no regression)

---

## Phase 4 Benchmarking Framework

### A. SETUP TIME METRICS

**What We Measure:**
- Time from job start to first actual workflow step (pure setup overhead)
- Breakdown: image pull → tool initialization → dependency resolution

**Baseline Collection:**

```bash
# Extract from workflow logs (GitHub Actions API)
# Pattern: Match "Run actions/setup-python" to "Run [next step]"

SETUP_BASELINE = (
  Average time across 50 legacy workflows 
  using actions/setup-python@v6
)

# Expected baseline: 60-90 seconds per setup-python call
```

**Custom Image Measurement:**

```bash
SETUP_CUSTOM = (
  Average time across 24 canary workflows
  using container image
  excluding container pull time (cached)
)

# Expected: 5-15 seconds (90% reduction)
```

**Formula:**

```
Setup Time Improvement = ((BASELINE - CUSTOM) / BASELINE) * 100%
Target: >= 40%
```

**Dashboard Query (GitHub Actions API):**

```graphql
query BenchmarkSetupTime {
  repository(owner: "Aries-Serpent", name: "_codex_") {
    workflows(first: 5, query: "name:validate") {
      nodes {
        runs(first: 20, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes {
            createdAt
            updatedAt
            jobs(first: 10) {
              nodes {
                name
                startedAt
                completedAt
                steps(first: 3) {
                  nodes {
                    name
                    startedAt
                    completedAt
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### B. TOTAL EXECUTION TIME

**What We Measure:**
- Full workflow duration (job start to completion)
- Broken down by: setup + execution + upload phases

**Baseline:**

```
EXECUTION_BASELINE = Average(legacy workflow durations)
Expected: 90-180 seconds (incl. setup overhead)
```

**Custom Image:**

```
EXECUTION_CUSTOM = Average(canary workflow durations)
Expected: 50-120 seconds (reduced setup overhead)
```

**Analysis:**

```
Total Time Improvement = ((BASELINE - CUSTOM) / BASELINE) * 100%
Target: >= 30%

If CUSTOM > BASELINE:
  → Investigate: container pull caching issues
  → Check: resource contention on runner
```

**Dashboard Query:**

```sql
-- Query GitHub Actions API logs via WorkflowRun objects
SELECT 
  workflow_name,
  run_id,
  status,
  created_at,
  updated_at,
  EXTRACT(EPOCH FROM (updated_at - created_at)) as duration_seconds,
  CASE 
    WHEN workflow_name LIKE '%canary%' THEN 'custom_image'
    ELSE 'legacy_setup'
  END as cohort
FROM workflow_runs
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### C. NETWORK I/O METRICS

**What We Measure:**
- Bytes downloaded for setup dependencies (actions, packages, tools)
- Network latency during image pull and pip install

**Baseline (Legacy Setup):**

```
Typical actions/setup-python@v6 downloads:
  - Action artifact: ~50MB
  - Python runtime: ~80-120MB
  - pip packages (if needed): ~50-200MB
  - Total: ~180-370MB per setup call

NETWORK_BASELINE = Average across legacy workflows
Expected: ~250MB per workflow
```

**Custom Image (Pre-cached):**

```
Typical container image pull:
  - Image download (first pull): ~200-300MB
  - Subsequent pulls (cached): ~1-5MB
  - pip install (project deps only): ~10-50MB
  
NETWORK_CUSTOM = Average across canary workflows
Expected: ~50MB per workflow (cached)
Expected: ~250MB per workflow (first pull)
```

**Metrics Collection (via Container Logs):**

```bash
# In workflow step, collect download stats
- name: Collect network metrics
  run: |
    # Track total bytes downloaded
    iftop -n -t -s 5 > network_stats.log 2>&1 || true
    
    # Track container image pull time
    docker images --digests > container_images.log
    
    # Track pip download size
    pip list --format json > installed_packages.json
    
    # Estimate based on package sizes
    python -c "
    import json
    with open('installed_packages.json') as f:
        packages = json.load(f)
    total_size = sum(p.get('size', 0) for p in packages)
    print(f'Estimated package size: {total_size / 1024 / 1024:.1f}MB')
    "
```

**Formula:**

```
Network I/O Reduction = ((BASELINE - CUSTOM) / BASELINE) * 100%
Target: >= 50% (for cached pulls)
```

### D. RESOURCE CONSUMPTION

**What We Measure:**
- CPU time during setup phase
- Memory usage (peak and average)
- Disk I/O for package installation

**Baseline (Legacy):**

```
setup-python@v6 resource profile:
  - CPU: 100% utilization during extraction (~30s)
  - Memory: Peak ~200MB, Average ~100MB
  - Disk I/O: High during pip install
```

**Custom Image:**

```
Container startup + execution:
  - CPU: Reduced during pull (already extracted)
  - Memory: Reduced (no redundant caching layer)
  - Disk I/O: Reduced (container layers pre-optimized)
```

**Collection Method (GitHub Actions Metrics):**

```yaml
- name: Export runner metrics
  if: always()
  run: |
    # GitHub Actions provides via environment variables
    echo "Runner OS: $RUNNER_OS"
    echo "Runner CPU Count: $RUNNER_PROCESSOR_COUNT"
    echo "Free Disk Space: $(df -h / | tail -1 | awk '{print $4}')"
    
    # Capture via /proc if available
    cat /proc/cpuinfo > cpuinfo.log 2>/dev/null || true
    cat /proc/meminfo > meminfo.log 2>/dev/null || true
```

### E. COST EFFICIENCY ANALYSIS

**GitHub Actions Pricing (as of 2026):**

```
ubuntu-latest:       $0.015 per minute
ubuntu-latest-m:     $0.020 per minute (with 4-core)
ubuntu-8-core:       $0.050 per minute (with 8-core)

Storage:             $0.50 per GB/month
Network egress:      $0.10 per GB (outside org)
```

**Baseline Cost (Legacy Setup):**

```
Per workflow run (avg):
  - Setup overhead: 90s @ $0.015/min = $0.0225
  - Execution: 60s @ $0.015/min = $0.0150
  - Total: ~$0.0375 per run

Monthly (for canary cohort at 8,760 runs):
  - $0.0375 * 8,760 = $328.50/month
  
Network cost (250MB * 1,000 runs/month * $0.10/GB):
  - ~$25/month
  
Total baseline: ~$353.50/month
```

**Custom Image Cost:**

```
Per workflow run (avg):
  - Image pull (cached): 5s @ $0.015/min = $0.00125
  - Execution: 60s @ $0.015/min = $0.0150
  - Total: ~$0.01625 per run (57% reduction)

Monthly (for canary cohort at 8,760 runs):
  - $0.01625 * 8,760 = $142.35/month
  
Network cost (50MB cached * 1,000 runs + 250MB first pulls):
  - ~$5/month

Total custom image: ~$147.35/month
  
Savings: $353.50 - $147.35 = $206.15/month (58% reduction)
```

**Formula:**

```
Cost Savings = ((BASELINE_COST - CUSTOM_COST) / BASELINE_COST) * 100%
Target: >= 30% (conservative estimate)
Expected: ~58% (aggressive estimate)
```

**Dashboard Query:**

```python
# Use GitHub API to pull billing data
import github

gh = github.Github(token=GITHUB_TOKEN)
org = gh.get_organization("Aries-Serpent")

# Fetch workflow usage
usage = org.get_workflow_run_usage()
billable_minutes_ubuntu = usage.billable_ubuntu_minutes

# Calculate estimated cost
cost_per_minute = 0.015
monthly_cost = billable_minutes_ubuntu * cost_per_minute
print(f"Estimated monthly cost: ${monthly_cost:.2f}")
```

---

## A/B Testing Strategy

### Test Design

**Group A (Control):** Legacy setup-* pattern
- Workflows: Randomly selected from non-canary cohort
- Duration: Week 2-3 (concurrent with canary)
- Size: ~50 workflows

**Group B (Treatment):** Custom image pattern
- Workflows: 24 canary workflows
- Duration: Week 1-2 (canary phase)
- Size: 24 workflows

**Randomization:**
- Not random per se (canary is non-critical workflows)
- But control group is statistically similar by: frequency, duration, dependencies

### Metrics Captured Per Run

```json
{
  "run_id": "abc123",
  "workflow_name": "validate.yml",
  "cohort": "canary_custom_image",
  "timestamp": "2026-07-18T14:30:00Z",
  "setup_time_seconds": 8.3,
  "execution_time_seconds": 45.2,
  "total_duration_seconds": 53.5,
  "setup_baseline_seconds": 78.4,
  "container_image": "ghcr.io/aries-serpent/codex-python-3.12:latest-slim",
  "container_pull_cached": true,
  "container_pull_time_seconds": 2.1,
  "network_bytes_downloaded": 5242880,
  "workflow_status": "success",
  "runner_name": "GitHub Actions Runner",
  "cpu_count": 2,
  "memory_gb": 7
}
```

### Statistical Analysis

**Hypothesis Test:**

```
H₀: Setup time(legacy) = Setup time(custom)
H₁: Setup time(legacy) > Setup time(custom)

Test: One-tailed t-test
α = 0.05 (95% confidence)
```

**Expected Outcome:**

```
With n=24 canary runs + n=50 control runs:

Setup time (legacy):   μ = 78.4s, σ = 5.2s
Setup time (custom):   μ = 8.3s, σ = 1.1s

t-statistic = (78.4 - 8.3) / sqrt((5.2²/24) + (1.1²/50))
            = 70.1 / sqrt(1.13 + 0.024)
            = 70.1 / 1.06
            ≈ 66.1

Critical value (t₀.₀₅, df=72) ≈ 1.67
Since t-statistic >> critical value: REJECT H₀ (highly significant)
```

---

## Real-Time Monitoring Dashboard

### Dashboard Components

**1. Setup Time Comparison**
- Chart: Box plot of legacy vs. custom image setup times
- Update frequency: Per workflow run (real-time)
- Threshold alert: If custom > legacy + 20%

**2. Cost Tracking**
- Chart: Cumulative cost (legacy baseline vs. custom)
- Update frequency: Daily
- Threshold alert: If custom cost > baseline + 5%

**3. Reliability Metrics**
- Chart: Success rate over time (legacy vs. custom)
- Update frequency: Hourly
- Threshold alert: If success rate < 99.5%

**4. Network Performance**
- Chart: Network I/O (bytes downloaded per run)
- Update frequency: Per workflow run
- Threshold alert: If network > baseline + 30%

**5. Container Registry Health**
- Chart: Pull success rate + latency
- Update frequency: Per pull
- Threshold alert: If pull fails or latency > 30s

### Query Examples for Dashboard

```sql
-- Query 1: Setup Time Comparison (30-day rolling)
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  CASE WHEN workflow_name IN (...canary_list...) 
    THEN 'custom_image' 
    ELSE 'legacy_setup' 
  END as cohort,
  COUNT(*) as run_count,
  AVG(EXTRACT(EPOCH FROM setup_duration)) as avg_setup_seconds,
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM setup_duration)
  ) as median_setup_seconds,
  PERCENTILE_CONT(0.95) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM setup_duration)
  ) as p95_setup_seconds
FROM workflow_runs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('hour', created_at), cohort
ORDER BY hour DESC;

-- Query 2: Cost Analysis (cumulative)
SELECT
  DATE(created_at) as day,
  SUM(CASE WHEN workflow_name IN (...canary_list...) 
      THEN computed_cost_custom 
      ELSE computed_cost_legacy 
    END) as daily_cost_usd,
  SUM(CASE WHEN workflow_name IN (...canary_list...) 
      THEN computed_cost_custom 
    END) as custom_daily_cost_usd
FROM workflow_runs
WHERE created_at >= NOW() - INTERVAL '14 days'
GROUP BY DATE(created_at)
ORDER BY day DESC;

-- Query 3: Reliability by Cohort
SELECT
  CASE WHEN workflow_name IN (...canary_list...) 
    THEN 'custom_image' 
    ELSE 'legacy_setup' 
  END as cohort,
  COUNT(*) as total_runs,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
  ROUND(
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100,
    2
  ) as success_rate_percent
FROM workflow_runs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY cohort;
```

---

## Baseline Measurement Strategy

### Week 1 Pre-Migration (Days 1-3)

**Collection Phase:**

1. **Run 50 legacy workflows 10 times each** (500 baseline runs)
   - Extract setup time from logs
   - Record total execution time
   - Note any failures/anomalies
   
2. **Collect environment data**
   - Runner specs (CPU, memory)
   - Network conditions
   - Time of day effects

3. **Calculate baseline statistics**

```python
import statistics

baseline_setup_times = [...]  # collected from logs

baseline_stats = {
    'mean': statistics.mean(baseline_setup_times),
    'median': statistics.median(baseline_setup_times),
    'stdev': statistics.stdev(baseline_setup_times),
    'p95': sorted(baseline_setup_times)[int(len(baseline_setup_times) * 0.95)]
}

# Expected output:
# baseline_stats = {
#     'mean': 78.4,
#     'median': 76.2,
#     'stdev': 5.2,
#     'p95': 89.3
# }
```

### Week 1 Post-Migration (Days 4-7)

**Measurement Phase:**

1. **Run 24 canary workflows continuously**
   - Each workflow runs 30+ times (for statistical significance)
   - Total: 720+ canary runs
   - Collect all metrics per run

2. **Compare cohorts**

```python
# Calculate improvement
improvement = (baseline_stats['mean'] - canary_stats['mean']) / baseline_stats['mean'] * 100
print(f"Setup time improvement: {improvement:.1f}%")

# Check for regressions
if canary_stats['mean'] > baseline_stats['mean'] * 1.1:
    print("⚠️ WARNING: Custom image slower than baseline (>10%)")
    trigger_rollback = True
else:
    print("✅ Custom image meets performance targets")
```

### Week 2 Analysis

**Comprehensive Report:**

- [ ] Setup time: baseline vs. custom
- [ ] Total execution time: baseline vs. custom
- [ ] Cost analysis: monthly savings projection
- [ ] Network I/O: reduction percentage
- [ ] Reliability: success rate comparison
- [ ] Resource utilization: CPU, memory, disk
- [ ] Statistical significance: t-test results
- [ ] Confidence intervals: 95% CI for all metrics

---

## Success Thresholds & Decision Gates

### Go/No-Go Criteria (End of Week 2)

✅ **PROCEED to Phase-2** if ALL criteria met:

- [ ] Setup time reduction: ≥40% (vs. baseline)
- [ ] Total time reduction: ≥30% (vs. baseline)
- [ ] Cost reduction: ≥30% (vs. baseline)
- [ ] Success rate: ≥99.5% (no regression)
- [ ] Network I/O: ≥50% reduction (vs. baseline)
- [ ] P-value (t-test): <0.05 (statistically significant)
- [ ] No P1 incidents correlated with migration
- [ ] Container registry health: 99.9%+ availability

❌ **ROLLBACK** if ANY of these occur:

- [ ] Setup time increase >10%
- [ ] Success rate drops <95%
- [ ] Cost increase >5%
- [ ] Network failures >0.1%
- [ ] P1 incident within 24h of canary
- [ ] Container registry unavailable >1h

### Monitoring During Canary

**Real-time Alerts (via GitHub Actions):**

```yaml
# Alert 1: Setup time regression
if: avg_setup_time > baseline_mean * 1.1
  then: Create high-priority issue

# Alert 2: Success rate drop
if: success_rate < 99.5%
  then: Page on-call engineer

# Alert 3: Cost anomaly
if: daily_cost > baseline_daily * 1.05
  then: Create diagnostic issue

# Alert 4: Container registry failures
if: pull_failure_rate > 0.001
  then: Rollback custom image
```

---

## Documentation & Reporting

### Weekly Report Template

```markdown
## Phase 4 Benchmarking Report — Week N

### Executive Summary
- Setup time improvement: X%
- Cost savings: $Y/month
- Success rate: Z%
- Status: [🟢 ON TRACK | 🟡 AT RISK | 🔴 ROLLBACK NEEDED]

### Detailed Metrics
- [Metrics table with baseline vs. custom vs. improvement %]

### Key Findings
- [3-5 bullet points on performance]

### Action Items
- [ ] Item 1
- [ ] Item 2

### Next Steps
- [Recommendations for Phase-2]
```

---

## Artifact Storage

All benchmarking artifacts stored in `.codex/benchmarking/`:

```
.codex/benchmarking/
├── baseline_metrics.json          # Week 1 pre-migration baseline
├── canary_runs_metrics.ndjson     # All canary run metrics (per-run)
├── weekly_summary_w1.json         # Week 1 analysis
├── weekly_summary_w2.json         # Week 2 analysis (decision gates)
├── statistical_analysis.json      # T-test results, confidence intervals
└── phase2_projections.json        # Cost/time projections for 219 workflows
```

---

**Document Owner:** Copilot Cloud Agent  
**Last Updated:** 2026-07-18  
**Version:** 1.0
