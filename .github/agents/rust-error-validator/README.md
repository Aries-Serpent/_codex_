# Rust Error Validator Agent

**Version**: 1.0.0  
**Status**: Production  
**Maturity**: Tier 1  
**Test Coverage**: 100% (24/24 tests passing)

## Purpose

Validates Rust error handling patterns to prevent runtime panics, with special focus on PyO3 (Rust-Python) bindings where panics can crash the Python interpreter.

## Features

- **Unwrap Detection**: Identifies `.unwrap()` calls that can panic
- **Expect Detection**: Finds `.expect()` calls with panic risks
- **Panic Detection**: Locates explicit `panic!()` macro usage
- **Context-Aware Severity**: Assigns severity based on code context (PyO3, tests, internal)
- **Actionable Suggestions**: Provides specific fix recommendations for each finding
- **Report Generation**: Comprehensive reports with severity breakdown
- **Cognitive Brain Integration**: Tracks metrics, learns patterns, alerts on thresholds

## Quick Start

### Command Line

```bash
# Scan a directory
python -m rust_error_validator --dir ./rust_src --verbose

# Scan with custom config
python -m rust_error_validator --dir ./rust_src --config config/agent_config.yaml

# Output as JSON
python -m rust_error_validator --dir ./rust_src --format json > findings.json
```

### Programmatic Usage

```python
from pathlib import Path
from rust_error_validator import RustErrorValidator

validator = RustErrorValidator()
findings = validator.scan_directory(Path("./rust_src"))
report = validator.generate_report(findings)

print(f"Total findings: {report['total_findings']}")
print(f"High severity: {report['severity_breakdown']['high']}")
```

## Installation

```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.11+
- click
- pyyaml

## Detection Rules

### High Severity
- `.unwrap()` or `.expect()` in `#[pyfunction]` decorated functions
- `.unwrap()` or `.expect()` in `#[pymethods]` blocks
- `panic!()` macro in any non-test code

### Medium Severity
- `.unwrap()` in private/internal functions
- `.expect()` with insufficient error context

### Ignored
- `.unwrap()` in `#[test]` or `#[cfg(test)]` code (configurable)

## Example Output

### Text Format
```
/path/to/file.rs:42 [HIGH] unwrap() can panic - found in: let x = result.unwrap();
  → Suggestion: Use PyResult for PyO3 functions or unwrap_or_else() for graceful handling

Total: 3 findings
  High: 1
  Medium: 2
  Low: 0
Files affected: 2
```

### JSON Format
```json
{
  "total_findings": 3,
  "severity_breakdown": {
    "high": 1,
    "medium": 2,
    "low": 0
  },
  "unique_files": 2
}
```

## Configuration

See `config/agent_config.yaml` for full configuration options:

- Detection toggles (unwrap, expect, panic)
- Severity level customization
- Test code filtering
- Output formatting
- Cognitive brain integration
- Performance tuning

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test class
pytest tests/test_agent.py::TestRustErrorValidator -v
```

**Test Coverage**: 100% (24/24 tests passing)
- 14 unit tests (core functionality)
- 8 integration tests (workflows)
- 2 legacy tests (backward compatibility)

## Integration

### GitHub Actions

```yaml
- name: Validate Rust Error Handling
  run: |
    python .github/agents/rust-error-validator/src/agent.py \
      --dir ./rust_src \
      --format json > findings.json
    
    HIGH_COUNT=$(jq '.severity_breakdown.high' findings.json)
    if [ "$HIGH_COUNT" -gt "0" ]; then
      echo "Found $HIGH_COUNT high severity issues"
      exit 1
    fi
```

### Pre-commit Hook

```bash
#!/bin/bash
python .github/agents/rust-error-validator/src/agent.py \
  --dir ./rust_src --format text
```

## Documentation

- **Main Prompt**: `prompts/main.md` - Detection rules and workflow
- **Examples**: `prompts/examples.md` - Common patterns and fixes
- **Advanced**: `prompts/advanced.md` - Complex scenarios and CI integration

## Cognitive Brain Integration

Tracks the following metrics:
- Total findings per scan
- Severity breakdown (high/medium/low)
- Files scanned vs files with issues
- Average findings per file
- Scan duration

Alerts when:
- High severity findings > 5
- Medium severity findings > 20
- Scan duration > 5 minutes

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Contributing

Follow the standard agent structure:
- `src/` - Agent implementation
- `tests/` - Comprehensive test suite (≥90% coverage required)
- `config/` - Configuration files
- `prompts/` - Usage documentation
- `CHANGELOG.md` - Version history

## License

Part of the _codex_ repository. See repository LICENSE for details.

## Maintainers

- GitHub Copilot Agent (primary)
- @mbaetiong (repository owner)
