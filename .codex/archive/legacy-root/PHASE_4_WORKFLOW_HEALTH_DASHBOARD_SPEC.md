# Phase 4: Workflow Health Dashboard Specification

**Date**: 2026-07-13  
**Version**: 1.0  
**Status**: Ready for Phase 5 Implementation  
**Estimated Implementation Time**: 40 hours

---

## Executive Summary

Complete specification for a comprehensive workflow health dashboard that monitors all 235 workflows and provides real-time insights into CodeQL reliability, performance trends, and operational health.

**Dashboard Purpose**:
- Real-time visibility into workflow health
- Early detection of issues
- Performance optimization insights
- CodeQL reliability tracking (target: 99%+)
- Automated alerting for critical failures

---

## 1. Dashboard Architecture

### Data Sources

```
GitHub Actions API
  ├─ /repos/{owner}/{repo}/actions/runs
  ├─ /repos/{owner}/{repo}/actions/workflows
  ├─ /repos/{owner}/{repo}/commits
  └─ /repos/{owner}/{repo}/code-scanning/alerts

Workflow Logs (via gh CLI)
  ├─ Job logs
  ├─ Step duration data
  └─ Error/warning messages

Repository Data
  ├─ Branch information
  ├─ Protection rules
  ├─ Required checks
  └─ CodeQL configuration
```

### Data Collection Strategy

**Collection Frequency**:
```yaml
Real-time metrics:
  - Active workflow count: Every 30 seconds
  - Recent job status: Every 1 minute
  - Alert triggers: Real-time on GitHub webhook

Historical metrics:
  - Success rates: Every 5 minutes
  - Runtime trends: Every 15 minutes
  - Failure patterns: Every 1 hour
  - CodeQL alerts: Every 5 minutes

Daily aggregation:
  - Summary statistics: 2 AM UTC daily
  - Trend analysis: 2 AM UTC daily
  - Report generation: 3 AM UTC daily
```

**Data Retention**:
```
Real-time: Last 24 hours
Historical: Last 30 days in database
Archived: S3 cold storage beyond 30 days
CodeQL alerts: 90 days (compliance requirement)
```

---

## 2. Dashboard Sections

### 2.1 Top-Level Health Summary

**Location**: Dashboard homepage, above the fold

**Metrics Displayed**:

```
┌─────────────────────────────────────────────────────────────┐
│  WORKFLOW HEALTH OVERVIEW                          [Last 24H] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Overall Health:          ████████░░  97.3% GOOD           │
│                                                               │
│  Total Runs (24h):  2,847  │  Success:  2,764   │  97.1%  │
│  Failed Runs:       83     │  Failure:  83      │  2.9%   │
│  Cancelled:         0      │  Skipped:  0       │  0%     │
│                                                               │
│  ⚠️ Issues Detected: 3 (View Details)                        │
│     • High-frequency job timeouts (5 workflows)            │
│     • Increased failure rate in test workflows (+2%)       │
│     • 1 workflow consistently exceeding timeout             │
│                                                               │
│  CodeQL Status:  ✅ EXCELLENT                                │
│     • Success Rate: 99.8%  (Target: ≥99%)                 │
│     • Avg Runtime: 42 min  (Target: <60 min)             │
│     • SARIF Uploads: 100%  (Last 24h: 24/24)             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Status Indicators**:
```
EXCELLENT   ≥98% success, CodeQL ok, no alerts
GOOD        ≥95% success, minor alerts
WARNING     ≥90% success, multiple alerts
CRITICAL    <90% success, immediate action needed
```

---

### 2.2 CodeQL-Specific KPIs Section

**Location**: Top-right panel, always visible

**Metrics Displayed**:

```
┌────────────────────────────────┐
│  CodeQL HEALTH                 │
├────────────────────────────────┤
│                                │
│  Success Rate:  99.8%  ✅      │
│  (24h: 24/24 runs completed)  │
│                                │
│  Avg Runtime:  42 min          │
│  P95 Runtime:  48 min          │
│  P99 Runtime:  52 min          │
│  Max timeout:  60 min ✅       │
│                                │
│  SARIF Upload Success:  100%   │
│  (24h: 24/24 uploads successful)
│                                │
│  Alerts Generated:  12         │
│  New Alerts (24h):  2          │
│  Fixed Alerts:      1          │
│                                │
│  Last Successful Run:          │
│  2026-07-13 14:32:15 UTC ✓    │
│                                │
│  Next Scheduled Run:           │
│  2026-07-18 03:00:00 UTC      │
│  (Thursday 3 AM UTC)           │
│                                │
└────────────────────────────────┘
```

**Alert Rules for CodeQL**:
```
CRITICAL: success_rate < 95%
  Action: Page on-call immediately
  Alert: Send Slack/PagerDuty

MAJOR: success_rate < 99%
  Action: Create high-priority issue
  Alert: Daily digest

MINOR: success_rate < 99.9%
  Action: Log trend, track pattern
  Alert: Weekly summary

TIMEOUT: runtime > 55 min
  Action: Alert ops team
  Alert: Immediate Slack notification
```

---

### 2.3 Workflow Performance Heatmap

**Location**: Center of dashboard

**Display**:
```
Workflow Name              Success  Fails  Avg Time  Status    Trend
─────────────────────────────────────────────────────────────────────
ci-tests.yml               98.1%    2.9%   32.5 min  GOOD      ↓ (slower)
lint-check.yml             99.2%    0.8%    8.2 min  EXCELLENT ↑
codeql-analysis.yml        99.8%    0.2%   42.1 min  EXCELLENT ↑
security-scan.yml          97.3%    2.7%   15.3 min  GOOD      →
build-docker.yml           96.1%    3.9%   22.5 min  WARNING   ↓
type-check.yml             99.5%    0.5%   12.1 min  EXCELLENT ↑
integration-tests.yml      95.2%    4.8%   28.3 min  WARNING   ↓ (alert!)
... (232 more workflows)
```

**Features**:
- Click to drill down on individual workflow
- Sort by: name, success rate, avg time, status
- Filter by: status, trend, workflow type
- Color coding: Green (good) → Red (critical)

---

### 2.4 Failure Analysis Dashboard

**Location**: Left sidebar tab

**Display**:

```
┌─────────────────────────────────────────────┐
│  FAILURE ANALYSIS (Last 24 Hours)           │
├─────────────────────────────────────────────┤
│                                             │
│  Total Failures: 83 (2.9% of 2,847 runs)  │
│                                             │
│  Top Failure Categories:                  │
│  ┌─────────────────────────────────────┐  │
│  │ 1. Timeout errors         (24/83)    │  │
│  │    Workflows: build-docker,         │  │
│  │               integration-tests     │  │
│  │    Avg failure time: 58.9 min       │  │
│  │                                     │  │
│  │ 2. Resource exhaustion     (18/83)   │  │
│  │    Workflows: ci-tests, perf-bench  │  │
│  │    Peak concurrent jobs: 18/20      │  │
│  │                                     │  │
│  │ 3. API rate limits         (15/83)   │  │
│  │    Workflows: gh-cli based          │  │
│  │    Retry strategy working            │  │
│  │                                     │  │
│  │ 4. Network transients      (12/83)   │  │
│  │    Workflows: deploy-prod, release  │  │
│  │    Expected & handled correctly     │  │
│  │                                     │  │
│  │ 5. Other/Unknown           (14/83)   │  │
│  │    Workflows: misc tasks            │  │
│  │    Requires investigation           │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  Root Cause Breakdown:                    │
│  • Environmental: 45% (timeouts, network) │
│  • Code issues: 32% (test failures, etc)  │
│  • Config issues: 15% (permissions, etc)  │
│  • Unknown: 8% (requires manual review)   │
│                                             │
└─────────────────────────────────────────────┘
```

---

### 2.5 Runtime Trend Analysis

**Location**: Lower left panel

**Chart Type**: Line chart with 7-day history

```
Workflow Runtime Trends (Last 7 Days)
────────────────────────────────────────────

Avg Runtime (min)
│
60 ├─  
   │   ╱╲        ╱╲      
55 ├─ ╱  ╲  ╱╲  ╱  ╲  ╱╲
   │╱    ╲╱  ╲╱    ╲╱  ╲
50 ├─              
   │                     
45 ├─                
   │                     
40 ├─                
   │                     
35 ├─                
   └────────────────────────────────────────────
     Mon Tue Wed Thu Fri Sat Sun

Key Observations:
  ✓ Consistent 42-min CodeQL average (stable)
  ⚠ Build-docker trending UP (20→24 min)
  ⚠ Integration tests trending UP (25→29 min)
  → Other workflows stable

Recommendation:
  Investigate build-docker and integration-tests
  for efficiency improvements
```

---

### 2.6 Concurrency & Queuing Metrics

**Location**: Lower right panel

**Display**:

```
┌───────────────────────────────────────┐
│  CONCURRENCY & QUEUING ANALYSIS       │
├───────────────────────────────────────┤
│                                       │
│  Concurrent Jobs:                    │
│  ┌─────────────────────────────────┐ │
│  │ ████████░░░░░░░░ 12/20 (60%)   │ │
│  │ Peak: 18/20 (90%) Fri 14:30 UTC│ │
│  │ Average: 8/20 (40%)             │ │
│  │ Minimum: 2/20 (10%)             │ │
│  └─────────────────────────────────┘ │
│                                       │
│  Queue Depth (Pending Runs):         │
│  ┌─────────────────────────────────┐ │
│  │ ░░░░░░░░░░ 0 (no backlog) ✓    │ │
│  │ Max queue: 3 runs (Wed evening) │ │
│  │ Avg queue: 0 runs               │ │
│  │ Queue time: <2 min avg          │ │
│  └─────────────────────────────────┘ │
│                                       │
│  Concurrency Group Status:           │
│  ✅ 235/235 workflows have groups    │
│  ✅ 0 collisions detected            │
│  ✅ CodeQL isolated                  │
│  ✅ No deadlocks detected            │
│                                       │
└───────────────────────────────────────┘
```

---

### 2.7 Alert History & Notifications

**Location**: Right sidebar, scrollable panel

**Display**:

```
┌──────────────────────────────────────────┐
│  RECENT ALERTS                           │
├──────────────────────────────────────────┤
│                                          │
│  🔴 CRITICAL [Just now]                │
│  CodeQL runtime approaching limit      │
│  Last run: 52 min (target: <60)        │
│  Workflow: codeql-analysis.yml         │
│  Action: Monitor next run               │
│                                          │
│  🟡 WARNING [5 min ago]                │
│  build-docker timeout detected         │
│  Failures: 3 in last 2 hours           │
│  Workflow: build-docker.yml            │
│  Action: Review & fix                   │
│                                          │
│  ✅ RESOLVED [1 hour ago]              │
│  integration-tests queue cleared       │
│  Peak queue: 5 runs                     │
│  Now: Normal operation                  │
│                                          │
│  ℹ️ INFO [3 hours ago]                 │
│  CodeQL security alerts generated      │
│  New findings: 2                        │
│  Total known: 12 (0 fixed)             │
│  Links: Security tab                    │
│                                          │
│  ✅ OK [1 day ago]                     │
│  All workflows passing                 │
│  Success rate: 99.2%                   │
│  No issues detected                    │
│                                          │
└──────────────────────────────────────────┘
```

---

## 3. Drill-Down Capabilities

### Workflow Detail Page

**URL**: `/dashboard/workflows/{workflow-name}`

**Contents**:

```
┌─────────────────────────────────────────────────────────────┐
│ CI TESTS WORKFLOW DETAILS               [Last 7 Days]       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Configuration:                                             │
│  ├─ Trigger: pull_request                                  │
│  ├─ Timeout: 30 minutes                                    │
│  ├─ Concurrency: ci-tests-${{ github.head_ref || ...    │
│  └─ Status: ACTIVE ✅                                      │
│                                                              │
│  24-Hour Metrics:                                          │
│  ├─ Total runs: 87                                         │
│  ├─ Success: 85 (97.7%)                                   │
│  ├─ Failures: 2 (2.3%)                                    │
│  ├─ Avg runtime: 32.5 min                                 │
│  └─ P95 runtime: 35.2 min                                 │
│                                                              │
│  7-Day Trend:                                              │
│  [Line chart showing: 95% → 98% → 97% → 96% → 98% → ...] │
│                                                              │
│  Recent Failures:                                          │
│  ├─ 2026-07-13 12:30 - Database connection timeout       │
│  │  Duration: 30 min (hit timeout)                        │
│  │  Error: "Timeout waiting for fixture"                 │
│  │  Job ID: 123456789                                    │
│  │                                                         │
│  └─ 2026-07-13 08:15 - Memory exhaustion                  │
│     Duration: 28 min                                      │
│     Error: "Python process killed by OOM"                │
│     Job ID: 123456788                                    │
│                                                              │
│  Related Workflows:                                        │
│  ├─ Triggered by: PR created/updated                     │
│  ├─ Depends on: (none)                                    │
│  ├─ Triggers: auto-approve-tests-pass.yml               │
│  └─ Blocks PR merge: YES (required check)                │
│                                                              │
│  Performance History:                                     │
│  [Detailed chart with confidence intervals]               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Job-Level Analysis

**URL**: `/dashboard/workflows/{workflow-name}/jobs`

**Contents**: Breakdown of all jobs within workflow

```
Job Name                   Status    Time    % Total  Trend
────────────────────────────────────────────────────────────
1. Setup                   ✅ PASS   1.2 m    3.7%   ↑
2. Install dependencies    ✅ PASS   4.5 m   13.8%   ↓
3. Unit tests              ✅ PASS  18.2 m   56.0%   →
4. Integration tests       ✅ PASS   6.8 m   21.0%   ↑
5. Report coverage         ✅ PASS   1.8 m    5.5%   →
```

---

## 4. Automated Alerting Rules

### Alert Configuration

```yaml
alerts:
  # CodeQL Alerts
  codeql_success_rate_critical:
    condition: codeql.success_rate < 95%
    severity: CRITICAL
    action: [page_oncall, slack_critical, create_issue]
    throttle: No throttling (immediate)
    
  codeql_success_rate_major:
    condition: codeql.success_rate < 99%
    severity: MAJOR
    action: [create_issue, slack_warning]
    throttle: Once per hour
    
  codeql_runtime_warning:
    condition: codeql.avg_runtime > 50_min
    severity: MAJOR
    action: [slack_warning, create_issue]
    throttle: Once per day
    
  codeql_timeout_incident:
    condition: codeql.timeout_count > 0
    severity: CRITICAL
    action: [page_oncall, slack_critical]
    throttle: No throttling
    
  # Workflow Performance Alerts
  workflow_failure_spike:
    condition: workflow.failures > (avg_failures * 2)
    severity: WARNING
    action: [slack_alert, create_issue]
    throttle: Once per hour
    
  workflow_timeout_rate:
    condition: workflow.timeout_rate > 5%
    severity: MAJOR
    action: [slack_warning, create_issue]
    throttle: Once per day
    
  # Resource Alerts
  concurrent_job_limit_reached:
    condition: concurrent_jobs >= 18  # Out of 20
    severity: WARNING
    action: [slack_alert]
    throttle: Once per hour
    
  queue_depth_critical:
    condition: pending_runs > 10
    severity: MAJOR
    action: [slack_warning, create_issue]
    throttle: Once per hour
```

---

## 5. Data Visualization Specifications

### Chart Types

**1. Success Rate Trend (Line Chart)**
```
- X-axis: Time (hourly)
- Y-axis: Success percentage (0-100%)
- Color: Green (>99%), Yellow (>95%), Red (<95%)
- Smoothing: 2-hour moving average
- Period: Selectable (24h, 7d, 30d)
```

**2. Runtime Distribution (Histogram)**
```
- X-axis: Runtime (minutes)
- Y-axis: Frequency (number of runs)
- Bins: 1-minute intervals
- Color: Blue (typical), Orange (>average), Red (>timeout)
- Include: Mean, median, P95, P99
```

**3. Failure Categories (Pie Chart)**
```
- Categories: Timeout, Resource, Network, Code, Config, Other
- Color: Distinct color per category
- Show: Count and percentage
- Clickable: Drill to filtered logs
```

**4. Concurrent Jobs Timeline (Area Chart)**
```
- X-axis: Time (hourly)
- Y-axis: Concurrent jobs (0-20)
- Color: Green (<10), Yellow (10-15), Red (>15)
- Show: Actual + max limit line
- Period: Last 7 days
```

---

## 6. Dashboard Data Model

### Database Schema

```sql
-- Workflow metrics
CREATE TABLE workflow_runs (
    run_id INTEGER PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    run_number INTEGER,
    status VARCHAR(20),  -- success, failure, cancelled
    conclusion VARCHAR(20),
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_minutes DECIMAL,
    branch TEXT,
    trigger_event VARCHAR(50),
    trigger_actor TEXT,
    pr_number INTEGER,
    commit_sha TEXT
);

-- Job metrics
CREATE TABLE job_runs (
    job_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    job_name TEXT NOT NULL,
    status VARCHAR(20),
    conclusion VARCHAR(20),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_minutes DECIMAL,
    FOREIGN KEY (run_id) REFERENCES workflow_runs(run_id)
);

-- Step metrics
CREATE TABLE step_runs (
    step_id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    status VARCHAR(20),
    conclusion VARCHAR(20),
    duration_seconds INTEGER,
    FOREIGN KEY (job_id) REFERENCES job_runs(job_id)
);

-- CodeQL specific
CREATE TABLE codeql_runs (
    codeql_run_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    languages JSON,
    alerts_found INTEGER,
    new_alerts INTEGER,
    fixed_alerts INTEGER,
    sarif_upload_status VARCHAR(20),
    upload_timestamp TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES workflow_runs(run_id)
);

-- Alerts
CREATE TABLE dashboard_alerts (
    alert_id INTEGER PRIMARY KEY,
    alert_type VARCHAR(100),
    severity VARCHAR(20),
    message TEXT,
    created_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSON
);

-- Indexes for performance
CREATE INDEX idx_runs_workflow_created ON workflow_runs(workflow_name, created_at DESC);
CREATE INDEX idx_runs_status ON workflow_runs(status);
CREATE INDEX idx_codeql_runs ON codeql_runs(codeql_run_id);
```

---

## 7. Implementation Requirements

### Backend Requirements

```
Framework: Python Flask or FastAPI
Database: PostgreSQL or SQLite
API: REST API for dashboard frontend
Authentication: GitHub OAuth
Caching: Redis for real-time metrics
Job Scheduler: APScheduler for data collection
Monitoring: Prometheus metrics export
```

### Frontend Requirements

```
Framework: React or Vue.js
Charts: Chart.js or D3.js
State: Redux or Vuex
Real-time: WebSocket for live updates
Responsive: Mobile-friendly design
Accessibility: WCAG 2.1 AA compliance
```

### Integration Points

```
GitHub Actions API: For workflow/job/run data
GitHub REST API: For repository information
GitHub GraphQL API: For optimized queries
Slack: For alert notifications
PagerDuty: For on-call routing
CloudWatch: For monitoring
DataDog: Optional for advanced analytics
```

---

## 8. Success Metrics

### Dashboard KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page load time | <2 sec | APM monitoring |
| Chart render | <500ms | Frontend profiling |
| Data freshness | <5 min | Timestamp diff |
| Uptime | 99.9% | Availability monitoring |
| User engagement | >80% | Session tracking |

### CodeQL Dashboard Specific

| Metric | Target | Baseline |
|--------|--------|----------|
| CodeQL success rate display | Accurate to ±0.1% | 99.92% |
| Alert response time | <2 min | Automated |
| Dashboard update latency | <5 min | Real-time data |

---

## 9. Phase 5 Implementation Plan

**Timeline**: 2-3 weeks post-Phase 4

**Deliverables**:
1. Dashboard backend API (1 week)
2. Frontend UI implementation (1 week)
3. Integration with GitHub APIs (3 days)
4. Alert system setup (2 days)
5. Testing & validation (2 days)
6. Monitoring & documentation (2 days)

**Effort**: ~40 hours development

---

**Document Status**: SPECIFICATION COMPLETE - READY FOR PHASE 5  
**Prepared by**: Workflow Compliance Guardian v2.0.0  
**Next Phase**: PHASE_5_WORKFLOW_HEALTH_DASHBOARD_IMPLEMENTATION
