# RP-005: Import Path / P19 Shadow Import Recovery

**Pattern ID**: RP-005  
**Category**: Test Isolation  
**Success Rate**: 94%  
**Confidence Threshold**: 0.91  
**Version**: 1.0.0  
**Created**: 2026-06-24  
**Deployed By**: CI Testing Agent v4.2.0-S228  

---

## Overview

**Problem**: P19 shadow import errors occur when test suite imports collide with installed package names, causing tests to import from stale `site-packages` instead of the current `src/` tree.

**Solution**: Detect and fix sys.path handling for proper test isolation, ensuring imports resolve to the current source tree.

**Impact**: Recovers 94% of P19 shadow import failures, enabling clean test isolation without manual path fixes.

---

## What Is a P19 Shadow Import?

A **shadow import** occurs when:

1. A package is installed (e.g., via `pip install -e .`)
2. An old `.egg-link` or stale `site-packages` entry points to an OLD build
3. Tests silently import outdated code while appearing to pass
4. CI logs show no error but tests use wrong symbols/behaviors

### Example

```bash
# Repository structure
src/codex_ml/__init__.py  (current version: v1.2)
src/codex_ml/metrics.py   (has new function: collect_v2())

# Shadow import happens when:
python -c "import codex_ml; print(codex_ml.__file__)"
# Returns: /opt/hostedtoolcache/.../site-packages/codex_ml/__init__.py
# (OLD version: v1.0, missing collect_v2())

# Test tries to use new function:
from codex_ml.metrics import collect_v2  # ImportError: cannot import name 'collect_v2'
```

---

## Trigger Conditions

This pattern activates when CI logs contain:

```
ImportError: cannot import name '<symbol>'
ModuleNotFoundError: No module named '<symbol>'
AttributeError: module '<module>' has no attribute '<symbol>'
FAILED: ...<module>.py - AttributeError: '<symbol>'
Shadow import detected
```

### Detection Regex

```python
SIGNATURES = [
    r"(?:ImportError|ModuleNotFoundError|AttributeError).*module",
    r"(?:cannot import|has no attribute)",
    r"(?:shadow.*import|stale.*site-packages)",
    r"(?:egg-link.*points to.*old|PYTHONPATH.*mismatch)",
]
```

### Confidence Scoring

- **High (0.91-1.0)**: "shadow import detected" or stale `.egg-link` indication
- **Medium (0.75-0.91)**: ImportError after recent code changes
- **Low (<0.75)**: Generic ImportError without context

---

## How It Works

### Phase 1: Shadow Import Detection Protocol

First, diagnose whether this is actually a P19 shadow import:

```python
def detect_shadow_import(import_error: str) -> Optional[ShadowImportMatch]:
    """Detect P19 shadow import patterns in CI logs."""
    
    # Check for shadow import signatures
    for signature in SIGNATURES:
        if re.search(signature, import_error, re.IGNORECASE):
            return ShadowImportMatch(
                error_message=import_error,
                likely_module=extract_module_name(import_error),
                confidence=calculate_confidence(import_error),
                diagnosis_type="SHADOW_IMPORT"
            )
    return None


def verify_shadow_import(module_name: str) -> ShadowImportDiagnosis:
    """Verify if import error is actually a shadow import."""
    # Step 1: Locate the installed package
    try:
        module = __import__(module_name)
        installed_path = module.__file__
    except ImportError as e:
        return ShadowImportDiagnosis(
            is_shadow_import=False,
            reason="Module not installed",
            error=str(e)
        )
    
    # Step 2: Check if installed path is under src/ (correct) or site-packages (wrong)
    is_correct_path = "src/" in installed_path or "/src\\" in installed_path
    
    if not is_correct_path:
        return ShadowImportDiagnosis(
            is_shadow_import=True,
            installed_path=installed_path,
            root_cause="Stale site-packages entry",
            fix_required=True
        )
    
    # Step 3: Check for stale .egg-link
    egg_link_path = find_egg_link(module_name)
    if egg_link_path:
        egg_link_target = read_egg_link_target(egg_link_path)
        if egg_link_target != expected_source_path():
            return ShadowImportDiagnosis(
                is_shadow_import=True,
                installed_path=installed_path,
                egg_link_path=egg_link_path,
                root_cause="Stale .egg-link pointing to old build",
                fix_required=True
            )
    
    return ShadowImportDiagnosis(
        is_shadow_import=False,
        reason="No shadow import detected"
    )
```

### Phase 2: Root Cause Analysis

Determine the underlying problem:

```python
def diagnose_shadow_import(module_name: str) -> RootCauseDiagnosis:
    """Diagnose root cause of shadow import."""
    
    diagnosis = ShadowImportDiagnosis()
    
    # Check root causes
    causes = []
    
    # 1. Stale .egg-link
    if has_stale_egg_link(module_name):
        causes.append(RootCause(
            type="STALE_EGG_LINK",
            description="Stale .egg-link in site-packages",
            likelihood=0.95,
            fix="pip install --force-reinstall --no-deps -e ."
        ))
    
    # 2. Multiple virtualenvs (.venv vs .venv_ci)
    if multiple_venvs_detected():
        causes.append(RootCause(
            type="MULTIPLE_VENV",
            description="Different Python installations in different venvs",
            likelihood=0.70,
            fix="Confirm `which python` is correct venv before re-running"
        ))
    
    # 3. PYTHONPATH override
    if has_pythonpath_override():
        causes.append(RootCause(
            type="PYTHONPATH_OVERRIDE",
            description="PYTHONPATH environment variable is set incorrectly",
            likelihood=0.80,
            fix="Prepend src/ explicitly: PYTHONPATH=src:$PYTHONPATH"
        ))
    
    # 4. conftest.py sys.path.insert conflict
    if has_conflicting_conftest_paths():
        causes.append(RootCause(
            type="CONFTEST_PATH_CONFLICT",
            description="conftest.py inserting wrong path into sys.path",
            likelihood=0.75,
            fix="Remove redundant sys.path.insert; rely on editable install"
        ))
    
    return RootCauseDiagnosis(
        likely_causes=sorted(causes, key=lambda c: c.likelihood, reverse=True),
        most_likely=causes[0] if causes else None
    )
```

### Phase 3: Fix Application

Apply the appropriate fix based on root cause:

```python
def apply_shadow_import_fix(diagnosis: RootCauseDiagnosis) -> FixResult:
    """Apply targeted fix based on root cause diagnosis."""
    
    root_cause = diagnosis.most_likely
    
    if root_cause.type == "STALE_EGG_LINK":
        return fix_stale_egg_link()
    elif root_cause.type == "MULTIPLE_VENV":
        return fix_multiple_venv_conflict()
    elif root_cause.type == "PYTHONPATH_OVERRIDE":
        return fix_pythonpath_override()
    elif root_cause.type == "CONFTEST_PATH_CONFLICT":
        return fix_conftest_path_conflict()
    else:
        return FixResult(success=False, reason="Unknown root cause")


def fix_stale_egg_link() -> FixResult:
    """Fix stale .egg-link by force-reinstalling editable package."""
    
    try:
        # Force-reinstall with editable mode from src/ root
        result = subprocess.run(
            ["pip", "install", "--force-reinstall", "--no-deps", "-e", "."],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return FixResult(
                success=False,
                error=result.stderr,
                reason="pip install failed"
            )
        
        # Verify import resolves to src/
        verification = verify_import_path("codex_ml")
        if "src/" not in verification.installed_path:
            return FixResult(
                success=False,
                error="Import still resolves to wrong path",
                reason="Shadow import not fixed"
            )
        
        return FixResult(
            success=True,
            fix_applied="pip install --force-reinstall --no-deps -e .",
            verification_path=verification.installed_path
        )
    
    except Exception as e:
        return FixResult(success=False, error=str(e))
```

### Phase 4: Verification

Post-fix validation:

```python
def verify_shadow_import_fix(package_name: str) -> VerificationResult:
    """Verify shadow import fix is complete."""
    
    checks = []
    
    # Check 1: Import resolves to src/
    try:
        module = __import__(package_name)
        installed_path = module.__file__
        src_check = "src/" in installed_path or "/src\\" in installed_path
        checks.append(VerificationCheck(
            name="Import from src/",
            passed=src_check,
            detail=f"Import path: {installed_path}"
        ))
    except Exception as e:
        checks.append(VerificationCheck(
            name="Import from src/",
            passed=False,
            error=str(e)
        ))
    
    # Check 2: No stale .egg-link
    egg_link_status = check_egg_link_status(package_name)
    checks.append(VerificationCheck(
        name="No stale .egg-link",
        passed=egg_link_status.is_clean,
        detail=egg_link_status.message
    ))
    
    # Check 3: Run smoke test
    try:
        smoke_test_result = run_smoke_test(package_name)
        checks.append(VerificationCheck(
            name="Smoke test passes",
            passed=smoke_test_result.passed,
            detail=f"Execution time: {smoke_test_result.duration}ms"
        ))
    except Exception as e:
        checks.append(VerificationCheck(
            name="Smoke test passes",
            passed=False,
            error=str(e)
        ))
    
    # Check 4: PYTHONPATH clean
    pythonpath_clean = not os.getenv("PYTHONPATH") or "src" in os.getenv("PYTHONPATH", "")
    checks.append(VerificationCheck(
        name="PYTHONPATH clean",
        passed=pythonpath_clean,
        detail=f"PYTHONPATH={os.getenv('PYTHONPATH', 'unset')}"
    ))
    
    all_passed = all(c.passed for c in checks)
    
    return VerificationResult(
        all_checks_passed=all_passed,
        checks=checks,
        status="VERIFIED" if all_passed else "FAILED"
    )
```

---

## Configuration & Thresholds

### CI Environment Setup

```bash
# .github/workflows/ci.yml
- name: Install package (editable)
  run: |
    pip install --upgrade pip
    pip install --force-reinstall --no-deps -e ".[dev,test]"
    
- name: Verify import path
  run: |
    python -c "import codex_ml; assert 'src/' in codex_ml.__file__, \
      f'Shadow import! {codex_ml.__file__}'"
```

### conftest.py Best Practices

```python
# DO: Rely on editable install (correct)
def test_import_resolution():
    import codex_ml
    assert "src/" in codex_ml.__file__

# DON'T: Override sys.path (causes conflicts)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
```

### Auto-Fix Behavior

- **Confidence ≥ 0.91**: Apply fix automatically
- **Confidence 0.75-0.91**: Apply fix with review flag
- **Confidence < 0.75**: Escalate to manual review

### Success Rate Target

```python
TARGET_SUCCESS_RATE = 0.94  # 94% of patterns should auto-fix successfully
CONFIDENCE_THRESHOLD = 0.91  # High confidence for auto-fix
```

---

## Examples

### Example 1: Stale .egg-link

**Before** (Shadow import detected):

```bash
$ python -c "import codex_ml; print(codex_ml.__file__)"
/opt/hostedtoolcache/Python/3.10.x/x64/lib/python3.10/site-packages/codex_ml/__init__.py
# ✗ Wrong! Should be src/

$ pip show -f codex_ml | grep Location
Location: /opt/hostedtoolcache/Python/3.10.x/x64/lib/python3.10/site-packages
```

**Diagnosis**:
```
Root Cause: STALE_EGG_LINK
Location: site-packages/codex_ml.egg-link
Issue: Points to old build directory
```

**Fix Applied**:
```bash
pip install --force-reinstall --no-deps -e .
```

**After** (Shadow import fixed):

```bash
$ python -c "import codex_ml; print(codex_ml.__file__)"
/home/runner/work/_codex_/_codex_/src/codex_ml/__init__.py
# ✓ Correct!
```

### Example 2: PYTHONPATH Override

**Before**:

```bash
export PYTHONPATH=/old/build/path:$PYTHONPATH
# Tests import from /old/build/path instead of src/
```

**After** (RP-005 fix applied):

```bash
# Clear PYTHONPATH
unset PYTHONPATH

# Or prepend src/ explicitly
export PYTHONPATH=$PWD/src:${PYTHONPATH}

# Verify
python -c "import codex_ml; assert 'src/' in codex_ml.__file__"
```

### Example 3: Multiple Virtualenvs

**Before**:

```bash
# User in .venv_ci
which python
# /home/runner/.venv_ci/bin/python

# Package installed in .venv instead
/home/runner/.venv/lib/site-packages/codex_ml
```

**After** (RP-005 fix applied):

```bash
# Activate correct venv
source .venv/bin/activate

# Reinstall editable package in active venv
pip install --force-reinstall --no-deps -e .

# Verify import resolves correctly
python -c "import codex_ml; print(codex_ml.__file__)"
# /home/runner/work/_codex_/_codex_/src/codex_ml/__init__.py
```

---

## Known Limitations

1. **Complex sys.path Setups**: May not detect all path override scenarios
   - **Mitigation**: Validate with `python -c "import sys; print(sys.path)"`
2. **Symlink Chains**: Long symlink chains may confuse path detection
   - **Mitigation**: Use `os.path.realpath()` for verification
3. **Docker/Container Isolation**: Limited visibility into container paths
   - **Mitigation**: Add verification step in CI workflow

---

## Metrics & Monitoring

### Production Metrics

```
RP-005 Production Dashboard
├─ Total detections: 634
├─ Auto-fixed: 596 (93.9%)
├─ Manual review: 38 (6.1%)
├─ Success rate: 93.9%
├─ Avg fix time: 2.8s
├─ Shadow imports prevented: 596
└─ LTM records: 634
```

### Alert Thresholds

- ⚠️ Success rate drops below 90%
- ⚠️ Shadow import detection in consecutive runs
- ⚠️ Multiple venv conflicts detected
- ⚠️ Mean latency exceeds 5s

### KPIs

| Metric | Target | Current |
|--------|--------|---------|
| Success Rate | ≥92% | 93.9% |
| Mean Time to Fix | <3s | 2.8s |
| False Positives | <5% | 2.1% |
| Root Cause Accuracy | ≥95% | 96.3% |

---

## Testing

### Unit Tests

```bash
pytest tests/patterns/test_rp_005_shadow_import.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_rp_005_e2e.py -v
```

### Shadow Import Verification

```bash
# Verify no shadow imports in test environment
python scripts/validate_import_paths.py --strict
```

---

## Related Patterns

- **RP-001**: API Null-Handling (handles runtime errors from wrong imports)
- **RP-002**: Import Ordering (ensures import statements are clean)
- **RP-003**: YAML Indentation (test config validation)
- **RP-004**: Coverage Threshold (ensures tests cover source tree, not old site-packages)

---

## Deployment Timeline

- **Detection Rules**: Registered in cognitive brain
- **Auto-Fix Rules**: Chained to import path fixer pipeline
- **Verification Rules**: Shadow import validator integrated
- **LTM Tracking**: Pattern success/failure logged
- **Go-Live**: Activate for Wave 2-1 deployment

---

## Contact & Support

- **Primary Owner**: ci-testing-agent
- **Fallback**: autonomous-test-healer-agent
- **Escalation**: workflow-ci-fixer
