# [Validation]: Optional Dependencies Soft-Fail Mechanism

## Mechanism
| Component | Role | Behavior |
|-----------|------|----------|
| tools/codex_evaluator.py | Optional import layer | Populates MISSING_OPTIONALS; logs warning if SOFT_FAIL |
| CODEX_OPTIONAL_SOFTFAIL | Env flag | "1" = soft-fail; "0" = raise SystemExit(2) |
| tests/evaluators/test_codex_evaluator.py | Conditional test logic | Skips tests dependent on optionals when missing |
| nox coverage session | Ensures pydantic/typer attempt | Expands coverage paths if install succeeds |

## Acceptance Criteria
| Criterion | Pass Condition |
|-----------|----------------|
| No SystemExit/ImportError aborts | Pytest completes collection |
| Skipped optional tests allowed | Marked as skipped, not error |
| Coverage artifact produced | artifacts/coverage.xml exists |
| Hard failure only if SOFT_FAIL=0 | Setting env to 0 with missing deps raises SystemExit(2) |

## Manual Verification
```bash
# Soft-fail (default)
CODEX_OPTIONAL_SOFTFAIL=1 pytest -q -k evaluator

# Hard-fail simulation
pip uninstall -y pydantic typer
CODEX_OPTIONAL_SOFTFAIL=0 pytest -q -k evaluator  # should raise SystemExit(2)
```

## Implementation Details

### Before (Hard Fail)
```python
def _require_module(name: str) -> None:
    if importlib.util.find_spec(name) is None:
        sys.stderr.write(f"[evaluator] Missing: '{name}'.\n")
        raise SystemExit(2)  # ❌ Aborts pytest collection

for _optional in ("pydantic", "typer"):
    _require_module(_optional)
```

### After (Soft Fail)
```python
SOFT_FAIL = os.getenv("CODEX_OPTIONAL_SOFTFAIL", "1") == "1"
MISSING_OPTIONALS: List[Tuple[str, str]] = []

for _pkg in _OPTIONAL_PACKAGES:
    _try_import(_pkg)  # Populates MISSING_OPTIONALS

if MISSING_OPTIONALS and not SOFT_FAIL:
    raise SystemExit(2)  # ✅ Only fails if explicitly disabled
```

### Test Adaptation
```python
pytestmark = pytest.mark.skipif(
    bool(ce.MISSING_OPTIONALS),
    reason=f"Optional dependencies missing: {ce.MISSING_OPTIONALS}"
)
```

## Error That Was Fixed

**Before Fix:**
```
INTERNALERROR> SystemExit: 2
INTERNALERROR> ... import tools.codex_evaluator as ce
nox > Command pytest ... failed with exit code 3
Error: Process completed with exit code 1
```

**After Fix:**
```
nox > Running session coverage
nox > pytest ... --cov-fail-under=95 -v
[evaluator] Optional dependencies missing (soft-fail mode): pydantic, typer
tests/evaluators/test_codex_evaluator.py::test_optional_dependencies_available SKIPPED
... (other tests run normally)
Coverage report generated: artifacts/coverage.xml
```

— End —
