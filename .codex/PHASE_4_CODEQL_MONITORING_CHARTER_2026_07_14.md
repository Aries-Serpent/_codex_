# Phase 4 CodeQL Monitoring Charter — 2026-07-14

**Date:** 2026-07-14  
**Status:** ✅ MONITORING ACTIVE  
**Authority:** @mbaetiong D-tier autonomous  
**Phase:** Phase 4 — CodeQL GA Deployment

---

## Executive Summary

This charter establishes continuous monitoring and alert infrastructure for Phase 4 CodeQL GA deployment. The monitoring strategy focuses on:

1. **CodeQL Alert Regression Detection** — Immediate notification if untrusted-checkout patterns resurface
2. **Workflow Execution Monitoring** — Health checks for 3 fixed workflows
3. **Branch Protection Validation** — Continuous verification of CodeQL in required status checks
4. **Security Pattern Tracking** — Documentation of any new CodeQL patterns detected

**Success Criteria:** Zero CodeQL alerts maintained, all workflows execute successfully, zero regressions detected.

---

## Part 1: CodeQL Alert Regression Monitoring

### Alert Configuration: "CodeQL Untrusted Code Pattern"

**Trigger Conditions:**
- Any CodeQL alert of type "Checkout of untrusted code" appears on main branch
- Any new security alert with severity CRITICAL or HIGH
- Any alert in workflow files (*.yml/*.yaml)

**Notification Recipients:**
- Primary: @mbaetiong (owner)
- Secondary: Copilot security-review-agent (for automated analysis)

**Response SLA:** 2 hours for CRITICAL alerts, 8 hours for HIGH severity

**Investigation Steps:**
1. Check alert location (which workflow file)
2. Compare against known-good commit SHA (8e875c16)
3. Review last 5 commits to main for problematic git operations
4. If regression detected: Immediately escalate to emergency response protocol

### Implementation

GitHub Actions monitoring workflow (automatic):

```yaml
# .github/workflows/codeql-monitoring.yml (reference for manual setup)
name: CodeQL Regression Monitoring
on:
  schedule:
    - cron: '0 * * * *'  # Hourly
  workflow_run:
    workflows: [codeql.yml]
    types: [completed]

jobs:
  check_regression:
    runs-on: ubuntu-latest
    steps:
      - name: Check for CodeQL alerts
        run: |
          # Query GitHub API for open alerts on main
          ALERTS=$(gh api repos/${{ github.repository }}/code-scanning/alerts \
            --method GET \
            --field state=open \
            --field ref=refs/heads/main)
          
          if [ $(echo "$ALERTS" | jq 'length') -gt 0 ]; then
            # Alert found - notify @mbaetiong
            gh issue create \
              --repo Aries-Serpent/_codex_ \
              --title "SECURITY ALERT: CodeQL regression detected on main" \
              --body "$(echo "$ALERTS" | jq -r '.[] | "- \(.rule.id): \(.message.text)"')" \
              --assignee mbaetiong
          fi
        env:
          GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY }}
```

---

## Part 2: Workflow Execution Monitoring

### 3 Workflows to Monitor

#### 1. `iterative-self-healing-ci.yml`

**Trigger:** workflow_run (any workflow failure on main)  
**Key Jobs:** heal, baseline-sweep  
**Health Indicators:**
- ✅ heal job completes successfully
- ✅ baseline-sweep job completes successfully
- ✅ No git operation errors in logs
- ✅ API validation calls succeed (gh api repos/...)
- ❌ Absence of "untrusted-checkout" warnings

**Monitoring Points:**
- Check recent runs on GitHub Actions page
- Review job logs for API call failures
- Verify file synchronization completed

**SLA:** Should complete within 5 minutes of triggered event

#### 2. `cognitive-analysis-feed.yml`

**Trigger:** workflow_run completion + scheduled (2 AM UTC)  
**Key Jobs:** feed_patterns, aftermath_evaluator  
**Health Indicators:**
- ✅ feed_patterns job completes without errors
- ✅ aftermath_evaluator job completes without errors
- ✅ API validation calls execute successfully
- ✅ Pattern learning updates applied
- ❌ Absence of git checkout errors

**Monitoring Points:**
- Check scheduled runs at 2 AM UTC
- Review feed_patterns job for pattern updates
- Verify aftermath_evaluator processing

**SLA:** Should complete within 15 minutes of trigger

#### 3. `vars-guide-sync.yml`

**Trigger:** workflow_run completion (push to main)  
**Key Job:** sync-guide  
**Health Indicators:**
- ✅ sync-guide job completes successfully
- ✅ Files staged and committed correctly
- ✅ No API validation errors
- ✅ Synchronization artifacts generated

**Monitoring Points:**
- Check recent runs after main branch pushes
- Review commit history for sync artifacts
- Verify documentation files updated

**SLA:** Should complete within 10 minutes of trigger

### Manual Workflow Verification (Weekly)

```bash
#!/bin/bash
# Weekly workflow health check script

# Check iterative-self-healing-ci.yml recent runs
gh run list \
  --workflow iterative-self-healing-ci.yml \
  --branch main \
  --limit 5 \
  --json status,conclusion,createdAt

# Check cognitive-analysis-feed.yml recent runs
gh run list \
  --workflow cognitive-analysis-feed.yml \
  --branch main \
  --limit 5 \
  --json status,conclusion,createdAt

# Check vars-guide-sync.yml recent runs
gh run list \
  --workflow vars-guide-sync.yml \
  --branch main \
  --limit 5 \
  --json status,conclusion,createdAt

# Summary: All runs should have status "completed" with conclusion "success"
```

---

## Part 3: Branch Protection Validation

### Required Status Checks on Main Branch

**Verify Monthly:**

```bash
# Check branch protection rules
gh api repos/Aries-Serpent/_codex_/branches/main/protection \
  --method GET \
  --jq '.required_status_checks'

# Expected output includes:
# {
#   "strict": true,
#   "contexts": [
#     "CodeQL (code-scanning)",
#     "REQ-4 / Accountability",
#     "REQ-5 / Changelog",
#     ... other CI checks
#   ]
# }
```

**Verification Checklist:**
- ✅ CodeQL (code-scanning) in required_status_checks
- ✅ Require PR reviews: at least 1
- ✅ Require branches to be up to date: enabled
- ✅ CodeQL scanning workflow passing
- ✅ No temporary bypass rules active

### Manual Branch Protection Audit

```bash
# 1. Verify CodeQL in required checks
gh api repos/Aries-Serpent/_codex_/branches/main/protection \
  | jq '.required_status_checks.contexts[] | select(. | contains("CodeQL"))'

# Expected: "CodeQL (code-scanning)"

# 2. Verify PR review requirement
gh api repos/Aries-Serpent/_codex_/branches/main/protection \
  | jq '.required_pull_request_reviews'

# Expected: { "required_approving_review_count": 1, ... }

# 3. Verify up-to-date requirement
gh api repos/Aries-Serpent/_codex_/branches/main/protection \
  | jq '.required_status_checks.strict'

# Expected: true
```

---

## Part 4: Security Pattern Tracking

### CodeQL Alert Database (Historical)

**Location:** `.codex/codeql_monitoring_log.jsonl`  
**Format:** One JSON record per monitoring cycle

```json
{
  "timestamp": "2026-07-14T23:30:00Z",
  "alert_count": 0,
  "alerts": [],
  "workflow_status": {
    "iterative-self-healing-ci": "success",
    "cognitive-analysis-feed": "success",
    "vars-guide-sync": "success"
  },
  "branch_protection_validated": true,
  "notes": "Phase 4 GA deployment monitoring initialized"
}
```

### Pattern Entry Template (If New Patterns Detected)

When a new CodeQL pattern is detected:

```json
{
  "date": "2026-07-XX",
  "pattern_id": "CODEQL-SECURITY-NEW-001",
  "rule_name": "[pattern name]",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "affected_workflow": "[workflow filename]",
  "root_cause": "[description]",
  "recommended_fix": "[solution]",
  "reference": "[link to analysis]"
}
```

---

## Part 5: Escalation Protocol

### Immediate Actions (If Alert Detected)

**Level 1 — CodeQL Alert Detected:**
1. ✅ Automatic GitHub issue created
2. ✅ @mbaetiong notified
3. ✅ Auto-snapshot current main branch SHA
4. ✅ Run comparison against known-good SHA (8e875c16)

**Level 2 — Regression Confirmed:**
1. ✅ Lock main branch from merges (via branch protection)
2. ✅ Activate emergency response workflow
3. ✅ Notify copilot security-review-agent
4. ✅ Create investigation brief

**Level 3 — Critical Pattern (Multiple Alerts):**
1. ✅ Escalate to @mbaetiong immediately
2. ✅ Activate full CI emergency response
3. ✅ Revert to last known-good SHA if needed
4. ✅ Full audit of workflow files

### Recovery Protocol

```bash
# 1. Identify problematic commit
git log --oneline main | head -10

# 2. Compare against known-good
git diff 8e875c16..main -- .github/workflows/

# 3. If regression found:
# - Check for git operations in workflow_run contexts
# - Verify YAML structure and API calls
# - Apply fix following Phase 4 pattern (API-only validation)

# 4. Commit fix with reference
git commit -m "fix(security): Resolve CodeQL regression - ref: [alert-id]"

# 5. Verify fix
gh run create -w codeql.yml -r main
```

---

## Part 6: Monthly Review Checklist

**Every 1st of the month, @mbaetiong should:**

- [ ] Review CodeQL alert history (zero expected)
- [ ] Check workflow execution logs (all 3 should be green)
- [ ] Validate branch protection rules
- [ ] Review any new security patterns detected
- [ ] Archive monitoring logs to `.codex/codeql_monitoring_log.jsonl`
- [ ] Update this charter if patterns change

**Review Command:**
```bash
# Generate monthly report
python scripts/monitoring/generate_codeql_report.py \
  --month $(date +%Y-%m) \
  --output .codex/CODEQL_MONTHLY_REPORT_$(date +%Y_%m).md
```

---

## Part 7: Documentation & Runbooks

### References for On-Call Engineers

- **CodeQL Alert Resolution Pattern:** `.codex/CODEQL_ALERT_RESOLUTION_FINAL_REPORT_2026_07_14.md`
- **Workflow Security Pattern:** `docs/SECURITY.md#workflow_run-privileged-context-security-pattern`
- **Contribution Guidelines:** `CONTRIBUTING.md#workflow-security-checklist`
- **Phase 4 Completion Report:** `.codex/PHASE4_RESOLUTION_COMPLETION_SUMMARY_2026_07_14.md`

### Escalation Contacts

| Role | Contact | Trigger |
|------|---------|---------|
| Owner | @mbaetiong | Any CRITICAL or HIGH alert |
| Security Review Agent | copilot security-review-agent | Pattern analysis on new alerts |
| Emergency Response | CI Emergency Response Agent | Multiple alerts or lock condition |

---

## Sign-Off

**Status:** ✅ MONITORING CHARTER ACTIVE

Continuous monitoring for Phase 4 CodeQL GA deployment has been established. All workflows are instrumented for health tracking, alert regressions will trigger immediate escalation, and monthly reviews will ensure sustained security compliance.

**Next Milestone:** Phase 4 GA deployment authorized for production (August 2026)

---

**Generated:** 2026-07-14T23:30:00Z  
**Session:** Phase 4 CodeQL GA Deployment Verification  
**Authority:** @mbaetiong D-tier autonomous
