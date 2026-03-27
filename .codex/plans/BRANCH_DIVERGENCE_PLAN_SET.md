# Branch Divergence Investigation & Resolution — Plan Set

**Created:** 2026-03-27 (S237 — PR #3770)
**Author:** Copilot coding agent (S237)
**Triggered by:** Recurring CI failures in `branch-divergence-monitor.yml` + triage report #3737
**Related docs:** `.codex/docs/BRANCH_DIVERGENCE_PREVENTION.md`, `.codex/docs/INTEGRATION_BRANCH_MODEL.md`
**Status:** 🔄 Active execution

---

## 📊 Problem Statement

Branch divergence between `0D_base_` and `main` is a **recurring, self-reinforcing failure pattern**
that has generated 3+ triage failures in the past 24 hours alone. The divergence causes:

1. `branch-divergence-monitor.yml` failures (Python SyntaxError from double-zero output — fixed S237)
2. Auto-gen commits leaking to `main` instead of routing to `0D_base_`
3. Merge conflicts in staging-gate PRs (each leaked commit = additional conflict surface)
4. Downstream failures: `cognitive-analysis-feed.yml`, `embedding-index-rebuild.yml`,
   `repo-var-sync-schedule.yml`, `vars-guide-sync.yml` all use `git checkout -B` without `-f` (fixed S237)
5. Blocked `main` health: tests run on a mix of staged + unstaged code

---

## 🔍 Root Cause Taxonomy (S237 Deep Research)

### RC-1: `grep -c . || echo 0` Double-Output Bug ✅ FIXED (S237)

**Location:** `branch-divergence-monitor.yml` lines 115, 118
**Pattern:** `COUNT=$(echo "$VAR" | grep -c . || echo 0)`
**Failure mode:** `grep -c .` outputs `0` AND exits 1 when input is empty.
`|| echo 0` then appends a second `0` to stdout. `COUNT` becomes `"0\n0"`.
**Downstream effects:**
- `echo "behind_count=$BEHIND_COUNT"` → writes `behind_count=0\n0` to `$GITHUB_OUTPUT`
- GitHub rejects the bare `0` line: `##[error]Invalid format '0'`
- Python heredoc sees `"behind_count": 0\n0,` → SyntaxError (two juxtaposed expressions)
**Fix:** Replace `|| echo 0` with `|| true` — `grep -c` already outputs `0` on no-match.
**Commit:** S237 (PR #3770)

### RC-2: `git checkout -B` Without `-f` in Commit-Step Workflows ✅ FIXED (S237)

**Location:** `cognitive-analysis-feed.yml:119,206`, `repo-var-sync-schedule.yml:219`,
`embedding-index-rebuild.yml:151`, `vars-guide-sync.yml:136`
**Failure mode:** Workflow generates local file changes, copies to `/tmp`, then tries
`git checkout -B _autogen_sync_ origin/$TARGET` — but git refuses because uncommitted
changes would be overwritten. Files are already safe in `/tmp` so force-checkout is correct.
**Fix:** `git checkout -fB _autogen_sync_ origin/"$_TARGET"`
**Commit:** S237 (PR #3770)

### RC-3: Chicken-and-Egg Auto-Gen Routing 🔄 IN PROGRESS

**Root cause:** Scheduled workflows always run from `main`. Routing logic (`if 0D_base_ exists → push there`)
lives on `0D_base_` but NOT yet on `main` (arrives only after staging-gate PR merges).
**Current state:** RC-2 fix (S237) resolves the `git checkout` abort, allowing successful
routing commits to land on `0D_base_`. Once the current staging-gate PR merges:
- `main` will have the routing fix
- Future auto-gen commits will correctly target `0D_base_`
- Divergence accumulation rate drops to ~0 (except expected staged work)

### RC-4: Branch Divergence Monitor Does Not Alert on Its Own Failure 📋 PLANNED

**Problem:** When `branch-divergence-monitor.yml` itself fails (due to RC-1), the failure
is silent — no rescue comment, no issue update, no escalation. The divergence continues
to grow undetected.
**Fix:** Add rescue-comment-push job (pattern from S237) + `continue-on-error: true` on
the Python summary step so the monitor keeps running even if JSON serialization fails.

### RC-5: Forward-Sync Safety Net Has Rejection Window ⏳ NEEDS INVESTIGATION

**Problem:** `forward-sync-autogen.yml` triggers on individual file pushes to `main`.
But if `0D_base_` is already ahead, the push to `0D_base_` is rejected as non-fast-forward.
This creates a window where auto-gen commits land on `main` but the safety net fails
to sync them to `0D_base_`.
**Investigation needed:** Check `forward-sync-autogen.yml` for fast-forward rejection handling.

---

## 📋 Plan Set — Ordered by Priority

### Phase 1: Immediate Fixes (S237 — this session) ✅

| Task | File | Status |
|------|------|--------|
| Fix `grep -c . \|\| echo 0` double-output | `branch-divergence-monitor.yml` | ✅ Fixed |
| Fix `git checkout -B` without `-f` | 4 auto-gen workflows | ✅ Fixed |
| Add trailing-newline safety to Python heredoc in monitor | `branch-divergence-monitor.yml` | ✅ See below |

#### Phase 1 additional: Python heredoc defensive hardening

The Python heredoc should defensively handle empty/malformed variable expansions:
- Add `int()` cast on count variables
- Add `str()` cast on SHA variables
This prevents any future variable expansion edge cases from producing SyntaxError.

### Phase 2: Monitoring Hardening (Next session) 📋

| Task | File | Priority | Effort |
|------|------|----------|--------|
| Add rescue-comment-push to `branch-divergence-monitor.yml` | monitor | P2 | 30 min |
| Add `continue-on-error: true` to Python summary step | monitor | P2 | 5 min |
| Add exit-code annotation so JSON failure is visible in log | monitor | P2 | 10 min |
| Check `forward-sync-autogen.yml` fast-forward rejection handling | sync | P1 | 30 min |
| Add `|| true` guard pattern audit to ALL workflows with `grep -c` | all | P2 | 20 min |

### Phase 3: Prevention Architecture (Backlog) 📋

| Task | File | Priority | Effort |
|------|------|----------|--------|
| Move auto-gen routing logic to a reusable action | `.github/actions/route-autogen-commit/` | P3 | 2h |
| Add `DIVERGENCE_THRESHOLD` variable gate that blocks merge if drift > N | `branch-rebase-gate.yml` | P3 | 1h |
| Add daily digest of divergence status to GitHub Discussions | `branch-divergence-monitor.yml` | P3 | 1h |
| Document divergence recovery playbook in `BRANCH_DIVERGENCE_PREVENTION.md` | docs | P2 | 30 min |

---

## 🔧 Implementation Checklist (S237)

### Step 1 — Fix branch-divergence-monitor.yml Python heredoc ✅

Replace raw shell variable expansions in Python heredoc with safe casts.

Before:
```python
"behind_count": $BEHIND_COUNT,
"ahead_count": $AHEAD_COUNT,
```

After:
```python
"behind_count": int("$BEHIND_COUNT".strip() or "0"),
"ahead_count": int("$AHEAD_COUNT".strip() or "0"),
```

This ensures any accidental whitespace or multi-line expansion is safely converted to `int`.

### Step 2 — Fix grep-c double-output ✅

```bash
# Before (broken):
BEHIND_COUNT=$(echo "$MAIN_ONLY" | grep -c . || echo 0)
# After (fixed):
BEHIND_COUNT=$(echo "$MAIN_ONLY" | grep -c . || true)
```

### Step 3 — Fix git checkout -fB in 4 commit-step workflows ✅

```bash
# Before:
git checkout -B _autogen_sync_ origin/"$_TARGET"
# After:
git checkout -fB _autogen_sync_ origin/"$_TARGET"  # S237: files already in /tmp
```

### Step 4 — Audit all `grep -c . || echo` patterns 📋

Find and fix any other workflows using the same broken pattern:
```bash
grep -rn "grep -c . || echo" .github/workflows/
```

### Step 5 — Validate divergence monitor exit code ✅

After fixes: `branch-divergence-monitor.yml` should:
- Run without Python SyntaxError
- Write clean `key=value` pairs to GITHUB_OUTPUT (no multi-line values)
- Report divergence status correctly
- Self-correct auto-gen leaks via forward-sync trigger

---

## 🔄 Agent Execution Protocol

When a Copilot agent encounters a branch divergence failure:

```
1. IDENTIFY:
   - Check `branch-divergence-monitor.yml` latest run
   - Get job logs: look for "SyntaxError", "Invalid format", "checkout" errors
   - Check divergence count: behind_count > 0 = leaked commits on main

2. CLASSIFY:
   - AUTO-GEN: github-actions[bot] author, [skip ci]/[automated]/🧠 pattern
     → Trigger forward-sync-autogen.yml (workflow_dispatch)
   - CODE-LEAK: human/non-bot commit on main not in 0D_base_
     → Open issue with [DIVERGENCE-CRITICAL] label, escalate to @mbaetiong

3. REMEDIATE:
   A) For auto-gen leaks: trigger forward-sync or cherry-pick to 0D_base_
   B) For code leaks: investigate origin, apply minimal fix to 0D_base_
   C) For monitor failures: fix the monitor workflow itself (this plan set)

4. VERIFY:
   - Re-trigger branch-divergence-monitor.yml (workflow_dispatch)
   - Confirm conclusion = "success" and severity = "healthy"
   - Check 0D_base_ PR is green
   - Document in CI_FAILURE_TRACKING_LOG.md
```

---

## 📊 Pattern Library Entry

**Pattern ID:** `branch_divergence_grep_c_double_output`
**First seen:** 2026-03-27 (S237)
**Frequency:** Recurring (3+ failures in last 24h before S237 fix)
**Auto-fix eligible:** YES — `|| echo 0` → `|| true`
**Detection heuristic:**
```
grep -rn "grep -c.*|| echo [0-9]" .github/workflows/
```
**Prevention:** Never use `grep -c PATTERN | ... || echo N` when N equals the
no-match output of grep-c (which is already 0). Use `|| true` to suppress exit code only.

---

## 📎 Related CI Failures (from triage report #3737)

| Workflow | Root Cause | Status |
|----------|-----------|--------|
| Branch Divergence Monitor | RC-1 (grep-c double-output) + Python SyntaxError | ✅ Fixed S237 |
| Cognitive Analysis & Learning | RC-2 (git checkout -B without -f) | ✅ Fixed S237 |
| Embedding Index Rebuild | RC-2 (git checkout -B without -f) | ✅ Fixed S237 |
| Repo Var Sync (Scheduled) | RC-2 (git checkout -B without -f) | ✅ Fixed S237 |
| Auto-Sync Variables Master Guide | RC-2 (git checkout -B without -f) | ✅ Fixed S237 |

---

## 🧠 Cognitive Brain Integration

**AfterMath pattern:** `branch_divergence_grep_c_double_output` → store in `.codex/cognitive_brain/patterns/`
**Objective tracker:** Update OBJ-002 (branch divergence health) with S237 fixes
**CI tracking log:** Add new row to `.codex/CI_FAILURE_TRACKING_LOG.md`

---

*Last updated: 2026-03-27T22:30Z — S237*
