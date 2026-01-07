# [Guide]: ML Component Test Suite
> Generated: 2024-11-19 03:54:01 UTC | Author: mbaetiong | Roles: [Test Engineering Lead] ⚡ Energy: 5

## Overview
Comprehensive test suite covering all ML training components with 85%+ coverage target.

## Test Structure

### Test Categories

| Category | Path | Tests | Coverage Target |
|----------|------|-------|-----------------|
| Training Engine | `tests/training/` | 18 | 85%+ |
| Dataset Loaders | `tests/data/` | 12 | 90%+ |
| Metrics | `tests/metrics/` | 10 | 95%+ |
| Callbacks | `tests/callbacks/` | 8 | 80%+ |
| Checkpointing | `tests/checkpointing/` | 15 | 90%+ |
| Integration | `tests/integration/` | 10 | 75%+ |

### Test Markers

```python
# Fast unit tests (default)
pytest.mark.unit

# Slow tests (>5 seconds)
pytest.mark.slow

# Integration tests
pytest.mark.integration

# ML comprehensive tests
pytest.mark.ml_comprehensive

# Requires GPU
pytest.mark.gpu

# Requires multiple GPUs
pytest.mark.multigpu
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Suite
```bash
# Training tests only
pytest tests/training/

# Without slow tests
pytest tests/ -m "not slow"

# Integration tests only
pytest tests/integration/ -m "integration"

# Skip ML comprehensive tests (for faster iteration)
pytest tests/ -m "not ml_comprehensive"
```

### With Coverage
```bash
pytest tests/ \
  --cov=src \
  --cov=training \
  --cov-report=html \
  --cov-report=term
```

### Parallel Execution
```bash
pytest tests/ -n auto  # Requires pytest-xdist
```

## Test Fixtures

### Common Fixtures

```python
@pytest.fixture
def mock_model():
    """Returns torch.nn.Module"""
    return torch.nn.Linear(10, 5)

@pytest.fixture
def mock_optimizer():
    """Returns torch.optim.Optimizer"""
    model = torch.nn.Linear(10, 5)
    return torch.optim.Adam(model.parameters())

@pytest.fixture
def temp_checkpoint_dir():
    """Returns temporary Path for checkpoints"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
```

## Coverage Requirements

### Per-Component Targets

| Component | Minimum | Target | Current |
|-----------|---------|--------|---------|
| Training Engine | 80% | 85% | TBD |
| Data Loaders | 85% | 90% | TBD |
| Metrics | 90% | 95% | TBD |
| Callbacks | 75% | 80% | TBD |
| Checkpointing | 85% | 90% | TBD |

### Enforcement

Coverage gates enforced in CI:
- PR merge requires 50%+ overall coverage (relaxed initially)
- No regressions >5% allowed
- Critical paths require 90%+

## Writing New Tests

### Test Template

```python
"""
Test module for [component]
"""
import pytest
from unittest.mock import Mock

pytestmark = pytest.mark.ml_comprehensive

class Test[Component]:
    """Test [component] functionality"""
    
    def test_[specific_behavior](self):
        """Test that [component] does [behavior]"""
        # Arrange
        input_data = ...
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_value
```

### Best Practices

1. **Descriptive Names**: `test_early_stopping_triggers_after_patience`
2. **One Assertion**: Test one behavior per test
3. **Mock External**: Mock file I/O, network, GPU
4. **Fast by Default**: Keep unit tests <100ms
5. **Deterministic**: Use fixed seeds for randomness

## Debugging Failed Tests

### Verbose Output
```bash
pytest tests/training/test_engine_hf_trainer_comprehensive.py::test_specific -v --tb=long
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Last Failed
```bash
pytest tests/ --lf
```

### Print Output
```bash
pytest tests/ -s
```

## CI Integration

### GitHub Actions

Tests run automatically on:
- Push to main/develop
- Pull requests
- Nightly schedule

### Test Matrix

- Python: 3.9, 3.10, 3.11
- OS: Ubuntu (Linux)
- Components: Training, Data, Metrics, Callbacks, Checkpointing

### Artifacts

- Coverage reports uploaded to Codecov
- HTML coverage archived
- Test timing reports

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| ImportError | Install test dependencies: `pip install pytest pytest-cov` |
| Timeout | Increase timeout: `pytest --timeout=600` |
| GPU tests fail | Skip with `-m "not gpu"` |
| Flaky tests | Check for race conditions, use fixed seeds |

### Getting Help

1. Check test documentation: `pytest --help`
2. Review test logs in CI artifacts
3. File issue with `testing` label

---

**End of ML Test Suite Guide**
