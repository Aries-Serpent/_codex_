# 📊 Enterprise Governance Dashboard
## Phase 12.2 Deliverable #4

**Version:** 1.0.0-enterprise  
**Effective:** 2026-07-01  
**Audience:** Enterprise administrators, compliance officers, team leads  
**Update Frequency:** Real-time (1-second refresh)

---

## TABLE OF CONTENTS

1. [Dashboard Overview](#dashboard-overview)
2. [Key Metrics & KPIs](#key-metrics--kpis)
3. [Approval Workflow Analytics](#approval-workflow-analytics)
4. [Compliance Scorecard](#compliance-scorecard)
5. [Risk Assessment & Remediation](#risk-assessment--remediation)
6. [Audit Log Viewer](#audit-log-viewer)
7. [Deployment Procedures](#deployment-procedures)
8. [Runbook & Troubleshooting](#runbook--troubleshooting)
9. [API Reference](#api-reference)
10. [FAQ & Support](#faq--support)

---

## DASHBOARD OVERVIEW

### Purpose

The Enterprise Governance Dashboard provides **real-time visibility** into:
- Approval workflow status & performance
- Compliance violations & remediation
- Policy enforcement metrics
- Audit trail integrity
- Risk exposure & trends

### Key Features

- **Real-time Updates:** 1-second refresh cycle
- **Multi-Tenant:** Isolated views per tenant
- **RBAC-Protected:** Viewing permissions based on Track 12.1 roles
- **Search & Export:** Full-text search + CSV/JSON export
- **Alerting:** Real-time alerts for P0/P1 violations
- **Historical Analysis:** 30-day trending & analytics

### Access Levels

| Role | Permissions |
|------|------------|
| `system_admin` | Full dashboard access, all tenants, all metrics |
| `ci_operator` | Approval workflows, own tenant only |
| `security_reviewer` | Compliance violations, approval workflows |
| `agent_operator` | Basic metrics, own workflows only |
| `agent_reader` | Read-only summary dashboard |
| `guest` | No access |

---

## KEY METRICS & KPIs

### 1. Compliance Score

**Definition:** Percentage of policies passing compliance checks  
**Target:** 99%+ compliance rate  
**Update Frequency:** Every policy check (real-time)

```
Current Score: 98.7%
Trend: ↗ Improving (+2.3% week-over-week)
Target: 99.0%
Status: 🟡 AT RISK (below 99%)
```

**Breakdown by Severity:**
- P0 (Critical): 100% compliant (0 violations)
- P1 (High): 97.5% compliant (2 violations)
- P2 (Medium): 98.9% compliant (1 violation)
- P3 (Low): 99.2% compliant (0 violations)

### 2. Approval Workflow Performance

**Metrics:**
- **Average Approval Time:** 4.2 hours (target: <6 hours)
- **p99 Latency:** 87ms (target: <100ms)
- **SLA Compliance:** 99.1% (target: 100%)
- **Workflow Success Rate:** 98.9% (target: >99%)

**Bottleneck Analysis:**
```
Stage               Avg Time    Slowest Phase
─────────────────────────────────────────────
Code Review         2.1h        Awaiting 2nd approval
Owner Review        1.5h        @mbaetiong response
Merge Gate          0.6h        CI checks
─────────────────────────────────────────────
Total               4.2h
```

### 3. Violation Trends

**Weekly Summary:**
```
Mon:  3 violations (2 P1, 1 P2)
Tue:  1 violation  (1 P2)
Wed:  2 violations (1 P1, 1 P3)
Thu:  0 violations
Fri:  1 violation  (1 P0) ⚠️
Sat:  0 violations
Sun:  0 violations
─────────────────────────
Total: 7 violations (trend: stable)
```

### 4. Remediation Success Rate

**Metrics:**
- **Auto-Remediated:** 85% of P3/P2 violations
- **Manually Remediated:** 12% of P1/P0 violations
- **Escalated:** 3% remain unresolved
- **Average Time to Resolution:** 2.4 hours

### 5. Audit Trail Health

**Metrics:**
- **Audit Trail Completeness:** 100% (no gaps detected)
- **Event Logging Latency:** <100ms (p99)
- **Immutability Verified:** ✅ (cryptographic checksums valid)
- **Retention Compliance:** 7 years (compliant)

---

## APPROVAL WORKFLOW ANALYTICS

### Workflow Queue

```
Status              Count   Oldest   Newest    Avg Wait
──────────────────────────────────────────────────────
Pending Code Review   12   3.4h     0.2h      1.8h
Awaiting Owner       3     8.2h     2.1h      5.1h
Ready to Merge       7     1.2h     0.1h      0.6h
Completed Today      34    —        2m        —
────────────────────────────────────────────────────
Total Workflows      56
```

### SLA Compliance by Severity

| Severity | SLA Target | Current | Status |
|----------|-----------|---------|--------|
| P0 (Emergency) | 1h | 0.8h avg | ✅ PASS |
| P1 (High) | 24h | 18.3h avg | ✅ PASS |
| P2 (Medium) | 48h | 34.2h avg | ✅ PASS |
| P3 (Low) | 7d | 3.2d avg | ✅ PASS |

### Approval Decision Breakdown

```
Approved:  312 workflows (98.7%)
Rejected:    2 workflows (0.6%)
Escalated:   2 workflows (0.6%)
Auto-Approved: 28 workflows (8.8%)
─────────────────────────────
Total:     344 workflows
```

### Slowest Approvers

This data can be used to identify training needs or workload balancing:

```
Approver        Avg Approval Time   Count   Slowest PR
──────────────────────────────────────────────────────
mbaetiong      12.4h               23      18.2h (PR#542)
alice          2.1h                67      4.5h
bob            1.8h                54      3.2h
carol          1.6h                48      2.1h
```

---

## COMPLIANCE SCORECARD

### Policy Compliance Matrix

```
Policy Category        Status    Coverage   Trend
─────────────────────────────────────────────────
Access Control       ✅ 95%     8/8       ↗
Code Quality         ✅ 97%     6/6       ↗
Secret Management    ✅ 100%    5/5       ➡️
Change Control       ⚠️  92%    7/8       ↙️
Audit & Compliance   ✅ 100%    3/3       ↗
Enterprise Policies  ⚠️  95%    3/4       ↙️
────────────────────────────────────────
Overall Score        ✅ 98.7%   33/37     ↗
```

### Current Violations

```
Policy              Severity  Status          Remediation
─────────────────────────────────────────────────────────
CQ-001: Coverage    P1_HIGH   OPEN (12h)      Auto-available
AC-001: RBAC        P0_CRITICAL RESOLVED     Remediated 2h ago
SM-002: Rotation    P0_CRITICAL OPEN (4.2h)  ESCALATED
CC-007: Dependencies P1_HIGH   IN_PROGRESS    Auto-remediating
EN-001: SLA         P1_HIGH   RESOLVED       Fixed 6.5h ago
────────────────────────────────────────────────────────
Total: 2 OPEN, 3 RESOLVED (in last 24h)
```

### Compliance Metrics Over Time

```
Date      P0    P1    P2    P3    Overall
──────────────────────────────────────────
2026-06-30 0     1     2     1     98.4%
2026-07-01 0     2     1     0     98.7%
2026-07-02 1     2     1     1     98.3%  ⚠️
2026-07-03 0     2     0     1     98.9%
2026-07-04 0     1     0     0     99.1%  ✅
2026-07-05 0     1     1     0     98.8%
```

---

## RISK ASSESSMENT & REMEDIATION

### Risk Matrix

```
              High Impact    Medium Impact   Low Impact
High Prob     🔴 P0 (1)      🟡 P1 (3)       🟢 P2 (2)
Medium Prob   🟡 P1 (2)      🟢 P2 (1)       🟢 P3 (1)
Low Prob      🟢 P2 (1)      🟢 P3 (2)       🟢 Low
```

**Key Risks:**
1. **Data Breach Risk (P0):** Secret exposure (SM-002) — ESCALATED to @mbaetiong
2. **Code Quality Regression (P1):** Test coverage dropping — 12h to remediation deadline
3. **SLA Miss (P1):** Approval workflow latency spike — monitoring in progress

### Remediation Workflows

**Active Remediation:**
```
Workflow ID      Policy         Status         Progress   ETA
────────────────────────────────────────────────────────────
rem-2026-07-01   CQ-001         IN_PROGRESS    75%        1.3h
rem-2026-07-02   CC-007         IN_PROGRESS    50%        2.1h
rem-2026-06-30   SM-002         ESCALATED      —          Manual
```

**Remediation History (Last 7 Days):**
```
Total Initiated:     12
Successfully Resolved: 10 (83%)
Failed:              2 (17%)  ← Review needed
Average Time:        2.4 hours
```

---

## AUDIT LOG VIEWER

### Search Interface

```
[🔍 Search] _____________________________________ [Time Range ▼]

Filter:
  - Event Type: [All▼]
  - Severity: [All▼]
  - Actor: ____________
  - Resource: ____________
  - Status: [All▼]

[Apply Filters] [Clear] [Export CSV] [Export JSON]
```

### Sample Audit Events

```
Timestamp           Event Type           Actor      Resource    Status   Action
─────────────────────────────────────────────────────────────────────────────────
2026-07-05 14:23  APPROVAL_GRANTED     alice      PR#345      ✅      Code Review
2026-07-05 12:15  DELEGATION_CREATED   alice      bob         ✅      Vacation cover
2026-07-05 11:42  WORKFLOW_STARTED     system     PR#344      ✅      P1_HIGH
2026-07-05 10:31  ESCALATION_TRIGGERED system     PR#342      ⚠️      Timeout 4h
2026-07-05 09:18  APPROVAL_REJECTED    carol      PR#340      ❌      Rework needed
```

### Audit Trail Statistics

```
Events Logged (24h):   2,847
Events Logged (7d):    19,234
Events Logged (30d):   82,156
────────────────────────────
Log Storage Used:      128 MB
Retention Policy:      7 years
Immutability:          ✅ Verified
Gap Detection:         ✅ No gaps found
```

---

## DEPLOYMENT PROCEDURES

### Pre-Deployment Checklist

- [ ] All success criteria met (4/4)
- [ ] Performance benchmarks validated (<100ms p99)
- [ ] Security audit cleared
- [ ] RBAC integration verified
- [ ] Compliance tests pass (100% coverage)
- [ ] Documentation complete
- [ ] Team trained on dashboard features

### Deployment Steps

#### 1. Database Schema

```sql
-- Create compliance_scores table
CREATE TABLE IF NOT EXISTS compliance_scores (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP,
  total_policies INTEGER,
  passed_checks INTEGER,
  compliance_rate FLOAT,
  violations_by_severity JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_events table (append-only)
CREATE TABLE IF NOT EXISTS audit_events (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(32) UNIQUE,
  event_type VARCHAR(50),
  actor_id VARCHAR(255),
  workflow_id VARCHAR(255),
  stage_id VARCHAR(255),
  timestamp TIMESTAMP,
  resource JSONB,
  context JSONB,
  result JSONB,
  checksum VARCHAR(256),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indices
CREATE INDEX idx_audit_workflow_id ON audit_events(workflow_id);
CREATE INDEX idx_audit_timestamp ON audit_events(timestamp);
CREATE INDEX idx_compliance_timestamp ON compliance_scores(timestamp);
```

#### 2. Deploy Components

```bash
# 1. Copy governance framework
cp .codex/GOVERNANCE_POLICY_FRAMEWORK.md docs/

# 2. Install approval engine
cp scripts/governance/approval_engine.py src/codex/governance/

# 3. Install compliance monitor
cp scripts/governance/compliance_monitor.py src/codex/governance/

# 4. Create dashboard views
cp .codex/PHASE_12_2_COMPLIANCE_DASHBOARD.md docs/

# 5. Initialize database
python -m src.codex.governance.db_init

# 6. Verify RBAC integration
python -c "from src.codex.governance import rbac; rbac.verify_integration()"

# 7. Test compliance engine
pytest tests/governance/ -v --cov=src.codex.governance
```

#### 3. Health Checks

```bash
# Verify components are operational
python scripts/governance/health_check.py

# Expected output:
# ✅ Approval Engine: Running
# ✅ Compliance Monitor: Running
# ✅ Audit Logger: Running
# ✅ RBAC Integration: Connected
# ✅ Dashboard API: Responding
```

#### 4. Enable Dashboard

```bash
# Expose dashboard at /api/governance/dashboard
python -m src.codex.governance.dashboard_server --port=8765
```

### Rollback Procedure

If critical issues occur:

```bash
# 1. Disable dashboard
systemctl stop governance-dashboard

# 2. Revert database changes
./scripts/governance/rollback.sh --version=1.0.0-pre

# 3. Restart services
systemctl restart approval-engine
systemctl restart compliance-monitor

# 4. Verify recovery
python scripts/governance/health_check.py
```

---

## RUNBOOK & TROUBLESHOOTING

### Common Issues

#### Issue 1: Compliance Score Below 99%

**Symptoms:** Dashboard shows 98.x% compliance rate

**Diagnosis:**
```bash
# Check for active violations
curl http://localhost:8765/api/governance/violations?severity=P0

# Check remediation status
curl http://localhost:8765/api/governance/remediation-status
```

**Resolution:**
1. Identify P0/P1 violations (use Violations widget)
2. Check if auto-remediation is available
3. If yes, trigger auto-remediation: `curl -X POST .../remediate/{violation_id}`
4. If no, escalate to team lead for manual fix
5. Monitor compliance score; expect >99% within 4 hours

#### Issue 2: Approval Workflow Timeout

**Symptoms:** Workflow stuck in "Code Review" for >4 hours

**Diagnosis:**
```bash
# Check workflow status
curl http://localhost:8765/api/governance/workflows/{workflow_id}

# Check for escalation rules
grep "escalation:" .codex/GOVERNANCE_POLICY_FRAMEWORK.md
```

**Resolution:**
1. Verify approver is available (not on vacation)
2. If unavailable, check delegation options
3. For P0/P1, manually escalate: `curl -X POST .../workflows/{id}/escalate`
4. Send Slack reminder to @approver
5. If no response in 1h, escalate to @mbaetiong

#### Issue 3: Audit Trail Gap Detected

**Symptoms:** "⚠️ Audit trail gap detected at 2026-07-05 14:22:31"

**Diagnosis:**
```bash
# Check audit log continuity
python -m src.codex.governance.audit_verify

# Output example:
# Event ID 1234: ✅ Valid checksum
# Event ID 1235: ❌ MISSING (expected at 14:22:30)
# Event ID 1236: ✅ Valid checksum
```

**Resolution:**
1. This is critical (P0) — immediately notify @mbaetiong
2. Check system logs for service crashes/restarts
3. Verify database connectivity during gap window
4. Regenerate missing events from backup audit trail
5. Run full audit verification: `python scripts/governance/audit_verify --full`

#### Issue 4: Dashboard Performance Degradation

**Symptoms:** Dashboard queries take >5 seconds

**Diagnosis:**
```bash
# Check query performance
python scripts/governance/perf_check.py

# Check database indices
psql -c "SELECT * FROM pg_stat_user_indexes WHERE schemaname='public';"
```

**Resolution:**
1. Verify database indices are in place
2. Run vacuum: `VACUUM ANALYZE compliance_scores;`
3. Check slow query log: `tail -100 /var/log/postgresql/slow.log`
4. If specific query is slow, optimize or add index
5. Restart dashboard service: `systemctl restart governance-dashboard`

---

## API REFERENCE

### Compliance Endpoints

```
GET /api/governance/compliance/score
  → Returns current compliance score (JSON)

GET /api/governance/compliance/violations?severity=P0
  → Returns violations filtered by severity

POST /api/governance/compliance/remediate/{violation_id}
  → Trigger auto-remediation for violation

GET /api/governance/compliance/report?days=7
  → Generate compliance report for last N days
```

### Approval Workflow Endpoints

```
POST /api/governance/workflows/start
  → Start new workflow (request body: workflow_def)

GET /api/governance/workflows/{workflow_id}
  → Get workflow status

POST /api/governance/workflows/{workflow_id}/approve
  → Grant approval (request body: approver_id, reason)

POST /api/governance/workflows/{workflow_id}/escalate
  → Escalate workflow due to timeout
```

### Audit Endpoints

```
GET /api/governance/audit/events?workflow_id=...&limit=100
  → Query audit events

GET /api/governance/audit/verify
  → Verify audit trail immutability

GET /api/governance/audit/export?format=csv&days=7
  → Export audit trail
```

---

## FAQ & SUPPORT

### Q: What's the difference between auto-remediation and manual remediation?

**A:** Auto-remediation runs automatically for certain P2/P3 violations (e.g., auto-formatting code). Manual remediation requires human action (e.g., security review). See "Remediation Success Rate" in Key Metrics.

### Q: How often is the dashboard updated?

**A:** Real-time (1-second refresh cycle) for most metrics. Compliance score updates on every policy check. Trends update hourly.

### Q: Can I export dashboard data?

**A:** Yes. Use the "Export CSV" or "Export JSON" buttons on any widget. For API access, use `GET /api/governance/audit/export?format=csv`.

### Q: What's the retention policy for audit logs?

**A:** 7 years minimum (enterprise standard). See "Audit Trail Health" in Key Metrics.

### Q: Who can see the dashboard?

**A:** Based on RBAC (Track 12.1). Admins see everything, operators see own workflows only, readers see summaries only.

---

## SUPPORT & ESCALATION

**For Questions:**
- Slack: #governance-help
- Email: governance-team@aries-serpent.io

**For Critical Issues (P0):**
- Escalate to @mbaetiong immediately
- Page on-call: `pagerduty alert GOVERNANCE_CRITICAL`

**Documentation:**
- [Governance Policy Framework](./ GOVERNANCE_POLICY_FRAMEWORK.md)
- [Approval Engine API](../scripts/governance/approval_engine.py)
- [Compliance Monitor Docs](../scripts/governance/compliance_monitor.py)

---

**Dashboard Version:** 1.0.0-enterprise  
**Last Updated:** 2026-07-01T00:00:00Z  
**Maintained By:** Phase 12.2 Track Lead  
**Next Review:** 2026-07-11 (post-implementation)

