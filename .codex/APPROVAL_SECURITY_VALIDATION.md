# Unified Approval Hub Security Validation

**Document Version:** 1.0  
**Status:** Phase 2 Task 2.1 Extended Deliverable  
**Date:** 2025-02-21  
**Author:** Unified Security Scanner  
**Scope:** 5-workflow approval consolidation infrastructure

---

## Executive Summary

This document provides comprehensive security analysis of the proposed unified approval hub design, consolidating approval mechanisms across 5 critical GitHub Actions workflows. The analysis identifies security threat vectors, validates token chain architecture, assesses audit logging sufficiency, and provides actionable recommendations to achieve production-grade security posture before consolidation.

**Key Findings:**
- **Token Chain:** Properly tiered (Tier 1-4) with fallback protection; Tier 2-3 require rotation policy and secrets scanning improvements
- **Audit Logging:** Current implementation (.codex/approvals.jsonl format) lacks formal specification and signed entries; recommend append-only storage with file permissions
- **Approval Rules:** Label-based controls present bypass risk if non-maintainers can edit labels; recommend CODEOWNERS enforcement via label creation workflows
- **Attack Surface:** 4 critical attack scenarios identified; self-trigger guard mitigates cascade loops; token compromise remains highest-impact threat
- **Compliance Gaps:** SOC 2 controls ~70% implemented; HIPAA/PCI require organizational scoping; recommend quarterly compliance audits

**Recommendation:** Proceed with consolidation on conditional basis—implement CRITICAL and HIGH recommendations before production deployment.

---

## 1. Security Threat Model

### 1.1 Identified Threat Vectors

#### TV-1: Token Compromise (Critical Severity)

**Description:** Leaked or exfiltrated CODEX_MASTER_KEY PAT used to auto-approve arbitrary PRs without review.

**Attack Vector:** 
- Stored in GitHub secret (protected via GitHub encryption)
- Visible in logs if token is inadvertently printed or leaked in error messages
- Accessible to any GitHub Actions workflow with `secrets: inherit` and appropriate permissions
- Risk increases with workflow complexity and number of actions used

**Current Mitigation:**
- Token stored as GitHub secret (encrypted at rest)
- Explicit scope check: `repo`, `workflow`, `actions:write` only (no admin access)
- Concurrency control prevents rapid-fire approvals (cancel-in-progress: true)
- github.token fallback (Tier 4) as final safety valve

**Validation Approach:**
- Audit GitHub Actions run logs for token leakage (test: run `echo $GITHUB_TOKEN` in workflow)
- Verify no token printing in error handlers (scripts/ci/approve_pending_runs.py line 93-95)
- Check for secrets scanning alerts on repository (GitHub Advanced Security dashboard)
- Verify CODEOWNERS block on secrets modification

**Enhancement:** Implement monthly token rotation with new PAT creation and fallback-to-new-key migration. Add pre-approval log line: `"Approving run ID: {id} via token tier: {tier}"` to audit which token tier was used.

---

#### TV-2: Approval Bypass via Label Manipulation (High Severity)

**Description:** Non-maintainer contributor adds `wec:auto-approve` or `wec:auto-approve-once` label to PR, triggering auto-approval without required review.

**Attack Vector:**
- Labels are writable by users with collaborator access (contributor role)
- auto-approve-workflows.yml checks label presence (line 149-170) but does not verify label creator identity
- Persistent label `wec:auto-approve` enables permanent bypass once added

**Current Mitigation:**
- PR template discourages label use without maintainer review
- Audit log entry should capture label addition, but current logging format unclear
- CODEOWNERS file can restrict who can approve, but label creation is uncontrolled

**Validation Approach:**
- Audit .codex/approvals.jsonl entries for non-maintainer label additions
- Test: Create PR as contributor, add `wec:auto-approve` label, verify approval workflow does NOT fire
- Check GitHub audit logs for label creation events (Actions > Settings > Audit log)
- Verify PR review requirement is enforced before merge (even if approval workflow fires)

**Enhancement:** Implement label validation workflow that enforces CODEOWNERS approval before `wec:auto-approve*` label is applied. Add to auto-approve-workflows.yml:
```yaml
- name: Verify label authority
  if: github.event_name == 'pull_request' && contains(github.event.pull_request.labels.*.name, 'wec:auto-approve')
  run: |
    # Check if label creator is in CODEOWNERS
    python3 scripts/ci/verify_label_authority.py
```

---

#### TV-3: Audit Trail Tampering (High Severity)

**Description:** Attacker deletes or modifies .codex/approvals.jsonl to hide approval records and cover tracks.

**Attack Vector:**
- File is stored in repository (writable by users with push access)
- No cryptographic signing or tamper-evident storage
- No read-only backup or archive mechanism
- Deletion would appear as normal commit in git history but could be rebased/rewritten

**Current Mitigation:**
- File stored in .codex/ (convention suggests restricted visibility)
- Git commit history provides immutable record of modifications
- CODEOWNERS can restrict direct writes, but commit rewriting circumvents this

**Validation Approach:**
- Verify .codex/approvals.jsonl format and schema (currently undefined—needs formal specification)
- Test: Attempt to delete and recreate approvals.jsonl; verify git log shows deletion commit
- Check CODEOWNERS restrictions on .codex/ directory
- Verify approval entries are only APPENDED, never modified (idempotent log)

**Enhancement:** Implement append-only logging with immutable storage:
1. Move .codex/approvals.jsonl to append-only log with per-entry HMAC-SHA256 signature
2. Add log rotation (monthly archive to .codex/approvals-archive/{YYYY-MM}.jsonl.gz)
3. Restrict write permissions: only approve_pending_runs.py and admin workflows can append
4. Implement read-only CI job that validates log integrity on each PR (fail if signature mismatch)

---

#### TV-4: Rate-Limit Exhaustion / Denial of Service (Medium Severity)

**Description:** Malicious or misconfigured workflow triggers high-frequency approval requests, exhausting GitHub API rate limit quota and blocking all subsequent approvals.

**Attack Vector:**
- Workflow can be triggered with `workflow_dispatch` (manual trigger)
- Pull request event could fire multiple times if PR is updated rapidly
- No per-PR or per-workflow approval throttling documented
- Rate limit pre-check exists (line ~180 in auto-approve-workflows.yml) but granularity unknown

**Current Mitigation:**
- Pre-check: Stop if remaining API calls < 20 (prevents catastrophic quota exhaustion)
- cancel-in-progress: true prevents old approval requests from executing if new one arrives
- Log entry: Output remaining quota after each approval (helps detect quota anomalies)

**Validation Approach:**
- Simulate high-frequency PR updates; measure approval request rate
- Verify rate-limit pre-check threshold (20 remaining) is appropriate for typical usage
- Calculate approval requests per 24h under normal conditions (establish baseline)
- Test: Trigger 10 approvals rapidly; verify only 1 executes and others are cancelled

**Enhancement:** Implement per-workflow throttling:
```python
# In approve_pending_runs.py
APPROVALS_PER_WORKFLOW_PER_HOUR = 10
def check_approval_throttle(workflow_id):
    recent_approvals = query_approvals_by_workflow(workflow_id, hours=1)
    if len(recent_approvals) >= APPROVALS_PER_WORKFLOW_PER_HOUR:
        return False  # Throttled
    return True
```

---

#### TV-5: Fallback Token Failure / Silent Degradation (Medium Severity)

**Description:** Tier 4 fallback (github.token) lacks `actions:write` scope; approval silently fails with HTTP 403 and workflow continues without alerting user.

**Attack Vector:**
- github.token is automatically provided but has minimal scopes (no actions:write)
- Approval attempt will return HTTP 403 Forbidden
- Current error handling may suppress error or log at debug level without alerting
- User assumes approval succeeded (Tier 2-3 tokens were unavailable) but it actually failed

**Current Mitigation:**
- Token chain resolution tries Tier 1-3 before falling back to Tier 4
- Idempotent approval handler (line 189-230) catches HTTP 409/422 errors
- Pre-approval logging shows which token tier will be used

**Validation Approach:**
- Verify Tier 1-3 tokens are present in GitHub Actions environment
- Test: Simulate absence of CODEX_MASTER_KEY and CODEX_BACKUP_KEY secrets; verify workflow fails with explicit error message (not silent HTTP 403)
- Check error logs for HTTP 403 responses from github.token fallback
- Verify workflow status is "failed" (not "success") if all token tiers unavailable

**Enhancement:** Explicit token validation at workflow start:
```yaml
- name: Validate approval token
  run: |
    if [[ -z "${{ secrets.CODEX_MASTER_KEY }}" && -z "${{ secrets.CODEX_BACKUP_KEY }}" ]]; then
      echo "ERROR: No approval token configured. Set CODEX_MASTER_KEY or CODEX_BACKUP_KEY secret."
      exit 1
    fi
```

---

## 2. Token Chain Security Analysis

### 2.1 Token Tier Architecture

| Tier | Source | Scope | Rotation | Exposure Risk | Priority |
|------|--------|-------|----------|---------------|----------|
| **T1** | Cognitive Brain App | `repo`, `workflow`, `actions:write` | 9 min (auto) | Very Low | 1 (Use First) |
| **T2** | CODEX_MASTER_KEY PAT | `repo`, `workflow`, `actions:write` | Manual (None) | High | 2 |
| **T3** | CODEX_BACKUP_KEY PAT | `repo`, `workflow`, `actions:write` | Manual (None) | High | 3 |
| **T4** | github.token | `contents:read`, `statuses:read` | Session | Low | 4 (Fail-Safe) | <!-- pragma: allowlist secret -->

### 2.2 Scope Analysis

**Tier 1 (Cognitive Brain App):** ✅ Properly scoped. App permissions are fine-grained to approval workflow use case. 9-minute auto-rotation ensures compromise window is limited.

**Tier 2-3 (PATs):** ⚠️ Adequate scoping but poor rotation. Scope is minimal (`repo`, `workflow`, `actions:write`—no admin, no delete), but static nature of PATs means compromise = permanent until manual rotation. **Recommendation:** Implement monthly rotation schedule with notification workflow.

**Tier 4 (github.token):** ✅ Properly scoped to fail safe. Token has no `actions:write` scope, so approval will fail (good). However, error handling must be explicit.

### 2.3 Exposure Risk Assessment

| Risk Category | Mitigation | Status |
|---------------|-----------|--------|
| Logging leak (token in error messages) | Explicit masking in approve_pending_runs.py | ⚠️ Needs verification | <!-- pragma: allowlist secret -->
| GitHub secret rotation | GitHub encrypts at rest; audit trail exists | ✅ Adequate | <!-- pragma: allowlist secret -->
| PAT expiration | No expiration set on CODEX_MASTER_KEY; should set 1-year TTL | ❌ Missing |
| Secrets scanning | GitHub Advanced Security should detect leaked PATs | ✅ Enabled (assume) | <!-- pragma: allowlist secret -->
| Scope validation | Test PAT permissions after rotation | ⚠️ Manual process |

### 2.4 Priority Logic Validation

**Implementation location:** scripts/ci/approve_pending_runs.py, lines 105–163

**Flow:**
1. Attempt to mint Cognitive Brain App token (lines 138-146)
2. If unavailable, use CODEX_MASTER_KEY (from secrets)
3. If unavailable, use CODEX_BACKUP_KEY (from secrets)
4. If all unavailable, fallback to github.token (automatic from Actions runtime)
5. Validation: First successful token is used; others are not attempted (efficient)

**Security Implication:** ✅ Correct logic. Highest-trust token is tried first; escalation to static secrets only if app token unavailable; ultimate fallback provides safe degradation.

---

## 3. Approval Logging & Audit Trail

### 3.1 Current Logging Implementation

**File:** .codex/approvals.jsonl (referenced in APPROVAL_DEPENDENCY_MATRIX.md, lines ~245-280)

**Identified Gaps:**
- **Schema undefined:** No formal specification of JSON entry fields (id, timestamp, workflow, run_id, approver, token_tier, approval_status, error_message?)
- **Signing:** No cryptographic signature or HMAC to verify entry authenticity
- **Retention:** No clear policy (90 days? 1 year? Compliance requirement?)
- **Access control:** Unclear who can read/write the file (CODEOWNERS enforcement?)
- **Rotation:** No monthly archive or log rollover mechanism

### 3.2 Recommended Audit Log Schema

```json
{
  "timestamp": "2025-02-21T14:23:45.123Z",
  "event_type": "approval_executed",
  "workflow_id": "auto-approve-workflows.yml",
  "run_id": 12345678,
  "pr_number": 456,
  "target_run_id": 87654321,
  "approver": "github-actions[bot]",
  "token_tier": 2,
  "approval_status": "success",
  "http_status": 200,
  "error_message": null,
  "label_used": "wec:auto-approve",
  "signature": "sha256=abc123..."
}
```

**Signature calculation:** `HMAC-SHA256(json_entry, AUDIT_LOG_SECRET)`

### 3.3 Implementation Checklist

- [ ] Define formal JSON schema for .codex/approvals.jsonl entries
- [ ] Implement HMAC-SHA256 signing for each entry with `AUDIT_LOG_SECRET` (separate from CODEX_MASTER_KEY)
- [ ] Add monthly log rotation to .codex/approvals-archive/{YYYY-MM}.jsonl.gz
- [ ] Restrict write permissions: Only approve_pending_runs.py and CI admin workflows
- [ ] Add read-only job to validate log integrity (fail PR if signature mismatch)
- [ ] Set GitHub Actions secret `AUDIT_LOG_SECRET` with 32-byte random value
- [ ] Document retention policy (recommend 6 years for compliance)

---

## 4. Approval Rules Security Analysis

### 4.1 Rule Types & Security Posture

| Rule Type | Implementation | Security | Risk |
|-----------|----------------|----------|------|
| **Persistent Label** | `wec:auto-approve` on PR | Medium | Bypass if non-maintainer adds label |
| **One-Session Label** | `wec:auto-approve-once` on PR | Medium | Same as above; removes after use |
| **Maintainer-Based** | CODEOWNERS approval check | High | Requires explicit maintainer approval |
| **Time-Window** | Schedule trigger (time-based) | Medium | Could auto-approve at off-hours; may hide issues |

### 4.2 Label Authority Validation

**Gap:** Auto-approve-workflows.yml (line 149-170) does not verify that PR author or label creator has CODEOWNERS write permission.

**Enhancement:** Add upstream check in pull_request event:
```yaml
- name: Check label authority
  if: github.event_name == 'pull_request'
  env:
    PR_LABEL: ${{ github.event.pull_request.labels[*].name }}
  run: |
    python3 scripts/ci/verify_codeowners_for_label.py \
      --repo ${{ github.repository }} \
      --pr ${{ github.event.pull_request.number }} \
      --label wec:auto-approve
```

---

## 5. Attack Scenario Analysis

### Scenario A: Token Compromise → Unauthorized Approvals

**Timeline:**
1. **Day 0, 08:00:** CODEX_MASTER_KEY leaked via typo in GitHub Actions log (accidentally echoed in debug command)
2. **Day 0, 08:15:** Attacker discovers leaked PAT in public workflow run logs
3. **Day 0, 08:30:** Attacker crafts malicious PR, manually triggers auto-approve-workflows via `workflow_dispatch` with `wec:auto-approve` label
4. **Day 0, 08:35:** Malicious PR approved and merged (auto-merge enabled on repository)
5. **Day 0, 09:00:** Compromised code runs in production; sensitive data exfiltrated

**Detection:**
- Approval log shows unusual approver: `github-actions[bot]` instead of human reviewer
- Log timestamp (08:35) misaligns with PR creation (08:30); approval happened too quickly
- GitHub audit log shows PAT used from unusual IP address or time of day
- Secrets scanning alerts on accidentally leaked PAT (post-detection)

**Prevention:**
1. ✅ Implement token rotation (monthly PAT refresh)
2. ✅ Add CI job that prevents `echo $CODEX_MASTER_KEY` (test: grep -r "CODEX_MASTER_KEY" .github/workflows/)
3. ✅ Require human approval (CODEOWNERS) even if auto-approve label present
4. ✅ Enable PR merge restrictions: Require passing branch protection rules before auto-merge allowed
5. ✅ Monitor approval log for anomalies: Alert if approval happens <5 min after PR creation

---

### Scenario B: Cascade Approval Loop (Self-Trigger)

**Timeline:**
1. **Day 0, 14:00:** Auto-approve-workflows.yml completes an approval
2. **Day 0, 14:01:** Approval completion triggers workflow_run event
3. **Day 0, 14:02:** workflow_run event re-triggers auto-approve-workflows (if not guarded)
4. **Day 0, 14:03–14:30:** Cascade loop: approval → workflow_run → approval → workflow_run...
5. **Day 0, 14:30:** GitHub API rate limit exhausted; all subsequent approvals blocked

**Detection:**
- Approval log shows multiple approval entries for same run within seconds
- Workflow run duration increases (execution time × number of cascade iterations)
- API rate limit warning in logs

**Prevention:**
1. ✅ **Self-trigger guard (already implemented):** auto-approve-workflows.yml lines 93-95 check `if: github.actor != 'github-actions[bot]'`
2. ✅ **Concurrency control:** cancel-in-progress: true ensures only 1 approval executes at a time
3. ⚠️ **Validation:** Test by removing self-trigger guard and verifying cascade loop is prevented by concurrency control

---

### Scenario C: Label Bypass by Non-Maintainer

**Timeline:**
1. **Day 0, 10:00:** External contributor opens PR with security fix
2. **Day 0, 10:15:** PR author adds `wec:auto-approve` label (self-approval attempt)
3. **Day 0, 10:20:** Auto-approve-workflows.yml fires; contributor's own PR auto-approved without human review
4. **Day 0, 10:25:** Contributor merges PR via auto-merge
5. **Day 0, 11:00:** Hidden backdoor code merged into production

**Detection:**
- Approval log shows approval without explicit human reviewer signature
- PR timeline shows approval happened immediately after label creation
- GitHub audit log shows label creator = PR author ≠ CODEOWNERS member

**Prevention:**
1. ✅ Add label authority check (see Section 4.2 enhancement)
2. ✅ Enforce CODEOWNERS approval in branch protection rules (supersedes auto-approve workflow)
3. ✅ Remove `auto_merge` capability from external contributors (restrict to maintainers only)
4. ⚠️ Log enhancement: Capture label creator identity in audit entry

---

### Scenario D: Audit Log Deletion / Cover-up

**Timeline:**
1. **Day 0:** Attacker compromises CODEX_MASTER_KEY via social engineering
2. **Day 0:** Attacker uses PAT to approve malicious PR, triggers security incident
3. **Day 1:** Incident response team reviews .codex/approvals.jsonl
4. **Day 1, 14:00:** Attacker gains push access to repository (via compromised PAT or separate attack)
5. **Day 1, 14:05:** Attacker deletes .codex/approvals.jsonl to hide approval record
6. **Day 1, 14:06:** Attacker force-pushes to main to remove the deletion commit
7. **Day 1, 14:07:** Approval trail is now gone; incident appears to have no root cause

**Detection:**
- Git reflog shows rebase/force-push of main branch (unusual event)
- Monitoring system alerts on reflog anomalies
- GitHub audit log shows `push` event to main by attacker account
- Backup of .codex/approvals.jsonl from external storage (if available) shows missing entries

**Prevention:**
1. ✅ Implement append-only logging with HMAC signatures (prevents tampering without detection)
2. ✅ Enable GitHub branch protection: Disallow force-pushes to main (except for administrators)
3. ✅ Archive approvals.jsonl to external storage (e.g., encrypted S3 bucket) on daily schedule
4. ✅ Add monitoring alert: Notify on force-push to main or deletion of .codex/ files
5. ⚠️ Require approval log restore from archive if current log is modified

---

## 6. Compliance & Regulatory Checks

### 6.1 SOC 2 Type II Controls

| Control | Requirement | Status | Gap |
|---------|-------------|--------|-----|
| **AC-1** | User access control (approval authority) | ✅ Implemented (CODEOWNERS check) | Non-maintainer label bypass risk |
| **AC-2** | Change management (approval workflow) | ✅ Implemented (auto-approve-workflows.yml) | No formal change log or review board |
| **AU-1** | Audit logging (approval trail) | ⚠️ Partial (.codex/approvals.jsonl exists) | No formal retention policy; no signing |
| **IR-1** | Incident response (anomaly alerting) | ⚠️ Limited (GitHub audit log only) | No automated alert for unusual approval patterns |
| **UP-1** | User authentication (token validation) | ✅ Implemented (token chain) | Tier 2-3 PAT rotation not enforced | <!-- pragma: allowlist secret -->

**Compliance Status:** ~70% of core controls implemented. Recommend quarterly SOC 2 audits to verify control effectiveness.

### 6.2 HIPAA/PCI Applicability

**Important:** Compliance with HIPAA (Healthcare) or PCI-DSS (Payment) depends on whether the codebase processes protected health information (PHI) or payment card data (PCI). **Assumption:** Unclear from codebase scope—recommend organizational scoping exercise.

**If HIPAA-applicable:**
- **Required:** 6-year audit log retention (current gap: no explicit retention policy)
- **Required:** Access logging for all approval requests (current gap: who accessed the approval logs?)
- **Required:** Token rotation every 90 days (current gap: CODEX_MASTER_KEY never rotated)
- **Required:** Encryption in transit (current: ✅ all GitHub API calls are HTTPS)

**If PCI-DSS-applicable:**
- **Required:** Unique user identification for all approval actions (current gap: github-actions[bot] is shared identity)
- **Required:** Segregation of duties (approval authority separate from code changes)—**Status:** ✅ via CODEOWNERS
- **Required:** Audit log integrity controls (current gap: no HMAC signing)

---

## 7. Security Recommendations

### CRITICAL Priority

1. **CR-1: Token Rotation Policy (Effort: 4 hours)**
   - Create GitHub Actions workflow: `scripts/ci/rotate-approval-tokens.yml`
   - Monthly: Generate new PAT with same scopes as CODEX_MASTER_KEY
   - Verify new PAT works (test approval on canary PR)
   - Update GitHub secret CODEX_MASTER_KEY with new PAT
   - Disable old PAT in GitHub Settings
   - **Success Metric:** PAT age in GitHub UI should reset to 0 days; no approval workflow failures after rotation

2. **CR-2: Audit Log Signing (Effort: 6 hours)**
   - Define JSON schema for .codex/approvals.jsonl (see Section 3.2)
   - Add `AUDIT_LOG_SECRET` GitHub Actions secret (32-byte random string)
   - Update approve_pending_runs.py to HMAC-SHA256 sign each entry
   - Add validation job: Runs on every PR, verifies all audit log entries have valid signatures
   - **Success Metric:** All approval entries have valid signatures; validation job passes

3. **CR-3: Token Validation at Workflow Startup (Effort: 2 hours)**
   - Add explicit check in auto-approve-workflows.yml to verify CODEX_MASTER_KEY exists
   - If missing, fail workflow with clear error message (not silent 403)
   - **Success Metric:** Workflow fails with explicit "CODEX_MASTER_KEY required" message if secret is missing

---

### HIGH Priority

4. **HR-1: Label Authority Enforcement (Effort: 4 hours)**
   - Implement verify_codeowners_for_label.py (see Section 4.2 enhancement)
   - Add to auto-approve-workflows.yml PR event
   - Block auto-approval if label was created by non-CODEOWNERS user
   - Log label creator identity in audit entry
   - **Success Metric:** Non-maintainer label additions block approval; audit log captures label creator

5. **HR-2: Append-Only Audit Logging with Archive (Effort: 8 hours)**
   - Implement monthly log rotation to .codex/approvals-archive/{YYYY-MM}.jsonl.gz
   - Add file permission restrictions: Only approve_pending_runs.py and admin workflows can write
   - Archive encrypted copy to external storage (e.g., S3, GCS) on weekly schedule
   - **Success Metric:** Monthly archives created; no approval entries are modified after creation

6. **HR-3: Anomaly Detection & Alerting (Effort: 6 hours)**
   - Add monitoring job: Check for approval patterns that violate security policy:
     - Approval within <5 min of PR creation
     - Multiple approvals of same run in <10 min window
     - Approval at unusual times (e.g., 02:00 UTC if org is US-based)
   - Send alert to #security-alerts Slack channel on anomaly detection
   - **Success Metric:** Anomaly alerts fire for test scenarios; false positive rate <10%

---

### MEDIUM Priority

7. **MR-1: Rate-Limit Monitoring (Effort: 3 hours)**
   - Log API rate limit remaining quota before/after each approval
   - Alert if quota drops below 100 remaining calls
   - Document approval request rate under normal conditions (baseline)
   - **Success Metric:** Rate-limit logs are present; alert fires if quota exhausted

8. **MR-2: Formal Compliance Audit Schedule (Effort: 2 hours)**
   - Document compliance requirements for org (SOC 2, HIPAA, PCI scope)
   - Create annual compliance audit calendar with quarterly check-ins
   - Assign owner for each control
   - **Success Metric:** Compliance audit schedule is documented and tracked

---

## 8. Implementation Checklist

### Pre-Production Validation (Before Deployment)

- [ ] **Token Chain:**
  - [ ] CR-1: Token rotation workflow created and tested (one manual rotation cycle)
  - [ ] CR-3: Token validation at workflow startup prevents silent 403 failures
  - [ ] Test: Verify Tier 1-3 tokens work; Tier 4 fallback fails explicitly
  
- [ ] **Audit Logging:**
  - [ ] CR-2: All audit log entries have valid HMAC-SHA256 signatures
  - [ ] HR-2: Monthly log rotation to archive directory is automated
  - [ ] HR-2: External archive (S3/GCS) receives encrypted copy weekly
  - [ ] Test: Verify archived logs can be restored and signatures still validate

- [ ] **Approval Rules:**
  - [ ] HR-1: Non-maintainer label additions block auto-approval
  - [ ] Label authority validation job is in place and passing
  - [ ] Test: Contributor adds `wec:auto-approve` label; approval is blocked with clear error

- [ ] **Security Monitoring:**
  - [ ] HR-3: Anomaly detection alerts configured and tested
  - [ ] MR-1: Rate-limit monitoring in place; alert threshold set to 100
  - [ ] Test: Trigger approval anomaly (rapid succession); verify alert fires

- [ ] **Self-Trigger Guard:**
  - [ ] Verify auto-approve-workflows.yml has `if: github.actor != 'github-actions[bot]'` guard
  - [ ] Test: Remove guard temporarily; verify cascade loop is prevented by concurrency control

- [ ] **Documentation:**
  - [ ] Token tier scopes documented in runbook (scripts/ci/APPROVAL_RUNBOOK.md)
  - [ ] Audit log schema defined (JSON schema file in .codex/)
  - [ ] Alert runbook for anomaly scenarios (SOP for responders)

---

### Post-Implementation Validation (1 Month After Deployment)

- [ ] **Token Rotation:**
  - [ ] First automated rotation completes successfully
  - [ ] Old PAT is disabled in GitHub; no approval failures after rotation
  - [ ] Rotation job is scheduled to run monthly (cron: `0 0 1 * *`)

- [ ] **Audit Log Integrity:**
  - [ ] 30+ approval entries logged with valid signatures
  - [ ] No audit log entries are modified (git history shows append-only)
  - [ ] Validation job passes on every PR (100% signature match rate)

- [ ] **Alert Effectiveness:**
  - [ ] Anomaly detection has fired at least once (low false positive rate observed)
  - [ ] All alerts routed to #security-alerts and acknowledged within SLA

- [ ] **Compliance Readiness:**
  - [ ] Quarterly compliance audit completed (SOC 2 controls validated)
  - [ ] Org compliance requirements documented (HIPAA/PCI scope determined)
  - [ ] Control owners assigned for each approval security function

---

## Conclusion

The unified approval hub design demonstrates solid foundational security with proper token tiering, concurrency controls, and self-trigger protection. However, three critical gaps must be addressed before production deployment:

1. **Token rotation** (currently never rotated)
2. **Audit log signing** (currently unsigned and vulnerable to tampering)
3. **Explicit token validation** (Tier 4 fallback fails silently)

With implementation of all CRITICAL and HIGH recommendations, the consolidated approval infrastructure will achieve production-grade security posture suitable for handling 125+ approval decisions per month across 5 critical workflows.

**Approval for Consolidation:** ✅ **Conditional**—Proceed pending completion of CR-1, CR-2, CR-3, and HR-1 within 2 weeks.

---

**Next Steps:**
1. Present findings to approval infrastructure maintainers
2. Prioritize implementation of CRITICAL recommendations
3. Schedule pre-production security testing (2 weeks)
4. Conduct 30-day post-deployment compliance audit

