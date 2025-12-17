# CTEP Quick Reference Card

> **Version:** 1.0.0  
> **Full Documentation:** [Copilot_Task_Execution_Protocol.md](./Copilot_Task_Execution_Protocol.md)

---

## Quick Activation

| Command | Action |
|---------|--------|
| `Enable CTEP` | Activate protocol |
| `CTEP Mode: ON` | Activate protocol |
| `Task mode: ON` | Activate protocol |
| `Disable CTEP` | Deactivate protocol |
| `CTEP Mode: OFF` | Deactivate protocol |

---

## Active Mode Indicator

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 CTEP ACTIVE - COMPREHENSIVE TASK COMPLETION MODE        │
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

## Response Structure

### 1. Header
```markdown
# [Task Title]
> Generated: [timestamp] | Protocol: CTEP Active | Status: [status]
```

### 2. Progress Tracker
```markdown
## 📊 Task Execution Progress

### Phase 1: [Name] - X% Complete
- [ ] Task 1.1: [Description] ⏳ PENDING
- [x] Task 1.2: [Description] ✅ COMPLETE
```

### 3. Codebase Audit
```markdown
## 🔍 Codebase Integration Analysis

**Pre-Implementation Audit:**
- [x] Searched [path] - Found [utility]
```

### 4. Implementation
```markdown
## 🛠️ Implementation

#### Task X.X: [Name] ✅ COMPLETE
**File:** [path]
**Changes:** [description]
```

### 5. Completion Summary
```markdown
## ✅ Completion Summary

**Total Tasks**: X
**Completed**: X ✅
**Skipped**: 0 ❌

**CTEP Compliance**: ✅ PASS
```

---

## Status Icons

| Icon | Meaning |
|------|---------|
| ⏳ | PENDING - Not started |
| 🔄 | IN PROGRESS - Currently working |
| ✅ | COMPLETE - Done |
| ❌ | BLOCKED - Needs input |
| ⚠️ | WARNING - Attention needed |

---

## Compliance Checklist

Before completing response:

- [ ] All tasks from request completed
- [ ] Zero tasks skipped
- [ ] Codebase audit performed
- [ ] Existing utilities reused where applicable
- [ ] Progress tracker maintained
- [ ] No TODO statements left
- [ ] Verification: `Completed = Total`

---

## Common Patterns

### Starting a Session
```
User: Enable CTEP
User: [task list]
```

### Mid-Session Check
```
User: Show CTEP status
```

### Ending a Session
```
User: Disable CTEP
```

---

## Prohibited Actions

❌ Skipping tasks  
❌ Leaving TODOs  
❌ Duplicate utilities  
❌ Missing progress updates  
❌ Incomplete verification  

---

## Emergency Commands

| Situation | Command |
|-----------|---------|
| Reset progress | "Reset CTEP progress" |
| Force complete | "Complete all CTEP tasks now" |
| Status check | "Show CTEP session status" |
| Exit immediately | "Disable CTEP" |
