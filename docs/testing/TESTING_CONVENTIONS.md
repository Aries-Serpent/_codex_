# Testing Conventions

This document outlines the testing conventions and best practices for the _codex_ repository. Following these conventions ensures consistency, maintainability, and prevents common configuration errors.

---

## Table of Contents

1. [Pytest Configuration Strategy](#pytest-configuration-strategy)
2. [Centralized vs. Workflow-Specific Settings](#centralized-vs-workflow-specific-settings)
3. [Plugin Requirements](#plugin-requirements)
4. [Timeout Configuration](#timeout-configuration)
5. [Coverage Requirements](#coverage-requirements)
6. [Test Markers](#test-markers)
7. [Workflow Testing Patterns](#workflow-testing-patterns)
8. [Common Pitfalls](#common-pitfalls)
9. [Examples](#examples)

---

## Pytest Configuration Strategy

### Centralized Configuration (pytest.ini)

The repository uses **centralized pytest configuration** in `pytest.ini` for settings that should apply to **all test runs**. This prevents duplication, ensures consistency, and avoids argument conflicts.

**Location**: `/pytest.ini`

**Key Principle**: If a setting should apply globally, it belongs in `pytest.ini`. Do not duplicate these settings in workflow files.

### Current Global Settings

```ini
[pytest]
testpaths = tests
addopts = 
    -q
    --strict-markers
    --timeout=300
    --timeout-method=thread
filterwarnings =
    ignore::DeprecationWarning
```

**What this means**:
- All test runs automatically use 300-second timeouts
- Thread-based timeout method is used globally
- Deprecation warnings are ignored
- Strict marker enforcement is enabled

---

## Centralized vs. Workflow-Specific Settings

### ✅ Settings That Belong in pytest.ini

These settings should **always** be in `pytest.ini`, never duplicated in workflow files:

| Setting | Purpose | Example |
|---------|---------|---------|
| `--timeout` | Global test timeout | `--timeout=300` |
| `--timeout-method` | Timeout mechanism | `--timeout-method=thread` |
| `--strict-markers` | Marker validation | Enabled by default |
| `-q` / `-v` | Output verbosity (global default) | `-q` for quiet |
| `filterwarnings` | Warning filters | `ignore::DeprecationWarning` |
| `testpaths` | Default test discovery paths | `tests` |

### ✅ Settings That Belong in Workflows

These settings are **appropriate for workflow-specific configuration**:

| Setting | Purpose | Example |
|---------|---------|---------|
| `--cov` | Coverage targets | `--cov=src/codex/rag` |
| `--cov-report` | Coverage report formats | `--cov-report=xml` |
| `--cov-fail-under` | Coverage thresholds | `--cov-fail-under=90` |
| `-n auto` | Parallel execution | `-n auto` (xdist) |
| `--dist` | Distribution strategy | `--dist=loadfile` |
| `--maxfail` | Fail-fast behavior | `--maxfail=5` |
| `--reruns` | Retry logic | `--reruns=2` |
| `-k` | Test selection | `-k "not slow"` |
| `-m` | Marker selection | `-m "smoke"` |

### ⚠️ Per-Workflow Overrides (Use Sparingly)

If a workflow truly needs to override a global setting:

```yaml
# Example: Override timeout for long-running integration tests
- name: Run integration tests
  run: |
    pytest tests/integration/ \
      --timeout=600 \  # Override 300s global timeout
      --timeout-method=thread \
      -v
```

**Best Practice**: Document why the override is needed in a comment.

---

## Plugin Requirements

### Required Plugins

Install these pytest plugins as specified in workflows:

| Plugin Package | Provides Flags | Purpose |
|----------------|----------------|---------|
| `pytest` | Core functionality | Base test framework |
| `pytest-cov` | `--cov`, `--cov-report` | Code coverage |
| `pytest-xdist` | `-n`, `--dist` | Parallel execution |
| `pytest-timeout` | `--timeout`, `--timeout-method` | Test timeouts |
| `pytest-rerunfailures` | `--reruns`, `--reruns-delay` | Test retries |

### ⚠️ Common Plugin Name Confusion

**CORRECT**: `pytest-rerunfailures`  
**WRONG**: `pytest-retry` (different package)

The `--reruns` and `--reruns-delay` flags are provided by **pytest-rerunfailures**, not pytest-retry.

**Installation**:
```bash
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-rerunfailures
```

**Workflow Example**:
```yaml
- name: Install test dependencies
  run: |
    pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-rerunfailures
```

---

## Timeout Configuration

### Global Timeout (pytest.ini)

```ini
[pytest]
addopts = 
    --timeout=300
    --timeout-method=thread
```

**What this means**:
- Every test has a 300-second (5-minute) timeout
- Timeouts use thread-based interruption
- No need to specify `--timeout` in workflow files

### When to Override

Override the global timeout only for:
1. **Long-running integration tests** (e.g., 600s for ML model training)
2. **Performance benchmarks** (e.g., 1800s for comprehensive benchmarks)
3. **Tests that need shorter timeouts** (e.g., 60s for unit tests)

**Example Override**:
```yaml
- name: Run long integration tests
  run: |
    pytest tests/integration/ \
      --timeout=600 \  # Override for long tests
      --timeout-method=thread
```

### ❌ DON'T Duplicate Global Settings

**BAD** - Duplicates pytest.ini settings:
```yaml
- name: Run tests
  run: |
    pytest tests/ \
      --timeout=300 \          # ❌ Already in pytest.ini
      --timeout-method=thread  # ❌ Already in pytest.ini
```

**GOOD** - Relies on pytest.ini:
```yaml
- name: Run tests
  run: |
    pytest tests/  # ✅ Uses 300s timeout from pytest.ini
```

---

## Coverage Requirements

### Repository-Wide Coverage Target

**Current**: ~27.5%  
**Target**: 70%

### Module-Specific Targets

| Module | Target | Current |
|--------|--------|---------|
| RAG Pipeline (`src/codex/rag/`) | 90%+ | In progress |
| Core Library (`src/codex/`) | 70%+ | ~27.5% |
| ML Components (`src/codex_ml/`) | 60%+ | Low |
| Agents (`agents/`) | 50%+ | Low |

### Workflow Coverage Configuration

```yaml
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=src \                      # Coverage target
      --cov-report=xml \               # XML for Codecov
      --cov-report=html \              # HTML for human review
      --cov-report=term-missing \      # Terminal output
      --cov-fail-under=70              # Fail if below threshold
```

---

## Test Markers

### Available Markers

Defined in `pytest.ini`:

| Marker | Purpose | Usage |
|--------|---------|-------|
| `smoke` | Quick validation tests | `@pytest.mark.smoke` |
| `slow` | Long-running tests | `@pytest.mark.slow` |
| `integration` | Cross-component tests | `@pytest.mark.integration` |
| `live` | Tests requiring network | `@pytest.mark.live` |
| `not_live` | Offline-only tests | `@pytest.mark.not_live` |
| `gpu` | GPU-specific tests | `@pytest.mark.gpu` |
| `cpu` | CPU-only tests | `@pytest.mark.cpu` |
| `ml` | ML/tensor dependent | `@pytest.mark.ml` |
| `security` | Security-focused tests | `@pytest.mark.security` |

### Running Tests by Marker

```bash
# Run only smoke tests
pytest -m smoke

# Skip slow tests
pytest -m "not slow"

# Run integration tests without network
pytest -m "integration and not_live"
```

### Adding New Markers

1. Add to `pytest.ini`:
```ini
markers =
    your_marker: Description of your marker
```

2. Use in tests:
```python
@pytest.mark.your_marker
def test_something():
    pass
```

---

## Workflow Testing Patterns

### Pattern 1: Comprehensive Test Suite

**Use case**: Run all tests across multiple Python versions

```yaml
name: Comprehensive Tests

jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - name: Install dependencies
        run: |
          pip install -e ".[test]"
          pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-rerunfailures
      
      - name: Run tests
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            -n auto \
            --dist=loadfile \
            --maxfail=5 \
            --reruns=2 \
            --reruns-delay=1
        env:
          CODEX_FORCE_CPU: "1"
```

### Pattern 2: Module-Specific Tests

**Use case**: Test a specific module with high coverage requirements

```yaml
name: RAG Module Tests

jobs:
  test:
    steps:
      - name: Run RAG tests
        run: |
          pytest tests/test_rag_*.py \
            --cov=src/codex/rag \
            --cov-report=xml \
            --cov-fail-under=90 \
            -v \
            --tb=short \
            -n auto
```

### Pattern 3: Smoke Tests (Fast CI)

**Use case**: Quick validation for every PR

```yaml
name: Smoke Tests

jobs:
  smoke:
    steps:
      - name: Run smoke tests
        run: |
          pytest -m smoke \
            -v \
            --maxfail=1 \
            --tb=short
```

---

## Common Pitfalls

### ❌ Pitfall 1: Duplicate Timeout Arguments

**Problem**: Specifying `--timeout` in workflow when it's already in `pytest.ini`

**Symptoms**:
```
pytest: error: unrecognized arguments: --timeout=300 --timeout-method=thread
```

**Solution**: Remove timeout arguments from workflow, rely on `pytest.ini`

**Example**:
```yaml
# ❌ BAD - Causes error
pytest tests/ --timeout=300 --timeout-method=thread

# ✅ GOOD - Uses pytest.ini defaults
pytest tests/
```

---

### ❌ Pitfall 2: Wrong Plugin Package Name

**Problem**: Installing `pytest-retry` instead of `pytest-rerunfailures`

**Symptoms**:
```
pytest: error: unrecognized arguments: --reruns=2 --reruns-delay=1
```

**Solution**: Install correct plugin:
```bash
# ❌ WRONG
pip install pytest-retry

# ✅ CORRECT
pip install pytest-rerunfailures
```

---

### ❌ Pitfall 3: Conflicting Coverage Configurations

**Problem**: Multiple coverage configurations in different places

**Symptoms**:
- Inconsistent coverage reports
- Unexpected coverage failures

**Solution**: Centralize coverage configuration in workflows, not pytest.ini

**Example**:
```yaml
# ✅ GOOD - Explicit coverage config in workflow
pytest tests/ \
  --cov=src \
  --cov-report=xml \
  --cov-fail-under=70
```

---

## Examples

### Example 1: Basic Test Run

```yaml
- name: Run tests
  run: pytest tests/
```

**What happens**:
- Uses 300s timeout from `pytest.ini`
- Uses thread-based timeout method from `pytest.ini`
- Runs quietly (`-q` from `pytest.ini`)
- Ignores deprecation warnings from `pytest.ini`

---

### Example 2: Coverage Test Run

```yaml
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=src \
      --cov-report=xml \
      --cov-report=html \
      --cov-fail-under=70
```

**What happens**:
- Everything from Example 1, plus:
- Collects coverage for `src/` directory
- Generates XML and HTML reports
- Fails if coverage is below 70%

---

### Example 3: Parallel Test Run with Retries

```yaml
- name: Run tests in parallel with retries
  run: |
    pytest tests/ \
      --cov=src \
      --cov-report=xml \
      -n auto \
      --dist=loadfile \
      --reruns=2 \
      --reruns-delay=1
```

**What happens**:
- Everything from Example 2, plus:
- Runs tests in parallel (auto-detect CPU count)
- Distributes tests by file
- Retries failed tests twice with 1s delay

---

### Example 4: Marker-Based Test Selection

```yaml
- name: Run smoke tests
  run: pytest -m smoke -v

- name: Run integration tests (offline)
  run: pytest -m "integration and not_live" -v

- name: Run all except slow tests
  run: pytest -m "not slow" -v
```

---

## Validation Checklist

Before adding or modifying test workflows:

- [ ] Check if setting exists in `pytest.ini` (don't duplicate)
- [ ] Use correct plugin package names (`pytest-rerunfailures`, not `pytest-retry`)
- [ ] Document any global setting overrides with comments
- [ ] Test locally before committing workflow changes
- [ ] Verify no duplicate timeout arguments
- [ ] Ensure coverage targets are appropriate for module
- [ ] Use appropriate test markers for selection
- [ ] Add retry logic only where needed (flaky tests)

---

## Quick Reference

### Install Test Dependencies
```bash
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-rerunfailures
```

### Run Tests Locally (Matches CI)
```bash
# Basic
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html

# Parallel with retries
pytest tests/ -n auto --reruns=2
```

### Check Configuration
```bash
# Show pytest configuration
pytest --co -q

# Show markers
pytest --markers

# Dry run
pytest --collect-only
```

---

## Related Documentation

- **Pytest Configuration**: `/pytest.ini`
- **Workflow Files**:
  - `.github/workflows/test-comprehensive.yml`
  - `.github/workflows/test-rag.yml`
- **Custom Actions**: `.github/actions/setup-python-cached/`
- **Cognitive Brain**: `.codex/cognitive_brain/CI_WORKFLOW_FIXES_2026_01_17.md`

---

## Maintenance

This document should be updated when:
- New global pytest settings are added to `pytest.ini`
- New test markers are introduced
- Coverage targets change
- New testing patterns emerge
- Plugin requirements change

**Last Updated**: 2026-01-17  
**Maintained By**: AI Agent (@copilot) + Human Admin (@mbaetiong)
