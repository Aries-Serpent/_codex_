# Phase 4 Governance Documentation Guide

**Version:** 1.0.0  
**Created:** 2026-07-13T18:20:52Z  
**Purpose:** Comprehensive governance handbook for Phase 4 consolidated workflows  
**Audience:** All developers, agents, and infrastructure teams  
**Authority:** @mbaetiong (D-tier autonomous)

---

## Document Overview

This guide consolidates all Phase 4 governance, compliance, and monitoring documentation into a single reference point for operators, developers, and automated systems.

### Quick Links

| Purpose | Document | Size |
|---------|----------|------|
| **Governance Framework** | PHASE_4_GOVERNANCE_MATRIX.md | 20 KB |
| **Workflow Checklist** | WEC_CANONICAL_ITEMS.md | 10 KB |
| **AI Policy** | CODEBASE_AGENCY_POLICY.md | 15 KB |
| **Compliance** | PHASE_4_COMPLIANCE_VALIDATION_REPORT.md | 15 KB |
| **Monitoring** | PHASE_4_MONITORING_DEPLOYMENT.md | 23 KB |
| **Executive Summary** | PHASE_4_FINAL_EXECUTIVE_REPORT.md | 25 KB |

---

## 1. Understanding the Phase 4 Governance Architecture

### 1.1 Three Core Pillars

Phase 4 governance is built on **three independent validation pillars** that must all pass before merge approval:

```
Pillar 1: Owner Approval
├─ Question: Does PR author have authority?
├─ Check: @mbaetiong approval for sensitive changes
├─ Default: Auto-approve if CI green
└─ Gate: BLOCK if owner-gated file changed without approval

Pillar 2: Config Validation
├─ Question: Are all configurations valid?
├─ Check: Validate configs against schemas
├─ Default: Pass if all files match schema
└─ Gate: BLOCK if schema validation fails + show errors

Pillar 3: Compliance Check
├─ Question: Does code follow all policies?
├─ Check: No secrets, no deferral language, addresses comments
├─ Default: Pass if no policy violations
└─ Gate: BLOCK if violations found + list remediation steps
```

**Decision Logic:**
```
IF (Pillar1 == PASS) AND (Pillar2 == PASS) AND (Pillar3 == PASS)
  THEN: APPROVE (post green comment)
ELSE
  THEN: BLOCK (post red comment with remediation)
```

### 1.2 The 9 Master Workflows

All CI/CD logic flows through **exactly 9 canonical workflows**:

| # | Workflow | Owner | Category | Gate Type |
|---|----------|-------|----------|-----------|
| 1 | pre-merge-validation.yml | workflow-health-monitor | Quality | BLOCKING |
| 2 | code-quality-coverage-suite.yml | unified-coverage-agent | Quality | BLOCKING |
| 3 | codeql-fix-verification.yml | codeql-alert-resolution-agent | Security | BLOCKING (HIGH/CRIT) |
| 4 | security-comprehensive-audit.yml | unified-security-scanner | Security | WARNING |
| 5 | comment-review-gate.yml | policy-coach-agent | Governance | BLOCKING |
| 6 | deferral-language-gate.yml | policy-coach-agent | Governance | BLOCKING |
| 7 | ml-tests.yml | ml-validation-suite-agent | Testing | OPTIONAL |
| 8 | rust_swarm_ci.yml | autonomous-test-healer-agent | Testing | OPTIONAL |
| 9 | test-rag.yml | rag-module-management-agent | Testing | OPTIONAL |

**All other workflows are archived in `.github/workflows/archived/` with recovery procedures.**

---

## 2. Governance Rules by Context

### 2.1 For PR Authors

**Rule 1: Mandatory Pre-Session Review**
- Before making ANY changes, complete the checklist in CODEBASE_AGENCY_POLICY.md §0
- Review all bot comments and maintainer comments (@mbaetiong)
- Address all failing CI checks

**Rule 2: Commit Message Standards**
- No deferral language ("will fix later", "pre-existing", "out of scope")
- Reference the issue/task by number
- Explain the reasoning behind changes

**Rule 3: WEC Checklist**
- PR body MUST include Workflow Execution Checklist
- Check boxes for workflows that apply to your change
- All checked workflows must pass before merge

**Rule 4: Approval Gate**
- If you modify sensitive files (workflows, security, requirements), @mbaetiong approval required
- If you modify other files, auto-approved once CI green

### 2.2 For Workflow Authors

**Rule 1: Path-Based Triggers**
- Use `paths:` filter to only run when relevant files change
- This minimizes runner costs and speeds up unrelated PRs

**Rule 2: Conditional Job Isolation**
- Use `if: contains(github.event.head_commit.modified, '.py')` patterns
- Avoid running Rust jobs on Python-only changes
- Avoid running ML tests if only docs changed

**Rule 3: Job Dependencies**
- Define `needs:` correctly to enable parallelization
- Phase 1 (linting, type checks) → Phase 2 (tests) → Phase 3 (merge gate)
- Don't make Phase 1 wait for Phase 2

**Rule 4: Validation & Remediation**
- If validation fails, provide clear remediation steps
- Link to relevant documentation
- Suggest automated fixes where possible

### 2.3 For Maintainers (@mbaetiong)

**Rule 1: Ownership Gate**
- Review all PRs modifying `.github/workflows/` (governance gate)
- Review all PRs modifying `security/` (security gate)
- Review all PRs modifying `requirements/lock.txt` (dependency gate)

**Rule 2: Comment Addressing**
- All agent comments must be substantively addressed by PR author
- Use CODEBASE_AGENCY_POLICY.md §0a for enforcement
- "comment-review-gate.yml" CI job blocks merge if comments unaddressed

**Rule 3: Health Monitoring**
- Monitor `.codex/WORKFLOW_HEALTH_DASHBOARD.json` for RED alerts
- Escalate to specialized agents if needed (ci-health-alert-agent, etc.)
- Authorize Phase 4D-4H continuation work

---

## 3. Compliance Requirements Checklist

### 3.1 REQ-4: Accountability Report (AGENT_ACCOUNTABILITY_REPORT.md)

**Requirement:**
- Every agent session must be logged in AGENT_ACCOUNTABILITY_REPORT.md
- Entry must include: Session timestamp, status, agents used, outcomes

**Verification:**
```bash
# Check if current commit touches accountability report
git diff HEAD~1 -- docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | grep -q "+" && echo "✅ PASS" || echo "❌ FAIL"
```

**Auto-Fix:**
- Script: `python scripts/ci/session_wrapup_autofix.py --fix-accountability`
- Effect: Appends Phase 4C session entry to AGENT_ACCOUNTABILITY_REPORT.md

### 3.2 REQ-5: Changelog (CHANGELOG.md)

**Requirement:**
- Every significant change must be documented in CHANGELOG.md
- Entry must include: Feature name, impact, metrics, reference to related PRs/issues

**Verification:**
```bash
# Check if current commit touches CHANGELOG.md
git diff HEAD~1 -- CHANGELOG.md | grep -q "+" && echo "✅ PASS" || echo "❌ FAIL"
```

**Auto-Fix:**
- Script: `python scripts/ci/session_wrapup_autofix.py --fix-changelog`
- Effect: Appends Phase 4C entry to CHANGELOG.md with all deliverables

### 3.3 REQ-14: Governance Pattern Documentation

**Requirement:**
- Document all recurring violation patterns
- Configure escalation triggers for each pattern
- Review & update quarterly

**Verification:**
```bash
# Check AGENT_ACCOUNTABILITY_REPORT.md for pattern entries
grep "Recurring violation pattern" docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | wc -l
# Should be ≥3 documented patterns
```

**Patterns Documented in Phase 4:**

| Pattern | Frequency | Escalation | Documented In |
|---------|-----------|-----------|---|
| Deferral Language | >5 in 30 days | Increase gate strictness | PHASE_4_GOVERNANCE_MATRIX.md §8 |
| Coverage Regression | >3 in 30 days | Lower threshold + alert | HEALTH_DASHBOARD_CONFIG.md |
| Unaddressed Comments | >2 in 30 days | Enforce via comment-review-gate | CODEBASE_AGENCY_POLICY.md §0a |
| CodeQL Alerts | >10 in 30 days | Emergency security review | PHASE_4_GOVERNANCE_MATRIX.md §5 |

---

## 4. Health Monitoring & Alerting

### 4.1 Understanding Health Metrics

The health dashboard tracks **12 key metrics**:

```
1. Workflow Success Rate         — % of workflows that complete successfully
2. Avg Workflow Duration         — Time to complete (target ≤25 min)
3. CodeQL Alert Volume           — Active security alerts
4. Test Pass Rate                — % of tests that pass
5. Code Coverage                 — % of code covered by tests
6. Secret Detections             — Count of exposed secrets found
7. Dependency Vulnerabilities    — Active unpatched vulnerabilities
8. CI Failure Rate               — % of workflows that fail
9. Deployment Success Rate       — % of releases that complete
10. Performance (p99 latency)    — Max response time at 99th percentile
11. Cost per Workflow            — Runner hours × hourly rate
12. Agent Success Rate           — % of agent tasks that complete successfully
```

**Baseline (Phase 4A):**
```json
{
  "overall_health_score": 96.8,
  "metrics": {
    "workflow_success_rate": 97.2,
    "test_pass_rate": 99.8,
    "code_coverage": 90.2,
    "avg_workflow_duration_minutes": 23.4
  }
}
```

### 4.2 Alert Levels

| Level | Color | Threshold | Action |
|-------|-------|-----------|--------|
| GREEN | 🟢 | Metric ≥ target | Update dashboard only |
| YELLOW | 🟡 | Metric in warn range | Post comment on open PRs |
| RED | 🔴 | Metric below critical | Create GitHub Issue + @mbaetiong notify |

**Example: Workflow Success Rate**
```
Target: 97.0%
GREEN:  ≥90% (all good)
YELLOW: 85%-89% (warning posted)
RED:    <85% (issue created, escalation triggered)
```

### 4.3 Reading the Dashboard

**Location:** `.codex/WORKFLOW_HEALTH_DASHBOARD.json`

```json
{
  "workflow_success_rate": {
    "current_value": 97.2,
    "target": 97.0,
    "trend": "stable",
    "alert_threshold_warning": 90.0,
    "alert_threshold_critical": 85.0,
    "status": "GREEN"
  }
}
```

**Interpretation:**
- ✅ `current_value (97.2%) ≥ target (97.0%)` — metric is healthy
- ✅ `trend: stable` — no concerning changes
- ✅ `status: GREEN` — no alert needed

---

## 5. Troubleshooting Guide

### 5.1 "CI Green Light Not Appearing"

**Symptom:** PR shows all workflow runs succeeded, but no green ✅ on merge button

**Diagnosis:**
1. Check that all 9 master workflows ran (not just subset)
2. Verify WEC checklist in PR body (all required items checked)
3. Look for red 🔴 governance gate comment

**Resolution:**
1. Review governance gate comment for specific blocker
2. Fix the issue (e.g., update coverage, address comment)
3. Push new commit
4. Workflows will re-run automatically

### 5.2 "Archive Recovery Needed"

**Symptom:** Need to restore a deprecated workflow (e.g., legacy-build.yml)

**Steps:**
1. Search archive index: `grep "legacy-build" .codex/WORKFLOW_ARCHIVE_INDEX.json`
2. Get recovery command: `jq '.workflows[] | select(.name == "legacy-build.yml") | .recovery_command' .codex/WORKFLOW_ARCHIVE_INDEX.json`
3. Run: `bash .codex/restore_workflow.sh legacy-build.yml`
4. Verify: `gh workflow view legacy-build.yml --repo Aries-Serpent/_codex_`

**SLA:** <5 minutes from request to operational

### 5.3 "RED Health Alert — What Does It Mean?"

**Symptom:** GitHub Issue created: "🚨 Health Critical: Code Coverage"

**Interpretation:**
- Code coverage dropped below 80% (critical threshold)
- Recent commits likely deleted test coverage without adding tests
- This is a merge-blocking condition

**Resolution:**
1. Identify what files changed (git log --oneline)
2. Add tests for uncovered code
3. Run coverage report: `coverage run -m pytest && coverage report`
4. When coverage ≥88%, merge gate will pass

---

## 6. FAQ

### Q: Can I bypass the governance gate?

**A:** No. The 3-pillar governance gate has no bypass unless explicitly approved by @mbaetiong in writing. If a gate blocks your PR, the remediation is always possible (update code, add tests, address comments, etc.).

### Q: What if a workflow is not in the 9 masters?

**A:** That workflow is archived. Search `.codex/WORKFLOW_ARCHIVE_INDEX.json` and restore it if needed. However, consider whether you really need it — the 9 masters are designed to cover all use cases.

### Q: How often is the health dashboard updated?

**A:** Every 30 minutes, 24/7. See `.codex/PHASE_4_MONITORING_DEPLOYMENT.md` for details on collection cycle.

### Q: What happens if I commit with deferral language?

**A:** `deferral-language-gate.yml` will detect phrases like "will fix later" and block the PR. Reword the commit message and re-push.

### Q: Can I disable a master workflow?

**A:** No. All 9 masters are required for production integrity. If a workflow is problematic, escalate to @mbaetiong instead of disabling.

### Q: Where do I file a governance exception request?

**A:** Create a GitHub Issue with label `governance-exception` and assign to @mbaetiong. Document the reasoning and proposed exception clearly.

---

## 7. Integration Points

### 7.1 For GitHub Actions Authors

When creating new workflows, use these templates and patterns:

**Template 1: Path-Based Trigger**
```yaml
on:
  push:
    branches: [main, 0D_base_, copilot/session-*]
    paths: ['src/**/*.py', 'pyproject.toml']
  pull_request:
    paths: ['src/**/*.py', 'pyproject.toml']
```

**Template 2: Conditional Job Isolation**
```yaml
jobs:
  lint:
    if: contains(github.event.head_commit.modified, '.py')
    runs-on: ubuntu-latest
    # ... job definition
```

**Template 3: Job Dependencies for Parallelization**
```yaml
jobs:
  phase_1:
    runs-on: ubuntu-latest
    # ... fast checks
  
  phase_2:
    needs: [phase_1]  # Wait for phase 1
    runs-on: ubuntu-latest
    # ... comprehensive tests
  
  merge_gate:
    needs: [phase_1, phase_2]  # Wait for both
    if: always()  # Run even if previous failed
    # ... final decision logic
```

### 7.2 For Agent Developers

When implementing agents that interact with governance:

**Integration 1: Read Health Dashboard**
```python
import json

with open('.codex/WORKFLOW_HEALTH_DASHBOARD.json') as f:
    dashboard = json.load(f)
    
coverage = dashboard['metrics']['code_coverage']['current_value']
if coverage < 88:
    print(f"⚠️ Coverage below threshold: {coverage}%")
```

**Integration 2: Write Governance Report**
```python
import json
from datetime import datetime

report = {
    "governance_status": "APPROVED",
    "timestamp": datetime.utcnow().isoformat(),
    "pillars": {
        "owner_approval": {"status": "auto_approved"},
        "config_validation": {"status": "valid"},
        "compliance": {"status": "clean"}
    }
}

with open('artifacts/governance-report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

**Integration 3: Escalate to Specialized Agent**
```bash
# Trigger autonomous-test-healer-agent on test failures
gh issue create \
  --title "Test Failures Detected" \
  --body "cc: @autonomous-test-healer-agent" \
  --label test-failure
```

---

## 8. Updates & Amendments

### 8.1 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-13 | Initial Phase 4 release |

### 8.2 Amendment Process

To propose amendments to Phase 4 governance:

1. **Document Proposed Change**
   - File: `.codex/GOVERNANCE_AMENDMENT_PROPOSAL.md`
   - Include: Rationale, impact analysis, affected workflows

2. **Get Buy-In**
   - Request review from @mbaetiong
   - Post to GitHub Discussions for community input

3. **Implement & Test**
   - Create PR with `governance-amendment` label
   - Update affected documentation
   - Run test cycle

4. **Merge & Communicate**
   - Merge only if @mbaetiong approves
   - Update version in this document
   - Post notice in CHANGELOG.md

---

## 9. Resources & References

### 9.1 Key Documents

- **Governance Matrix:** `.codex/PHASE_4_GOVERNANCE_MATRIX.md` (20 KB) — All 9 workflows documented
- **AI Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` — Mandatory for all agents
- **WEC Items:** `.codex/WEC_CANONICAL_ITEMS.md` — Workflow checklist
- **Health Dashboard:** `.codex/WORKFLOW_HEALTH_DASHBOARD.json` — Live metrics
- **Archive Manifest:** `.codex/PHASE_4_ARCHIVE_MANIFEST.md` — Recovery procedures

### 9.2 GitHub Actions Status

```bash
# List all active workflows
gh workflow list --repo Aries-Serpent/_codex_

# Get status of 9 masters
for wf in pre-merge-validation comment-review-gate deferral-language-gate code-quality-coverage-suite codeql-fix-verification; do
  gh workflow view "$wf.yml" --repo Aries-Serpent/_codex_ --json status
done
```

### 9.3 Help & Support

- **For governance questions:** File issue with `governance-question` label
- **For workflow help:** Mention `@workflow-health-monitor`
- **For compliance questions:** Mention `@policy-coach-agent`
- **For security questions:** Mention `@codeql-alert-resolution-agent`

---

**END OF GOVERNANCE DOCUMENTATION**

*Created: 2026-07-13 | Status: Active | Authority: @mbaetiong | Next Review: 2026-10-13*
