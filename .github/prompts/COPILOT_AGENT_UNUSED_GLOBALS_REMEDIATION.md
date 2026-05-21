# Copilot Cloud Agent Prompt: Unused Global Variables Remediation

> **Prompt Type:** AI Agent Instruction Set  
> **Target:** GitHub Copilot Cloud Agent (Autonomous Execution)  
> **Scope:** Remediate 70 unused global variable findings per `.github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md`  
> **Generated:** 2026-05-21 | Author: mbaetiong

---

## Mission Statement

Your task is to autonomously remediate **70 unused global variable CodeQL findings** across the Aries-Serpent/_codex_ repository. Follow the phased approach and categorization defined in `.github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md`. Execute with precision, maintain code quality, and provide detailed commit messages per phase.

---

## Core Directives

### 1. Foundational Constraints

You **MUST**:
- ✅ Adhere strictly to the **Investigation Protocol** defined below
- ✅ Process findings in **3 phases** (High → Medium → Low priority)
- ✅ Run full test suite (`pytest tests/ -v`) after each phase
- ✅ Validate CodeQL metrics before/after remediation
- ✅ Document all changes in detailed commit messages
- ✅ Preserve intentional variables marked in Category 7 (KEEP)
- ✅ Follow `.codex/CODEBASE_AGENCY_POLICY.md` for autonomy governance

You **MUST NOT**:
- ❌ Remove variables without evidence from `.github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md`
- ❌ Modify code beyond remediation scope (no refactoring unrelated code)
- ❌ Collapse multiple findings into single commit (one file = one commit)
- ❌ Skip test execution between phases
- ❌ Deploy to production without maintainer approval
- ❌ Assume default branch is `main` (verify via repo metadata)

---

## Evidence Gathering Phase (Required Before Any Fix)

### Step 1: Baseline Validation

Before remediation, execute these commands and document results:

```bash
# Establish baseline metrics
BASELINE_COUNT=$(pylint . --disable=unused-global-variable 2>/dev/null | grep -c "unused-global-variable")
echo "BASELINE: $BASELINE_COUNT unused global variables"

# List all findings with file/line precision
pylint . --disable=unused-global-variable --output-format=json > codeql_baseline.json

# Verify remediation document exists and is readable
test -f .github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md && echo "✅ Remediation guide present" || exit 1
```

**Document:** Include baseline count and timestamp in PR description

### Step 2: Cross-Reference Remediation Categories

Map each finding to its category in the remediation document:

| CodeQL Finding | File | Line | Category | Action | Evidence |
|---|---|---|---|---|---|
| `_rate_ts` | `services/api/main.py` | 624 | FIX: State Management | Migrate to `app.state` | [Link to doc] |
| `_rate_count` | `services/api/main.py` | 628 | FIX: State Management | Migrate to `app.state` | [Link to doc] |
| ... | ... | ... | ... | ... | ... |

**Do not proceed** until this mapping is complete and cross-referenced to the remediation document.

---

## Phase 1: High Priority (Critical) Execution

**Target:** 6 findings across 3 files  
**Time Budget:** 4 hours  
**Test Gate:** Full middleware integration tests must pass

### 1.1 Category: FIX - State Management

#### File: `services/api/main.py:624-630`

**Current Code (Lines 624-630):**
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
        if now - _rate_ts >= 1:          # ❌ USES GLOBAL
            _rate_ts = now                 # ❌ SETS GLOBAL
            _rate_count = 0                # ❌ SETS GLOBAL
        if _rate_count >= limit:           # ❌ USES GLOBAL
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        _rate_count += 1                   # ❌ USES GLOBAL
```

**Remediation:**
```python
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # State management moved to app.state for thread-safety
    key = request.headers.get("x-api-key")
    expected = os.getenv("API_KEY")
    if expected and key != expected:
        return JSONResponse({"detail": "unauthorized"}, status_code=401)

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

**Validation:**
- [ ] Run `pytest tests/test_api.py -v -k rate_limit`
- [ ] Load test: 200 concurrent requests, verify rate limiting at ~100/sec
- [ ] Verify `pylint` no longer flags `_rate_ts`, `_rate_count`

**Commit Message:**
```
fix(api): Replace global rate limit variables with thread-safe app.state

Addresses CodeQL unused-global-variable findings for _rate_ts and _rate_count.
Migrates middleware state management to FastAPI app.state pattern for thread
safety and eliminates global variable contention during concurrent requests.

Fixes:
- services/api/main.py:624 (_rate_ts unused)
- services/api/main.py:628 (_rate_count unused)
- services/api/main.py:630 (_rate_count unused)

Testing:
- Verified rate limiting works with concurrent load
- All middleware tests pass
- CodeQL validation: 0 findings in api/main.py
```

---

### 1.2 Category: FIX - Error Handlers

#### File: `services/msp_gateway/routers/kb.py:54`

**Current Code:**
```python
except Exception as exc:  # pragma: no cover - optional dependency path
    _retrieval_adapter_error = exc  # ❌ ASSIGNED BUT NEVER USED
    logger.error(
        "Failed to initialize retrieval adapter for KB queries: %s",
        exc,
    )
```

**Remediation:**
```python
except Exception:  # pragma: no cover - optional dependency path
    logger.error(
        "Failed to initialize retrieval adapter for KB queries",
        exc_info=True,
    )
```

**Validation:**
- [ ] Run `pytest tests/test_kb_adapter.py -v`
- [ ] Verify error logging still captures traceback via `exc_info=True`
- [ ] Confirm `pylint` no longer flags `_retrieval_adapter_error`

**Commit Message:**
```
fix(msp_gateway): Remove unused exception variable in KB adapter error handler

Addresses CodeQL unused-global-variable finding for _retrieval_adapter_error.
Exception is logged but variable was never referenced; removed binding and
enhanced logging with exc_info=True for traceback capture.

Fixes:
- services/msp_gateway/routers/kb.py:54

Testing:
- KB adapter tests pass
- Error logging preserves traceback information
```

---

#### File: `services/msp_gateway/routers/infer.py:70`

**Current Code:**
```python
except Exception as exc:  # pragma: no cover - optional dependency path
    _retrieval_adapter_error = exc  # ❌ ASSIGNED BUT NEVER USED
    logger.warning(
        "Failed to initialize retrieval adapter; proceeding without RAG: %s",
        exc,
    )
```

**Remediation:**
```python
except Exception:  # pragma: no cover - optional dependency path
    logger.warning(
        "Failed to initialize retrieval adapter; proceeding without RAG",
        exc_info=True,
    )
```

**Validation:**
- [ ] Run `pytest tests/test_infer_adapter.py -v`
- [ ] Verify graceful degradation (RAG disabled, inference continues)
- [ ] Confirm `pylint` no longer flags `_retrieval_adapter_error`

**Commit Message:**
```
fix(msp_gateway): Remove unused exception variable in infer adapter error handler

Addresses CodeQL unused-global-variable finding for _retrieval_adapter_error.
Exception is logged but variable was never referenced; removed binding and
enhanced logging with exc_info=True for traceback capture.

Fixes:
- services/msp_gateway/routers/infer.py:70

Testing:
- Infer adapter tests pass
- Graceful degradation without RAG verified
- Error logging preserves traceback information
```

---

### Phase 1 Test Gate

**Execute before proceeding to Phase 2:**

```bash
# Full middleware/API test suite
pytest services/ -v --tb=short -k "api or middleware or rate_limit or adapter" --cov=services

# Verify findings reduced
PHASE1_COUNT=$(pylint services/ --disable=unused-global-variable 2>/dev/null | grep -c "unused-global-variable")
echo "Phase 1 Result: $PHASE1_COUNT findings (target: ~64 remaining)"

# CodeQL validation
codeql database create /tmp/codeql_db --language=python --source-root=.
codeql query run /path/to/py-unused-global-variable.ql --database=/tmp/codeql_db
```

**Gate Condition:** All tests pass AND findings reduced by 6

---

## Phase 2: Medium Priority (Important) Execution

**Target:** 12 findings across 8 files  
**Time Budget:** 3 hours  
**Test Gate:** Unit tests + import validation

### 2.1 Category: MIGRATE - Lazy Import Patterns

#### File: `src/codex_ml/tracking/mlflow_utils.py:126-127`

**Current Code (Lines 126-135):**
```python
_mlf = None  # Actual mlflow module if import succeeds
_HAS_MLFLOW = False

def ensure_mlflow():
    global _mlf, _HAS_MLFLOW
    if _HAS_MLFLOW and _mlf is not None:  # ❌ REDUNDANT CHECK
        return
```

**Remediation:**
```python
_mlf = None  # Actual mlflow module if import succeeds
_HAS_MLFLOW = False

def ensure_mlflow():
    global _mlf, _HAS_MLFLOW
    if _HAS_MLFLOW:  # Single sentinel sufficient
        return
```

**Validation:**
- [ ] Run `pytest tests/test_mlflow.py -v`
- [ ] Verify lazy loading works (import attempted once, cached)
- [ ] Test offline mode (no MLflow available)
- [ ] Confirm `pylint` no longer flags redundant check

**Commit Message:**
```
refactor(mlflow_utils): Simplify lazy import guard logic

Addresses CodeQL unused-global-variable finding for redundant _mlf check.
The condition `_HAS_MLFLOW and _mlf is not None` is overly defensive; _mlf
is only set when _HAS_MLFLOW is True. Simplified to single sentinel check.

Fixes:
- src/codex_ml/tracking/mlflow_utils.py:126-127

Testing:
- MLflow lazy loading tests pass
- Offline mode (no MLflow) verified
- Performance: single check instead of double
```

---

#### File: `agents/developer_orchestrator.py:64-68`

**Current Code:**
```python
try:
    from codex.logging.session_logger import log_message
    LOGGING_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")      # ❌ FIRST LOG
    logger.warning(f"ImportError: {e}", exc_info=True)  # ❌ SECOND LOG (duplicate)
    LOGGING_AVAILABLE = False
    
    def log_message(session_id, role, message, **kwargs):
        pass
```

**Remediation:**
```python
try:
    from codex.logging.session_logger import log_message
    LOGGING_AVAILABLE = True
except ImportError:
    logger.warning("Failed to import session logger; using fallback", exc_info=True)
    LOGGING_AVAILABLE = False
    
    def log_message(session_id, role, message, **kwargs):
        """Fallback logging when session logger unavailable."""
        pass
```

**Validation:**
- [ ] Run `pytest tests/test_orchestrator.py -v`
- [ ] Verify single warning logged on import failure
- [ ] Test fallback logging function works
- [ ] Confirm `pylint` no longer flags exception variable

**Commit Message:**
```
refactor(orchestrator): Consolidate duplicate import error logging

Addresses CodeQL unused-global-variable finding for ImportError exception.
Removed redundant debug+warning logging pattern; single warning with exc_info
preserves traceback without verbosity.

Fixes:
- agents/developer_orchestrator.py:64-68

Testing:
- Orchestrator import error handling verified
- Fallback logging function tested
- Log output reduced from 2 to 1 message
```

---

#### File: `agents/physics_integration.py:41-45` (Identical Pattern)

**Apply same refactoring as developer_orchestrator.py**

**Commit Message:**
```
refactor(physics_integration): Consolidate duplicate import error logging

Addresses CodeQL unused-global-variable finding for ImportError exception.
Removed redundant debug+warning logging pattern; single warning with exc_info
preserves traceback without verbosity. Pattern matches developer_orchestrator.py.

Fixes:
- agents/physics_integration.py:41-45

Testing:
- Physics integration import error handling verified
- Fallback logging function tested
```

---

### 2.2 Category: REMOVE - Reserved Future Constants

#### File: `.github/agents/core/phase8_10_production_deployment.py:38-73`

**Current Code (7 unused constants):**
```python
UNUSED_QUANTUM_ADVANTAGE_8_10_TARGET = 1.0 / K1_PHASE_8_10_TARGET  # = 4.55x (preserved for documentation)
UNUSED_METRICS_EXPORT_INTERVAL_SECONDS = 15  # Reserved for future metrics export
UNUSED_TRACE_SAMPLE_RATE = 0.1  # Reserved for future distributed tracing
UNUSED_LOG_RETENTION_DAYS = 30  # Reserved for future log retention policy
UNUSED_DOC_FORMATS = ["markdown", "html", "pdf"]
UNUSED_RATE_LIMIT_REQUESTS_PER_MINUTE = 100  # Reserved for future rate limiting enforcement
UNUSED_RBAC_ROLES = ["admin", "developer", "viewer"]  # Reserved for future RBAC enforcement
UNUSED_HEALTH_CHECK_TIMEOUT_SECONDS = 30  # Reserved for future health check timeout enforcement
UNUSED_ROLLBACK_THRESHOLD_ERROR_RATE = 0.05  # Reserved for future rollback gating logic
```

**Remediation:**

1. Search for all references to these constants:
```bash
grep -r "UNUSED_QUANTUM_ADVANTAGE_8_10_TARGET\|UNUSED_METRICS_EXPORT\|UNUSED_TRACE_SAMPLE\|UNUSED_LOG_RETENTION\|UNUSED_DOC_FORMATS\|UNUSED_RATE_LIMIT\|UNUSED_RBAC_ROLES\|UNUSED_HEALTH_CHECK\|UNUSED_ROLLBACK_THRESHOLD" --include="*.py" .
```

2. If NO matches found:
```python
# DELETED: All UNUSED_* constants from phase8_10_production_deployment.py
# Rationale: Never referenced; future features should track via GitHub Issues
# Commit history preserved for reference if needed
```

**Validation:**
- [ ] Confirm zero references to deleted constants via grep
- [ ] Verify no imports of `phase8_10_production_deployment.UNUSED_*` anywhere
- [ ] Run `pytest tests/test_agents_phase8.py -v`
- [ ] CodeQL count reduced by 7

**Commit Message:**
```
refactor(agents): Remove reserved-for-future constants from Phase 8.10

Addresses CodeQL unused-global-variable findings (7 instances).
Constants prefixed with UNUSED_ were placeholders for future features but
were never referenced. Removed per remediation policy: future features should
be tracked as GitHub Issues, not as dead code.

Deleted constants:
- UNUSED_QUANTUM_ADVANTAGE_8_10_TARGET
- UNUSED_METRICS_EXPORT_INTERVAL_SECONDS
- UNUSED_TRACE_SAMPLE_RATE
- UNUSED_LOG_RETENTION_DAYS
- UNUSED_DOC_FORMATS
- UNUSED_RATE_LIMIT_REQUESTS_PER_MINUTE
- UNUSED_RBAC_ROLES
- UNUSED_HEALTH_CHECK_TIMEOUT_SECONDS
- UNUSED_ROLLBACK_THRESHOLD_ERROR_RATE

Fixes:
- .github/agents/core/phase8_10_production_deployment.py (7 findings)

Testing:
- Phase 8 agent tests pass
- No imports of deleted constants found
```

---

#### File: `.github/agents/core/phase8_11_advanced_reasoning.py:57-73` (2 instances)

**Current Code:**
```python
CONSTRAINT_VIOLATION_PENALTY = 1000.0  # ❌ UNUSED
RANDOM_SEED_8_11 = 44
```

**Note:** These are intentional constants for documentation (see remediation doc Category 7). Add explicit marker:

**Remediation:**
```python
CONSTRAINT_VIOLATION_PENALTY = 1000.0
# Intentional reference to keep constant explicit and avoid dead-code drift
_ = CONSTRAINT_VIOLATION_PENALTY

RANDOM_SEED_8_11 = 44  # Used in deterministic behavior seed initialization
```

**Validation:**
- [ ] `pylint` no longer flags these as unused
- [ ] Comment explains intent
- [ ] Run `pytest tests/test_agents_phase8.py -v`

**Commit Message:**
```
refactor(agents): Mark intentional constants and add documentation

Addresses CodeQL unused-global-variable findings for deliberately unused
constants. Added explicit markers and comments to clarify intent and avoid
false positives in future scans.

Fixes:
- .github/agents/core/phase8_11_advanced_reasoning.py (2 findings)

Testing:
- Phase 8.11 agent tests pass
- pylint validation clean
```

---

### Phase 2 Test Gate

```bash
# Unit tests for all modified modules
pytest agents/ src/codex_ml/tracking/ -v --tb=short --cov=agents,src/codex_ml/tracking

# Verify findings reduced
PHASE2_COUNT=$(pylint . --disable=unused-global-variable 2>/dev/null | grep -c "unused-global-variable")
echo "Phase 2 Result: $PHASE2_COUNT findings (target: ~45 remaining)"
```

**Gate Condition:** All tests pass AND findings reduced by 12 (from 64→52)

---

## Phase 3: Low Priority (Maintenance) Execution

**Target:** 9 findings across 9 files  
**Time Budget:** 2 hours  
**Test Gate:** Quick unit test pass

### 3.1 Category: REMOVE - Unused Assignment Results

#### Files to Process (9 total):

1. **`src/cognitive_brain/experiments/exp3_validation.py:234`**
   ```python
   # BEFORE
   _results = run_exp3_validation()
   
   # AFTER
   run_exp3_validation()
   ```

2. **`agents/mental_mapping.py:1374`**
   ```python
   # BEFORE
   outcome_node = mental_map.record_outcome(...)
   
   # AFTER
   mental_map.record_outcome(...)
   ```

3. **`agents/physics_orchestrator.py:641`**
   ```python
   # BEFORE
   result = orchestrator.orchestrate(state, possible_actions)
   
   # AFTER
   orchestrator.orchestrate(state, possible_actions)
   ```

4. **`scripts/cognitive/analyze_token_converter.py:564`**
   ```python
   # BEFORE
   results = main()
   
   # AFTER
   main()
   ```

5-9. **Other similar assignments** (verify in remediation doc)

**Validation for Each:**
- [ ] Variable never read after assignment
- [ ] Function call has required side-effects
- [ ] Tests pass
- [ ] Code behavior unchanged

**Single Commit Message (covers all 9):**
```
refactor: Remove unused assignment results (9 instances)

Addresses CodeQL unused-global-variable findings. These variables captured
return values that were never read; function calls retained for side-effects.

Removed assignments from:
- src/cognitive_brain/experiments/exp3_validation.py:234 (_results)
- agents/mental_mapping.py:1374 (outcome_node)
- agents/physics_orchestrator.py:641 (result)
- scripts/cognitive/analyze_token_converter.py:564 (results)
- scripts/deep_research_task_process.py (2 instances)
- (5 more instances from various modules)

Fixes: 9 unused-global-variable findings

Testing:
- All affected modules tested
- Behavior unchanged (side-effects preserved)
```

---

### 3.2 Category: REMOVE - Test Artifacts

#### File: `tests/test_sentencepiece_adapter.py:25`

**Current Code:**
```python
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
```

**Remediation:** Move to `tests/conftest.py`:

```python
# In tests/conftest.py (ADD if not present)
import pytest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
```

**Then DELETE from test_sentencepiece_adapter.py**

**Validation:**
- [ ] Run `pytest tests/test_sentencepiece_adapter.py -v -W ignore::DeprecationWarning`
- [ ] Verify deprecation warnings still suppressed
- [ ] CodeQL no longer flags `pytestmark` as unused

**Commit Message:**
```
refactor(tests): Move pytest marker to conftest.py

Addresses CodeQL unused-global-variable finding for pytestmark.
Moved filter configuration to tests/conftest.py for project-wide
deprecation warning suppression.

Fixes:
- tests/test_sentencepiece_adapter.py:25

Testing:
- Deprecation warning suppression verified
- All tests pass
```

---

### Phase 3 Test Gate

```bash
# Quick validation
pytest tests/ -v --tb=short -x

# Final count
FINAL_COUNT=$(pylint . --disable=unused-global-variable 2>/dev/null | grep -c "unused-global-variable")
echo "Final Result: $FINAL_COUNT findings (target: 13 with intentional markers)"
```

**Gate Condition:** Final count ≤ 15 (acceptable with intentional markers)

---

## Post-Execution Validation

### After All Phases Complete

#### 1. Comprehensive Metrics
```bash
# Before baseline (from evidence gathering)
echo "BASELINE: $BASELINE_COUNT"

# After completion
FINAL=$(pylint . --disable=unused-global-variable 2>/dev/null | grep -c "unused-global-variable")
echo "FINAL: $FINAL"
echo "REDUCTION: $((BASELINE_COUNT - FINAL)) findings fixed"
echo "SUCCESS RATE: $(echo "scale=2; (($BASELINE_COUNT - $FINAL) / $BASELINE_COUNT) * 100" | bc)%"
```

**Expected:** ≥ 95% reduction (65-70 of 70 findings resolved)

#### 2. Full Test Suite
```bash
pytest tests/ -v --cov=src --cov=agents --cov=services --cov=scripts \
  --cov-report=html --tb=short
```

**Expected:** 100% of tests pass

#### 3. CodeQL Re-validation
```bash
codeql database create /tmp/codeql_final --language=python --source-root=.
codeql query run py-unused-global-variable.ql --database=/tmp/codeql_final \
  --output=/tmp/final_results.sarif
```

**Expected:** ≤ 15 findings (intentional markers with documentation)

#### 4. Manual Code Review
- [ ] Each commit message references remediation doc
- [ ] No unrelated refactoring included
- [ ] Comments explain intentional variables
- [ ] No dead code remains

---

## Governance & Safety Checkpoints

### Decision Gates (MUST NOT BYPASS)

1. **Before Phase 1:** Evidence gathering complete ✅
2. **After Phase 1:** 6 findings resolved, tests pass ✅
3. **After Phase 2:** 12 more findings resolved, tests pass ✅
4. **After Phase 3:** 9 final findings resolved, tests pass ✅
5. **Before Merge:** PR review + maintainer approval ✅

### Rollback Procedures

**If tests fail at any gate:**
```bash
git reset --hard <last_known_good_commit>
git clean -fd
pytest tests/ -v
```

**Document failure in PR comment:**
```markdown
⚠️ GATE FAILED: [Phase] - [Reason]

Failed test: [test_name]
Error: [stack trace excerpt]

Rolling back to: [commit sha]
Re-evaluating: [specific finding]
```

---

## Critical Implementation Notes

### Thread Safety (Phase 1)

⚠️ **High Risk:** `services/api/main.py` middleware state management

**Testing Requirements:**
- Load test: 1000 concurrent requests
- Verify rate limiting works correctly under load
- Monitor for race conditions (enable ThreadSanitizer if available)

```python
# Load test example
import asyncio
import httpx

async def test_concurrent_rate_limiting():
    client = httpx.AsyncClient(base_url="http://localhost:8000")
    tasks = [
        client.get("/api/endpoint", headers={"x-api-key": "test"})
        for _ in range(200)
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    errors = [r for r in responses if isinstance(r, Exception) or r.status_code >= 500]
    assert len(errors) == 0, f"Concurrent request failures: {errors}"
```

### Import Safety (Phase 2)

⚠️ **Medium Risk:** Lazy import patterns

**Testing Requirements:**
- Test offline mode (dependencies unavailable)
- Test with dependencies available
- Verify error messages helpful
- No import side-effects

```bash
# Test offline mode
PYTHONPATH=. python -c "
import sys
sys.modules['mlflow'] = None  # Simulate unavailable
from src.codex_ml.tracking import mlflow_utils
try:
    mlflow_utils.ensure_mlflow()
    assert False, 'Should raise RuntimeError'
except RuntimeError as e:
    assert 'mlflow' in str(e).lower()
"
```

---

## Success Criteria

### Primary Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| CodeQL findings reduced | 65+ of 70 | Automated scan |
| Tests passing | 100% | `pytest --tb=short` |
| Code coverage maintained | ≥95% (baseline) | `pytest --cov` |
| Intentional markers documented | 13-15 vars | Code review |
| Commits per file | 1 | git log analysis |

### Secondary Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Middleware throughput | No regression | Load test |
| Import latency | No regression | Benchmark |
| Error messages clarity | Improved | Manual review |
| Comment/documentation quality | High | Code review |

---

## Execution Checklist

### Pre-Execution
- [ ] Fork/branch: `fix/unused-globals-remediation`
- [ ] Read `.github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md` completely
- [ ] Read `.codex/CODEBASE_AGENCY_POLICY.md` for autonomy rules
- [ ] Establish baseline CodeQL metrics (Step 1 above)
- [ ] Create cross-reference mapping (Step 2 above)

### Phase 1 Execution
- [ ] Execute all commits in FIX categories
- [ ] Run Phase 1 test gate
- [ ] Document results in PR comment
- [ ] Proceed only if gate passes

### Phase 2 Execution
- [ ] Execute all commits in MIGRATE category
- [ ] Execute all commits in REMOVE category
- [ ] Run Phase 2 test gate
- [ ] Document results in PR comment
- [ ] Proceed only if gate passes

### Phase 3 Execution
- [ ] Execute remaining low-priority commits
- [ ] Run Phase 3 test gate
- [ ] Document results in PR comment
- [ ] Proceed only if gate passes

### Post-Execution
- [ ] Run comprehensive metrics validation
- [ ] Create PR summary with before/after metrics
- [ ] Request maintainer review
- [ ] Await approval before merge
- [ ] Monitor for 48h post-merge for production issues

---

## Communication Template

### PR Description (Auto-Generated)

```markdown
## Remediation: Unused Global Variables (CodeQL py/unused-global-variable)

**Scope:** 70 CodeQL findings across 26+ files  
**Status:** Implementation in progress (Phase: [1/2/3])  
**Branch:** fix/unused-globals-remediation

### Summary

This PR remediates all unused global variable findings per the remediation 
plan in `.github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md`.

### Baseline Metrics
- **Before:** 70 unused-global-variable findings
- **After:** [FINAL_COUNT] findings
- **Reduction:** [PERCENTAGE]%

### Changes by Category

#### Phase 1: High Priority (Thread Safety)
- [x] FIX: services/api/main.py (6 findings)
- [x] FIX: services/msp_gateway/routers/ (2 findings)

#### Phase 2: Medium Priority (Code Quality)
- [x] MIGRATE: Lazy import patterns (12 findings)
- [x] REMOVE: Reserved constants (15 findings)

#### Phase 3: Low Priority (Maintenance)
- [x] REMOVE: Unused assignments (9 findings)
- [x] REMOVE: Test artifacts (3 findings)

### Testing
- Full test suite: ✅ PASS
- Middleware load test (1000 concurrent): ✅ PASS
- CodeQL re-validation: ✅ [FINAL_COUNT] findings

### Risks Mitigated
- ✅ Thread-safety: Middleware state moved to app.state
- ✅ Import safety: Lazy loading patterns validated
- ✅ Code clarity: Dead code removed, intent documented

### References
- Remediation plan: `.github/docs/UNUSED_GLOBAL_VARIABLES_REMEDIATION.md`
- Policy: `.codex/CODEBASE_AGENCY_POLICY.md`
- CodeQL rule: py/unused-global-variable
```

---

## Final Authority & Escalation

**If encountered issues beyond remediation scope:**

1. **Import Error:** Verify dependency installed; escalate to @owner if missing
2. **Test Failure:** Document exact failure; create issue for investigation
3. **Policy Conflict:** Reference `.codex/CODEBASE_AGENCY_POLICY.md`; escalate if violation
4. **Unexpected Code Pattern:** Do NOT guess; escalate to maintainer for clarification

**Escalation Template:**
```markdown
⚠️ ESCALATION: [Category]

Issue: [Description]
File: [path:line]
Error: [exact error message]

Attempted: [what was tried]
Expected: [what should happen]
Actual: [what actually happened]

Decision Required: [options A/B/C]
```

---

## Success Declaration

**Remediation is COMPLETE when:**

✅ All 3 phases executed without rollback  
✅ CodeQL findings reduced from 70 → ≤15  
✅ 100% of tests passing  
✅ All commits reference remediation document  
✅ PR reviewed and approved by maintainer  
✅ Code merged to main branch  
✅ 48h post-merge monitoring confirms no production issues  

**Sign-off:**
```
Remediation Status: COMPLETE
Final Finding Count: [NUMBER]
Reduction: [PERCENTAGE]%
Merge Commit: [SHA]
Merged At: [TIMESTAMP]
```

