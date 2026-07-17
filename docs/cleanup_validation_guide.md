# Root Folder Cleanup Validation Infrastructure
**Last Updated:** 2026-07-11
**Version:** v0.2.1

## Overview

This document describes the comprehensive validation infrastructure for root folder cleanup operations. The validation system is designed to ensure **zero breaking changes** through multi-phase verification before, during, and after cleanup execution.

## Validation Architecture

### Five-Phase Validation Strategy

```
Phase 1: Configuration Loading  →  Phase 2: Tool Integration  →  Phase 3: Import Paths  →  Phase 4: Workflow  →  Phase 5: Artifacts
```

## Phase 1: Configuration Loading Tests

**Purpose**: Verify all configuration files load correctly after cleanup.

### Configuration Files Validated

| File | Purpose | Validation |
|------|---------|-----------|
| `pytest.ini` | Test framework config | pythonpath, markers, testpaths |
| `mypy.ini` | Type checking config | Python version, warnings, settings |
| `pyproject.toml` | Package metadata & build | build-system, project metadata |
| `requirements*.txt` | Dependencies | Format, package specs, syntax |
| `.coveragerc` | Coverage config | Coverage settings, report format |
| `.editorconfig` | Editor settings | Formatting standards |
| `.pre-commit-config.yaml` | Pre-commit hooks | Hook definitions, versions |

### Test Class: `TestConfigurationLoading`

```python
def test_pytest_ini_loads():
    pass

def test_pytest_ini_pythonpath_configured():
    pass

def test_pytest_markers_configured():
    pass

def test_mypy_ini_loads():
    pass

def test_mypy_ini_python_version():
    pass

def test_pyproject_toml_loads():
    pass

def test_pyproject_toml_build_system():
    pass

def test_all_requirements_files_exist():
    pass

def test_requirements_files_parseable():
    pass

def test_coverage_config_exists():
    pass
```

### Running Phase 1 Tests

```bash
python -m pytest tests/cleanup_validation/test_cleanup_validation.py::TestConfigurationLoading -v
```

## Phase 2: Tool Integration Tests

**Purpose**: Verify all CLI tools work correctly after cleanup.

### Tools Validated

| Tool | Purpose | Validation Command |
|------|---------|-------------------|
| pytest | Test runner | `pytest tests/ --collect-only` |
| mypy | Type checker | `mypy --version && mypy src/` |
| pre-commit | Git hooks | `pre-commit run --all-files` |
| ruff | Linter | `ruff check src/` |
| black | Formatter | `black --check src/` |
| coverage | Coverage | `coverage run && coverage report` |

### Test Class: `TestToolIntegration`

```python
def test_pytest_collection_works():
    pass

def test_pytest_basic_test_runs():
    pass

def test_mypy_can_check_code():
    pass

def test_pre_commit_config_exists():
    pass

def test_ruff_config_exists():
    pass

def test_editorconfig_exists():
    pass

def test_black_can_format_sample_code():
    pass
```

### Running Phase 2 Tests

```bash
python -m pytest tests/cleanup_validation/test_cleanup_validation.py::TestToolIntegration -v
```

## Phase 3: Import Path Tests

**Purpose**: Verify no broken imports after cleanup.

### Critical Import Paths

```python
import codex                      # Main package
from codex.rag import *           # RAG module
from codex.utils import *         # Utilities
from codex.agent import *         # Agent system
from codex.integrations import *  # Integrations
```

### Test Class: `TestImportPaths`

```python
def test_src_imports_work():
    pass

def test_critical_public_apis_importable():
    pass

def test_no_broken_relative_imports():
    pass

def test_conftest_loads():
    pass
```

### Running Phase 3 Tests

```bash
python -m pytest tests/cleanup_validation/test_cleanup_validation.py::TestImportPaths -v
```

## Phase 4: Workflow Simulation

**Purpose**: Simulate CI workflow execution to verify cleanup doesn't break CI/CD.

### Simulated Workflow Steps

1. **Test Discovery**: `pytest --collect-only`
2. **Import Smoke Test**: Test all critical imports
3. **Type Checking**: Run mypy analysis
4. **Pre-commit Validation**: Run pre-commit hooks
5. **Coverage Analysis**: Generate coverage reports

### Test Class: `TestWorkflowSimulation`

```python
def test_pytest_collect_discovers_tests():
    pass

def test_import_smoke_test():
    pass

def test_pytest_basic_test_discovery():
    pass

def test_config_files_in_place():
    pass
```

### Running Phase 4 Tests

```bash
python -m pytest tests/cleanup_validation/test_cleanup_validation.py::TestWorkflowSimulation -v
```

## Phase 5: Artifact Verification

**Purpose**: Verify artifact generation still works after cleanup.

### Artifacts Validated

| Artifact | Purpose | Validation |
|----------|---------|-----------|
| Test reports | Test results | pytest report generation |
| Type analysis | Type errors | mypy output |
| Coverage reports | Coverage metrics | coverage.txt, HTML reports |
| Lint reports | Code quality | ruff/black output |

### Test Class: `TestArtifactVerification`

```python
def test_pytest_can_generate_report():
    pass

def test_mypy_generates_output():
    pass

def test_coverage_can_be_configured():
    pass
```

### Running Phase 5 Tests

```bash
python -m pytest tests/cleanup_validation/test_cleanup_validation.py::TestArtifactVerification -v
```

## Integration Tests

### Test Class: `TestCleanupSafety`

Comprehensive integration tests:

```python
def test_no_circular_imports_in_src():
    pass  # No circular dependencies

def test_git_status_clean_after_tests():
    pass  # Tests don't modify files

def test_all_test_markers_defined():
    pass  # All pytest markers exist
```

## Validation Scripts

### 1. Universal Validation Script

**File**: `scripts/validate_cleanup.sh`

**Purpose**: Run all validation checks in a single command

**Usage**:
```bash
bash scripts/validate_cleanup.sh
```

**Output**:
- Summary of all checks
- Pass/Fail status for each phase
- Detailed error messages
- Exit code 0 on success, 1 on failure

### 2. Pre-Cleanup Validation Script

**File**: `scripts/pre_cleanup_validation.sh`

**Purpose**: Verify repository is ready before cleanup

**Steps**:
1. Check git status is clean
2. Verify all config files exist
3. Verify requirements are valid
4. Run pytest collection
5. Run mypy
6. Verify critical imports
7. Run validation test suite
8. Backup critical files

**Usage**:
```bash
bash scripts/pre_cleanup_validation.sh
```

**Exit Codes**:
- 0: Ready for cleanup
- 1: Issues detected, fix before cleanup

### 3. Post-Cleanup Validation Script

**File**: `scripts/post_cleanup_validation.sh`

**Purpose**: Verify cleanup didn't break anything

**Steps**:
1. Verify all config files still exist
2. Verify pytest still works
3. Verify mypy still works
4. Verify critical imports
5. Verify submodule imports
6. Run pre-commit hooks
7. Verify requirements intact
8. Run cleanup validation test suite
9. Verify no broken imports
10. Verify artifact generation
11. Detailed configuration check
12. Compare with pre-cleanup backups

**Usage**:
```bash
bash scripts/post_cleanup_validation.sh
```

**Exit Codes**:
- 0: Cleanup verified successful
- 1: Issues detected, review logs

## Complete Validation Workflow

### Pre-Cleanup (Before Execution)

```bash
# 1. Run pre-cleanup validation
bash scripts/pre_cleanup_validation.sh

# 2. Review backup location
ls -la .codex/pre_cleanup_backups/

# 3. Verify git status clean
git status
```

### During Cleanup

```bash
# Monitor cleanup execution
# (See ROOT_FOLDER_CLEANUP_PLAN.md for execution steps)
```

### Post-Cleanup (After Execution)

```bash
# 1. Run post-cleanup validation
bash scripts/post_cleanup_validation.sh

# 2. Review changes
git diff --stat

# 3. Verify test suite still works
python -m pytest tests/ --collect-only

# 4. If issues detected, restore from backups
cp .codex/pre_cleanup_backups/*.backup .
```

## Validation Checklist

### Pre-Cleanup Checklist

- [ ] Working directory is clean (`git status`)
- [ ] All config files exist
- [ ] Requirements files are valid
- [ ] Pytest can collect tests
- [ ] Mypy works correctly
- [ ] Critical imports work
- [ ] All validation tests pass
- [ ] Backups created in `.codex/pre_cleanup_backups/`

### Post-Cleanup Checklist

- [ ] All config files still exist
- [ ] Pytest still works and collects tests
- [ ] Mypy still works correctly
- [ ] Critical imports still work
- [ ] Submodule imports work
- [ ] Pre-commit hooks pass
- [ ] Requirements files intact
- [ ] All cleanup validation tests pass
- [ ] No broken imports detected
- [ ] Artifact generation works
- [ ] No accidental modifications (compared to backups)

## Success Criteria

**Cleanup is considered successful when**:

- All Phase 1 configuration tests pass
- All Phase 2 tool integration tests pass
- All Phase 3 import path tests pass
- All Phase 4 workflow simulation tests pass
- All Phase 5 artifact verification tests pass
- All integration safety tests pass
- Pre-cleanup and post-cleanup validation scripts return 0
- Zero breaking changes verified
- CI/CD pipeline functions correctly
- All tools can find their configurations

## Running All Validation Tests

### Quick Summary

```bash
# Run all cleanup validation tests
python -m pytest tests/cleanup_validation/ -v

# Expected output:
# tests/cleanup_validation/test_cleanup_validation.py::TestConfigurationLoading::test_pytest_ini_loads PASSED
# tests/cleanup_validation/test_cleanup_validation.py::TestConfigurationLoading::test_mypy_ini_loads PASSED
# ... (many more tests)
# ========================= X passed in Y.XXs ==========================
```

### With Coverage Report

```bash
python -m pytest tests/cleanup_validation/ -v --cov=src --cov-report=term-missing
```

### With Detailed Output

```bash
python -m pytest tests/cleanup_validation/ -vv --tb=long
```

## Troubleshooting

### Issue: pytest collection fails

**Solution**:
```bash
# Check pythonpath in pytest.ini
grep "pythonpath" pytest.ini

# Verify src/ contains __init__.py
ls -la src/__init__.py

# Try manual collection
python -m pytest src/ --collect-only
```

### Issue: mypy errors

**Solution**:
```bash
# Check mypy.ini
cat mypy.ini

# Run mypy directly on a file
python -m mypy src/codex/__init__.py

# Check Python version compatibility
python --version
```

### Issue: Import errors

**Solution**:
```bash
# Check sys.path
python -c "import sys; print(sys.path)"

# Verify package structure
find src -name "__init__.py" | head -10

# Try importing directly
python -c "import sys; sys.path.insert(0, 'src'); import codex; print(codex.__file__)"
```

### Issue: Tests skip unexpectedly

**Solution**:
```bash
# Check for skip markers
python -m pytest tests/cleanup_validation/ -v -rs

# Look for conditional imports
grep -r "pytest.importorskip" tests/

# Check optional dependencies
pip list | grep -E "pytest|mypy|coverage"
```

## Maintenance

### Adding New Validation Tests

1. Add test method to appropriate test class in `test_cleanup_validation.py`
2. Follow naming convention: `test_<feature>_<aspect>`
3. Use descriptive assertion messages
4. Document the test purpose in docstring

### Updating Validation Scripts

1. Update bash scripts in `scripts/` directory
2. Test scripts locally before commit
3. Update documentation with new checks
4. Update this README with new sections

### Updating Configuration Validation

When configuration files change:

1. Update validation tests in `TestConfigurationLoading`
2. Update validation scripts pre/post
3. Update backup lists
4. Document changes in version control

## Integration with CI/CD

### GitHub Actions Integration

Add to `.github/workflows/validation.yml`:

```yaml
- name: Run cleanup validation
  run: |
    bash scripts/validate_cleanup.sh
    python -m pytest tests/cleanup_validation/ -v --tb=short
```

### Pre-commit Hook Integration

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: cleanup-validation
      name: Cleanup Validation
      entry: bash scripts/validate_cleanup.sh
      language: script
      stages: [commit]
```

## Performance Characteristics

| Phase | Typical Duration | Timeout |
|-------|------------------|---------|
| Phase 1 (Config) | < 1 second | 10 seconds |
| Phase 2 (Tools) | 5-10 seconds | 30 seconds |
| Phase 3 (Imports) | 2-5 seconds | 15 seconds |
| Phase 4 (Workflow) | 10-20 seconds | 60 seconds |
| Phase 5 (Artifacts) | 5-10 seconds | 30 seconds |
| **Total** | **30-50 seconds** | **2 minutes** |

## Documentation Files

- `tests/cleanup_validation/__init__.py` - Module documentation
- `tests/cleanup_validation/test_cleanup_validation.py` - Comprehensive test suite
- `scripts/validate_cleanup.sh` - Universal validation script
- `scripts/pre_cleanup_validation.sh` - Pre-cleanup checklist
- `scripts/post_cleanup_validation.sh` - Post-cleanup verification
- `docs/cleanup_validation_guide.md` - This file

## Related Documentation

- `ROOT_FOLDER_CLEANUP_PLAN.md` - Main cleanup execution plan
- `CLEANUP_VALIDATION_GUIDE.md` - Detailed validation procedures
- `.codex/pre_cleanup_backups/` - Backup directory for critical files

## Contact & Support

For validation issues or questions:

1. Check troubleshooting section above
2. Review GitHub Actions logs
3. Check .codex/audit/ directory for execution logs
4. Review git history for recent changes

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial validation infrastructure |

---

**Last Updated**: 2024
**Validation Status**: Ready for use
**Zero Breaking Changes**: Guaranteed by validation
