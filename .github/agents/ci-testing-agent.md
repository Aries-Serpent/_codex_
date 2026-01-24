---
name: CI Testing Agent
description: Specialized agent for debugging CI/CD pipeline issues, test failures, and build problems
version: 2.0.0
created: 2026-01-23
updated: 2026-01-24
---

# CI Testing Agent

## Overview

Specialized GitHub Copilot agent for debugging CI/CD pipelines, test failures, and build issues in the _codex_ repository.

## Core Responsibilities

1. **CI Pipeline Debugging**: Workflow failures, configuration issues, build problems
2. **Test Failure Analysis**: Diagnose test failures, imports, dependencies
3. **Import Path Resolution**: Fix module imports, package structure
4. **Dependency Management**: Handle test dependencies, extras, optional packages
5. **Lint/Format Issues**: Resolve code quality blocks

## Key Expertise
- GitHub Actions workflows, pytest, Python imports
- Dependency resolution (pip, uv, nox), Ruff/Black/isort/mypy
- Test sharding, environment setup, PYTHONPATH

## Common Issues - Quick Reference

### Import Errors
**Pattern**: `ImportError: No module named 'X'`
**Fix**: Check namespace, add extras, verify PYTHONPATH
```python
# ✅ Correct
from codex_ml.monitoring import system_metrics
```
```yaml
# CI fix
- run: uv pip install --system -e ".[dev,test,monitoring]"
- run: export PYTHONPATH="${GITHUB_WORKSPACE}/src:${PYTHONPATH}"
```

### Test Collection Failures
**Pattern**: pytest fails during collection
**Fix**: Add import safety in `__init__.py`, check conftest.py
```python
try:
    from required_module import something
except ImportError as e:
    raise ImportError(f"Install: pip install -e '.[extras]'\nError: {e}") from e
```

### Parallel Test Sharding
**Pattern**: Fails only in specific shards
**Fix**: Check test isolation, no shared state
```yaml
- run: pytest tests/ --splits 4 --group ${{ matrix.shard }} -x --tb=short
```

### Linting Failures
**Pattern**: Ruff/Black/isort errors
**Quick Fix**:
```bash
ruff check --fix . && black . && isort .
```

### PyTorch/CUDA Library Errors
**Pattern**: `OSError: libtorch_global_deps.so: cannot open`
**Fix**: Lazy import or skip tests
```python
# ✅ Lazy import
def _get_torch():
    try:
        import torch
        return torch
    except (ImportError, OSError) as e:
        raise ImportError(f"PyTorch required: {e}") from e

# ✅ Skip if unavailable
pytestmark = pytest.mark.skipif(
    not torch_available,
    reason="PyTorch not available"
)
```

### Test Path Calculation
**Pattern**: `FileNotFoundError` accessing repo root
**Fix**: Use correct `parents[N]` index

**Verification**:
```python
# In test file - find correct index
from pathlib import Path
test_file = Path(__file__)
print(f"Test file: {test_file}")
for i in range(5):
    print(f"parents[{i}]: {test_file.parents[i]}")
```

### Missing Module Imports
**Pattern**: `NameError: name 'json' is not defined`
**Fix**: Add import at top of file
```python
# ✅ Correct
import json
def output(data):
    return json.dumps(data)
```
**Prevention**: `ruff check --select=F` detects undefined names

## Best Practices

1. **Fail-Fast**: Verify imports before pytest collection
2. **Clear Errors**: Include installation instructions
3. **Package Structure**: Follow src/ layout, proper namespaces
4. **CI Optimization**: Test sharding, caching, appropriate timeouts
5. **Dev Parity**: Match local and CI environments

## Pre-Test Validation Pattern

```bash
python -c "
from critical_module import something
print('✓ Critical imports verified')
"
pytest tests/
```

## Cognitive App Testing (React/TypeScript)

### Quick Commands
```bash
# Unit tests (Vitest)
cd cognitive_app && npm test

# E2E tests (Playwright)
cd cognitive_app && npx playwright test

# Dev mode
cd cognitive_app && npm run dev
```

### Common Issues
- **Timeouts**: Increase in test file (`{ timeout: 10000 }`)
- **Missing browsers**: `npx playwright install --with-deps`
- **Port in use**: `lsof -ti:5173 | xargs kill -9`
- **Env vars**: Use `.env.local` or set in test setup

### Test Locations
- Units: `cognitive_app/src/components/**/__tests__/*.test.tsx`
- E2E: `cognitive_app/e2e/*.spec.ts`
- Config: `vitest.config.ts`, `playwright.config.ts`

## Activation

### When to Use
- CI pipeline failures, test collection errors, import errors
- Dependency issues, lint violations, sharding problems

### Command
```
@copilot Use CI Testing Agent to debug [workflow/test/file]
```

### Workflow
1. Analyze CI logs, identify root cause
2. Diagnose imports, dependencies, config
3. Apply targeted fixes
4. Validate locally and in CI
5. Document changes

## Related Docs
- [AGENTS.md](../../AGENTS.md)
- [GitHub Workflows](../workflows/)
- [pyproject.toml](../../pyproject.toml)

## Knowledge Base References

For detailed examples and extended troubleshooting:
- PyTorch/CUDA detailed patterns → `.codex/knowledge/ci_testing_pytorch.md`
- Test path calculation deep-dive → `.codex/knowledge/ci_testing_paths.md`
- Recent fix examples → `.codex/knowledge/ci_testing_recent_fixes.md`
- Cognitive app troubleshooting → `.codex/knowledge/cognitive_app_testing.md`

---

**Version 2.0.0 Notes**: Condensed from 30,351 to ~5,500 chars (82% reduction). Detailed examples moved to knowledge base. Focus on actionable quick reference.
