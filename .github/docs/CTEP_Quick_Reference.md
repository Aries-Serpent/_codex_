# CTEP Quick Reference Card

> **Version:** 2.0.0
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
│  ✅ Account for all tasks; respect task authority             │
│  📊 Live progress tracker required                          │
│  🔍 Codebase audit before new code                          │
│  🧰 Document all new utilities                              │
│  🔄 Update after each task                                  │
│  ✅ Total = Completed + Blocked + Deferred + Pending          │
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
**Completed**: C | **Blocked**: B | **Deferred**: D | **Pending**: P
**Accounting**: X = C + B + D + P

**Acceptance**: [actual evidence-supported status, not tracking compliance]
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

- [ ] Every task accounted for, including incomplete work
- [ ] Blocked/deferred/pending tasks have evidence, proposed owner and next action
- [ ] Codebase audit performed
- [ ] Existing utilities reused where applicable
- [ ] Progress tracker maintained
- [ ] Required security owner/reason classification and approvals preserved
- [ ] Verification: `Total = Completed + Blocked + Deferred + Pending`

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

❌ Silently omitting or falsely completing tasks
❌ Bypassing task authority or required controls
❌ Duplicate utilities  
❌ Missing progress updates  
❌ Claiming unperformed verification

Read-only means inspection/reporting only, no edits or session dispatch.
Incomplete tasks remain incomplete; continue unaffected authorized work.
Optional memory/specialists are not gates to direct execution. Resource ceilings
stop affected actions safely. Publication, merges, settings and activation require
applicable authorization. Follow the [current agency policy](../../.codex/CODEBASE_AGENCY_POLICY.md).

---

## Emergency Commands

| Situation | Command |
|-----------|---------|
| Reset progress | "Reset CTEP progress" |
| Review remaining work | "Show incomplete tasks, blockers and next actions" |
| Status check | "Show CTEP session status" |
| Exit immediately | "Disable CTEP" |
