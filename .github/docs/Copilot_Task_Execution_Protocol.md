# Copilot Task Execution Protocol (CTEP)

> **Version:** 2.0.0
> **Created:** 2025-12-16  
> **Purpose:** Comprehensive task completion protocol for GitHub Copilot

---

## Overview

CTEP is optional task accounting when requested, not a guarantee that every task
can be completed. It follows the [current agency policy](../../.codex/CODEBASE_AGENCY_POLICY.md).
Enabling tracking does not grant authorization or independent approval.

- **No silent omissions** - Account for completed, blocked, deferred and pending tasks
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

✅ Account for all tasks; complete authorized work
📊 Maintain live progress tracker
🔍 Codebase-first approach - search before creating
🧰 Document all new utilities with integration plans
🔄 Update progress after each task completion
✅ Final verification: Total = Completed + Blocked + Deferred + Pending

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
**Completed**: C
**Blocked**: B
**Deferred**: D
**Pending**: P
**Accounting**: X = C + B + D + P
**Acceptance**: [actual evidence-supported status]

## ✅ CTEP Compliance Verification

- [ ] Every task has exactly one current state and supporting evidence
- [ ] Incomplete tasks retain proposed owner, reason and next action
- [x] Codebase audit performed
- [x] Existing utilities reused where applicable
- [x] Progress tracker maintained
- [ ] Required controls and unresolved acceptance gaps reported

**CTEP tracking**: [actual accounting status; not task acceptance or approval]
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
    "blocked_tasks": 0,
    "deferred_tasks": 0,
    "pending_tasks": 0,
    "new_utilities": [],
    "codebase_audits": [],
    "phases": []
}
```

---

## Prohibited Actions During CTEP

1. ❌ Silently omitting tasks or marking blocked/deferred/pending work complete
2. ❌ Bypassing read-only boundaries, required security owner/reason classification
   or actual review/execution approvals to force completion
3. ❌ Creating duplicate utilities when existing ones suffice
4. ❌ Omitting progress updates
5. ❌ Claiming unperformed verification or approval

Blocked/deferred/pending tasks are incomplete, not failed accounting. Record the
evidence, impact, proposed owner and next action; continue unaffected authorized
work. Read-only tasks permit inspection/reporting only, not edits or session
dispatch. Missing optional memory or specialists is not a startup gate: use
direct execution where authorized. At a resource ceiling, stop the affected
action safely and preserve state. Publication, merges, protected settings and
governance activation still require applicable authorization.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  CTEP ACTIVE - COMPREHENSIVE TASK COMPLETION MODE           │
├─────────────────────────────────────────────────────────────┤
│  ✅ Account for all tasks; respect task authority             │
│  📊 Live progress tracker required                          │
│  🔍 Codebase audit before new code                          │
│  🧰 Document all new utilities                              │
│  🔄 Update after each task                                  │
│  ✅ Total = Completed + Blocked + Deferred + Pending          │
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
