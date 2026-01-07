---
name: CI Testing Agent
description: Specialized agent for debugging and fixing CI/CD pipeline issues, test failures, and build problems
version: 1.0.0
created: 2024-12-29
updated: 2024-12-29
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

### Fix: Import Error in test_system_metrics.py (2024-12-29)

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

## Cognitive App Testing (Added 2026-01-06)

### Overview

Extended capabilities for testing the React/TypeScript cognitive app in addition to Python backend testing.

### Responsibilities

1. **Unit Testing (Vitest)**: Run and debug Jest/Vitest tests for React components
2. **E2E Testing (Playwright)**: Execute browser-based tests for user workflows
3. **Dev Mode Validation**: Test application behavior in development environment
4. **Component Testing**: Validate lazy initialization, state management, and props
5. **Environment Configuration**: Test various VITE_* environment variable combinations

### Cognitive App Test Execution

#### Unit Tests with Vitest

```bash
cd cognitive_app

# Install dependencies if not present
if [ ! -d "node_modules" ]; then
  npm install
fi

# Run specific test suite
npm test -- CodeGenerator.lazy-init.test.tsx

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

#### E2E Tests with Playwright

```bash
cd cognitive_app

# Install Playwright browsers
npx playwright install --with-deps

# Start dev server in background (async mode)
npm run dev &
DEV_PID=$!

# Wait for server to be ready
sleep 5

# Run E2E tests
npx playwright test e2e/code-generator-lazy-init.spec.ts --reporter=list

# Run with UI
npx playwright test --ui

# Cleanup dev server
kill $DEV_PID
```

#### Dev Mode Testing Protocol

When testing in dev mode, validate these scenarios:

**Test 2: No API Key**
```bash
# Start without VITE_CODEX_KEY
unset VITE_CODEX_KEY
npm run dev

# Verify:
# - Error message: "Missing VITE_CODEX_KEY environment variable"
# - Red status indicator visible
# - Generate button disabled
```

**Test 3: With API Key**
```bash
# Start with valid API key
export VITE_CODEX_KEY="test-key-12345"
npm run dev

# Verify:
# - Initial "Checking..." status (yellow)
# - Transitions to "Connected" or "Error"
# - Generate button becomes enabled
```

**Test 4: Mock Fallback**
```bash
# Start with invalid API key
export VITE_CODEX_KEY="invalid-key"
npm run dev

# Enter prompt (10+ characters)
# Click generate
# Verify:
# - Mock client activates
# - Toast shows "(Demo Mode)"
# - Code generation succeeds
```

**Test 5: Timing Configuration**
```bash
# Test with fast timing
export VITE_STAGE_EXECUTION_TIME_MS=200
npm run dev

# Test with slow timing
export VITE_STAGE_EXECUTION_TIME_MS=2000
npm run dev

# Test invalid values (should fall back to 800ms)
export VITE_STAGE_EXECUTION_TIME_MS=0
export VITE_STAGE_EXECUTION_TIME_MS=20000
export VITE_STAGE_EXECUTION_TIME_MS=invalid
npm run dev
```

### Common Cognitive App Issues

#### Issue: Tests timeout
**Solution**: Increase timeout in test file or config
```typescript
// In test file
test('slow test', async () => {
  // test code
}, { timeout: 10000 });

// In vitest.config.ts
export default defineConfig({
  test: {
    testTimeout: 10000,
  },
});
```

#### Issue: Component not rendering
**Solution**: Check for missing dependencies or incorrect imports
```bash
# Verify imports
npm run build --dry-run

# Check for missing peer dependencies
npm ls

# Reinstall if needed
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Environment variables not loading
**Solution**: Use .env.local or set in test setup
```typescript
// In test setup
beforeEach(() => {
  import.meta.env.VITE_CODEX_KEY = 'test-key';
});

// Or use .env.local file
// cognitive_app/.env.local
VITE_CODEX_KEY=test-key-12345
VITE_CODEX_API=http://localhost:8000
```

#### Issue: Playwright browsers not installed
**Solution**: Install browsers before running E2E tests
```bash
npx playwright install
# Or with system dependencies
npx playwright install --with-deps
```

#### Issue: Dev server port already in use
**Solution**: Kill existing process or use different port
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 5174
```

### Test File Locations

- **Unit Tests**: `cognitive_app/src/components/**/__tests__/*.test.tsx`
- **E2E Tests**: `cognitive_app/e2e/*.spec.ts`
- **Test Config**: `cognitive_app/vitest.config.ts`
- **Playwright Config**: `cognitive_app/playwright.config.ts` (create if needed)
- **Test Setup**: `cognitive_app/src/test/setup.ts`

### Test Reports & Documentation

- [Test Suite README](../../cognitive_app/TEST_SUITE_README.md)
- [Testing Validation Report](../../reports/cognitive_app_testing_validation.md)
- [E2E Test Spec](../../cognitive_app/e2e/code-generator-lazy-init.spec.ts)
- [Unit Test Suite](../../cognitive_app/src/components/code/__tests__/CodeGenerator.lazy-init.test.tsx)

### Agent Usage for Cognitive App

#### Run All Cognitive App Tests
```
@copilot Use CI Testing Agent to run complete test suite for cognitive app
```

Agent will:
1. Install dependencies if needed
2. Run unit tests with Vitest
3. Start dev server
4. Run E2E tests with Playwright  
5. Generate coverage report
6. Report results with pass/fail status

#### Debug Specific Test Failure
```
@copilot Use CI Testing Agent to debug failing test "should show red error indicator"
```

Agent will:
1. Read test file and component code
2. Run test with verbose output
3. Analyze failure stack trace
4. Identify root cause (code bug, config, timing issue)
5. Apply fix or suggest solution
6. Re-run test to validate fix

#### Validate in Dev Mode
```
@copilot Use CI Testing Agent to validate cognitive app behavior in dev mode with all test scenarios
```

Agent will:
1. Start dev server in background
2. Test each scenario (no API key, with API key, mock fallback, timing)
3. Verify UI states and interactions
4. Check console for errors
5. Stop dev server
6. Report findings and any issues

---

**Maintained by**: @mbaetiong  
**Last Review**: 2026-01-06  
**Next Review**: 2025-02-06
