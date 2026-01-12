# Rust Error Validator - Usage Examples

## Example 1: PyO3 Function with Unwrap

### Before (Problematic)
```rust
#[pyfunction]
fn read_file(path: &str) -> String {
    let contents = std::fs::read_to_string(path).unwrap();
    contents
}
```

**Finding**: High severity - unwrap() in PyO3 function can crash Python interpreter

### After (Fixed)
```rust
use pyo3::exceptions::PyIOError;

#[pyfunction]
fn read_file(path: &str) -> PyResult<String> {
    std::fs::read_to_string(path)
        .map_err(|e| PyIOError::new_err(format!("Failed to read {}: {}", path, e)))
}
```

## Example 2: Parsing with Expect

### Before (Problematic)
```rust
fn parse_config(json: &str) -> Config {
    serde_json::from_str(json).expect("Invalid JSON")
}
```

**Finding**: Medium severity - expect() can panic on invalid input

### After (Fixed)
```rust
fn parse_config(json: &str) -> Result<Config, serde_json::Error> {
    serde_json::from_str(json)
}
```

## Example 3: Explicit Panic

### Before (Problematic)
```rust
fn handle_request(req: Request) -> Response {
    if !req.is_valid() {
        panic!("Invalid request received");
    }
    process(req)
}
```

**Finding**: High severity - explicit panic in request handler

### After (Fixed)
```rust
fn handle_request(req: Request) -> Result<Response, String> {
    if !req.is_valid() {
        return Err("Invalid request received".to_string());
    }
    Ok(process(req))
}
```

## Example 4: Acceptable Test Unwrap

```rust
#[test]
fn test_read_file() {
    // ✅ This is fine - test code can use unwrap
    let contents = read_file("test.txt").unwrap();
    assert_eq!(contents, "expected content");
}
```

**Finding**: None - unwrap in test code is ignored

## Example 5: Batch Processing with Error Collection

### Before (Stops on First Error)
```rust
fn process_batch(items: Vec<Item>) -> Vec<Result> {
    items.iter()
        .map(|item| process_item(item).unwrap())  // Fails on first error
        .collect()
}
```

### After (Collects All Results)
```rust
fn process_batch(items: Vec<Item>) -> Vec<Result<Output, Error>> {
    items.iter()
        .map(|item| process_item(item))
        .collect()
}
```

## Example 6: Using unwrap_or_else for Graceful Defaults

### Before
```rust
fn get_config() -> Config {
    load_config().unwrap()  // Panics if config missing
}
```

### After
```rust
fn get_config() -> Config {
    load_config().unwrap_or_else(|_| Config::default())
}
```

## Example 7: Scanning Output Format

### Text Output
```
/path/to/file.rs:42 [HIGH] unwrap() can panic - found in: let x = result.unwrap();
  → Suggestion: Use PyResult for PyO3 functions or unwrap_or_else() for graceful handling

Total: 3 findings
  High: 1
  Medium: 2
  Low: 0
Files affected: 2
```

### JSON Output
```json
{
  "total_findings": 3,
  "severity_breakdown": {
    "high": 1,
    "medium": 2,
    "low": 0
  },
  "findings_by_severity": {
    "high": [
      {
        "file": "/path/to/file.rs",
        "line": 42,
        "severity": "high",
        "issue": "unwrap() can panic",
        "suggestion": "Use PyResult..."
      }
    ]
  },
  "unique_files": 2
}
```
