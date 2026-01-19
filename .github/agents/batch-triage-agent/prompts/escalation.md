# Escalation Criteria Prompt

## Context

You are determining when to escalate CI failures to human engineers vs. attempting automated resolution.

## Escalation Framework

### Auto-Handle (No Escalation)
**Criteria**: All must be true
- Confidence > 90%
- Historical success rate > 85%
- Impact: Low (single file, easily reversible)
- Pattern: Well-known with proven fixes
- Risk: Low

**Actions**:
- Auto-apply fix
- Create PR
- Notify in Slack (#ci-alerts channel)
- Monitor for reversion

**Examples**:
- Add missing test dependency
- Fix typo in import
- Update deprecated API call (documented)
- Reformat code with Black/Ruff

---

### Create PR for Review (Escalate to Team)
**Criteria**: Any is true
- Confidence 70-90%
- Historical success rate 70-85%
- Impact: Moderate (multiple files, requires testing)
- Pattern: Known but with some variance
- Risk: Medium

**Actions**:
- Generate fix
- Create PR with detailed description
- Request review from relevant team
- Add automated tests
- Tag with `needs-review` label

**Examples**:
- Refactor function with multiple callers
- Update configuration with side effects
- Add feature flag for optional dependency
- Modify test assertions

---

### Create Issue for Investigation (Escalate to Engineering Lead)
**Criteria**: Any is true
- Confidence < 70%
- No historical success data
- Impact: High (architecture, breaking change)
- Pattern: Novel or complex
- Risk: High

**Actions**:
- Create detailed issue
- Include all diagnostic data
- Notify engineering lead
- Provide investigation guide
- Tag with `needs-investigation` and severity label

**Examples**:
- Flaky test with no clear root cause
- Segmentation fault or crash
- Performance regression
- Security vulnerability
- Data corruption

---

### Immediate Alert (Critical Escalation)
**Criteria**: Any is true
- Security vulnerability detected
- Production system affected
- Data loss risk
- Multiple critical tests failing
- CI completely blocked

**Actions**:
- Page on-call engineer (if configured)
- Slack alert to #eng-oncall
- Create P0 incident
- Block merges if necessary
- Escalate to engineering lead + CTO

**Examples**:
- Security scan finds critical CVE
- All CI pipelines failing
- Production deployment blocked
- Database migration failure
- Secret leaked in logs

---

## Decision Tree

```
Start: Analyze Failure
  │
  ├─ Is it Critical? (Security/Production/Data Loss)
  │  └─ YES → IMMEDIATE ALERT
  │  └─ NO → Continue
  │
  ├─ Do we have a proven fix? (>90% confidence, >85% success rate)
  │  └─ YES → Is risk LOW?
  │     ├─ YES → AUTO-HANDLE
  │     └─ NO → CREATE PR FOR REVIEW
  │  └─ NO → Continue
  │
  ├─ Do we have a probable fix? (70-90% confidence)
  │  └─ YES → CREATE PR FOR REVIEW
  │  └─ NO → Continue
  │
  └─ CREATE ISSUE FOR INVESTIGATION
```

## Escalation Templates

### Template 1: Auto-Handle Notification
```
🤖 **Auto-Fix Applied**: #{issue_number}

**Issue**: {failure_description}
**Fix**: {remediation_description}
**Confidence**: {confidence}%
**PR**: #{pr_number}

Tests running... Results in ~{estimated_time}
```

### Template 2: Review Request
```
🔧 **CI Fix Needs Review**: #{pr_number}

**Failures Addressed**: {issue_numbers}
**Root Cause**: {root_cause}
**Proposed Fix**: {remediation_summary}

**Confidence**: {confidence}%
**Historical Success**: {success_rate}%
**Estimated Effort**: {effort}

Please review changes in: {files_changed}
/cc @{reviewer}
```

### Template 3: Investigation Required
```
🚨 **CI Failure Requires Investigation**: #{issue_number}

**Summary**: {failure_summary}
**Severity**: {severity}
**Affected**: {affected_areas}

**Diagnostic Data**:
- Logs: {log_url}
- Stack Trace: {stack_trace}
- Recent Changes: {related_prs}

**Investigation Guide**:
1. {step_1}
2. {step_2}
3. {step_3}

**Potential Leads**:
- {hypothesis_1}
- {hypothesis_2}

/cc @{engineering_lead}
```

### Template 4: Critical Alert
```
🚨🚨🚨 **CRITICAL CI FAILURE** 🚨🚨🚨

**Severity**: P0 - CRITICAL
**Impact**: {impact_description}
**Status**: {current_status}

**Immediate Actions Required**:
1. {action_1}
2. {action_2}

**Incident Details**:
- Started: {timestamp}
- Affected Systems: {systems}
- Current State: {state}

**War Room**: {slack_channel}
**Incident Lead**: @{on_call_engineer}

/page @{on_call}
```

## Escalation Metrics

Track:
- False escalations (auto-fix would have worked)
- Missed escalations (should have escalated sooner)
- Time to resolution by escalation tier
- Engineer satisfaction with escalation decisions

## Continuous Improvement

Review escalation decisions:
- Weekly: Review last week's escalations
- Adjust thresholds based on outcomes
- Update confidence scores
- Refine criteria

**Feedback Loop**:
1. Record escalation decision
2. Track actual outcome
3. Compare decision with outcome
4. Adjust model parameters
5. Update escalation criteria

## Special Cases

### Flaky Tests
- Escalation: CREATE ISSUE
- Reason: Need root cause analysis
- Action: Disable test + investigate

### New Test Failures (First Time)
- Escalation: CREATE PR FOR REVIEW
- Reason: Might be intentional change
- Action: Review with PR author

### Recurring Failures (>3 in 7 days)
- Escalation: CREATE ISSUE + NOTIFY LEAD
- Reason: Systemic issue, not one-off
- Action: Investigate root cause

### Post-Deployment Failures
- Escalation: IMMEDIATE ALERT if prod
- Escalation: CREATE ISSUE if staging/dev
- Action: Rollback consideration

## Integration with Owner Approval Guard

For automated fixes requiring approval:
1. Generate fix + PR
2. Request approval from `owner-approval-guard` agent
3. Apply if approved within 24h
4. Escalate to human if approval denied or timeout
