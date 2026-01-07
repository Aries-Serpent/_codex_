# Continuation Prompt Template

This template helps maintain context when token limits force multi-iteration work.

---

## 📋 Quick Copy-Paste Format

```markdown
Continue from ITERATION [N+1]:

**Context**: [One sentence: what is the overall goal?]

**Last Completed**: [What did you just finish?]

**Remaining Work**:
1. [First remaining task]
2. [Second remaining task]
3. [etc.]

**Files Modified So Far**:
- file1.py (added X lines)
- file2.md (created)

**Token Usage Check**: ⚠️ [Current iteration used ~X% of 64k limit]

**Resume Instructions**:
- Start immediately with implementation
- No questions, no explanations
- Execute all code directly
- End with continuation prompt if >60k tokens used
- Confirm "✅ ITERATION [N+1] COMPLETE" when done

**EXECUTE NOW.**
```

---

## 📝 Detailed Template (Use for Complex Tasks)

### Iteration N Status Report

**Iteration Number**: [e.g., 3 of 5 estimated]
**Date/Time**: [ISO 8601 timestamp]
**PR/Branch**: [e.g., PR #2601, branch `0D_base_`]
**Overall Goal**: [Brief description]

---

### ✅ Completed This Iteration

<details>
<summary>Click to expand completed work</summary>

#### Files Created
- [ ] `path/to/file1.py` - [Purpose]
- [ ] `path/to/file2.md` - [Purpose]

#### Files Modified
- [ ] `path/to/existing.py` (lines 10-50) - [What changed]
- [ ] `path/to/config.yaml` (added section X) - [What changed]

#### Tests Added/Updated
- [ ] `tests/test_feature.py` - [What's covered]

#### Documentation Updates
- [ ] Updated `README.md` - [What's new]
- [ ] Created `.github/POLICY.md` - [Purpose]

#### Verification Steps Completed
- [ ] Tests pass: `pytest tests/security -v` ✅
- [ ] Linting: `ruff check --fix` ✅
- [ ] Type checking: `mypy src/` ✅

</details>

---

### ⏳ Remaining Work

<details>
<summary>Click to expand remaining tasks</summary>

**Priority 1 (Must Complete):**
- [ ] Task A - [Description]
- [ ] Task B - [Description]

**Priority 2 (Should Complete):**
- [ ] Task C - [Description]

**Priority 3 (Nice to Have):**
- [ ] Task D - [Description]

**Blocked/Deferred:**
- [ ] Task E - [Reason for deferral]

</details>

---

### 📊 Progress Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Files Created | X | 🟢 On Track |
| Files Modified | Y | 🟢 On Track |
| Tests Added | Z | 🟡 In Progress |
| Documentation Updated | A | 🟢 Complete |
| Security Alerts Resolved | B | 🔴 Needs Attention |
| Token Usage (This Iteration) | ~X% of 64k | ⚠️ Approaching Limit |

**Legend:**
- 🟢 Complete or on track
- 🟡 In progress
- 🔴 Blocked or needs attention
- ⚠️ Warning threshold

---

### 🔄 Continuation Checkpoint

**Token Limit Strategy:**
- [ ] Current iteration: ~X tokens used (Y% of 64k limit)
- [ ] Estimated remaining: ~Z tokens needed
- [ ] **Action**: ⚠️ If >60% used, create continuation prompt
- [ ] **Commit Early**: Push progress every 50% to avoid loss

**When to Create Continuation Prompt:**
- ✅ After completing a major task (good stopping point)
- ✅ When token usage >60% of limit
- ✅ Before starting complex implementation (>5 files)
- ❌ In the middle of a logical unit of work

---

## 🎯 Handoff Instructions (For Next Iteration)

### Context Summary
```markdown
**What We're Building**: [One paragraph summary]

**Why This Matters**: [Business/technical justification]

**Current Status**: [Where we are in the overall plan]
```

### Critical Information
- **Base Commit**: `[commit SHA]`
- **Working Branch**: `[branch name]`
- **Dependencies**: [Any external factors]
- **Known Issues**: [Anything the next iteration needs to watch for]

### Next Steps
1. [First thing to do]
2. [Second thing to do]
3. [Continue until complete]

---

## 📌 Example Filled Template

### Iteration 2 Status Report

**Iteration Number**: 2 of 3 estimated
**Date/Time**: 2025-12-23T21:00:00Z
**PR/Branch**: PR #2601, branch `copilot/fix-security-alert-url-sanitization`
**Overall Goal**: Fix HIGH severity security alert and document duplicate files

---

### ✅ Completed This Iteration

<details>
<summary>Click to expand completed work</summary>

#### Files Created
- [x] `src/codex/security/__init__.py` - Added `sanitize_url()` function
- [x] `.github/DUPLICATE_FILES_POLICY.md` - Documented intentional duplicates
- [x] `.github/CONTINUATION_PROMPT_TEMPLATE.md` - Created this template

#### Files Modified
- [x] `tests/security/test_security_integration.py` (added 85 lines) - Added URL sanitization tests
- [x] `.github/SHIM_INVENTORY.yaml` (updated duplicate_policy) - Added ignore patterns

#### Tests Added/Updated
- [x] `tests/security/test_security_integration.py` - 13 new URL security tests

#### Verification Steps Completed
- [x] Tests pass: `pytest tests/security/test_security_integration.py -v` ✅ 18/18 passed
- [x] Security function works: All real-world attack vectors blocked

</details>

---

### ⏳ Remaining Work

<details>
<summary>Click to expand remaining tasks</summary>

**Priority 1 (Must Complete):**
- [ ] Commit changes with descriptive message
- [ ] Push to remote branch
- [ ] Reply to PR comments explaining fixes

**Priority 2 (Should Complete):**
- [ ] Run full test suite to verify no regressions
- [ ] Update PR description with completion status

**Priority 3 (Nice to Have):**
- [ ] Add security documentation to main SECURITY.md
- [ ] Create example usage in docs/

</details>

---

### 📊 Progress Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Files Created | 3 | 🟢 Complete |
| Files Modified | 2 | 🟢 Complete |
| Tests Added | 13 | 🟢 Complete |
| Documentation Updated | 2 | 🟢 Complete |
| Security Alerts Resolved | 1 HIGH | 🟢 Fixed & Tested |
| Token Usage (This Iteration) | ~45% of 64k | 🟢 Healthy |

---

### 🔄 Continuation Checkpoint

**Token Limit Strategy:**
- [x] Current iteration: ~28k tokens used (45% of 64k limit)
- [x] Estimated remaining: ~5k tokens needed for final steps
- [x] **Action**: ✅ Safe to complete in this iteration
- [x] **Commit**: Ready to commit all changes

**Stopping Point Assessment:**
- ✅ Security fix: Complete
- ✅ Tests: All passing
- ✅ Documentation: Complete
- ✅ No partial work in progress
- **Ready to finalize** ✨

---

### 🎯 Handoff Instructions (For Next Iteration)

Not needed - work can be completed in this iteration.

---

## 🚀 Best Practices

### DO ✅
- Copy-paste the "Quick Copy-Paste Format" to start new iteration
- Update metrics after each major task
- Commit frequently (every 10-20 minutes)
- Leave clear handoff notes
- Test before moving to next iteration

### DON'T ❌
- Wait until 100% token usage to create prompt
- Leave work in partially broken state
- Skip testing before continuation
- Forget to document what's left
- Start new complex task near token limit

---

**Template Version**: 1.0.0
**Last Updated**: 2025-12-23
**Maintained By**: Repository Maintainers
**Related**: `.github/DUPLICATE_FILES_POLICY.md`, `.github/SHIM_INVENTORY.yaml`
