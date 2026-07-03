# PHASE 8.3: PERFORMANCE BASELINE ESTABLISHMENT — README

**Version:** 1.0.0  
**Established:** 2026-06-22  
**Status:** 🟢 ACTIVE

---

## Overview

Phase 8.3 establishes production performance baselines for Codex v0.1.0-final and enables continuous performance monitoring with automated regression detection and SLA enforcement.
 # pragma: allowlist secret
## Core Deliverables

### 1. Documentation Files

#### `.codex/PHASE_8_3_PERFORMANCE_BASELINE.md`
- **Purpose:** Official production performance baseline
- **Contains:** Baseline metrics, SLA thresholds, detection rules
- **Update Frequency:** Quarterly or as needed
- **Size:** ~12 KB

#### `.codex/PHASE_8_3_PERFORMANCE_REPORT.md`
- **Purpose:** Weekly performance report template
- **Contains:** Sample report structure and metrics
- **Update Frequency:** Auto-generated weekly (Monday 06:00 UTC)
- **Size:** ~9 KB

#### `.codex/PHASE_8_3_SLA_THRESHOLDS.json`
- **Purpose:** SLA configuration for monitoring
- **Contains:** Metric thresholds, alert rules, escalation procedures
- **Format:** JSON
- **Update Frequency:** As needed (with approval)
- **Size:** ~5 KB

### 2. Python Scripts

#### `scripts/ci/phase_8_3_benchmark_collector.py`
**Purpose:** Collect GitHub Actions performance metrics

**Usage:**
```bash
# Collect last 24 hours of metrics
python scripts/ci/phase_8_3_benchmark_collector.py

# Collect last 72 hours
python scripts/ci/phase_8_3_benchmark_collector.py --hours 72

# Filter by workflow
python scripts/ci/phase_8_3_benchmark_collector.py --workflow "CI"

# Export to JSON
python scripts/ci/phase_8_3_benchmark_collector.py --export-json metrics.json
```

**Metrics Collected:**
- Workflow execution times (mean, p50, p95, p99)
- Job execution times by type
- GitHub API response times
- Cache hit rates
- Artifact processing times

**Output:** JSON format with per-metric percentiles

---

#### `scripts/ci/phase_8_3_perf_analyzer.py`
**Purpose:** Analyze metrics against baselines and detect regressions

**Usage:**
```bash
# Basic analysis
python scripts/ci/phase_8_3_perf_analyzer.py --current metrics.json

# Compare against baseline
python scripts/ci/phase_8_3_perf_analyzer.py \
  --current metrics.json \
  --baseline baseline.json

# Generate markdown report
python scripts/ci/phase_8_3_perf_analyzer.py \
  --current metrics.json \
  --generate-report

# Export analysis as JSON
python scripts/ci/phase_8_3_perf_analyzer.py \
  --current metrics.json \
  --export-json analysis.json
```

**Analysis Performed:**
- Baseline comparison (delta %)
- Regression detection (WARNING/CRITICAL/SEVERE)
- Trend analysis
- Percentile calculations
- Report generation

**Output:** Markdown report + JSON results

---

#### `scripts/ci/phase_8_3_sla_enforcer.py`
**Purpose:** Enforce SLA thresholds and manage alerts

**Usage:**
```bash
# Check SLA compliance
python scripts/ci/phase_8_3_sla_enforcer.py --metrics metrics.json --check-sla

# Send alerts (requires env vars)
python scripts/ci/phase_8_3_sla_enforcer.py --metrics metrics.json --send-alerts

# Export violations
python scripts/ci/phase_8_3_sla_enforcer.py \
  --metrics metrics.json \
  --export-json violations.json
```

**Functions:**
- SLA threshold checking
- Violation detection and categorization
- Alert summary generation
- Automatic rollback decision logic
- Violations export (JSON)

**Output:** Violation report + JSON data

---

### 3. GitHub Actions Workflow

#### `.github/workflows/phase-8-3-perf-monitor.yml`
**Purpose:** Continuous performance monitoring (runs hourly)

**Jobs:**
1. `collect-metrics` — Gathers performance data
2. `analyze-metrics` — Analyzes metrics against baseline
3. `enforce-sla` — Checks SLA compliance
4. `update-dashboard` — Updates performance dashboard
5. `notify` — Sends notifications
6. `summary` — Generates summary

**Trigger:** Hourly schedule + on-demand

**Artifacts Generated:**
- `performance-metrics/metrics-current.json`
- `performance-analysis/analysis-results.json`
- `sla-violations/sla-violations.json`

---

## Key Metrics

### Baseline Metrics (v0.1.0-final)

| Metric | Baseline | P95 | P99 | Alert >20% |
|--------|----------|-----|-----|-----------|
| Workflow Exec Time | 300s | 450s | 600s | 90s |
| Job Exec Time | 120s | 200s | 250s | 24s |
| API Response Time | 500ms | 1.5s | 3s | 100ms |
| Artifact Processing | 30s | 50s | 75s | 4.5s |
| Cache Hit Rate | 75% | — | — | <60% |

### SLA Tiers

**GREEN (Acceptable)**
- Deviation: <5-10% from baseline
- Action: None

**YELLOW (Warning)**
- Deviation: 10-20% from baseline
- Action: Log + Slack notification

**RED (Critical)**
- Deviation: >20% from baseline
- Action: Escalate to @mbaetiong

**BLACK (Severe)**
- Deviation: >30% from baseline
- Action: Trigger rollback decision

---

## Installation & Setup

### Prerequisites

```bash
# Python 3.11+
python --version

# Required packages
pip install requests pyyaml
```

### Quick Start

1. **View Baseline:**
   ```bash
   cat .codex/PHASE_8_3_PERFORMANCE_BASELINE.md
   ```

2. **View SLA Configuration:**
   ```bash
   cat .codex/PHASE_8_3_SLA_THRESHOLDS.json
   ```

3. **Collect Metrics (Local Test):**
   ```bash
   GITHUB_TOKEN=your_token python scripts/ci/phase_8_3_benchmark_collector.py
   ```

4. **Run Analysis:**
   ```bash
   python scripts/ci/phase_8_3_perf_analyzer.py --current metrics.json
   ```

5. **Check SLA:**
   ```bash
   python scripts/ci/phase_8_3_sla_enforcer.py --metrics metrics.json --check-sla
   ```

---

## Workflow Examples

### Example 1: Manual Metrics Collection

```bash
#!/bin/bash

# Collect 24-hour metrics
python scripts/ci/phase_8_3_benchmark_collector.py \
  --owner Aries-Serpent \
  --repo _codex_ \
  --hours 24 \
  --export-json metrics-$(date +%Y%m%d).json

echo "✅ Metrics collected"
```

### Example 2: Performance Analysis with Report

```bash
#!/bin/bash

# Collect current metrics
python scripts/ci/phase_8_3_benchmark_collector.py \
  --export-json current.json

# Analyze against baseline
python scripts/ci/phase_8_3_perf_analyzer.py \
  --current current.json \
  --baseline .codex/baseline.json \
  --generate-report \
  --export-json analysis.json

# Check SLA
python scripts/ci/phase_8_3_sla_enforcer.py \
  --metrics current.json \
  --check-sla

echo "✅ Analysis complete"
```

### Example 3: Weekly Report Generation

```bash
#!/bin/bash

# This runs automatically every Monday at 06:00 UTC
# Manual trigger:

python scripts/ci/phase_8_3_benchmark_collector.py \
  --hours 168 \
  --export-json weekly-metrics.json

python scripts/ci/phase_8_3_perf_analyzer.py \
  --current weekly-metrics.json \
  --generate-report > weekly-report.md

echo "✅ Weekly report generated"
```

---

## Configuration

### Modifying SLA Thresholds

Edit `.codex/PHASE_8_3_SLA_THRESHOLDS.json`:

```json
{
  "sla_thresholds": {
    "workflow_execution_time": {
      "baseline_ms": 300000,
      "baseline_p95_ms": 450000,
      "deviation_acceptable_percent": 5,
      "alert_threshold_percent": 20
    }
    // ...
  }
}
```

**Steps:**
1. Edit the JSON file
2. Validate: `python -m json.tool PHASE_8_3_SLA_THRESHOLDS.json`
3. Commit: `git commit -m "chore: update SLA thresholds"`
4. Changes take effect immediately

### Adjusting Monitoring Schedule

Edit `.github/workflows/phase-8-3-perf-monitor.yml`:

```yaml
on:
  schedule:
    # Change frequency (cron syntax)
    - cron: "0 * * * *"  # Every hour
    # Options:
    # - cron: "0 */6 * * *"  # Every 6 hours
    # - cron: "0 0 * * *"    # Daily
```

---

## Troubleshooting

### Issue: "GITHUB_TOKEN not found"
**Solution:** Set GITHUB_TOKEN environment variable
```bash
export GITHUB_TOKEN=ghp_xxxxx
python scripts/ci/phase_8_3_benchmark_collector.py
```

### Issue: "No workflows found"
**Solution:** Check repository and time window
```bash
python scripts/ci/phase_8_3_benchmark_collector.py \
  --owner your-owner \
  --repo your-repo \
  --hours 168
```

### Issue: "SLA violations detected"
**Solution:** Review `.codex/PHASE_8_3_SLA_THRESHOLDS.json` and baseline metrics
- Check if thresholds are realistic
- Verify metric collection is working
- Review actual performance metrics

### Issue: Workflow not triggering
**Solution:** Verify workflow file location and syntax
```bash
# Validate YAML
python -m yaml .github/workflows/phase-8-3-perf-monitor.yml

# Check file permissions
ls -l .github/workflows/phase-8-3-perf-monitor.yml
```

---

## Monitoring & Alerts

### Alert Channels

| Severity | Channels | Recipients |
|----------|----------|------------|
| INFO | Logs | Monitoring system |
| WARNING | Slack | performance-team |
| CRITICAL | Slack + Email | mbaetiong |
| SEVERE | Slack + SMS + GitHub Issue | mbaetiong |

### Configuring Slack Notifications

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add to GitHub Secrets: `SLACK_WEBHOOK_URL`
3. Workflow automatically sends alerts on violations

### Creating GitHub Issues for Regressions

Issues are auto-created for:
- CRITICAL violations (>20% regression)
- Persistent violations (>2 consecutive hours)
- SLA breaches requiring investigation

---

## Performance Optimization

### Quick Wins (2-4 hours effort)

1. **Cache Warming** (+10-15% improvement)
   ```bash
   # Pre-populate Docker layer cache
   docker pull base-image:latest
   docker build --cache-from base-image --tag codex:latest .
   ```

2. **Parallel Jobs** (+20-30% improvement)
   - Identify independent jobs
   - Run in parallel in workflow
   - Update `.github/workflows/*.yml`

3. **Dependency Pruning** (+5-10% improvement)
   ```bash
   pip check
   poetry optimize
   ```

### Medium-Term Improvements (1-2 weeks)

1. Multi-stage Docker builds
2. Build artifact compression
3. Test parallelization
4. Layer caching optimization

---

## Roadmap

### Phase 8.3 Complete (2026-06-22)
- [x] Baseline established
- [x] SLA thresholds configured
- [x] Monitoring deployed
- [x] Reports automated

### Phase 8.4 (2026-07-01)
- [ ] Optimization recommendations
- [ ] Performance dashboard enhancements
- [ ] Historical trend analysis

### Phase 8.5 (2026-07-15)
- [ ] Predictive performance modeling
- [ ] Anomaly detection improvements
- [ ] Cost optimization analysis

---

## Support & Questions

- **Baseline Issues:** See `.codex/PHASE_8_3_PERFORMANCE_BASELINE.md`
- **SLA Questions:** See `.codex/PHASE_8_3_SLA_THRESHOLDS.json`
- **Script Errors:** Run with `--help` for usage
- **Escalations:** Contact @mbaetiong

---

## References

- Baseline: `.codex/PHASE_8_3_PERFORMANCE_BASELINE.md`
- Reports: `.codex/reports/PHASE_8_3_WEEKLY_*.md`
- Dashboard: `.codex/PHASE_8_3_PERFORMANCE_DASHBOARD.md`
- Progress: `.codex/PHASE_8_3_PROGRESS.md`

---

**Last Updated:** 2026-06-22  
**Maintainer:** Performance Team  
**Authority:** @mbaetiong (D-tier)
