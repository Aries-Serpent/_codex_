---
name: datetime-modernizer
description: Modernizes datetime handling to use timezone-aware datetime objects and UTC-based timestamps throughout the codebase.
---

# DateTime Modernizer Agent

This agent modernizes datetime handling across the codebase, ensuring consistent use of timezone-aware datetime objects and UTC-based timestamps.

## Capabilities

- **Detection**: Finds naive datetime usage in code
- **Modernization**: Converts to timezone-aware datetime with UTC
- **Deprecation Warnings**: Adds warnings for deprecated patterns
- **Testing**: Validates datetime handling in tests

## Patterns Fixed

```python
# Before (naive)
from datetime import datetime
now = datetime.now()

# After (timezone-aware)
from datetime import datetime, UTC
now = datetime.now(UTC)
```

## When to Use

- When updating code to Python 3.11+ datetime patterns
- During code quality improvement sprints
- When fixing timezone-related bugs

## Integration

This agent works with any Python file containing datetime operations.
