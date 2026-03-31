# WEC PR Body Append — Conflicts & Best Approach

> **Version:** 1.0.0
> **Created:** 2026-03-31 S260
> **Status:** ✅ Authoritative — identified in S260, hardened in `session_wrapup_autofix.py`

---

## Problem Statement

The **Workflow Execution Checklist (WEC)** must always appear at the end of the PR body
on every update. However, the `report_progress` tool **replaces the entire PR body** with
its `prDescription` parameter — silently stripping the WEC on every push unless it is
explicitly included.

---

## Identified Conflict Patterns

### Conflict 1 — `report_progress` Full-Body Replacement (CRITICAL)

| Attribute | Detail |
|-----------|--------|
| **Trigger** | Every `report_progress` call |
| **Effect** | Entire PR body replaced with `prDescription` value |
| **Result** | WEC stripped unless explicitly appended to `prDescription` |
| **Frequency** | Every session (multiple times per session) |
| **Severity** | 🔴 Critical — breaks agent-auth-delegation WEC gate |

**Root cause:** `report_progress` uses GitHub API `updatePullRequest` which sets `body`
to whatever string is passed. There is no "append-only" mode.

---

### Conflict 2 — WEC State Loss on Overwrite

| Attribute | Detail |
|-----------|--------|
| **Trigger** | `report_progress` called without reading current WEC state first |
| **Effect** | Maintainer-selected `[x]` items (e.g., `cost-gate.yml`, `auto-approve-workflows`) reset to `[ ]` |
| **Result** | `agent-auth-delegation.yml` re-injection also loses state if body was overwritten |
| **Severity** | 🟡 Medium — approval gates re-armed incorrectly |

---

### Conflict 3 — Race Condition: `agent-auth-delegation.yml` vs `report_progress`

| Attribute | Detail |
|-----------|--------|
| **Trigger** | `report_progress` push triggers `agent-auth-delegation.yml` which re-injects WEC |
| **Effect** | WEC is missing in the window between push and workflow completion (~60s) |
| **Result** | Comment Review Gate may scan during this window and see no WEC |
| **Severity** | 🟡 Medium — transient gap, healed by workflow |

---

### Conflict 4 — `_REQUIRED_PR_CHECKBOXES` vs Live PR State

| Attribute | Detail |
|-----------|--------|
| **Trigger** | `fix_pr_body_checkboxes` called with no existing WEC state |
| **Effect** | Falls back to `_REQUIRED_PR_CHECKBOXES` (all optional items unchecked) |
| **Result** | Maintainer's in-session `[x]` selections lost if WEC was stripped before fix runs |
| **Severity** | 🟡 Medium — correctible by maintainer re-checking |

---

## Recommended Approach: Always-Append Strategy

**Selected approach:** ✅ **Option A — Explicit WEC in every `report_progress` call**

### Why Option A

- Zero race-condition window (WEC is in the body from the moment of push)
- Preserves maintainer state (agent reads current WEC state before calling `report_progress`)
- No workflow dependency (doesn't rely on `agent-auth-delegation.yml` re-injection timing)
- Auditable (WEC state visible in every commit's PR body snapshot)

### Implementation

Every `report_progress` call **MUST** end its `prDescription` with the WEC block:

```python
import sys; sys.path.insert(0, 'scripts/ci')
import session_wrapup_autofix as swa
import subprocess, json

# 1. Read current WEC state from live PR body
result = subprocess.run(
    ['gh','pr','view','<PR_NUMBER>','--repo','Aries-Serpent/_codex_','--json','body'],
    capture_output=True, text=True
)
current_body = json.loads(result.stdout).get('body', '')
existing_state = swa._extract_wec_state(current_body)

# 2. Build WEC with preserved state
wec = swa._build_wec_block(existing_state=existing_state)

# 3. Always append to prDescription
pr_description = f"""{progress_checklist}
{wec}"""
# Then pass pr_description to report_progress(prDescription=pr_description, ...)
```

### Pre-checked Always-Required Items

These items are **always** `[x]` regardless of `existing_state` (enforced by `_WEC_ALWAYS_REQUIRED`):

- `pre-merge-validation.yml`
- `comment-review-gate.yml`
- `agent-auth-delegation.yml`

---

## Alternative Options Considered

### Option B — Post-push `session_wrapup_autofix.py --fix-pr-body`

Relies on `copilot-agent-session-done.yml` `preflight-autofix` job running after every push.
**Rejected:** ~60s race-condition window; requires checked `Auto-Post` checkbox; does not run on every push.

### Option C — `agent-auth-delegation.yml` Always Re-inject

Already implemented. Re-injects WEC on every PR push event.
**Retained as safety net** but insufficient alone due to Conflict 3 timing gap.

### Option D — GitHub App Middleware

Intercept all `updatePullRequest` API calls and append WEC automatically.
**Rejected:** Requires external GitHub App infrastructure; out of scope.

---

## Hardening Checklist

- [x] `session_wrapup_autofix.py`: `_build_wec_block()` and `_extract_wec_state()` available for pre-call state preservation
- [x] `agent-auth-delegation.yml`: WEC re-injected on every PR push event (safety net)
- [x] Both PR templates: WEC section present with all 14 items
- [x] `_WEC_ITEMS` count: 14 (3+3+1+6+1) — includes `workflow-execution-gate.yml` and `copilot-iterative-self-healing.yml`
- [x] This document: conflicts catalogued; Option A mandated

---

## Enforcement

Every Copilot coding agent session **MUST**:

1. Read current PR body WEC state via `_extract_wec_state()` before calling `report_progress`
2. Append `_build_wec_block(existing_state)` output at the **end** of every `prDescription`
3. Never call `report_progress` with a `prDescription` that omits the `## 🔄 Workflow Execution Checklist` heading

Enforced by: `comment-review-gate.yml` (will flag missing WEC) + `agent-auth-delegation.yml` (re-injects as fallback).

---

_Created: 2026-03-31 S260 | Owner: Aries-Serpent/_codex_ | Policy ref: .codex/CODEBASE_AGENCY_POLICY.md_
