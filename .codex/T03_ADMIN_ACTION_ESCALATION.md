# T-03 Admin Action Escalation — Token Scope Configuration

**Issue:** #5073 — CI Failure: Admin Action — T-03 security_events Scope Gate  
**Date:** 2026-06-25T13:24Z  
**Status:** ESCALATION REQUIRED  
**Owner:** @mbaetiong  

---

## Executive Summary

Workflow `admin-action-t03.yml` is failing due to missing `security_events` OAuth scope on `CODEX_MASTER_KEY` token. This blocks CodeQL alert retrieval and remediation workflows.

**Root Cause:** Token probe returns HTTP 403 (Resource not accessible by integration)  
**Expected Behavior:** Token should return HTTP 200 with proper `security_events` scope  
**Impact:** Blocks `codeql-alert-fetcher.yml` and CodeQL-based agent workflows

---

## Action Required (Admin Only)

### Prerequisites
- Access to GitHub organization personal access tokens
- Authority to update organization secrets in GitHub Actions

### Steps to Fix

#### 1. Access the Token
Navigate to: https://github.com/settings/tokens
- Find the PAT used for `CODEX_MASTER_KEY`
- Click **Edit** to open token configuration

#### 2. Add Scope: `security_events`
- Current scopes: `repo`, `workflow`
- **Action:** Add `security_events` to the scope list
- Set expiry: **90 days** from today (recommendation)
- Click **"Update token"** — copy the new token value

#### 3. Update Organization Secret
Navigate to: https://github.com/organizations/Aries-Serpent/settings/secrets/actions/CODEX_MASTER_KEY
- Paste the new token value
- Click **Save**

#### 4. Verification
Run the token probe workflow to verify the fix:
```bash
gh workflow run token-probe.yml \
  --repo Aries-Serpent/_codex_ \
  --field pr_number=5073
```

#### 5. Post-Rotation Check
After token update, run:
```bash
GH_TOKEN=<new_token> bash scripts/ci/post_rotation_verify.sh
```

---

## Auto-Resolution

Once token scope is updated:
1. Workflow `admin-action-t03.yml` will automatically:
   - Detect HTTP 200 from the CodeQL API
   - **Close issue #5073** with success comment
   - Allow dependent workflows to proceed

2. Dependent workflows will activate:
   - `codeql-alert-fetcher.yml` — Retrieve CodeQL alerts
   - CodeQL remediation agents — Fix identified vulnerabilities

---

## Reference Documentation

| Document | Section | Purpose |  
|----------|---------|---------|  
| `docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md` | § T-03 | Full token review and scopes |  
| `.codex/docs/ADMIN_ACTION_WORKFLOW_PATTERN.md` | Admin Actions | Workflow pattern documentation |  
| `.github/workflows/admin-action-t03.yml` | Lines 39-62 | Full fix instructions (embedded) |  

---

## Failure Details (For Reference)

**Workflow:** `.github/workflows/admin-action-t03.yml`  
**Probe URL:** `https://api.github.com/repos/Aries-Serpent/_codex_/code-scanning/alerts?per_page=1`  
**Expected Status:** HTTP 200  
**Current Status:** HTTP 403 (Forbidden)  
**Error Message:** "Resource not accessible by integration"

---

## Automation After Fix

The following workflows will automatically execute once the token is rotated:

1. **Token Probe** (manual verification step)
   - Confirms token now has `security_events` scope
   - Returns HTTP 200 on code-scanning/alerts endpoint

2. **CodeQL Alert Fetcher** (auto-triggered)
   - Retrieves all CodeQL alerts from GitHub API
   - Categorizes by severity and rule
   - Generates alert report for remediation agents

3. **CodeQL Remediation Agents** (parallel execution)
   - `codeql-alert-resolution-agent` — Fixes security alerts
   - `code-scanning-remediation-agent` — Handles GHAS findings
   - `unified-security-scanner` — Comprehensive security audit

4. **Auto-Close Issue #5073**
   - When probe passes (HTTP 200), workflow automatically closes issue
   - Posts success comment with resolution timestamp

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Token rotation breaks other workflows | Token update maintains `repo` and `workflow` scopes; only adds `security_events` |  <!-- pragma: allowlist secret -->
| Token expiry disrupts automation | 90-day expiry provides 3-month window; reminder set at day 80 |
| Scope change introduces security risk | `security_events` is read-only for CodeQL alerts (no mutation capability) |  <!-- pragma: allowlist secret -->


---

## Next Steps

1. **Immediate:** Admin (@mbaetiong) performs token scope update
2. **Verification:** Run token probe workflow to confirm fix
3. **Auto-Resolution:** Issue #5073 closes automatically on success
4. **Downstream:** CodeQL remediation workflows execute in parallel

**Timeline:** 5-10 minutes for token update + verification  
**Blocking:** No — other work can proceed while awaiting admin action  
**Escalation:** @mbaetiong (PR #5078 assignee)

---

**Generated:** 2026-06-25T13:24Z  
**Session:** copilot-health-remediation-5078  
**Auto-Close Trigger:** Token probe HTTP 200 response
