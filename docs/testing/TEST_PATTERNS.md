# Test Patterns Guide

**Status**: Active  
**Created**: 2026-01-18  
**Phase**: 14.0 - Test Coverage Foundation

---

## Overview

This document describes the standard test patterns used in the Codex repository. Following these patterns ensures consistency, maintainability, and effective test coverage.

## File Organization

### Directory Structure

```
tests/
├── conftest.py              # Global fixtures and configuration
├── conftest_shared.py       # Shared fixtures for all test types
├── templates/               # Test templates for new modules
│   ├── test_cli_template.py
│   ├── test_api_template.py
│   ├── test_data_template.py
│   └── test_ml_template.py
├── cli/                     # CLI tests
├── data/                    # Data module tests
├── training/                # Training pipeline tests
├── security/                # Security tests
├── safety/                  # Safety module tests
├── integration/             # Integration tests
└── unit/                    # Unit tests
```

### Naming Conventions

- Test files: `test_<module_name>.py`
- Test functions: `test_<function_name>_<scenario>()`
- Test classes: `Test<ClassName>`

## Test Categories

### Unit Tests

Unit tests focus on individual functions or methods in isolation.

```python
"""Example unit test pattern."""
import pytest

def test_function_returns_expected_value():
    """Test that function returns the expected value."""
    result = target_function(input_value)
    assert result == expected_value

def test_function_handles_edge_case():
    """Test edge case handling."""
    with pytest.raises(ValueError, match="expected error"):
        target_function(invalid_input)

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (2, 4),
    (0, 0),
])
def test_function_parametrized(input_val, expected):
    """Test multiple input/output combinations."""
    assert target_function(input_val) == expected
```

### Integration Tests

Integration tests verify cross-module interactions.

```python
"""Example integration test pattern."""
import pytest

@pytest.mark.integration
class TestPipelineIntegration:
    """Integration tests for the data pipeline."""

    def test_data_flows_through_pipeline(self, temp_index_dir):
        """Test end-to-end data flow."""
        # Setup
        loader = DataLoader(temp_index_dir)
        processor = DataProcessor()
        
        # Execute
        raw_data = loader.load()
        processed = processor.process(raw_data)
        
        # Verify
        assert processed.is_valid()
        assert len(processed.records) > 0
```

### CLI Tests

CLI tests verify command-line interface functionality.

```python
"""Example CLI test pattern."""
import subprocess
import sys

import pytest


def test_cli_help_displays_usage():
    """Test that --help displays usage information."""
    result = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout


def test_cli_command_executes_successfully(tmp_path):
    """Test CLI command execution."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("key: value")
    
    result = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli", "validate", str(config_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
```

### Data Tests

Data tests verify data loading and validation.

```python
"""Example data test pattern."""
import pytest


@pytest.fixture
def sample_dataset(tmp_path):
    """Create a sample dataset for testing."""
    data_file = tmp_path / "data.jsonl"
    data_file.write_text('{"id": 1, "text": "sample"}\n')
    return data_file


class TestDataLoader:
    """Tests for the data loader module."""

    def test_loads_jsonl_file(self, sample_dataset):
        """Test loading a JSONL file."""
        loader = DataLoader()
        records = loader.load(sample_dataset)
        assert len(records) == 1
        assert records[0]["id"] == 1

    def test_validates_schema(self, sample_dataset):
        """Test schema validation."""
        loader = DataLoader(schema={"id": int, "text": str})
        records = loader.load(sample_dataset)
        assert all(isinstance(r["id"], int) for r in records)
```

### Security Tests

Security tests verify security-critical functionality.

```python
"""Example security test pattern."""
import pytest


class TestInputSanitization:
    """Security tests for input sanitization."""

    @pytest.mark.security
    def test_blocks_sql_injection(self):
        """Test that SQL injection attempts are blocked."""
        malicious_input = "'; DROP TABLE users; --"
        result = sanitize_input(malicious_input)
        assert "DROP" not in result
        assert "'" not in result

    @pytest.mark.security
    def test_blocks_xss_attacks(self):
        """Test that XSS attacks are blocked."""
        malicious_input = "<script>alert('xss')</script>"
        result = sanitize_html(malicious_input)
        assert "<script>" not in result

    @pytest.mark.security
    def test_validates_path_traversal(self):
        """Test that path traversal is blocked."""
        malicious_path = "../../../etc/passwd"
        with pytest.raises(SecurityError):
            validate_path(malicious_path)
```

## Common Fixtures

### Temporary Directories

```python
@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
```

### Mock Services

```python
@pytest.fixture
def mock_api_client(mocker):
    """Mock external API client."""
    mock = mocker.patch("module.api_client.Client")
    mock.return_value.get.return_value = {"status": "ok"}
    return mock
```

### Deterministic RNG

```python
@pytest.fixture
def deterministic_seed():
    """Set deterministic random seed."""
    import random
    random.seed(42)
    yield
    # Cleanup if needed
```

## Markers

Use these markers to categorize tests:

```python
@pytest.mark.smoke        # Quick validation tests
@pytest.mark.integration  # Integration tests
@pytest.mark.security     # Security tests
@pytest.mark.slow         # Long-running tests
@pytest.mark.gpu          # GPU-specific tests
@pytest.mark.requires_torch  # Needs PyTorch
```

## Best Practices

### Do

- Write descriptive test names that explain the scenario
- Use fixtures for setup/teardown to maintain test isolation
- Mock external dependencies (APIs, databases, file systems)
- Test edge cases and error conditions explicitly
- Use parametrized tests for multiple inputs
- Keep assertions granular - one logical assertion per test when possible
- Use clear assertion messages for debugging
- Manage test data in fixtures, not inline
- Clean up resources in teardown (or use context managers)
- Document complex test scenarios with docstrings

### Test Isolation

- Each test should be independent and runnable alone
- Don't rely on side effects from other tests
- Use fresh fixtures for each test
- Reset global state if modified

### Assertion Granularity

```python
# Good: Granular assertions with messages
def test_user_creation():
    user = create_user(name="test", email="test@example.com")
    assert user is not None, "User should be created"
    assert user.name == "test", f"Expected name 'test', got '{user.name}'"
    assert user.email == "test@example.com"

# Avoid: Compound assertions that obscure failure cause
def test_user_creation_bad():
    user = create_user(name="test", email="test@example.com")
    assert user and user.name == "test" and user.email == "test@example.com"
```

### Test Data Management

```python
# Good: Test data in fixtures
@pytest.fixture
def sample_user_data():
    return {"name": "test", "email": "test@example.com"}

def test_create_user(sample_user_data):
    user = create_user(**sample_user_data)
    assert user.name == sample_user_data["name"]

# Avoid: Inline test data
def test_create_user_bad():
    user = create_user(name="test", email="test@example.com")  # Duplicated data
```

### Don't

- Test implementation details
- Use sleep() in tests (use polling or mocks)
- Share state between tests
- Rely on test execution order
- Hardcode file paths

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific category
pytest -m "security"

# Run in parallel
pytest -n auto

# Run verbose with output
pytest -v -s
```

---

**Last Updated**: 2026-01-18
