# F-001 Diagnostic Report — T-03 `security_events` Scope Gate

**Generated:** 2026-07-03 (D-tier autonomous campaign, branch `copilot/multi-agent-campaign-plan`)
**Analyst:** Copilot CI Log Retrieval Agent v3.0
**Workflow file:** `.github/workflows/admin-action-t03.yml`
**Reusable notifier:** `.github/workflows/admin-action-notifier.yml`
**Total historical runs analysed:** 21,116

---

## 1. Executive Summary

| Question | Answer |
|---|---|
| Is the `failure`/`action_required` conclusion by design? | **PARTIALLY** — token scope is by design; jobs never executing is a **bug** |
| Does the workflow YAML have syntax errors? | No — YAML is valid |
| Does the workflow execute any jobs? | **NO** — all 21,116 runs show 0 jobs (see §3) |
| Has a T-03 admin-action issue ever been created on GitHub? | **NO** — the issue-creation step never fires |
| Is there a code-fixable bug causing this? | **YES** — duplicate concurrency group causes self-cancellation |
| Admin action still required after code fixes? | **YES** — `CODEX_MASTER_KEY` needs `security_events` scope |  <!-- pragma: allowlist secret -->
| Is this blocking other phases? | **YES** — CodeQL alert automation blocked |

---

## 2. What the Workflow Is Supposed to Do

`admin-action-t03.yml` is a **notifier workflow** designed to:

1. Fire when `⚡ Auto-Approve Pending Workflow Runs` completes.
2. Probe `GET /repos/{repo}/code-scanning/alerts?per_page=1` using `CODEX_MASTER_KEY`.  <!-- pragma: allowlist secret -->
3. If the probe returns HTTP 403 (scope missing):
   - Create / update a GitHub issue `[T-03] CODEX_MASTER_KEY missing security_events scope…`  <!-- pragma: allowlist secret -->
   - Write a CI step summary with click-by-click admin fix instructions.
4. If the probe returns HTTP 200 (scope present):
   - Auto-close the open T-03 issue.

It delegates all logic to `.github/workflows/admin-action-notifier.yml` via `workflow_call`.

---

## 3. Observed Behaviour (Evidence)

### 3.1 Run History Pattern

| Runs | Conclusion | Duration | Jobs Executed |
|------|-----------|----------|---------------|
| #21,111 – #21,116 (most recent) | `action_required` | 0 s (instant) | 0 |
| #21,097 – #21,110 | `failure` | 1–2 s | 0 |
| All earlier runs (thousands) | `failure` | 1–2 s | 0 |

**Key finding:** Every single run in the workflow's entire 21,116-run history has executed **zero jobs**.
Because no jobs run, the `probe-and-notify` job never fires, which means:
- No T-03 GitHub issue is ever created.
- No admin notification is ever sent.
- The workflow is silently broken.

### 3.2 Run Mode Shift (recent)

Runs #21,111 onwards changed from `failure` (1–2 s) to `action_required` (0 s). This coincides with GitHub's workflow-approval gate being triggered for `workflow_run`-sourced runs — likely because the trigger rate increased and GitHub began requiring manual approval. The underlying cause (0 jobs) is the same for both modes.

---

## 4. Root-Cause Analysis — Code Bugs

### 4.1 🔴 Critical: Duplicate Concurrency Group Causes Self-Cancellation

**Location:** `admin-action-notifier.yml` lines 81–83 (now fixed — see §6)

**The bug:**

Both caller and callee defined the **same** concurrency group:

```yaml
# In admin-action-t03.yml  (caller)
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

# In admin-action-notifier.yml  (callee) ← DUPLICATE — now removed
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

**Why this is fatal:**

In a `workflow_call` context, `github.workflow` in the *called* workflow resolves to the
**caller's** workflow name (GitHub documented behaviour). Both expressions therefore expand
to the identical string, e.g.:

```
Admin Action — T-03 security_events Scope Gate-refs/heads/main
```

When `admin-action-t03.yml` starts, it claims this concurrency group.
When it invokes `admin-action-notifier.yml`, GitHub evaluates the reusable workflow's
concurrency block **before dispatching its jobs**. The group is already marked as
in-progress (by the calling workflow run). With `cancel-in-progress: true`, the reusable
workflow immediately cancels the in-progress runner — which is the calling workflow itself.
Result: all jobs are cancelled within 1–2 seconds; 0 jobs execute.

**Fix applied:** Removed the `concurrency` block from `admin-action-notifier.yml`.
The caller workflow already owns the correct concurrency group; the notifier inherits it.

### 4.2 🟡 Minor: Python Reads Unexported Bash Variable

**Location:** `admin-action-notifier.yml` probe step (now fixed)

```bash
# BEFORE (broken):
RESPONSE_FILE="${RUNNER_TEMP}/admin_probe_response.json"
RESPONSE_MSG=$(python3 -c \
  "import json,sys,os; d=json.load(open(os.environ['RESPONSE_FILE'])); ..." \
  2>/dev/null || echo "(no message)")
```

`RESPONSE_FILE` is a bash variable but **not exported** to child process environment.
`os.environ['RESPONSE_FILE']` raises `KeyError`; the `2>/dev/null || echo "(no message)"`
silently masks the error. The API error message is never extracted; it always shows
`(no message)` in the CI summary, reducing diagnostic value.

**Fix applied:** Added `export RESPONSE_FILE` immediately after the assignment.

### 4.3 ⚪ Dead Code: Unused `force_create_issue` Input

**Location:** `admin-action-t03.yml` lines 11–18

```yaml
workflow_dispatch:
  inputs:
    force_create_issue:
      description: Force issue creation even if probe passes (for testing)
      ...
```

This input is never passed to `admin-action-notifier.yml` (which doesn't support it
either). It does no harm and can remain as a future hook, but should be noted as
non-functional.

**Status:** No fix applied (safe dead code).

---

## 5. YAML Health Assessment

| Check | Status | Notes |
|---|---|---|
| YAML syntax valid | ✅ Pass | Both files parse without errors |
| Required inputs all provided | ✅ Pass | `gap_id`, `probe_url`, `issue_title`, `issue_body_md` all set |
| Permissions block correct | ✅ Pass | `issues: write` enables issue creation; `security-events: read` is present |
| `secrets: inherit` usage | ✅ Pass | Correctly propagates `CODEX_MASTER_KEY` to notifier |  <!-- pragma: allowlist secret -->
| `probe_url` expression | ✅ Pass | `${{ github.repository }}` in `with:` is valid for `uses:` jobs |
| `workflow_run` trigger | ✅ Pass | Correct trigger on both trigger workflows |
| Step-level `if:` conditions | ✅ Pass | `scope_ok == 'false'` / `scope_ok == 'true'` branching is correct |
| Auto-close logic | ✅ Pass | Correctly finds and closes open issues when probe succeeds |
| Step summary | ✅ Pass | Writes to `$GITHUB_STEP_SUMMARY` with `if: always()` guard |
| **Concurrency in notifier** | ✅ **Fixed** | Removed duplicate group that caused self-cancellation |
| **Python env var** | ✅ **Fixed** | `RESPONSE_FILE` now exported |

---

## 6. Changes Made (This Session)

### `admin-action-notifier.yml`

**Change 1 — Remove duplicate concurrency block**

```diff
-concurrency:
-  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
-  cancel-in-progress: true
-
 permissions:
```

Replaced with a comment explaining why it's absent.

**Change 2 — Export `RESPONSE_FILE` before Python reads it**

```diff
 RESPONSE_FILE="${RUNNER_TEMP}/admin_probe_response.json"
+export RESPONSE_FILE
 RESPONSE_MSG=$(python3 -c \
```

---

## 7. Admin Action Required (Human Escalation)

> **This section requires human admin action — cannot be automated.**

### Step-by-Step Fix for `CODEX_MASTER_KEY`  <!-- pragma: allowlist secret -->

1. **Open the token settings:**
   → [github.com/settings/tokens](https://github.com/settings/tokens)
   Find the PAT that backs `CODEX_MASTER_KEY` and click **Edit**.  <!-- pragma: allowlist secret -->

2. **Add the `security_events` scope:**
   Keep existing scopes: `repo`, `workflow`
   Add: ☑ `security_events` (read:security_events is sufficient)
   Set expiry: 90 days from today
   Click **"Update token"** → copy the new value.

3. **Update the org secret:**
   → [Organization Settings → Secrets → CODEX_MASTER_KEY](https://github.com/organizations/Aries-Serpent/settings/secrets/actions/CODEX_MASTER_KEY)  <!-- pragma: allowlist secret -->
   Paste the new token value and save.

4. **Verify** by running the token probe:
   ```bash
   gh workflow run token-probe.yml --repo Aries-Serpent/_codex_ --field pr_number=4346
   ```

5. **Run post-rotation check:**
   ```bash
   GH_TOKEN=<new_token> bash scripts/ci/post_rotation_verify.sh
   ```

### What Happens After the Code Fix + Token Fix

1. Code fix (this session): removes self-cancellation → jobs will start executing.
2. Token still lacks `security_events` → probe returns HTTP 403 → notifier creates T-03 GitHub issue.
3. Human rotates token → probe returns HTTP 200 → notifier auto-closes T-03 issue.
4. `codeql-alert-fetcher.yml` and CodeQL agent flows unblocked.

---

## 8. Impact Assessment

### Is this blocking other phases?

**YES.**

| Blocked Item | Impact | Unblocked By |
|---|---|---|
| `codeql-alert-fetcher.yml` | Cannot retrieve CodeQL alert file:line locations | Token rotation |
| OBJ-B `py/wrong-named-arg` ×15 | Agent cannot see alerts to fix them | Token rotation |
| `scripts/ci/fetch_codeql_alerts.py` | Returns HTTP 403 for all calls | Token rotation |
| T-03 admin notification | Human never informed via issue | Code fix (this PR) |

### Severity of the Code Bug (§4.1)

**HIGH** — Without this fix, the entire notification system for T-03 is broken silently.
The admin was never notified that the token needed updating. After this fix, the next
workflow run will create the T-03 GitHub issue, surfacing the token problem correctly.

---

## 9. Summary Verdict

| Finding | Classification | Resolution |
|---|---|---|
| `CODEX_MASTER_KEY` lacks `security_events` scope | By design (intentional gate) | Human admin |  <!-- pragma: allowlist secret -->
| All runs show 0 jobs (notifier never fires) | **Bug** — self-cancellation | Fixed this session |
| Python `RESPONSE_FILE` not exported | Minor bug | Fixed this session |
| `force_create_issue` input unused | Dead code | No action needed |
| Overall YAML structure | Correct | No action needed |

**Bottom line:** The underlying problem (missing token scope) is a known admin action.
The workflow itself had a critical code bug (duplicate concurrency) that prevented it from
ever executing and therefore from ever notifying the admin. Both fixable code issues have
been resolved in this PR.

---

*Report generated by Copilot CI Log Retrieval Agent v3.0 as part of D-tier autonomous campaign on branch `copilot/multi-agent-campaign-plan`.*
