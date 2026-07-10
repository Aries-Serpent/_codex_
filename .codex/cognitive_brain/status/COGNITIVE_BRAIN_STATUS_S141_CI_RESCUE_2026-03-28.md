# Cognitive Brain Status — S141 CI Rescue + PR Review + Lifecycle Doc

> **Session:** S141 (2026-03-28)  
> **Branch:** `0D_base_` (PR #3777)  
> **Previous:** COGNITIVE_BRAIN_STATUS_S138_N9_N10_N11_2026-03-28.md  
> **Status:** ✅ Complete  
> **Commit:** `3f60148`  

---

## 🎯 Session Objectives

| Objective | Status | Notes |
|-----------|--------|-------|
| Fix mypy CI regression (342 > 306 baseline) | ✅ Done | 9 new errors fixed; baseline 306→333 |
| Apply PR review items | ✅ Done | 3 files updated |
| Create PR lifecycle document | ✅ Done | `docs/ci/PR_LIFECYCLE.md` |
| Update cognitive brain status | ✅ Done | This file |
| Update objectives tracker | ✅ Done | v1.6.0, S141 row added |
| Update accountability report | ✅ Done | S141 session summary |

---

## 🔍 Root Cause Analysis — mypy CI Regression

### Background

Session S139 fixed the `src/services/crawler/__init__.py` import regression (P19-BATCH-WATCH-001)
and lowered `.mypy_baseline` from 333 → 306. However, the baseline was set using the **local
fully-installed environment** (all packages: pydantic, PyJWT, cryptography, etc.), giving 306 errors.
The **CI isolated venv** (only `mypy>=1.8.0, types-PyYAML, types-requests`) gives **333 errors**.

The 27-error gap exists because `mypy.ini` has `warn_unused_ignores = True`:
- Locally with packages installed: `# type: ignore` annotations suppress real errors → not "unused"
- In CI without packages: imports are ignored silently → `# type: ignore` is redundant → `unused-ignore`

### New Errors Introduced by P19 Backfill

Additionally, the P19 backfill (S137/S138) introduced **9 new CI-specific errors**:

| File | Error | Root Cause | Fix |
|------|-------|-----------|-----|
| `src/codex/zendesk/agent.py:9` (×2) | `Module "tools" has no attribute "ToolRegistry"` | Root `./tools/__init__.py` shadows `src/tools/` | Reverted to `from src.tools import` |
| `src/codex_ml/tokenization/train_tokenizer.py:25,31` (×2) | Variable not valid as type | `TrainTokenizerConfig = module.attr` not type alias | Explicit `from tokenization.train_tokenizer import TrainTokenizerConfig as TrainTokenizerConfig` |
| `src/codex/zendesk/monitoring/mcp_bridge.py:30,32,33,35` (×4) | Unused `# type: ignore[arg-type]` | `mcp.*` now resolvable; `set_gauge(float)` correct | Removed redundant annotations |
| `src/mcp/server/jsonrpc_adapter.py:60` (×1) | Unused `# type: ignore[return-value]` | `BackendAdapter` now resolvable | Removed redundant annotation |

### Resolution

1. Fixed all 9 new errors in source files
2. Updated `.mypy_baseline` from 306 → **333** using CI isolated venv
3. Verified: CI venv now reports 333 = 333 baseline → ✅ PASS

---

## 📝 PR Review Items Applied

From `copilot-pull-request-reviewer` on commit `1cdbcd7`:

### Item 1: `scripts/codex_offline_audit.py:73-76`
**Issue:** Only `REPO_ROOT` on `sys.path`; P19 imports (`from experiments ...`) need `src/` on path.  
**Fix:** Added `REPO_ROOT / "src"` to `sys.path` for direct script invocation.

### Item 2: `scripts/ci/auto_fix_common_issues.py:1504-1506`
**Issue:** `list({...})` builds list from set — non-deterministic ordering in CI logs.  
**Fix:** Changed to `sorted({...})` for stable, diff-friendly output.

### Item 3: `tests/space_traversal/test_peft_comprehensive/test_extended_trainer.py:31-34`
**Issue:** Mixed `src.training.trainer` (src.) and `logging_utils` (non-src.) imports.  
**Fix:** Changed `import src.training.trainer as trainer_mod` → `import training.trainer as trainer_mod`. File already adds `src/` to `sys.path` before imports.

---

## 📄 PR Lifecycle Document Created

**File:** `docs/ci/PR_LIFECYCLE.md`

Covers:
- Phase 1 (pre-approval) / Phase 2 (token gate) / Phase 3 (post-approval) lifecycle
- Workflow trigger map for all 10 relevant workflows
- Copilot session startup triggers (5 trigger types)
- Expected failing checks and known flaky patterns
- Rescue & self-healing chain (7-step cascade)
- Mermaid flowchart lifecycle diagram
- Mermaid sequence diagram for rescue flow
- Historical CI log cross-reference (runs 23689574622–23692231510)
- Root cause analysis for mypy environment mismatch

---

## 📊 Pattern Learning

### P19-ENV-001 — mypy Baseline Environment Parity

**Rule:** `.mypy_baseline` MUST be set using the CI isolated venv (matching CI's environment),
NOT the local fully-installed environment.

**Why:** `warn_unused_ignores = True` causes environment-dependent error counts. With installed
packages, mypy can see type errors that `# type: ignore` annotations hide. In CI without packages,
those annotations become "unused".

**How:** Set baseline using:
```bash
python -m venv /tmp/mypy-check-venv --clear
/tmp/mypy-check-venv/bin/pip install "mypy>=1.8.0" types-PyYAML types-requests
/tmp/mypy-check-venv/bin/python scripts/ci/mypy_baseline.py --update
```

### P19-SHADOW-001 — Root-Level Package Name Conflicts

**Rule:** When a module name used in `src/` also exists as a directory at REPO_ROOT (e.g.,
`./tools/`, `./agent/`), the P19 `from src.X` → `from X` substitution causes mypy to find the
wrong module. Keep `from src.X` for conflicting names.

**Known conflicts:**
- `tools` — `./tools/__init__.py` exists at REPO_ROOT; conflicts with `src/tools/`

**Detection:** `ls ./X/__init__.py` where X is the package being de-src-ified.

---

## 📋 Next-Phase Plan (N14 onwards)

### N14 — P19 Continued Backfill (Priority: Low, Ongoing)
- **Remaining:** ~252 files (unchanged — S141 fixes were in src/ not tests/)
- **Method:** P19-BATCH-001 + P19-SHADOW-001 check before each file
- **Next targets:** `tests/agent/`, `tests/agents/`

### N15 — P21 Deadline Watch (Priority: Monitor, Deadline: 2026-06-02)
- **Status:** All 7 action families upgraded ✅ — no violations
- **Run:** `python3 scripts/ci/auto_fix_common_issues.py --check-only | grep "Pattern 21"`

### N16 — PR Lifecycle doc alignment (Priority: Low)
- `docs/ci/PR_LIFECYCLE.md` created — verify Mermaid renders on GitHub
- Update as new workflows are added or rescue patterns discovered

---

## 🔗 Cross-References

- `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` — S141 session summary
- `.codex/cognitive_brain/objectives_tracker.md` — v1.6.0, S141 sweep row
- `.github/agents/codebase-health-guardian.md` — v2.5, S141 row
- `docs/ci/PR_LIFECYCLE.md` — NEW: full PR lifecycle documentation
- `.mypy_baseline` — 333 (CI isolated-venv count)
- `src/codex/zendesk/agent.py` — `from src.tools import` (shadow pattern)
- `src/codex_ml/tokenization/train_tokenizer.py` — explicit TrainTokenizerConfig re-export
