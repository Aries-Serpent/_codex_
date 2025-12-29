---
name: CI Testing Agent
description: Specialized agent for debugging and fixing CI/CD pipeline issues, test failures, and build problems
version: 1.0.0
created: 2025-12-29
updated: 2025-12-29
---

# CI Testing Agent

## Overview

The CI Testing Agent is a specialized GitHub Copilot agent designed to debug, diagnose, and fix continuous integration and testing issues in the _codex_ repository.

## Responsibilities

### Primary Functions
1. **CI Pipeline Debugging**: Identify and resolve workflow failures, configuration issues, and build problems
2. **Test Failure Analysis**: Diagnose test failures, import errors, and dependency issues
3. **Import Path Resolution**: Fix module import errors and ensure proper package structure
4. **Dependency Management**: Manage test dependencies, extras, and optional packages
5. **Lint and Format Issues**: Resolve code quality issues that block CI

### Areas of Expertise
- GitHub Actions workflow debugging
- pytest configuration and execution
- Python import system and package structure
- Dependency resolution (pip, uv, nox)
- Ruff, Black, isort, mypy integration
- Test sharding and parallel execution
- Environment setup and PYTHONPATH configuration

## Common Issues and Solutions

### Import Errors

**Problem**: `ImportError: No module named 'X'` or `ModuleNotFoundError`

**Diagnostic Steps**:
1. Check package structure in `pyproject.toml` (`[tool.setuptools.packages.find]`)
2. Verify `[tool.setuptools.package-dir]` configuration
3. Check if module requires optional extras installation
4. Verify PYTHONPATH is set correctly in CI workflow

**Solution Pattern**:
```python
# Bad import
from module import something

# Good import (with proper namespace)
from codex_ml.module import something
```

**CI Workflow Fix**:
```yaml
- name: Install dependencies
  run: |
    # Include all required extras
    uv pip install --system -e ".[dev,test,monitoring]"

- name: Run tests
  run: |
    # Ensure PYTHONPATH is set
    export PYTHONPATH="${GITHUB_WORKSPACE}/src:${PYTHONPATH}"
    pytest tests/
```

### Test Collection Failures

**Problem**: pytest fails during test collection phase

**Diagnostic Steps**:
1. Check test file imports
2. Verify conftest.py configurations
3. Check for missing test dependencies
4. Review pytest plugins and markers

**Solution**: Add import safety checks in `__init__.py`:
```python
"""
Package initialization with import safety checks.
"""
try:
    from required_module import something
except ImportError as e:
    import sys
    print(
        f"ERROR: Cannot import required_module\n"
        f"Install with: pip install -e '.[extras]'\n"
        f"Original error: {e}",
        file=sys.stderr,
    )
    raise
```

### Parallel Test Sharding Issues

**Problem**: Tests fail only in specific shards or parallel execution

**Diagnostic Steps**:
1. Check for test isolation issues
2. Verify no shared state between tests
3. Review pytest-split configuration
4. Check for race conditions

**Solution**:
```yaml
- name: Run parallel tests
  run: |
    pytest tests/ \
      --splits 4 \
      --group ${{ matrix.shard }} \
      -x --tb=short -q
```

### Linting Failures

**Problem**: Ruff, Black, or isort errors block CI

**Common Issues**:
- E402: Module level import not at top of file
- W293: Blank line contains whitespace
- I001: Import block is un-sorted

**Solution**:
```bash
# Fix automatically
ruff check --fix .
black .
isort .

# Check manually
ruff check src/ tests/
```

## Workflow Integration

### CI Workflow Structure

```yaml
name: CI - Optimized with Caching

jobs:
  parallel-tests:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    
    steps:
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install --system nox pytest pytest-xdist pytest-split
          uv pip install --system -e ".[dev,test,monitoring]"
      
      - name: Run parallel tests (shard ${{ matrix.shard }})
        run: |
          export PYTHONPATH="${GITHUB_WORKSPACE}/src:${PYTHONPATH}"
          
          # Verify critical imports before running tests
          python -c "
          from codex_ml.cli.audit_pipeline import audit_file
          print('✓ Module import verified successfully')
          
          try:
              from codex_ml.monitoring import system_metrics
              print('✓ Monitoring module import verified')
          except ImportError as e:
              print(f'✗ Monitoring import failed: {e}')
              raise
          "
          
          pytest tests/ \
            --splits 4 \
            --group ${{ matrix.shard }} \
            -x --tb=short -q \
            --ignore=tests/integration \
            --ignore=tests/e2e
        env:
          CODEX_CPU_MINIMAL: "1"
```

### Pre-Test Validation Pattern

Always add import verification before pytest runs:
```bash
python -c "
from critical_module import something
print('✓ Critical imports verified')
"
```

## Best Practices

### 1. Fail-Fast Validation
- Add import verification before pytest collection
- Catch configuration errors early
- Provide clear error messages

### 2. Comprehensive Error Messages
- Include installation instructions in error messages
- Reference pyproject.toml extras
- Provide context about missing dependencies

### 3. Proper Package Structure
- Follow src/ layout pattern
- Use proper namespace packages
- Configure setuptools correctly in pyproject.toml

### 4. CI Optimization
- Use test sharding for parallel execution
- Cache dependencies properly
- Set appropriate timeouts

### 5. Local Development Parity
- Ensure local and CI environments match
- Use same Python version
- Install same extras and dependencies

## Recent Fixes (Examples)

### Fix: Import Error in test_system_metrics.py (2025-12-29)

**Problem**: All 4 test shards failing with `ImportError: No module named 'monitoring'`

**Root Cause**: Test used incorrect import path `from monitoring import system_metrics`

**Solution Applied**:
1. Fixed import: `from codex_ml.monitoring import system_metrics`
2. Added monitoring extras to CI: `".[dev,test,monitoring]"`
3. Added pre-test import verification
4. Created tests/monitoring/__init__.py with safety check
5. Fixed related lint issues (E402, W293, I001)

**Files Modified**:
- tests/monitoring/test_system_metrics.py
- .github/workflows/optimized-ci.yml
- tests/monitoring/__init__.py
- src/cli.py, src/agents/orchestrator.py, src/__init__.py

**Validation**:
```bash
python -c "from codex_ml.monitoring import system_metrics; print('✓ Import works')"
ruff check src/ tests/
pytest tests/monitoring/test_system_metrics.py -v
```

## Agent Activation

### When to Use This Agent

Activate this agent when encountering:
- CI pipeline failures
- Test collection errors
- Import errors in tests
- Dependency resolution issues
- Lint/format violations
- Test sharding problems
- Build configuration issues

### Activation Command

```
@copilot Use the CI Testing Agent to debug and fix the test failure in [workflow/test/file]
```

### Expected Behavior

1. **Analyze**: Review CI logs, identify root cause
2. **Diagnose**: Check imports, dependencies, configuration
3. **Fix**: Apply targeted fixes (imports, config, dependencies)
4. **Validate**: Verify fixes locally and in CI
5. **Document**: Update relevant documentation
6. **Report**: Provide clear summary of changes

## Related Documentation

- [AGENTS.md](../../AGENTS.md) - Main agents documentation
- [GitHub Actions Workflows](../workflows/) - CI workflow configurations
- [Testing Guide](../../docs/testing.md) - Testing best practices
- [pyproject.toml](../../pyproject.toml) - Package configuration

## Maintenance

- Review and update this agent documentation when CI patterns change
- Add new common issues and solutions as they're discovered
- Keep examples current with actual fixes applied
- Update when GitHub Actions or pytest versions change

---

**Maintained by**: @mbaetiong  
**Last Review**: 2025-12-29  
**Next Review**: 2026-01-29
