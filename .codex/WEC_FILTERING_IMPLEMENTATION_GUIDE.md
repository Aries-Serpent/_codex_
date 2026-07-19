# WEC Filtering Implementation Guide (BLOCKER 2 & Follow-up)

**Status**: Implementation guidance for PR #5337 follow-up  
**Created**: 2026-07-18  
**Priority**: CRITICAL → HIGH (Phase 2)

---

## Overview

This document provides a complete implementation guide for **BLOCKER 2: Approval Queue Filtering**, which requires the auto-approve-workflows.yml to respect WEC (Workflow Execution Checklist) checkbox state when approving workflows.

**Current State**: 
- ✅ workflow-execution-gate.yml now fires on PR events
- ✅ Archived workflow references fixed in session_wrapup_autofix.py
- ✅ 3 hardcoded PR exclusions removed
- ⏳ **PENDING**: WEC-aware filtering logic in auto-approve-workflows.yml

**Impact**: Without filtering, 105+ workflows get approved instead of 8-9 core workflows.

---

## Problem Statement

### Current Behavior
```yaml
# auto-approve-workflows.yml line 236-241 (Priority 2 rule)
if echo "$LABELS" | grep -q "^wec:auto-approve$"; then
  echo "decision=APPROVE" >> $GITHUB_OUTPUT
  # ⚠️ This approves ALL action_required runs without WEC filtering
fi
```

**Issue**: When `wec:auto-approve` label is set:
1. **ALL** pending workflows get approved (105+)
2. Non-core workflows bypass WEC enforcement
3. Approval queue becomes unmanageable
4. WEC checklist is ignored

### Desired Behavior
```python
# Pseudocode
for workflow in pending_workflows:
    if workflow not in CORE_WEC_WORKFLOWS:
        skip(workflow)
        continue
    
    if has_wec_auto_approve_label:
        approve(workflow)  # Approve all core workflows
    elif is_checked_in_pr_wec(pr_number, workflow):
        approve(workflow)  # Approve only if checked
    else:
        skip(workflow)
```

---

## Core Workflows (WEC Approved Workflows)

These 7 workflows are the only ones approved by WEC:

| Workflow | File | Trigger | Always-Req | Notes |
|----------|------|---------|-----------|-------|
| Pre-Merge Validation | `pre-merge-validation.yml` | pull_request | ✅ Yes | Always required |
| Comment Review Gate | `comment-review-gate.yml` | pull_request | ✅ Yes | Comment analysis |
| Deferral Language Gate | `deferral-language-gate.yml` | pull_request | ✅ Yes | Guard against deferral language |
| Agent Auth Delegation | `agent-auth-delegation.yml` | pull_request | ✅ Yes | Token delegation |
| Workflow Execution Gate | `workflow-execution-gate.yml` | pull_request (NEW) | ✅ Yes | WEC enforcement |
| Copilot Management | `unified-copilot-management.yml` | push/schedule | ✅ Yes | Copilot check-in suite |
| Cost Gate | `cost-gate.yml` | workflow_call | ✅ Yes | Cost governance |

Additional opt-in (if checked in WEC):
- `validate.yml` - Validation pipeline
- `resilient_validation.yml` - Full pytest suite
- `security-scanning-suite.yml` - Security audit
- `reference-integrity.yml` - Reference + agent size

---

## Implementation Path

### Phase 1: Parsing (Parse WEC Checklist from PR Body)

**Goal**: Extract checked workflows from PR body WEC section

**Input**: PR body (from `github.event.pull_request.body`)

**Output**: Set of checked workflow names

**Patterns**:
```
## 🔄 Workflow Execution Checklist

### ALWAYS-REQUIRED (auto-checked)
- [x] pre-merge-validation.yml
- [x] comment-review-gate.yml
- [x] deferral-language-gate.yml
- [x] agent-auth-delegation.yml
- [x] workflow-execution-gate.yml
- [x] unified-copilot-management.yml
- [x] cost-gate.yml

### TESTING & VALIDATION (opt-in)
- [x] validate.yml
- [ ] resilient_validation.yml
```

**Regex Pattern**:
```regex
## 🔄 Workflow Execution Checklist(.*?)(?=##|\Z)  # Find WEC section
- \[x\]\s+([a-z0-9\-_.]+\.ya?ml)                   # Extract checked items
```

### Phase 2: Filtering (Check if Workflow Should Be Approved)

**Decision Tree**:
```python
def should_approve(workflow_name, pr_body, has_label):
    # Rule 1: Non-core workflows NEVER approved
    if not is_core_wec(workflow_name):
        return False
    
    # Rule 2: If label present, approve all core
    if has_label:
        return True
    
    # Rule 3: Check PR body WEC section
    checked = parse_wec(pr_body)
    return workflow_name in checked
```

### Phase 3: Integration Points

Three places need modification:

#### 3a. auto-approve-workflows.yml (Workflow-level)

**File**: `.github/workflows/auto-approve-workflows.yml`  
**Line**: ~650 (github-script action)

**Current**:
```javascript
async function approvePR(prNum, headSha) {
    let allRuns = await listActionRequiredRuns(headSha);
    
    for (const run of allRuns) {
        // ⚠️ Approves ALL runs
        await github.rest.actions.approveWorkflowRun({ owner, repo, run_id: run.id });
    }
}
```

**Required Change**:
```javascript
async function approvePR(prNum, headSha) {
    let allRuns = await listActionRequiredRuns(headSha);
    
    // Get PR body and label info
    const { data: pr } = await github.rest.pulls.get({ owner, repo, pull_number: prNum });
    const prBody = pr.body || '';
    const labels = pr.labels.map(l => l.name);
    const hasLabel = labels.includes('wec:auto-approve');
    
    for (const run of allRuns) {
        // NEW: Filter by WEC rules
        const workflow = run.name;
        if (!shouldApproveWorkflow(workflow, prBody, hasLabel)) {
            core.info(`⏭️  Skipped (not in WEC): ${workflow}`);
            continue;
        }
        
        // ✅ Approve only WEC-approved workflows
        await github.rest.actions.approveWorkflowRun({ owner, repo, run_id: run.id });
    }
}

function shouldApproveWorkflow(workflow, prBody, hasLabel) {
    // Core WEC workflows
    const CORE_WORKFLOWS = [
        "pre-merge-validation",
        "comment-review-gate",
        "deferral-language-gate",
        "agent-auth-delegation",
        "workflow-execution-gate",
        "unified-copilot-management",
        "cost-gate",
    ];
    
    // Check if workflow is core
    const isCore = CORE_WORKFLOWS.some(w => 
        workflow.toLowerCase().includes(w.toLowerCase())
    );
    
    if (!isCore) return false;
    
    // If label present, approve all core
    if (hasLabel) return true;
    
    // Otherwise, check WEC checklist
    const wecSection = prBody.match(/## 🔄 Workflow Execution Checklist(.*?)(?=##|\Z)/is)?.[1] || '';
    const checked = Array.from(wecSection.matchAll(/- \[x\]\s+([a-z0-9\-_.]+\.ya?ml)/gi))
        .map(m => m[1].toLowerCase());
    
    return checked.some(c => workflow.toLowerCase().includes(c.replace('.yml', '')));
}
```

#### 3b. approve_pending_runs.py (Script-level)

**File**: `.scripts/ci/approve_pending_runs.py`  
**Function**: `main()` at line ~350

**Required Addition**:
1. Add PR body fetching:
```python
def _fetch_pr_body(token: str, repo: str, pr_number: str) -> str:
    """Fetch PR body for WEC parsing."""
    status, data = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status == 200 and isinstance(data, dict):
        return data.get("body", "")
    return ""
```

2. Add WEC parsing:
```python
def _parse_wec_checked(pr_body: str) -> set[str]:
    """Parse WEC checklist and return checked workflow names."""
    import re
    wec_match = re.search(
        r'## 🔄 Workflow Execution Checklist(.*?)(?=##|\Z)',
        pr_body, re.DOTALL | re.IGNORECASE
    )
    if not wec_match:
        return set()
    
    checked = re.findall(
        r'- \[x\]\s+([a-z0-9\-_.]+\.ya?ml)',
        wec_match.group(1), re.IGNORECASE
    )
    return {w.lower() for w in checked}
```

3. Add WEC filtering to `_approve_run()`:
```python
def _approve_run(
    token: str, repo: str, run: dict[str, Any], 
    *,
    dry_run: bool = False,
    wec_approved: set[str] = None,  # NEW
    has_label: bool = False,         # NEW
) -> str:
    """Approve or rerun a workflow run.
    
    With WEC filtering, checks if run matches approved workflows.
    """
    # NEW: WEC-based filtering
    if wec_approved is not None:
        workflow_name = run.get("name", "").lower()
        core_workflows = {
            "pre-merge-validation",
            "comment-review-gate",
            "deferral-language-gate",
            "agent-auth-delegation",
            "workflow-execution-gate",
            "unified-copilot-management",
            "cost-gate",
        }
        
        # If not a core workflow, skip
        is_core = any(w in workflow_name for w in core_workflows)
        if not is_core:
            return "skipped"  # Not a WEC workflow
        
        # If label present, approve all core
        if not has_label:
            # Check if explicitly in WEC checklist
            if not any(c in workflow_name for c in wec_approved):
                return "skipped"  # Not checked in WEC
    
    # ... rest of approval logic
```

#### 3c. session_wrapup_autofix.py (Integration Hook)

**File**: `.scripts/ci/session_wrapup_autofix.py`

Add `--wec-approved-list` option to pass checked workflows to approval script:

```python
parser.add_argument(
    "--wec-approved-list",
    type=str,
    default="",
    help="Comma-separated list of WEC-approved workflows"
)
```

---

## Testing Strategy

### Unit Tests

```python
def test_parse_wec_checklist():
    pr_body = """## 🔄 Workflow Execution Checklist
- [x] pre-merge-validation.yml
- [x] comment-review-gate.yml
- [ ] resilient_validation.yml
"""
    checked = parse_wec_checklist(pr_body)
    assert "pre-merge-validation.yml" in checked
    assert "resilient_validation.yml" not in checked


def test_should_approve_workflow():
    # Core workflow + label → approve
    assert should_approve("pre-merge-validation", "", True) == True
    
    # Non-core workflow → skip
    assert should_approve("some-random-workflow", "", True) == False
    
    # Core + checked in WEC → approve
    pr_body = "## 🔄 Workflow Execution Checklist\n- [x] validate.yml"
    assert should_approve("validate", pr_body, False) == True
    
    # Core + unchecked in WEC → skip
    pr_body = "## 🔄 Workflow Execution Checklist\n- [ ] resilient_validation.yml"
    assert should_approve("resilient_validation", pr_body, False) == False
```

### Integration Test

1. Create test PR with WEC:
   - ✅ Check pre-merge-validation.yml
   - ✅ Check comment-review-gate.yml
   - ❌ Leave resilient_validation.yml unchecked

2. Trigger auto-approve with `wec:auto-approve` label

3. **Expected**: Only 2 workflows approved (not 105+)

4. **Verify**:
   ```bash
   gh api repos/Aries-Serpent/_codex_/actions/runs \
     -q '.workflow_runs[] | select(.conclusion == "action_required") | .name'
   # Should show empty or very few results
   ```

---

## Timeline

| Phase | Task | Estimated | Blocker? |
|-------|------|-----------|----------|
| 1 | Parse WEC checklist from PR body | 10 min | CRITICAL |
| 2 | Filter action_required runs by WEC | 20 min | CRITICAL |
| 3 | Integration test & validation | 15 min | YES |
| **Total** | **Complete BLOCKER 2** | **45 min** | **YES** |

---

## Success Criteria

After implementing BLOCKER 2:

1. ✅ PR #5337 with `wec:auto-approve` label approves **8-9 workflows** (not 105+)
2. ✅ Only core WEC workflows appear in approval queue
3. ✅ WEC checklist items are respected
4. ✅ Non-core workflows are completely skipped
5. ✅ Approval queue is manageable and predictable

---

## Related Issues

- PR #5337: WEC Enforcement Blockers
- workflow-compliance-guardian validation report
- WEC_ACTION_PLAN_PR5337.md

---

## References

- **WEC Items**: scripts/ci/session_wrapup_autofix.py (lines 100-220)
- **Workflow**: auto-approve-workflows.yml
- **Approval Script**: scripts/ci/approve_pending_runs.py
- **WEC Template**: Generated in session_wrapup_autofix.py

