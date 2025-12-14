# Tests

This directory contains the test suite for the Codex ML project.

## Running Tests

### Basic Test Run

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

The coverage reports will be generated in:
- HTML: `htmlcov/index.html`
- XML: `coverage.xml`
- Terminal: displayed after test run

### Run Specific Test Markers

The project uses pytest markers to categorize tests. You can run specific categories:

```bash
# Run only smoke tests
pytest -m smoke

# Run only ML tests
pytest -m ml

# Run tests excluding slow tests
pytest -m "not slow"
```

See `pytest.ini` for the full list of available markers.

### Run Tests in Quiet Mode

```bash
pytest -q
```

### Run with Maximum Failures

```bash
pytest --maxfail=1
```

This will stop after the first failure, useful for quick feedback.

## Test Discovery

Tests are automatically discovered in the `tests/` directory. All test files should:
- Be named `test_*.py` or `*_test.py`
- Contain test functions named `test_*`
- Be placed in appropriate subdirectories based on the module being tested

## Test Structure

The test directory is organized to mirror the source structure:

```
tests/
├── README.md (this file)
├── codex/          # Tests for src/codex
├── codex_ml/       # Tests for codex_ml
├── codex_utils/    # Tests for codex_utils
├── hhg_logistics/  # Tests for HHG logistics
├── eval/           # Evaluation tests
└── ...
```

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Every push to `main`, `0D_base_`, or `0C_base_` branches
- Every pull request targeting these branches

The CI workflow:
1. Sets up Python 3.11+
2. Installs dependencies from `requirements.txt`
3. Runs pytest with coverage
4. Uploads coverage reports as artifacts
5. Fails if coverage is below the configured threshold (default: 90%)

## Coverage Requirements

The project aims for high test coverage. The CI workflow enforces a minimum coverage threshold:
- Default threshold: 90%
- Configurable via workflow environment variable `COVERAGE_THRESHOLD`

## Adding New Tests

1. Create a new test file in the appropriate subdirectory
2. Import the module/function you want to test
3. Write test functions using pytest conventions
4. Use appropriate markers to categorize your tests
5. Run tests locally before committing
6. Ensure coverage doesn't decrease

Example test file:

```python
import pytest
from src.codex.mymodule import my_function


@pytest.mark.smoke
def test_my_function_basic():
    """Test basic functionality of my_function."""
    result = my_function(input_data="test")
    assert result == expected_output


@pytest.mark.integration
def test_my_function_integration():
    """Test my_function in integration with other components."""
    # Integration test code here
    pass
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:
1. The package is installed: `pip install -e .`
2. You're running from the repository root
3. Required dependencies are installed: `pip install -r requirements.txt`

### Slow Tests

If tests are running slowly:
1. Use `pytest -m "not slow"` to skip slow tests
2. Run specific test files or functions: `pytest tests/test_specific.py::test_function`
3. Use `pytest -x` to stop at first failure

### Coverage Issues

If coverage is lower than expected:
1. Check which files are missing coverage: `pytest --cov=src --cov-report=term-missing`
2. Add tests for uncovered code paths
3. Review the HTML coverage report for details: `htmlcov/index.html`

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- Project-specific test guidelines: See `CONTRIBUTING.md`
