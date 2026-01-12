# PyO3 Integration Tester Agent

**Version**: 1.0.0  
**Status**: Production  
**Maturity**: Tier 1  
**Test Coverage**: 100% (11/11 tests passing)

## Purpose

Validates Python-Rust bindings created with PyO3 by automatically discovering bindings and generating comprehensive Python integration tests.

## Features

- **Automatic Discovery**: Scans Rust files for `#[pyfunction]` and `#[pymethods]` bindings
- **Comprehensive Testing**: Generates happy path, type validation, error handling, and performance tests
- **Async Support**: Detects and generates tests for async functions
- **Error Handling**: Identifies PyResult returns and generates exception tests
- **Report Generation**: Provides statistics on discovered bindings
- **Cognitive Brain Integration**: Tracks metrics and learns patterns

## Quick Start

### Command Line

```bash
# Scan Rust directory and generate tests
python -m pyo3_integration_tester --rust-dir ./rust_src --output ./tests

# With summary report
python -m pyo3_integration_tester --rust-dir ./rust_src --output ./tests --report

# Overwrite existing tests
python -m pyo3_integration_tester --rust-dir ./rust_src --output ./tests --overwrite
```

### Programmatic Usage

```python
from pathlib import Path
from pyo3_integration_tester import PyO3IntegrationTester

tester = PyO3IntegrationTester()
bindings = tester.scan_directory(Path("./rust_src"))
generated = tester.generate_tests(bindings, Path("./tests"))

print(f"Generated {len(generated)} test files")
```

## Installation

```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.11+
- click
- pyyaml
- pytest (for running generated tests)
- pytest-asyncio (for async tests)

## Generated Test Structure

For each discovered binding, generates:

1. **Happy Path Test**: Basic functionality with valid inputs
2. **Type Validation Test**: Placeholder for type checking
3. **Error Handling Test**: Exception testing (for PyResult returns)
4. **Async Test**: Async/await testing (for async functions)
5. **Performance Test**: Smoke test to catch regressions

## Example

### Rust Code
```rust
#[pyfunction]
pub fn compress_data(data: &[u8]) -> PyResult<Vec<u8>> {
    // Implementation
}
```

### Generated Test
```python
import pytest

def test_compress_data_happy_path():
    from codex_swarm import compress_data
    result = compress_data(b"test data")
    assert isinstance(result, bytes)

def test_compress_data_error_handling():
    from codex_swarm import compress_data
    with pytest.raises(Exception):
        compress_data(None)

@pytest.mark.performance
def test_compress_data_performance():
    import time
    from codex_swarm import compress_data
    
    start = time.time()
    result = compress_data(b"data" * 1000)
    duration = time.time() - start
    
    assert duration < 1.0
```

## Configuration

See `config/agent_config.yaml` for options:

- Module name customization
- Test type toggles (happy_path, type_validation, error_handling, performance, async)
- Performance thresholds
- Scanning options (recursive, file patterns)
- Cognitive brain integration

## Testing

Run the agent test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Test Coverage**: 100% (11/11 tests passing)
- Binding discovery
- Test generation
- Async detection
- Error handling coverage
- Report generation

## Integration

### GitHub Actions

```yaml
- name: Generate PyO3 Integration Tests
  run: |
    python .github/agents/pyo3-integration-tester/src/agent.py \
      --rust-dir ./rust_src \
      --output ./tests/integration \
      --report
    
    pytest ./tests/integration -v
```

### Pre-commit Hook

```bash
#!/bin/bash
python .github/agents/pyo3-integration-tester/src/agent.py \
  --rust-dir ./rust_src \
  --output ./tests/integration
```

## Documentation

- **Main Prompt**: `prompts/main.md` - Detection rules and workflow
- **Examples**: `prompts/examples.md` - Common patterns and CI integration

## Cognitive Brain Integration

Tracks:
- Total bindings found per scan
- Tests generated
- Async functions detected
- Error handling coverage
- Scan duration

Alerts when:
- Bindings without tests > 5
- Error handling coverage < 50%

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

Follow standard agent structure:
- `src/` - Agent implementation
- `tests/` - Comprehensive test suite (≥90% coverage)
- `config/` - Configuration files
- `prompts/` - Usage documentation
- `CHANGELOG.md` - Version history

## License

Part of the _codex_ repository.

## Maintainers

- GitHub Copilot Agent
- @mbaetiong
