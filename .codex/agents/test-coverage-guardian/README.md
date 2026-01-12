# Test Coverage Guardian Agent

Ensures security-critical code has comprehensive test coverage.

## Features

- **Security-Critical Detection**: Automatically identifies validation, authentication, crypto functions
- **Coverage Requirements**:
  - Security-Critical: 100% coverage
  - High Priority: 95% coverage
  - Medium Priority: 80% coverage
- **Test Generation**: Automatically creates comprehensive test templates
- **Attack Vector Tests**: Includes injection, XSS, path traversal tests

## Quick Start

```bash
# Analyze all source files
python run.py --all

# Check specific module
python run.py --files src/agents/validation.py

# Generate test files
python run.py --all --generate-tests --output-dir tests/generated

# Only report security-critical functions
python run.py --all --security-critical-only
```

## Criticality Detection

### Security-Critical (100% coverage)
Functions matching patterns:
- `*validate*`, `*sanitize*`, `*authenticate*`, `*authorize*`
- `*encrypt*`, `*decrypt*`, `*hash*`, `*sign*`, `*verify*`
- Contains: password, token, secret, key operations

### High Priority (95% coverage)
- Login/logout functions
- Session management
- API key handling
- Input validation with `raise ValueError`

## Generated Test Example

For a security-critical function:

```python
@pytest.mark.parametrize(
    "invalid_input,expected_error",
    [
        ("; rm -rf /", ValueError),
        ("$(whoami)", ValueError),
        ("../../../etc/passwd", ValueError),
    ],
)
def test_invalid_input_rejected(invalid_input, expected_error):
    with pytest.raises(expected_error):
        validate_input(invalid_input)
```

## Output

```
Test Coverage Guardian - Analysis Results
================================================================================

Total Issues: 5
Security Critical: 2
High Priority: 3

SECURITY CRITICAL:
  src/security/validation.py:42 - _validate_override
    Coverage: 0.0% / 100.0%
    Missing tests for security_critical function
```

## Integration

Pre-commit hook:
```yaml
- repo: local
  hooks:
    - id: test-coverage-guardian
      entry: python .codex/agents/test-coverage-guardian/run.py
      language: python
```

## Success Metrics

- All security-critical functions: 100% tested
- Injection attack vectors: Comprehensive coverage
- Generated tests: Production-ready templates
