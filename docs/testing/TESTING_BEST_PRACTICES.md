# Testing Best Practices Guide

**Last Updated:** 2026-06-22

## Overview

This guide documents best practices for writing tests in the _codex_ repository, with special focus on handling optional dependencies, mocking strategies, and test organization.

## Table of Contents

1. [Test Organization](#test-organization)
2. [Handling Optional Dependencies](#handling-optional-dependencies)
3. [Mocking Strategies](#mocking-strategies)
4. [Stub Module Detection](#stub-module-detection)
5. [Test Markers](#test-markers)
6. [Common Patterns](#common-patterns)

## Test Organization

### Directory Structure

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Integration tests (may use real dependencies)
├── slow/           # Long-running tests (>30s)
├── utils/          # Shared test utilities and helpers
│   ├── torch_helpers.py      # PyTorch/ML dependency helpers
│   ├── quantum_helpers.py    # Quantum plugin mocking utilities
│   └── doc_refactor_helpers.py  # Documentation validation helpers
└── conftest.py     # Pytest configuration and fixtures
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestQuantumPlugin`)
- Test methods: `test_*` (e.g., `test_plugin_loading`)

## Handling Optional Dependencies

### Problem

Many tests require optional dependencies (PyTorch, Transformers, MLflow, etc.) that may not be installed in all environments. Tests should gracefully skip when dependencies are unavailable.

### Solution: Use Skip Helpers

#### Basic Module Check

```python
from tests.utils.torch_helpers import skip_if_missing, require_module

def test_training_with_torch():
    """Test training pipeline with PyTorch."""
    torch = require_module("torch", "PyTorch")
    # Test code using torch...
```

#### Multiple Dependencies

```python
from tests.utils.torch_helpers import skip_if_any_missing

def test_ml_pipeline():
    """Test full ML pipeline."""
    skip_if_any_missing("torch", "transformers", "mlflow")
    # Test code using all three modules...
```

#### PyTorch with Stub Detection

```python
from tests.utils.torch_helpers import require_torch

def test_model_training():
    """Test model training."""
    torch = require_torch()  # Skips if PyTorch is stub or missing
    model = torch.nn.Linear(10, 5)
    # Test code...
```

## Mocking Strategies

### Quantum Plugin Mocking

When testing quantum plugin behavior without requiring actual module implementations:

```python
from tests.utils.quantum_helpers import quantum_plugin_fixture

def test_plugin_loading(quantum_plugin_fixture):
    """Test plugin loading with mocked modules."""
    # Mock the modules that may not exist
    quantum_plugin_fixture.mock_module("src.rag.pipelines.chunking")
    quantum_plugin_fixture.mock_module("src.rag.pipelines.embedding")

    # Test code using mocked modules...
    # Cleanup happens automatically via fixture
```

### Creating Mock Modules

```python
from tests.utils.quantum_helpers import create_mock_module, install_mock_module

def test_custom_mock():
    """Test with custom mock attributes."""
    mock_module = create_mock_module(
        "src.custom.module",
        process=lambda x: x.upper(),
        CONSTANT=42
    )
    install_mock_module(mock_module)

    from src.custom import module
    assert module.process("hello") == "HELLO"
    assert module.CONSTANT == 42
```

## Stub Module Detection

### Problem

The repository includes stub modules (e.g., `torch/`) that provide minimal imports but don't have full functionality. Tests that import stubs instead of real modules may pass locally but fail with `MagicMock` errors in CI.

### Solution: Stub Detection Pattern

The `torch_helpers.py` module provides utilities to detect and skip tests when stubs are detected:

```python
from tests.utils.torch_helpers import require_torch

def test_with_real_torch():
    """This test requires real PyTorch, not a stub."""
    torch = require_torch()

    # Detection checks:
    # 1. hasattr(torch, 'nn')
    # 2. hasattr(torch.nn, 'Linear')
    # 3. hasattr(torch, 'IS_CODEX_STUB')

    model = torch.nn.Linear(10, 5)  # Works with real torch
```

### Adding Stub Markers

If you create a stub module, add a marker so tests can detect it:

```python
# stub_module/__init__.py
IS_CODEX_STUB = True  # Mark as stub module
```

## Test Markers

### Available Markers

- `@pytest.mark.unit` - Fast unit tests (default)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Long-running tests (>30s)
- `@pytest.mark.requires_gpu` - Requires GPU hardware
- `@pytest.mark.requires_docker` - Requires Docker
- `@pytest.mark.smoke` - Smoke tests (critical functionality)

### Running Specific Test Groups

```bash
# Run only unit tests
pytest -m "unit"

# Run integration tests, excluding slow ones
pytest -m "integration and not slow"

# Run all tests except slow
pytest -m "not slow"
```

### Auto-Marking

The `conftest.py` automatically marks tests as `slow` if they:
- Have `@pytest.mark.slow` explicitly
- Contain "slow" in the test name
- Take longer than 30 seconds to run

**Note**: Integration tests are NOT auto-marked as slow. Mark them explicitly if needed.

## Common Patterns

### Pattern 1: Optional Dependency Test

```python
from tests.utils.torch_helpers import require_module

def test_with_optional_dep():
    """Test that requires optional dependency."""
    transformers = require_module("transformers", "HuggingFace Transformers")

    model = transformers.AutoModel.from_pretrained("bert-base-uncased")
    # Test code...
```

### Pattern 2: Multiple Optional Dependencies

```python
from tests.utils.torch_helpers import skip_if_any_missing

def test_ml_pipeline():
    """Test full ML pipeline."""
    skip_if_any_missing("torch", "transformers", "mlflow")

    import torch
    import transformers
    import mlflow
    # Test code using all three...
```

### Pattern 3: Quantum Plugin with Mocks

```python
from src.quantum import QuantumPlugin, QuantumPluginRegistry, PluginState
from tests.utils.quantum_helpers import quantum_plugin_fixture

def test_plugin_dependencies(quantum_plugin_fixture):
    """Test plugin with dependency chain."""
    # Mock modules
    quantum_plugin_fixture.mock_module("src.rag.pipelines.chunking")
    quantum_plugin_fixture.mock_module("src.rag.pipelines.embedding")

    registry = QuantumPluginRegistry()
    registry.register(QuantumPlugin(
        name="chunking",
        import_path="src.rag.pipelines.chunking"
    ))
    registry.register(QuantumPlugin(
        name="embedding",
        import_path="src.rag.pipelines.embedding",
        dependencies=["chunking"]
    ))

    # Load with dependencies
    module = registry.load_with_dependencies("embedding")
    assert module is not None
    assert registry.plugins["chunking"].state == PluginState.COLLAPSED
```

### Pattern 4: Parameterized Tests with Optional Deps

```python
import pytest
from tests.utils.torch_helpers import require_module

@pytest.mark.parametrize("model_name", [
    "bert-base-uncased",
    "gpt2",
    "t5-small"
])
def test_models(model_name):
    """Test various transformer models."""
    transformers = require_module("transformers")

    model = transformers.AutoModel.from_pretrained(model_name)
    assert model is not None
```

### Pattern 5: Conditional Skip at Module Level

```python
import pytest
from tests.utils.torch_helpers import skip_if_missing

# Skip entire module if dependency missing
skip_if_missing("mlflow", "MLflow")

# All tests in this module require MLflow
def test_mlflow_tracking():
    import mlflow
    # Test code...

def test_mlflow_logging():
    import mlflow
    # Test code...
```

## Best Practices Summary

1. **Always handle optional dependencies gracefully** - Use `require_module()` or `skip_if_missing()`
2. **Detect stub modules** - Use `require_torch()` for PyTorch tests to avoid stub imports
3. **Use appropriate markers** - Mark slow and integration tests correctly
4. **Mock when appropriate** - Use `quantum_plugin_fixture` for plugin tests
5. **Keep tests fast** - Unit tests should complete in <1s, integration <10s
6. **Clean up resources** - Use fixtures for automatic cleanup
7. **Document test purpose** - Write clear docstrings explaining what is being tested
8. **Avoid test interdependencies** - Each test should be independent
9. **Use parametrize** - Test multiple scenarios with `@pytest.mark.parametrize`
10. **Handle CI differences** - Account for modules that may not be available in CI

## Troubleshooting

### Test Imports Stub Instead of Real Module

**Problem**: Test passes locally but fails in CI with MagicMock errors.

**Solution**: Use `require_torch()` or similar helpers that detect stubs.

### Test Hangs or Times Out

**Problem**: Test runs indefinitely or exceeds timeout.

**Solution**:
- Mark test with `@pytest.mark.slow`
- Reduce test complexity
- Check for infinite loops or deadlocks

### Import Errors in CI

**Problem**: Tests fail with `ModuleNotFoundError` in CI.

**Solution**:
- Use `require_module()` to skip when module unavailable
- Ensure module is listed in `requirements-test.txt`
- Check if module is optional and should be skipped

### Pytest Collection Warnings

**Problem**: `cannot collect test class 'TestState' because it has a __init__ constructor`

**Solution**: Rename class to not start with `Test` or remove `__init__` method.

---

**Last Updated**: 2026-02-14
**Maintained By**: Codex Team
**Related Files**:
- `tests/utils/torch_helpers.py`
- `tests/utils/quantum_helpers.py`
- `tests/conftest.py`
- `.codex/cognitive_brain/PR3248_RESOLUTION_COGNITIVE_UPDATE.md`
