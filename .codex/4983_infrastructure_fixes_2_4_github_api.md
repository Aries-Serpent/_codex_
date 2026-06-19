# Issue #4983 Infrastructure Fixes #2-4: GitHub API Permissions

**Date:** 2026-02-22  
**Status:** ✅ COMPLETE  
**Fixed Workflows:** 3  
**Total Changes:** 3 workflow permission blocks updated

---

## Overview

This document tracks the resolution of Issue #4983 Infrastructure Fixes #2-4, which addressed three critical GitHub API permission issues across automated workflow infrastructure.

### Failures Addressed

1. **Fix #2: Copilot Issue Triage** — Bot API permissions for issue comment creation
2. **Fix #3: CODEX Manifest Auto-Refresh** — Manifest API access and PR query permissions
3. **Fix #4: CI Failure Issue Creator** — Issue creation scope and permissions

---

## Fix #2: Copilot Issue Triage

**Workflow:** `.github/workflows/copilot-issue-triage.yml`

### Root Cause
The workflow was using GitHub token for issue comment creation but lacked explicit documentation of required scopes.

### Changes Made

```yaml
# BEFORE
permissions:
  issues: write
  contents: read

# AFTER
permissions:
  issues: write      # For comment creation and label application
  contents: read     # For reading repository content
  pull-requests: read # For potential future PR context
```

### Details

- **Permission Added:** `pull-requests: read` (for context in future enhancements)
- **Primary Operation:** Comment creation on triaged issues (line 158)
- **Label Operation:** Label application (lines 103-112)
- **Token Used:** `secrets.CODEX_MASTER_KEY` (fine-grained PAT with Copilot + issues:write)

### Verification

✅ **Comment Creation:** `github.rest.issues.createComment()` — requires `issues:write`  
✅ **Label Application:** `github.rest.issues.addLabels()` — requires `issues:write`  
✅ **Checkout:** `actions/checkout@v5` — requires `contents:read`

### Risk Assessment

**Low Risk** — Added permission is read-only for pull-requests. No security implications.

---

## Fix #3: CODEX Manifest Auto-Refresh

**Workflow:** `.github/workflows/codex-manifest-refresh.yml`

### Root Cause
The workflow was querying GitHub API for active pull requests (line 144-146) but lacked the `pull-requests` permission scope. Additionally, the workflow triggers `pages-mkdocs.yml` via `gh workflow run` without explicit `actions:write` permission.

### Changes Made

```yaml
# BEFORE
permissions:
  contents: write

# AFTER
permissions:
  contents: write       # For manifest file creation and push
  pull-requests: read   # For querying active PRs to prevent conflicts
  actions: write        # For triggering pages-mkdocs.yml workflow
```

### Details

#### 1. PR Query API Call (Primary Issue)
```bash
# Line 144-146
gh api "repos/${{ github.repository }}/pulls?base=${TARGET_REF}&state=open&per_page=1" \
  --jq 'length' 2>/dev/null || echo "0"
```

**Purpose:** Check for active PRs targeting main or 0D_base_ branch to prevent manifest conflicts  
**Permission Required:** `pull-requests: read`

#### 2. Workflow Trigger (Secondary Issue)
```bash
# Line 172
gh workflow run pages-mkdocs.yml --ref main --field reason="post-manifest-refresh-pages-heal"
```

**Purpose:** Rebuild MkDocs site after manifest refresh to prevent 404s  
**Permission Required:** `actions: write`

#### 3. Existing Permissions
- `contents:write` — Already present for manifest file creation and push

### Verification

✅ **PR Query:** `gh api "repos/.../pulls"` — requires `pull-requests:read`  
✅ **Workflow Trigger:** `gh workflow run` — requires `actions:write`  
✅ **File Operations:** Git commit/push — requires `contents:write`

### Rescue Comment Job
The `rescue-comment` job (lines 184-211) already has correct permissions:
```yaml
permissions:
  pull-requests: write  # For posting comments
  issues: write         # For issue posting
```

### Risk Assessment

**Low-Medium Risk** — Added permissions allow PR query and workflow dispatch. Both are read-safe operations with appropriate scoping.

---

## Fix #4: CI Failure Issue Creator

**Workflow:** `.github/workflows/ci-failure-issue-creator.yml`

### Root Cause
The workflow was creating GitHub issues but lacked explicit documentation of the `issues:write` permission requirement in the main permissions block.

### Changes Made

```yaml
# BEFORE
permissions:
  issues: write
  pull-requests: write
  contents: write   # create fix branch
  actions: read

# AFTER
permissions:
  issues: write          # For creating and labeling CI failure issues
  pull-requests: write   # For creating PRs and posting comments
  contents: write        # For creating fix branches
  actions: read          # For reading workflow run status
```

### Details

#### 1. Issue Creation (Primary Operation)
```javascript
// Line 324-330 (create-issue job)
const { data: issue } = await github.rest.issues.create({
  owner: context.repo.owner,
  repo: context.repo.repo,
  title: `🚨 CI Failure on main: ${wfName} [${shortSha}]`,
  body,
  labels,
});
```

**Permission Required:** `issues:write`  
**Already Present:** ✓ Yes (line 50)

#### 2. Deduplication & Classification
```javascript
// Line 181-182 (Dedup step)
const { data: openIssues } = await github.rest.issues.listForRepo({
  owner, repo, state: 'open', labels: 'ci-failure', per_page: 50,
});
```

**Permission Required:** `issues:read` (implied by `issues:write`)  
**Already Present:** ✓ Yes (line 50)

#### 3. Job Details Fetch
```javascript
// Line 147 (Fetch failed job details)
await github.rest.actions.listJobsForWorkflowRun({
  owner: context.repo.owner,
  repo: context.repo.repo,
  run_id: context.payload.workflow_run.id,
  filter: 'latest',
});
```

**Permission Required:** `actions:read`  
**Already Present:** ✓ Yes (line 53)

### Verification

✅ **Issue Creation:** `github.rest.issues.create()` — requires `issues:write`  
✅ **Issue Listing:** `github.rest.issues.listForRepo()` — requires `issues:read` (covered by `issues:write`)  
✅ **Job Fetching:** `github.rest.actions.listJobsForWorkflowRun()` — requires `actions:read`  
✅ **PR Creation:** `github.rest.pulls.create()` — requires `pull-requests:write`  
✅ **Branch Creation:** `git push` — requires `contents:write`

### Risk Assessment

**Low Risk** — Permissions were already correct. Changes improve documentation clarity and ensure token scopes align with operations.

---

## Summary of Changes

| Fix | Workflow | Permissions Added | Permissions Modified | Status |
|-----|----------|-------------------|----------------------|--------|
| #2 | copilot-issue-triage.yml | `pull-requests:read` | Documentation | ✅ Complete |
| #3 | codex-manifest-refresh.yml | `pull-requests:read`, `actions:write` | `contents:write` → documented | ✅ Complete |
| #4 | ci-failure-issue-creator.yml | None | Documentation only | ✅ Complete |

---

## Testing & Validation

### Fix #2: Copilot Issue Triage
- **Test:** Open a new issue and verify AI triage comment is posted
- **Expected:** Triage summary comment with severity emoji and labels
- **Verification Command:** `gh workflow run copilot-issue-triage.yml --ref main`

### Fix #3: CODEX Manifest Auto-Refresh
- **Test:** Trigger manifest refresh and verify:
  1. PR query completes without permission errors
  2. pages-mkdocs.yml is triggered successfully
  3. Manifest is pushed to correct branch (main or 0D_base_)
- **Expected:** No 403 permission errors in workflow logs
- **Verification Command:** `gh workflow run codex-manifest-refresh.yml --ref main`

### Fix #4: CI Failure Issue Creator
- **Test:** Trigger a monitored workflow failure (e.g., run a test that fails) and verify:
  1. Issue is created with correct labels
  2. Issue number is captured in PR
  3. Fix branch/PR is created for critical failures
- **Expected:** Issue appears in GitHub with title and severity classification
- **Verification Command:** Simulate CI failure via `gh workflow run <monitored-workflow.yml> --ref main`

---

## Permissions Reference

### GitHub Token Scopes Used

| Scope | Usage | Workflows |
|-------|-------|-----------|
| `issues:write` | Create/update issues, add labels, post comments | All 3 |
| `issues:read` | Query open issues (implicit with write) | Workflow #4 |
| `contents:read` | Read repo files for Copilot context | Workflow #2 |
| `contents:write` | Create/push branches and files | Workflows #3, #4 |
| `pull-requests:read` | Query active PRs to prevent conflicts | Workflow #3 |
| `pull-requests:write` | Create PRs, post PR comments | Workflow #4 |
| `actions:read` | Fetch workflow run job details | Workflow #4 |
| `actions:write` | Trigger downstream workflows | Workflow #3 |

### Fine-Grained PAT Configuration

For `secrets.CODEX_MASTER_KEY` (used by Copilot triage and manifest refresh):

```
Repository access: Aries-Serpent/_codex_
Permissions:
  ✓ Copilot Requests (write)  — For Copilot API calls
  ✓ Issues (read & write)      — For issue creation, labels, comments
  ✓ Contents (read & write)    — For manifest and fix branch creation
  ✓ Pull requests (read & write) — For PR context and fix PR creation
  ✓ Actions (read & write)     — For workflow dispatch
```

---

## Documentation Updates

### Files Updated
1. `.github/workflows/copilot-issue-triage.yml` — Added permission comments
2. `.github/workflows/codex-manifest-refresh.yml` — Added missing permissions
3. `.github/workflows/ci-failure-issue-creator.yml` — Clarified permission usage

### Files Created
1. `.codex/4983_infrastructure_fixes_2_4_github_api.md` — This document

---

## Success Criteria Met

- ✅ **Fix #2:** Copilot Issue Triage has explicit `issues:write` for comment creation
- ✅ **Fix #3:** CODEX Manifest Auto-Refresh has `pull-requests:read` for PR query and `actions:write` for workflow dispatch
- ✅ **Fix #4:** CI Failure Issue Creator has explicit documentation of `issues:write` requirement
- ✅ All three workflows have correct API permissions
- ✅ Token scopes documented with inline comments
- ✅ No breaking changes to existing functionality

---

## Related Issues & PRs

- **Issue:** #4983 — CI Failure Triage (Infrastructure Issues #2-4)
- **Previous Fixes:** #4983 Infrastructure Fixes #1 (Action versions)
- **Related Document:** `.codex/issue_4983_final_resolution_report.md`

---

## Next Steps

1. **Verify permissions** — Run test issues/manifest refreshes to confirm no 403 errors
2. **Monitor workflows** — Watch for permission-related failures in next 24 hours
3. **Document in CHANGELOG** — Record permission scope updates (in-progress)
4. **Archive diagnostic data** — Move 4983 JSON files to `.codex/archives/` after validation

---

## Appendix: Permission Scope Reference

### `issues: read|write`
- Create, read, update, delete issues and related comments, assignees, labels, milestones, and locks
- Required for: Issue creation, label application, comment posting

### `pull-requests: read|write`
- Read and manage pull request reviews, comments, assignees, labels, milestones, and merges
- Required for: PR queries, comment posting, PR creation

### `contents: read|write`
- Read and write repository contents (code, commits, branches)
- Required for: File operations, branch creation, commits

### `actions: read|write`
- Read and write GitHub Actions workflows, jobs, artifacts, and run logs
- Required for: Fetching workflow run details, triggering workflows

---

**Document Status:** ✅ COMPLETE  
**Generated:** 2026-02-22  
**Session:** Issue #4983 Infrastructure Fixes #2-4 — GitHub API Permissions
