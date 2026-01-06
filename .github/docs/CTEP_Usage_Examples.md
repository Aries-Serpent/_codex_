# CTEP Usage Examples

> **Version:** 1.0.0  
> **Related:** [Copilot Task Execution Protocol](./Copilot_Task_Execution_Protocol.md)

---

## Example 1: Activating CTEP

### User Input
```
Enable CTEP
```

### Copilot Response
```
🎯 Copilot Task Execution Protocol ACTIVATED

Protocol Mode: COMPREHENSIVE TASK COMPLETION
Session ID: CTEP-20251216-001
Activated: Previous Cycle-12-16T17:00:00Z

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVE DIRECTIVES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Complete ALL tasks - zero omissions
📊 Maintain live progress tracker
🔍 Codebase-first approach - search before creating
🧰 Document all new utilities with integration plans
🔄 Update progress after each task completion
✅ Final verification: Completed = Total, Skipped = 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to execute. Please provide your task list.
```

---

## Example 2: Task Execution with CTEP Active

### User Input
```
Fix the following 3 issues in config.py:
1. Add input validation
2. Fix logging configuration
3. Add error handling
```

### Copilot Response
```markdown
# Configuration File Fixes
> Generated: Previous Cycle-12-16T17:05:00Z | Protocol: CTEP Active | Status: In Progress

## 📊 Task Execution Progress

### Phase 1: Issue Resolution - 0% Complete
- [ ] Task 1.1: Add input validation ⏳ PENDING
- [ ] Task 1.2: Fix logging configuration ⏳ PENDING
- [ ] Task 1.3: Add error handling ⏳ PENDING

---

**Overall Progress**: 0% (0 of 3 tasks)

## 🔍 Codebase Integration Analysis

**Pre-Implementation Audit:**
- [x] Searched `/src/utils/` - Found `validation.py` with reusable validators
- [x] Searched `/src/common/` - Found `logger_config.py` with standard setup
- [x] Searched error handling patterns - Found `error_handlers.py` decorator

**Reuse Strategy:**
- Using: `validate_config()` from `src/utils/validation.py`
- Using: `setup_logger()` from `src/common/logger_config.py`
- Using: `@handle_errors` decorator from `src/utils/error_handlers.py`

## 🛠️ Implementation

### Phase 1: Issue Resolution

#### Task 1.1: Add Input Validation ✅ COMPLETE

**File:** `src/config.py`

**Changes:**
```python
from src.utils.validation import validate_config

def load_config(path: str) -> dict:
    # Input validation
    if not path or not isinstance(path, str):
        raise ValueError("Config path must be a non-empty string")
    
    if not Path(path).exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    config = _read_config(path)
    validate_config(config)  # Reusing existing validator
    return config
```

**Verification:**
- [x] Tests pass
- [x] Lint clean

---

#### Task 1.2: Fix Logging Configuration ✅ COMPLETE

**File:** `src/config.py`

**Changes:**
```python
from src.common.logger_config import setup_logger

logger = setup_logger(__name__)  # Using existing utility

def load_config(path: str) -> dict:
    logger.info(f"Loading configuration from: {path}")
    # ... implementation
    logger.debug(f"Configuration loaded successfully: {len(config)} keys")
    return config
```

**Verification:**
- [x] Tests pass
- [x] Lint clean

---

#### Task 1.3: Add Error Handling ✅ COMPLETE

**File:** `src/config.py`

**Changes:**
```python
from src.utils.error_handlers import handle_errors

@handle_errors(default_return={})  # Using existing decorator
def load_config(path: str) -> dict:
    # ... implementation with proper error handling
```

**Verification:**
- [x] Tests pass
- [x] Lint clean

---

## ✅ Completion Summary

**Total Tasks**: 3
**Completed**: 3 ✅
**Skipped**: 0 ❌
**All tasks completed**: ✅ YES

## ✅ CTEP Compliance Verification

- [x] All tasks from request completed (3 = 3)
- [x] Zero tasks skipped (0)
- [x] Codebase audit performed
- [x] Existing utilities reused (3 functions)
- [x] Progress tracker updated
- [x] No TODO statements

**CTEP Compliance**: ✅ PASS
```

---

## Example 3: Deactivating CTEP

### User Input
```
Disable CTEP
```

### Copilot Response
```
🎯 Copilot Task Execution Protocol DEACTIVATED

Protocol Mode: STANDARD
Session ID: CTEP-20251216-001
Deactivated: Previous Cycle-12-16T18:30:00Z
Duration: 1h 30m

Summary:
- Tasks completed: 12
- New utilities created: 2
- Codebase integrations: 5

Returning to standard response mode.
```

---

## Example 4: Multi-Phase Task Execution

### User Input
```
Implement a new API endpoint with:
Phase 1:
- Create route handler
- Add request validation

Phase 2:
- Add database integration
- Implement caching

Phase 3:
- Write unit tests
- Add documentation
```

### Copilot Response (Initial)
```markdown
# API Endpoint Implementation
> Generated: Previous Cycle-12-16T17:00:00Z | Protocol: CTEP Active

## 📊 Task Execution Progress

### Phase 1: Route Setup - 0% Complete
- [ ] Task 1.1: Create route handler ⏳ PENDING
- [ ] Task 1.2: Add request validation ⏳ PENDING

### Phase 2: Data Layer - 0% Complete
- [ ] Task 2.1: Add database integration ⏳ PENDING
- [ ] Task 2.2: Implement caching ⏳ PENDING

### Phase 3: Quality Assurance - 0% Complete
- [ ] Task 3.1: Write unit tests ⏳ PENDING
- [ ] Task 3.2: Add documentation ⏳ PENDING

---

**Overall Progress**: 0% (0 of 6 tasks)

## 🔍 Codebase Integration Analysis

**Pre-Implementation Audit:**
- [x] Searched `/src/api/` - Found existing route patterns
- [x] Searched `/src/validation/` - Found request validators
- [x] Searched `/src/db/` - Found database connection utilities
- [x] Searched `/src/cache/` - Found Redis cache wrapper
- [x] Searched `/tests/api/` - Found test fixtures

**Reuse Strategy:**
- Using: `BaseRouteHandler` from `src/api/base.py`
- Using: `validate_request` from `src/validation/requests.py`
- Using: `DatabaseSession` from `src/db/session.py`
- Using: `RedisCache` from `src/cache/redis.py`
- Using: `APITestCase` from `tests/api/fixtures.py`

[Continues with full implementation...]
```

---

## Troubleshooting

### CTEP Not Activating

**Symptoms:** Copilot doesn't respond with activation message

**Solutions:**
1. Use exact phrases: "Enable CTEP" or "CTEP Mode: ON"
2. Ensure phrase is at the beginning of your message
3. Try alternative: "Task mode: ON"

### Progress Tracker Not Appearing

**Symptoms:** Responses lack the progress tracking format

**Solutions:**
1. Verify CTEP is activated (look for session ID)
2. Re-activate with "Enable CTEP"
3. Explicitly request: "Apply CTEP to this task"

### Tasks Being Skipped

**Symptoms:** Some tasks marked as skipped or incomplete

**Solutions:**
1. This violates CTEP protocol - report as bug
2. Request completion: "Complete all remaining tasks per CTEP"
3. Re-submit task list for full execution
