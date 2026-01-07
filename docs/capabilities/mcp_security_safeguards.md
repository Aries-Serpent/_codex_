# MCP Security Safeguards

## Overview

The MCP security safeguards capability implements defensive programming patterns and security controls for Model Context Protocol services, including confirmation prompts, dry-run modes, input sanitization, and validation safeguards.

**Keywords**: mcp, security, safeguards, validation, sanitization, confirm, dry-run, defensive, protection, safety

## Purpose

Provides security safeguards through:
- **Confirmation Prompts**: User confirmation for sensitive operations
- **Dry-Run Mode**: Preview changes without executing
- **Input Sanitization**: Clean and validate all inputs
- **Bounds Checking**: Validate ranges, limits, constraints
- **Error Handling**: Safe failure modes with rollback
- **Audit Logging**: Track security-relevant operations

## Architecture

### Security Layers

```
┌─────────────────────────────────────┐
│   Confirmation Layer                │
│   (User prompts for sensitive ops)  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Validation Layer                  │
│   (Input sanitization & bounds)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Execution Layer                   │
│   (Dry-run mode, safe execution)    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Audit Layer                       │
│   (Security logging & monitoring)   │
└─────────────────────────────────────┘
```

## Implementation Patterns

### Confirmation Prompts

```python
def confirm_action(action: str, details: dict) -> bool:
    """Prompt user for confirmation of sensitive operation."""
    print(f"⚠️  About to perform: {action}")
    print(f"Details: {json.dumps(details, indent=2)}")
    
    response = input("Proceed? (yes/no): ").strip().lower()
    return response in ["yes", "y"]

# Usage
if confirm_action("delete_database", {"database": "production"}):
    delete_database()
else:
    print("Operation cancelled")
```

### Dry-Run Mode

```python
class Operation:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
    
    def execute(self, command: str):
        """Execute command with dry-run support."""
        if self.dry_run:
            print(f"[DRY-RUN] Would execute: {command}")
            return {"executed": False, "would_have": command}
        else:
            print(f"Executing: {command}")
            result = actually_execute(command)
            return {"executed": True, "result": result}

# Usage
op = Operation(dry_run=True)
op.execute("rm -rf /data")  # Safe, just previews
```

### Input Sanitization

```python
import re
from typing import Optional

def sanitize_input(user_input: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Bounds check
    if len(user_input) > max_length:
        raise ValueError(f"Input exceeds max length {max_length}")
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_input)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',
        r'exec\s*\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValueError(f"Dangerous pattern detected: {pattern}")
    
    return sanitized.strip()

# Usage
try:
    safe_input = sanitize_input(user_data)
    process(safe_input)
except ValueError as e:
    print(f"Invalid input: {e}")
```

### Bounds Checking

```python
from typing import Union, Optional

def validate_bounds(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    name: str = "value"
) -> None:
    """Validate value is within bounds."""
    if min_val is not None and value < min_val:
        raise ValueError(f"{name} must be >= {min_val}, got {value}")
    
    if max_val is not None and value > max_val:
        raise ValueError(f"{name} must be <= {max_val}, got {value}")

# Usage
def set_timeout(seconds: int):
    validate_bounds(seconds, min_val=1, max_val=300, name="timeout")
    # Safe to proceed
    config.timeout = seconds
```

### Safe Failure with Rollback

```python
class Transaction:
    """Context manager for safe operations with rollback."""
    
    def __init__(self):
        self.operations = []
        self.committed = False
    
    def add_operation(self, op: Callable, rollback: Callable):
        """Add operation with rollback function."""
        self.operations.append((op, rollback))
    
    def execute(self):
        """Execute all operations."""
        executed = []
        try:
            for op, rollback in self.operations:
                op()
                executed.append((op, rollback))
        except Exception as e:
            # Rollback in reverse order
            for op, rollback in reversed(executed):
                try:
                    rollback()
                except Exception as rb_error:
                    print(f"Rollback error: {rb_error}")
            raise e
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.committed = True
        return False

# Usage
with Transaction() as txn:
    txn.add_operation(
        op=lambda: create_user("alice"),
        rollback=lambda: delete_user("alice")
    )
    txn.add_operation(
        op=lambda: send_email("alice@example.com"),
        rollback=lambda: None  # Email can't be unsent
    )
    txn.execute()
```

## Usage Examples

### Example 1: Secure File Operations

```python
import os
from pathlib import Path

def safe_delete_file(file_path: str, dry_run: bool = False, confirm: bool = True):
    """Safely delete file with safeguards."""
    # Sanitize path
    path = Path(file_path).resolve()
    
    # Bounds check: prevent deleting outside allowed directories
    allowed_dirs = [Path("/tmp"), Path("/var/data")]
    if not any(path.is_relative_to(allowed) for allowed in allowed_dirs):
        raise ValueError(f"Path {path} not in allowed directories")
    
    # Confirmation
    if confirm:
        if not confirm_action("delete_file", {"path": str(path)}):
            print("Deletion cancelled")
            return
    
    # Dry-run mode
    if dry_run:
        print(f"[DRY-RUN] Would delete: {path}")
        return
    
    # Execute with error handling
    try:
        os.remove(path)
        print(f"✓ Deleted: {path}")
    except Exception as e:
        print(f"✗ Failed to delete {path}: {e}")
        raise
```

### Example 2: Secure API Endpoint

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, validator

app = FastAPI()

class SecureRequest(BaseModel):
    user_id: str
    action: str
    parameters: dict
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Sanitize user ID."""
        if not v.isalnum():
            raise ValueError('user_id must be alphanumeric')
        if len(v) > 50:
            raise ValueError('user_id too long')
        return v
    
    @validator('action')
    def validate_action(cls, v):
        """Validate action against whitelist."""
        allowed = ['read', 'write', 'update', 'delete']
        if v not in allowed:
            raise ValueError(f'action must be one of {allowed}')
        return v

@app.post("/api/execute")
async def execute_action(
    request: SecureRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    dry_run: bool = False
):
    """Execute action with security safeguards."""
    # Validate API key
    if not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Audit log
    log_security_event(
        "api_request",
        user=request.user_id,
        action=request.action,
        dry_run=dry_run
    )
    
    # Dry-run mode
    if dry_run:
        return {
            "executed": False,
            "would_perform": request.action,
            "parameters": request.parameters
        }
    
    # Execute with safeguards
    try:
        result = execute_with_timeout(
            request.action,
            request.parameters,
            timeout_seconds=30
        )
        return {"success": True, "result": result}
    except Exception as e:
        log_security_event("api_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

### Example 3: Database Operations with Safeguards

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def safe_db_transaction(db_path: str, dry_run: bool = False):
    """Database transaction with rollback on error."""
    conn = sqlite3.connect(db_path)
    conn.isolation_level = None  # Auto-commit off
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN")
        
        if dry_run:
            # In dry-run, collect queries but don't commit
            queries = []
            original_execute = cursor.execute
            
            def tracked_execute(query, *args, **kwargs):
                queries.append(query)
                return original_execute(query, *args, **kwargs)
            
            cursor.execute = tracked_execute
        
        yield cursor
        
        if dry_run:
            cursor.execute("ROLLBACK")
            print(f"[DRY-RUN] Would execute {len(queries)} queries")
        else:
            cursor.execute("COMMIT")
    
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Transaction rolled back: {e}")
        raise
    
    finally:
        conn.close()

# Usage
with safe_db_transaction("data.db", dry_run=True) as cursor:
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", ("admin", 123))
```

## Integration with Audit Pipeline

### Detection Command

```bash
# Check security safeguards capability
python scripts/space_traversal/audit_runner.py explain mcp-security-safeguards

# Run full audit
python scripts/space_traversal/audit_runner.py run
```

### Programmatic Detection

```python
from scripts.space_traversal.detectors import mcp_security_safeguards

# Run detector
file_index = {
    "files": [
        {"path": "src/services/api.py"},
        {"path": "src/utils/security.py"}
    ]
}

result = mcp_security_safeguards.detect(file_index)
print(f"Found patterns: {result['found_patterns']}")
# Expected: ['confirm', 'dry_run', 'sanitize']
```

## Best Practices

### Defense in Depth

1. **Multiple Layers**: Don't rely on single safeguard
2. **Fail Secure**: Default to safe/restricted behavior
3. **Audit Everything**: Log security-relevant operations
4. **Principle of Least Privilege**: Minimize permissions

### Input Validation

1. **Whitelist over Blacklist**: Allow known-good, not block known-bad
2. **Validate Early**: Check inputs at entry points
3. **Sanitize Always**: Never trust user input
4. **Use Type Safety**: Leverage Pydantic/typing for validation

### Error Handling

1. **Don't Expose Details**: Generic error messages to users
2. **Log Detailed Errors**: Full details in secure logs
3. **Graceful Degradation**: Fall back to safe defaults
4. **Test Error Paths**: Ensure errors don't leak information

## Troubleshooting

### Issue: Confirmation Prompts in Automated Scripts

**Solution**: Add `--yes` flag to bypass prompts
```python
import sys

def confirm_action(action: str, auto_yes: bool = False):
    if auto_yes or "--yes" in sys.argv:
        return True
    return input(f"Confirm {action}? (yes/no): ").lower() == "yes"
```

### Issue: Dry-Run Not Preventing Side Effects

**Solution**: Check dry-run flag at lowest level
```python
class DBConnection:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
    
    def execute(self, query):
        if self.dry_run:
            print(f"[DRY-RUN] {query}")
            return
        # Actually execute
```

## Performance Considerations

- **Validation Overhead**: 1-10ms per request (acceptable for security)
- **Dry-Run Cost**: Minimal (just logging)
- **Confirmation UX**: Use timeouts for prompts

## Monitoring

### Security Metrics

```python
security_events = {
    "sanitization_blocks": 0,
    "confirmation_denials": 0,
    "dry_run_executions": 0
}

def log_security_event(event_type: str, **details):
    security_events[event_type] = security_events.get(event_type, 0) + 1
    logger.info(f"Security event: {event_type}", extra=details)
```

## Related Capabilities

- **mcp-configuration**: Secure configuration management
- **mcp-schema-validation**: Input validation schemas
- **safeguards_keywords**: Safeguard keyword detection

## Safeguards in This Capability

1. **Input Validation**: All user inputs sanitized
2. **Bounds Checking**: Range validation on parameters
3. **Confirmation**: User prompts for dangerous operations
4. **Dry-Run**: Preview mode for testing
5. **Rollback**: Transaction support for atomicity
6. **Audit Logging**: Track all security events

---

**Last Updated**: 2025-12-09  
**Capability ID**: mcp-security-safeguards
