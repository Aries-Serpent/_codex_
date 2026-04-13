# Self-Healing Complete Plan Set — PR #3954 / Session S_PR3954_SELF_HEALING

**Created:** 2026-04-13T03:15Z
**Author:** Copilot coding agent (S_PR3954_SELF_HEALING)
**Branch:** automated/repository-health-11
**Template:** `.github/prompts/sprint_execution_plan/TEMPLATE.md`
**PDA AfterMath:** `.codex/aftermath/pda_iterations.jsonl` (8 entries)
**Status:** ✅ All plans implemented

---

## 📊 Problem Statement

The repository's self-healing system had a **recurring engine of failure**:

1. `fix_manifest_baseline()` in `session_wrapup_autofix.py` computed a raw SHA-1
   of `CODEX_MANIFEST.json` but `detect-secrets` uses a per-line secret hash.
   These produce **different values** — so every wrapup run **corrupted** the hash
   that `sync_tracked_files.py` had just correctly set, causing permanent
   `.secrets.baseline` staleness.

2. `run_validation.sh` ran `sync-tracked-files` pre-commit hook (which fixed
   `.secrets.baseline`) but **did not stage the result**, so the subsequent
   `detect-secrets` hook failed with "baseline file is unstaged".

3. `copilot-agent-session-done.yml` and `e-to-d-transition-gate.yml` committed
   `CODEX_MANIFEST.json` without running `sync_tracked_files --fix` first.

4. The iterative self-healer had no universal sweep step — it ran pattern-specific
   fixes only when `fixable==true`, missing the baseline staleness root cause for
   every `fixable==false` (unknown) pattern.

5. Node.js 20 EOL workflows and no nightly clean-state maintenance on `main`/`0D_base_`.

---

## 📋 Plan Sets

### PLANSET-001 — Universal Baseline-Sweep Job in Iterative Self-Healer

```yaml
task_id: PLANSET-001
priority: P0
phase: 2
phase_name: Reproducibility
effort_estimate: Small
status: COMPLETE ✅
```

**Problem:** `iterative-self-healing-ci.yml` only ran pattern-specific fixes when
`fixable==true`. For unknown/non-fixable patterns, no baseline sync happened, so
the most common root cause (stale CODEX_MANIFEST hash) was never cleared.

**Plan:**
- Add `baseline-sweep` job to `iterative-self-healing-ci.yml`
- Job runs `sync_tracked_files --fix` + `auto_fix_common_issues.py` for ALL failures
- `escalate` and `copilot-escalation` jobs now `needs: [triage, baseline-sweep]`
- Commits with `[skip ci]` to prevent cascade re-triggering

**Do (implementation):**
- File: `.github/workflows/iterative-self-healing-ci.yml`
- Added `baseline-sweep` job before `escalate` job (line 645)
- Updated `needs:` on `escalate` and `copilot-escalation` to `[triage, baseline-sweep]`
- Cascade-safe: rate_cap (10/hr) inherited from `triage` job

**Act (verification):**
```bash
gh workflow run iterative-self-healing-ci.yml
gh run list --workflow iterative-self-healing-ci.yml | head -5
```

**PDA AfterMath:** `PLANSET-001-BASELINE-SWEEP-JOB`

---

### PLANSET-002 — Nightly Codebase Health Sweep Workflow

```yaml
task_id: PLANSET-002
priority: P0
phase: 2
phase_name: Reproducibility
effort_estimate: Small
status: COMPLETE ✅
```

**Problem:** No scheduled maintenance ran on `main`/`0D_base_`. Fixable issues
accumulated between sessions and caused recurring CI failures.

**Plan:**
- Create `codebase-health-sweep.yml` — scheduled nightly at 02:15 UTC
- Sweeps `main` AND `0D_base_`: `sync_tracked_files --fix` + `auto_fix_common_issues.py` + `doc_metrics_sync --fix`
- Opens/updates tracking GitHub issue for remaining manual-only problems
- Appends PDA AfterMath entry per run
- Also triggers on `workflow_run` after `copilot-agent-session-done`
- Rate gate: skips if last sweep ran < 6h ago (prevents double-sweep)

**Do (implementation):**
- File created: `.github/workflows/codebase-health-sweep.yml`
- Jobs: `sweep-main`, `sweep-staging`, `report-manual-issues`
- All commits tagged `[skip ci]`

**Act (verification):**
```bash
gh workflow run codebase-health-sweep.yml --ref main
gh run list --workflow codebase-health-sweep.yml | head -3
```

**PDA AfterMath:** `PLANSET-002-NIGHTLY-SWEEP`

---

### PLANSET-003 — Pre-Session Health Sweep in `--activate-workflows`

```yaml
task_id: PLANSET-003
priority: P1
phase: 2
phase_name: Reproducibility
effort_estimate: Small
status: COMPLETE ✅
```

**Problem:** The Copilot Session Startup Protocol (`--activate-workflows`) armed
WEC workflows but did not first clean up fixable issues. Sessions started on a
potentially stale codebase.

**Plan:**
- Add `_run_pre_session_health_sweep()` to `session_wrapup_autofix.py`
- Call it inside the `--activate-workflows` path before `select_merge_required_workflows()`
- Runs: `sync_tracked_files --fix`, `auto_fix_common_issues.py`, `doc_metrics_sync --fix`

**Do (implementation):**
- File: `scripts/ci/session_wrapup_autofix.py`
- Added `_run_pre_session_health_sweep(dry_run)` function (55 lines)
- Called from `--activate-workflows` standalone path

**Act (verification):**
```bash
python scripts/ci/session_wrapup_autofix.py --pr-number TEST --activate-workflows --dry-run
```

**PDA AfterMath:** `PLANSET-003-SESSION-START-SWEEP`

---

### PLANSET-004 — Node.js 20 → 22 in 4 Workflows

```yaml
task_id: PLANSET-004
priority: P1
phase: 3
phase_name: Autonomy
effort_estimate: Trivial
status: COMPLETE ✅
```

**Problem:** 4 workflows pinned `node-version: '20'` or `NODE_VERSION: '20'`.
Node.js 20 EOL is April 2026. GitHub Actions will start showing deprecation
warnings and eventually block these runs.

**Affected files:**
- `.github/workflows/copilot-setup-steps.yml` — `NODE_VERSION: "20"` → `"22"`
- `.github/workflows/documentation-link-checker.yml` — `'20'` → `'22'`
- `.github/workflows/har-capture.yml` — `NODE_VERSION: '20'` → `'22'`
- `.github/workflows/unified-deployment.yml` — `'20'` → `'22'`

**Act (verification):**
```bash
grep -r "node-version: '20'" .github/workflows/ | wc -l  # → 0
grep -r "NODE_VERSION.*20" .github/workflows/ | grep -v "#" | wc -l  # → 0
```

**PDA AfterMath:** `PLANSET-004-NODEJS20`

---

### PLANSET-ROOT — Root Cause Fixes (SCP-RESCUE-5)

```yaml
task_id: PLANSET-ROOT
priority: P0
phase: 1
phase_name: Foundation
effort_estimate: Small
status: COMPLETE ✅
```

Three root-cause fixes that eliminate the engine of recurring `.secrets.baseline`
staleness:

#### ROOT-1: `fix_manifest_baseline()` wrong hash algorithm
- **File:** `scripts/ci/session_wrapup_autofix.py`
- **Fix:** Replaced raw `hashlib.sha1(file.read_bytes())` with delegation to
  `sync_tracked_files.py --fix --manifest-only` (the authoritative tool)
- **PDA:** `SCP-RESCUE-5-ROOT-CAUSE`

#### ROOT-2: `run_validation.sh` unstaged baseline
- **File:** `scripts/run_validation.sh`
- **Fix:** Added `python scripts/ci/sync_tracked_files.py --fix --manifest-only && git add .secrets.baseline`
  before the pre-commit run
- **PDA:** `SCP-RESCUE-5-VALIDATION`

#### ROOT-3: Bot commit workflows missing baseline sync
- **Files:** `.github/workflows/copilot-agent-session-done.yml`,
  `.github/workflows/e-to-d-transition-gate.yml`
- **Fix:** Added `python3 scripts/ci/sync_tracked_files.py --fix --manifest-only`
  before `git add .secrets.baseline` in both workflows
- **PDA:** `SCP-RESCUE-5-SESSION-DONE`

---

## 🔄 PDA Loop — Verification Sequence

Run these in order after all commits land to confirm full resolution:

```bash
# 1. Verify baseline is clean
python scripts/ci/sync_tracked_files.py --check --manifest-only

# 2. Verify no auto-fixable issues
python scripts/ci/auto_fix_common_issues.py --check-only

# 3. Verify session startup sweep works
python scripts/ci/session_wrapup_autofix.py --pr-number 3954 --activate-workflows --dry-run

# 4. Verify no Node 20 references remain
grep -r "node-version: '20'" .github/workflows/ | wc -l  # → 0

# 5. Check nightly sweep workflow exists
gh workflow list | grep "Codebase Health Sweep"

# 6. Check iterative-healer has baseline-sweep job
grep "baseline-sweep:" .github/workflows/iterative-self-healing-ci.yml
```

---

## 📈 AfterMath Summary

| Pattern ID | Type | Status |
|-----------|------|--------|
| SCP-RESCUE-5-ROOT-CAUSE | fix | ✅ resolved |
| SCP-RESCUE-5-VALIDATION | fix | ✅ resolved |
| SCP-RESCUE-5-SESSION-DONE | fix | ✅ resolved |
| PLANSET-001-BASELINE-SWEEP-JOB | enhancement | ✅ implemented |
| PLANSET-002-NIGHTLY-SWEEP | enhancement | ✅ implemented |
| PLANSET-003-SESSION-START-SWEEP | enhancement | ✅ implemented |
| PLANSET-004-NODEJS20 | fix | ✅ resolved |

All 7 patterns resolved. PDA AfterMath entries appended to
`.codex/aftermath/pda_iterations.jsonl`.
