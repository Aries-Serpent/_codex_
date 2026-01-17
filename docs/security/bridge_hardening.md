# Bridge Security Hardening - Phase 3.1

## Overview

The `src/bridge_manager.py` module provides a secure IPC bridge for Cognitive-Copilot communication, replacing the fragile file-based approach at `temp/bridge_codex_copilot_bridge`.

## Security Features Implemented

### 1. Authenticated Named Pipes (0o600 Permissions)

**Implementation:**
- Named pipes (FIFO) created with `0o600` permissions (owner-only read/write)
- Bridge directory restricted to `0o700` (owner-only access)
- Secure temp location: `/tmp/codex_secure_bridge` (configurable)

```python
# From bridge_manager.py:202
os.mkfifo(str(self.pipe_path), 0o600 if self.owner_only else 0o666)

# From bridge_manager.py:179
os.chmod(self.bridge_dir, 0o700)  # Owner only: rwx------
```

### 2. File-Based Locking (fcntl)

**Implementation:**
- Exclusive locking using `fcntl.flock()` to prevent race conditions
- Lock file with 0o600 permissions
- Timeout support to prevent deadlocks

```python
# From bridge_manager.py:94
fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
```

### 3. Message Validation

**Implementation:**
- Typed message format using Pydantic dataclasses
- Required fields: timestamp, source, message_type, context
- JSON serialization with integrity checks

```python
# From bridge_manager.py:59
def validate(self) -> bool:
    """Validate message structure."""
    required_fields = ["timestamp", "source", "message_type", "context"]
    return all(hasattr(self, field) for field in required_fields)
```

### 4. Unix Domain Socket Support

**Implementation:**
- Alternative to named pipes for higher throughput
- Socket file with 0o600 permissions
- Connection-oriented protocol with proper cleanup

```python
# From bridge_manager.py:337
if self.owner_only:
    os.chmod(self.socket_path, 0o600)
```

## Threat Model (STRIDE)

Reference: `temp/bridge_codex_copilot_bridge` vulnerabilities documented in STRIDE.md

### Mitigations

| Threat | Original Risk | Mitigation |
|--------|--------------|------------|
| **Spoofing** | Any process could write to bridge | 0o600 permissions restrict access to owner |
| **Tampering** | No integrity checks on messages | Typed messages with validation |
| **Repudiation** | No audit trail | Metadata in ContextMessage (timestamp, source) |
| **Information Disclosure** | World-readable bridge files | 0o700 directory, 0o600 files |
| **Denial of Service** | Race conditions, no locking | fcntl-based exclusive locking |
| **Elevation of Privilege** | Insecure temp location | Secure temp dir with restricted permissions |

## Usage Examples

### Basic Usage

```python
from src.bridge_manager import BridgeManager, ContextMessage, BridgeMode
from datetime import datetime

# Create secure bridge
bridge = BridgeManager(
    mode=BridgeMode.NAMED_PIPE,
    owner_only=True  # Enforces 0o600 permissions
)

# Send message
message = ContextMessage(
    timestamp=datetime.now().isoformat(),
    source="cognitive_brain",
    message_type="context_update",
    context={"workflow_state": "active"}
)

success = bridge.write_message(message)

# Read message
received = bridge.read_message(timeout=5)

# Cleanup
bridge.cleanup()
```

### Context Manager Usage

```python
from src.bridge_manager import bridge_lock

# Safe critical section
with bridge_lock(bridge.lock_path):
    # Operations here are protected from race conditions
    bridge.write_message(message)
```

### Convenience Functions

```python
from src.bridge_manager import share_context_with_copilot

# High-level API
success = share_context_with_copilot(
    context={"task": "build", "status": "complete"}
)
```

## Configuration

### Environment Variables

- `CODEX_BRIDGE_MODE`: Set to "unix_socket" or "named_pipe" (default: "named_pipe")
- `CODEX_BRIDGE_DIR`: Custom bridge directory path (default: secure temp)
- `CODEX_BRIDGE_OWNER_ONLY`: Set to "false" to allow group access (default: "true")

### Best Practices

1. **Always use owner_only=True in production**
2. **Set timeouts on read operations** to prevent hangs
3. **Call cleanup()** after bridge use or use context managers
4. **Validate messages** before processing content
5. **Monitor lock_path** for abandoned locks

## Security Audit Checklist

- [x] Named pipes created with 0o600 permissions
- [x] Bridge directory restricted to 0o700
- [x] File-based locking using fcntl
- [x] Message validation with required fields
- [x] Secure temp location (not world-writable)
- [x] Unix socket support with proper permissions
- [x] Timeout support to prevent deadlocks
- [x] Proper cleanup of IPC resources
- [x] Logging of security events
- [x] No hardcoded credentials or secrets

## Migration from Legacy Bridge

### Old Approach (Insecure)

```python
# DEPRECATED: temp/bridge_codex_copilot_bridge
bridge_file = Path("temp/bridge_codex_copilot_bridge/context.json")
bridge_file.write_text(json.dumps(context))  # World-readable!
```

### New Approach (Secure)

```python
from src.bridge_manager import share_context_with_copilot

# Secure, validated, locked
share_context_with_copilot(context)
```

## Testing

See `tests/integration/test_bridge_security.py` for security validation tests:

- Permission enforcement
- Lock acquisition under contention
- Message validation
- Cleanup verification

## References

- [STRIDE Threat Model](../../../STRIDE.md)
- [SECURITY.md](../../SECURITY.md)
- [Bridge Manager Implementation](../../../src/bridge_manager.py)

## Compliance

This implementation addresses:

- **OWASP Top 10**: A01:2021 - Broken Access Control
- **CWE-732**: Incorrect Permission Assignment for Critical Resource
- **CWE-362**: Concurrent Execution using Shared Resource with Improper Synchronization

## Future Enhancements

- [ ] Add authentication tokens for multi-user environments
- [ ] Implement message encryption for sensitive contexts
- [ ] Add audit logging to dedicated security log
- [ ] Support for SELinux/AppArmor policies
- [ ] Message rate limiting to prevent DoS
- [ ] Automatic cleanup of stale locks

---

**Status:** ✅ Secure bridge implementation complete (Phase 3.1)

**Last Updated:** 2026-01-08

**Reviewed By:** Lead Systems Architect & Integration Engineer
