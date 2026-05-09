# Workflow Conflict Analysis — PR #4368 / Active Session Impact

> **Generated:** S899-cont · 2026-05-09
> **Author:** Copilot agent (S899)
> **Status:** Fixes applied in this document

---

## Executive Summary

The "8 pending workflows" that repeatedly appear after each approval are caused by
**two overlapping `pull_request` event types** firing for every push+description-update cycle,
compounded by **workflow bot commits that lack `[skip ci]`**, which re-trigger the full
gating suite. Four fixes were applied in this session; two pre-existing patterns require
admin attention.

---

## Root Cause Chain

```
report_progress() ──► git push (new SHA)
                   │
                   ├──► pull_request: synchronize ──► pr-followup-generator.yml runs
                   │                                      │
                   │                                      └──► git commit "chore: Generate..."
                   │                                               (NO [skip ci] ← BUG #1)
                   │                                               │
                   │                                               └──► pull_request: synchronize
                   │                                                    ──► 4 gating workflows (set A)
                   │
                   └──► PR description update ──► pull_request: edited
                                                  ──► 4 gating workflows (set B)

Total = 8 pending (set A + set B)
```

**Each approval of the 8** runs `agent-auth-delegation.yml` which pushes `chore(auth)`
and `chore(d00)` commits (both have `[skip ci]` ✅ — these do NOT re-cascade).
But `pr-followup-generator` fires again on the NEXT synchronize → cycle repeats.

---

## Workflow Audit: Push Behavior & Conflict Risk

### 🔴 HIGH — Can push commits to branch (directly affects session work)

| Workflow | Trigger | Commit message | `[skip ci]`? | Fix applied |
|----------|---------|----------------|-------------|-------------|
| `pr-followup-generator.yml` | `synchronize, edited, opened, ...` | `chore: Generate follow-up prompt for PR #N` | ❌ **MISSING** | ✅ Added `[skip ci]` (S899-cont) |
| `iterative-self-healing-ci.yml` | `workflow_run: completed` | `self-heal(iter-N): auto-fix PATTERN [skip ci-if-no-change]` | ❌ Non-standard tag | ✅ Fixed to `[skip ci]` (S899-cont) |
| `auto-fix-pr-check.yml` | `pull_request: synchronize` | `fix(ci): resolve auto-fixable issues` | ❌ **MISSING** | ✅ Added `[skip ci]` (S899-cont) |
| `auto-fix-common-issues.yml` | `workflow_dispatch` only | `fix(ci): auto-fix common CI issues` | ❌ **MISSING** | ✅ Added `[skip ci]` (S899-cont) |
| `agent-auth-delegation.yml` | `pull_request: edited, opened, ...` | `chore(auth)/chore(d00)/fix(docs)` | ✅ All have `[skip ci]` | No change needed |
| `copilot-agent-session-done.yml` | `workflow_run: completed` | `fix(docs): auto-post pre-flight auto-fix` | ✅ Has `[skip ci]` | No change needed |
| `codex-manifest-refresh.yml` | `pull_request: opened, reopened` / schedule | `chore(manifest): auto-refresh` | ✅ Has `[skip ci]` | No change needed |
| `e-to-d-transition-gate.yml` | `pull_request` | `chore(manifest): auto-heal C2` | ✅ Has `[skip ci]` | No change needed |
| `codebase-health-sweep.yml` | `workflow_run: completed` | `fix(ci): nightly codebase health sweep` | ✅ Has `[skip ci]` | No change needed |

### 🟡 MEDIUM — Fire on every push/PR update (generate action_required cascades)

| Workflow | Trigger types | Concurrency cancel? | Session impact |
|----------|--------------|---------------------|---------------|
| `workflow-execution-gate.yml` | `pull_request: edited`, `pull_request_review: submitted` | ✅ yes | Fires on every PR-body update from `report_progress` |
| `agent-auth-delegation.yml` | `pull_request: opened/edited/reopened/ready_for_review/closed` | ✅ yes | Fires on every `report_progress` PR-body update |
| `pr-cost-check.yml` | `pull_request: *` | unknown | Fires on every push |
| `pr-followup-generator.yml` | `pull_request: opened/reopened/synchronize/edited/ready_for_review` | ✅ yes | Fires on EVERY push — high frequency |

### 🟢 LOW — Read-only validation (safe, no push risk)

| Workflow | Notes |
|----------|-------|
| `validate.yml`, `resilient_validation.yml`, `nox_gates.yml` | Run tests, no file writes |
| `codeql-analysis.yml`, `codeql.yml`, `semgrep_sarif.yml` | SAST scans, upload results only |
| `security-scanning-suite.yml`, `audit-qa-suite.yml` | Read-only audits |
| `pre-merge-validation.yml`, `comment-review-gate.yml` | Gate checks, no writes |
| `deferral-language-gate.yml`, `pr-checks.yml` | Static checks |
| `rag-tests.yml`, `test-*.yml` | Test runners |

---

## Remaining Risk Patterns (Require Admin Attention)

### ⚠️ RCP-01 — `iterative-self-healing-ci.yml` push window

Even with `[skip ci]` fixed, if self-healing runs concurrently with an active agent
session and both push to the same branch, a force-push race is possible.

**Mitigation already in place:** `concurrency: group: iterative-self-healing-${{ github.ref }}`
with `cancel-in-progress: true` prevents multiple instances.

**Recommended T-04 admin action:** Add branch protection rule requiring linear history OR
configure `iterative-self-healing-ci.yml` to only run on `workflow_dispatch`, not
`workflow_run` triggers, to prevent unintended activation during active sessions.

### ⚠️ RCP-02 — `auto-fix-pr-check.yml` concurrent push window

`auto-fix-pr-check.yml` triggers on `pull_request: synchronize` (every push) and has
`contents: write` + `git push`. Even though it only pushes when auto-fixable issues are
found, if it fires while an agent session is mid-commit it can create non-fast-forward
conflicts.

**Current concurrency guard:** `group: auto-fix-${{ github.ref }}` cancel-in-progress ✅
**Recommended:** Restrict trigger to `workflow_dispatch` only, or add a flag check
for active Copilot sessions before pushing.

### ⚠️ RCP-03 — `pr-followup-generator.yml` concurrency with report_progress

`pr-followup-generator.yml` fires on EVERY `synchronize` and `edited` event. Each
`report_progress` call fires both events → 2 runs of the follow-up generator per session push.
The `[skip ci]` fix (applied S899-cont) breaks the cascade loop; however the workflow itself
still runs twice per push consuming Actions minutes.

**Recommended:** Add an additional trigger guard:
```yaml
if: |
  !contains(github.event.head_commit.message, '[skip ci]') &&
  github.actor != 'github-actions[bot]'
```

### ⚠️ RCP-04 — `agent-auth-delegation.yml` fires on `pull_request: edited`

`report_progress` updates the PR body → `pull_request: edited` → `agent-auth-delegation`
runs → pushes `chore(auth)` + `chore(d00)` (both `[skip ci]` ✅). The commits don't cascade,
but the delegation workflow itself still runs on every `report_progress` call, consuming
Actions minutes and generating approval cycles.

**Status:** Acceptable current behavior — `[skip ci]` on bot commits prevents true cascades.
Monitor Actions minutes consumption.

---

## Session Best Practices (Derived from This Analysis)

1. **Minimise `report_progress` calls** — each call fires `synchronize` + `edited` events,
   triggering 4–8 workflows per call. Batch all pending changes into a single call.

2. **All bot-commit messages MUST contain `[skip ci]`** — the four fixes applied in S899-cont
   address the known gaps. Any new auto-commit workflow should follow this pattern.

3. **Monitor `action_required` count, not approval count** — after the `[skip ci]` fixes,
   the expected steady-state is ≤4 `action_required` workflows per push (one approval round),
   down from the previous 8.

4. **Auto-Approve covers most cases** — `auto-approve-workflows.yml` (already `[x]` in WEC)
   handles the approval delegation automatically. Manual approval is only needed when
   `auto-approve-workflows` itself is `action_required`.

5. **Cooldown after session ends** — wait for all in-progress workflows to complete before
   merging. The 3 pre-existing `startup_failure` workflows (Rust-Python, Progressive,
   Data Quality) are infra-level and do NOT block merge.

---

## Post-Fix Expected Behaviour

After the 4 fixes applied in S899-cont:

| Scenario | Before fix | After fix |
|----------|-----------|-----------|
| `report_progress` push | 8 `action_required` (2 sets) | ≤4 `action_required` (1 set) |
| Self-healing auto-fix commit | Triggers full CI suite | `[skip ci]` — no cascade |
| `auto-fix-pr-check` commit | Triggers full CI suite | `[skip ci]` — no cascade |
| `auto-fix-common-issues` commit | Triggers full CI suite | `[skip ci]` — no cascade |
| Follow-up prompt commit | Triggers full CI suite | `[skip ci]` — no cascade |

