# [BROAD-PR-001]: Broad Merge-Readiness Cleanup and Branch Initialization

> **🤖 GITHUB COPILOT: This is an actionable task prompt. Begin implementation immediately.**
>
> **Template Version:** 2.0.0 (Autonomous Iteration)  
> **Last Updated:** 2026-09-26  
> **Status:** Ready for Copilot Execution  
> **Autonomy Level:** Self-Healing, Self-Troubleshooting, Self-Iterating

---

## 🎯 COPILOT INSTRUCTION: START HERE

1. Read the full prompt and the applicable repo policy.
2. Confirm the branch model before editing.
3. Execute the smallest credible broad remediation path and validate after each step.
4. Keep the PR scope honest: broad enough to improve merge readiness, but bounded enough to stay reviewable.
5. Document what remains for subsequent sessions or PRs.

**Execution Mode:** Autonomous with human oversight  
**Expected Duration:** Medium: 3-5 iterations  
**Success Criteria:** All acceptance criteria checked ✅

---

## Metadata

```yaml
 task_id: "BROAD-PR-001"
 priority: "P1"
 phase: "1"
 phase_name: "Foundation"
 effort_estimate: "Medium: 3-5 iterations"
 sprint_week: "Pre-commit 1-5"
 dependencies:
   - "None"
 blocks:
   - "Follow-on broad repo cleanup sessions"
 capability_impact:
   - "Merge readiness"
   - "Branch hygiene"
   - "Governance hygiene"
 related_gaps:
   - "Global backlog and repo-wide residual cleanup"
 autonomous_features:
   - "Self-validation with automated tests"
   - "Self-diagnosis via error pattern matching"
   - "Self-correction through iterative refinement"
   - "Self-verification against acceptance criteria"
 iteration_protocol:
   max_attempts: 5
   validation_frequency: "After each implementation step"
   fallback_strategy: "Documented in Rollback Plan"
   expansion_triggers:
     - "Missing prerequisite detected"
     - "Unexpected dependency discovered"
   prompt_generation: "Automatic sub-prompt creation for blocking issues"
```

---

## Context

### Current State

**Problem Statement:**
This repo currently has a global backlog unrelated to the branch. A literal 100/100 score is not achievable via a narrow, branch-local fix alone. The work needed to improve merge readiness is broad, but it must be organized as a credible branch-level remediation initiative rather than a misleading claim that the whole backlog is resolved in one PR.

**Audit Evidence:**
- `.codex/CODEBASE_AGENCY_POLICY.md` mandates comprehensive issue resolution and prohibits deferral language.
- `.codex/INTEGRATION_BRANCH_MODEL.md` confirms the valid repo model is `copilot/session-*` -> `0D_base_` or `0D_base_` -> `main` for direct promotion work.
- `workbench/gap_backlog_prioritized.md` records a large repo-wide backlog, including a gap still marked `In Progress` (`Gap 5: Add coverage gate enforcement`) and a large historical remediation footprint.
- `.codex/auto-fix-diagnostic.json` shows the current branch is green for automation (`status: "GREEN"`, `auto_fixable: 0`), but this does not mean the repo-wide backlog is fully closed in one branch-local PR.
- The current branch being worked on is `copilot/broad-merge-readiness-cleanup`, which is aligned with the repo’s staging model and should remain targeted at `0D_base_` unless this is explicitly converted to a direct promotion PR.

**Files/Modules Affected:**
```
- .codex/CODEBASE_AGENCY_POLICY.md
- .codex/INTEGRATION_BRANCH_MODEL.md
- workbench/gap_backlog_prioritized.md
- .codex/auto-fix-diagnostic.json
- .codex/session_startup_packet.json
- docs/plans/BROAD_MERGE_READINESS_CLEANUP_PLAN.md
```

### Target State

**Desired Outcome:**
Create a clear broad remediation branch/PR path that honestly documents the repo-wide backlog, begins the lowest-risk quality improvements, and preserves a reviewable scope while moving the repo toward merge readiness.

**Success Metrics:**
- Branch strategy matches the repo’s integration model (`copilot/session-*` -> `0D_base_` or `0D_base_` -> `main` when direct promotion PR is active)
- The plan explicitly states that the repo currently has a global backlog unrelated to the branch
- A literal 100/100 score is acknowledged as not achievable via a narrow, branch-local fix alone
- Initial remediation work is started and validated
- Follow-up items are documented for continuation in subsequent sessions or PRs

**Capability Improvement:**
- Merge readiness: branch hygiene + honest backlog triage + initial repo-level remediation

---

## Prerequisites

**Required Before Starting:**
- [x] Repo policy loaded and reviewed
- [x] Branch model reviewed and confirmed
- [x] Current branch state assessed
- [x] Global backlog exhibits a repo-wide residual burden beyond a single branch

**Knowledge Requirements:**
- Familiarity with the repo’s branch model and staging setup
- Ability to distinguish branch-local drift from repo-wide horizontal backlog
- Comfort with low-risk governance and validation fixes

**Tools Required:**
- git
- Python
- repo validation scripts (`auto_fix_common_issues.py`, `session_wrapup_autofix.py`)

---

## Implementation Guide

### Step 1: Confirm branch and target base

**Objective:** Ensure all work follows repo policy and stays on the correct branch path.

**Actions:**
1. Confirm the current branch is `copilot/broad-merge-readiness-cleanup` and that the repo policy requires sub-PR work to target `0D_base_` (or `0D_base_` -> `main` for direct promotion PR mode).
2. Treat the repo’s main integration branch as the correct base for a broad remediation PR.
3. Keep the work reviewable and branch-scoped; do not mis-state a 100/100 fix as achievable in a single patch.

**Validation:**
```bash
git branch --show-current
git status --short --branch
git rev-list --left-right --count HEAD...origin/0D_base_
```

**Expected Output:**
- Current branch is the broad remediation branch
- Base alignment matches the repo model

### Step 2: Establish the broad remediation plan and backlog statement

**Objective:** Encode the honest repo-state narrative and the phased remediation plan.

**Actions:**
1. Create a sprint execution plan following the repo template.
2. Include explicit language that the repo currently has a global backlog unrelated to the branch.
3. State that a literal 100/100 score is not achievable via a narrow, branch-local fix alone.
4. Frame the PR as the start of a broad remediation initiative rather than a fake “complete cleanup.”

**Validation:**
```bash
sed -n '1,220p' docs/plans/BROAD_MERGE_READINESS_CLEANUP_PLAN.md
```

**Expected Output:**
- The plan contains current state, target state, phases, risks, and continuation items

### Step 3: Start the initial, low-risk remediation work

**Objective:** Fix a concrete, safe branch-local issue that improves governance or repo health without overextending scope.

**Actions:**
1. Revert the drift in `.codex/session_startup_packet.json` to the tracked baseline if it was modified during the session.
2. Keep the fix narrowly tied to merge-readiness and governance hygiene.
3. Preserve evidence that the repo’s remaining backlog is broader than the branch and requires staged continuation.

**Validation:**
```bash
git diff -- .codex/session_startup_packet.json
python -m json.tool .codex/session_startup_packet.json >/dev/null
```

**Expected Output:**
- No spurious timestamp churn remains in generated artifacts
- The branch is cleanly aligned to the tracked baseline

### Step 4: Validate repo health and record the remaining work

**Objective:** Capture the honest status after the branch-local remediation begins.

**Actions:**
1. Run the repo’s narrow validation command(s) to ensure the branch remains healthy.
2. Record which issues are already resolved, which remain global backlog items, and what must continue in follow-up sessions.
3. Keep the PR doc explicit about next phases rather than claiming full repo closure.

**Validation:**
```bash
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/session_wrapup_autofix.py --check --pr-number 5634
```

**Expected Output:**
- The validation result is captured, and remaining work is documented as follow-up continuity, not deferral language

---

## Testing Requirements

### Unit Tests

**Test Cases Required:**
1. `startup-packet drift is stable`
   - Purpose: ensure generated branch health artifacts do not drift without an explicit change
   - Location: validated via repo scripts, not a new test file

### Integration Tests

**Test Cases Required:**
1. Branch is on the repo’s integration model and aligned with `0D_base_` / `main` expectations
2. Repo health scripts still run in the current session

### Validation Commands

```bash
# branch + drift status
git status --short --branch
git diff -- .codex/session_startup_packet.json

# repo health / merge-readiness checks
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/session_wrapup_autofix.py --check --pr-number 5634
```

**Expected Coverage:**
- Minimum: branch hygiene and validation script pass
- Target: repo remains in a green, reviewable state for the broad PR

---

## Acceptance Criteria

**Definition of Done:**
- [x] Correct branch model confirmed
- [x] Honest repo-wide backlog statement included
- [x] Literal 100/100 not claimed for a narrow branch-local fix
- [x] Sprint execution plan created using the repo template
- [x] Initial branch-safe remediation started and validated
- [x] Follow-up continuation work documented
- [x] No deferral language used to mask repo-level issues

**Verification Checklist:**
- [x] Functional: branch and plan align with repo policy
- [x] Performance: no broad refactor introduced
- [x] Security: no new secret or credential exposure
- [x] Documentation: branch strategy and backlog are documented
- [x] Tests: validation scripts rerun successfully
- [x] Backward compatibility: no repo-wide behavior changes beyond the branch drift fix and plan artifact

---

## Validation & Verification

### Automated Validation

```bash
python -m json.tool .codex/session_startup_packet.json >/dev/null
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/session_wrapup_autofix.py --check --pr-number 5634
```

### Manual Validation

**Steps:**
1. Confirm the branch is the broad remediation branch
2. Confirm the target base is the staging integration branch or direct promotion branch per repo policy
3. Verify the plan explicitly documents the remaining repo-wide backlog and the non-achievability of a 100/100 local fix

### Regression Testing

```bash
git diff --stat
```

---

## Rollback Plan

**If Implementation Fails:**
1. Revert the drift fix or plan file if the branch is not ready for review
2. Restore the tracked startup packet baseline
3. Re-run the repo validation scripts and adjust the plan to the actual branch state

**Mitigation Strategies:**
- Keep scope constrained to governance + branch hygiene + plan artifacts
- Do not broaden the PR into unrelated system-level refactors
- Continue backlog work in explicit follow-up phases

---

## 🤖 Autonomous Iteration Protocol

**Adaptive Prompt Expansion:**
- If validation fails, diagnose the exact branch drift or policy mismatch before changing scope.
- If repo health scripts report a true blocker in the branch, fix the blocker directly and re-run validation.
- If a wider issue is outside the branch scope, add it to the follow-up tasks section rather than deferring with language that hides responsibility.

**Self-Validation Loop:**
- Validate after each step
- Correct only the specific discovered issue
- Keep the PR narrative honest and reviewable
