# Test Taxonomy

## Test Organization

Tests are organized by type and purpose, with clear markers for categorization and filtering.

### Directory Structure

```text
tests/
├── config/          # Configuration and schema tests
├── unit/            # Unit tests (isolated, fast)
├── integration/     # Integration tests
├── training/        # Training-related tests
├── eval/            # Evaluation tests
├── cli/             # CLI tests
└── ...
```

### Test Markers

All markers are registered in `pytest.ini`. Use these consistently:

#### Core Markers

- **`smoke`**: Quick smoke tests for basic functionality
  - Runtime: < 1 second each
  - Run frequently during development
  - Usage: `@pytest.mark.smoke`

- **`slow`**: Long-running or resource-intensive tests
  - Runtime: > 10 seconds
  - Skip during quick checks
  - Usage: `@pytest.mark.slow`

#### Environment Markers

- **`requires_torch`**: Tests requiring PyTorch installation
  - Automatically skipped if torch unavailable
  - Usage: `@pytest.mark.requires_torch`

- **`cpu_only`**: Tests that should only run on CPU
  - Prevents GPU resource usage
  - Usage: `@pytest.mark.cpu_only`

- **`distributed`**: Distributed/accelerate tests
  - Opt-in via `ACCELERATE_TEST=1`
  - Usage: `@pytest.mark.distributed`

#### Feature Markers

- **`lora`**: LoRA-specific tests
  - Opt-in via `RUN_LORA_TESTS=1`
  - Usage: `@pytest.mark.lora`

- **`perf_smoke`**: Performance smoke tests
  - Opt-in via `RUN_PERF_SMOKE=1`
  - Usage: `@pytest.mark.perf_smoke`

### Running Tests by Category

```bash
# Smoke tests only (fast)
pytest -m smoke

# All tests except slow
pytest -m "not slow"

# Only torch-dependent tests
pytest -m requires_torch

# CPU tests only
pytest -m cpu_only

# Combine markers
pytest -m "smoke and not requires_torch"
```

### Test Naming Conventions

#### Test Files

- `test_*.py` for test modules
- Descriptive names: `test_config_schema.py`, not `test_stuff.py`
- Group related tests in same file

#### Test Functions

```python
def test_<feature>_<scenario>_<expected_result>():
    """Clear docstring explaining what is tested."""
    pass

# Examples:
def test_config_loads_valid_yaml():
    """Test that valid YAML config loads successfully."""
    pass

def test_model_raises_error_on_invalid_device():
    """Test that model initialization fails with invalid device."""
    pass
```

### Test Structure (AAA Pattern)

```python
def test_example():
    """Test description."""
    # Arrange: Set up test data and conditions
    config = {"epochs": 5}
    
    # Act: Perform the action being tested
    result = process_config(config)
    
    # Assert: Verify the expected outcome
    assert result.epochs == 5
```

### Best Practices

1. **Keep tests focused**: One concept per test
2. **Make tests independent**: No test should depend on another
3. **Use descriptive names**: Test name should explain what it tests
4. **Add docstrings**: Explain the test's purpose
5. **Keep tests fast**: Use mocks/stubs for external dependencies
6. **Use appropriate markers**: Help others filter tests
7. **Clean up resources**: Use fixtures with teardown when needed
8. **Test edge cases**: Not just happy paths

### Debugging Tests

```bash
# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l

# Enter debugger on failure
pytest --pdb

# Verbose output
pytest -v

# Show print statements
pytest -s
```
