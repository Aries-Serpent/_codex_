# Workflow Failure Root-Cause Matrix

**Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Purpose:** Diagnostic guide for identifying and resolving common workflow failures  
**Audience:** Copilot Agents, CI maintainers, and debugging automation

---

## Executive Summary

This matrix catalogs the most common workflow failure patterns observed in the Aries-Serpent/_codex_ repository, with automated detection methods, root causes, and remediation strategies. It serves as a decision tree for both autonomous repair and manual intervention.

**Key Metrics:**
- **Total Patterns:** 8 documented
- **Auto-fixable:** 3 patterns (REQ-4, REQ-5, WEC format)
- **Manual review required:** 3 patterns (approval failures, token issues, cost overages)
- **Infrastructure-only:** 2 patterns (rate limiting, transient failures)

---

## Pattern 1: REQ-4 Violation (AGENT_ACCOUNTABILITY_REPORT.md Not Updated)

### Pattern ID
`WF-001-REQ4-MISSING`

### Root Cause
The file `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` was not included in the latest commit, violating governance requirement REQ-4.

**Common Reasons:**
1. Copilot Agent session completed without updating accountability file
2. `report_progress` calls were made without including the file in final commit
3. File was staged but not committed
4. Session wrapup step did not run `session_wrapup_autofix.py --auto-update`

### Detection Method

**Automatic Detection:**
```bash
# Workflow: phase-12-2-compliance-check.yml
python scripts/ci/phase_12_2_compliance_dashboard.py --check --report

# Output: ✗ REQ-4: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md was NOT updated in the last commit
```

**Manual Check:**
```bash
# Check if file is in latest commit
git show HEAD:docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md >/dev/null 2>&1 && \
  echo "✅ File present" || echo "❌ File missing"

# Check if file was modified
git diff HEAD~1 HEAD -- docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
```

### Failure Mode
- **Workflow:** `phase-12-2-compliance-check.yml` job `compliance-check`
- **Exit Code:** 1 (failure)
- **Blocking:** ✅ YES — blocks all PR merges to main
- **Impact:** Merge cannot proceed until file is updated

### Remediation Steps

**Automatic Remediation:**
```bash
# 1. Run autofix tool to update file
python scripts/ci/session_wrapup_autofix.py --auto-update --pr N

# 2. Stage and commit
git add docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
git commit --amend --no-edit

# 3. Push
git push --force-with-lease
```

**Manual Remediation:**
1. Manually edit `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
2. Add session entry with: PR number, branch, commit SHA, objective, changes made
3. Stage and commit: `git add ... && git commit -m "..."`
4. Push: `git push`

### Prevention Strategy

**For Copilot Agents:**
- ✅ Always run `python scripts/ci/session_wrapup_autofix.py --check --pr N` before final commit
- ✅ If check fails: immediately run `--auto-update` to populate file
- ✅ Include governance compliance status in session summary comment
- ✅ Verify file is in final commit before session end

**For CI/CD:**
- ✅ `phase-12-2-compliance-check.yml` runs on every push
- ✅ `pre-merge-validation.yml` includes REQ-4 check
- ✅ Blocks merge until issue is resolved

### Related Issues
- GitHub Issue: [CI Phase 12.2 Compliance Failures](https://github.com/Aries-Serpent/_codex_/issues/5100) *(Reference example; actual issue number may vary)*
- Related Document: `.codex/WEC_SESSION_INVARIANT.md` §PHASE 3
- Script: `scripts/ci/session_wrapup_autofix.py` --auto-update mode

---

## Pattern 2: REQ-5 Violation (CHANGELOG.md Not Updated)

### Pattern ID
`WF-002-REQ5-MISSING`

### Root Cause
The file `CHANGELOG.md` was not included in the latest commit, violating governance requirement REQ-5.

**Common Reasons:**
1. Copilot Agent forgot to update changelog
2. Changes were made to code but changelog was not bumped
3. `report_progress` calls did not include the file in final commit
4. Session wrapup autofix was not triggered

### Detection Method

**Automatic Detection:**
```bash
# Same as REQ-4, but for CHANGELOG.md
python scripts/ci/phase_12_2_compliance_dashboard.py --check --report

# Output: ✗ REQ-5: CHANGELOG.md was NOT updated in the last commit
```

**Manual Check:**
```bash
git diff HEAD~1 HEAD -- CHANGELOG.md | head -20
```

### Failure Mode
- **Workflow:** `phase-12-2-compliance-check.yml` job `compliance-check`
- **Exit Code:** 1 (failure)
- **Blocking:** ✅ YES — blocks all PR merges
- **Impact:** Merge cannot proceed until file is updated

### Remediation Steps

**Automatic Remediation:**
```bash
python scripts/ci/session_wrapup_autofix.py --auto-update --pr N
git add CHANGELOG.md
git commit --amend --no-edit
git push --force-with-lease
```

**Manual Remediation:**
1. Add entry to `CHANGELOG.md` under `## [Unreleased]` section
2. Follow existing changelog format (semantic versioning)
3. Commit and push

### Prevention Strategy

**For Copilot Agents:**
- ✅ Always check REQ-5 status before final commit
- ✅ Run `session_wrapup_autofix.py --auto-update` if needed
- ✅ Verify both REQ-4 and REQ-5 are satisfied before commit

**For CI/CD:**
- ✅ `phase-12-2-compliance-check.yml` enforces both REQ-4 and REQ-5
- ✅ Blocks merge until resolved

### Related Issues
- Related Pattern: WF-001-REQ4-MISSING
- Script: `scripts/ci/session_wrapup_autofix.py` --auto-update mode

---

## Pattern 3: WEC State Loss (Workflow Execution Checklist Stripped)

### Pattern ID
`WF-003-WEC-STRIPPED`

### Root Cause
The `## 🔄 Workflow Execution Checklist` section was removed from the PR body, typically due to `report_progress` tool replacing the entire PR body without including the WEC.

**Common Reasons:**
1. `report_progress` call did NOT include WEC in `prDescription` parameter
2. Copilot Agent did not read current WEC state before calling `report_progress`
3. `agent-auth-delegation.yml` re-injection failed or was delayed

### Detection Method

**Automatic Detection:**
```bash
# Check if WEC is in PR body
gh pr view N --json body | jq -r '.body' | \
  grep -q "## 🔄 Workflow Execution Checklist" && \
  echo "✅ WEC present" || echo "❌ WEC missing"
```

**Manual Check:**
```bash
# Fetch PR body and inspect
gh pr view N --json body -q '.body' | head -100
```

### Failure Mode
- **Detection:** Missing WEC section in PR body
- **Impact:** 
  - ⚠️ `workflow-execution-gate.yml` cannot read workflow intent
  - ⚠️ Maintainer's workflow selections are lost
  - ⚠️ WEC validation gates will FAIL
- **Blocking:** ✅ YES (via `workflow-execution-gate.yml`)

### Remediation Steps

**Automatic Remediation:**
```bash
# 1. Fetch last known WEC state
git log --all --pretty=format:"%B" -- "$PR_TITLE" | \
  grep -A 20 "## 🔄 Workflow Execution Checklist" | head -1 > /tmp/wec_backup.txt

# 2. Rebuild WEC from canonical items
python scripts/ci/wec_enforcer.py --validate-body --pr N --fix

# 3. If fix succeeded, you're done
# If not, manual approach below:
```

**Manual Remediation:**
1. Fetch last successful WEC state from git history or issue comments
2. Manually append WEC block to PR body using `gh pr edit`
3. Example:
   ```bash
   WEC_BLOCK=$(cat <<'EOF'
   ## 🔄 Workflow Execution Checklist
   - [x] pre-merge-validation.yml
   - [x] comment-review-gate.yml
   ...
   EOF
   )
   gh pr edit N --body-append "$WEC_BLOCK"
   ```

### Prevention Strategy

**For Copilot Agents:**
- ✅ ALWAYS read current WEC state BEFORE every `report_progress` call
- ✅ ALWAYS include WEC block in `prDescription` parameter
- ✅ After each push, verify WEC is still in PR body (do not assume)
- ✅ Post session comment with "WEC State Preserved" confirmation
- ✅ Reference: `.codex/WEC_SESSION_INVARIANT.md` §PHASE 2

**For CI/CD:**
- ✅ `workflow-execution-gate.yml` validates WEC presence
- ✅ Session preload in `copilot-setup-steps.yml` logs WEC state
- ✅ `agent-auth-delegation.yml` re-injects WEC if missing (race condition protection)

### Related Issues
- Root Cause Document: `docs/workflows/WEC_PR_BODY_CONFLICTS.md`
- Prevention Guide: `.codex/WEC_SESSION_INVARIANT.md`
- Script: `scripts/ci/wec_enforcer.py`

---

## Pattern 4: WEC Format Corruption (Invalid Checkbox Syntax)

### Pattern ID
`WF-004-WEC-FORMAT-INVALID`

### Root Cause
The WEC section exists but contains invalid checkbox syntax, preventing parsers from reading it.

**Common Reasons:**
1. Manual edits to PR body with typos: `[X]` instead of `[x]` or `[ ]`
2. Markdown rendering issues: extra spaces in `[ x ]` or `[x ]`
3. Accidental line breaks within checkboxes
4. Copy-paste errors from external sources

### Detection Method

**Automatic Detection:**
```bash
# Validate WEC format
python scripts/ci/wec_enforcer.py --validate-body --pr N

# Output on failure:
# ❌ WEC format invalid: checkbox on line 42 has invalid syntax: [X] (expected [x] or [ ])
```

**Manual Check:**
```bash
gh pr view N --json body | jq -r '.body' | \
  grep -E "- \[[^x \]|[x ][^]]*\]" | head -5
```

### Failure Mode
- **Detection:** `wec_enforcer.py` or `workflow-execution-gate.yml`
- **Impact:** Parsers cannot read WEC; gate fails
- **Blocking:** ✅ YES (via `workflow-execution-gate.yml`)

### Remediation Steps

**Automatic Remediation:**
```bash
python scripts/ci/wec_enforcer.py --validate-body --pr N --fix
```

**Manual Remediation:**
1. Fetch current PR body
2. Identify invalid checkboxes (search for `[X]`, `[x ]`, `[ x]`, etc.)
3. Replace with valid syntax: `[x]` (checked) or `[ ]` (unchecked)
4. Update PR body using `gh pr edit N --body "..."`

### Prevention Strategy

**For Copilot Agents:**
- ✅ When manually editing WEC, use EXACT format: `- [x]` or `- [ ]`
- ✅ Never use capital X: `[X]` is invalid
- ✅ Validate before committing: `wec_enforcer.py --validate-body`

**For CI/CD:**
- ✅ `workflow-execution-gate.yml` validates format
- ✅ `wec_enforcer.py --validate-body` can auto-fix common typos

### Related Documents
- Format Specification: `.codex/WEC_CANONICAL_ITEMS.md` §WEC Format & Syntax
- Validation Tool: `scripts/ci/wec_enforcer.py`

---

## Pattern 5: Workflow Approval Failure (Token Insufficient Scope)

### Pattern ID
`WF-005-APPROVAL-TOKEN-INSUFFICIENT`

### Root Cause
Auto-approval workflow (`auto-approve-workflows.yml`) cannot approve pending runs because the token lacks `actions:write` scope.

**Common Reasons:**
1. CODEX_MASTER_KEY or CODEX_BACKUP_KEY is not available in workflow context
2. Fallback to `github.token` which lacks `actions:write` scope
3. Token has expired or been revoked
4. Token is for a fork instead of the main repository

### Detection Method

**Automatic Detection:**
```bash
# Check workflow summary in GitHub Actions
# Look for: "::warning::Approval failed: 403 Forbidden"

# Or check workflow logs:
gh run view RUN_ID --log | grep -i "403\|forbidden\|insufficient"
```

**Manual Check:**
```bash
# Test token scope
GH_TOKEN=$CODEX_MASTER_KEY gh api user | jq '.login'
GH_TOKEN=$CODEX_MASTER_KEY gh api -H "Accept: application/vnd.github+json" \
  /repos/Aries-Serpent/_codex_/actions/runs/RUN_ID/approve-deployment
```

### Failure Mode
- **Detection:** `auto-approve-workflows.yml` job fails or skips approvals
- **Impact:** 
  - ⚠️ Workflows remain in `action_required` state
  - ⚠️ Manual approval is required
  - ⚠️ PR merge is blocked if auto-approval was mandatory
- **Blocking:** ❌ NO (non-blocking; manual approval can proceed)

### Remediation Steps

**Automatic Remediation (CI):**
```bash
# Ensure CODEX_MASTER_KEY and CODEX_BACKUP_KEY are set in repository secrets
# Re-run the approval workflow with proper token
```

**Manual Remediation:**
1. Manually approve workflow run in GitHub UI:
   - Go to Actions tab
   - Find workflow run
   - Click "Approve and run" button
2. Or use CLI:
   ```bash
   GH_TOKEN=$CODEX_MASTER_KEY gh run approve RUN_ID --repo Aries-Serpent/_codex_
   ```

### Prevention Strategy

**For CI/CD:**
- ✅ Ensure `CODEX_MASTER_KEY` is set in repository secrets
- ✅ Verify token has `actions:write` scope: `gh auth status --show-token | grep actions`
- ✅ Token hierarchy: CODEX_MASTER_KEY > CODEX_BACKUP_KEY > github.token
- ✅ `auto-approve-workflows.yml` logs token validation status

**For Repository Maintainers:**
- ✅ Verify secrets are configured correctly
- ✅ Test token access: `gh auth status`
- ✅ Create backup token if primary expires

### Related Documents
- Token Configuration: `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md`
- Auto-Approval Guide: `.codex/AUTO_APPROVE_PREREQUISITE_GUIDE.md`
- Workflow: `.github/workflows/auto-approve-workflows.yml`

---

## Pattern 6: WEC Required Items Unchecked (Merge to main)

### Pattern ID
`WF-006-WEC-REQUIRED-UNCHECKED`

### Root Cause
One or more REQUIRED workflow items are unchecked in WEC before merging to main.

**REQUIRED items for main branch:**
1. `pre-merge-validation.yml`
2. `comment-review-gate.yml`
3. `deferral-language-gate.yml`
4. `agent-auth-delegation.yml` (if agent-delegated PR)
5. `workflow-execution-gate.yml`

### Detection Method

**Automatic Detection:**
```bash
# Check WEC for required items
gh pr view N --json body | jq -r '.body' | \
  grep -E "pre-merge-validation|comment-review-gate|workflow-execution-gate" | \
  grep "\[ \]" && echo "❌ REQUIRED item unchecked"
```

**Workflow Detection:**
```bash
# workflow-execution-gate.yml checks this
# If any REQUIRED item is unchecked, workflow fails
```

### Failure Mode
- **Detection:** `pre-merge-validation.yml` or `workflow-execution-gate.yml`
- **Impact:** ✅ BLOCKS merge to main
- **Error Message:** "WEC contains unchecked REQUIRED workflows"

### Remediation Steps

**Immediate Fix:**
1. Identify which REQUIRED items are unchecked (look for `[ ]`)
2. Edit PR body to check them: `- [ ]` → `- [x]`
3. Use `gh pr edit N --body "..."` or manual edit in UI
4. Re-run compliance gate

**Root Cause Analysis:**
- Why were they intentionally unchecked?
- If accidental: check them
- If intentional but merge to main required: escalate to maintainer

### Prevention Strategy

**For Copilot Agents:**
- ✅ Reference: `.codex/WEC_CANONICAL_ITEMS.md` §WEC Requirements by Merge Target
- ✅ ALWAYS check all 5 REQUIRED items before final commit for main-branch PRs
- ✅ Validate in pre-commit step: `wec_enforcer.py --validate-body --pr N`

**For CI/CD:**
- ✅ `workflow-execution-gate.yml` enforces this
- ✅ Blocks merge if any REQUIRED item is unchecked

### Related Documents
- WEC Requirements: `.codex/WEC_CANONICAL_ITEMS.md`
- Session Invariant: `.codex/WEC_SESSION_INVARIANT.md` §WEC Requirements by Merge Target

---

## Pattern 7: Cost Gate Exceeded (Cost Governance)

### Pattern ID
`WF-007-COST-GATE-EXCEEDED`

### Root Cause
Deployment cost exceeds budget threshold defined in `cost-gate.yml`, blocking merge to main.

**Common Reasons:**
1. Resource-intensive infrastructure changes (e.g., larger instances, more replicas)
2. New service deployment with expensive tier
3. Cost gate not checked in WEC so cost validation runs automatically
4. Budget threshold is lower than projected deployment cost

### Detection Method

**Automatic Detection:**
```bash
# Check cost-gate.yml workflow logs
gh run view RUN_ID --log | grep -i "cost\|budget\|exceeded"
```

### Failure Mode
- **Detection:** `cost-gate.yml` workflow
- **Impact:** ⚠️ BLOCKS merge if cost-gate is checked in WEC
- **Non-blocking:** ✅ If cost-gate is NOT checked in WEC

### Remediation Steps

**If Cost Is Justified:**
1. Update cost-gate.yml to increase budget threshold
2. Or: Update cost projection in deployment plan
3. Rerun cost-gate

**If Cost Can Be Reduced:**
1. Modify infrastructure changes to reduce cost
2. Use cheaper resource tiers
3. Rerun deployment

### Prevention Strategy

**For Copilot Agents:**
- ✅ For cost-impacting changes: UNCHECK `cost-gate.yml` in WEC (optional gate)
- ✅ Or: ensure projected costs are within budget before final commit
- ✅ Reference: `.codex/WEC_CANONICAL_ITEMS.md` §Item 9: cost-gate.yml

---

## Pattern 8: Rate Limiting (GitHub API Exhaustion)

### Pattern ID
`WF-008-RATE-LIMIT-EXCEEDED`

### Root Cause
GitHub API rate limit has been exceeded, blocking further API calls in the workflow.

**Common Reasons:**
1. Multiple workflows running simultaneously making API calls
2. Large batch operations (listing commits, workflows, etc.)
3. `auto-approve-workflows.yml` scheduled sweep making many approval requests
4. Rate limit window reset not yet completed

### Detection Method

**Automatic Detection:**
```bash
# Check workflow logs
gh run view RUN_ID --log | grep -i "rate limit\|429\|quota"

# Or use API to check current usage
GH_TOKEN=$CODEX_MASTER_KEY gh api rate_limit | jq '.rate'
```

### Failure Mode
- **Detection:** API calls fail with 429 status
- **Impact:** 🟡 Non-blocking workflow failure; retryable
- **Recovery:** Automatic retry or manual re-trigger

### Remediation Steps

**Automatic Remediation:**
- Workflows have built-in retry logic (exponential backoff)
- Wait for rate limit window to reset (typically 1 hour)
- Re-run the workflow

**Manual Remediation:**
```bash
# Wait for rate limit window to reset
sleep 3600

# Re-run workflow
gh workflow run WORKFLOW_NAME.yml --repo Aries-Serpent/_codex_
```

### Prevention Strategy

**For CI/CD:**
- ✅ `github_api_trickle.py` provides rate-limit-aware API calling
- ✅ Workflows use `GH_TRICKLE_*` environment variables for polite rate limiting
- ✅ `auto-approve-workflows.yml` checks rate limit before making batch approvals

### Related Documents
- Rate Limiting Guide: `scripts/ci/github_api_trickle.py`
- API Reference: `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md`

---

## Summary Table: Quick Reference

| Pattern | Root Cause | Auto-Fix | Blocking | Detection | Priority |
|---------|-----------|----------|----------|-----------|----------|
| WF-001 | REQ-4 missing | ✅ YES | ✅ YES | `phase-12-2-compliance-check.yml` | 🔴 CRITICAL |
| WF-002 | REQ-5 missing | ✅ YES | ✅ YES | `phase-12-2-compliance-check.yml` | 🔴 CRITICAL |
| WF-003 | WEC stripped | ⚠️ PARTIAL | ✅ YES | PR body missing WEC section | 🔴 CRITICAL |
| WF-004 | WEC format invalid | ✅ YES | ✅ YES | `wec_enforcer.py --validate-body` | 🔴 CRITICAL |
| WF-005 | Token insufficient | ❌ NO | ❌ NO | Auto-approval logs | 🟡 MEDIUM |
| WF-006 | REQUIRED unchecked | ⚠️ MANUAL | ✅ YES | `workflow-execution-gate.yml` | 🔴 CRITICAL |
| WF-007 | Cost exceeded | ❌ NO | 🟡 CONDITIONAL | `cost-gate.yml` logs | 🟡 MEDIUM |
| WF-008 | Rate limit | ✅ RETRY | ❌ NO | API response 429 | 🟢 LOW |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-26 | Initial matrix: 8 patterns documented |

---

## References

- **WEC Canonical Items:** `.codex/WEC_CANONICAL_ITEMS.md`
- **WEC Session Invariant:** `.codex/WEC_SESSION_INVARIANT.md`
- **Governance Policy:** `.codex/CODEBASE_AGENCY_POLICY.md`
- **Session Wrapup Tool:** `scripts/ci/session_wrapup_autofix.py`
- **WEC Enforcer:** `scripts/ci/wec_enforcer.py`
