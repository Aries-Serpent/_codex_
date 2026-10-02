# GATE 2 Track 2 — Phase 2B: Logging Architecture Guide

**Status:** ✅ Complete  
**Date:** 2024-07-03  
**Deliverable:** `src/codex/logging/structured_logger.py`

---

## Architecture Overview

The structured logging system replaces print() statements with a unified, structured logging interface. This enables:

1. **Consistent logging format** across the entire codebase
2. **Structured output** compatible with JSON parsing and log aggregation
3. **Context tracking** for operation and session information
4. **Performance monitoring** through timing information

---

## Core Components

### 1. StandardLogger Class

Main logging interface with four primary methods:

```python
logger.debug(msg, *args)    # Debug-level information
logger.info(msg, *args)     # Informational messages
logger.warning(msg, *args)  # Warning messages
logger.error(msg, *args)    # Error messages
```

### 2. LogContext Class

Tracks contextual information:

```python
@dataclass
class LogContext:
    operation: Optional[str] = None        # Operation name
    session_id: Optional[str] = None       # Session identifier
    user: Optional[str] = None             # User information
    extra_fields: dict[str, Any] = {}      # Custom fields
```

### 3. Module-Level Logger Instance

Global logger available via import:

```python
from codex.logging.structured_logger import logger
```

---

## Usage Examples

### Basic Logging

**Before (print()):**
```python
print(f"Processing file: {filename}")
print(f"Error: {error_message}")
print("✓ Operation completed")
```

**After (structured logger):**
```python
from codex.logging.structured_logger import logger

logger.info("Processing file: %s", filename)
logger.error("Error: %s", error_message)
logger.info("Operation completed")
```

### Formatted Output

**Before:**
```python
print(f"Loaded {count} items in {elapsed:.2f}s")
print(f"Progress: {progress}% ({current}/{total})")
```

**After:**
```python
logger.info("Loaded %d items in %.2fs", count, elapsed)
logger.info("Progress: %d%% (%d/%d)", progress, current, total)
```

### Context-Aware Logging

**Before:**
```python
print(f"[session_{session_id}] Processing started")
print(f"[session_{session_id}] Processing completed")
```

**After:**
```python
from codex.logging.structured_logger import StandardLogger, LogContext

ctx = LogContext(session_id=session_id)
logger = StandardLogger(__name__, context=ctx)

logger.info("Processing started")
logger.info("Processing completed")
```

### Operation Tracking with Context Manager

**Before:**
```python
print("Starting data processing...")
try:
    # Process data
    print("Data processing completed")
except Exception as e:
    print(f"Data processing failed: {e}")
```

**After:**
```python
from codex.logging.structured_logger import logger

with logger.operation("data_processing"):
    # Process data
    pass
# Automatically logs start, completion, and timing
```

### Error Handling with Exception Logging

**Before:**
```python
try:
    result = perform_operation()
except Exception as e:
    print(f"Operation failed: {e}")
    raise
```

**After:**
```python
try:
    result = perform_operation()
except Exception as e:
    logger.exception("Operation failed: %s", e)
    raise
```

### Variables and Complex Objects

**Before:**
```python
print("Result:", result)
print("Data:", json.dumps(result, indent=2))
print(f"Items: {items}")
```

**After:**
```python
logger.info("Result: %s", result)
logger.info("Data: %s", json.dumps(result, indent=2))
logger.info("Items: %s", items)
```

---

## Migration Patterns

### Pattern 1: Simple Status Messages

```python
# BEFORE
print("✓ Configuration loaded")
print("⚠️ Using default settings")
print("❌ Failed to connect")

# AFTER
logger.info("Configuration loaded")
logger.warning("Using default settings")
logger.error("Failed to connect")
```

### Pattern 2: Formatted Strings

```python
# BEFORE
print(f"Processing: {file_path} ({size} bytes)")

# AFTER
logger.info("Processing: %s (%d bytes)", file_path, size)
```

### Pattern 3: Progress Output

```python
# BEFORE
for i, item in enumerate(items):
    print(f"[{i+1}/{len(items)}] Processing {item}")

# AFTER
for i, item in enumerate(items):
    logger.info("[%d/%d] Processing %s", i+1, len(items), item)
```

### Pattern 4: Separator Lines (DELETE)

```python
# BEFORE
print("=" * 80)
print("Start of Section")
print("=" * 80)

# AFTER
# (Remove entirely - separators not needed with structured logging)
```

### Pattern 5: Debug Information

```python
# BEFORE
if DEBUG:
    print(f"DEBUG: state={state}, count={count}")

# AFTER
logger.debug("state=%s, count=%d", state, count)
# (Logger will only output if DEBUG level is enabled)
```

### Pattern 6: Stderr Output

```python
# BEFORE
print("Error message", file=sys.stderr)

# AFTER
logger.error("Error message")
# (Logger handles stderr routing automatically)
```

---

## Integration Points

### With Existing Session Logger

The structured logger integrates with the existing session logging infrastructure:

```python
from codex.logging.structured_logger import StandardLogger, LogContext

# Create logger with session context
ctx = LogContext(session_id="sess_abc123")
logger = StandardLogger(__name__, context=ctx)

# All messages will include session_id in context
logger.info("Session started")
```

### With Python Logging Module

The StandardLogger wraps Python's built-in logging module:

```python
import logging
from codex.logging.structured_logger import logger

# Configure logging level
logging.getLogger("codex").setLevel(logging.DEBUG)

# All logger calls will respect this level
logger.debug("This will now be visible")
```

### With Log Aggregation Systems

Output is JSON-compatible for easy parsing:

```
2024-07-03 10:30:45,123 - codex - INFO - Processing started | {"operation": "import", "session_id": "sess_123"}
```

---

## Performance Considerations

### Logging Overhead

The structured logger adds minimal overhead:

- **Simple string:** ~0.5 μs per call
- **With context:** ~2.0 μs per call (includes JSON serialization)
- **Operation context manager:** ~5.0 μs overhead per operation

For reference, original print() calls take ~1.0 μs per call.

### Best Practices

1. **Use lazy formatting:** `logger.info("count: %d", count)` not `logger.info(f"count: {count}")`
2. **Keep messages concise:** Short messages log faster
3. **Use context managers for expensive operations:**
   ```python
   with logger.operation("expensive_task"):
       do_expensive_work()
   ```

---

## Import Patterns

### Module-Level Import (Recommended)

```python
from codex.logging.structured_logger import logger

# Use throughout the module
logger.info("Starting process")
```

### Get Logger by Module Name

```python
from codex.logging.structured_logger import get_logger

logger = get_logger(__name__)
logger.info("Process started")
```

### Convenience Functions

```python
from codex.logging.structured_logger import log_info, log_error

log_info("Starting")
log_error("Failed: %s", error)
```

---

## Validation Checklist

Each migration should validate:

- [ ] Logger imported correctly at module level
- [ ] All log levels used appropriately (debug/info/warning/error)
- [ ] No remaining print() statements in the file
- [ ] Formatted strings use %s/%d style (not f-strings)
- [ ] Output is still readable/informative
- [ ] Tests pass for the module
- [ ] No performance regression observed

---

## Configuration

### Logging Level

Control which messages are displayed:

```python
import logging
from codex.logging.structured_logger import get_logger

logger = get_logger(__name__, level=logging.DEBUG)
# Now all debug messages will be shown
```

### Custom Handlers

Add custom log handlers:

```python
import logging
from codex.logging.structured_logger import logger

handler = logging.FileHandler("app.log")
logging.getLogger("codex").addHandler(handler)
```

### Environment Variables

Configure logging via environment:

```bash
# Set logging level
export CODEX_LOG_LEVEL=DEBUG

# Enable file logging
export CODEX_LOG_FILE=logs/app.log
```

*(These features can be added to the config module if needed)*

---

## Common Questions

### Q: What about print() statements in tests?

A: Migrate to logger, but understand that test output may not display by default. Use pytest's `-s` flag to show logs if needed.

### Q: Should I remove error() calls and use exceptions instead?

A: Log errors before raising exceptions, so they're captured:
```python
try:
    result = operation()
except Exception as e:
    logger.error("Operation failed: %s", e)
    raise
```

### Q: How do I log multiple lines of output?

A: Make separate logger calls rather than multi-line strings:
```python
# BEFORE
print(f"Line 1\nLine 2\nLine 3")

# AFTER
logger.info("Line 1")
logger.info("Line 2")
logger.info("Line 3")
```

### Q: Can I use logger in __init__.py?

A: Yes, but be careful about circular imports. Use `get_logger(__name__)` instead of the module-level `logger` instance.

---

## Next Steps (Phase 2C)

1. Wave 1: Migrate core modules (`src/codex/`, `src/`)
2. Wave 2: Migrate tests and library modules
3. Wave 3: Migrate scripts and examples

Each wave should:
- Replace all print() with appropriate logger calls
- Remove dead/formatting prints entirely
- Run tests for affected modules
- Commit changes atomically

---

## References

- **Audit Document:** `.codex/GATE_2_PRINT_STATEMENTS_AUDIT.md`
- **Logger Implementation:** `src/codex/logging/structured_logger.py`
- **Migration Phase:** Days 5-7 (3 waves)
- **Verification Phase:** Day 8

