# WEC Core Workflows: Configuration Analysis
## Detailed Compliance Matrix

### Summary Table

| # | Workflow Name | File Status | Triggers | Timeout | Concurrency | Skip Cond | WEC Required | Status |
|----|---------------|-------------|----------|---------|-------------|-----------|--------------|--------|
| 1 | pre-merge-validation.yml | ✅ Active | PR, Review, Dispatch | ✅ 60m | ✅ Branched | None | Always | ✅ PASS |
| 2 | comment-review-gate.yml | ✅ Active | PR, Review, Comment | ✅ Default | ✅ Branched | PR!=5328 | Always | ⚠️ WARN |
| 3 | deferral-language-gate.yml | ✅ Active | PR | ✅ Default | ✅ Branched | PR!=5328 | Always | ⚠️ WARN |
| 4 | agent-auth-delegation.yml | ✅ Active | PR, Review, Dispatch | ✅ Default | ✅ Branched | None | Always | ✅ PASS |
| 5 | workflow-execution-gate.yml | ✅ Active | Dispatch only | ✅ 10m | ✅ Branched | event==dispatch | Always | ❌ FAIL |
| 6 | copilot-agent-checkin.yml | ❌ ARCHIVED | N/A | N/A | N/A | N/A | Always | ❌ FAIL |
| 7 | cost-gate.yml | ✅ Active | workflow_call | ✅ Default | ✅ Branched | PR!=5328 | Always | ⚠️ WARN |
| 8 | copilot-agent-session-done.yml | ❌ MISSING | N/A | N/A | N/A | N/A | Always | ❌ FAIL |
| 9 | copilot-iterative-self-healing.yml | ❌ MISSING | N/A | N/A | N/A | N/A | Optional | ❌ FAIL |

### Legend
- ✅ PASS: Compliant, no issues
- ⚠️ WARN: Compliant but has hardcoded PR exclusion (needs fixing)
- ❌ FAIL: Critical issue preventing WEC enforcement

---

## Workflow-by-Workflow Details

### 1. ✅ pre-merge-validation.yml

```yaml
name: Pre-Merge Validation
on:
  pull_request: [opened, synchronize, reopened, ready_for_review]
  pull_request_review: [submitted]
  workflow_dispatch: null

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  final-validation:
    timeout-minutes: 60
    if: github.event.pull_request.draft == false
```

**Status**: ✅ **PASS — Fully Compliant**
- Triggers on all expected events
- Proper branch-scoped concurrency
- Explicit timeout-minutes: 60
- No skip conditions or hardcoded PR exclusions
- **Assessment**: Ready for WEC enforcement

---

### 2. ⚠️ comment-review-gate.yml

```yaml
name: PR Comment Review Gate
on:
  pull_request: [opened, synchronize, reopened, ready_for_review]
  pull_request_review: [submitted]
  issue_comment: [created]

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  scan-and-post:
    if: >
      github.event.pull_request.number != 5328 &&
      (github.event_name == 'pull_request' || ...)
```

**Status**: ⚠️ **WARN — Hardcoded PR Exclusion**
- Triggers on all expected events ✅
- Proper concurrency ✅
- **Issue**: Hardcoded exclusion for PR #5328
- **Impact**: This is a CORE WEC workflow; should not have PR-specific exclusions
- **Action Required**: Remove hardcoded PR number check
- **Why it exists**: Likely temporary workaround during WEC testing

---

### 3. ⚠️ deferral-language-gate.yml

```yaml
name: 🚨 Deferral Language Gate
on:
  pull_request: [opened, synchronize, reopened]

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  deferral-language-check:
    if: ${{ github.event.pull_request.number != 5328 }}
```

**Status**: ⚠️ **WARN — Hardcoded PR Exclusion**
- Triggers correctly ✅
- Proper concurrency ✅
- **Issue**: Hardcoded exclusion for PR #5328 (same as comment-review-gate)
- **Impact**: Core WEC workflow should not have PR-specific skip conditions
- **Action Required**: Remove `if: github.event.pull_request.number != 5328`

---

### 4. ✅ agent-auth-delegation.yml

```yaml
name: Agent Token Delegation
on:
  pull_request: [opened, edited, reopened, ready_for_review, closed]
  pull_request_review: [submitted]
  workflow_dispatch:
    inputs:
      pr_number: {required: true, type: number}

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  pr-body-checkpoint-guardian:
    if: github.event_name == 'pull_request' && github.event.action != 'closed'
```

**Status**: ✅ **PASS — Fully Compliant**
- Comprehensive trigger coverage ✅
- Proper concurrency ✅
- Contextual skip condition (event type checking) ✅
- No hardcoded PR exclusions ✅
- **Assessment**: Ready for WEC enforcement

---

### 5. ❌ workflow-execution-gate.yml

```yaml
name: Workflow Execution Gate
on:
  workflow_dispatch:
    inputs:
      pr_number: {required: true, type: number}
      verbose_mode: {type: boolean, default: false}

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: false

jobs:
  gate-check:
    timeout-minutes: 10
    if: ${{ github.event_name == 'workflow_dispatch' }}
```

**Status**: ❌ **FAIL — Critical Issue**
- **Problem**: Only triggers on `workflow_dispatch`, NOT on PR events
- **Impact**: WEC gate does NOT automatically validate when PR is opened/pushed
- **Current Behavior**: Must be manually triggered via workflow_dispatch input
- **Expected Behavior**: Should trigger on `pull_request: [opened, synchronize]`
- **Implementation Blocker**: This is THE GATE that should parse WEC checklist
- **Action Required**: Add PR trigger

**Recommended Fix**:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      pr_number: {required: true, type: number}
```

---

### 6. ❌ copilot-agent-checkin.yml

```
File: .github/workflows/_archived/copilot-agent-checkin.yml.archived
Status: ARCHIVED
```

**Status**: ❌ **FAIL — Archived/Missing**
- **Problem**: Workflow archived but still listed in `_WEC_ITEMS`
- **Location**: `.github/workflows/_archived/copilot-agent-checkin.yml.archived`
- **WEC Status**: Listed as `always_required=True`
- **Impact**: WEC validation will fail with "missing workflow"
- **Decision Needed**: 
  - Option A: Restore workflow to active
  - Option B: Remove from `_WEC_ITEMS` list in session_wrapup_autofix.py
- **Action Required**: Immediate decision

---

### 7. ⚠️ cost-gate.yml

```yaml
name: 💰 Cost Gate
on:
  workflow_call:
    inputs:
      workflow_name: {required: true, type: string}
      runner: {required: false, default: 'ubuntu-latest', type: string}
      # ... more inputs

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  estimate:
    if: ${{ github.event.pull_request.number != 5328 }}
```

**Status**: ⚠️ **WARN — Hardcoded PR Exclusion + Wrong Trigger**
- **Trigger Issue**: `on: [workflow_call]` only (reusable workflow)
  - Cannot trigger directly from PR
  - Only callable from other workflows (agent-auth-delegation calls it)
- **Skip Condition Issue**: Has hardcoded PR #5328 exclusion
- **Concurrency Issue**: Using PR context in concurrency group, but may not exist
- **Impact**: Partial WEC compliance
- **Action Required**: 
  1. Remove hardcoded PR number check
  2. Verify reusable workflow pattern is correct
  3. Document that cost-gate only runs when called by agent-auth-delegation

---

### 8. ❌ copilot-agent-session-done.yml

```
File: MISSING (not found in .github/workflows/)
Status: NOT FOUND
```

**Status**: ❌ **FAIL — Missing Workflow**
- **Problem**: Workflow referenced in `_WEC_ITEMS` but doesn't exist
- **Listed in**: `session_wrapup_autofix.py` line 107
- **WEC Status**: `always_required=False` (so won't hard-block, but may confuse)
- **Impact**: Medium — Listed in checklist but can't be executed
- **Decision Needed**:
  - Option A: Create the workflow
  - Option B: Remove from `_WEC_ITEMS`
  - Option C: Rename existing similar workflow
- **Action Required**: Clarify intent

---

### 9. ❌ copilot-iterative-self-healing.yml

```
File: MISSING (exact name not found)
File Found: .github/workflows/iterative-self-healing-ci.yml (similar name)
Status: NAME MISMATCH
```

**Status**: ❌ **FAIL — Naming Mismatch**
- **Expected**: `copilot-iterative-self-healing.yml`
- **Found**: `iterative-self-healing-ci.yml`
- **Listed in**: `session_wrapup_autofix.py` line 108
- **WEC Status**: `always_required=False` (so won't hard-block)
- **Impact**: Low — Won't fail validation but may confuse WEC checklist
- **Action Required**: Align naming or clarify in documentation

---

## Auto-Approve Workflows Routing

### auto-approve-workflows.yml (Not in Core 8/9)

```yaml
name: ⚡ Auto-Approve Pending Workflow Runs
on:
  push:
    branches: [copilot/**, feature/**]
  workflow_run:
    workflows:
      - Copilot coding agent
      - 🔄 Auto-Post @copilot review After Agent Session
    types: [requested, in_progress, completed]
  pull_request: [synchronize, opened, reopened, ready_for_review]
  pull_request_review: [submitted]
  schedule: [cron: '*/5 * * * *']
  workflow_dispatch:
    inputs:
      approval_source: {choice: [trigger-on-approval, self-approve, agent-auth, ...]}
      approval_intent: {choice: [auto_approve_action_required, conditional_approve, ...]}
```

**Status**: Not a core WEC workflow (supporting infrastructure)
- Handles approval logic
- Responds to labels: `wec:auto-approve`, `wec:auto-approve-once`
- Filters based on approval rules
- **Issue**: Does NOT filter queue to 8-9 workflows (approves all matching criteria)

---

## Workflow Queue Filtering — ROOT CAUSE ANALYSIS

### Problem: 105+ Workflows in Queue (Not 8-9)

**Why is the queue so large?**

1. **No WEC-based filtering in approval logic**
   - `approve_pending_runs.py` doesn't check WEC state
   - Approves based on labels/rules, not workflow whitelist

2. **46 workflows with hardcoded PR #5328 exclusions**
   - These are skipped only for that ONE PR
   - Not applicable to PR #5337

3. **Missing approval queue filter logic**
   - No mechanism to say "only approve these 8-9 workflows"
   - Every workflow that matches approval criteria gets approved

4. **Stub WEC enforcement gate**
   - Doesn't parse PR body checklist
   - Doesn't extract approved workflow list
   - Doesn't dispatch approval filtering

### Solution: Implement WEC-Based Queue Filtering

```python
# In approve_pending_runs.py

CORE_WEC_WORKFLOWS = {
    "pre-merge-validation",
    "comment-review-gate",
    "deferral-language-gate",
    "agent-auth-delegation",
    "workflow-execution-gate",
    "cost-gate",
    # + 2-3 more if user includes auto-approve in core set
}

def get_wec_approved_workflows(pr_number: int) -> set[str]:
    """
    Parse PR body checklist to get approved workflows.
    Return set of workflow names user checked in WEC.
    """
    pr = gh.get_pr(pr_number)
    
    # Look for WEC section in PR body
    wec_section = extract_wec_section(pr.body)
    
    # Parse checked items
    approved = set()
    for line in wec_section.split('\n'):
        if '- [x]' in line:  # checked item
            workflow_name = extract_workflow_name(line)
            approved.add(workflow_name)
    
    return approved

def should_approve_run(run, pr_number: int, wec_auto_approve_label: bool) -> bool:
    """
    Determine if workflow run should be approved.
    
    Logic:
    1. If wec:auto-approve label: only approve CORE workflows
    2. Otherwise: only approve if explicitly checked in WEC
    """
    
    # Not a core workflow? Skip it
    if run.name not in CORE_WEC_WORKFLOWS:
        return False
    
    # If using persistent auto-approve label: approve core workflows
    if wec_auto_approve_label:
        return True
    
    # Otherwise: only approve if explicitly checked in WEC
    approved = get_wec_approved_workflows(pr_number)
    return run.name in approved
```

---

## Implementation Priority

### 🔴 CRITICAL (Block PR #5337)
1. Fix `workflow-execution-gate.yml` trigger (add PR events)
2. Implement WEC checklist parsing in enforcement gate
3. Implement queue filtering in approve_pending_runs.py

### 🟠 HIGH (Block merge)
4. Restore/remove `copilot-agent-checkin.yml`
5. Clarify/remove `copilot-agent-session-done.yml`
6. Remove hardcoded PR exclusions from 3 CORE workflows

### 🟡 MEDIUM (Follow-up PR)
7. Align `copilot-iterative-self-healing.yml` naming
8. Add PR trigger documentation
9. Create WEC audit dashboard

---

## Validation Results Summary

```
🔴 CRITICAL: 3 issues blocking WEC enforcement
   ❌ workflow-execution-gate.yml only on manual trigger
   ❌ Archived copilot-agent-checkin.yml
   ❌ Queue filtering logic missing

🟠 HIGH: 4 issues requiring fixes
   ⚠️  3 CORE workflows with hardcoded PR exclusions
   ❌ Missing copilot-agent-session-done.yml

🟡 MEDIUM: 2 issues for follow-up
   ❌ Mismatched copilot-iterative-self-healing.yml naming
   ℹ️  Documentation clarification needed

✅ PASS: 3 workflows fully compliant
   ✅ pre-merge-validation.yml
   ✅ agent-auth-delegation.yml
   ✅ (will be 4 after removing PR exclusions)
```

---

**Overall Assessment**: ❌ **NOT READY FOR PRODUCTION**
- Too many critical issues
- Approval queue at 13x target size (105 vs 8-9)
- Need 24-48 hours to fix all issues

