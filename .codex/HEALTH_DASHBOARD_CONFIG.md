# Health Dashboard Configuration

**Version**: 1.0  
**Created**: 2026-07-13T17:52:42Z  
**Updated**: 2026-07-13T17:52:42Z  
**Status**: ACTIVE

---

## Executive Summary

This document defines the operational configuration for the Workflow Health Dashboard, including collection schedules, alert thresholds, escalation procedures, and monitoring infrastructure.

---

## 1. Collection Schedule

### Primary Collection (Every 30 Minutes)

**Workflow**: `.github/workflows/workflow-health-update.yml`

```yaml
schedule:
  - cron: '0 */30 * * *'  # Every 30 minutes
```

**Execution Details**:
- **Trigger**: Scheduled job
- **Timeout**: 30 minutes
- **Concurrency**: Single (no parallel runs)
- **Permissions**: `contents: write`, `actions: read`

**Steps**:
1. Checkout repository
2. Set up Python 3.11
3. Collect workflow metrics (30-day window)
4. Generate dashboard JSON
5. Commit and push if changed

**Output File**: `.codex/WORKFLOW_HEALTH_DASHBOARD.json`

---

### Secondary Collection (Daily Summary)

**Trigger**: Daily at 2 AM UTC (cron: `0 2 * * *`)

**Purpose**: Historical trend analysis and archive updates

**Metrics Aggregated**:
- 30-day rolling averages
- Min/max tracking
- Trend classification
- Weekly summaries (Sundays)

---

### Manual Trigger

**Option**: `workflow_dispatch`

**Use Case**: On-demand health check or remediation verification

**Command**:
```bash
gh workflow run workflow-health-update.yml --ref main
```

---

## 2. Data Collection Configuration

### Workflow Metrics

**Source**: GitHub Actions API (`/repos/{owner}/{repo}/actions/workflows`)

**Collected Data**:
- Workflow name and ID
- Last 30 runs data
- Success/failure counts
- Average duration
- Trend classification

**Sample Query**:
```bash
gh api repos/{owner}/{repo}/actions/workflows \
  --paginate \
  --jq '.workflows[] | {id, name, state}'
```

---

### Execution Metrics

**Source**: Workflow run logs and job data

**Collected Data**:
- Total runs (24h, 7d, 30d)
- Success count and rate
- Failure count and patterns
- Cancelled and skipped counts
- Average duration (by workflow)

---

### Code Quality Metrics

**Source**: Multiple (Coverage.py, CodeQL, etc.)

**Collected Data**:
- Test pass rate
- Code coverage percentage (line, branch, function)
- CodeQL alerts (by severity)
- Security vulnerabilities
- Dependency vulnerabilities

---

### Deployment Metrics

**Source**: Deployment workflow logs

**Collected Data**:
- Total deployments
- Successful deployments
- Failed deployments
- Average deployment duration
- Rollback counts

---

### Performance Metrics

**Source**: Performance monitoring tools

**Collected Data**:
- P50 latency
- P95 latency
- P99 latency
- SLA compliance percentage
- Peak load metrics

---

## 3. Alert Thresholds

### Alert Trigger Rules

**All alerts are evaluated every 30 minutes** during metric collection.

#### M001: Workflow Success Rate

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 95.0% | — |
| Warning | 90.0% | ⚠️ Yellow alert |
| Critical | 85.0% | 🔴 Red alert, escalate |
| Change Detection | Drop >2pp | Immediate evaluation |

**Alert Message**:
```
⚠️ Workflow Success Rate has dropped to {value}% (target: 95%)
Last 24h: {count_failed}/{count_total} runs failed
Trend: {trend}
Recommendation: Review failed workflow logs and identify patterns
```

---

#### M002: Average Workflow Duration

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 25 min | — |
| Warning | 35 min | ⚠️ Yellow alert |
| Critical | 45 min | 🔴 Red alert, escalate |
| Change Detection | Increase >20% | Immediate evaluation |

---

#### M003: CodeQL Alert Volume

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 0 | — |
| Warning | 5 | ⚠️ Yellow alert |
| Critical | 10 | 🔴 Red alert, escalate |
| Critical Condition | Any CRITICAL severity | 🔴 Red alert, immediate escalation |

**Alert Message** (Critical CRITICAL alert):
```
🚨 CRITICAL SECURITY ALERT: CodeQL has detected {count} critical-severity vulnerabilities
Affected workflows: {workflow_list}
Recommendation: Review findings immediately at GitHub code scanning dashboard
Escalation: Notify security team
```

---

#### M004: Test Pass Rate

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 99.0% | — |
| Warning | 97.5% | ⚠️ Yellow alert |
| Critical | 95.0% | 🔴 Red alert, escalate |
| Change Detection | Drop >1pp | Immediate evaluation |

---

#### M005: Code Coverage

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 85.0% | — |
| Warning | 80.0% | ⚠️ Yellow alert |
| Critical | 75.0% | 🔴 Red alert, escalate |
| Change Detection | Drop >2pp | Immediate evaluation |

---

#### M006: Security Vulnerabilities

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 0 | — |
| Warning | 1 or any MEDIUM+ | ⚠️ Yellow alert |
| Critical | 3 or any HIGH+CRITICAL | 🔴 Red alert, escalate |

---

#### M007: Deployment Success Rate

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 100.0% | — |
| Warning | 95.0% | ⚠️ Yellow alert |
| Critical | 90.0% | 🔴 Red alert, escalate |

---

#### M008: CI Failure Rate

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 5.0% | — |
| Warning | 10.0% | ⚠️ Yellow alert |
| Critical | 15.0% | 🔴 Red alert, escalate |
| Change Detection | Increase >50% | Immediate evaluation |

---

#### M009: Performance P99 Latency

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 500 ms | — |
| Warning | 600 ms | ⚠️ Yellow alert |
| Critical | 800 ms | 🔴 Red alert, escalate |
| SLA Condition | Compliance <95% | ⚠️ Yellow alert |

---

#### M010: Cost Per Workflow

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | $2.50 | — |
| Warning | $3.50 | ⚠️ Yellow alert |
| Critical | $5.00 | 🔴 Red alert, escalate |
| Change Detection | Increase >20% | Immediate evaluation |

---

#### M011: Autonomous Agent Success Rate

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 90.0% | — |
| Warning | 80.0% | ⚠️ Yellow alert |
| Critical | 70.0% | 🔴 Red alert, escalate |
| Change Detection | Drop >10pp | Immediate evaluation |

---

#### M012: Documentation Freshness

| Threshold | Value | Action |
|-----------|-------|--------|
| Target | 95.0% | — |
| Warning | 85.0% | ⚠️ Yellow alert |
| Critical | 75.0% | 🔴 Red alert, escalate |
| Change Detection | Drop >5pp | Immediate evaluation |

---

## 4. Alert Escalation Procedures

### Level 1: Warning Alert (⚠️ Yellow)

**Threshold**: One or more metrics at warning level

**Trigger Condition**:
- Metric value between warning and critical threshold
- OR metric changes by >X% from baseline

**Actions**:
1. ✅ Alert logged in `.codex/WORKFLOW_HEALTH_DASHBOARD.json`
2. ✅ Comment added to relevant GitHub issues (if exists)
3. ✅ Visual indicator updated in dashboard
4. ⏳ Human review within 1 business day

**Response SLA**: 24 hours

---

### Level 2: Critical Alert (🔴 Red)

**Threshold**: One or more metrics at critical level OR critical security finding

**Trigger Condition**:
- Metric value exceeds critical threshold
- OR critical security vulnerability detected
- OR deployment success <90%

**Immediate Actions**:
1. ✅ Alert escalated to `.codex/WORKFLOW_HEALTH_DASHBOARD.json`
2. ✅ GitHub Issue created with URGENT label
3. ✅ Notification posted to `.codex` tracking
4. ✅ Assessment initiated

**Response SLA**: 2 hours

**Escalation Path**:
- L1: Health Dashboard monitoring system
- L2: On-call infrastructure team
- L3: Engineering leadership (for security alerts)

---

### Alert Notification Destinations

#### GitHub Issues

**Issue Template**:
```markdown
# [AUTO-ALERT] Health Dashboard: {metric_name} Critical

**Status**: 🔴 CRITICAL
**Metric**: {metric_name}
**Current Value**: {current_value} {unit}
**Threshold**: {threshold}
**Triggered**: {timestamp}

## Details
{alert_details}

## Recommended Actions
1. {action_1}
2. {action_2}
3. {action_3}

## Historical Context
- Previous 30-day average: {30_day_avg}
- Trend: {trend}
```

**Labels**: 
- `health-dashboard`
- `urgent` (for CRITICAL)
- `metric-{metric_id}`

---

#### Dashboard JSON Updates

All alerts stored in `.codex/WORKFLOW_HEALTH_DASHBOARD.json`:

```json
"alerts": {
  "active_alerts": [
    {
      "alert_id": "ALERT-2026-07-13-001",
      "metric_id": "M001",
      "severity": "CRITICAL",
      "message": "Workflow Success Rate has dropped to 87%",
      "triggered_at": "2026-07-13T17:30:00Z",
      "threshold_exceeded": 87.0,
      "threshold_limit": 85.0,
      "suggested_action": "Review workflow logs for common failure patterns"
    }
  ]
}
```

---

## 5. Monitoring & Validation

### Daily Validation Checks

**When**: 03:00 UTC (after daily summary collection)

**Checks**:
1. ✅ Dashboard JSON schema validation
2. ✅ Metric value range validation
3. ✅ Timestamp freshness check (within 2 hours)
4. ✅ Alert deduplication (no duplicate active alerts)
5. ✅ Historical data consistency

---

### Weekly Review

**When**: Monday 09:00 UTC

**Activities**:
1. Review all active alerts
2. Assess trend patterns
3. Validate threshold appropriateness
4. Generate weekly summary report

---

### Monthly Analysis

**When**: 1st of month at 10:00 UTC

**Activities**:
1. Comprehensive health assessment
2. Threshold adjustment (if needed)
3. Capacity planning analysis
4. Trend forecasting

---

## 6. Dashboard Integration Points

### 1. Health Dashboard JSON
- **Location**: `.codex/WORKFLOW_HEALTH_DASHBOARD.json`
- **Updated**: Every 30 minutes
- **Format**: JSON
- **Size Target**: <100 KB

### 2. Dashboard Markdown View
- **Location**: `.codex/WORKFLOW_HEALTH_DASHBOARD.md`
- **Updated**: After JSON generation
- **Purpose**: Human-readable summary
- **Audience**: Developers, operations teams

### 3. Archive Location
- **S3 Path**: `s3://codex-dashboards/health/{YYYY-MM-DD}/dashboard.json`
- **Retention**: 1 year
- **Frequency**: Daily snapshots

### 4. GitHub Pages (Future)
- **URL**: `https://aries-serpent.github.io/_codex_/health/`
- **Refresh**: Real-time via API
- **Features**: Interactive charts, historical trends

---

## 7. Configuration Parameters

### Collection Configuration

```yaml
# .codex/.dashboard-config.yaml
collection:
  interval_minutes: 30
  retention_days: 30
  archive_interval_days: 1
  batch_size: 50
  timeout_seconds: 1800
  
metrics:
  enabled: [M001, M002, M003, M004, M005, M006, M007, M008, M009, M010, M011, M012]
  exclude: []
  
alerts:
  enabled: true
  deduplication_window_minutes: 60
  max_active_alerts: 50
```

---

## 8. Health Score Calculation

**Formula**:
```
health_score = (
  (metrics_on_target / 12) × 75 +
  (1 - (warning_alerts / 12)) × 15 +
  (1 - (critical_alerts / 12)) × 10
)
```

**Score Ranges**:
- **90-100**: EXCELLENT (✅ Green)
- **80-89**: GOOD (🟢 Light Green)
- **70-79**: WARNING (🟡 Yellow)
- **60-69**: DEGRADED (🔶 Orange)
- **<60**: CRITICAL (🔴 Red)

---

## 9. Baseline Metrics (Phase 3 Baseline)

**Captured on**: 2026-07-13T16:54:22Z

| Metric | Baseline | Phase 3 Status |
|--------|----------|----------------|
| Workflow Success Rate | 95.0% | 97.2% ✅ |
| Avg Workflow Duration | 28.0 min | 23.4 min ✅ |
| CodeQL Alert Volume | 0 | 0 ✅ |
| Test Pass Rate | 99.0% | 99.8% ✅ |
| Code Coverage | 85.0% | 90.2% ✅ |
| Security Vulnerabilities | 0 | 0 ✅ |
| Deployment Success Rate | 100.0% | 100.0% ✅ |
| CI Failure Rate | 10.0% | 7.3% ✅ |
| Performance P99 Latency | 550 ms | 456.2 ms ✅ |
| Cost Per Workflow | $3.00 | $2.18 ✅ |
| Agent Success Rate | 85.0% | 94.3% ✅ |
| Documentation Freshness | 90.0% | 92.4% ✅ |

**Overall Health Score**: 96.8/100 (EXCELLENT)

---

## 10. Master Workflows Monitored

The dashboard tracks metrics for these **9 master workflows**:

1. ✅ **unified-testing.yml** — Test execution consolidator
2. ✅ **unified-security-scanning.yml** — Security analyzer
3. ✅ **unified-deployment.yml** — Deployment orchestrator
4. ✅ **unified-coverage.yml** — Coverage collector
5. ✅ **ci-health-monitor.yml** — CI health tracker
6. ✅ **agent-orchestration-unified.yml** — Agent coordinator
7. ✅ **documentation-quality.yml** — Doc validator
8. ✅ **performance-monitoring.yml** — Performance tracker
9. ✅ **artifact-monitoring.yml** — Artifact health

---

## 11. Troubleshooting Guide

### Issue: Dashboard JSON not updating

**Check**:
1. Verify workflow trigger: `.github/workflows/workflow-health-update.yml`
2. Confirm schedule is active (check `.github/workflows/workflow-health-update.yml`)
3. Verify Python dependencies installed
4. Check for API rate limiting

**Fix**:
```bash
# Manual trigger
gh workflow run workflow-health-update.yml --ref main

# Check status
gh run list --workflow workflow-health-update.yml -L 5
```

---

### Issue: Alerts not triggering

**Check**:
1. Verify alert thresholds in `.codex/HEALTH_DASHBOARD_CONFIG.md`
2. Confirm metric is being collected
3. Check JSON format validity

**Validation**:
```bash
# Validate JSON
python3 -m json.tool .codex/WORKFLOW_HEALTH_DASHBOARD.json > /dev/null && echo "✅ Valid"

# Check recent metrics
grep -A2 "current_value" .codex/WORKFLOW_HEALTH_DASHBOARD.json
```

---

## 12. Future Enhancements

- [ ] Real-time alerting via Slack/Discord
- [ ] Interactive web dashboard with charts
- [ ] Machine learning-based anomaly detection
- [ ] Predictive alerting (predict failures before they occur)
- [ ] Custom metric creation UI
- [ ] Alert suppression during maintenance windows
- [ ] Integration with incident management systems

---

## References

- **Schema**: `.codex/HEALTH_DASHBOARD_SCHEMA.md`
- **Dashboard Data**: `.codex/WORKFLOW_HEALTH_DASHBOARD.json`
- **Collector Script**: `scripts/ci/workflow_health_collector.py`
- **Workflow**: `.github/workflows/workflow-health-update.yml`
- **Phase 3 Report**: `CHANGELOG.md` (Success Metrics section)

---

**Configuration Version**: 1.0  
**Last Updated**: 2026-07-13T17:52:42Z  
**Next Review**: 2026-08-13 (monthly)  
**Maintained By**: Infrastructure & Operations Team
