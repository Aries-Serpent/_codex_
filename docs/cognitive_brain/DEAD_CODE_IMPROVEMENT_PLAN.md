# Dead Code & Incomplete Feature Improvement Plan

**Generated:** 2026-03-16  
**Updated:** 2026-03-16 (S120 — all CB items addressed)  
**Source:** Codebase-wide vulture scan (PR #3586 Session S118–S119)  
**Policy:** Per AI Agency Policy — no placeholder removed without full assessment.  
All items are either **implemented in this session** or **added to the ongoing
Cognitive Brain improvement backlog** below.

---

## ✅ Implemented in This Session (PR #3586)

| # | File | Issue | Fix Applied | Session |
|---|------|-------|-------------|---------|
| 1 | `src/codex/rag/gpu_utils.py` | `max_memory_gb` param ignored — free memory used without cap | Capped `free_memory` by `max_memory_gb` before computing batch size | S119 |
| 2 | `src/codex_ml/utils/checkpoint_core.py` | `_environment_summary` imported but local implementation used instead | `capture_environment_summary()` now delegates to provenance module first; falls back to local | S119 |
| 3 | `src/codex/quality/cli.py` | `fail_on`/`warn_on` CLI params parsed but never applied | Implemented severity-based exit logic: maps category names to counts; exits 1 if any `--fail-on` category has findings | S119 |
| 4 | `src/codex_ml/utils/checkpointing.py` | `capture_error()` defined but never called | Wired into `save_checkpoint` and `load_checkpoint` exception handlers | S119 |
| 5 | `src/codex_ml/train_loop.py` | CB-007: `data_loaders` import fell back to `None` | `codex_ml.data.loaders` module already exists; import resolves correctly — marked resolved | S119 |
| 6 | `src/security/decorators.py` | **CB-001**: `get_token_scopes` raises `NotImplementedError` (security-critical stub) | Implemented JWT validation via `TokenManager.validate_token()`; reads `CODEX_AUTH_SECRET` from env; returns space-split `scope` claim as list | S120 |
| 7 | `src/cognitive_brain/quantum/superposition.py` | **CB-002**: `quantum_superposition` decorator ignores `enabled_config_attr`, `fallback_on_low_coherence`, `coherence_threshold` | Decorator now checks config attribute on `self`, invokes `SuperpositionEngine.evaluate_superposition()` for coherence measurement, and gates fallback on coherence threshold | S120 |
| 8 | `src/codex/cognitive/session_hook.py` | **CB-003**: `PatternCompressor` (448-line PCA/quantization engine) has no callers | Wired as optional lazy component of `CognitiveBrainSessionInjector._build_payload()`; activated for pattern sets ≥ 10 items; compress-then-decompress round-trip preserves numeric metadata | S120 |
| 9 | `src/codex/cognitive/session_hook.py` | **CB-004**: `BrainClient` (468-line HTTP client) not injected into session injector | Added optional `brain_client` param to `__init__`; pre-flight `is_available()` check in `inject()`; `memory_search()` augments wave-collapse in `_quantum_reconstruct()` | S120 |
| 10 | `src/codex/api/app.py` | **CB-006**: `auth_routes.py` router never mounted in app factory | Added `include_router(create_auth_router(), prefix="/api/auth")` with `ImportError` guard | S120 |
| 11 | `src/codex/cli/main.py` | **CB-005**: `HTMLVisualizer` has no CLI entrypoint | Registered `ast-view` typer subcommand with `--output` and `--open` flags | S120 |
| 12 | `src/services/audio/analysis/intelligent_analyzer.py` | **QA-002**: `sr` param passed to `_classify_content`/`_detect_problems` but never used | Removed `sr: int` from both signatures and updated all call sites | S120 |
| 13 | `src/codex/logging/session_logger.py` | **QA-001**: `_shared_init_db` imported but never called on explicit `db_path` | Added `__post_init__` to `SessionLogger`; calls `_shared_init_db(db_path)` eagerly when path provided | S120 |

---
**File:** `src/security/decorators.py:219`  
**Pattern:** `get_token_scopes(credentials)` raises `NotImplementedError`  
**Risk:** 🔴 **Security-critical** — any code path that reaches this function will raise,
ensuring fail-closed behaviour. However, the stub must be replaced before production.  
**Required implementation:**
1. Decode JWT bearer token from `credentials.credentials`
2. Validate signature using public key from `CODEX_MASTER_KEY` / JWK endpoint
3. Extract `scope` claim as list of strings
4. Return scopes for downstream `require_scope()` decorator checks

**Acceptance criteria:** Unit test with mock JWT, integration test against `/api/auth/login`
response token.

---

## 🔴 Remaining Backlog (Pending Design Decisions)

> All CB-001 through CB-007 and QA-001/QA-002 items have been implemented or resolved
> in S119–S120. The items below reflect secondary acceptance-criteria gaps (tests,
> further integration) that require deeper design work before they can be closed.

### CB-001 Follow-up: JWT Integration Tests
**Status:** Core implementation ✅ done (`TokenManager.validate_token()` wired in S120)  
**Remaining:** Add unit test with mock JWT and integration test against `/api/auth/login`.  
**Acceptance criteria:** Test validates expired-token → 401, invalid-token → 401, valid-token → scope list.

---

### CB-004 Follow-up: `brain_client.yml` Test Fixture
**Status:** BrainClient wired into `CognitiveBrainSessionInjector` in S120.  
**Remaining:** Add `brain_client.yml` offline mock fixture so session injector tests don't require a live brain server.  
**Acceptance criteria:** `test_inject_with_brain_client.py` runs offline and verifies `memory_search()` is called with agent name.

---

### CB-005 Follow-up: HTMLVisualizer Tests
**Status:** `ast-view` CLI subcommand registered in S120.  
**Remaining:** Add 3 unit tests: node rendering, tree depth, CSS output.  
**Acceptance criteria:** `pytest tests/ast/test_visualizer.py -v` passes.

---

## 📊 False Positives — No Action Required

| File | Item | Reason |
|------|------|--------|
| `adapter.py:69` | `_SentencePieceAdapter` | `TYPE_CHECKING` guard — never loaded at runtime |
| `audit/cli.py:16` | `check_dependencies`, `check_vulns` | Click command parameters — used via Click framework |
| `train_loop.py` | `apply_lora` | Used at line 1442 (`if lora and apply_lora is not None`) |
| `superposition.py` outer params | As decorator outer params | ✅ Now wired — `enabled_config_attr` + `coherence_threshold` + `fallback_on_low_coherence` fully implemented (S120) |
| `cognitive_brain/meta_cognitive_reflection.py` | `MetaCognitiveReflectionLayer` | 15+ tests, part of cognitive brain system |
| `codex/cli.py` | `train_cmd`, `duplication_*` | Click subcommands registered via `main.add_command` |

---

## 🔗 Related Issues

- PR #3586 — original dead code scan and fixes  
- Issue #3587 — CI failure triage report  
- `.codex/patterns/ci_failure_patterns.yaml` — `DEAD_CODE_100_CONFIDENCE` pattern added  
- `scripts/ci/dead_code_scan.py` — CI tool for ongoing enforcement  
- `.pre-commit-config.yaml` — `dead-code-scan` pre-push hook (100% confidence gate)

---

_This document is the authoritative record of dead code disposition.  
Update this file whenever a backlog item is implemented._
