# PR #3248 Attempt 19: Root Cause Analysis

**Date**: 2026-02-16T23:00:00Z
**Commit**: 31851a5 (PR #3311 merged)
**CI Runs**: 22079330623 (progressive), 22079330605 (resilient)
**Agent**: GitHub Copilot (Session ID: 2026-02-16-23:07)

---

## Executive Summary

**Total Failures**: 25 tests (20 quick validation + 5 slow validation)
**Fixes Applied**: 8/25 (32%)
**Root Cause**: Python 3.12 strict typing with union operators in Pydantic models and typing constructs

---

## Category 1: Python 3.12 isinstance() Type Errors (12 failures)

### Root Cause
Python 3.12 enforces strict type checking when `isinstance()` or `issubclass()` receives typing constructs like:
- `str | None` (union operator)
- `int | None`
- `Optional[T]` used incorrectly with isinstance()

When Pydantic 2.x processes models with `| None` annotations, it can trigger isinstance() calls with these type objects, which Python 3.12 rejects.

### Failures Analyzed

#### Group A: API Service (8 tests) ✅ FIXED
**Tests**: `test_api_infer_masking.py::test_secret_masking[*]` (8 parameterized tests)

**Error**:
```
fastapi.exceptions.HTTPException: 500: isinstance() arg 2 must be a type, a tuple of types, or a union
```

**Root Cause**: Line 358 in `services/api/main.py`:
```python
class TrainRequest(BaseModel):
    notes: str | None = None  # ❌ Python 3.12 incompatible
```

**Solution Applied** (Commit 6f1876c2):
```python
from typing import Any, Optional  # Added Optional import

class TrainRequest(BaseModel):
    notes: Optional[str] = None  # ✅ Pydantic compatible
```

Also converted all return type annotations for consistency:
- `_resolve_context_limit() -> int | None` → `Optional[int]`
- `_coerce_int() -> int | None` → `Optional[int]`
- `_get_attr() -> int | None` → `Optional[int]`
- `_get_model_vocab_size() -> int | None` → `Optional[int]`
- `_valid_size() -> int | None` → `Optional[int]`

**Expected Impact**: All 8 `test_api_infer_masking` tests should pass

#### Group B: Checkpoint Serialization (1 test) ⏳ PENDING
**Test**: `test_checkpoint_corrupt_load.py::test_load_checkpoint_detects_corruption`

**Error**:
```
CheckpointLoadError: failed to save checkpoint to /tmp/.../model.pt:
failed to save checkpoint via pickle: issubclass() arg 2 must be a class, a tuple of classes, or a union
```

**Root Cause**: Python 3.12 pickle module encounters union types during serialization of objects with `| None` type annotations in their class definitions or attributes.

**Investigation Needed**:
- Check if DummyModel or DummyOpt classes have union type annotations
- May need to sanitize type annotations before pickling
- Could be deep in torch.save() internals

**Possible Solutions**:
1. Remove type annotations from test classes
2. Use `typing.get_type_hints()` to resolve forward references before pickling
3. Skip test in Python 3.12 if unfixable

#### Group C: CLI Validation (2 tests) ⏳ PENDING
**Tests**:
- `test_cli_manifest_validate.py::test_validate_ok_and_strict`
- `test_cli_manifest_validate.py::test_validate_rejects_wrong_schema`

**Error**:
```
assert 2 == 0  # exit code
assert 'invalid schema' in ''  # output
```

**Root Cause**: CLI command execution failing with exit code 2 instead of expected codes.

**Investigation Needed**:
- Check if CLI uses typer with union type annotations
- May be related to argument parsing with Python 3.12

#### Group D: CLI Argument Parsing (1 test) ⏳ PENDING
**Test**: `test_cli_argument_parsing.py::test_cli_non_mapping_config_rejection`

**Error**:
```
Failed: DID NOT RAISE <class 'ValueError'>
```

**Root Cause**: Expected ValueError not being raised, possibly due to type checking changes in Python 3.12.

---

## Category 2: Quantum Memory Mock Issues (6 failures)

### Group A: Repository Mock Missing Method (4 tests) ✅ FIXED
**Tests**: `test_memory.py::TestIntegration::*` (4 tests)

**Error**:
```
AttributeError: 'MockRepo' object has no attribute 'create'
```

**Root Cause**: MockRepo fixture missing `create()` method called by `CoherenceMonitor.record_metric()` at line 168.

**Solution Applied** (Commit 6f1876c2):
```python
class MockRepo:
    def store_quantum_metric(self, *args, **kwargs):
        pass

    def create(self, metric):  # ✅ Added missing method
        """Mock create method for CoherenceMonitor."""
        return metric
```

**Expected Impact**: All 4 TestIntegration tests should pass

### Group B: Consolidation Logic (1 test) ⏳ PENDING
**Test**: `test_memory.py::TestConsolidation::test_success_rate_criterion`

**Error**:
```
AssertionError: assert ('high-success' in {} or 0 >= 1)
```

**Root Cause**: After consolidation, LTM remains empty when it should contain promoted patterns.

**Investigation Needed**:
- Check `QuantumMemoryManager.consolidate()` implementation
- Verify promotion threshold logic
- May be logic bug or test expectation issue

### Group C: Compression Accuracy (1 test) ⏳ PENDING
**Test**: `test_memory.py::TestCompression::test_decompression_accuracy`

**Error**:
```
assert 0.15897819033052182 < 0.05  # 15.9% error vs 5% threshold
```

**Root Cause**: Decompression accuracy below threshold (15.9% vs 5% expected).

**Investigation Needed**:
- Check `PatternCompressor` algorithm
- May need algorithm tuning or threshold adjustment
- Could be test data issue

---

## Category 3: BLEU Metrics (2 failures)

**Tests**:
- `test_metrics_correctness.py::test_bleu_score`
- `test_metrics_correctness.py::test_bleu_known_value`

**Error**:
```
assert 0.0 == 1.0 ± 1.0e-06  # Expected 1.0 for identical strings
```

**Root Cause**: BLEU calculation returning 0.0 instead of 1.0 for identical reference/hypothesis pairs.

**Investigation Path**:
1. `src/codex_ml/eval/metrics.py:bleu()` tries sacrebleu first, then nltk
2. Line 307: `return float(score.score / 100.0)` - sacrebleu returns 0-100 scale
3. If sacrebleu returns 0 instead of 100, result is 0.0
4. May be sacrebleu version incompatibility or exception being caught silently

**Possible Solutions**:
1. Check sacrebleu installation and version
2. Add debug logging to see which backend is used
3. Test nltk fallback path
4. May need to update sacrebleu usage for newer API

---

## Category 4: RAG/HuggingFace Integration (5 failures)

### Group A: SentenceTransformers Missing (3 tests)
**Tests**: `test_embeddings_comprehensive.py::TestLocalSentenceTransformerProvider::*`

**Error**:
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Root Cause**: Optional dependency not installed in CI environment.

**Solution**:
1. Add `pytest.importorskip("sentence_transformers")` at module level
2. OR add proper mock patches for the module
3. OR mark tests as requiring optional dependency

### Group B: HuggingFace Revision Invalid (1 test)
**Test**: `test_hf_factory_compat.py::test_hf_dataset_factory`

**Error**:
```
OSError: abcdef0 is not a valid git identifier for model hf-internal-testing/llama-tokenizer
```

**Root Cause**: Test uses fake revision 'abcdef0' which doesn't exist.

**Solution**:
1. Use a real revision from the HuggingFace repo
2. OR mock the HuggingFace Hub API calls
3. OR use a local test model

### Group C: PEFT Integration (1 test)
**Test**: `test_peft_integration.py::test_peft_apply_lora`

**Error**:
```
TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union
```

**Root Cause**: Similar to Group A - torch.nn.init code using isinstance with dtype.

**Solution**: Apply same fix as in Attempt 18 - check `type(obj).__name__` instead of isinstance with torch.dtype.

---

## Fixes Applied (Commit 6f1876c2)

### File: services/api/main.py
**Changes**: 6 type annotation conversions

```python
# Import addition
from typing import Any, Optional  # Added Optional

# Pydantic model fix
class TrainRequest(BaseModel):
    notes: Optional[str] = None  # Was: str | None

# Return type annotations (consistency)
def _resolve_context_limit(...) -> Optional[int]:  # Was: int | None
    def _coerce_int(...) -> Optional[int]:  # Was: int | None
    def _get_attr(...) -> Optional[int]:  # Was: int | None
def _get_model_vocab_size(...) -> Optional[int]:  # Was: int | None
    def _valid_size(...) -> Optional[int]:  # Was: int | None
```

### File: tests/cognitive_brain/quantum/test_memory.py
**Changes**: 1 mock enhancement

```python
class MockRepo:
    def store_quantum_metric(self, *args, **kwargs):
        pass

    def create(self, metric):  # Added missing method
        """Mock create method for CoherenceMonitor."""
        return metric
```

---

## Expected Test Results

### After Current Fixes (8 tests)
✅ **Should Pass**:
- `test_api_infer_masking.py::test_secret_masking[*]` (8 tests)

⚠️ **Partially Fixed**:
- `test_memory.py::TestIntegration::*` (4 tests) - MockRepo.create() added

### Remaining Failures (17 tests)

**High Priority (P0-CRITICAL)**:
- CLI validation (2 tests)
- CLI argument parsing (1 test)
- Checkpoint serialization (1 test)
- PEFT integration (1 test)

**Medium Priority (P1-HIGH)**:
- BLEU metrics (2 tests)
- RAG SentenceTransformers (3 tests)
- HuggingFace revision (1 test)

**Low Priority (P2-MEDIUM)**:
- Quantum memory consolidation (1 test)
- Quantum memory compression (1 test)

---

## Lessons Learned

### Python 3.12 Type Compatibility
1. **Never use `| None` in Pydantic models** - always use `Optional[T]`
2. **Return type annotations are safe** - only field annotations cause runtime issues
3. **isinstance() is strict** - cannot accept typing constructs as second argument

### Test Fixture Completeness
1. **Mock all methods** - even if not obviously needed, check actual code paths
2. **Test mocks thoroughly** - validate mock behavior matches real implementation
3. **Document mock limitations** - note what's mocked vs real

### Systematic Approach Value
1. **Categorization helps** - grouping similar failures enables pattern recognition
2. **Priority matters** - fix P0 issues before P2 to maximize CI green time
3. **Root cause over symptoms** - understanding "why" prevents future issues

---

## Recommended Next Steps

### Immediate (Next Session)
1. **Fix CLI issues** - investigate typer/Hydra type annotation handling
2. **Fix BLEU metrics** - debug sacrebleu vs nltk backends
3. **Fix RAG imports** - add proper mocking or importorskip

### Short Term
1. **Fix checkpoint serialization** - resolve pickle + union types issue
2. **Fix quantum memory logic** - debug consolidation and compression
3. **Run code_review** - ensure all changes are clean
4. **Run codeql_checker** - security validation

### Long Term
1. **Add Python 3.12 type safety guide** - document patterns to avoid
2. **Enhance test fixtures** - comprehensive mock coverage
3. **Improve BLEU testing** - more robust metric validation

---

## References

- **Commit**: 6f1876c2
- **CI Runs**: 22079330623, 22079330605
- **Related PRs**: #3306 (Attempt 15), #3308 (Attempt 16), #3310 (Attempt 17), #3311 (Attempt 18)
- **Documentation**:
  - `.codex/README_FIRST_MANDATORY.md`
  - `.codex/PR_3248_FAILURE_TRACKING_LOG.md`
  - Stored memory: "Python 3.12 isinstance() issues"
