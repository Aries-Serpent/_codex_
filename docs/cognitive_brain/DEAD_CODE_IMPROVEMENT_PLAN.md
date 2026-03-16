# Dead Code & Incomplete Feature Improvement Plan

**Generated:** 2026-03-16  
**Source:** Codebase-wide vulture scan (PR #3586 Session S118–S119)  
**Policy:** Per AI Agency Policy — no placeholder removed without full assessment.  
All items are either **implemented in this session** or **added to the ongoing
Cognitive Brain improvement backlog** below.

---

## ✅ Implemented in This Session (PR #3586)

| # | File | Issue | Fix Applied |
|---|------|-------|-------------|
| 1 | `src/codex/rag/gpu_utils.py` | `max_memory_gb` param ignored — free memory used without cap | Capped `free_memory` by `max_memory_gb` before computing batch size |
| 2 | `src/codex_ml/utils/checkpoint_core.py` | `_environment_summary` imported but local implementation used instead | `capture_environment_summary()` now delegates to provenance module first; falls back to local |
| 3 | `src/codex/quality/cli.py` | `fail_on`/`warn_on` CLI params parsed but never applied | Implemented severity-based exit logic: maps category names to counts; exits 1 if any `--fail-on` category has findings |
| 4 | `src/codex_ml/utils/checkpointing.py` | `capture_error` defined/imported but never called | Wired into `save_checkpoint` and `load_checkpoint` exception handlers |

---

## 🔴 High Priority — Cognitive Brain Backlog

### CB-001: `security/decorators.py` — JWT Token Validation Stub
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

### CB-002: `cognitive_brain/quantum/superposition.py` — Quantum Superposition Decorator
**File:** `src/cognitive_brain/quantum/superposition.py:609`  
**Pattern:** `quantum_superposition(enabled_config_attr, fallback_on_low_coherence)` parameters
defined but decorator body ignores them — always calls original function  
**Current state:** Placeholder closure — no quantum coherence check performed  
**Required implementation:**
1. Accept agent config context via `_QuantumContext` thread-local or first positional arg
2. Check `config.<enabled_config_attr>` to determine if quantum path is active
3. Invoke `QuantumSuperpositionEngine` to score decision options
4. If `engine.coherence() < coherence_threshold` and `fallback_on_low_coherence=True`,
   fall back to classical path
5. Log quantum vs classical execution path for observability

**Integration:** Wire `QuantumSuperpositionEngine` (already in
`src/cognitive_brain/quantum/superposition.py`) into the decorator's closure.

---

### CB-003: `cognitive_brain/quantum/compression.py` — PatternCompressor Integration
**File:** `src/cognitive_brain/quantum/compression.py`  
**Size:** 448 lines, full PCA/quantization implementation  
**Current state:** Complete implementation — no callers in `src/`  
**Required integration:**
1. Import `PatternCompressor` in `src/cognitive_brain/pattern_library.py` (or equivalent)
2. Use `PatternCompressor.fit(patterns)` when storing large pattern sets in `SQLiteMemory`
3. Use `PatternCompressor.compress(pattern)` on write, `decompress()` on read
4. Add integration test: compress 1 000 patterns → verify round-trip fidelity ≥ 99%

**Acceptance criteria:** Pattern retrieval latency ≤ 10 ms for 10k stored patterns.

---

### CB-004: `codex/agents/brain_client.py` — BrainClient Wire-up
**File:** `src/codex/agents/brain_client.py`  
**Size:** 468 lines, complete HTTP client  
**Current state:** Complete implementation — referenced in `github_app.py` docstring only  
**Required integration:**
1. Inject `BrainClient` into `CognitiveBrainSessionInjector` via constructor
2. Use `BrainClient.memory_search()` during session pre-flight to load context
3. Use `BrainClient.run_command()` to delegate CLI operations to the brain API
4. Add health check: `BrainClient.is_available()` gating before every call
5. Add `brain_client.yml` test fixture for offline mock

**Acceptance criteria:** Session injector test verifies memory_search is called with
agent name as query.

---

### CB-005: `codex/ast/visualize.py` — HTMLVisualizer Integration
**File:** `src/codex/ast/visualize.py`  
**Size:** 145 lines, HTML AST renderer  
**Current state:** No tests, no callers  
**Required integration:**
1. Register as `codex ast-view` CLI subcommand in `src/codex/cli.py`
2. Accept `--output <file.html>` and `--open` flags
3. Add at least 3 unit tests covering node rendering, tree depth, and CSS output
4. Wire into `codex-ast-upgrade` flow to optionally preview transformation diff

---

### CB-006: `codex/api/auth_routes.py` — Mount in App Factory
**File:** `src/codex/api/auth_routes.py`  
**Size:** 360 lines, complete FastAPI auth router (register/login/logout/refresh/CSRF)  
**Current state:** Router created but never mounted in app factory  
**Required integration:**
1. Locate or create `src/codex/api/app.py` / `src/codex/api/factory.py`
2. Call `app.include_router(create_auth_router(...), prefix="/api/auth")`
3. Ensure rate-limiter parameters come from config (not hardcoded)
4. Add integration test using `httpx.AsyncClient` against mounted app

---

### CB-007: `train_loop.py` — Data Loaders Pipeline Integration
**File:** `src/codex_ml/train_loop.py:142`  
**Pattern:** `from codex_ml.data import loaders as data_loaders` — module doesn't exist yet  
**Current state:** Import falls back to `None`; no code path uses `data_loaders`  
**Required implementation:**
1. Create `src/codex_ml/data/loaders.py` with `DataLoader`, `StreamingDataLoader` classes
2. Wire `data_loaders.get_loader(dataset_path, batch_size)` into the training epoch loop
3. Replace direct dataset iteration in `TrainLoop._run_epoch()` with loader abstraction
4. Register as `codex_ml.data_loaders` entry point in `pyproject.toml`

---

## 🟡 Medium Priority — Quality Backlog

### QA-001: `session_logger.py` — `_shared_init_db` Explicit Init
**File:** `src/codex/logging/session_logger.py:57`  
**Pattern:** `init_db as _shared_init_db` imported but never called  
**Assessment:** DB init is currently lazy (first log event). `_shared_init_db` was
designed for explicit pre-flight initialization (e.g., when the agent knows the session DB
path in advance). Lazy init is safe but explicit init allows early failure detection.  
**Recommendation:** Call `_shared_init_db(db_path)` inside `SessionLogger.__init__()` when
`db_path` is explicitly provided. Keep lazy fallback for default path.

---

### QA-002: `intelligent_analyzer.py` — Unused `sr` Parameter
**File:** `src/services/audio/analysis/intelligent_analyzer.py:91,109`  
**Pattern:** `sr` (sample rate) parameter passed to `_classify_content` and
`_detect_problems` but never used inside either method — feature extraction already
includes frequency domain data  
**Assessment:** Either remove `sr` from method signatures (callers pass `features` dict
which already encodes sample-rate dependent features) OR use `sr` for time-domain
normalisation of `rms_energy` in `_detect_problems`.  
**Recommendation:** Remove `sr` from both method signatures to clarify the interface.

---

## 📊 False Positives — No Action Required

| File | Item | Reason |
|------|------|--------|
| `adapter.py:69` | `_SentencePieceAdapter` | `TYPE_CHECKING` guard — never loaded at runtime |
| `audit/cli.py:16` | `check_dependencies`, `check_vulns` | Click command parameters — used via Click framework |
| `train_loop.py` | `apply_lora` | Used at line 1442 (`if lora and apply_lora is not None`) |
| `superposition.py` outer params | As decorator outer params | Used as public API config surface; inner closure is the placeholder |
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
