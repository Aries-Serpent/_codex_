# Copilot Task Execution Protocol (CTEP)

> **Version:** 1.0.0  
> **Created:** 2025-12-16  
> **Purpose:** Comprehensive task completion protocol for GitHub Copilot

---

## Overview

The Copilot Task Execution Protocol (CTEP) is a structured approach to ensure comprehensive task completion. When activated, Copilot operates in a mode that guarantees:

- **Zero task omissions** - All tasks are completed, no exceptions
- **Live progress tracking** - Real-time status updates
- **Codebase-first approach** - Search existing utilities before creating new ones
- **Full documentation** - All new utilities are documented with integration plans

---

## Activation Commands

CTEP can be activated using any of the following phrases:

- `Enable CTEP`
- `CTEP Mode: ON`
- `Task mode: ON`
- `Activate Task Execution Protocol`
- `Apply Copilot Task Execution Protocol`

### Activation Response

When activated, Copilot will respond with:

```
🎯 Copilot Task Execution Protocol ACTIVATED

Protocol Mode: COMPREHENSIVE TASK COMPLETION
Session ID: CTEP-[YYYYMMDD]-[XXX]
Activated: [timestamp]

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

## Deactivation Commands

CTEP can be deactivated using:

- `Disable CTEP`
- `CTEP Mode: OFF`
- `Exit Task mode`
- `Deactivate CTEP`

### Deactivation Response

```
🎯 Copilot Task Execution Protocol DEACTIVATED

Protocol Mode: STANDARD
Session ID: [same ID]
Deactivated: [timestamp]
Duration: [time in CTEP mode]

Summary:
- Tasks completed: [count]
- New utilities created: [count]
- Codebase integrations: [count]

Returning to standard response mode.
```

---

## Protocol Behavior

### 1. Task Inventory

When receiving tasks, CTEP requires:

```markdown
## 📊 Task Execution Progress

### Phase 1: [Phase Name] - X% Complete
- [ ] Task 1.1: [Description] ⏳ PENDING
- [ ] Task 1.2: [Description] ⏳ PENDING
- [x] Task 1.3: [Description] ✅ COMPLETE

### Phase 2: [Phase Name] - X% Complete
- [ ] Task 2.1: [Description] ⏳ PENDING
```

### 2. Codebase Audit

Before creating new code, search for existing utilities:

```markdown
## 🔍 Codebase Integration Analysis

**Pre-Implementation Audit:**
- [x] Searched `/src/utils/` - Found `validation.py` with reusable validators
- [x] Searched `/src/common/` - Found `logger_config.py` with standard setup
- [x] Searched error handling patterns - Found `error_handlers.py` decorator

**Reuse Strategy:**
- Using: `validate_config()` from `src/utils/validation.py`
- Creating: New `config_parser.py` (no existing equivalent found)
```

### 3. Progress Updates

After each task completion:

```markdown
#### Task X.X: [Name] ✅ COMPLETE

**Implementation:**
- File: `path/to/file.py`
- Changes: [description]
- Integration: [how it connects to existing code]

**Verification:**
- [x] Tests pass
- [x] Lint clean
- [x] Documentation updated
```

### 4. Completion Summary

Final response must include:

```markdown
## ✅ Completion Summary

**Total Tasks**: X
**Completed**: X ✅
**Skipped**: 0 ❌
**All tasks completed**: ✅ YES

## ✅ CTEP Compliance Verification

- [x] All tasks from request completed (X = X)
- [x] Zero tasks skipped (0)
- [x] Codebase audit performed
- [x] Existing utilities reused where applicable
- [x] Progress tracker maintained
- [x] No TODO statements left

**CTEP Compliance**: ✅ PASS
```

---

## Session State Tracking

CTEP maintains the following state during a session:

```python
ctep_session = {
    "active": True,
    "session_id": "CTEP-20251216-001",
    "activated_at": "2025-12-16T17:00:00Z",
    "total_tasks": 0,
    "completed_tasks": 0,
    "skipped_tasks": 0,  # Must remain 0
    "new_utilities": [],
    "codebase_audits": [],
    "phases": []
}
```

---

## Prohibited Actions During CTEP

1. ❌ Skipping tasks without explicit user approval
2. ❌ Leaving TODO comments for future implementation
3. ❌ Creating duplicate utilities when existing ones suffice
4. ❌ Omitting progress updates
5. ❌ Incomplete verification checklists

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  CTEP ACTIVE - COMPREHENSIVE TASK COMPLETION MODE           │
├─────────────────────────────────────────────────────────────┤
│  ✅ Complete ALL tasks - no exceptions                      │
│  📊 Live progress tracker required                          │
│  🔍 Codebase audit before new code                          │
│  🧰 Document all new utilities                              │
│  🔄 Update after each task                                  │
│  ✅ Verify: Completed = Total, Skipped = 0                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [CTEP Usage Examples](./CTEP_Usage_Examples.md)
- [CTEP Quick Reference](./CTEP_Quick_Reference.md)
- [Copilot Instructions](../copilot-instructions.md)

---

## Changelog

### v1.0.0 (2025-12-16)
- Initial CTEP specification
- Activation/deactivation commands defined
- Progress tracking format established
- Codebase audit requirements documented
