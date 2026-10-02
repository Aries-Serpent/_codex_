# PR Validation Flow - Coverage Baseline Monitoring

**Created:** 2026-07-02T02:22:00Z  
**Version:** 4.1.0  
**Status:** READY FOR WORKFLOW INTEGRATION (Phase 5)

**Document Purpose:** Define the end-to-end PR validation flow for coverage monitoring, from PR opening through merge decision.

**References:**
- `.codex/agent_briefs/UNIFIED_COVERAGE_AGENT_BRIEF.md` (agent responsibilities)
- `.codex/COVERAGE_VALIDATION_CRITERIA.md` (validation thresholds)
- `.codex/ESCALATION_RULES.yaml` (escalation routing)
- `.codex/PHASE_VALIDATION_GATES.yaml` (phase-specific gates)

---

## Overview

This flow is triggered on every PR opened/updated and every merge to main. It validates coverage compliance and routes escalations to appropriate agents.

```
PR Opened/Updated
    ↓
[STEP 1] Run Baseline Tracking Report
    ↓
[STEP 2] Execute Module Gates Validation
    ↓
[STEP 3] Run Quality Metrics Validation
    ↓
[STEP 4] Generate Validation Comment
    ↓
[STEP 5] Determine Traffic-Light Status (🟢/🟡/🔴)
    ↓
[STEP 6] Route Escalation (if needed)
    ↓
[STEP 7] Block Merge or Approve
```

---

## STEP 1: Run Baseline Tracking Report

### Trigger
- PR opened/updated to any branch
- Push to main (post-merge tracking)

### Action
Execute: `scripts/ci/generate_baseline_tracking_report.py`

```bash
python scripts/ci/generate_baseline_tracking_report.py \
  --pr-number ${{ github.event.number }} \
  --pr-sha ${{ github.event.pull_request.head.sha }} \
  --baseline-file .codex/COVERAGE_BASELINE_34_63.json \
  --output .codex/coverage/BASELINE_TRACKING_REPORT.json
```

### Outputs Generated
1. **Coverage metrics** (overall statement, branch, function coverage)
2. **Module tier breakdown** (Tier 1-4 individual coverage)
3. **Quality metrics** (pass rate, flakiness, determinism, isolation)
4. **Test count** (total tests, distribution by type)
5. **Comparison vs. baseline** (variance %, absolute change)
6. **Module changes** (any module losing >1% coverage)
7. **Escalation recommendation** (based on ESCALATION_RULES.yaml)

### Output File Format (JSON)
```json
{
  "pr_number": 1234,
  "pr_sha": "abc123def...",
  "run_timestamp": "2026-07-02T10:30:00Z",
  
  "coverage_metrics": {
    "overall_percent": 34.62,
    "branch_coverage_percent": 18.1,
    "function_coverage_percent": 24.2
  },
  
  "baseline_comparison": {
    "baseline_coverage": 34.63,
    "coverage_delta": -0.01,
    "variance_percent": -0.03,
    "status": "stable"
  },
  
  "module_tiers": {
    "tier_1": { "coverage": 92.5, "status": "maintaining" },
    "tier_2": { "coverage": 86.0, "status": "maintaining" },
    "tier_3": { "coverage": 76.1, "status": "stable" },
    "tier_4": { "coverage": 61.2, "status": "stable" }
  },
  
  "quality_metrics": {
    "test_pass_rate_percent": 100.0,
    "test_flakiness_percent": 0.0,
    "test_determinism_percent": 100.0,
    "test_isolation_percent": 100.0
  },
  
  "test_statistics": {
    "total_tests": 2467,
    "happy_path": 1604,
    "edge_case": 493,
    "error_path": 370
  },
  
  "escalation_recommendation": "stable",
  "escalation_agent": "none",
  "blocks_merge": false
}
```

---

## STEP 2: Execute Module Gates Validation

### Trigger
Output from STEP 1 ready

### Action
Load `.codex/PHASE_VALIDATION_GATES.yaml` (baseline_phase section) and validate:

```python
def validate_module_gates(report_json):
    """
    Check all module tiers against baseline_phase gates in
    .codex/PHASE_VALIDATION_GATES.yaml
    """
    gates = load_yaml('.codex/PHASE_VALIDATION_GATES.yaml')
    baseline = gates['baseline_phase']
    
    # Validate Tier 1 (Security) - MAINTAIN ≥90%
    tier_1_pass = report['module_tiers']['tier_1']['coverage'] >= 90.0
    if not tier_1_pass:
        escalate('tier_1_breach', 'red_alert_critical')
    
    # Validate Tier 2 (Auth) - MAINTAIN ≥85%
    tier_2_pass = report['module_tiers']['tier_2']['coverage'] >= 85.0
    if not tier_2_pass:
        escalate('tier_2_breach', 'orange_alert')
    
    # Validate Tier 3 (Infrastructure) - MAINTAIN ≥77%
    tier_3_pass = report['module_tiers']['tier_3']['coverage'] >= 77.0
    if not tier_3_pass:
        escalate('tier_3_breach', 'orange_alert')
    
    # Validate Tier 4 (Extended) - MAINTAIN ≥62%
    tier_4_pass = report['module_tiers']['tier_4']['coverage'] >= 62.0
    if not tier_4_pass:
        escalate('tier_4_breach', 'yellow_alert')
    
    return all([tier_1_pass, tier_2_pass, tier_3_pass, tier_4_pass])
```

### Decision Tree

**IF any tier breaches minimum:**
- ❌ FAIL gate validation
- → Move to STEP 3 (quality check)
- → BLOCK merge (Section STEP 7)

**IF all tiers pass:**
- ✅ PASS gate validation
- → Move to STEP 3

---

## STEP 3: Run Quality Metrics Validation

### Trigger
Output from STEP 2 ready

### Action
Check all 4 quality metrics from BASELINE_TRACKING_REPORT.json:

```python
def validate_quality_metrics(report_json):
    """
    Check all 4 quality metrics against baseline_phase gates
    """
    gates = load_yaml('.codex/PHASE_VALIDATION_GATES.yaml')
    baseline = gates['baseline_phase']
    
    # Check Test Pass Rate (≥99.5%)
    pass_rate_pass = report['quality_metrics']['test_pass_rate_percent'] >= 99.5
    
    # Check Test Flakiness (≤0.5%)
    flakiness_pass = report['quality_metrics']['test_flakiness_percent'] <= 0.5
    
    # Check Test Determinism (≥100%)
    determinism_pass = report['quality_metrics']['test_determinism_percent'] >= 100.0
    
    # Check Test Isolation (≥100%)
    isolation_pass = report['quality_metrics']['test_isolation_percent'] >= 100.0
    
    return {
        'pass_rate': pass_rate_pass,
        'flakiness': flakiness_pass,
        'determinism': determinism_pass,
        'isolation': isolation_pass
    }
```

### Escalation Actions

**Test Pass Rate < 99.5%:**
- → Escalate to `ci-testing-agent`
- → BLOCK merge (unresolved failures)

**Test Flakiness > 0.5%:**
- → Escalate to `autonomous-test-healer-agent`
- → Create fix PR automatically
- → Post comment: "Flaky tests detected, triggering autonomous-test-healer-agent"

**Test Determinism < 100%:**
- → Escalate to `ci-testing-agent`
- → BLOCK merge (non-deterministic behavior)

**Test Isolation < 100%:**
- → Escalate to `ci-testing-agent`
- → BLOCK merge (test cross-contamination)

### Decision Tree

**IF all quality metrics pass:**
- ✅ PASS quality validation
- → Move to STEP 4

**IF any metric fails:**
- ❌ FAIL quality validation
- → Move to STEP 4 (generate comment)
- → BLOCK merge (STEP 7)

---

## STEP 4: Generate Validation Comment

### Trigger
Steps 1-3 complete

### Action
Compile all validation results into a structured PR comment

### Comment Template

```markdown
## 📊 Coverage Validation Report

**PR:** #1234 | **Commit:** abc123...  
**Timestamp:** 2026-07-02T10:30:00Z

### ✅ Baseline Coverage

| Metric | Value | Status |
|--------|-------|--------|
| **Overall Coverage** | 34.62% | ✅ Stable (±0.01%) |
| **Variance from Baseline** | -0.03% | ✅ Within range |
| **Acceptable Range** | 33.13% - 36.13% | ✅ Pass |

### ✅ Module Tier Status

| Tier | Coverage | Min Required | Status |
|------|----------|--------------|--------|
| **Tier 1** (Security) | 92.5% | ≥90.0% | ✅ Maintain |
| **Tier 2** (Auth) | 86.0% | ≥85.0% | ✅ Maintain |
| **Tier 3** (Infrastructure) | 76.1% | ≥77.0% | ⚠️ Watch |
| **Tier 4** (Extended) | 61.2% | ≥62.0% | ✅ Maintain |

### ✅ Quality Metrics

| Metric | Value | Requirement | Status |
|--------|-------|-------------|--------|
| **Test Pass Rate** | 100.0% | ≥99.5% | ✅ Pass |
| **Test Flakiness** | 0.0% | ≤0.5% | ✅ Pass |
| **Test Determinism** | 100.0% | ≥100% | ✅ Pass |
| **Test Isolation** | 100.0% | ≥100% | ✅ Pass |

### ✅ Test Statistics

| Category | Count | Distribution |
|----------|-------|--------------|
| **Total Tests** | 2,467 | — |
| **Happy Path** | 1,604 | 65.0% |
| **Edge Case** | 493 | 20.0% |
| **Error Path** | 370 | 15.0% |

### Module Changes (>1% coverage change)

None detected.

### 🟢 Overall Status: APPROVED

**Escalation Level:** 🟢 STABLE  
**Recommended Action:** No action required - coverage stable  
**Merge Status:** ✅ Ready to merge

---

*Report generated by unified-coverage-agent | [View Details](...) | [Baseline Reference](.codex/COVERAGE_BASELINE_34_63.json)*
```

### Decision Tree for Comment Content

**IF coverage stable AND all quality metrics pass:**
- Use ✅ APPROVED template
- Include "Ready to merge" status

**IF coverage warning OR quality metric warning:**
- Use ⚠️ WARNING template
- Include specific recommendations

**IF coverage regression OR quality metric failure:**
- Use 🔴 BLOCKED template
- Include escalation agent and instructions

---

## STEP 5: Determine Traffic-Light Status

### Trigger
Validation comment content decided

### Action
Based on escalation recommendation from BASELINE_TRACKING_REPORT.json, determine status:

```python
def determine_traffic_light_status(report_json):
    """
    Map escalation_recommendation to traffic-light status
    """
    status_map = {
        'stable': ('🟢 STABLE', 'Continue monitoring'),
        'acceptable': ('🟡 ACCEPTABLE', 'Log and continue'),
        'yellow_alert': ('🟡 YELLOW ALERT', 'Review and recommend'),
        'orange_alert': ('🟠 ORANGE ALERT', 'Block and investigate'),
        'red_alert_critical': ('🔴 RED ALERT', 'Escalate to human')
    }
    
    symbol, action = status_map.get(
        report['escalation_recommendation'],
        ('❌ UNKNOWN', 'Review manually')
    )
    
    return symbol, action, report['escalation_agent']
```

### Traffic-Light Meanings

| Status | Symbol | Merge | Action |
|--------|--------|-------|--------|
| **STABLE** | 🟢 | ✅ Allowed | Continue monitoring |
| **ACCEPTABLE** | 🟡 | ✅ Allowed | Monitor and log |
| **YELLOW ALERT** | 🟡 | ✅ Allowed | Review and recommend |
| **ORANGE ALERT** | 🟠 | ❌ BLOCKED | Block and investigate |
| **RED ALERT** | 🔴 | ❌ BLOCKED | Escalate to human |

### Badge Integration

Add PR badge to comment:
```markdown
![Coverage Status](https://img.shields.io/badge/coverage-🟢%20STABLE-brightgreen)
```

---

## STEP 6: Route Escalation (If Needed)

### Trigger
Traffic-light status determined AND status is not 🟢

### Action
Route to appropriate agent based on ESCALATION_RULES.yaml

```python
def route_escalation(escalation_level, escalation_agent, pr_number):
    """
    Route escalation to appropriate agent or human
    """
    if escalation_agent == 'none':
        return  # No escalation needed
    
    if escalation_agent == '@mbaetiong':
        # Ping human directly
        post_pr_comment(
            f"@mbaetiong Coverage escalation required. "
            f"Escalation Level: {escalation_level}"
        )
        create_github_issue(
            title=f"Coverage Escalation: {escalation_level}",
            body=f"PR #{pr_number} requires human review due to {escalation_level}",
            labels=['coverage', 'escalation']
        )
    
    elif escalation_agent == 'unified-coverage-agent':
        # Post comment and wait for agent to respond
        post_pr_comment(
            f"@copilot unified-coverage-agent: Please review this coverage issue. "
            f"Escalation Level: {escalation_level}"
        )
    
    elif escalation_agent == 'ci-emergency-response-agent':
        # Post comment and wait for agent to block
        post_pr_comment(
            f"@copilot ci-emergency-response-agent: "
            f"Coverage regression detected. Please block PR. "
            f"Escalation Level: {escalation_level}"
        )
    
    elif escalation_agent == 'ci-testing-agent':
        # Post comment for test investigation
        post_pr_comment(
            f"@copilot ci-testing-agent: "
            f"Quality metric failure detected. Please investigate. "
            f"Escalation Level: {escalation_level}"
        )
    
    elif escalation_agent == 'autonomous-test-healer-agent':
        # Trigger automatic healing
        post_pr_comment(
            f"@copilot autonomous-test-healer-agent: "
            f"Flaky tests detected. Please initiate healing. "
            f"Escalation Level: {escalation_level}"
        )
    
    # Log escalation
    log_to_escalation_log({
        'pr_number': pr_number,
        'escalation_level': escalation_level,
        'escalation_agent': escalation_agent,
        'timestamp': now(),
        'status': 'pending'
    })
```

### Escalation Routing Table

| Escalation Level | Agent | Action |
|------------------|-------|--------|
| 🟢 STABLE | none | Continue |
| 🟡 ACCEPTABLE | unified-coverage-agent | Log and monitor |
| 🟡 YELLOW ALERT | unified-coverage-agent | Review and recommend |
| 🟠 ORANGE ALERT | ci-emergency-response-agent | Block and investigate |
| 🔴 RED ALERT | @mbaetiong | Escalate immediately |
| 🔴 FLAKY TESTS | autonomous-test-healer-agent | Auto-heal |
| 🔴 TEST FAILURE | ci-testing-agent | Investigate |

---

## STEP 7: Block Merge or Approve

### Trigger
Escalation routed (STEP 6 complete)

### Action
Apply merge status based on validation results

```python
def determine_merge_status(
    baseline_pass,
    quality_pass,
    escalation_level
):
    """
    Determine whether PR can be merged
    """
    # Hard blocks
    if baseline_pass and quality_pass:
        if escalation_level in ['stable', 'acceptable']:
            return 'APPROVE', 'All checks pass'
    
    # Soft blocks
    if not baseline_pass:
        return 'BLOCK', 'Coverage regression detected'
    
    if not quality_pass:
        return 'BLOCK', 'Quality metric failure'
    
    if escalation_level in ['yellow_alert']:
        return 'APPROVE_WITH_CAUTION', 'Coverage warning - monitor'
    
    if escalation_level in ['orange_alert', 'red_alert_critical']:
        return 'BLOCK', f'Escalation Level: {escalation_level}'
    
    return 'REVIEW', 'Manual review required'
```

### Merge Status Codes

| Status | Symbol | GitHub Status | Action |
|--------|--------|---------------|--------|
| **APPROVE** | ✅ | ✅ Pass | Merge allowed |
| **APPROVE_WITH_CAUTION** | ⚠️ | ⚠️ Pending | Merge allowed, monitor after merge |
| **BLOCK** | 🔴 | ❌ Fail | Merge blocked by CI |
| **REVIEW** | ❓ | ⏳ Pending | Manual review required |

### GitHub Status Check Integration

```python
# Set GitHub status check on commit
set_github_status_check(
    commit_sha=pr_sha,
    context='coverage/baseline-monitoring',
    state=merge_status.github_status,  # 'success', 'failure', 'pending'
    description=merge_status.description,
    target_url=f'{pr_url}#coverage-validation-report'
)
```

### Post-Merge Behavior

**If PR blocked:**
- ✅ Post comment explaining reason
- ✅ Link to relevant documentation
- ✅ Provide remediation steps
- ✅ Mention escalated agent (if applicable)

**If PR approved:**
- ✅ Post comment: "Coverage check passed ✅"
- ✅ Continue monitoring post-merge
- ✅ Log to BASELINE_HISTORY.ndjson

---

## Decision Tree (Complete Flow)

```
START: PR Opened/Updated
  ↓
[STEP 1] Generate BASELINE_TRACKING_REPORT
  ↓ (report ready)
[STEP 2] Validate Module Tiers
  ├─ Tier 1 ≥90%? ───NO──→ Escalate: red_alert_critical
  ├─ Tier 2 ≥85%? ───NO──→ Escalate: orange_alert
  ├─ Tier 3 ≥77%? ───NO──→ Escalate: orange_alert
  └─ Tier 4 ≥62%? ───NO──→ Escalate: yellow_alert
  ↓ (all pass)
[STEP 3] Validate Quality Metrics
  ├─ Pass Rate ≥99.5%? ──NO──→ Escalate: ci-testing-agent → BLOCK
  ├─ Flakiness ≤0.5%?  ──NO──→ Escalate: autonomous-test-healer-agent
  ├─ Determinism=100%?  ──NO──→ Escalate: ci-testing-agent → BLOCK
  └─ Isolation=100%?    ──NO──→ Escalate: ci-testing-agent → BLOCK
  ↓ (all pass)
[STEP 4] Generate Validation Comment
  ↓
[STEP 5] Determine Traffic-Light Status
  ├─ 🟢 STABLE? ────────→ APPROVE
  ├─ 🟡 ACCEPTABLE? ────→ APPROVE
  ├─ 🟡 YELLOW? ────────→ APPROVE + WARN
  ├─ 🟠 ORANGE? ────────→ BLOCK + ESCALATE
  └─ 🔴 RED ALERT? ────→ BLOCK + ESCALATE TO HUMAN
  ↓
[STEP 6] Route Escalation (if needed)
  ├─ unified-coverage-agent? ──→ Post comment
  ├─ ci-emergency-response-agent? ──→ Post comment
  ├─ ci-testing-agent? ──────────→ Post comment
  ├─ autonomous-test-healer-agent? ──→ Post comment
  └─ @mbaetiong? ───────────────→ Ping + Create Issue
  ↓
[STEP 7] Block/Approve Merge
  ├─ All pass? ──→ ✅ APPROVE
  ├─ Warn? ────→ ⚠️ APPROVE_WITH_CAUTION
  └─ Fail? ────→ ❌ BLOCK
  ↓
END: Set GitHub Status + Post Comment
```

---

## Automatic Actions

### Automatic Fixes

**Flaky Tests (autonomous-test-healer-agent):**
- Detect: Test flakiness > 0.5%
- Action: Auto-create PR with fixes
- Reference: `.codex/ESCALATION_RULES.yaml` - Quality Metrics → Flakiness

### Automatic Escalations

**Coverage Critical Loss:**
- Detect: Coverage drop > 3%
- Action: Escalate to @mbaetiong immediately
- Timeout: 1 hour auto-escalation

**Test Count Regression:**
- Detect: Total tests < 2,467
- Action: Block PR + escalate to ci-testing-agent
- Timeout: 2 hours auto-escalation

**Module Tier Breach (Tier 1):**
- Detect: Tier 1 (security) drops > 0.5%
- Action: Block PR + escalate to @mbaetiong
- Timeout: 30 minutes

---

## Integration with CI Workflows

### GitHub Actions Workflow Example

```yaml
name: Coverage Validation

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]

jobs:
  coverage-validation:
    runs-on: ubuntu-latest
    steps:
      # STEP 1: Run tracking report
      - name: Generate Baseline Tracking Report
        run: |
          python scripts/ci/generate_baseline_tracking_report.py \
            --pr-number ${{ github.event.number }} \
            --pr-sha ${{ github.event.pull_request.head.sha }} \
            --baseline-file .codex/COVERAGE_BASELINE_34_63.json \
            --output .codex/coverage/BASELINE_TRACKING_REPORT.json

      # STEP 2 & 3: Validate gates
      - name: Validate Module Gates & Quality Metrics
        run: |
          python .codex/coverage/validate_gates.py \
            --report .codex/coverage/BASELINE_TRACKING_REPORT.json \
            --gates .codex/PHASE_VALIDATION_GATES.yaml \
            --escalation-rules .codex/ESCALATION_RULES.yaml

      # STEP 4: Generate comment
      - name: Generate Validation Comment
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            // Read report and generate comment
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('.codex/coverage/BASELINE_TRACKING_REPORT.json')
            );
            
            // Generate markdown comment
            const comment = generateComment(report);
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      # STEP 5-7: Set status & block if needed
      - name: Set GitHub Status Check
        uses: actions/github-script@v6
        with:
          script: |
            const report = JSON.parse(
              fs.readFileSync('.codex/coverage/BASELINE_TRACKING_REPORT.json')
            );
            
            github.rest.repos.createCommitStatus({
              owner: context.repo.owner,
              repo: context.repo.repo,
              sha: context.payload.pull_request.head.sha,
              state: report.blocks_merge ? 'failure' : 'success',
              description: report.escalation_recommendation,
              context: 'coverage/baseline-monitoring'
            });
            
            if (report.blocks_merge) {
              core.setFailed('Coverage validation failed');
            }
```

---

## Rollback & Recovery

### If Validation Fails

1. **Review escalation reason** in PR comment
2. **Understand the gap** from .codex/COVERAGE_BASELINE_34_63.json
3. **Add tests** to address gap
4. **Re-run** workflow on next commit
5. **Verify** new baseline tracking report

### If False Positive Detected

1. **Document** the false positive in a GitHub issue
2. **Escalate** to @mbaetiong
3. **Adjust** thresholds in ESCALATION_RULES.yaml if needed
4. **Re-test** with adjusted rules

---

## Reference Summary

| Document | Purpose |
|----------|---------|
| `.codex/COVERAGE_BASELINE_34_63.json` | Authoritative baseline snapshot |
| `.codex/COVERAGE_VALIDATION_CRITERIA.md` | Validation thresholds & escalation matrix |
| `.codex/ESCALATION_RULES.yaml` | Escalation routing & automation |
| `.codex/PHASE_VALIDATION_GATES.yaml` | Phase-specific validation gates |
| `.codex/agent_briefs/UNIFIED_COVERAGE_AGENT_BRIEF.md` | Agent responsibilities |
| `scripts/ci/generate_baseline_tracking_report.py` | Report generation script |
| `.codex/coverage/BASELINE_TRACKING_REPORT.json` | Per-PR report output |
| `.codex/coverage/ESCALATION_LOG.ndjson` | Escalation history |
