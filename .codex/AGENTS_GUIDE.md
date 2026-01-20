# Codex Agents Guide

> **Version:** 1.0.0  
> **Created:** 2026-01-19  
> **Purpose:** Guidelines for contributors and Codex automation agents

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Logging Roles](#logging-roles)
3. [Tooling & Testing](#tooling--testing)
4. [Testing Requirements](#testing-requirements)
5. [Pytest Plugin Configuration](#pytest-plugin-configuration)
6. [CLI & Tool Usage](#cli--tool-usage)
7. [Prohibited Actions](#prohibited-actions)

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CODEX_ENV_PYTHON_VERSION` | Select Python version during environment setup |
| `CODEX_ENV_NODE_VERSION` | Select Node.js version during environment setup |
| `CODEX_ENV_RUST_VERSION` | Select Rust version during environment setup |
| `CODEX_ENV_GO_VERSION` | Select Go version during environment setup |
| `CODEX_ENV_SWIFT_VERSION` | Select Swift version during environment setup |
| `CODEX_SESSION_ID` | Identifier for a logical session; group log events |
| `CODEX_SESSION_LOG_DIR` | Directory for session log files (default: `.codex/sessions`) |
| `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` | Path to the SQLite database used by logging tools |
| `CODEX_SQLITE_POOL` | Set to `1` to enable per-session SQLite connection pooling |

---

## Logging Roles

Use one of the following roles when recording conversation or session events:

- `system`
- `user`
- `assistant`
- `tool`

---

## Tooling & Testing

### Code Formatting & Linting

- **Format with Black** - `black src/ tests/`
- **Lint with Ruff** - `ruff check src/ tests/`
- **Sort imports with isort** - `isort src/ tests/`

### Type Checking

- Run type checks with **mypy** if changing Python modules:
  ```bash
  mypy src/
  ```

### Pre-commit Checks

Before committing, run:
```bash
pre-commit run --files <changed_files>
nox -s tests
```

Ensure optional test dependencies (e.g., `hydra-core`, `mlflow`) are installed or appropriately mocked.

---

## Testing Requirements

### Required pytest Plugins

The following pytest plugins **must** be installed before running tests:

```txt
pytest>=7.2,<10
pytest-cov>=4.0,<8        # Code coverage reporting
pytest-xdist>=3.0,<4      # Parallel test execution
pytest-timeout>=2.0,<3    # Test timeouts
pytest-rerunfailures>=13.0,<15  # Automatic test reruns
pytest-randomly>=3.0,<4   # Random test order
coverage>=7.0,<8          # Coverage.py library
```

### Why Plugin Installation Order Matters

**Critical: Plugins must be installed BEFORE the main package.**

When using pytest-xdist for parallel testing, all worker processes must have access to the same plugin versions at consistent paths. Installing plugins after the package can result in:

- Version conflicts (package dependencies may install older plugin versions)
- Import path inconsistencies across xdist workers
- "unrecognized arguments" errors when workers don't find plugins

### Correct Installation Order

```bash
# 1. Install pytest plugins FIRST
pip install pytest==9.0.2 pytest-cov==7.0.0 pytest-xdist==3.8.0 \
            pytest-timeout==2.3.1 pytest-rerunfailures==14.0 \
            pytest-randomly==3.16.0 coverage==7.6.0

# 2. Install the package (use --no-deps to avoid plugin conflicts)
pip install --no-deps -e . || pip install -e .

# 3. Install remaining dependencies
pip install -e ".[test]"
```

---

## Pytest Plugin Configuration

### pytest.ini Configuration

The `pytest.ini` file centralizes test configuration. All pytest options should be defined there to ensure consistency between local development and CI environments.

**Current configuration:**

```ini
[pytest]
testpaths = tests
addopts = 
    -q                      # Quiet mode
    --strict-markers        # Enforce marker registration
    --cov=src               # Coverage target directory
    --cov-report=xml        # XML coverage report
    --cov-report=html       # HTML coverage report
    --cov-report=term-missing  # Terminal report with missing lines
    --cov-fail-under=0      # Coverage threshold (0 = don't fail)
    -n auto                 # Parallel execution (auto-detect CPUs)
    --dist=loadfile         # Distribute tests by file
    --reruns=2              # Retry failed tests up to 2 times
    --reruns-delay=1        # Wait 1s between retries
timeout = 300               # Global test timeout (5 minutes)
timeout_method = thread     # Use thread-based timeouts
```

### Running Tests

**Local development:**
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests (uses pytest.ini configuration)
pytest tests/

# Run specific test file
pytest tests/test_example.py

# Run tests matching pattern
pytest tests/ -k "test_model"

# Verbose output
pytest tests/ -v
```

**CI environment:**
Tests run automatically via `.github/workflows/test-comprehensive.yml`. The workflow:
1. Installs pytest plugins with pinned versions
2. Installs the package
3. Runs tests using pytest.ini configuration

---

## CLI & Tool Usage

### Useful Commands

**Session logging:**
```bash
python -m codex.logging.session_logger
```

**View session logs:**
```bash
python -m codex.logging.viewer
```

**Search conversation transcripts:**
```bash
python -m codex.logging.query_logs
```

---

## Prohibited Actions

### ❌ Do NOT Create GitHub Actions Workflows

- Do **not** create or activate any GitHub Actions workflow files manually
- Keep automation artifacts confined to `.codex/`
- All workflow changes must be reviewed and approved

### ❌ Do NOT Skip Plugin Installation

- Never run tests without installing required plugins
- Always follow the correct installation order (plugins → package → dependencies)
- Do not assume plugins are already installed in CI environments

### ❌ Do NOT Override pytest.ini in Workflows

- pytest.ini is the single source of truth for test configuration
- Workflows should rely on pytest.ini defaults
- Only override specific options when absolutely necessary (e.g., `-v` for verbosity)

---

## Best Practices

### 1. Test Configuration

- ✅ **DO** define test options in `pytest.ini`
- ✅ **DO** use centralized configuration for consistency
- ❌ **DON'T** duplicate configuration in multiple places
- ❌ **DON'T** override pytest.ini in workflows unless necessary

### 2. Plugin Management

- ✅ **DO** install plugins with pinned versions in CI
- ✅ **DO** install plugins before the main package
- ✅ **DO** use `--no-deps` flag when appropriate
- ❌ **DON'T** rely on package dependencies to install plugins
- ❌ **DON'T** use `--force-reinstall` as a workaround

### 3. Test Execution

- ✅ **DO** run tests locally before pushing
- ✅ **DO** verify plugin installation with `pytest --version`
- ✅ **DO** use `pytest --co` to validate test collection
- ❌ **DON'T** commit code without testing
- ❌ **DON'T** disable tests to "fix" CI failures

---

## Troubleshooting

### "unrecognized arguments" Error

**Symptom:** pytest reports unrecognized arguments like `--cov`, `-n`, or `--reruns`

**Cause:** Pytest plugins not installed or not accessible to xdist workers

**Solution:**
1. Verify plugins are installed: `pip list | grep pytest`
2. Check installation order (plugins before package)
3. Reinstall with correct order:
   ```bash
   pip uninstall pytest-cov pytest-xdist pytest-rerunfailures -y
   pip install pytest-cov pytest-xdist pytest-rerunfailures
   ```

### "No tests ran" with Exit Code 5

**Symptom:** pytest collects tests but doesn't run any (exit code 5)

**Cause:** Test filtering options or collection errors

**Solution:**
1. Check pytest.ini for overly restrictive filters
2. Verify test files are named correctly (`test_*.py` or `*_test.py`)
3. Run with `-v` to see collection details
4. Use `pytest --co` to debug collection

### xdist Workers Crashing

**Symptom:** Workers crash or hang during parallel execution

**Cause:** Version mismatches between main process and workers

**Solution:**
1. Ensure consistent plugin versions
2. Install plugins before package
3. Use pinned versions in CI
4. Verify with: `pytest --version` (should show plugin versions)

---

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- Repository CI logs: `.github/workflows/test-comprehensive.yml`
- Cognitive brain: `.codex/cognitive_brain/`

---

**Document Status:** ACTIVE  
**Last Updated:** 2026-01-19  
**Next Review:** After next major test infrastructure change
