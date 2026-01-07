# Error Handling Improvement Guide

## Overview

This document provides guidelines for improving error handling patterns across the codebase, addressing security scanning alerts related to silent exception handling.

## Current Issues

### 1. Try-Except-Pass Pattern

**Problem**: Silent exception swallowing makes debugging impossible and hides failures.

```python
# ❌ BAD: Silent failure
try:
    risky_operation()
except:
    pass
```

**Solution**: Add logging and proper error context.

```python
# ✅ GOOD: Logged failure with context
import logging
logger = logging.getLogger(__name__)

try:
    risky_operation()
except Exception as e:
    logger.warning(f"Operation failed but continuing: {e}", exc_info=True)
    # Optionally provide fallback or default value
```

## Recommended Patterns

### Pattern 1: Log and Continue

For non-critical operations where failure is acceptable:

```python
try:
    optional_operation()
except Exception as e:
    logger.info(f"Optional operation failed: {e}")
    # Continue without this feature
```

### Pattern 2: Log and Re-raise

For critical operations that should halt execution:

```python
try:
    critical_operation()
except Exception as e:
    logger.error(f"Critical operation failed: {e}", exc_info=True)
    raise  # Re-raise to propagate the error
```

### Pattern 3: Specific Exception Handling

Catch only expected exceptions, let unexpected ones propagate:

```python
try:
    file_content = Path(file_path).read_text()
except FileNotFoundError:
    logger.warning(f"File not found: {file_path}, using default")
    file_content = DEFAULT_CONTENT
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    raise
# Other exceptions (e.g., OSError) propagate naturally
```

### Pattern 4: Context Managers for Resources

Use context managers for automatic cleanup:

```python
# ✅ GOOD: Automatic cleanup
with open(file_path, 'r') as f:
    content = f.read()
# File automatically closed even if exception occurs
```

## Implementation Strategy

### Phase 1: Audit Current Exception Handlers

```bash
# Find all bare except clauses
grep -rn "except:" --include="*.py" src/ agents/ scripts/

# Find try-except-pass patterns
grep -A 1 "except:" --include="*.py" src/ | grep -B 1 "pass"
```

### Phase 2: Categorize by Criticality

1. **Critical**: Security, data integrity, core functionality
2. **Important**: Feature functionality, user-facing operations
3. **Optional**: Logging, metrics, non-essential features

### Phase 3: Apply Appropriate Pattern

- **Critical**: Log and re-raise or use specific exceptions
- **Important**: Log with warning level, optionally provide fallback
- **Optional**: Log with info level, continue without feature

## Automated Fix Script (Partial)

```python
#!/usr/bin/env python3
"""
Semi-automated error handling improvement.
Adds logging to bare except blocks as a first step.
"""
import re
from pathlib import Path

def add_logging_to_bare_except(file_path: Path) -> bool:
    content = file_path.read_text()
    
    # Add logger import if missing
    if 'import logging' not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                lines.insert(i + 1, 'import logging')
                break
        content = '\n'.join(lines)
    
    if 'logger = logging.getLogger' not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import logging' in line:
                lines.insert(i + 1, 'logger = logging.getLogger(__name__)')
                break
        content = '\n'.join(lines)
    
    # Replace bare except: pass with logged version
    content = re.sub(
        r'except:\s*\n\s+pass',
        'except Exception as e:\n        logger.warning(f"Exception caught: {e}", exc_info=True)',
        content
    )
    
    if content != file_path.read_text():
        file_path.write_text(content)
        return True
    return False
```

## Best Practices

### 1. Always Use Specific Exception Types

```python
# ❌ Too broad
except Exception:
    pass

# ✅ Specific
except (FileNotFoundError, PermissionError) as e:
    logger.warning(f"File access error: {e}")
```

### 2. Include Context in Log Messages

```python
# ❌ Generic message
logger.error("Operation failed")

# ✅ Specific context
logger.error(f"Failed to process file {file_path}: {e}", exc_info=True)
```

### 3. Use exc_info for Stack Traces

```python
# ✅ Include full traceback for debugging
logger.error("Operation failed", exc_info=True)
```

### 4. Fail Fast for Unexpected Errors

```python
# ✅ Don't catch what you can't handle
try:
    critical_operation()
except ValueError as e:
    # Handle expected error
    logger.warning(f"Invalid value: {e}")
# Let other exceptions propagate
```

## Migration Checklist

- [ ] Audit all try-except blocks in module
- [ ] Categorize by criticality
- [ ] Add logging to all bare except blocks
- [ ] Convert generic exceptions to specific types
- [ ] Add proper error messages with context
- [ ] Test error paths with unit tests
- [ ] Document expected exceptions in docstrings

## Testing Error Paths

```python
def test_error_handling(caplog):
    """Test that errors are properly logged."""
    with caplog.at_level(logging.WARNING):
        result = function_with_error_handling()
    
    # Verify error was logged
    assert "Expected error message" in caplog.text
    
    # Verify fallback behavior
    assert result == EXPECTED_FALLBACK
```

## References

- Python Logging: https://docs.python.org/3/library/logging.html
- Exception Handling Best Practices: PEP 3151
- Security Implications: OWASP Error Handling Guide

## Status

- **Created**: 2025-12-22
- **Status**: Living document - update as patterns evolve
- **Owner**: Security Team
