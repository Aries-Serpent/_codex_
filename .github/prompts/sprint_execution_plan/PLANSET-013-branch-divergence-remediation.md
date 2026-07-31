# PLANSET-013: Complete Remediation of Automated Workflow Branch Divergence
> **🤖 GITHUB COPILOT: This is an actionable task prompt. Begin implementation immediately.**
>
> **Template Version:** 2.0.0 (Autonomous Iteration)
> **Last Updated:** 2026-07-31
> **Status:** Ready for Copilot Execution
> **Autonomy Level:** Self-Healing, Self-Troubleshooting, Self-Iterating

---

## 🎯 COPILOT INSTRUCTION: START HERE

**@workspace Execute this task using the following protocol:**

1. **READ** the entire prompt to understand context and requirements
2. **CHECK** prerequisites and generate sub-prompts if dependencies missing
3. **IMPLEMENT** each step sequentially with validation after each
4. **TEST** implementation continuously using provided commands
5. **SELF-CORRECT** if validation fails (up to 5 attempts)
6. **VERIFY** all acceptance criteria are met before marking complete

**Execution Mode:** Autonomous with human oversight  
**Expected Duration:** Large: 1-2 phases / 5-10 iterations  
**Success Criteria:** All acceptance criteria checked ✅

---

## Metadata

```yaml
task_id: "PLANSET-013"
priority: "P0"
phase: "3"
phase_name: "Autonomy → Excellence"
effort_estimate: "Large: 1-2 phases"
sprint_week: "Pre-commit 32"
dependencies:
  - "PR #5412 merged (0D_base_ → main)"
  - "Branches aligned (issue #5395 closed or stable)"
  - "0D_base_ branch present"
blocks:
  - "None"
capability_impact:
  - "CI/CD reliability"
  - "Branch governance"
  - "Autonomous self-healing"
related_gaps:
  - "Branch divergence false-critical alerts (#5395)"
  - "Automated writers bypass staging chain"
autonomous_features:
  - "Self-validation with actionlint + dry-run divergence monitor"
  - "Self-diagnosis via compliance-gate failures"
  - "Self-correction through iterative workflow edits"
  - "Self-verification against acceptance criteria"
  - "Self-expansion: generate prerequisite prompts for missing actions"
iteration_protocol:
  max_attempts: 5
  validation_frequency: "After each implementation step"
  fallback_strategy: "Documented in Troubleshooting section"
  expansion_triggers:
    - "Missing prerequisite composite action"
    - "Workflow syntax error from actionlint"
    - "Divergence monitor still reports codeleak_count > 0"
```

---

## Context

### Current State

**Problem Statement:**
Automated workflows commit generated artifacts directly to `main`, bypassing the repository's staging-chain model (`sub-PR → 0D_base_ → main`). This causes the divergence monitor to flag benign auto-generated commits as CODE-LEAK, producing spurious CRITICAL alerts and steadily widening the gap between `main` and `0D_base_`.

**Audit Evidence:**
- **Issue:** [#5395](https://github.com/Aries-Serpent/_codex_/issues/5395)
- **PR:** [#5412](https://github.com/Aries-Serpent/_codex_/pull/5412) — branches aligned, but implementation incomplete
- **Culprit workflow:** `.github/workflows/phase-12-hourly-monitoring.yml`
- **Commit pattern:** `docs(phase-12): Hourly checkpoint N - 2026-07-...`
- **File written:** `.codex/PHASE_12_HOURLY_CHECKPOINT_LOG_2026_07_17.md`
- **Divergence severity:** CRITICAL (72 commits on `main` not in `0D_base_`)

**Files/Modules Affected:**
```
.github/workflows/phase-12-hourly-monitoring.yml
.github/workflows/codebase-health-sweep.yml
.github/workflows/quality-metrics-collection.yml
.github/workflows/forward-sync-autogen.yml
.github/workflows/branch-divergence-monitor.yml
.github/actions/resolve-push-target/action.yml
.github/actions/commit-to-staging-chain/action.yml          # NEW
.github/workflows/staging-chain-compliance-gate.yml         # NEW
.codex/workflow-exceptions.yml                              # NEW
scripts/ci/check_workflow_staging_compliance.py             # NEW
```

### Target State

**Desired Outcome:**
Every workflow that writes to the repository either:
1. Routes its commits through the deepest available staging branch via `./.github/actions/resolve-push-target`, or
2. Is explicitly registered as a legitimate exception in `.codex/workflow-exceptions.yml`.

High-frequency monitoring logs are moved out of git history into workflow artifacts. The divergence monitor correctly classifies remaining generated commits, and the compliance gate blocks non-compliant workflow merges.

**Success Metrics:**
- `branch-divergence-monitor.yml` dry-run reports `codeleak_count=0` for 3 consecutive scheduled runs.
- `actionlint .github/workflows/*.yml` reports 0 errors.
- 100% of active workflows with `contents: write` pass the staging-chain compliance gate or have an exception entry.
- `phase-12-hourly-monitoring.yml` produces zero per-hour commits to git.

**Capability Improvement:**
- CI/triage noise: CRITICAL → healthy
- Branch governance: manual enforcement → automated enforcement

---

## Prerequisites

**Required Before Starting:**
- [x] PR #5412 merged and `0D_base_` aligned with `main`
- [ ] Issue #5395 triaged and understood
- [ ] Permission to create new composite actions and workflows

**Knowledge Requirements:**
- GitHub Actions composite actions
- The repository's existing `resolve-push-target` algorithm
- `actionlint` workflow validation
- Python YAML parsing (for compliance checker)

**Tools Required:**
- `actionlint`
- `yq` or `python-yaml`
- GitHub CLI (`gh`)
- repository write token (`CODEX_MASTER_KEY` or fallback)

---

## Implementation Guide

### Step 1: Create the `commit-to-staging-chain` Composite Action

**Objective:** Make the compliant path the easiest path for workflow authors.

**Actions:**
1. Create `.github/actions/commit-to-staging-chain/action.yml`.
   ```yaml
   name: Commit to Staging Chain
   description: |
     Resolve the deepest staging branch, stage files, commit, rebase onto the
     latest target, and push. Falls back to the current branch only if no
     integration branch is active.
   inputs:
     message:
       description: 'Commit message first line (must include [skip ci])'
       required: true
     files:
       description: 'Space-separated list of files/paths to commit'
       required: true
   outputs:
     target_branch:
       description: 'Branch the commit was pushed to'
       value: ${{ steps.resolve.outputs.branch }}
   runs:
     using: composite
     steps:
       - name: 🔀 Resolve push target
         id: resolve
         uses: ./.github/actions/resolve-push-target
       - name: 📦 Stage, commit, and push
         shell: bash
         env:
           TARGET: ${{ steps.resolve.outputs.branch }}
           MESSAGE: ${{ inputs.message }}
           FILE_LIST: ${{ inputs.files }}
         run: |
           set -euo pipefail
           git config user.name "github-actions[bot]"
           git config user.email "github-actions[bot]@users.noreply.github.com"
           git fetch origin "$TARGET" --depth=5 || true
           git checkout "$TARGET" || git checkout -b "$TARGET"
           for f in $FILE_LIST; do
             mkdir -p "$(dirname "$f")"
             git add "$f" || true
           done
           git diff --cached --quiet && { echo "No changes to commit"; exit 0; }
           git commit -m "$MESSAGE"
           git pull --rebase --autostash origin "$TARGET" || {
             echo "⚠️ Rebase failed — resetting to latest $TARGET and re-applying"
             git rebase --abort 2>/dev/null || true
             git fetch origin "$TARGET" --depth=5
             git reset --hard origin/"$TARGET"
             git cherry-pick HEAD@{1} --no-commit || {
               echo "❌ Could not re-apply changes"
               exit 1
             }
             git commit -m "$MESSAGE (post-rebase retry)"
           }
           git push origin "HEAD:${TARGET}"
           echo "target_branch=${TARGET}" >> "$GITHUB_OUTPUT"
   ```
2. Validate syntax with `actionlint .github/actions/commit-to-staging-chain/action.yml`.

**Validation:**
```bash
actionlint .github/actions/commit-to-staging-chain/action.yml
```

**Expected Output:**
```text
(no output)
```

---

### Step 2: Migrate `phase-12-hourly-monitoring.yml` Off `main`

**Objective:** Stop the hourly divergence driver.

**Actions:**
1. Open `.github/workflows/phase-12-hourly-monitoring.yml`.
2. Replace the direct `git add / commit / push` logic with the composite action.
3. Change the commit subject to include a recognized auto-gen marker, e.g.:
   ```text
   chore(autosync): phase-12 hourly checkpoint [skip ci]
   ```
4. Optional but recommended: move the checkpoint log from `.codex/*.md` to workflow artifacts. If business requirements require a committed summary, reduce frequency to once per day and route through `commit-to-staging-chain`.

**Validation:**
```bash
actionlint .github/workflows/phase-12-hourly-monitoring.yml
```

**Expected Output:**
```text
(no output)
```

---

### Step 3: Route `codebase-health-sweep.yml` Through the Staging Chain

**Objective:** Eliminate the `sweep-main` job's direct pushes to `main`.

**Actions:**
1. In `sweep-main`:
   - Add `uses: ./.github/actions/resolve-push-target`.
   - Replace the final `git push origin HEAD:refs/heads/main` with `uses: ./.github/actions/commit-to-staging-chain`.
2. Keep the `sweep-staging` job as-is (it already targets `0D_base_`).
3. Ensure commit subject remains: `fix(ci): nightly codebase health sweep — main [skip ci]`.

**Validation:**
```bash
actionlint .github/workflows/codebase-health-sweep.yml
```

---

### Step 4: Route `quality-metrics-collection.yml` Through the Staging Chain

**Objective:** Stop `publish-metrics` from pushing `.reports/` snapshots directly to `main`.

**Actions:**
1. In the `publish-metrics` job:
   - Add `uses: ./.github/actions/resolve-push-target` before the commit step.
   - Replace `git commit` + `git push` with `uses: ./.github/actions/commit-to-staging-chain`.
2. Ensure the commit subject includes `[skip ci]`.

**Validation:**
```bash
actionlint .github/workflows/quality-metrics-collection.yml
```

---

### Step 5: Expand the Auto-Gen Classifier in `branch-divergence-monitor.yml`

**Objective:** Recognize phase-12 and similar generated commits even if the routing fix is delayed.

**Actions:**
1. Locate the `case "$SUBJECT" in ... esac` block in the `measure` step.
2. Add the following patterns:
   ```bash
   *"[skip ci]"*|*"[automated]"*|*"chore(vars)"*|\
   *"chore(phase-3)"*|*"chore(autosync)"*|*"chore(phase-12)"*|\
   *"docs(phase-12)"*|*"🧠 Update"*)
   ```
3. Add a file-based fallback classifier after the subject check:
   ```bash
   # Fallback: all changed files match known auto-gen globs
   if [ "$IS_AUTOGEN" = "false" ] && [ "$AUTHOR" = "github-actions[bot]" ]; then
     AUTO_GEN_GLOBS='^(\.codex/PHASE_12_.*\.md|\.codex/agent_context\.json|\.codex/cognitive_brain/.*|\.codex/embeddings/codex_index_meta\.json|docs/admin/GITHUB_VARIABLES_MASTER_GUIDE\.md|docs/admin/variable_audit_latest\.md|requirements/.*\.txt)$'
     NON_AUTOGEN=$(echo "$CHANGES_OUTPUT" | grep -vE "$AUTO_GEN_GLOBS" || true)
     [ -z "$NON_AUTOGEN" ] && IS_AUTOGEN=true
   fi
   ```

**Validation:**
```bash
actionlint .github/workflows/branch-divergence-monitor.yml
```

---

### Step 6: Expand `forward-sync-autogen.yml` File Allow-List

**Objective:** Ensure the safety net covers all known generated files.

**Actions:**
1. Add to both `on.push.paths:` and the `FILES=(...)` arrays:
   ```yaml
   - .codex/PHASE_12_HOURLY_CHECKPOINT_LOG_*.md
   - .codex/PHASE_12_EXECUTION_DASHBOARD_LIVE.md
   - .codex/PHASE_12_INCIDENT_LOG_*.md
   - .reports/metrics/snapshots/**             # if still committing metrics
   ```
2. Add a comment warning that `paths:` and `FILES=(...)` must be kept in sync.

**Validation:**
```bash
actionlint .github/workflows/forward-sync-autogen.yml
```

---

### Step 7: Create the Staging-Chain Compliance Gate

**Objective:** Block merges of workflows that can push but do not route through the staging chain.

**Actions:**
1. Create `.github/workflows/staging-chain-compliance-gate.yml`.
   ```yaml
   name: Staging-Chain Compliance Gate
   on:
     pull_request:
       paths: ['.github/workflows/**']
     push:
       branches: [0D_base_, main]
       paths: ['.github/workflows/**']
   jobs:
     check-push-routing:
       runs-on: ubuntu-latest
       permissions:
         contents: read
         pull-requests: write
       steps:
         - uses: actions/checkout@v5
         - uses: actions/setup-python@v5
           with:
             python-version: '3.12'
         - name: Install dependencies
           run: pip install pyyaml
         - name: Check workflow staging-chain compliance
           run: python scripts/ci/check_workflow_staging_compliance.py
   ```
2. Create `scripts/ci/check_workflow_staging_compliance.py`:
   - Walk `.github/workflows/*.yml`.
   - Skip workflows listed in `.codex/workflow-exceptions.yml`.
   - Skip workflows without `contents: write` or without any push/commit step.
   - Flag workflows that do not reference `./.github/actions/resolve-push-target` or `./.github/actions/commit-to-staging-chain`.
   - Exit non-zero and print a GitHub Actions annotation for each violation.

**Validation:**
```bash
python scripts/ci/check_workflow_staging_compliance.py
```

**Expected Output:**
```text
✅ All committable workflows route through the staging chain or are exempt.
```

---

### Step 8: Create the Workflow Exceptions Registry

**Objective:** Document legitimate `main`-pushing workflows so the gate can approve them.

**Actions:**
1. Create `.codex/workflow-exceptions.yml`:
   ```yaml
   exceptions:
     - workflow: release.yml
       reason: Creates GitHub releases from tags; does not alter src/ or default branch history.
       allowed_push_targets: [tags]
     - workflow: release-to-pypi.yml
       reason: Publishes release artifacts to PyPI; no repository branch writes.
       allowed_push_targets: [pypi]
     - workflow: pages-mkdocs.yml
       reason: Deploys to GitHub Pages branch (gh-pages), not main or 0D_base_.
       allowed_push_targets: [gh-pages]
     - workflow: workflow-restore.yml
       reason: Emergency recovery workflow; explicitly bypasses staging chain.
       allowed_push_targets: [main]
       requires_issue_reference: true
   ```
2. Update `check_workflow_staging_compliance.py` to read this file.

**Validation:**
```bash
python -c "import yaml; print(yaml.safe_load(open('.codex/workflow-exceptions.yml')))"
```

---

### Step 9: Add Compliance Gate Tests

**Objective:** Ensure the gate detects known bad patterns and approves known good patterns.

**Actions:**
1. Create `tests/ci/test_staging_chain_compliance.py` with cases for:
   - Workflow with `contents: write` and no resolve-push-target → fail.
   - Workflow with `contents: read` only → pass.
   - Workflow with `resolve-push-target` → pass.
   - Workflow listed in exceptions → pass.
   - Archived / disabled workflows → skip.
2. Run tests.

**Validation:**
```bash
pytest tests/ci/test_staging_chain_compliance.py -v
```

**Expected Output:**
```text
4 passed
```

---

### Step 10: Run Dry-Run Divergence Monitor and Merge

**Objective:** Confirm the fix before promoting to `main`.

**Actions:**
1. Push all changes to a feature branch targeting `0D_base_`.
2. Open a PR against `0D_base_`.
3. Run `branch-divergence-monitor.yml` with `dry_run=true`.
4. Confirm `codeleak_count=0` and `severity` is healthy or low.
5. Merge to `0D_base_`.
6. Allow one scheduled run of `branch-divergence-monitor.yml` to auto-correct any remaining auto-gen divergence.
7. Open/merge promotion PR `0D_base_ → main`.

**Validation:**
```bash
gh workflow run branch-divergence-monitor.yml -f dry_run=true --repo Aries-Serpent/_codex_
```

**Expected Output:**
```text
severity=healthy
behind_count=0
codeleak_count=0
```

---

## Testing Requirements

### Unit Tests

**Test Cases Required:**
1. **Test Name:** `test_workflow_without_routing_fails`
   - **Purpose:** Verify compliance gate flags an un-routed committable workflow.
   - **Location:** `tests/ci/test_staging_chain_compliance.py`
2. **Test Name:** `test_workflow_with_routing_passes`
   - **Purpose:** Verify compliance gate approves a workflow using `resolve-push-target`.
3. **Test Name:** `test_exception_workflow_passes`
   - **Purpose:** Verify workflows in `.codex/workflow-exceptions.yml` are skipped.
4. **Test Name:** `test_read_only_workflow_passes`
   - **Purpose:** Verify workflows without `contents: write` are ignored.

### Integration Tests

**Test Cases Required:**
1. Run `phase-12-hourly-monitoring.yml` manually and confirm the push target is `0D_base_` (or a sub-PR) and commit subject contains `[skip ci]`.

### Validation Commands

```bash
# Syntax-check all modified/new workflows
actionlint .github/workflows/phase-12-hourly-monitoring.yml \
  .github/workflows/codebase-health-sweep.yml \
  .github/workflows/quality-metrics-collection.yml \
  .github/workflows/branch-divergence-monitor.yml \
  .github/workflows/forward-sync-autogen.yml \
  .github/workflows/staging-chain-compliance-gate.yml

# Run compliance checker locally
python scripts/ci/check_workflow_staging_compliance.py

# Run unit tests
pytest tests/ci/test_staging_chain_compliance.py -v

# Dry-run divergence monitor
gh workflow run branch-divergence-monitor.yml -f dry_run=true --repo Aries-Serpent/_codex_
```

**Expected Coverage:**
- Minimum: 80% line coverage for new Python scripts
- Target: 90%+ line coverage

---

## Acceptance Criteria

**Definition of Done:**
- [x] All implementation steps completed
- [ ] All tests passing (unit + integration)
- [ ] Code coverage meets minimum threshold (≥80%)
- [ ] Documentation updated (this planset, CHANGELOG, AGENT_ACCOUNTABILITY_REPORT)
- [ ] Pre-commit hooks pass (linting, formatting, type checking)
- [ ] CI pipeline passes all checks
- [ ] `branch-divergence-monitor.yml` dry-run reports `codeleak_count=0`
- [ ] No new security vulnerabilities introduced
- [ ] Manual validation completed
- [ ] Promotion PR `0D_base_ → main` opened and merged

**Verification Checklist:**
- [ ] **Functional:** Automated writers route through the staging chain
- [ ] **Performance:** No significant Actions-minute increase
- [ ] **Security:** No secrets or PAT misuse introduced
- [ ] **Documentation:** Changes documented in CHANGELOG.md and AGENT_ACCOUNTABILITY_REPORT.md
- [ ] **Tests:** Compliance gate has passing unit tests
- [ ] **Backward Compatibility:** Existing exception workflows continue to function

---

## Validation & Verification

### Automated Validation

```bash
# 1. Syntax-check workflows
actionlint .github/workflows/*.yml

# 2. Run compliance checker
python scripts/ci/check_workflow_staging_compliance.py

# 3. Run unit tests
pytest tests/ci/test_staging_chain_compliance.py -v

# 4. Run dry-run divergence monitor
gh workflow run branch-divergence-monitor.yml -f dry_run=true --repo Aries-Serpent/_codex_
```

### Manual Validation

**Steps:**
1. Trigger `phase-12-hourly-monitoring.yml` manually.
   - **Action:** `gh workflow run phase-12-hourly-monitoring.yml --repo Aries-Serpent/_codex_`
   - **Expected:** Job summary shows push target is `0D_base_` and no direct `git push origin HEAD:main`.

2. Wait for the next scheduled `branch-divergence-monitor.yml` run.
   - **Action:** Inspect the updated issue #5395 or the Actions run summary.
   - **Expected:** `codeleak_count=0` and `severity` is not CRITICAL.

3. Verify compliance gate status on the remediation PR.
   - **Action:** Check the PR checks tab.
   - **Expected:** `Staging-Chain Compliance Gate` is green.

### Regression Testing

```bash
# Ensure existing functionality still works
pytest tests/ -m "not slow" --maxfail=1

# Smoke test the new composite action in isolation
act -j check-push-routing -W .github/workflows/staging-chain-compliance-gate.yml
```

---

## Rollback Plan

**If Implementation Fails:**

1. **Revert Changes:**
   ```bash
   git revert --no-commit <remediation-pr-merge-sha>
   git commit -m "revert: rollback PLANSET-013 remediation"
   ```

2. **Restore Previous State:**
   - Restore the original `phase-12-hourly-monitoring.yml` commit/push logic.
   - Disable the new `staging-chain-compliance-gate.yml` by renaming to `.disabled` if it blocks merges.

3. **Verify Stability:**
   ```bash
   actionlint .github/workflows/*.yml
   python scripts/ci/check_workflow_staging_compliance.py
   gh workflow run branch-divergence-monitor.yml -f dry_run=true --repo Aries-Serpent/_codex_
   ```

**Mitigation Strategies:**
- If phase-12 migration breaks, fall back to routing the existing `.md` commits through `resolve-push-target` instead of removing them from git.
- If the compliance gate has false positives, add the workflow to `.codex/workflow-exceptions.yml` temporarily while fixing the root cause.

---

## 🤖 Autonomous Iteration Protocol

### Prompt Expansion System

**Automatic Prerequisite Detection:**
If `resolve-push-target` is missing or malformed, generate a sub-prompt to fix or recreate it before proceeding with Step 1.

If `actionlint` is not installed, generate a sub-prompt to add it to the development environment.

### Self-Validation Loop

After each step:
1. Run `actionlint` on changed workflow files.
2. Run `python scripts/ci/check_workflow_staging_compliance.py`.
3. Run unit tests if scripts were modified.
4. If any check fails, diagnose, fix, and rerun. Max 5 iterations per step.

### Troubleshooting Decision Matrix

| Issue Type | Auto-Fix Available? | Action | Escalation Threshold |
|------------|---------------------|--------|---------------------|
| actionlint syntax error | ⚠️ Partial | Fix YAML/escaping | After 2 attempts |
| Compliance gate false positive | ✅ | Add temporary exception + ticket | After 1 attempt |
| Divergence still non-zero | ❌ | Investigate remaining uncaught workflow | Immediate human review |
| resolve-push-target API failure | ❌ | Check token/GitHub API status | Immediate |

---

## Related Audit Artifacts

**Primary References:**
- **Investigation Report:** `.github/reports/branch-divergence-investigation-5395.md`
- **Issue:** [#5395](https://github.com/Aries-Serpent/_codex_/issues/5395)
- **PR:** [#5412](https://github.com/Aries-Serpent/_codex_/pull/5412)
- **Runbook:** `.codex/docs/BRANCH_DIVERGENCE_PREVENTION.md`
- **Integration Branch Model:** `.codex/docs/INTEGRATION_BRANCH_MODEL.md`

**Supporting References:**
- **resolve-push-target action:** `.github/actions/resolve-push-target/action.yml`
- **forward-sync-autogen workflow:** `.github/workflows/forward-sync-autogen.yml`
- **branch-divergence-monitor workflow:** `.github/workflows/branch-divergence-monitor.yml`

---

## Progress Tracking

**Status:** `[x] Not Started | [ ] In Progress | [ ] Testing | [ ] Complete`

**Linked PR:** [#5412](https://github.com/Aries-Serpent/_codex_/pull/5412)
**Linked Issue:** [#5395](https://github.com/Aries-Serpent/_codex_/issues/5395)

---

## Conclusion

This planset transforms the branch-divergence problem from a recurring incident into a governed, self-healing system: a reusable routing action, a compliance gate that enforces it, an accurate auto-gen classifier, and a migration of high-frequency logs out of git history. Execute the steps in order, validate after each, and promote through `0D_base_ → main`.
