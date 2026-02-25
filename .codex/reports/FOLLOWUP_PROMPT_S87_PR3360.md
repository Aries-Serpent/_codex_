# Follow-Up Prompt S87 → S88

**PR:** #3360 (`copilot/sub-pr-3248-again` → `0D_base_`)
**Session:** S87 → S88 handoff
**Date:** 2026-02-24
**Latest commit:** `c1fc0d8`
**Branch:** `copilot/sub-pr-3248-again`

---

## S87 Completion Summary

| Task | Status | Commit |
|------|--------|--------|
| Resilient Suite slow — SafetyConfig @patch AttributeError (2 tests) | ✅ Fixed | c1fc0d8 |
| Resilient Suite slow — MLFLOW_TRACKING_URI env var isolation | ✅ Fixed | c1fc0d8 |
| RS-ARCH-001: Duplicate function detection | ✅ Complete (expected OOP patterns) | — |
| RS-ARCH-002: `__init__.py` gap scan | ✅ 4 gaps fixed | c1fc0d8 |
| Cognitive brain S87 | ✅ Done | c1fc0d8 |
| Follow-up S88 | ✅ This file | c1fc0d8 |

---

## S88 Priority Queue

### 🔴 P0 — Full CI Verification (MANDATORY FIRST STEP)

**Per AI Codebase Agency Policy: NEVER declare CI green without checking ALL workflows**

```
Check ALL of these on latest commit c1fc0d8:
- Art_Validation Pipeline / Fast Validation
- Resilient Validation Suite / validation (quick)
- Resilient Validation Suite / validation (slow)
- Resilient Validation Suite / validation (integration)
- Pre-Flight CI Validation
- Pre-Merge Validation
- Art_Rust-Python Hybrid Swarm CI/CD / Code Coverage
- Code scanning results / CodeQL (2 alerts from 67a3808 — check if resolved)
```

Fix ALL failures before proceeding. Do not declare CI green until ALL workflows are checked.

### 🔴 P1 — CodeQL Alerts (from 67a3808)

The comment mentioned "2 new CodeQL alerts including 1 error". API access is 403 so cannot read them directly. Check:
1. What files were changed in `86ce05b` that introduced code changes (superposition.py, evaluate.py patterns)
2. Run CodeQL proactively on changed source files
3. Use `codeql_checker` tool after all code changes are complete

### 🟡 P2 — AGENT_REGISTRY.yaml expansion (53 → 70+)

Current state: 36 registered, 182 files in `.github/agents/`.
True agent files (`.agent.md`, `*-agent.md`) ≈ 70.

Action: Update `AGENT_REGISTRY.yaml` to register all true agent files (not doc/status files).
```bash
# Find true agent files
ls .github/agents/*-agent.md .github/agents/*.agent.md .github/agents/*.agent.yml 2>/dev/null | wc -l
```

### 🟡 P3 — Merge Gate Preparation

**S89 will merge regardless of green status.** Prepare:
- Document all remaining flaky/known-failing tests in `.codex/HOTFIX_POST_MERGE_PLAN.md`
- Update `.codex/PR_3248_FAILURE_TRACKING_LOG.md` with S87 fixes
- Create S89_FINAL_STATUS.md template

### 🟢 P4 — Coverage Phase 23–26

Target: 90% overall.
Inspect latest CI coverage report artifact for gap modules.

---

## Cumulative Fix Summary (S85–S87)

| Session | Fixes | Tests Fixed |
|---------|-------|-------------|
| S85 | 4 test failures + 7 EOF violations + 4 PR comments | `test_resume_flag`, `test_compression_effectiveness`, `test_dataset_manager_create_archive`, `test_resume_error_is_recorded` |
| S86 | 4 CI failures | `test_performance_within_limits`, `test_run_functional_training_resume`, pre-flight check, Fast Validation |
| S87 | 3 test failures + 4 `__init__.py` gaps | `test_sanitize_prompt_list_with_strings`, `test_sanitize_prompt_list_with_dicts`, `test_enable_mlflow_without_uri` |
| **Total** | **11 test failures + 11 infra fixes** | |

---

## Pattern Library P-023–P-034 (Quick Reference)

| ID | Trigger | Fix |
|----|---------|-----|
| P-025 | `format.endswith(".tar.gz")` never matches | `format in {"tar", "tar.gz"}` |
| P-026 | Mock returns `Path`; caller unpacks 2-tuple | Return `(Path, CheckpointMeta)` |
| P-027 | `epochs < 1` rejects `epochs=0` | Validate `epochs < 0` |
| P-028 | gzip expands < 1 KB files | Guard `size_original >= 1024` |
| P-029 | JSON/MD missing `\n`; YAML trailing blank | Apply `end-of-file-fixer` |
| P-030 | Plugin pins in composite action, not workflow | Extend scan to `.github/actions/*/action.yml` |
| P-031 | `Decision(evaluator=func)` wrong kwarg | `Decision(name=id, evaluation_fn=func)` |
| P-032 | `HFModelUnavailableError` — no network in CI | `try/except: pytest.skip(...)` |
| P-033 | `@patch("module.NAME")` AttributeError | Move import to module level with `None` fallback |
| P-034 | Env var contamination (`MLFLOW_TRACKING_URI`) | `patch.dict` + `pop` in test scope |

---

## Critical Reminders for S88

- ✅ NEVER declare CI green without querying `list_workflow_runs` for ALL workflow names
- ✅ Run `pre-commit run trailing-whitespace end-of-file-fixer` on all new files
- ✅ Use `codeql_checker` AFTER code_review, BEFORE finalizing
- ✅ S89 merges regardless of green status — document all flaky tests in HOTFIX plan

---

**Generated:** 2026-02-24T22:55:00Z
**Next session:** S88
