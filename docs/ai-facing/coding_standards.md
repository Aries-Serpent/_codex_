# Coding Standards

> For AI Agents - Last Updated: 2025-12-24

This document defines the coding standards for contributions to _codex_.

## Python Style Guide

### General Rules

1. **Follow PEP 8** with these exceptions:
   - Line length: 100 characters (not 79)
   - Use double quotes for strings

2. **Use type hints** for all function signatures:
   ```python
   def process_data(items: list[str], limit: int = 10) -> dict[str, Any]:
       ...
   ```

3. **Use dataclasses** for data containers:
   ```python
   @dataclass
   class Result:
       success: bool
       value: str | None = None
   ```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `calculate_score` |
| Classes | PascalCase | `DataProcessor` |
| Constants | UPPER_CASE | `MAX_RETRIES` |
| Private | _leading_underscore | `_internal_method` |

### Imports

Order imports as:
1. Standard library
2. Third-party packages
3. Local imports

```python
import json
import os
from pathlib import Path

import pytest
from pydantic import BaseModel

from src.config import settings
```

### Documentation

Use docstrings for all public functions:
```python
def fetch_data(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch data from the specified URL.
    
    Args:
        url: The URL to fetch from.
        timeout: Request timeout in seconds.
    
    Returns:
        Parsed JSON response as dictionary.
    
    Raises:
        RequestError: If the request fails.
    """
```

## Error Handling

### Pattern: Defensive Error Handling

```python
def safe_operation(data: dict) -> Result:
    """Perform operation with defensive error handling."""
    try:
        # Validate input
        if not data:
            return Result(success=False, error="Empty data")
        
        # Perform operation
        result = process(data)
        return Result(success=True, value=result)
    
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return Result(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

### Logging

Use structured logging:
```python
logger = logging.getLogger(__name__)

logger.info("Processing started", extra={"count": len(items)})
logger.error("Operation failed", exc_info=True)
```

## Testing

### Test Structure

```python
class TestDataProcessor:
    """Test suite for DataProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return DataProcessor()
    
    def test_process_valid_data(self, processor):
        """Test processing valid input."""
        result = processor.process({"key": "value"})
        assert result.success is True
    
    def test_process_empty_data(self, processor):
        """Test handling empty input."""
        result = processor.process({})
        assert result.success is False
```

### Test Naming

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<behavior>_<condition>`

## Security

1. **Never hardcode secrets** - Use environment variables
2. **Validate all inputs** - Use Pydantic or manual checks
3. **Sanitize outputs** - Escape user-provided data
4. **Log securely** - Never log passwords or tokens

## Performance

1. **Avoid premature optimization** - Profile first
2. **Use generators** for large data sets
3. **Cache expensive operations** - Use `@lru_cache`
4. **Batch API calls** when possible

## See Also

- [Tools Reference](tools_reference.md)
- [Business Rules](business_rules.md)
