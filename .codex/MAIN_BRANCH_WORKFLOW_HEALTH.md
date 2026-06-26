# Main Branch Workflow Health Baseline

**Version:** 1.0.0  
**Last Updated:** 2026-06-26T22:35:45Z  
**Purpose:** Track workflow execution health on main branch; provide reference baseline for healthy PR profiles  
**Update Frequency:** After every successful merge to main

---

## Health Metrics Definitions

### Workflow Health Score Formula

```
Health Score = (Successful Runs / Total Runs) × 100 + 
               (Auto-Approved / (Auto-Approved + Manual Approved)) × 10 +
               (REQ-4/REQ-5 Compliance / 100) × 10

Minimum: 0%   |   Healthy Baseline: 90%   |   Excellent: 95%+
```

### Metric Definitions

| Metric | Definition | Target |
|--------|-----------|--------|
| **Success Rate** | (Successful runs / Total runs) × 100 | ≥95% |
| **Auto-Approve Rate** | (Workflows auto-approved / Total needing approval) × 100 | ≥90% |
| **Compliance Rate** | (PRs with REQ-4 ✅ & REQ-5 ✅ / Total PRs) × 100 | 100% |
| **WEC Preservation Rate** | (Merges with WEC intact / Total merges) × 100 | 100% |
| **Time-to-Merge (median)** | Median time from PR open to merge | <2 hours |

---

## Baseline Record: Last 10 Successful Merges to Main

### Entry Template

```
## PR #{PR_NUMBER}

**Merge Commit:** {SHA-8}  
**Merge Date:** {ISO-8601 timestamp}  
**Branch:** {branch-name}  
**Copilot Agent:** {agent or manual}  

### WEC State
- Pre-merge WEC: {9 items, checked/unchecked count}
- Post-merge WEC: {preserved/stripped}
- Governance: REQ-4 ✅, REQ-5 ✅

### Workflow Execution
- Pre-merge-validation: ✅ PASSED (auto-run)
- Comment-review-gate: ✅ PASSED (auto-run)
- Deferral-language-gate: ✅ PASSED (auto-run)
- Workflow-execution-gate: ✅ PASSED (auto-run)
- Cost-gate: ⏭️ SKIPPED (unchecked)

### Auto-Approval Events
- Workflows needing approval: N
- Auto-approved: N (auto-approve rate: 100%)
- Manual approvals: 0
- Approval failures: 0

### Performance
- Push-to-merge time: Xh Ym Zs
- Total workflow time: Ah Bm Cs
- Approval delay: 0-5 min

### Notable Events
- [Any delays, retries, or manual interventions]

### Health Score
{Score}% (Success ✅, Auto-Approval ✅, Compliance ✅)
```

---

## Current Health Baseline (As of 2026-06-26)

### Summary Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Last 10 Merges Health Score** | TBD (initialize on first merge) | 🟡 INITIALIZING |
| **Success Rate (7-day)** | TBD | 🟡 TRACKING |
| **Auto-Approve Rate** | TBD | 🟡 TRACKING |
| **Compliance Rate (REQ-4/REQ-5)** | TBD | 🟡 TRACKING |
| **WEC Preservation Rate** | TBD | 🟡 TRACKING |
| **Median Time-to-Merge** | TBD | 🟡 TRACKING |

### Initialization Status

This baseline document is being initialized with the WEC hardening phase (Session N). Baseline entries will be populated after the first successful merge post-hardening.

---

## How to Update This Document

### Step 1: After Successful Merge to Main

```bash
# 1. Capture merge details
MERGE_SHA=$(git rev-parse HEAD)
MERGE_DATE=$(git log -1 --format=%aI $MERGE_SHA)
PR_NUMBER=$(gh pr list --merged --limit 1 --json number | jq -r '.[0].number')

# 2. Extract WEC from PR body
gh pr view $PR_NUMBER --json body | jq -r '.body' | \
  sed -n '/## 🔄 Workflow Execution Checklist/,/^##/p' > /tmp/wec.txt

# 3. Fetch workflow run logs
gh run list --branch main --limit 1 --json id,status,name

# 4. Calculate metrics
python scripts/ci/calculate_workflow_health.py \
  --pr $PR_NUMBER \
  --merge-sha $MERGE_SHA \
  --output-file .codex/MAIN_BRANCH_WORKFLOW_HEALTH.md
```

### Step 2: Record Entry

Append a new entry to this document using the template above, populating all sections.

### Step 3: Update Summary

Recalculate aggregate metrics from the last 10 entries and update the "Summary Statistics" table.

---

## Trend Analysis (To Be Populated After Initial Merges)

### Health Score Trend

```
Date          | Score | Trend
2026-06-26    | N/A   | 🟡 INITIALIZING
2026-06-27    | TBD   | ⬜ PENDING
2026-06-28    | TBD   | ⬜ PENDING
```

### Success Rate Trend

```
7-day average:   TBD%
30-day average:  TBD%
Trend:           📈 PENDING
```

### Auto-Approval Rate Trend

```
7-day average:   TBD%
30-day average:  TBD%
Trend:           📈 PENDING
```

### Common Failure Patterns (Last 30 Days)

| Pattern | Count | Rate | Prevention Status |
|---------|-------|------|-------------------|
| REQ-4 missing | N/A | TBD | 🔴 INITIALIZING |
| REQ-5 missing | N/A | TBD | 🔴 INITIALIZING |
| WEC stripped | N/A | TBD | 🔴 INITIALIZING |
| Approval failed | N/A | TBD | 🔴 INITIALIZING |
| Cost exceeded | N/A | TBD | 🔴 INITIALIZING |

---

## Alert Thresholds

### 🔴 CRITICAL Alerts (Immediate Action Required)

- Health Score drops below 70%
- Success Rate drops below 80%
- REQ-4/REQ-5 Compliance drops below 90%
- WEC Preservation Rate drops below 95%
- 3+ consecutive failures on the same pattern

### 🟡 WARNING Alerts (Monitor Closely)

- Health Score drops below 85%
- Success Rate drops below 90%
- Compliance Rate drops below 100%
- Any manual approval required (should be auto-approved)
- 2 consecutive failures on the same pattern

### 🟢 INFO (Informational Only)

- All metrics within normal range
- Workflow execution time changes
- Auto-approval rate variations

---

## Escalation Procedures

### If Health Score Falls Below 85%

1. Check last 3 failed merges for common pattern
2. Reference `.codex/WORKFLOW_FAILURE_MATRIX.md` for root cause
3. If pattern found: implement quick fix or escalate
4. Post GitHub issue with [CI_HEALTH] tag
5. Notify @mbaetiong

### If REQ-4/REQ-5 Compliance Drops

1. Review last non-compliant merge
2. Check if `session_wrapup_autofix.py --check` was run
3. If tool wasn't used: retrain Copilot Agents
4. If tool failed: debug and fix the tool
5. Escalate to unified-governance-gate agent

### If WEC Preservation Rate Drops

1. Analyze PR body history for stripped WEC
2. Check if `report_progress` calls included WEC
3. Review Copilot Agent session logs
4. Update `.codex/WEC_SESSION_INVARIANT.md` if needed
5. Retrain agents on WEC preservation

---

## Reference Data: Healthy PR Profile

Use this as a checklist when reviewing PRs for potential issues:

```yaml
✅ HEALTHY PR:
  WEC:
    - Present in PR body: YES
    - Format valid: YES (all [x] or [ ] correct)
    - Required items checked (main): 5/5
    - Optional items checked: 3-4/4
    - Preserved after commits: YES
  
  Governance:
    - REQ-4 (AGENT_ACCOUNTABILITY_REPORT.md): UPDATED
    - REQ-5 (CHANGELOG.md): UPDATED
    - Both in final commit: YES
  
  Workflows:
    - Pre-merge-validation: ✅ PASSED
    - Compliance gates: ✅ PASSED
    - Auto-approved: 100%
    - Failures: 0
  
  Performance:
    - Push-to-merge time: <2h
    - No retries: YES
    - No manual interventions: YES
  
  Health Score: 95%+
```

---

## Tool Dependencies

This document is updated by:
- `scripts/ci/calculate_workflow_health.py` (metrics calculation) — **TBD Phase 6 Implementation**
- `scripts/ci/workflow_health_monitor.py` (daily monitoring) — **TBD Phase 6 Implementation**
- Copilot Agent `session_wrapup_autofix.py` (compliance tracking)

### Related Documents

- **Workflow Failure Matrix:** `.codex/WORKFLOW_FAILURE_MATRIX.md`
- **WEC Session Invariant:** `.codex/WEC_SESSION_INVARIANT.md`
- **WEC Canonical Items:** `.codex/WEC_CANONICAL_ITEMS.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-26 | Initial baseline template; initialization of health tracking |

---

## Future Work

- [ ] Implement `calculate_workflow_health.py` script for automated metric calculation
- [ ] Implement `workflow_health_monitor.py` for daily health reports
- [ ] Create GitHub Actions workflow to update this document post-merge
- [ ] Set up alerts for health score thresholds
- [ ] Create dashboard visualization of health trends
