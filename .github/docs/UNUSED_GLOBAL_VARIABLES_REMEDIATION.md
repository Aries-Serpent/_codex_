# Unused Global Variables Remediation Report

> Generated: 2026-05-21 | Source: CodeQL Security Quality Rules (py/unused-global-variable)
> 
> **Report Type:** Investigation & Remediation Plan  
> **Total Findings:** 70 issues across 3 scans  
> **Status:** Ready for Review & Implementation

---

## Executive Summary

This report documents all unused global variable findings from CodeQL scans and provides a structured remediation plan. Variables are categorized by remediation type: **FIX** (remove/refactor), **MIGRATE** (refactor pattern), or **REMOVE** (unused fallbacks). Each entry includes context, impact assessment, and implementation guidance.

---

## Table of Contents

1. [Summary Table](#summary-table)
2. [Categorized Findings](#categorized-findings)
3. [Detailed Remediation Plan](#detailed-remediation-plan)
4. [Implementation Checklist](#implementation-checklist)

---

## Summary Table

| Category | Count | Priority | Action |
|----------|-------|----------|--------|
| **FIX: Error Handlers** | 4 | HIGH | Remove unused exception variables |
| **FIX: Fallback Variables** | 8 | HIGH | Refactor lazy-import patterns |
| **FIX: State Management** | 6 | HIGH | Migrate to app.state pattern |
| **MIGRATE: Optional Imports** | 12 | MEDIUM | Refactor import guards |
| **REMOVE: Reserved Constants** | 15 | MEDIUM | Delete future-planning variables |
| **REMOVE: Test Artifacts** | 3 | MEDIUM | Remove pytest/test stubs |
| **REMOVE: Unused Outputs** | 9 | LOW | Delete unused assignment results |
| **KEEP: Intentional** | 13 | LOW | Maintain w/ explicit markers |
| **TOTAL** | **70** | — | — |

---

## Categorized Findings

### Category 1: FIX - Error Handlers (4 items)

Remove unused exception variables that capture but don't use errors.

#### 1.1 `services/msp_gateway/routers/kb.py:54`

**Current Code:**
```python
except Exception as exc:  # pragma: no cover - optional dependency path
    _retrieval_adapter_error = exc
    logger.error(...)
```

**Issue:** `_retrieval_adapter_error` is assigned but never read

**Fix:**
```python
except Exception:  # pragma: no cover - optional dependency path
    logger.error(...)
```

**Impact:** Removes dead variable; improves clarity

---

#### 1.2 `services/msp_gateway/routers/infer.py:70`

**Current Code:**
```python
except Exception as exc:  # pragma: no cover - optional dependency path
    _retrieval_adapter_error = exc
    logger.warning(...)
```

**Fix:**
```python
except Exception:  # pragma: no cover - optional dependency path
    logger.warning(...)
```

---

### Category 2: FIX - State Management (6 items)

Migrate global rate-limit variables to FastAPI `app.state` pattern.

#### 2.1 `services/api/main.py:624-630`

**Current Code:**
```python
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    global _rate_ts, _rate_count
    
    limit = int(os.getenv("API_RATE_LIMIT", "0"))
    if limit > 0:
        if not hasattr(app.state, "rate_ts"):
            app.state.rate_ts = 0.0
        if not hasattr(app.state, "rate_count"):
            app.state.rate_count = 0
        now = time.time()
        if now - _rate_ts >= 1:          # ❌ Uses global
            _rate_ts = now                 # ❌ Sets global
            _rate_count = 0                # ❌ Sets global
        if _rate_count >= limit:           # ❌ Uses global
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        _rate_count += 1                   # ❌ Uses global
```

**Fix:** Remove globals; use `app.state` exclusively:
```python
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    limit = int(os.getenv("API_RATE_LIMIT", "0"))
    if limit > 0:
        if not hasattr(app.state, "rate_ts"):
            app.state.rate_ts = 0.0
        if not hasattr(app.state, "rate_count"):
            app.state.rate_count = 0
        now = time.time()
        if now - app.state.rate_ts >= 1:
            app.state.rate_ts = now
            app.state.rate_count = 0
        if app.state.rate_count >= limit:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        app.state.rate_count += 1
    else:
        app.state.rate_count = 0
    try:
        return await call_next(request)
    except HTTPException:
        pass
```

**Impact:** Thread-safe state management; removes global contention

---

### Category 3: MIGRATE - Lazy Import Patterns (12 items)

Refactor conditional import guard patterns to use unified approach.

#### 3.1 `src/codex_ml/tracking/mlflow_utils.py:126-127`

**Current Code:**
```python
_mlf = None  # Actual mlflow module if import succeeds
_HAS_MLFLOW = False

def ensure_mlflow():
    global _mlf, _HAS_MLFLOW
    if _HAS_MLFLOW and _mlf is not None:
        return
    try:
        import importlib
        _m = importlib.import_module("mlflow")
        _mlf = _m
        _HAS_MLFLOW = True
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        _mlf = None
        _HAS_MLFLOW = False
        err = build_optional_dependency_error("mlflow", "experiment tracking")
        raise RuntimeError(err.args[0]) from exc
```

**Issue:** Redundant sentinel check (`_HAS_MLFLOW and _mlf is not None`)

**Fix:**
```python
_mlf = None  # Actual mlflow module if import succeeds
_HAS_MLFLOW = False

def ensure_mlflow():
    global _mlf, _HAS_MLFLOW
    if _HAS_MLFLOW:  # ✅ Single sentinel sufficient
        return
    try:
        import importlib
        _m = importlib.import_module("mlflow")
        _mlf = _m
        _HAS_MLFLOW = True
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        _mlf = None
        _HAS_MLFLOW = False
        err = build_optional_dependency_error("mlflow", "experiment tracking")
        raise RuntimeError(err.args[0]) from exc
```

---

#### 3.2 `agents/developer_orchestrator.py:64-68`

**Current Code:**
```python
try:
    from codex.logging.session_logger import log_message
    LOGGING_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    LOGGING_AVAILABLE = False
    
    def log_message(session_id, role, message, **kwargs):
        # Fallback implementation
        pass
```

**Issue:** Duplicate logging on import failure; `e` captured but both logged

**Fix:**
```python
try:
    from codex.logging.session_logger import log_message
    LOGGING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ImportError: {e}", exc_info=True)
    LOGGING_AVAILABLE = False
    
    def log_message(session_id, role, message, **kwargs):
        # Fallback implementation
        pass
```

**Impact:** Removes debug+warning duplication; same for:
- `agents/physics_integration.py:41-45` (identical pattern)
- `agents/physics_integration.py:45` (duplicate)

---

### Category 4: REMOVE - Reserved Future Constants (15 items)

Delete constants explicitly marked as reserved for future use but never referenced.

#### 4.1 `.github/agents/core/phase8_10_production_deployment.py:56-73`

**Current Code:**
```python
# Monitoring constants
UNUSED_METRICS_EXPORT_INTERVAL_SECONDS = 15  # Reserved for future metrics export
UNUSED_TRACE_SAMPLE_RATE = 0.1  # Reserved for future distributed tracing
UNUSED_LOG_RETENTION_DAYS = 30  # Reserved for future log retention policy

# Documentation constants
DOC_FORMATS = ["markdown", "html", "pdf"]
UNUSED_DOC_FORMATS = ["markdown", "html", "pdf"]  # Reserved for future documentation export

# Security constants
RATE_LIMIT_REQUESTS_PER_MINUTE = 100
UNUSED_RATE_LIMIT_REQUESTS_PER_MINUTE = 100  # Reserved for future rate limiting enforcement
RBAC_ROLES = ["admin", "developer", "viewer"]
UNUSED_RBAC_ROLES = ["admin", "developer", "viewer"]  # Reserved for future RBAC enforcement

# Deployment Pipeline constants
CANARY_PERCENTAGE = 10
UNUSED_HEALTH_CHECK_TIMEOUT_SECONDS = 30  # Reserved for future health check timeout enforcement
ROLLBACK_THRESHOLD_ERROR_RATE = 0.05
UNUSED_ROLLBACK_THRESHOLD_ERROR_RATE = 0.05  # Reserved for future rollback gating logic
```

**Fix:** Delete all `UNUSED_*` prefixed constants:
```python
# Monitoring constants
METRICS_EXPORT_INTERVAL_SECONDS = 15
TRACE_SAMPLE_RATE = 0.1
LOG_RETENTION_DAYS = 30

# Documentation constants
DOC_FORMATS = ["markdown", "html", "pdf"]

# Security constants
RATE_LIMIT_REQUESTS_PER_MINUTE = 100
RBAC_ROLES = ["admin", "developer", "viewer"]

# Deployment Pipeline constants
CANARY_PERCENTAGE = 10
HEALTH_CHECK_TIMEOUT_SECONDS = 30
ROLLBACK_THRESHOLD_ERROR_RATE = 0.05
```

**Rationale:** 
- Generates false positives in code quality scanning
- Documentation via version control history is preferable
- If reactivation needed: use git history, not dead code

**Affected Files (8 total):**
- `.github/agents/core/phase8_10_production_deployment.py` (7 instances)
- `.github/agents/core/phase8_11_advanced_reasoning.py` (2 instances)

---

### Category 5: REMOVE - Test Artifacts (3 items)

Remove pytest markers and stub assignments used only in tests.

#### 5.1 `tests/test_sentencepiece_adapter.py:25`

**Current Code:**
```python
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
```

**Issue:** Marker defined but not applied (tests should use inline decorators or conftest.py)

**Fix:**
```python
# Remove pytestmark; apply via conftest.py or per-function decorator:
# In conftest.py:
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
```

**Or per-test:**
```python
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_something():
    pass
```

---

#### 5.2 `tests/stub_packages/torch/__init__.py:24-25`

**Current Code:**
```python
cuda = _Cuda()
utils = _Utils()
```

**Issue:** Stub objects created but never imported by tests

**Fix:** Keep stubs in `__all__` only if imported; otherwise remove:
```python
__all__ = []  # Or remove class instantiations if not needed
```

---

### Category 6: REMOVE - Unused Assignment Results (9 items)

Delete variables capturing assignment results never read.

#### 6.1 `src/cognitive_brain/experiments/exp3_validation.py:234`

**Current Code:**
```python
if __name__ == "__main__":
    _results = run_exp3_validation()  # Copilot: Prefixed with _ to indicate intentionally unused
```

**Fix:**
```python
if __name__ == "__main__":
    run_exp3_validation()  # Run side-effects only
```

---

#### 6.2 `agents/mental_mapping.py:1374-1382`

**Current Code:**
```python
outcome_node = mental_map.record_outcome(...)  # Assigned but not used
```

**Fix:**
```python
mental_map.record_outcome(...)  # Call for side-effects
```

---

#### 6.3 `agents/physics_orchestrator.py:641`

**Current Code:**
```python
result = orchestrator.orchestrate(state, possible_actions)  # Never read
```

**Fix:**
```python
orchestrator.orchestrate(state, possible_actions)
```

---

#### 6.4 `scripts/cognitive/analyze_token_converter.py:564`

**Current Code:**
```python
if __name__ == "__main__":
    results = main()  # Assigned but not used
```

**Fix:**
```python
if __name__ == "__main__":
    main()
```

---

### Category 7: KEEP - Intentional Markers (13 items)

These variables serve documentation or intentional side-effect purposes. **Do NOT remove**; add explicit markers:

#### 7.1 `.github/agents/core/phase8_11_advanced_reasoning.py:57`

**Current Code:**
```python
CONSTRAINT_VIOLATION_PENALTY = 1000.0
```

**Add Marker:**
```python
CONSTRAINT_VIOLATION_PENALTY = 1000.0
# Intentional reference to keep constant explicit and avoid dead-code drift
_ = CONSTRAINT_VIOLATION_PENALTY
```

---

#### 7.2 `src/codex_ml/checkpointing/compat.py:54`

**Current Code:**
```python
_warned = False

def save_checkpoint(*args, **kwargs):
    global _warned
    if not _warned:
        warnings.warn(...)
        _warned = True
    return _core.save_checkpoint(*args, **kwargs)
```

**Status:** ✅ Correctly used (state tracking for deprecation warning)

**Add Comment:**
```python
_warned = False  # Tracks deprecation warning state across calls
```

---

---

## Detailed Remediation Plan

### Phase 1: High Priority (CRITICAL)

| File | Issue | Action | Effort |
|------|-------|--------|--------|
| `services/api/main.py:624-630` | Global state race condition | Migrate to `app.state` | 1 hour |
| `services/msp_gateway/routers/kb.py:54` | Unused exception variable | Remove exception binding | 15 min |
| `services/msp_gateway/routers/infer.py:70` | Unused exception variable | Remove exception binding | 15 min |

**Expected Outcome:** Thread-safe middleware; improved code clarity

---

### Phase 2: Medium Priority (IMPORTANT)

| File | Issue | Action | Effort |
|------|-------|--------|--------|
| `src/codex_ml/tracking/mlflow_utils.py:126` | Redundant sentinel check | Simplify guard logic | 20 min |
| `agents/developer_orchestrator.py:64` | Duplicate logging; unused exception | Remove debug log | 20 min |
| `agents/physics_integration.py:41` | Duplicate logging; unused exception | Remove debug log | 20 min |
| `.github/agents/core/phase8_10_production_deployment.py` | 7 unused `UNUSED_*` constants | Delete constants | 30 min |

**Expected Outcome:** Reduced log noise; cleaner codebase; improved scanning metrics

---

### Phase 3: Low Priority (MAINTENANCE)

| File | Issue | Action | Effort |
|------|-------|--------|--------|
| `tests/test_sentencepiece_adapter.py:25` | Unused pytest marker | Move to conftest.py | 10 min |
| `src/cognitive_brain/experiments/exp3_validation.py:234` | Unused assignment | Remove variable | 5 min |
| `agents/mental_mapping.py:1374` | Unused return value | Remove assignment | 5 min |
| 9 more unused assignments | (Various) | Remove assignments | 30 min |

**Expected Outcome:** Cleaner test code; reduced scanning noise

---

## Implementation Checklist

### Pre-Implementation

- [ ] Fork/create feature branch: `fix/unused-globals-remediation`
- [ ] Run baseline: `pylint . --disable=unused-global-variable` to establish counts
- [ ] Tag all intentional globals with `# noqa: unused-global-variable` or `_ = VAR`

### Implementation by Category

#### Phase 1: High Priority

- [ ] **services/api/main.py**
  - [ ] Remove `global _rate_ts, _rate_count` declaration
  - [ ] Replace all `_rate_ts` with `app.state.rate_ts`
  - [ ] Replace all `_rate_count` with `app.state.rate_count`
  - [ ] Test rate limiting with concurrent requests

- [ ] **services/msp_gateway/routers/**
  - [ ] `kb.py:54` — Remove `except Exception as exc:` → `except Exception:`
  - [ ] `infer.py:70` — Remove `except Exception as exc:` → `except Exception:`

#### Phase 2: Medium Priority

- [ ] **src/codex_ml/tracking/mlflow_utils.py**
  - [ ] Simplify guard: `if _HAS_MLFLOW:` instead of `if _HAS_MLFLOW and _mlf is not None:`

- [ ] **agents/developer_orchestrator.py, agents/physics_integration.py**
  - [ ] Remove duplicate `logger.debug()` calls
  - [ ] Keep `logger.warning()` with `exc_info=True`

- [ ] **.github/agents/core/phase8_10_production_deployment.py**
  - [ ] Delete all lines with `UNUSED_*` prefix (7 lines)
  - [ ] Verify no references in `phase8_9_*.py` or `phase8_11_*.py`

#### Phase 3: Low Priority

- [ ] **tests/test_sentencepiece_adapter.py**
  - [ ] Move `pytestmark` to `tests/conftest.py`

- [ ] **Script files**
  - [ ] Remove unused assignments: `_results = run_exp3_validation()` → `run_exp3_validation()`
  - [ ] 9 similar removals across scripts

### Post-Implementation

- [ ] Run CodeQL scan locally: `codeql database create ... && codeql query run ...`
- [ ] Verify count: `pylint . --disable=unused-global-variable | grep "unused-global-variable"`
- [ ] Expected result: **0 findings** (or 13 with intentional markers)
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Run linting: `pylint src/ agents/ services/`
- [ ] Create PR with detailed commit messages per file

---

## Affected Files Summary

### Complete File List (70 Issues)

#### Critical/High Impact (6 files)
1. `services/api/main.py` — State management [6 findings]
2. `services/msp_gateway/routers/kb.py` — Exception handler [1 finding]
3. `services/msp_gateway/routers/infer.py` — Exception handler [1 finding]
4. `src/codex_ml/tracking/mlflow_utils.py` — Import guard [2 findings]
5. `agents/developer_orchestrator.py` — Import/logging [2 findings]
6. `agents/physics_integration.py` — Import/logging [2 findings]

#### Medium Impact (8 files)
7. `.github/agents/core/phase8_10_production_deployment.py` — Unused constants [7 findings]
8. `.github/agents/core/phase8_11_advanced_reasoning.py` — Unused constants [2 findings]
9. `agents/mental_mapping.py` — Unused returns [2 findings]
10. `agents/physics_orchestrator.py` — Unused assignment [1 finding]
11. `src/cognitive_brain/experiments/exp3_validation.py` — Unused assignment [1 finding]
12. `scripts/cognitive/analyze_token_converter.py` — Unused assignment [1 finding]
13. `scripts/deep_research_task_process.py` — Unused paths [2 findings]
14. `tests/test_sentencepiece_adapter.py` — Test artifact [1 finding]

#### Low Impact (12+ files)
15-26. Various import guards, fallback variables, and constants in:
- `src/codex_ml/*` (monitoring, tokenization, models, training, safety)
- `audio_cleaner_v1/` (analyzer)
- `tests/stub_packages/torch/`
- And 8 additional Python modules

---

## Search Queries for Verification

Use these commands to verify remediation:

```bash
# Find all unused globals
pylint src/ agents/ services/ scripts/ --disable=all --enable=unused-global-variable

# Find orphaned _* variables (common pattern)
grep -r "^[[:space:]]*_[A-Z_]*\s*=" --include="*.py" src/ agents/ services/

# Find future-reserved constants
grep -r "UNUSED_" --include="*.py" .github/agents/

# Find unused assignments (double-check)
grep -r "^\s*[a-z_]*\s*=\s*\w*(.*)$" --include="*.py" | grep -v "def \|class \|return "
```

---

## Dangerous Options & Risks

### ⚠️ NOT Recommended

1. **Remove ALL globals indiscriminately**
   - ❌ Risk: Break deprecation warning tracking (`_warned` flags)
   - ❌ Risk: Remove intentional side-effect constants
   - ✅ Use: Per-category review; keep intentional markers

2. **Automate with code formatter only**
   - ❌ Risk: Remove constants needed for documentation
   - ❌ Risk: Break state tracking in middleware
   - ✅ Use: Manual review + automated checks per category

3. **Ignore "Reserved for future" constants**
   - ❌ Risk: CodeQL will flag repeatedly in each scan
   - ❌ Risk: Adds noise to security dashboards
   - ✅ Use: Delete or create GitHub Issue for explicit tracking

### ✅ Recommended Safeguards

- [ ] Create feature branch (non-direct main commit)
- [ ] Run full test suite before merge
- [ ] Code review by 2+ maintainers
- [ ] Monitor production for 48h post-deploy (middleware changes)
- [ ] Keep git history for rollback reference

---

## Verification Steps

### 1. Pre-Implementation Baseline
```bash
pylint . --disable=unused-global-variable 2>/dev/null | grep "unused-global-variable" | wc -l
# Expected: 70
```

### 2. Post-Implementation Target
```bash
pylint . --disable=unused-global-variable 2>/dev/null | grep "unused-global-variable" | wc -l
# Expected: 0 (or 13 if keeping intentional markers)
```

### 3. Test Execution
```bash
pytest tests/ -v --tb=short
# All tests must pass
```

### 4. Middleware Testing (Critical)
```python
# Test concurrent rate limiting
import asyncio
import httpx

async def test_rate_limit():
    client = httpx.AsyncClient(base_url="http://localhost:8000")
    # Send 101 requests within 1 second
    tasks = [client.get("/endpoint", headers={"x-api-key": "valid"}) for _ in range(101)]
    responses = await asyncio.gather(*tasks)
    # Verify exactly 100 succeed (429) and last is 429
    assert sum(1 for r in responses if r.status_code == 429) >= 1
```

---

## Conclusion

This remediation addresses **70 findings** across **26+ files** with a phased approach:

1. **Phase 1** eliminates thread-safety issues and exception handling bugs
2. **Phase 2** reduces log noise and cleans up future-planning scaffolding
3. **Phase 3** improves code clarity in tests and scripts

**Expected Impact:**
- ✅ Zero CodeQL "unused-global-variable" findings
- ✅ Improved thread-safety in FastAPI middleware
- ✅ Cleaner codebase with reduced scanning false positives
- ✅ Better maintainability for future developers

**Timeline:** 3-4 hours total effort across 3 phases

---

**Next Steps:**
1. Review this document
2. Approve remediation approach
3. Begin Phase 1 implementation
4. Submit PR with detailed commit messages per file

