# WEC Enforcement for PR #5337: Executive Action Plan
## Immediate Remediation Steps

**Report Date**: 2026-07-18  
**Scope**: PR #5337 with `wec:auto-approve` label  
**Current Issue**: 105+ workflows in approval queue vs 8-9 target  
**Compliance**: 34% (3 of 9 core workflows compliant)

---

## 🚨 Critical Blockers (MUST FIX BEFORE MERGE)

### Blocker #1: workflow-execution-gate.yml — No PR Event Trigger
**File**: `.github/workflows/workflow-execution-gate.yml`  
**Severity**: CRITICAL  
**Time to Fix**: 5 minutes

**Current**:
```yaml
on:
  workflow_dispatch:
    inputs:
      pr_number: ...
```

**Required Change**:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      pr_number: ...
```

**Why**: Without PR trigger, WEC gate never validates PR body checklist automatically.

---

### Blocker #2: Approval Queue Filtering Missing
**Files**: `scripts/ci/approve_pending_runs.py` + `scripts/ci/wec_enforcer.py`  
**Severity**: CRITICAL  
**Time to Fix**: 30-45 minutes

**Current State**:
- Approves all workflows matching label criteria
- No WEC-based filtering

**Required Implementation**:
1. Parse PR body for WEC checklist section
2. Extract approved workflow names (checked items)
3. Filter approval queue to only core workflows
4. Only approve workflows in: `pre-merge-validation`, `comment-review-gate`, `deferral-language-gate`, `agent-auth-delegation`, `cost-gate`

**Pseudo-code**:
```python
def should_approve_run(workflow_name, pr_number, has_wec_label):
    CORE_WORKFLOWS = {
        "pre-merge-validation",
        "comment-review-gate",
        "deferral-language-gate",
        "agent-auth-delegation",
        "cost-gate",
    }
    
    # Not a core workflow? Block it
    if workflow_name not in CORE_WORKFLOWS:
        return False
    
    # If wec:auto-approve label: approve all core
    if has_wec_label:
        return True
    
    # Otherwise: only if explicitly checked in WEC
    return is_checked_in_wec(pr_number, workflow_name)
```

---

### Blocker #3: Archived copilot-agent-checkin.yml
**File**: `.github/workflows/_archived/copilot-agent-checkin.yml.archived`  
**Severity**: CRITICAL  
**Time to Fix**: Depends on decision (5-30 mins)

**Decision Required**: 2 Options
1. **OPTION A**: Restore to active
   - Move from `_archived/` to `.github/workflows/`
   - Time: 2 minutes
   
2. **OPTION B**: Remove from WEC
   - Edit `scripts/ci/session_wrapup_autofix.py`
   - Remove copilot-agent-checkin.yml from `_WEC_ITEMS`
   - Time: 3 minutes

**Recommendation**: OPTION B is simpler if workflow is truly no longer needed.

---

## 🟠 High Priority Fixes (SHOULD FIX BEFORE MERGE)

### Fix #1: Remove 3 Hardcoded PR Exclusions
**Files**:
- `.github/workflows/comment-review-gate.yml`
- `.github/workflows/deferral-language-gate.yml`
- `.github/workflows/cost-gate.yml`

**Severity**: HIGH  
**Time to Fix**: 10 minutes (3 files)

**Current** (all three have same pattern):
```yaml
if: github.event.pull_request.number != 5328 && ...
```

**Change To**:
```yaml
if: |
  (github.event_name == 'pull_request' || ...) && ...
```

Or simply remove the PR number check entirely if contextual checks are sufficient.

---

### Fix #2: Clarify/Remove Missing Workflows
**Files**: `scripts/ci/session_wrapup_autofix.py`  
**Severity**: HIGH  
**Time to Fix**: 15 minutes

**Missing Workflows**:
1. `copilot-agent-session-done.yml` - NOT FOUND
2. `copilot-iterative-self-healing.yml` - NAME MISMATCH (found as `iterative-self-healing-ci.yml`)

**Actions**:
- [ ] Line 107: Decide on copilot-agent-session-done.yml
  - Create it? Remove from list? Rename something?
- [ ] Line 108: Rename to match actual filename OR create missing file

---

## 🟡 Medium Priority (FOLLOW-UP PR)

### Polish #1: WEC Gate Implementation
**File**: `.github/workflows/wec-enforcement-gate.yml`  
**Current**: Just echoes "passed"  
**Needed**: Actual WEC parsing and validation

### Polish #2: Remove Hardcoded PR Exclusions Repo-Wide
**Current**: 46 workflows with PR #5328 exclusion  
**Action**: Replace with dynamic WEC-based skip conditions

### Polish #3: Workflow Consolidation
**Current**: 219 active workflows  
**Target**: 50-80 (reduce approval noise)

---

## Implementation Checklist

```markdown
## 🔄 Workflow Execution Checklist

### BLOCKER FIXES (24 hours)
- [ ] Add PR trigger to workflow-execution-gate.yml
- [ ] Implement WEC-based queue filtering in approve_pending_runs.py
- [ ] Restore/remove copilot-agent-checkin.yml

### HIGH PRIORITY FIXES (24-48 hours)
- [ ] Remove 3 hardcoded PR number exclusions
  - [ ] comment-review-gate.yml
  - [ ] deferral-language-gate.yml
  - [ ] cost-gate.yml
- [ ] Fix missing workflows in session_wrapup_autofix.py
  - [ ] copilot-agent-session-done.yml
  - [ ] copilot-iterative-self-healing.yml naming

### VALIDATION
- [ ] Test PR #5337 with wec:auto-approve label
- [ ] Verify only 8-9 workflows in approval queue (not 105+)
- [ ] Verify WEC gate parses checklist correctly
- [ ] Run 5-pass self-review validation

### POST-MERGE (Follow-up PR)
- [ ] Update WEC enforcement gate with full logic
- [ ] Replace 46 hardcoded PR exclusions
- [ ] Create WEC audit dashboard
- [ ] Document WEC requirements
```

---

## Expected Outcomes After Fixes

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Workflows awaiting approval | 105+ | 8-9 | ✅ 8-9 |
| Core WEC compliance | 34% (3/9) | 100% (9/9) | ✅ 100% |
| Hardcoded PR exclusions | 46 | 0* | ✅ 0 |
| Approval gate functional | ❌ NO | ✅ YES | ✅ YES |

*After removal in follow-up PR

---

## Success Criteria

PR #5337 is ready to merge when:

1. ✅ All 9 core WEC workflows exist (not archived/missing)
2. ✅ 3 hardcoded PR exclusions removed
3. ✅ workflow-execution-gate.yml fires on PR events
4. ✅ Approval queue filtering implemented
5. ✅ Test run shows 8-9 workflows queued (not 105+)
6. ✅ WEC checklist parsing works end-to-end
7. ✅ PR #5337 successfully merges with `wec:auto-approve` label

---

## Risk Assessment

| Risk | Current | After Fixes | Mitigation |
|------|---------|------------|-----------|
| Approval queue too large | 🔴 Critical | ✅ Resolved | Filtering implementation |
| Archived workflows fail | 🔴 Critical | ✅ Resolved | Restore or remove |
| Manual trigger needed | 🟠 High | ✅ Resolved | Add PR trigger |
| Hardcoded exclusions | 🟠 High | ⚠️ Partial | Remove + document |
| Missing WEC items | 🟡 Medium | ✅ Resolved | Clarify/create |

---

**Estimated Time to Fix All Blockers**: 1-2 hours  
**Estimated Time for Testing**: 30 minutes  
**Total**: 2-3 hours before PR #5337 can safely merge

