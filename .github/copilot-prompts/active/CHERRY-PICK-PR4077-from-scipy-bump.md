# 🍒 Cherry-Pick Instructions for PR #4077

**Source branch**: `dependabot/pip/scipy-1.17.1`  
**Target PR**: #4077 (`copilot/create-implementation-plan-and-test-cases`)  
**Prepared by**: Copilot session `22b1bf38` (2026-04-27)  
**Status**: 🔴 ACTION REQUIRED — apply these patches to PR #4077

---

## 📋 What was fixed (source branch)

Two bugs in the CI auto-fix pipeline were fixed on `dependabot/pip/scipy-1.17.1`
that affect ALL branches including `copilot/create-implementation-plan-and-test-cases`:

### Bug 1 — Pattern 30: wrong arity call (commit `c683c12`)
`auto_fix_common_issues.py` line 2730 called
`swa._compute_merge_readiness_score(str(self.repo_root))` but the function
takes **0** positional arguments.  This caused Pattern 30 to silently swallow
its exception and report "✓ No issues found" even when the scorecard was broken.

**File**: `scripts/ci/auto_fix_common_issues.py`

### Bug 2 — Pattern 30 scorecard circular recursion (commit `9d898df`)
The scorecard's `auto_fix` dimension calls
`auto_fix_common_issues.py --check-only` as a subprocess.  That subprocess
runs Pattern 30, which runs the scorecard, which calls the subprocess again —
infinite recursion limited only by subprocess timeouts.

**Fix**: added `CODEX_SKIP_PATTERN_NUMS` env-var support in
`auto_fix_common_issues.py` (skips specified pattern numbers) and updated
`session_wrapup_autofix.py` to pass `CODEX_SKIP_PATTERN_NUMS=30` when
invoking the subprocess, breaking the loop.

**Files**: `scripts/ci/auto_fix_common_issues.py`, `scripts/ci/session_wrapup_autofix.py`

---

## 🛠️ Cherry-Pick Instructions

Run the following commands **inside the PR #4077 branch**
(`copilot/create-implementation-plan-and-test-cases`):

```bash
# Step 1 — fetch the source branch (unshallow if needed)
git fetch origin dependabot/pip/scipy-1.17.1

# Step 2 — grab only the two CI script files at their final fixed state
#          (avoids pulling in branch-specific PDA/accountability/baseline changes)
git checkout origin/dependabot/pip/scipy-1.17.1 -- \
    scripts/ci/auto_fix_common_issues.py \
    scripts/ci/session_wrapup_autofix.py

# Step 3 — verify the fixes are present
grep -n "_compute_merge_readiness_score()" scripts/ci/auto_fix_common_issues.py | head -3
grep -n "CODEX_SKIP_PATTERN_NUMS" scripts/ci/auto_fix_common_issues.py | head -3
grep -n "CODEX_SKIP_PATTERN_NUMS" scripts/ci/session_wrapup_autofix.py | head -3

# Step 4 — run the auto-fix check to confirm exit 0
python3 scripts/ci/auto_fix_common_issues.py --check-only
echo "Exit: $?"   # must be 0

# Step 5 — sync tracked files & update accountability
python3 scripts/ci/auto_fix_common_issues.py --pattern 25
python3 scripts/ci/sync_tracked_files.py --fix

# Step 6 — commit
git add scripts/ci/auto_fix_common_issues.py scripts/ci/session_wrapup_autofix.py \
        docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md .secrets.baseline
git commit -m "fix(ci): cherry-pick Pattern 30 arity fix + CODEX_SKIP_PATTERN_NUMS recursion guard from scipy bump branch"
```

---

## ✅ Verification Checklist

After applying the cherry-pick, verify all of the following:

- [ ] `grep "swa._compute_merge_readiness_score()" scripts/ci/auto_fix_common_issues.py` — **no `str(self.repo_root)` argument**
- [ ] `grep "CODEX_SKIP_PATTERN_NUMS" scripts/ci/auto_fix_common_issues.py` — **present**
- [ ] `grep "CODEX_SKIP_PATTERN_NUMS" scripts/ci/session_wrapup_autofix.py` — **present**
- [ ] `python3 scripts/ci/auto_fix_common_issues.py --check-only; echo $?` → **exit 0**
- [ ] Pattern 30 output reads `✅ Pattern 30 (Merge Readiness): 100/100 — all dimensions green`

---

## ⚠️ DO NOT cherry-pick these files (branch-specific)

- `.codex/aftermath/pda_iterations.jsonl` — contains scipy-bump-specific PDA entry
- `.secrets.baseline` — contains hashes specific to scipy-bump branch state
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — auto-generated entry for this branch
- `CODEX_MANIFEST.json` — scipy 1.17.1 specific

---

## 🔇 WEC Note

After applying fixes, **uncheck `auto-approve-workflows`** in the PR #4077
WEC block to prevent the CI rescue workflow from triggering new Copilot
continuation sessions automatically.
