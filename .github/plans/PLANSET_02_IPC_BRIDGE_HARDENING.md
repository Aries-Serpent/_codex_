# Planset 02: IPC Bridge Hardening (Named Pipes Security)

**Planset ID:** PS-02  
**Priority:** P0 - Critical (Security)  
**Phase:** Pre-commit Cycle 1-2  
**Status:** 📋 Planned  
**Dependencies:** None  
**Cognitive Brain Objective:** Eliminate security vulnerabilities in inter-process communication

---

## Context

**Problem:** `temp/bridge_codex_copilot_bridge` uses TCP sockets vulnerable to local interception

**Security Risk:** HIGH
- Local privilege escalation possible
- No authentication mechanism
- Potential data leakage
- MITM attacks on localhost

**Solution:** Replace TCP sockets with authenticated Linux Named Pipes (FIFOs) with 0o600 permissions

---

## Implementation Plan

### Pre-commit Cycle 1: Named Pipe Implementation

**Goal:** Replace TCP sockets with secure named pipes

**Tasks:**
- [ ] Analyze current `src/bridge_manager.py` socket implementation
- [ ] Design named pipe architecture with authentication
- [ ] Implement `SecureBridge` class using `os.mkfifo()`
- [ ] Add permission enforcement (0o600 - owner-only)
- [ ] Implement non-blocking open handling
- [ ] Add authentication token validation
- [ ] Create comprehensive error handling

**Files to Modify:**
- `src/bridge_manager.py` (~300 lines refactor)

**Files to Create:**
- `src/bridge/secure_ipc.py` (~250 lines)
- `tests/test_secure_bridge.py` (~300 lines)

**Security Features:**
- Owner-only permissions (0o600)
- Authentication token required
- Process isolation
- Non-blocking I/O
- Timeout handling

**Success Criteria:**
- [ ] Named pipes created with correct permissions
- [ ] Authentication working
- [ ] Non-blocking operations functional
- [ ] Security audit passing

### Pre-commit Cycle 2: Migration & Validation

**Goal:** Complete migration from TCP to named pipes

**Tasks:**
- [ ] Update all bridge consumers
- [ ] Migrate environment variables (CODEX_BRIDGE_TOKEN)
- [ ] Test repro workflows with new bridge
- [ ] Security penetration testing
- [ ] Performance benchmarking
- [ ] Document security model

**Files to Update:**
- All files importing `bridge_manager.py` (~15 files)
- Environment variable documentation

**Testing:**
- [ ] Unit tests (90%+ coverage)
- [ ] Integration tests (workflow execution)
- [ ] Security tests (permission validation)
- [ ] Performance tests (latency <10ms)

**Success Criteria:**
- [ ] Zero security vulnerabilities
- [ ] All workflows using secure bridge
- [ ] Performance maintained or improved
- [ ] Documentation complete

---

## Security Requirements

### Permission Model
```bash
# Named pipe must have:
- Mode: 0o600 (rw-------)
- Owner: Current process user
- No group/other access
```

### Authentication Flow
```
1. Client requests pipe access
2. Server validates CODEX_BRIDGE_TOKEN
3. If valid: Allow operation
4. If invalid: Reject and log attempt
```

### Audit Trail
- Log all authentication attempts
- Track authorized operations
- Alert on suspicious activity

---

## Success Metrics

- **Security Score:** 10/10 (no vulnerabilities)
- **Permission Compliance:** 100%
- **Authentication Success Rate:** 100%
- **Performance:** <10ms latency
- **Reliability:** 99.9% uptime

---

## Risk Mitigation

**Risk 1:** Breaking existing workflows
- **Mitigation:** Parallel run both systems for 1 cycle
- **Fallback:** Feature flag to enable/disable

**Risk 2:** Platform compatibility issues
- **Mitigation:** Linux-only initially (self-hosted runners)
- **Fallback:** Socket fallback for non-Linux

**Risk 3:** Deadlock on non-blocking opens
- **Mitigation:** Timeout + retry logic
- **Fallback:** Error handling with graceful degradation

---

## Cognitive Brain Integration

**Patterns Learned:**
1. Named pipe (FIFO) usage in Python
2. Permission enforcement with `os.mkfifo()`
3. Non-blocking I/O patterns
4. Authentication token validation
5. Security audit practices

**Reusable Utilities:**
1. `secure_ipc.py` - Generic secure IPC library
2. Permission validation helpers
3. Authentication decorators
4. Security testing utilities

**Knowledge Base Update:**
- Add IPC security best practices
- Document named pipe usage patterns
- Create security audit checklist

---

## Implementation Code

### Core Named Pipe Implementation

```python
import os
import stat
from pathlib import Path

class SecureBridge:
    def __init__(self, pipe_path: Path):
        self.pipe_path = pipe_path
        self.auth_token = os.getenv("CODEX_BRIDGE_TOKEN")
        
    def create_pipe(self):
        """Create named pipe with secure permissions."""
        if self.pipe_path.exists():
            self.pipe_path.unlink()
        
        # Create with owner-only permissions
        os.mkfifo(self.pipe_path, mode=0o600)
        
        # Verify permissions
        st = self.pipe_path.stat()
        mode = stat.S_IMODE(st.st_mode)
        if mode != 0o600:
            raise SecurityError(f"Insecure permissions: {oct(mode)}")
    
    def verify_permissions(self) -> bool:
        """Verify pipe has secure permissions."""
        if not self.pipe_path.exists():
            return False
        
        st = self.pipe_path.stat()
        
        # Check permissions (must be 0o600)
        if stat.S_IMODE(st.st_mode) != 0o600:
            return False
        
        # Check owner (must be current user)
        if st.st_uid != os.getuid():
            return False
        
        return True
```

---

## Dependencies

**Required:**
- Python 3.8+ (os.mkfifo support)
- Linux OS (self-hosted runners)

**Testing:**
- pytest-timeout (for non-blocking tests)

---

## Follow-Up Plansets

- **PS-03:** Split Brain Elimination (uses secure bridge)
- **PS-10:** Owner Guard Enforcement (uses bridge for CI/CD)

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)  
**Status:** Ready for implementation
