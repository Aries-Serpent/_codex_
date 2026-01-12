# Rust Error Validator - Advanced Patterns

## Pattern 1: Complex Error Propagation

### Scenario: Multiple fallible operations in PyO3 function

```rust
#[pyfunction]
fn complex_operation(input: &str, config: &str) -> PyResult<String> {
    // Parse input
    let data = parse_input(input)
        .map_err(|e| PyValueError::new_err(format!("Invalid input: {}", e)))?;
    
    // Load config
    let cfg = load_config(config)
        .map_err(|e| PyIOError::new_err(format!("Config error: {}", e)))?;
    
    // Process with config
    let result = process_with_config(&data, &cfg)
        .map_err(|e| PyRuntimeError::new_err(format!("Processing failed: {}", e)))?;
    
    Ok(result)
}
```

## Pattern 2: Custom Error Types

```rust
use pyo3::create_exception;

create_exception!(mymodule, ProcessingError, pyo3::exceptions::PyException);

#[pyfunction]
fn advanced_process(data: &str) -> PyResult<Output> {
    internal_process(data)
        .map_err(|e| ProcessingError::new_err(e.to_string()))
}
```

## Pattern 3: Option Handling

### Before
```rust
fn get_value(key: &str) -> String {
    lookup(key).unwrap()  // Panics if key missing
}
```

### After
```rust
fn get_value(key: &str) -> Option<String> {
    lookup(key)
}

// Or with default
fn get_value_or_default(key: &str) -> String {
    lookup(key).unwrap_or_else(|| "default".to_string())
}

// Or PyO3
#[pyfunction]
fn get_value(key: &str) -> PyResult<String> {
    lookup(key).ok_or_else(|| PyKeyError::new_err(format!("Key not found: {}", key)))
}
```

## Pattern 4: Early Return Pattern

```rust
#[pyfunction]
fn validate_and_process(input: &str) -> PyResult<String> {
    // Validate
    if input.is_empty() {
        return Err(PyValueError::new_err("Input cannot be empty"));
    }
    
    if !is_valid_format(input) {
        return Err(PyValueError::new_err("Invalid format"));
    }
    
    // Process
    let result = process(input)?;
    Ok(result)
}
```

## Pattern 5: Collecting Results

```rust
#[pyfunction]
fn process_multiple(items: Vec<&str>) -> PyResult<Vec<String>> {
    items.iter()
        .map(|item| process_item(item))
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}
```

## Pattern 6: Logging Before Returning Error

```rust
use log::error;

#[pyfunction]
fn critical_operation(data: &str) -> PyResult<Output> {
    match internal_op(data) {
        Ok(output) => Ok(output),
        Err(e) => {
            error!("Critical operation failed: {}", e);
            Err(PyRuntimeError::new_err(format!("Operation failed: {}", e)))
        }
    }
}
```

## Pattern 7: Contextual Error Messages

```rust
#[pyfunction]
fn load_and_process(path: &str, format: &str) -> PyResult<Output> {
    let data = load_file(path)
        .map_err(|e| PyIOError::new_err(
            format!("Failed to load file '{}': {}", path, e)
        ))?;
    
    let parsed = parse_data(&data, format)
        .map_err(|e| PyValueError::new_err(
            format!("Failed to parse as {}: {}", format, e)
        ))?;
    
    Ok(process(parsed))
}
```

## Pattern 8: Fallback Chain

```rust
fn get_config() -> Config {
    load_from_file("config.toml")
        .or_else(|_| load_from_env())
        .or_else(|_| load_defaults())
        .unwrap_or_else(|_| Config::minimal())
}
```

## CI Integration Example

### GitHub Actions Workflow
```yaml
name: Rust Error Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install validator
        run: |
          pip install click pyyaml
      
      - name: Run validation
        run: |
          python .github/agents/rust-error-validator/src/agent.py \
            --dir ./rust_src \
            --format json > findings.json
      
      - name: Check findings
        run: |
          HIGH_COUNT=$(jq '.severity_breakdown.high' findings.json)
          if [ "$HIGH_COUNT" -gt "0" ]; then
            echo "Found $HIGH_COUNT high severity issues"
            exit 1
          fi
      
      - name: Upload findings
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: rust-error-findings
          path: findings.json
```

## Pre-commit Hook Example

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running Rust error validation..."

python .github/agents/rust-error-validator/src/agent.py \
  --dir ./rust_src \
  --format text

if [ $? -ne 0 ]; then
  echo "❌ Rust error validation failed"
  echo "Fix errors or use 'git commit --no-verify' to skip"
  exit 1
fi

echo "✅ Rust error validation passed"
```
