# Testing Guide

This document describes the testing infrastructure, conventions, and best practices for the _codex_ project.

## Table of Contents

- [Overview](#overview)
- [Required Pytest Plugins](#required-pytest-plugins)
- [Running Tests](#running-tests)
- [Test Configuration](#test-configuration)
- [Environment Validation](#environment-validation)
- [CI/CD Testing](#cicd-testing)
- [Troubleshooting](#troubleshooting)

## Overview

The _codex_ project uses pytest as its primary testing framework with several plugins to enable parallel execution, test coverage reporting, and reliability improvements.

## Required Pytest Plugins

The following pytest plugins are **required** for the test suite to function correctly:

### Core Plugins

- **pytest** (>=7.0): Core testing framework
- **pytest-cov** (>=4.0): Code coverage reporting
- **pytest-xdist** (>=3.3): Parallel test execution with `-n auto` flag
- **pytest-timeout** (>=2.1): Test timeout management
- **pytest-rerunfailures** (>=12.0): Automatic retry of flaky tests
- **pytest-randomly** (>=3.10): Randomize test execution order

### Why These Plugins Are Required

1. **pytest-xdist**: Enables parallel test execution across multiple CPU cores, significantly reducing test runtime. Without this plugin, the `-n auto` flag will fail.

2. **pytest-rerunfailures**: Provides the `--reruns` and `--reruns-delay` flags to automatically retry flaky tests, improving test reliability in CI/CD environments.

3. **pytest-timeout**: Prevents tests from hanging indefinitely by enforcing timeout limits. Configuration is centralized in `pytest.ini`.

4. **pytest-cov**: Generates code coverage reports in multiple formats (XML, HTML, terminal) for CI/CD integration and local development.

5. **pytest-randomly**: Helps detect test interdependencies by randomizing test execution order.

## Running Tests

### Local Development

Basic test execution:
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest tests/ -n auto

# Run with automatic retries for flaky tests
pytest tests/ --reruns 2 --reruns-delay 1
```

### Full CI-equivalent Test Run

To run tests with all CI flags locally:
```bash
pytest tests/ \
  --cov=src \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  -v \
  --tb=short \
  -n auto \
  --dist=loadfile \
  --maxfail=5 \
  --reruns=2 \
  --reruns-delay=1
```

### Test Markers

The project uses pytest markers to categorize and filter tests. See `pytest.ini` for the full list of available markers.

Common markers:
- `@pytest.mark.smoke`: Quick validation tests
- `@pytest.mark.integration`: Cross-component integration tests
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.gpu`: GPU-specific tests
- `@pytest.mark.ml`: ML/tensor dependent tests

Run tests by marker:
```bash
# Run only smoke tests
pytest tests/ -m smoke

# Exclude slow tests
pytest tests/ -m "not slow"

# Run integration tests
pytest tests/ -m integration
```

## Test Configuration

### pytest.ini

Global pytest configuration is defined in `pytest.ini`:
- Test discovery paths
- Default command-line options
- Timeout settings (300s, thread method)
- Warning filters
- Test markers

**Important**: Timeout settings are centralized in `pytest.ini`. Do not duplicate timeout arguments in workflow files.

### Installation Order

The correct installation order is critical to prevent plugin conflicts:

```bash
# 1. Upgrade pip and build tools
python -m pip install --upgrade pip setuptools wheel

# 2. Install pytest plugins FIRST
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-rerunfailures

# 3. Install the package with test dependencies
pip install -e ".[test]"
```

This order ensures plugins are available before the editable package install.

## Environment Validation

### Validation Script

A validation script is provided to check your test environment:

```bash
python scripts/validate_test_env.py
```

This script checks:
- pytest installation and version
- All required plugin installations
- Command-line argument support (`-n`, `--reruns`, `--cov`, etc.)

**Exit codes:**
- `0`: All checks passed, environment is ready
- `1`: Validation failed, missing plugins or features

### Manual Validation

You can also manually verify plugins:

```bash
# Check pytest version
pytest --version

# List installed plugins
pytest --version --verbose

# Check specific plugin imports
python -c "import xdist; print('pytest-xdist:', xdist.__version__)"
python -c "import pytest_rerunfailures; print('pytest-rerunfailures: OK')"
python -c "import pytest_timeout; print('pytest-timeout: OK')"

# Test collection (dry run)
pytest --collect-only tests/
```

## CI/CD Testing

### GitHub Actions Workflow

The project uses `.github/workflows/test-comprehensive.yml` for CI testing with a matrix strategy across Python 3.9, 3.10, 3.11, and 3.12.

**Key workflow steps:**
1. Checkout code
2. Setup Python environment
3. Install dependencies (plugins first, then package)
4. Validate test environment with `scripts/validate_test_env.py`
5. Run tests with coverage
6. Upload coverage reports

### Coverage Requirements

- **Current coverage**: ~27.5%
- **Target coverage**: 70%
- Coverage reports are generated in XML (for CI) and HTML (for review)

## Troubleshooting

### Common Issues

#### "unrecognized arguments: -n auto"

**Cause**: `pytest-xdist` is not installed.

**Solution**:
```bash
pip install pytest-xdist>=3.3
```

#### "unrecognized arguments: --reruns"

**Cause**: `pytest-rerunfailures` is not installed.

**Solution**:
```bash
pip install pytest-rerunfailures>=12.0
```

#### "Workers crash immediately / 0 tests executed"

**Cause**: Missing plugins or plugin version conflicts.

**Solution**:
1. Run validation script: `python scripts/validate_test_env.py`
2. Reinstall from requirements: `pip install -r requirements-test.txt`
3. If using editable install: `pip install -e .[test]`

#### "timeout argument conflicts"

**Cause**: Duplicate timeout settings in command line and `pytest.ini`.

**Solution**: Remove `--timeout` and `--timeout-method` from command line. Use settings in `pytest.ini` instead.

### Plugin Version Compatibility

**Pinned versions in requirements-test.txt:**
- pytest==8.3.4
- pytest-cov==4.1.0
- pytest-xdist==3.3.1
- pytest-rerunfailures==12.0.0
- pytest-timeout==2.3.1

**Minimum versions in pyproject.toml:**
- pytest>=7.0
- pytest-cov>=4.0
- pytest-xdist>=3.3
- pytest-rerunfailures>=12.0
- pytest-timeout>=2.1

Use pinned versions for reproducible CI builds. Use minimum versions for development flexibility.

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pytest-rerunfailures documentation](https://github.com/pytest-dev/pytest-rerunfailures)

## Contributing

When adding new tests:
1. Follow existing test structure and naming conventions
2. Add appropriate markers for categorization
3. Ensure tests pass locally before pushing
4. Run with coverage to maintain/improve coverage metrics
5. Consider test execution time and mark slow tests appropriately

For questions or issues with the testing infrastructure, please open an issue or contact the maintainers.
