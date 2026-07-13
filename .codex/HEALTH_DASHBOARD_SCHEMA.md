# Health Dashboard Schema Documentation

**Version**: 1.0  
**Created**: 2026-07-13T17:52:42Z  
**Status**: Active  
**Last Updated**: 2026-07-13T17:52:42Z

---

## Executive Summary

This document defines the complete schema for the Workflow Health Dashboard (`WORKFLOW_HEALTH_DASHBOARD.json`), which tracks the health of all 235 active GitHub Actions workflows across the _codex_ repository.

The dashboard collects and aggregates metrics across 12 key performance indicators (KPIs) with real-time monitoring, historical trending, and automated alerting.

---

## 1. Root-Level Structure

```json
{
  "dashboard_metadata": { ... },
  "metrics": { ... },
  "alerts": { ... },
  "thresholds": { ... },
  "health_status": "string",
  "summary": { ... }
}
```

---

## 2. Dashboard Metadata

**Purpose**: Core dashboard configuration and operational state

```json
"dashboard_metadata": {
  "version": "string",              // Schema version (e.g., "1.0.0")
  "created_at": "ISO8601",          // Dashboard creation timestamp
  "last_updated": "ISO8601",        // Last metric collection timestamp
  "status": "string",               // ACTIVE | MAINTENANCE | ARCHIVED
  "retention_days": "integer",      // Data retention period (default: 30)
  "update_frequency_minutes": 30    // Collection interval (default: 30)
}
```

**Example**:
```json
"dashboard_metadata": {
  "version": "1.0.0",
  "created_at": "2026-07-13T16:54:22Z",
  "last_updated": "2026-07-13T16:54:22Z",
  "status": "ACTIVE",
  "retention_days": 30,
  "update_frequency_minutes": 30
}
```

**Validation Rules**:
- `version`: Must match semantic versioning (MAJOR.MINOR.PATCH)
- `status`: Must be one of: ACTIVE, MAINTENANCE, ARCHIVED
- `update_frequency_minutes`: Must be > 0
- `created_at` and `last_updated` must be ISO8601 formatted

---

## 3. Metrics Structure

**Purpose**: Collection of 12 key performance indicators (KPIs)

Each metric follows a consistent structure:

```json
"metrics": {
  "METRIC_KEY": {
    "metric_id": "string",                      // Unique ID (M001, M002, etc.)
    "display_name": "string",                   // Human-readable name
    "description": "string",                    // Detailed description
    "unit": "string",                           // Unit of measurement
    "target": "number",                         // Target/goal value
    "alert_threshold_warning": "number",        // Yellow alert threshold
    "alert_threshold_critical": "number",       // Red alert threshold
    "current_value": "number",                  // Most recent measurement
    "trend": "string",                          // improving | stable | degrading
    "baseline": "number",                       // Baseline comparison value
    "30_day_avg": "number",                     // 30-day rolling average
    "30_day_min": "number",                     // 30-day minimum value
    "30_day_max": "number",                     // 30-day maximum value
    "last_updated": "ISO8601",                  // Last update timestamp
    "data_points": ["array"]                    // Historical data (optional)
  }
}
```

---

## 4. Metric Definitions (12 KPIs)

### M001: Workflow Success Rate
```json
{
  "metric_id": "M001",
  "display_name": "Workflow Success Rate",
  "description": "Percentage of workflows that complete successfully",
  "unit": "percent",
  "target": 95.0,
  "alert_threshold_warning": 90.0,
  "alert_threshold_critical": 85.0,
  "current_value": 97.2
}
```
**Calculation**: (Successful runs / Total runs) × 100  
**Frequency**: Every 5 minutes  
**Alert Trigger**: Drop of >2pp (percentage points)

---

### M002: Average Workflow Duration
```json
{
  "metric_id": "M002",
  "display_name": "Average Workflow Duration",
  "description": "Average time for workflows to complete (in minutes)",
  "unit": "minutes",
  "target": 25.0,
  "alert_threshold_warning": 35.0,
  "alert_threshold_critical": 45.0,
  "current_value": 23.4
}
```
**Calculation**: Sum(workflow durations) / Count(workflows)  
**Frequency**: Every 15 minutes  
**Alert Trigger**: Increase >20%

---

### M003: CodeQL Alert Volume
```json
{
  "metric_id": "M003",
  "display_name": "CodeQL Alert Volume",
  "description": "Active CodeQL security alerts by severity",
  "unit": "count",
  "target": 0,
  "alert_threshold_warning": 5,
  "alert_threshold_critical": 10,
  "current_value": 0,
  "breakdown": {
    "CRITICAL": 0,
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0
  }
}
```
**Source**: GitHub Code Scanning API  
**Frequency**: Every 5 minutes  
**Alert Trigger**: CRITICAL alerts detected

---

### M004: Test Pass Rate
```json
{
  "metric_id": "M004",
  "display_name": "Test Pass Rate",
  "description": "Percentage of tests that pass across the test suite",
  "unit": "percent",
  "target": 99.0,
  "alert_threshold_warning": 97.5,
  "alert_threshold_critical": 95.0,
  "current_value": 99.8
}
```
**Calculation**: (Passing tests / Total tests) × 100  
**Frequency**: Every 5 minutes  
**Alert Trigger**: Drop >1pp

---

### M005: Code Coverage
```json
{
  "metric_id": "M005",
  "display_name": "Code Coverage",
  "description": "Percentage of code covered by automated tests",
  "unit": "percent",
  "target": 85.0,
  "alert_threshold_warning": 80.0,
  "alert_threshold_critical": 75.0,
  "current_value": 90.2,
  "coverage_by_type": {
    "line": 90.2,
    "branch": 88.1,
    "function": 89.5
  }
}
```
**Source**: Coverage.py reports  
**Frequency**: After each test run  
**Alert Trigger**: Drop >2pp

---

### M006: Security Vulnerabilities
```json
{
  "metric_id": "M006",
  "display_name": "Security Vulnerabilities",
  "description": "Count of known security vulnerabilities in dependencies",
  "unit": "count",
  "target": 0,
  "alert_threshold_warning": 1,
  "alert_threshold_critical": 3,
  "current_value": 0,
  "breakdown": {
    "CRITICAL": 0,
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0
  }
}
```
**Source**: Dependabot, GitHub Advisory Database  
**Frequency**: Every 6 hours  
**Alert Trigger**: Any HIGH or CRITICAL vulnerability

---

### M007: Deployment Success Rate
```json
{
  "metric_id": "M007",
  "display_name": "Deployment Success Rate",
  "description": "Percentage of deployments that complete successfully",
  "unit": "percent",
  "target": 100.0,
  "alert_threshold_warning": 95.0,
  "alert_threshold_critical": 90.0,
  "current_value": 100.0
}
```
**Source**: Deployment workflows  
**Frequency**: After each deployment  
**Alert Trigger**: Drop below 95%

---

### M008: CI Failure Rate
```json
{
  "metric_id": "M008",
  "display_name": "CI Failure Rate",
  "description": "Percentage of CI runs that fail (lower is better)",
  "unit": "percent",
  "target": 5.0,
  "alert_threshold_warning": 10.0,
  "alert_threshold_critical": 15.0,
  "current_value": 7.3
}
```
**Calculation**: (Failed CI runs / Total CI runs) × 100  
**Frequency**: Every 5 minutes  
**Alert Trigger**: Increase >50%

---

### M009: Performance P99 Latency
```json
{
  "metric_id": "M009",
  "display_name": "Performance P99 Latency",
  "description": "99th percentile latency vs SLA (lower is better)",
  "unit": "milliseconds",
  "target": 500.0,
  "alert_threshold_warning": 600.0,
  "alert_threshold_critical": 800.0,
  "current_value": 456.2,
  "sla_target": 500.0,
  "sla_compliance": 98.5
}
```
**Source**: Performance monitoring tools  
**Frequency**: Every 15 minutes  
**Alert Trigger**: SLA compliance drop >5%

---

### M010: Cost Per Workflow
```json
{
  "metric_id": "M010",
  "display_name": "Cost Per Workflow",
  "description": "Average runner-hours cost per workflow execution",
  "unit": "USD",
  "target": 2.50,
  "alert_threshold_warning": 3.50,
  "alert_threshold_critical": 5.00,
  "current_value": 2.18
}
```
**Calculation**: Total runner costs / Total workflow runs  
**Frequency**: Daily  
**Alert Trigger**: Increase >20%

---

### M011: Autonomous Agent Success Rate
```json
{
  "metric_id": "M011",
  "display_name": "Autonomous Agent Success Rate",
  "description": "Percentage of autonomous agent tasks that succeed",
  "unit": "percent",
  "target": 90.0,
  "alert_threshold_warning": 80.0,
  "alert_threshold_critical": 70.0,
  "current_value": 94.3,
  "breakdown_by_agent": {}
}
```
**Source**: Copilot agent execution logs  
**Frequency**: Every 30 minutes  
**Alert Trigger**: Drop >10pp

---

### M012: Documentation Freshness
```json
{
  "metric_id": "M012",
  "display_name": "Documentation Freshness",
  "description": "Percentage of documentation up-to-date with code",
  "unit": "percent",
  "target": 95.0,
  "alert_threshold_warning": 85.0,
  "alert_threshold_critical": 75.0,
  "current_value": 92.4,
  "stale_docs_count": 8,
  "total_docs": 112
}
```
**Source**: Documentation freshness checker agent  
**Frequency**: Daily  
**Alert Trigger**: Drop >5pp

---

## 5. Alerts Structure

**Purpose**: Track active, warning, and resolved alerts

```json
"alerts": {
  "active_alerts": [
    {
      "alert_id": "string",              // Unique alert ID
      "metric_id": "string",             // Associated metric
      "severity": "string",              // WARNING | CRITICAL
      "message": "string",               // Alert message
      "triggered_at": "ISO8601",         // When alert triggered
      "threshold_exceeded": "number",    // Exceeded value
      "threshold_limit": "number",       // Alert threshold
      "suggested_action": "string"       // Recommended action
    }
  ],
  "warning_alerts": [],                  // Warning-level alerts
  "resolved_alerts": [],                 // Recently resolved alerts
  "alert_history": []                    // Historical alert log
}
```

---

## 6. Thresholds Structure

**Purpose**: Define visual and behavioral thresholds

```json
"thresholds": {
  "HEALTHY": {
    "description": "All metrics within target range",
    "icon": "✅",
    "color": "#28a745"
  },
  "CAUTION": {
    "description": "One or more metrics approaching warning threshold",
    "icon": "⚠️",
    "color": "#ffc107"
  },
  "WARNING": {
    "description": "One or more metrics exceeding warning threshold",
    "icon": "🔶",
    "color": "#ff6b3b"
  },
  "CRITICAL": {
    "description": "One or more metrics exceeding critical threshold",
    "icon": "❌",
    "color": "#dc3545"
  }
}
```

---

## 7. Health Status

**Purpose**: Overall dashboard health state

```json
"health_status": "HEALTHY"  // HEALTHY | CAUTION | WARNING | CRITICAL
```

**Determination Logic**:
```
if any metric is CRITICAL:
  health_status = "CRITICAL"
else if any metric is WARNING:
  health_status = "WARNING"
else if any metric is CAUTION:
  health_status = "CAUTION"
else:
  health_status = "HEALTHY"
```

---

## 8. Summary Structure

**Purpose**: High-level health overview

```json
"summary": {
  "metrics_on_target": 12,           // Count of metrics within target
  "metrics_off_target": 0,           // Count of metrics exceeding thresholds
  "critical_alerts": 0,              // Count of critical alerts
  "warning_alerts": 0,               // Count of warning alerts
  "health_score": 96.8               // Overall health score (0-100)
}
```

**Health Score Calculation**:
```
health_score = (
  (metrics_on_target / total_metrics) × 100 +
  (1 - (critical_alerts / max_alerts)) × 0 +  // Critical alerts have high weight
  (1 - (warning_alerts / max_alerts)) × 10
) / 2
```

---

## 9. Data Type Specifications

| Type | Format | Example |
|------|--------|---------|
| ISO8601 | `YYYY-MM-DDTHH:MM:SSZ` | `2026-07-13T17:52:42Z` |
| Percentage | Number 0-100 | `97.2` |
| Count | Non-negative integer | `5` |
| Duration | Minutes | `23.4` |
| Currency | USD with 2 decimals | `2.18` |
| Trend | `improving` \| `stable` \| `degrading` | `stable` |

---

## 10. Update Frequency & Retention

**Collection Schedule**:

| Component | Frequency | Retention |
|-----------|-----------|-----------|
| Real-time metrics | Every 30 minutes | 24 hours |
| Historical trends | Every 5 minutes (aggregated) | 30 days |
| Alert history | Real-time | 90 days |
| Archive | Daily | S3 cold storage |

---

## 11. Collection Infrastructure

**Data Collection Pipeline**:

```
GitHub Actions API
    ↓
Workflow Health Collector (scripts/ci/workflow_health_collector.py)
    ↓
Metric Aggregation Engine
    ↓
WORKFLOW_HEALTH_DASHBOARD.json
    ↓
Dashboard Generator + Alert Engine
    ↓
Notifications (GitHub Issues, Discussions)
```

**Collector Configuration**:
- Script: `.github/workflows/workflow-health-update.yml`
- Trigger: Every 30 minutes (cron: `0 */30 * * *`)
- Output: `.codex/WORKFLOW_HEALTH_DASHBOARD.json`
- Timeout: 30 minutes

---

## 12. Validation Rules

All JSON files must validate against these rules:

1. **Metadata Validation**:
   - `version` must match pattern: `^\d+\.\d+\.\d+$`
   - `status` must be one of: `ACTIVE`, `MAINTENANCE`, `ARCHIVED`
   - Timestamps must be valid ISO8601

2. **Metric Validation**:
   - `metric_id` must follow pattern: `M\d{3}`
   - `current_value` must be ≥ 0
   - `target` must be > 0
   - `alert_threshold_warning` must be > `alert_threshold_critical` for percentage metrics
   - `30_day_avg` must be between `30_day_min` and `30_day_max`

3. **Alert Validation**:
   - `severity` must be: `WARNING` or `CRITICAL`
   - `triggered_at` must be recent (within retention period)
   - `threshold_exceeded` must exceed `threshold_limit`

4. **Summary Validation**:
   - `metrics_on_target` + `metrics_off_target` = 12
   - `health_score` must be 0-100

---

## 13. Example: Complete Minimal Schema

```json
{
  "dashboard_metadata": {
    "version": "1.0.0",
    "created_at": "2026-07-13T16:54:22Z",
    "last_updated": "2026-07-13T16:54:22Z",
    "status": "ACTIVE",
    "retention_days": 30,
    "update_frequency_minutes": 30
  },
  "metrics": {
    "workflow_success_rate": {
      "metric_id": "M001",
      "display_name": "Workflow Success Rate",
      "description": "Percentage of workflows that complete successfully",
      "unit": "percent",
      "target": 95.0,
      "alert_threshold_warning": 90.0,
      "alert_threshold_critical": 85.0,
      "current_value": 97.2,
      "trend": "stable",
      "baseline": 95.0,
      "30_day_avg": 96.1,
      "30_day_min": 92.5,
      "30_day_max": 98.9,
      "last_updated": "2026-07-13T16:54:22Z",
      "data_points": []
    }
  },
  "alerts": {
    "active_alerts": [],
    "warning_alerts": [],
    "resolved_alerts": [],
    "alert_history": []
  },
  "thresholds": {
    "HEALTHY": {
      "description": "All metrics within target range",
      "icon": "✅",
      "color": "#28a745"
    }
  },
  "health_status": "HEALTHY",
  "summary": {
    "metrics_on_target": 12,
    "metrics_off_target": 0,
    "critical_alerts": 0,
    "warning_alerts": 0,
    "health_score": 96.8
  }
}
```

---

## 14. API Endpoints

**Future Enhancement**: Dashboard can be exposed via REST API:

```
GET /api/health/dashboard          # Full dashboard
GET /api/health/metrics            # All metrics
GET /api/health/metrics/:metric_id # Specific metric
GET /api/health/alerts             # Active alerts
GET /api/health/summary            # Summary only
POST /api/health/alerts            # Create alert (admin only)
```

---

## 15. Master Workflows Tracked

The dashboard monitors the following **9 master workflows**:

1. **unified-testing.yml** - Consolidated test execution
2. **unified-security-scanning.yml** - Security scanning
3. **unified-deployment.yml** - Deployment automation
4. **unified-coverage.yml** - Coverage collection
5. **ci-health-monitor.yml** - CI health tracking
6. **agent-orchestration-unified.yml** - Autonomous agent execution
7. **documentation-quality.yml** - Documentation checks
8. **performance-monitoring.yml** - Performance tracking
9. **artifact-monitoring.yml** - Artifact health

---

## References

- **Dashboard Data**: `.codex/WORKFLOW_HEALTH_DASHBOARD.json`
- **Dashboard Config**: `.codex/HEALTH_DASHBOARD_CONFIG.md`
- **Collector Script**: `scripts/ci/workflow_health_collector.py`
- **Workflow Trigger**: `.github/workflows/workflow-health-update.yml`
- **Alert Rules**: `.codex/HEALTH_DASHBOARD_CONFIG.md` (Alert Thresholds section)

---

**Schema Version**: 1.0  
**Last Updated**: 2026-07-13T17:52:42Z  
**Maintained By**: Health Dashboard Infrastructure Team
