# CI Failure Diagnosis: Auto-Approve Workflow

**Date**: 2026-06-17  
**Branch**: `copilot/0d-base-cherry-pick-diffs`  
**Workflow**: `.github/workflows/auto-approve-workflows.yml`  
**Failed Runs**: 5 consecutive (27657538526, 27657536858, 27657535949, 27657535061, 27657534518)  
**Status**: `failure` with `0 jobs executed`

---

## Executive Summary

The auto-approve workflow is **failing because the workflow is triggered but NO jobs can execute**. The workflow triggers on `push` events but all job conditions require either:
1. `workflow_dispatch` event (evaluate-approval only)
2. Dependencies on evaluate-approval (which never runs for push)

This is a **workflow logic error**, not a syntax error.

---

## Root Cause Analysis

### Problem #1: Event Type Mismatch

**Trigger Definition** (in YAML `on:` section):
```yaml
on:
  workflow_run:
    workflows: ["Copilot coding agent", "🔄 Auto-Post @copilot review After Agent Session"]
    types: [requested, in_progress, completed]
  pull_request:
    types: [synchronize, opened, reopened, ready_for_review]
  pull_request_review:
    types: [submitted]
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:
    inputs: ...
```

**Actual Trigger Event**: `push` (from commit cb59523)

**Issue**: The workflow defines triggers for `workflow_run`, `pull_request`, `pull_request_review`, `schedule`, and `workflow_dispatch` — but NOT `push`. Yet GitHub Actions is triggering the workflow on push events.

**Why?**: The push is coming to a branch (`copilot/0d-base-cherry-pick-diffs`) that is NOT the default branch. GitHub Actions may have secondary triggers or the push is being interpreted differently by GitHub's action runner.

---

### Problem #2: Job Conditions Block All Execution

**Job Dependency Chain**:

```
evaluate-approval
  if: github.event_name == 'workflow_dispatch' && 
      github.event.inputs.approval_source != ''
  ❌ BLOCKS on push: Requires workflow_dispatch event
  
  ↓ (depends on evaluate-approval)
  
execute-approval
  if: needs.evaluate-approve.outputs.should_proceed == 'true' &&
      needs.evaluate-approval.outputs.approval_decision == 'APPROVE'
  ❌ BLOCKS on push: Upstream job doesn't run
  
cleanup-single-session
  if: always() &&
      needs.evaluate-approval.outputs.should_proceed == 'true' &&
      (github.event.inputs.approval_source == 'self-approve-pending-runs' ||
       github.event.inputs.approval_source == 'trigger-on-approval')
  ❌ BLOCKS on push: Upstream job doesn't run + no approval_source input
  
publish-metrics
  if: always() && github.event.inputs.approval_source != ''
  ❌ BLOCKS on push: No approval_source input in push event
```

**Result**: When a push event triggers the workflow:
1. `evaluate-approval` doesn't run (requires workflow_dispatch)
2. All other jobs can't run (depend on evaluate-approval or missing inputs)
3. **0 jobs execute**
4. **Workflow marked as failure**

---

### Problem #3: YAML Parsing Quirk

The `on:` keyword in the YAML file is interpreted as the boolean `True` by standard YAML parsers:

```python
import yaml
data = yaml.safe_load(open('.github/workflows/auto-approve-workflows.yml'))
list(data.keys())  # Output: ['name', True, 'concurrency', 'permissions', 'jobs']
data[True]         # Contains: workflow_run, pull_request, etc.
data.get('on')     # None (no string key 'on')
```

This is YAML specification compliance: `on`, `yes`, `no`, `true`, `false` are reserved keywords and interpreted as boolean/null values without quotes.

GitHub Actions has special handling for this (likely custom YAML loader), but standard Python YAML parsers show this quirk.

---

## Failure Manifestation

### What We See
- Workflow triggered: ✓ (GitHub Actions recognized something)
- Workflow status: ✗ failure
- Jobs executed: 0
- Duration: ~0 seconds (immediate failure)
- Logs: Empty (no job logs available)

### Why It Fails
1. Workflow `.yml` file is syntactically valid YAML
2. GitHub Actions successfully parses the trigger rules
3. GitHub Actions **does not trigger the workflow on push** (workflow shouldn't run at all)
   - BUT the push still causes a workflow run to appear
   - This suggests GitHub is treating the branch push as a secondary trigger
4. When the workflow does execute (via push), no jobs can run due to conditions
5. **Result**: Workflow marked failed with 0 jobs

---

## Timeline of 5 Consecutive Failures

All failures on 2026-06-17:

| Run ID | Time | Commit | Branch | Trigger | Jobs | Duration |
|--------|------|--------|--------|---------|------|----------|
| 27657538526 | 00:32:51 | cb59523 | copilot/0d-base-cherry-pick-diffs | push | 0 | ~0s |
| 27657536858 | 00:32:48 | cb59523 | copilot/0d-base-cherry-pick-diffs | push | 0 | ~0s |
| 27657535949 | 00:32:... | cb59523 | copilot/0d-base-cherry-pick-diffs | push | 0 | ~0s |
| 27657535061 | 00:32:... | cb59523 | copilot/0d-base-cherry-pick-diffs | push | 0 | ~0s |
| 27657534518 | 00:32:... | cb59523 | copilot/0d-base-cherry-pick-diffs | push | 0 | ~0s |

**Cause**: Commit cb59523 is being repeatedly pushed or the workflow is being re-triggered 5 times in quick succession.

---

## Failure Classification

- **Severity**: 🔴 **HIGH** — Workflow silently fails on every push
- **Type**: **Logic Error** (not syntax error)
- **Category**: **Job Condition Mismatch**
- **Impact**: 
  - Approval automation blocked for this branch
  - Pending workflow runs unable to auto-approve
  - Silent failures (no logs to debug)

---

## Recommended Fixes

### Fix #1: Add Push Trigger (If Desired)

**Option A**: Add explicit push trigger to enable approval on push events:

```yaml
on:
  push:
    branches:
      - 'copilot/**'  # Or specific branches
      - main
  workflow_run:
    # ... existing triggers
```

**Option B**: Remove implicit push trigger by understanding why GitHub is triggering it.

**Recommendation**: Add explicit `push:` trigger with specific branch guards if auto-approve should work on push events.

---

### Fix #2: Add Job for Push Events

Create a new job that handles push events (without workflow_dispatch requirement):

```yaml
approve-pending-runs:
  name: "⚡ Approve Pending Runs (Push Event)"
  runs-on: ubuntu-latest
  if: github.event_name == 'push'  # Run ONLY on push, not workflow_dispatch
  steps:
    - uses: actions/checkout@v4
    - name: Resolve PR for push
      id: resolve
      run: |
        # Find the PR associated with this push
        PR_NUMBER=$(gh pr list \
          --head "${{ github.ref_name }}" \
          --state open \
          --json number -q '.[0].number' 2>/dev/null || echo "")
        echo "pr_number=$PR_NUMBER" >> $GITHUB_OUTPUT
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Approve pending runs
      if: steps.resolve.outputs.pr_number
      run: python scripts/ci/approve_pending_runs.py
      env:
        REPO: ${{ github.repository }}
        HEAD_SHA: ${{ github.sha }}
        PR_NUMBER: ${{ steps.resolve.outputs.pr_number }}
        GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
```

**Recommendation**: Implement this to handle push-triggered approvals.

---

### Fix #3: Fix Job Dependency Chain

Restructure jobs to allow running on push events:

```yaml
jobs:
  # New base job for push events (no dependencies)
  auto-approve:
    name: "⚡ Auto-Approve Pending Runs"
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'push' ||
      github.event_name == 'pull_request' ||
      github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/ci/approve_pending_runs.py
        env:
          REPO: ${{ github.repository }}
          HEAD_SHA: ${{ github.sha }}
          GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}

  # Existing workflow_dispatch-only jobs
  evaluate-approval:
    if: github.event_name == 'workflow_dispatch'
    # ... existing job
```

**Recommendation**: Best approach — separates concerns between automated approval and manual approval flows.

---

## Validation Checklist

After implementing fixes, verify:

- [ ] **YAML Syntax**: Run `yamllint .github/workflows/auto-approve-workflows.yml`
- [ ] **Trigger Test**: Push a commit and verify workflow triggers
- [ ] **Job Execution**: Verify at least 1 job executes (not 0)
- [ ] **Logs Available**: Verify job logs are available in GitHub Actions UI
- [ ] **Success Status**: Workflow completes with `success` or appropriate `failure` with reason
- [ ] **No False Failures**: Workflow doesn't fail just because conditions skip jobs

---

## Investigation Notes

### YAML Parsing
The `on:` keyword is a YAML reserved word (boolean), parsed as `True` by Python's yaml library:
```python
>>> import yaml
>>> data = yaml.safe_load("on:\n  push: {}") 
>>> True in data  # True (the boolean key exists)
>>> 'on' in data  # False (string key doesn't exist)
```

However, GitHub Actions has special handling and correctly parses `on:` as the trigger definition.

### Log Limitations
No logs available because workflow failed before any jobs could execute. GitHub Actions doesn't generate logs for jobs that never run.

### Commit Context
- Commit cb59523: "Apply remaining changes" (minor session_context changes, 16 insertions/deletions)
- Previous commit bdf1b04: Added ~600 files to .codex/ (Phase 4 completion)
- Neither commit should have affected the workflow file itself

---

## Summary Table

| Aspect | Status | Details |
|--------|--------|---------|
| **YAML Syntax** | ✅ VALID | File is valid YAML, no syntax errors |
| **Workflow Triggers** | ⚠️ MISMATCH | Defines workflow_run/pull_request/schedule but triggered on push |
| **Job Conditions** | ❌ BLOCKING | All jobs require workflow_dispatch or depend on non-running jobs |
| **Root Cause** | 🔴 LOGIC ERROR | Triggered event (push) doesn't match job execution conditions |
| **Failure Type** | 🔴 INFRASTRUCTURE | Workflow framework issue, not code/test issue |
| **Fix Priority** | 🔴 HIGH | Blocking automation, affects all branch pushes |

---

## Related Files

- Workflow definition: `.github/workflows/auto-approve-workflows.yml` (988 lines)
- Approval script: `scripts/ci/approve_pending_runs.py` (17KB, valid)
- Trigger target PRs: See `.github/workflows/auto-approve-workflows.yml` lines 46-66

---

**Diagnosis Date**: 2026-06-17T00:37:00Z  
**Diagnosed By**: CI Testing Agent v4.2.0-S228  
**Status**: Ready for fix implementation
