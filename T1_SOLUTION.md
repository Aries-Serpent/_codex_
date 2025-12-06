# T1 Coverage Gate Implementation - Solution Summary

**Generated**: 2025-12-06T07:24:00Z  
**Author**: Copilot (based on guidance from @mbaetiong)  
**Commit**: 2021bae

## Overview

This document summarizes the concrete fixes applied to implement T1 (Coverage Gate Enforcement) as part of Phase 1 Foundation of the autonomous transformation plan. These changes establish the infrastructure for deterministic, coverage-enforced testing with prompt sanitization.

## Summary Table

| Area | Change | Why | How to Validate |
|------|--------|-----|-----------------|
| Deterministic tests | Added autouse deterministic seed fixture to `tests/conftest.py` | Prevent flaky tests and enforce deterministic behavior | Run `pytest -k deterministic` and observe stable seeds; tests produce identical results on repeated runs |
| Coverage gate in CI | Updated nox `tests` session to run `pytest --cov=src --cov=training --cov-fail-under=70` | Ensure Nox enforces coverage gate (previously misconfigured) | Run `nox -s tests` and confirm exit code non-zero when cov < 70% |
| Coverage gate in pytest | Added coverage addopts to `pytest.ini` including `--cov-fail-under=70` | Make pytest local runs behave same as CI | `pytest --help` shows coverage options; `pytest` enforces 70% threshold |
| Prompt sanitization | Added `src/utils/sanitize.py` with `sanitize_prompt()` function | Prevent XSS/script injection by escaping user prompts | Run `python -c "from src.utils.sanitize import sanitize_prompt; print(sanitize_prompt('<script>alert()</script>'))"` and assert output is escaped |
| CLI sanitization | Created `cli/inference.py` using sanitize function | Integrate sanitization into inference CLI workflow | Run `python cli/inference.py --prompt "<script>alert()</script>"` and assert output is escaped |
| Test for sanitize | Added `tests/test_sanitize.py` with 5 test cases | Ensure sanitize function behavior covered by tests | `pytest tests/test_sanitize.py --no-cov` should pass (5/5 tests) |

## Files Changed

### 1. tests/conftest.py

**Added**: Deterministic seed fixture (autouse=True)

```python
@pytest.fixture(autouse=True)
def set_deterministic_seed():
    """
    Autouse fixture to set deterministic seeds for randomness sources.
    This prevents flakiness arising from non-deterministic RNG state.
    """
    seed = int(os.environ.get("CODEX_TEST_SEED", "42"))
    random.seed(seed)
    # Guard optional numpy/torch usage...
```

**Benefits**:
- Prevents flaky tests from non-deterministic RNG
- Seeds random, numpy, and torch (when available)
- Configurable via CODEX_TEST_SEED environment variable
- Gracefully handles missing optional dependencies

### 2. noxfile.py

**Modified**: `tests` session to enforce coverage

```python
@nox.session(name="tests", python=PY_VERSIONS)
def tests(session: nox.Session) -> None:
    """
    Baseline test session with coverage enforcement.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    _show_vendor_scan(session)
    session.run(
        "pytest",
        "--cov=src",
        "--cov=training",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-fail-under=70",
        "-m",
        "not requires_torch",
        external=True,
    )
```

**Benefits**:
- Enforces 70% coverage threshold in CI
- Generates coverage reports (terminal + XML)
- Explicitly includes src/ and training/ packages
- Maintains marker-based test filtering

### 3. pytest.ini

**Modified**: Added coverage options to addopts

```ini
[pytest]
testpaths = tests
addopts = 
    -q
    --cov=src
    --cov=training
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=70
```

**Benefits**:
- Local pytest runs match CI behavior
- Developers see coverage by default
- Consistent coverage measurement
- Clear failure on insufficient coverage

### 4. src/utils/sanitize.py

**Created**: Prompt sanitization utility

```python
def sanitize_prompt(prompt: Optional[str]) -> str:
    """
    Escape a prompt string for safe HTML embedding / display.
    Returns empty string for None; escapes <, >, &, ", '
    """
    if prompt is None:
        return ""
    escaped = html.escape(str(prompt), quote=True)
    escaped = escaped.replace("'", "&#x27;")
    return escaped
```

**Benefits**:
- Prevents XSS attacks when prompts rendered to HTML
- Minimal dependency (uses stdlib html module)
- Clear documentation about limitations
- Easy to extend/replace with bleach later

### 5. cli/inference.py

**Created**: CLI inference wrapper with sanitization

```python
def run_inference(prompt: str) -> tuple[str, str]:
    """Placeholder inference with sanitized preview."""
    safe_preview = sanitize_prompt(prompt)
    result = f"<processed>{prompt}</processed>"  # placeholder
    return safe_preview, result
```

**Benefits**:
- Demonstrates sanitization usage
- Safe prompt echoing for user feedback
- Model receives original prompt (semantics preserved)
- Easy to integrate with real inference backend

### 6. tests/test_sanitize.py

**Created**: Comprehensive sanitization tests

5 test cases covering:
- Script tag escaping (`<script>` → `&lt;script&gt;`)
- None input handling (returns empty string)
- Quote escaping (both single and double)
- Ampersand escaping
- Safe text preservation

**Benefits**:
- Documents expected sanitization behavior
- Catches regressions
- Easy to extend with new test cases
- Fast execution (no external dependencies)

## Validation Results

✅ **All tests passing**: 5/5 sanitize tests pass  
✅ **Sanitization working**: CLI correctly escapes malicious input  
✅ **Coverage gate enforced**: pytest.ini and noxfile.py configured  
✅ **Deterministic fixture**: autouse=True ensures all tests use it  
⚠️ **Overall coverage**: Currently 1.19% (needs additional tests)

## Next Steps

### Immediate (T1 Completion)
1. Add focused unit tests to raise coverage to >= 70%
   - Target critical logic in `src/` and `training/`
   - Use `pytest --cov-report=term-missing` to identify uncovered lines
   - Prioritize high-value modules (checkpointing, tokenization, training engine)

### Phase 1 Continuation
2. **T5**: Integrate sanitization more broadly (all user input points)
3. **T9**: Add security scans to CI (Bandit, pip-audit, detect-secrets)
4. **T7**: Implement health probes (/health, /ready endpoints)
5. **T8**: Add Prometheus metrics (/metrics endpoint)
6. **P0 Stubs**: Clean up blocking stubs identified in audit

## Notes

- These are **minimal, targeted fixes** to establish the foundation
- More tests are required to reach the 70% coverage threshold
- The sanitizer is basic (HTML escaping); consider `bleach` for richer sanitization
- Coverage enforcement will help maintain quality as codebase evolves
- Deterministic fixtures prevent CI flakiness from RNG differences

## Validation Commands

```bash
# Run sanitize tests
pytest tests/test_sanitize.py --no-cov -v

# Test CLI sanitization
python cli/inference.py --prompt "<script>alert()</script>"
# Expected output line 1: &lt;script&gt;alert()&lt;/script&gt;

# Check coverage configuration
grep "cov-fail-under" pytest.ini noxfile.py

# Run nox tests (when ready)
nox -s tests-3.12

# View coverage report
pytest --cov=src --cov-report=term-missing
```

## References

- **Master Plan**: `.github/prompts/sprint_execution_plan/MASTER_ORCHESTRATOR.md`
- **T1 Task Details**: `.github/prompts/sprint_execution_plan/phase_1_foundation/T1_coverage_gate_enforcement.md`
- **Commit**: 2021bae
- **PR Comment**: #3619684252
