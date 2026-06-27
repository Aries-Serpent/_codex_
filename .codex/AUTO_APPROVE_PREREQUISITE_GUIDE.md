# Auto-Approve Workflow Prerequisite Guide

**Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Purpose:** Explain auto-approval requirements, token hierarchy, and failure recovery  
**Audience:** Copilot Agents, CI maintainers, and automation operators

---

## Overview

Automatic workflow approval is a critical capability that allows CI/CD pipelines to progress without manual intervention. This guide explains how auto-approval works in this repository, what prerequisites must be met, and how to recover from approval failures.

**Key Principle:** Workflows are auto-approved only if:
1. The workflow item is **checked in WEC** (Workflow Execution Checklist)
2. The token has **`actions:write` scope**
3. The workflow is in **`action_required` state**

---

## Token Hierarchy & Scope Requirements

### Token Priority Chain

```
CODEX_MASTER_KEY (Tier 1: Full authority)
    ↓ (if unavailable)
CODEX_BACKUP_KEY (Tier 2: Backup authority)
    ↓ (if unavailable)
github.token (Tier 3: Installation token - LIMITED)
```

### Token Scope Matrix

| Token | Scope | actions:write | Variables API | Secrets API | Notes |
|-------|-------|---------------|---------------|-------------|-------|
| **CODEX_MASTER_KEY** | repo, workflow, actions:write | ✅ YES | ✅ YES | ✅ YES | Primary auth; full authority |
| **CODEX_BACKUP_KEY** | repo, workflow, actions:write | ✅ YES | ✅ YES | ✅ YES | Fallback if primary exhausted |
| **github.token** | repo (limited) | ❌ **NO** | ❌ **NO** | ❌ **NO** | Installation token; insufficient for auto-approve |

### Why `github.token` Fails for Approvals

```
❌ FAILS because:
- github.token = GITHUB_TOKEN environment variable
- GITHUB_TOKEN is installation token with only "repo" scope
- auto-approve requires "actions:write" scope
- API call: POST /repos/{owner}/{repo}/actions/runs/{id}/approve-deployment
- Result: HTTP 403 Forbidden
```

### Checking Token Scope

```bash
# Verify token scope
gh auth status --show-token

# Output should include:
#   - repo
#   - workflow  
#   - actions:write

# If missing actions:write, approval will fail
```

---

## Auto-Approval Workflow Selection

### When Auto-Approval Happens

Workflow runs are auto-approved only if:

1. **Status Check:** Workflow is in `action_required` state (waiting for approval)
2. **WEC Check:** Corresponding item is CHECKED in PR's Workflow Execution Checklist
3. **Token Check:** CODEX_MASTER_KEY or CODEX_BACKUP_KEY is available with `actions:write`
4. **Format Check:** WEC is properly formatted with valid checkbox syntax

### WEC Item → Auto-Approve Mapping

Not all workflows require approval. Here's which ones can benefit from auto-approval:

| Workflow | Requires Approval? | Notes |
|----------|-------------------|-------|
| pre-merge-validation.yml | ❌ NO | Auto-runs on push; no approval needed |
| comment-review-gate.yml | ❌ NO | Auto-runs; only requires manual review in UI |
| deferral-language-gate.yml | ❌ NO | Auto-validates; non-blocking |
| agent-auth-delegation.yml | ⚠️ CONDITIONAL | Auto-approves only if token present; else manual |
| workflow-execution-gate.yml | ✅ YES | May require approval if deployment impact detected |
| copilot-agent-checkin.yml | ❌ NO | Informational; no approval needed |
| copilot-agent-session-done.yml | ❌ NO | Session completion; non-blocking |
| copilot-iterative-self-healing.yml | ⚠️ CONDITIONAL | May require approval for critical fixes |
| cost-gate.yml | ⚠️ CONDITIONAL | Requires approval if cost exceeds budget |

**Summary:**
- **Must Auto-Approve:** Workflows that block merge and have WEC checkbox (workflow-execution-gate.yml)
- **Optional Auto-Approve:** Conditional workflows that may need review (cost-gate.yml, copilot-iterative-self-healing.yml)
- **Never Auto-Approve:** Informational workflows (copilot-agent-checkin.yml, etc.)

---

## Approval Request Mechanics

### Workflow Execution Sequence

```
1. Copilot Agent pushes code to PR branch
   ↓
2. All workflows triggered by 'push' event
   ↓
3. Pre-merge-validation.yml runs (auto-passes or auto-fails)
   ↓
4. If code-quality or security gates need review:
   workflow goes into "action_required" state
   ↓
5. auto-approve-workflows.yml scheduled job runs (every 5 minutes)
   ↓
6. For each run in action_required state:
   a. Check if corresponding item is CHECKED in WEC
   b. If YES: attempt approval with CODEX_MASTER_KEY
   c. If NO: skip (leave pending for manual review)
   ↓
7. If approval succeeds:
   workflow continues and completes
   ↓
8. If approval fails (token invalid, scope insufficient):
   run remains pending; manual approval required
```

### Example: workflow-execution-gate.yml Approval

```bash
# Scenario: workflow-execution-gate.yml is in action_required state

# 1. Check WEC
gh pr view 1234 --json body | grep "workflow-execution-gate"
# Output: - [x] workflow-execution-gate.yml  ← CHECKED

# 2. auto-approve-workflows.yml detects:
#    - workflow is action_required
#    - WEC checkbox is [x]
#    - Token has actions:write

# 3. auto-approve-workflows.yml calls:
GH_TOKEN=$CODEX_MASTER_KEY gh run approve RUN_ID

# 4. Approval succeeds → workflow continues

# 5. If approval fails (403):
#    - Log: "::warning::Approval failed: 403 Forbidden"
#    - Run remains pending
#    - Maintainer must manually approve in GitHub UI
```

---

## Failure Scenarios & Recovery

### Scenario 1: Token Absent or Expired

**Symptom:**
```
❌ Auto-approval failed: token is null or invalid
```

**Root Cause:**
- CODEX_MASTER_KEY not set in repository secrets
- CODEX_BACKUP_KEY not set in repository secrets
- Both tokens have expired

**Recovery:**

```bash
# 1. Verify secrets are configured
gh secret list --repo Aries-Serpent/_codex_ | grep CODEX

# 2. If missing:
#    - Create new token in GitHub
#    - Add to repo secrets as CODEX_MASTER_KEY
#    - Verify it has actions:write scope

# 3. Manually approve pending run
gh run approve RUN_ID --repo Aries-Serpent/_codex_

# 4. Re-run approval workflow
gh workflow run auto-approve-workflows.yml --repo Aries-Serpent/_codex_
```

### Scenario 2: Token Has Insufficient Scope

**Symptom:**
```
❌ Auto-approval failed: 403 Forbidden (insufficient scope)
```

**Root Cause:**
- Token has `repo` scope but not `actions:write`
- Fallback to github.token which lacks `actions:write`

**Recovery:**

```bash
# 1. Regenerate token with correct scope
# GitHub → Settings → Developer settings → Personal access tokens
# Required scopes: repo, workflow, actions:write

# 2. Update repository secret
gh secret set CODEX_MASTER_KEY --body NEW_TOKEN

# 3. Manually approve pending run
gh run approve RUN_ID --repo Aries-Serpent/_codex_

# 4. Re-run auto-approval workflow
gh workflow run auto-approve-workflows.yml
```

### Scenario 3: WEC Item Is Unchecked

**Symptom:**
```
⏭️ Skipping approval: workflow item is unchecked in WEC
```

**Root Cause:**
- Maintainer or Copilot Agent left workflow item unchecked
- Signaling: "Manual review required"

**Recovery:**

```bash
# 1. Determine if this was intentional
#    - If intentional: manually approve in GitHub UI
#    - If accidental: check the WEC item

# 2. If accidental, fix and re-run:
gh pr edit 1234 --body "... updated WEC with [x] ..."
gh workflow run auto-approve-workflows.yml

# 3. If intentional, manually approve:
# GitHub UI → Actions → [workflow run] → "Approve and run"
```

### Scenario 4: Rate Limiting

**Symptom:**
```
❌ Auto-approval failed: 429 Too Many Requests (rate limited)
```

**Root Cause:**
- GitHub API rate limit exceeded (60 req/hour for public endpoints, 5000 req/hour for authenticated)
- Multiple concurrent workflows making API calls

**Recovery:**

```bash
# 1. Check rate limit status
GH_TOKEN=$CODEX_MASTER_KEY gh api rate_limit | jq '.rate'

# 2. Wait for rate limit window to reset (typically 1 hour)
sleep 3600

# 3. Re-run auto-approval workflow
gh workflow run auto-approve-workflows.yml

# 4. Prevention: Space out parallel API calls using github_api_trickle.py
# Reference: scripts/ci/github_api_trickle.py
```

---

## Auto-Approve Workflow Implementation

### Recommended Workflow Logic

```yaml
# .github/workflows/auto-approve-workflows.yml (skeleton)

name: Auto-Approve Workflows

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  auto-approve:
    runs-on: ubuntu-latest
    
    steps:
      # 1. Check rate limit before starting
      - name: Check Rate Limit
        run: |
          RATE=$(GH_TOKEN=${{ secrets.CODEX_MASTER_KEY }} \
            gh api rate_limit --jq '.rate.remaining')
          if [[ $RATE -lt 100 ]]; then
            echo "::warning::Rate limit low: $RATE remaining"
            exit 0
          fi
      
      # 2. Get all workflow runs in action_required state
      - name: Find Pending Runs
        run: |
          gh run list --repo ${{ github.repository }} \
            --status action_required --json id,name,headBranch
      
      # 3. For each run, check WEC and attempt approval
      - name: Auto-Approve Checked Workflows
        run: |
          python scripts/ci/auto_approve_with_wec.py \
            --pr ${{ github.event.pull_request.number }} \
            --token ${{ secrets.CODEX_MASTER_KEY }}
      
      # 4. Log approval results
      - name: Post Results
        run: |
          echo "Approval sweep complete: X approved, Y skipped, Z failed"
```

### WEC-Aware Approval Helper Script

```python
# scripts/ci/auto_approve_with_wec.py (pseudocode)

def auto_approve_with_wec(pr_number, token):
    """Approve workflows that are checked in WEC."""
    
    # 1. Fetch PR and extract WEC
    wec = extract_wec_from_pr(pr_number)
    
    # 2. Get all runs in action_required state
    runs = gh_api("GET /repos/{owner}/{repo}/actions/runs",
                  query_params={"status": "action_required"})
    
    for run in runs:
        workflow_name = run['name']
        
        # 3. Check if this workflow is in WEC
        if is_workflow_checked_in_wec(workflow_name, wec):
            # 4. Attempt approval
            try:
                gh_api("POST /repos/{owner}/{repo}/actions/runs/{id}/approve-deployment",
                       headers={"Authorization": f"token {token}"})
                log(f"✅ Approved: {workflow_name}")
            except Exception as e:
                if "403" in str(e):
                    log(f"❌ Insufficient scope: {workflow_name}")
                else:
                    log(f"❌ Approval failed: {workflow_name} - {e}")
        else:
            log(f"⏭️ Skipped (unchecked): {workflow_name}")
```

---

## Best Practices for Copilot Agents

### Before Merging

1. **Verify Token Configuration:**
   ```bash
   GH_TOKEN=$CODEX_MASTER_KEY gh auth status --show-token | grep actions
   ```

2. **Check WEC Is Complete:**
   ```bash
   gh pr view N --json body | grep "Workflow Execution Checklist" && \
     echo "✅ WEC present" || echo "❌ WEC missing"
   ```

3. **Validate All REQUIRED Items Are Checked:**
   ```bash
   gh pr view N --json body | jq -r '.body' | \
     grep -E "pre-merge-validation|workflow-execution-gate" | \
     grep "\[x\]" || echo "⚠️ Some REQUIRED items unchecked"
   ```

### During Session

1. **Monitor Auto-Approval Status:**
   - Check GitHub Actions logs for `auto-approve-workflows.yml`
   - Look for approval success/failure messages
   - If failures: check token and rate limit status

2. **If Manual Approval Needed:**
   ```bash
   # Wait for auto-approval attempt
   sleep 300
   
   # If still pending, manually approve
   gh run approve RUN_ID --repo Aries-Serpent/_codex_
   ```

3. **Log Approval Decisions:**
   - Document which workflows were auto-approved
   - Note any manual approvals needed
   - Record in AGENT_ACCOUNTABILITY_REPORT.md

---

## Troubleshooting Checklist

- [ ] Verify CODEX_MASTER_KEY is set: `gh secret list | grep CODEX`
- [ ] Verify token has actions:write: `gh auth status --show-token`
- [ ] Check rate limit: `gh api rate_limit | jq '.rate'`
- [ ] Verify WEC is in PR body: `gh pr view N --json body | grep "Workflow Execution Checklist"`
- [ ] Verify WEC has valid format: `python scripts/ci/wec_enforcer.py --validate-body --pr N`
- [ ] Check auto-approve logs: `gh run view RUN_ID --log | grep -i "approval\|approve"`
- [ ] If still failing: manually approve and escalate for investigation

---

## Related Documentation

- **WEC Canonical Items:** `.codex/WEC_CANONICAL_ITEMS.md`
- **WEC Session Invariant:** `.codex/WEC_SESSION_INVARIANT.md`
- **GitHub API Reference:** `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md`
- **Workflow Failure Matrix:** `.codex/WORKFLOW_FAILURE_MATRIX.md`
- **Token Configuration:** `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-26 | Initial guide: token hierarchy, failure scenarios, recovery procedures |
