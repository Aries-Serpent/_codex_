# PR #4368 — What's Next

**PR:** #4368 - Harden safe pickle imports, fix EvaluationRunner NameError and CodeQL alert, resolve merge conflicts, self-heal CI and compatibility failures
**Branch:** `copilot/update-safe-pickle-import`
**Status:** 🟡 ACTIVE — awaiting merge approval after all validations pass
**Latest Session:** S899 (2026-05-09T06:52Z)
**Latest Commit:** `c9517ad7`

---

## 📋 Complete Progress Tracking

### ✅ Phase 1: Safe Pickle Hardening (COMPLETE — S889)
- [x] Added `src/codex_ml/safe_pickle.py` restricted unpickler with optional HMAC signing
- [x] Versioned signed payload parsing (v1/v2 format support)
- [x] Tighter allowlisting and atomic key-creation behaviour
- [x] Updated dataset loader imports to use safe_pickle
- [x] Added regression tests for safe pickle loading

### ✅ Phase 2: EvaluationRunner Robustness (COMPLETE — S890)
- [x] Hardened `EvaluationRunner.run()` to tolerate torch stubs missing `no_grad`
- [x] Added callable-only model fallback support
- [x] Fixed `NameError` in `elif forward` branch (used `model_call` from sibling `if predict` branch)
- [x] Corrected to call `self.model.forward(inputs)` directly

### ✅ Phase 3: CI Self-Healing Batch (COMPLETE — S890–S894)
- [x] `token=None` handling in `scripts/security/verify_token_scope.py`
- [x] Tokenizer streaming tests + lightweight `tokenizers` stub compatibility
- [x] `codex_cli` smoke-test patching (echo patched inside tests, not at import time)
- [x] Offline metrics tests for psutil-less environments
- [x] Legacy tokenization proxy behaviour fallback
- [x] OmegaConf shim: `${oc.env:...}` resolution + nested dotlist parsing
- [x] Non-Hydra `codex_ml.cli.evaluate` fallback for `key=value` args
- [x] `list_plugins --format json` stderr/log suppression
- [x] Package export compatibility (`codex.__all__`, lazy `codex_cli.app`)

### ✅ Phase 4: Stale Rescue Triage + Accountability (COMPLETE — S895)
- [x] Confirmed `PR Auto-Fix Check` failure on `9d3ecb25dc03` was stale
- [x] Refreshed CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md (Pattern 25)
- [x] Updated active follow-up prompt with post-merge Cognitive Brain continuation

### ✅ Phase 5: Merge Conflict Resolution + CodeQL Fix (COMPLETE — S896)
- [x] Resolved `.secrets.baseline` merge conflict (`--ours`, 2-parent merge commit)
- [x] Restored `tests/agents/test_phase2_deep_coverage_batch8.py` (syntax error from automated commit)
- [x] Restored `tests/agents/test_phase2_deep_coverage_batch11.py` (unclosed list literal)
- [x] Fixed CodeQL "potentially uninitialized variable" in `tests/evaluation/test_metrics.py` (`torch = None`)
- [x] Suppressed F401 in `tests/unit/test_sanity.py` with `# noqa: F401`
- [x] Clarified CodeQL-init comment in test_metrics.py

### ✅ Phase 6: S897 CI Rescue + Living Docs (COMPLETE)
- [x] Investigated `Detect CI Issues & Post Fix Instructions` failure on `4f10df026238`
  - Root cause: Pattern 25 — commit skipped CHANGELOG/accountability update
  - SHA drift + sandbox detection = informational-only false positives
- [x] Merged 5 remote [skip ci] auto-commits with conflict resolution
- [x] Confirmed all local validations clean (ruff ✅ · mypy 130 ✅ · auto_fix clean ✅)
- [x] Updated CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md (Pattern 25 ✅)
- [x] Created PR4368_whats_next.md + PR4368_session_diagram.md (living docs)
- [x] PR body 88/100 diagnosed and fixed (Pattern 25 root cause)
- [x] Updated PR-4368-followup.md with S897 completion + post-merge block

### ✅ Phase 7: Cognitive Brain — Shared Fallback Helpers + Rate-Limit Orchestration (COMPLETE)
- [x] Created `scripts/cognitive/cb_fallbacks.py`:
  - `import_optional(module, attr)` — safe soft-dependency importer
  - `with_fallback(func, default, exc_types)` — exception-swallowing optional-feature wrapper
  - `rate_limited_call(func, *args, resource, min_remaining, max_retries)` — GitHub API quota
    guard + exponential backoff using `github_api_trickle.py` (degrades gracefully offline)
- [x] Updated `scripts/cognitive/cognitive_brain_core.py`:
  - `PerceptionLayer.perceive()` — `import_optional("psutil")` + `with_fallback` for system load
  - `ActionExecutor.execute()` — `rate_limited_call` for every task dispatch + `_dispatch_task` stub
- [x] `tests/cognitive_brain/test_cb_fallbacks.py` — 19 tests, all passing ✅

### ✅ Phase 8 (Final): Workflow Monitor + startup_failure Triage (S897-final)
- [x] Identified 3 recurring startup_failures: Progressive Validation Suite, Rust-Python Hybrid Swarm CI/CD, Data Quality & Determinism Suite
- [x] Triaged root cause: pre-existing infra/runner allocation failure (not code) — confirmed by 301 other workflows using same `@v5` action refs successfully
- [x] commit `f0b2d5c3` workflow status (f0b2d5c3):
  - ✅ PR Comment Review Gate, Auto-Approve, Issue Resolution Gate, Agent Vars Bootstrap
  - 🔄 Pre-Merge Validation, CodeQL, Validation Pipeline, Auto-Fix Common CI Issues (in-progress)
  - ⏳ mypy Baseline, Deferral Language Gate, Branch Rebase Gate — awaiting WEC gate completion
  - ⏳ Agent Token Delegation, Workflow Execution Gate — action_required (approval round pending)
  - ❌ startup_failure (infra only): Progressive Validation Suite, Rust-Python Swarm, Data Quality Suite

### ✅ Phase 9: CB Expansion — PerceptionLayer Sensors + MemoryLayer LTM + ActionExecutor Targets (S898)
- [x] **PerceptionLayer expanded sensors**: `memory_available_mb`, `disk_free_gb`, `net_bytes_sent`,
  `net_bytes_recv` (psutil fallback), `ci_failure_count` (reads `.codex/rescue_context.json`).
  `SENSOR_NAMES` constant exposed. `sensors_active` key. Architecture promoted to 5-layer.
- [x] **MemoryLayer (SQLite LTM)**: `store_perception()`, `recall_recent()`, `recall_by_cycle()`,
  `ltm_size()`. Wired as Stage 1b in PDA cycle. Graceful SQLite-absent degradation.
- [x] **ActionExecutor dispatch targets**: `DISPATCH_TARGETS = ("internal", "workflow_dispatch",
  "post_comment", "approve_run")`. Stub implementations ready for real GH API wiring.
- [x] 18 new tests added — 37 total, all passing ✅
- [x] All 4 blocking PR comments replied to — PR Comment Review Gate unblocked
- [x] Pattern 25 refresh: CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md updated

### ✅ Phase 10: Merge Conflict + Test Isolation Fix (S899)
- [x] Resolved `CODEX_MANIFEST.json` conflict (3 new main commits) — took main version (auto-gen, P-045)
  — committed as true 2-parent merge commit (`04c718f3`)
- [x] Fixed `test_verify_scopes_without_token` env-token leakage: added `@patch.dict(os.environ, {}, clear=True)`
  + `@patch("scripts.security.verify_token_scope.os.getenv", return_value=None)` + `assert verifier.token is None`
- [x] 23/23 token verification tests passing ✅
- [x] Updated living docs (whats_next + session_diagram) for S899
- [x] ruff ✅ · mypy 130 ✅ · auto_fix clean ✅ · Pattern 25 ✅
- [x] CI on `c9517ad7`: 21 workflows in-progress (all approved by @mbaetiong); 3 known infra startup_failures

---

## 🔮 Post-Merge Continuation

After merge, open a new PR/session targeting:
1. **Wire ActionExecutor to real GH API** — implement `workflow_dispatch`, `post_comment`,
   `approve_run` with `rate_limited_call` + CODEX_MASTER_KEY token chain
2. **MemoryLayer LTM eviction** — implement 30-cycle retention policy, vacuum on overflow
3. **AAIS Reliability uplift** — sustain green CI across 14+ consecutive runs to drive `ci_failure_rate` to 0%
4. **T-03 admin action** — `security_events` scope on `CODEX_MASTER_KEY` (see `admin-action-t03.yml`)
5. **`Progressive Validation Suite` startup_failure** — investigate `.github/workflows/progressive-validation.yml` runner config

---

## 📊 Merge Readiness

| Dimension | Status |
|-----------|--------|
| ruff | ✅ clean |
| mypy | ✅ 130 = baseline |
| auto_fix_common_issues | ✅ clean |
| sync_tracked_files | ✅ consistent |
| Pattern 25 | ✅ CHANGELOG + accountability in every commit |
| CodeQL | ✅ 0 new alerts |
| Merge conflicts | ✅ resolved (S899: CODEX_MANIFEST.json) |
| Broken tests restored | ✅ |
| Token verification tests | ✅ 23/23 pass (env-isolation fix S899) |
| CB fallback helpers | ✅ 19/19 tests pass |
| CB PerceptionLayer sensors | ✅ 37/37 tests pass |
| CB MemoryLayer LTM | ✅ 37/37 tests pass |
| CB ActionExecutor targets | ✅ 37/37 tests pass |
| Process hardening | ✅ documented |
| PR Comment Review Gate | ✅ all blocking comments replied |
| CI (c9517ad7) | 🔄 21 in-progress (approved) · 3 infra startup_failure (pre-existing) |

