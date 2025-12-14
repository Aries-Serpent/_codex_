# Testing & Coverage Guide

## Primary Test Runner: Pytest

The project uses **pytest** as the primary test runner with comprehensive CI/CD integration.

### Quick Start

**Basic test run:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

**Run specific test categories:**
```bash
pytest -m smoke              # Quick validation tests
pytest -m "not slow"         # Skip slow tests
pytest -m integration        # Integration tests
pytest -m ml                 # ML/tensor dependent tests
```

See `tests/README.md` for detailed testing instructions and all available markers.

## CI/CD Integration

### Automated Testing in GitHub Actions

Every push and pull request triggers the pytest CI workflow (`.github/workflows/ci-pytest.yml`):

**Workflow features:**
- Runs on: Python 3.11+ (ubuntu-latest)
- Test execution with pytest
- Coverage collection (HTML, XML, JSON formats)
- Coverage threshold enforcement (90% minimum, configurable)
- Fast fail on test failures
- Artifact uploads (30-day retention)
- Automatic PR comments with coverage summary

**Coverage threshold:**
- Default: 90% minimum
- Configurable via `COVERAGE_THRESHOLD` environment variable in workflow
- Build fails if coverage is below threshold

**Viewing CI results:**
1. Navigate to the PR or commit
2. Check the "CI - Pytest with Coverage" workflow status
3. View detailed logs in the workflow run
4. Download coverage artifacts from the workflow summary page
5. PR comment includes coverage summary and artifact download links

### Manual Workflow Execution

To re-run the pytest workflow from the GitHub web UI:
1. Go to Actions tab
2. Select "CI - Pytest with Coverage" workflow
3. Click "Run workflow" button
4. Select branch and trigger the run

## Coverage Gates

Codex enforces a **minimum 90% code coverage** requirement in CI to maintain high code quality. The threshold is configurable but defaults to 90% to ensure comprehensive test coverage.

### Running Tests Locally

**Option 1: pytest (recommended)**
```bash
pytest --cov=src --cov=codex_ml --cov=codex_utils --cov-fail-under=90
```

**Option 2: pytest with detailed reporting**
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

**Option 3: Makefile**
```bash
make -C config test
```

**Option 4: nox**
```bash
nox --noxfile configs/development/noxfile.py -s tests
```

**Option 5: Offline gate**
```bash
nox --noxfile configs/development/noxfile.py -s offline_check
```

The offline gate shells out to `nox -s tests --verbose` and scans the logs for
network calls. Any occurrence of `http`, `download`, or `fetch` fails the
session.

**Option 6: Validate enforcement**
```bash
python scripts/validate_coverage_gates.py
```

### Hydra plugin guard

The `coverage` session now invokes a helper that checks for the
`hydra.extra` pytest plugin. If it is missing, the session installs
`hydra-core[hydra_plugins]>=1.3` automatically and logs an advisory message.

## Coverage Failures

If coverage falls below 90%:

1. Add or update tests that exercise the uncovered code paths.
2. Target comprehensive coverage for new submissions to maintain the 90% standard.
3. Inspect gaps with an HTML report: `pytest --cov-report=html`.
4. View the HTML report at `htmlcov/index.html` to identify uncovered lines.
5. Commit the new tests alongside the fixes that require them.

## Coverage Reporting

### Local Coverage Reports

Generate detailed coverage reports locally:

```bash
# HTML report (interactive, best for local review)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# XML report (for CI/tools)
pytest --cov=src --cov-report=xml

# JSON report (for parsing)
pytest --cov=src --cov-report=json
```

### CI Coverage Artifacts

Coverage reports are automatically generated and uploaded in CI:

1. **HTML Report** (`coverage-html-report`): Interactive web-based coverage report
2. **XML Report** (`coverage-xml-report`): Machine-readable format for tools
3. **JSON Report** (`coverage-json-report`): Structured data for parsing

Download these artifacts from the workflow run summary page.

## Future Coverage Targets

| Phase | Target | Status |
|-------|--------|--------|
| Phase 2–3 | 5–10% | ✅ Achieved |
| Phase 4+ | 20–30% | ✅ Achieved |
| Production standard (Current) | 90% | ✅ Enforced in CI |

The 90% coverage threshold ensures production-ready code quality and comprehensive test coverage across all critical paths.
