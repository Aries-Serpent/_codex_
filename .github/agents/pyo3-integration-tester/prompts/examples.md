# PyO3 Integration Tester - Usage Examples

## Example 1: Basic PyO3 Function

### Rust Code
```rust
#[pyfunction]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

### Generated Test
```python
def test_add_happy_path():
    from codex_swarm import add
    result = add(2, 3)
    assert result == 5

def test_add_type_validation():
    from codex_swarm import add
    # TODO: Test with invalid types
    pass
```

## Example 2: Function with Error Handling

### Rust Code
```rust
#[pyfunction]
pub fn parse_json(data: &str) -> PyResult<HashMap<String, String>> {
    serde_json::from_str(data)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}
```

### Generated Test
```python
def test_parse_json_happy_path():
    from codex_swarm import parse_json
    result = parse_json('{"key": "value"}')
    assert isinstance(result, dict)
    assert result["key"] == "value"

def test_parse_json_error_handling():
    from codex_swarm import parse_json
    with pytest.raises(Exception):
        parse_json("invalid json")
```

## Example 3: Async Function

### Rust Code
```rust
#[pyfunction]
pub async fn fetch_url(url: &str) -> PyResult<String> {
    reqwest::get(url).await?
        .text().await
        .map_err(|e| PyErr::new::<PyIOError, _>(e.to_string()))
}
```

### Generated Test
```python
@pytest.mark.asyncio
async def test_fetch_url_async():
    from codex_swarm import fetch_url
    result = await fetch_url("https://httpbin.org/get")
    assert isinstance(result, str)
    assert len(result) > 0
```

## Example 4: Complete Workflow

```bash
# 1. Scan Rust codebase
python -m pyo3_integration_tester \
  --rust-dir ./rust_swarm \
  --output ./python_tests/integration \
  --report

# Output:
# Scanning ./rust_swarm for PyO3 bindings...
# Found 15 PyO3 bindings
# Generated: ./python_tests/integration/test_compress_data_integration.py
# Generated: ./python_tests/integration/test_decompress_data_integration.py
# ...
# Generated 15 test files in ./python_tests/integration
#
# === Summary Report ===
# Total bindings: 15
# Files scanned: 5
# Async functions: 3
# With error handling: 12

# 2. Run generated tests
pytest ./python_tests/integration -v

# 3. Review and enhance tests
# Edit generated files to add realistic test data
```

## Example 5: CI Integration

### GitHub Actions Workflow
```yaml
name: PyO3 Integration Tests

on: [push, pull_request]

jobs:
  generate-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-asyncio pyyaml click
      
      - name: Generate integration tests
        run: |
          python .github/agents/pyo3-integration-tester/src/agent.py \
            --rust-dir ./rust_swarm \
            --output ./tests/integration \
            --overwrite
      
      - name: Run integration tests
        run: |
          pytest ./tests/integration -v --tb=short
```
