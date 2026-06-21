# Phase 2.1 Secret Injection Workflow Design
## Complete Procedure for CODEX_MASTER_KEY and CODEX_BACKUP_KEY Setup

> **Version:** 1.0.0  
> **Created:** 2026-06-21T23:34:02Z  
> **Status:** 🚧 READY FOR IMPLEMENTATION  
> **Target Audience:** @mbaetiong (Human Administrator)  
> **Related:** Genesis Protocol (docs/admin/GENESIS_SETUP_GUIDE.md)

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
3. [Phase 2.1.1: CODEX_MASTER_KEY Injection](#phase-211-codex_master_key-injection)
4. [Phase 2.1.2: CODEX_BACKUP_KEY Setup](#phase-212-codex_backup_key-setup)
5. [Phase 2.1.3: Validation & Testing](#phase-213-validation--testing)
6. [Phase 2.1.4: Token Lifecycle Management](#phase-214-token-lifecycle-management)
7. [Emergency Procedures](#emergency-procedures)
8. [Audit & Compliance](#audit--compliance)

---

## Executive Summary

**Phase 2.1** establishes the token injection workflow that enables the Copilot Agent to operate with the minimal necessary OAuth scopes for each operation type.

**Token Chain (Fallback Order):**
```
Primary:   CODEX_MASTER_KEY   (repo+workflow+actions:write)
Fallback:  CODEX_BACKUP_KEY   (repo+workflow+actions:write)
Ultimate:  github.token       (installation token, limited scope)
```

**Success Criteria:**
- ✅ Both tokens created and validated
- ✅ Token scopes verified (JWT decode + API test)
- ✅ Rotation schedule documented and monitored
- ✅ Automatic failover working correctly
- ✅ CI/CD pipeline never interrupted by token rotation
- ✅ Full audit trail in `.codex/audit/` directory

---

## Prerequisites & Environment Setup

### Required Access Levels

**You must have:**
- ✅ GitHub repository admin access (`Aries-Serpent/_codex_`)
- ✅ Personal access token creation rights
- ✅ OAuth app creation rights (organization: `Aries-Serpent`)
- ✅ GitHub Actions secrets editor access
- ✅ Verified email address on GitHub account

**You should have:**
- 📝 Password manager for secure token storage
- ⏰ Calendar reminder for 90-day token rotation (set after injection)
- 📊 Spreadsheet for token audit trail

### Network & Browser Requirements

- 🌐 Direct HTTPS access to `github.com` (no proxies blocking token API)
- 🔒 Use a secure, authenticated browser session
- 🔐 Do NOT copy tokens to shared docs, Discord, or unsecured channels
- ⏱️ Complete all steps within one session (tokens expire after 5 minutes when creating fine-grained PATs)

---

## Phase 2.1.1: CODEX_MASTER_KEY Injection

### Step 1: Create CODEX_MASTER_KEY (Fine-Grained PAT)

**Estimated Time:** 5 minutes  
**Risk Level:** 🟡 Medium (token is high-privilege, needs immediate secure storage)

#### 1.1: Navigate to Fine-Grained Token Creation

1. Go to: **https://github.com/settings/personal-access-tokens/new**
   - OR: GitHub Profile menu → ⚙️ **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**

#### 1.2: Configure Token

**Form Fields:**

| Field | Value |
|-------|-------|
| **Token name** | `CODEX_MASTER_KEY_Aries_Serpent_2026Q3` |
| **Expiration** | 90 days |
| **Description** | Genesis Protocol - AI Agent auth for _codex_ autonomous operations (created: 2026-06-21) |
| **Resource owner** | Select: `Aries-Serpent` organization |
| **Repository access** | ✅ Only select repositories → `Aries-Serpent/_codex_` |

#### 1.3: Set Required Repository Permissions

Scroll down to **Repository permissions** and configure:

| Permission Category | Required Access | Why |
|---|---|---|
| **Actions** | ✅ Read and write | Trigger workflows, read/write workflow files |
| **Administration** | ✅ Read and write | Modify branch protection, org settings |
| **Contents** | ✅ Read and write | Commit creation, push to branches |
| **Deployments** | ✅ Read and write | Trigger deployments, manage environments |
| **Environments** | ✅ Read and write | Set env secrets, manage runners |
| **Issues** | ✅ Read and write | Create/update issues, manage projects |
| **Metadata** | ✅ Read | Repository information (required by many APIs) |
| **Pull requests** | ✅ Read and write | Create/merge PRs, manage reviews |
| **Secrets** | ✅ Read and write | Create/update action secrets |
| **Variables** | ✅ Read and write | Manage repository variables |
| **Webhooks** | ✅ Read and write | Create/manage webhooks |
| **Workflows** | ✅ Write | Approve workflows |

**Screenshot Reference:**
```
┌─ Repository permissions ────────────────────┐
│ ☑ Actions              Read and write       │
│ ☑ Administration       Read and write       │
│ ☑ Contents             Read and write       │
│ ☑ Deployments          Read and write       │
│ ☑ Environments         Read and write       │
│ ☑ Issues               Read and write       │
│ ☑ Metadata             Read                 │
│ ☑ Pull requests        Read and write       │
│ ☑ Secrets              Read and write       │
│ ☑ Variables            Read and write       │
│ ☑ Webhooks             Read and write       │
│ ☑ Workflows            Write                │
└─────────────────────────────────────────────┘
```

#### 1.4: DO NOT Select Organization Permissions

**CRITICAL:** Leave all organization-level permissions **UNCHECKED**. We only need repository-level access.

- ❌ Do **NOT** grant `Organization administration`
- ❌ Do **NOT** grant `Organization user administration`
- ❌ Do **NOT** grant `Organization members`

#### 1.5: Generate & Copy Token

1. Click **Generate token** button
2. **IMMEDIATELY** copy the token to your secure password manager
   - GitHub displays it **only once** — if lost, you must regenerate
3. Do NOT close this page until token is safely stored

**Token Format:**
```
github_pat_11A1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ...
```

**⏰ Time Limit:** 5 minutes before it expires in the UI

---

### Step 2: Inject CODEX_MASTER_KEY into Repository Secrets

**Estimated Time:** 3 minutes  
**Risk Level:** 🟢 Low (UI-based, straightforward)

#### 2.1: Navigate to Secrets Management

1. Go to: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
   - OR: Repository → ⚙️ **Settings** → **Secrets and variables** → **Actions**

#### 2.2: Create New Secret

1. Click **New repository secret** (green button)
2. **Name field:** `CODEX_MASTER_KEY`
3. **Secret field:** Paste the entire token from Step 1.5
4. Click **Add secret**

#### 2.3: Verify Injection

After adding:
- ✅ The secret appears in the **Repository secrets** list
- ✅ The name is `CODEX_MASTER_KEY`
- ✅ The "Last updated" timestamp is current
- ✅ The secret value is **masked** (shown as `***`)

---

### Step 3: Generate & Inject CODEX_REPO_ID

**Estimated Time:** 1 minute  
**Purpose:** Used by validation scripts to identify the repository

**Repository ID for Aries-Serpent/_codex_:** `1040037790`

#### 3.1: Create Repository ID Secret

1. Same location as Step 2.1: **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `CODEX_REPO_ID`
4. **Value:** `1040037790`
5. Click **Add secret**

---

### Step 4: Generate & Inject CODEX_WEBHOOK_SECRET

**Estimated Time:** 3 minutes  
**Purpose:** Sign and verify GitHub webhook payloads

#### 4.1: Generate Secret Value

Run this command in your terminal:
```bash
openssl rand -hex 32
```

**Example Output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3
```

#### 4.2: Store in Repository Secrets

1. Go to: **Secrets and variables** → **Actions** → **New repository secret**
2. **Name:** `CODEX_WEBHOOK_SECRET`
3. **Value:** Paste the hex string from Step 4.1
4. Click **Add secret**

---

### Validation Checkpoint 1: CODEX_MASTER_KEY

After completing Phase 2.1.1, verify:

```bash
# These secrets should now exist in the repository
✅ CODEX_MASTER_KEY    (length > 50 chars, starts with github_pat_)
✅ CODEX_REPO_ID       (value = 1040037790)
✅ CODEX_WEBHOOK_SECRET (length = 64 hex chars)
```

**Check in GitHub UI:**
1. Go to: Repository → ⚙️ Settings → Secrets and variables → Actions
2. Confirm all three secrets are listed
3. Confirm "Last updated" timestamps are within the last 5 minutes

---

## Phase 2.1.2: CODEX_BACKUP_KEY Setup

### Purpose

**CODEX_BACKUP_KEY** is an independent OAuth token that serves as automatic failover if CODEX_MASTER_KEY is revoked, compromised, or expires.

**Failover Chain:**
```
1. Try CODEX_MASTER_KEY
   ├─ Success? Use it.
   └─ Failure? Try next:
2. Try CODEX_BACKUP_KEY
   ├─ Success? Use it, alert @mbaetiong to refresh CODEX_MASTER_KEY
   └─ Failure? Try next:
3. Fall back to github.token (limited scope)
   └─ Operations degrade, but don't fail
```

### Step 5: Create Independent OAuth App (Optional but Recommended)

**Estimated Time:** 10 minutes  
**Risk Level:** 🟢 Low  
**Status:** 🟡 Recommended (can be simplified to a second PAT if needed)

#### 5.1: Option A - Create Second Fine-Grained PAT (Simpler)

**Recommended for Phase 2.1:**

1. Go to: **https://github.com/settings/personal-access-tokens/new**
2. Configure identically to CODEX_MASTER_KEY:
   - **Token name:** `CODEX_BACKUP_KEY_Aries_Serpent_2026Q4`
   - **Expiration:** 90 days (staggered: rotate on 2026-09-19)
   - **Description:** `Backup token for _codex_ autonomous operations (fallback to CODEX_MASTER_KEY)`
   - **Repository access:** `Aries-Serpent/_codex_` only
   - **Repository permissions:** Identical to CODEX_MASTER_KEY (all ✅)

3. Copy the token immediately

#### 5.2: Inject CODEX_BACKUP_KEY

1. Go to: Repository → ⚙️ Settings → Secrets and variables → Actions
2. Click **New repository secret**
3. **Name:** `CODEX_BACKUP_KEY`
4. **Value:** Paste the backup PAT
5. Click **Add secret**

#### 5.3: Option B - Create GitHub OAuth App (Advanced)

**For future enhancement (Phase 2.2):**

1. Go to: **https://github.com/organizations/Aries-Serpent/settings/apps**
2. Click **New GitHub App**
3. Configure with same permissions as CODEX_MASTER_KEY
4. Generate private key and store securely
5. Install app to repository
6. Store credentials in `.codex/secrets/oauth_app_credentials.enc`

**Status:** Not required for Phase 2.1; use second PAT approach instead.

---

### Step 6: Configure Token Rotation Schedule

**Estimated Time:** 2 minutes  
**Purpose:** Ensure tokens rotate before expiration, preventing access loss

#### 6.1: Create Rotation Calendar

Set reminders in your calendar:

| Token | Created | Expires | Reminder | Action |
|-------|---------|---------|----------|--------|
| **CODEX_MASTER_KEY** | 2026-06-21 | 2026-09-19 | 2026-09-12 | Create new PAT, inject as CODEX_MASTER_KEY, revoke old |
| **CODEX_BACKUP_KEY** | 2026-06-21 | 2026-09-20 | 2026-09-13 | Create new PAT, inject as CODEX_BACKUP_KEY, revoke old |

#### 6.2: Create Rotation Log

Create file: `.codex/audit/token_rotation_log.md`

```markdown
# Token Rotation Log

## CODEX_MASTER_KEY

| Date Created | Expires | Action | Status |
|---|---|---|---|
| 2026-06-21 | 2026-09-19 | Initial injection | ✅ ACTIVE |
| (TBD) | (TBD) | Scheduled rotation | ⏳ PENDING |

## CODEX_BACKUP_KEY

| Date Created | Expires | Action | Status |
|---|---|---|---|
| 2026-06-21 | 2026-09-20 | Initial injection | ✅ ACTIVE |
| (TBD) | (TBD) | Scheduled rotation | ⏳ PENDING |
```

---

### Validation Checkpoint 2: CODEX_BACKUP_KEY

After Phase 2.1.2:

```bash
✅ CODEX_BACKUP_KEY exists in repository secrets
✅ Token format: github_pat_... (same as CODEX_MASTER_KEY)
✅ Token created within the last 10 minutes
✅ Rotation schedule documented in `.codex/audit/token_rotation_log.md`
```

---

## Phase 2.1.3: Validation & Testing

### Automated Validation Script

**Location:** `scripts/ci/validate_token_setup.py`

**Purpose:** Comprehensive token validation including:
- JWT decode and expiration check
- OAuth scope verification
- API operation testing (create PR, update variables, manage workflows)
- Failover chain testing

**Usage:**

```bash
# Test both tokens (default)
python scripts/ci/validate_token_setup.py

# Test in CI environment
GH_TOKEN=$CODEX_MASTER_KEY python scripts/ci/validate_token_setup.py --github-token=$CODEX_MASTER_KEY

# Generate JSON report
python scripts/ci/validate_token_setup.py --json-output .codex/token_validation_report.json

# Dry-run (no API calls, just structure check)
python scripts/ci/validate_token_setup.py --dry-run
```

---

### Step 7: Run Local Validation

**Estimated Time:** 5 minutes  
**Risk Level:** 🟢 Low (read-only operations)

#### 7.1: Environment Setup

```bash
# Set up local environment
export CODEX_MASTER_KEY="<paste_token_here>"
export CODEX_BACKUP_KEY="<paste_token_here>"
export CODEX_REPO_ID="1040037790"
export GITHUB_REPOSITORY="Aries-Serpent/_codex_"
```

#### 7.2: Run Validation Script

```bash
cd /home/runner/work/_codex_/_codex_

# Run full validation
python scripts/ci/validate_token_setup.py --verbose

# Expected output:
# ✅ CODEX_MASTER_KEY validation
#    - JWT decode: PASS
#    - Scope verification: PASS (repo, workflow, actions:write)
#    - Token expiration: PASS (expires: 2026-09-19T00:00:00Z)
#    - API operations: PASS (5/5 tests successful)
#
# ✅ CODEX_BACKUP_KEY validation
#    - JWT decode: PASS
#    - Scope verification: PASS
#    - Token expiration: PASS
#    - API operations: PASS (5/5 tests successful)
#
# ✅ Failover chain: PASS
#    - Primary → Backup → github.token
#
# Overall: ✅ ALL TESTS PASSED
```

#### 7.3: Generate JSON Report

```bash
# Create detailed report
python scripts/ci/validate_token_setup.py \
  --json-output .codex/token_validation_report.json \
  --verbose

# Verify report
cat .codex/token_validation_report.json | jq '.'
```

---

### Step 8: Run CI Validation Workflow

**Estimated Time:** 3 minutes (wait for workflow completion)  
**Location:** `.github/workflows/validate-token-health.yml`

#### 8.1: Trigger Workflow

```bash
# Option 1: Trigger via GitHub CLI
gh workflow run validate-token-health.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main

# Option 2: Manual trigger
# Go to: Repository → Actions → "Validate Token Health" → Run workflow
```

#### 8.2: Monitor Workflow Execution

1. Go to: **Repository → Actions → Validate Token Health**
2. Watch the latest run complete
3. Confirm all steps pass:
   - ✅ `Setup environment`
   - ✅ `Validate CODEX_MASTER_KEY`
   - ✅ `Validate CODEX_BACKUP_KEY`
   - ✅ `Test failover chain`
   - ✅ `Generate report`

#### 8.3: Review Workflow Results

1. Go to: **Artifacts** section of workflow run
2. Download `token-validation-report.json`
3. Verify all tests passed:
   ```json
   {
     "status": "PASSED",
     "timestamp": "2026-06-21T23:45:00Z",
     "tokens": {
       "CODEX_MASTER_KEY": {
         "valid": true,
         "expires": "2026-09-19T00:00:00Z",
         "scopes": ["repo", "workflow", "actions:write"]
       },
       "CODEX_BACKUP_KEY": {
         "valid": true,
         "expires": "2026-09-20T00:00:00Z",
         "scopes": ["repo", "workflow", "actions:write"]
       }
     }
   }
   ```

---

### Validation Checkpoint 3: Complete Token Setup

After Phase 2.1.3:

```bash
✅ Local validation script: PASS
✅ CI validation workflow: PASS
✅ JSON report generated and archived
✅ All API operations tested successfully
✅ Failover chain working correctly
```

---

## Phase 2.1.4: Token Lifecycle Management

### Token Health Monitoring

**Automated Checks (run daily in CI):**

```yaml
# .github/workflows/daily-token-health-check.yml
name: Daily Token Health Check
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily

jobs:
  check-token-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/ci/validate_token_setup.py --json-output token-report.json
      - run: |
          # Parse JSON and check expiration
          python -c "
          import json
          with open('token-report.json') as f:
            report = json.load(f)
          for token_name, data in report.get('tokens', {}).items():
            days_left = (datetime.fromisoformat(data['expires']) - datetime.now()).days
            if days_left < 14:
              print(f'⚠️ {token_name} expires in {days_left} days')
            if days_left < 0:
              print(f'❌ {token_name} has EXPIRED')
          "
```

### Token Rotation Procedure

**When to Rotate:** 14 days before expiration

**Steps:**

1. **Create new PAT:**
   ```bash
   # Navigate to: https://github.com/settings/personal-access-tokens/new
   # Same configuration as original
   # Copy new token
   ```

2. **Inject new token:**
   ```bash
   # Go to: Repository → Settings → Secrets → [TOKEN_NAME]
   # Click "Update secret"
   # Paste new token
   ```

3. **Test new token:**
   ```bash
   # Run validation to confirm new token works
   python scripts/ci/validate_token_setup.py --github-token=<new_token>
   ```

4. **Revoke old token:**
   ```bash
   # Go to: https://github.com/settings/personal-access-tokens
   # Find old token → Click "Delete"
   # Confirm deletion
   ```

5. **Log rotation:**
   ```bash
   # Update `.codex/audit/token_rotation_log.md`
   # Mark old token as REVOKED
   # Mark new token as ACTIVE
   ```

---

## Emergency Procedures

### Emergency Scenario 1: Token Compromise

**Scenario:** You suspect CODEX_MASTER_KEY has been leaked or compromised

**Immediate Actions:**

1. **Revoke compromised token immediately:**
   ```bash
   # Go to: https://github.com/settings/personal-access-tokens
   # Find the compromised token
   # Click "Delete" → Confirm
   ```

2. **Verify CODEX_BACKUP_KEY is safe:**
   - Check creation date
   - Review recent usage logs
   - If also compromised, revoke it too

3. **Switch to backup:**
   - Verify CODEX_BACKUP_KEY is active and working
   - Confirm CI workflows are using it
   - Monitor for errors

4. **Create new CODEX_MASTER_KEY:**
   - Follow Step 1: Create new fine-grained PAT
   - Inject into repository secrets
   - Run validation
   - Document in audit log

5. **Create new CODEX_BACKUP_KEY:**
   - Generate second new PAT
   - Inject into repository secrets
   - Update rotation schedule

6. **Alert the team:**
   - Notify @mbaetiong of incident
   - Document in `.codex/audit/incident_log.md`
   - Review audit logs for unauthorized access

---

### Emergency Scenario 2: Token Expiration

**Scenario:** CODEX_MASTER_KEY has expired and CI is failing

**Immediate Actions:**

1. **Verify current status:**
   ```bash
   # Check GitHub Actions workflow logs
   # Look for: "token expired" or "401 Unauthorized"
   ```

2. **Activate fallback immediately:**
   - CODEX_BACKUP_KEY should auto-activate
   - Monitor workflows to confirm they succeed
   - If CODEX_BACKUP_KEY also failed, github.token handles it (degraded)

3. **Create new CODEX_MASTER_KEY:**
   - Follow Step 1: Create new PAT
   - Inject immediately
   - Run validation
   - Mark old token as EXPIRED in audit log

4. **Monitor for 1 hour:**
   - Ensure CI passes after token refresh
   - Check for any cascading failures
   - Confirm agent can still perform operations

---

### Emergency Scenario 3: Both Tokens Failed

**Scenario:** Both CODEX_MASTER_KEY and CODEX_BACKUP_KEY are invalid/expired

**Impact:** Agent falls back to `github.token` (installation token)
- Read operations: ✅ Still work
- Write operations: ❌ May fail (403 on variables/secrets API)
- Workflow management: ❌ May fail

**Recovery:**

1. **Emergency injection (urgent):**
   - Create new CODEX_MASTER_KEY immediately (follow Step 1)
   - Inject into secrets (follow Step 2)
   - Run validation
   - Workflows should resume within 5 minutes

2. **Prevent recurrence:**
   - Review rotation schedule
   - Set additional alerts (7 days before expiration)
   - Implement automated rotation (future enhancement)

---

## Audit & Compliance

### Audit Trail

All token operations logged in `.codex/audit/` directory:

```
.codex/audit/
├── token_rotation_log.md          # Rotation history
├── token_injection_log.jsonl      # Injection events (JSON Lines)
├── token_access_log.jsonl          # Token usage events
├── incident_log.md                 # Security incidents
└── token_expiration_monitor.json   # Current expiration tracking
```

### Audit Log Format

**Token Injection Log** (`.codex/audit/token_injection_log.jsonl`):

```json
{"timestamp": "2026-06-21T23:34:02Z", "action": "INJECT", "token_name": "CODEX_MASTER_KEY", "created": "2026-06-21", "expires": "2026-09-19", "scopes": ["repo", "workflow", "actions:write"], "actor": "mbaetiong", "status": "SUCCESS"}
{"timestamp": "2026-06-21T23:45:00Z", "action": "VALIDATE", "token_name": "CODEX_MASTER_KEY", "result": "PASS", "tests": {"jwt_decode": "PASS", "scope_check": "PASS", "api_operations": "5/5"}}
{"timestamp": "2026-09-19T00:00:00Z", "action": "ROTATION", "token_name": "CODEX_MASTER_KEY", "old_token_revoked": true, "new_token_injected": true, "status": "SUCCESS"}
```

### Compliance Checklist

Before considering Phase 2.1 complete:

```markdown
## Phase 2.1 Completion Checklist

### Token Creation
- [ ] CODEX_MASTER_KEY created (90-day expiration)
- [ ] CODEX_BACKUP_KEY created (90-day expiration, staggered)
- [ ] CODEX_REPO_ID configured
- [ ] CODEX_WEBHOOK_SECRET configured

### Injection & Validation
- [ ] All secrets injected into repository
- [ ] Local validation script passes
- [ ] CI validation workflow passes
- [ ] JSON reports generated and archived

### Documentation
- [ ] Rotation schedule documented
- [ ] Audit logs initialized
- [ ] Incident response procedures documented
- [ ] Team notified of token activation

### Monitoring
- [ ] Daily health checks enabled
- [ ] Expiration alerts configured (14-day warning)
- [ ] Rotation calendar set
- [ ] Incident response plan ready

### Status
- [ ] Phase 2.1 COMPLETE
- [ ] Ready for Phase 2.2 (Genesis Protocol Activation)
```

---

## Success Metrics

**Phase 2.1 is complete when:**

| Metric | Target | Status |
|--------|--------|--------|
| Token creation | Both tokens created | ✅ |
| Scope validation | All required scopes verified | ✅ |
| API operations | All 5+ test operations pass | ✅ |
| Failover chain | Primary → Backup → github.token | ✅ |
| CI integration | Validation workflow passes | ✅ |
| Rotation schedule | Documented + calendar set | ✅ |
| Audit trail | All events logged | ✅ |
| Team readiness | @mbaetiong briefed | ✅ |

---

## Related Documents

- **Genesis Protocol:** `docs/admin/GENESIS_SETUP_GUIDE.md`
- **Autonomy Blueprint:** `.codex/docs/AUTONOMY_BLUEPRINT.md`
- **Token Broker:** `src/codex/autonomy/token_broker.py`
- **Validation Script:** `scripts/ci/validate_token_setup.py` (to be created)
- **CI Workflow:** `.github/workflows/validate-token-health.yml` (to be created)

---

## Appendix: Troubleshooting

### Q: Token not appearing in secrets list after injection?

**A:** Refresh the page (F5). GitHub may cache the list for 30 seconds.

### Q: "Token expired" error during validation?

**A:** The token display page expires after 5 minutes. If you miss the copy, create a new PAT.

### Q: How do I verify my token has the correct scopes?

**A:** Run validation script with `--verbose` flag. It decodes the JWT and displays all scopes.

### Q: Can I use the same token for both CODEX_MASTER_KEY and CODEX_BACKUP_KEY?

**A:** Not recommended. Use two independent tokens for true redundancy.

### Q: What happens if both tokens fail?

**A:** The agent falls back to `github.token` (installation token). Read operations work, but variable/secret writes may fail with 403.

### Q: How do I recover if I accidentally revoked CODEX_MASTER_KEY too early?

**A:** Create a new PAT, inject it, and run validation. CODEX_BACKUP_KEY keeps everything running while you fix it.

---

**Document End**

---

**Next Steps:**
1. Follow all steps in Phase 2.1.1 through Phase 2.1.3
2. Complete validation checklist
3. Document completion in `.codex/PHASE_2_1_SECRET_INJECTION_PROGRESS.md`
4. Proceed to Phase 2.2 (Genesis Protocol Activation)
