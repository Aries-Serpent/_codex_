# CI Pytest Implementation Guide

## Overview

This document describes the pytest CI implementation added to the `_codex_` repository to enable reliable pytest and pytest-cov execution in GitHub Actions.

## Implementation Summary

### 1. GitHub Actions Workflow

**File**: `.github/workflows/ci-pytest.yml`

**Features:**
- Triggers on push/PR to main, 0D_base_, 0C_base_ branches
- Runs on ubuntu-latest with Python 3.11
- Executes pytest with coverage collection
- Enforces 90% coverage threshold (configurable via `COVERAGE_THRESHOLD` env var)
- Uploads coverage artifacts (HTML, XML, JSON) with 30-day retention
- Posts automatic PR comment with coverage summary and artifact links
- Fails fast on test failures or coverage below threshold

**Key Jobs:**
- `pytest-coverage`: Main job that runs tests, collects coverage, validates threshold, and uploads artifacts

### 2. Requirements Update

**File**: `requirements.txt`

**Changes:**
- Pinned `pytest>=8.0.0,<9.0.0` (previously unpinned)
- Pinned `pytest-cov>=4.1.0,<5.0.0` (previously unpinned)

**Rationale:**
- Ensures consistent test behavior across environments
- Prevents breaking changes from major version updates
- Maintains compatibility with existing test suite

### 3. Test Discovery Documentation

**File**: `tests/README.md` (newly created)

**Contents:**
- Running tests (basic, with coverage, specific markers)
- Test discovery and structure
- CI/CD integration details
- Coverage requirements (90% threshold)
- Adding new tests
- Troubleshooting guide

**Key Sections:**
- Quick start commands for pytest
- Coverage report generation and viewing
- Test marker usage examples
- CI workflow description
- Manual workflow execution instructions

### 4. Documentation Updates

All major documentation files updated to explicitly reference pytest as the primary test runner:

#### a. `AGENTS.md`
- Rewrote "Tooling, Testing & Checks" section
- Added detailed pytest instructions with markers
- Documented CI/CD testing workflow
- Maintained nox as alternative option

#### b. `CONTRIBUTING.md`
- Added "Testing Requirements" section at the top
- Detailed pytest commands for local testing
- Documented CI/CD testing expectations
- Updated coverage requirements (90% threshold)
- Added before-submitting checklist

#### c. `README.md`
- Added new "Testing" section with quick reference
- Documented pytest commands and markers
- Added CI/CD testing summary
- Updated "Local DoD" with pytest coverage command

#### d. `docs/guides/TESTING_GUIDE.md`
- Complete rewrite emphasizing pytest as primary runner
- Added CI/CD Integration section
- Updated coverage gates from 3.5% to 90%
- Added coverage reporting section
- Documented CI artifact downloads

#### e. `docs/dev/testing.md`
- Rewrote to position pytest as primary test runner
- Added CI/CD integration section
- Maintained nox documentation as alternative
- Added coverage enforcement details

#### f. `docs/quickstart.md`
- Updated testing section to use pytest first
- Added CI/CD testing information
- Maintained nox as alternative

#### g. `NEWCOMER_GUIDE.md`
- Expanded "Testing and Quality" section
- Added pytest quick start commands
- Documented CI/CD testing
- Updated quality gates checklist

## Running Tests

### Locally

**Basic test run:**
```bash
pytest
```

**With coverage:**
```bash
pytest --cov=src --cov=codex_ml --cov=codex_utils --cov-report=html --cov-report=xml --cov-report=term
```

**View HTML coverage report:**
```bash
open htmlcov/index.html
```

**Run specific test categories:**
```bash
pytest -m smoke                  # Quick smoke tests
pytest -m "not slow"             # Skip slow tests
pytest -m integration            # Integration tests
pytest -m ml                     # ML/tensor dependent tests
```

**Coverage threshold check:**
```bash
pytest --cov=src --cov-fail-under=90
```

### In CI/CD

**Automatic triggers:**
- Every push to main, 0D_base_, 0C_base_
- Every pull request targeting these branches

**Manual trigger:**
1. Go to Actions tab
2. Select "CI - Pytest with Coverage" workflow
3. Click "Run workflow"
4. Select branch and run

**Viewing results:**
- Check workflow status in PR or commit
- Review automated PR comment for summary
- Download coverage artifacts from workflow run page:
  - `coverage-html-report` - Interactive HTML report
  - `coverage-xml-report` - XML format for tools
  - `coverage-json-report` - JSON format for parsing

## Coverage Requirements

### Threshold
- **Default**: 90% minimum
- **Configurable**: Set `COVERAGE_THRESHOLD` environment variable in workflow
- **Enforcement**: Build fails if coverage is below threshold

### Reports Generated
1. **HTML**: Interactive web-based report (`htmlcov/index.html`)
2. **XML**: Machine-readable format (`coverage.xml`)
3. **JSON**: Structured data format (`coverage.json`)
4. **Terminal**: Summary printed to console

## Workflow Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COVERAGE_THRESHOLD` | 90 | Minimum coverage percentage required |
| `PYTHON_VERSION` | 3.11 | Python version to use for testing |

### Customization

To change the coverage threshold:

1. Edit `.github/workflows/ci-pytest.yml`
2. Modify the `COVERAGE_THRESHOLD` environment variable
3. Commit and push changes

Example:
```yaml
env:
  COVERAGE_THRESHOLD: 85  # Changed from 90 to 85
```

## Re-running Workflow from Web UI

### From Pull Request
1. Navigate to the PR
2. Scroll to the checks section
3. Click "Details" next to "CI - Pytest with Coverage"
4. Click "Re-run jobs" button

### From Actions Tab
1. Go to repository Actions tab
2. Select "CI - Pytest with Coverage" workflow
3. Choose a previous run or click "Run workflow"
4. Select branch and trigger

## Troubleshooting

### Tests Fail Locally but Pass in CI
- Ensure you're using Python 3.11+
- Install all dependencies: `pip install -r requirements.txt`
- Install package in editable mode: `pip install -e .`

### Coverage Below Threshold
- Run with `--cov-report=term-missing` to see uncovered lines
- Add tests for uncovered code paths
- Review HTML report for detailed coverage: `htmlcov/index.html`

### Import Errors
- Ensure package is installed: `pip install -e .`
- Check virtual environment is activated
- Verify PYTHONPATH includes repository root

### Workflow Artifacts Not Found
- Wait for workflow to complete (check status)
- Artifacts are available for 30 days after workflow run
- Download from workflow run summary page

## Integration with Existing CI

This pytest workflow complements existing CI workflows:

- **`.github/workflows/ci.yml`**: Segmented nox sessions (still active)
- **`.github/workflows/tests.yml`**: Fast unit tests (still active)
- **`.github/workflows/ci-pytest.yml`**: New comprehensive pytest with coverage

All workflows can run in parallel without conflicts.

## Next Steps

### Immediate
1. Monitor first workflow runs for any issues
2. Review coverage reports to identify gaps
3. Add tests to increase coverage if below 90%

### Future Enhancements
1. Add coverage trend tracking
2. Implement coverage badges in README
3. Add code coverage comments with line-by-line annotations
4. Set up coverage regression prevention

## Manual Verification Steps

Before merging this implementation:

1. **Verify workflow syntax**: `yamllint .github/workflows/ci-pytest.yml`
2. **Check workflow in Actions tab**: Ensure it appears in workflow list
3. **Trigger manual run**: Test workflow execution end-to-end
4. **Review artifacts**: Confirm all coverage reports are uploaded
5. **Check PR comment**: Verify automated comment posts correctly

## Files Modified

### New Files
- `.github/workflows/ci-pytest.yml` - Main CI workflow
- `tests/README.md` - Comprehensive testing documentation
- `CI_PYTEST_IMPLEMENTATION.md` - This implementation guide

### Modified Files
- `requirements.txt` - Pinned pytest and pytest-cov versions
- `AGENTS.md` - Updated testing documentation
- `CONTRIBUTING.md` - Added testing requirements
- `README.md` - Added testing section
- `docs/guides/TESTING_GUIDE.md` - Complete pytest guide
- `docs/dev/testing.md` - Updated primary test runner documentation
- `docs/quickstart.md` - Updated testing instructions
- `NEWCOMER_GUIDE.md` - Enhanced testing section

### Unchanged Files
- `pytest.ini` - Already properly configured
- `.coveragerc` - Existing coverage configuration still used
- `pyproject.toml` - Dev dependencies already include pytest/pytest-cov

## Conclusion

This implementation provides:

✅ Reliable pytest execution in GitHub Actions  
✅ Comprehensive coverage collection and reporting  
✅ Configurable coverage threshold enforcement  
✅ Automated PR feedback with coverage summary  
✅ Multiple coverage report formats  
✅ Clear documentation for all stakeholders  
✅ Backward compatibility with existing CI workflows

The repository is now fully equipped to run pytest and pytest-cov reliably in GitHub Actions with comprehensive documentation and user-friendly automation.
