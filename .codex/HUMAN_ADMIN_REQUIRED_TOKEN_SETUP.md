# Human Admin Required Actions - Token Configuration & Setup
# Critical Prerequisites for AI Agent Continuation

**Date:** 2025-12-27T21:40:00Z
**Priority:** P0 - BLOCKING
**Estimated Time:** 15-30 minutes
**Repository:** Aries-Serpent/_codex_
**Branch:** copilot/sub-pr-2623-one-more-time

---

## ⚠️ CRITICAL: Missing Tokens & Configuration

The comprehensive audit has identified that while the codebase has **NO restrictions** on token usage, the following tokens are **NOT YET CONFIGURED** and must be set up before AI Agent can proceed with advanced operations.

---

## 🔑 Required Token Setup (BLOCKING)

### Token 1: CODEX_MASTER_KEY ❌ NOT CONFIGURED

**Status:** Missing - Must be created and injected
**Purpose:** Master encryption key for repository-level operations
**Scope Required:** `repo`, `read:org`, `workflow`
**Type:** Repository Secret

#### How to Create & Inject:

```bash
# Step 1: Generate secure random key
CODEX_MASTER_KEY=$(openssl rand -base64 32)

# Step 2: Inject via GitHub UI
# Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
# Click "New repository secret"
# Name: CODEX_MASTER_KEY
# Value: [paste generated key]
# Click "Add secret"

# Alternative: Via GitHub CLI (if you have a PAT)
echo "$CODEX_MASTER_KEY" | gh secret set CODEX_MASTER_KEY --repo Aries-Serpent/_codex_
```

**Verification:**
```bash
# List repository secrets (won't show values)
gh secret list --repo Aries-Serpent/_codex_ | grep CODEX_MASTER_KEY
```

**Expected Output:** `CODEX_MASTER_KEY	Updated YYYY-MM-DD`

---

### Token 2: ORG_MASTER_KEY ❌ NOT CONFIGURED

**Status:** Missing - Must be created and injected
**Purpose:** Organization-wide admin access for cross-repository operations
**Scope Required:** `admin:org`, `repo`, `workflow`, `admin:repo_hook`, `write:packages`
**Type:** Organization Secret (preferred) OR Repository Secret

#### How to Create:

**Option A: Create GitHub Personal Access Token (Classic)**
1. Navigate to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Token name: `ORG_MASTER_KEY - Codex Automation`
4. Expiration: 90 days (set up rotation reminder)
5. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages` (Upload packages)
   - ✅ `delete:packages` (Delete packages)
   - ✅ `admin:org` (Full control of orgs)
   - ✅ `admin:repo_hook` (Full control of repository hooks)
6. Click "Generate token"
7. **IMPORTANT:** Copy token immediately (won't be shown again)

**Option B: Create GitHub App (Recommended for Production)**
1. Navigate to: https://github.com/organizations/Aries-Serpent/settings/apps/new
2. App name: `Codex Automation App`
3. Homepage URL: `https://github.com/Aries-Serpent/_codex_`
4. Webhook: Disable (not needed)
5. Repository permissions:
   - Actions: Read & Write
   - Administration: Read & Write
   - Contents: Read & Write
   - Metadata: Read-only
   - Secrets: Read & Write
   - Workflows: Read & Write
6. Organization permissions:
   - Administration: Read & Write
   - Members: Read
7. Create app and generate private key
8. Install app on Aries-Serpent organization

#### How to Inject:

**For Organization Secret (Recommended):**
```bash
# Via GitHub UI
# Navigate to: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
# Click "New organization secret"
# Name: ORG_MASTER_KEY
# Value: [paste token]
# Repository access: Selected repositories → Choose Aries-Serpent/_codex_
# Click "Add secret"

# Via GitHub CLI
echo "your-org-master-token" | gh secret set ORG_MASTER_KEY \
  --org Aries-Serpent \
  --repos Aries-Serpent/_codex_
```

**For Repository Secret (Alternative):**
```bash
# Via GitHub UI
# Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
# Click "New repository secret"
# Name: ORG_MASTER_KEY
# Value: [paste token]

# Via GitHub CLI
echo "your-org-master-token" | gh secret set ORG_MASTER_KEY --repo Aries-Serpent/_codex_
```

**Verification:**
```bash
# For organization secret
gh api /orgs/Aries-Serpent/actions/secrets | jq '.secrets[] | select(.name=="ORG_MASTER_KEY")'

# For repository secret  
gh secret list --repo Aries-Serpent/_codex_ | grep ORG_MASTER_KEY
```

---

### Token 3: GITHUB_TOKEN ✅ AVAILABLE (But Limited)

**Status:** Available in regular GitHub Actions, NOT in Copilot Agent sessions
**Purpose:** Standard GitHub Actions authentication
**Scope:** Automatic (based on workflow permissions)
**Type:** Automatic token

**Current Limitation:**
- ✅ Available in regular workflow runs
- ❌ NOT available in Copilot Agent interactive sessions
- This is BY DESIGN, not a configuration issue

**No Action Required** - This token is automatically provided by GitHub Actions in regular workflow contexts.

---

## 🔧 Additional Configuration (RECOMMENDED)

### Configuration 1: Larger Runners

**Status:** Organization settings required
**Purpose:** Enable resource-intensive operations (large-scale testing, ML training)

**Steps:**
1. Navigate to: https://github.com/organizations/Aries-Serpent/settings/actions/runners
2. Click "New runner" → "New GitHub-hosted runner"
3. Select runner size:
   - **Recommended:** `ubuntu-latest-8-cores` (8 CPU, 32GB RAM)
   - **Alternative:** `ubuntu-latest-16-cores` (16 CPU, 64GB RAM)
4. Set usage limits and cost controls
5. Add runner group: "codex-intensive-operations"
6. Assign to repository: Aries-Serpent/_codex_

**Verification:**
```bash
gh api /repos/Aries-Serpent/_codex_/actions/runners
```

---

### Configuration 2: Organization Audit Logging

**Status:** Should be enabled for compliance
**Purpose:** Track all organization and repository activities

**Steps:**
1. Navigate to: https://github.com/organizations/Aries-Serpent/settings/audit-log
2. Enable audit log streaming (if available in your plan)
3. Configure retention: 90 days minimum
4. Set up log forwarding to SIEM (optional)

**Verification:**
```bash
gh api /orgs/Aries-Serpent/audit-log?per_page=1
```

---

### Configuration 3: Dependabot Alerts & Updates

**Status:** Verify configuration
**Purpose:** Automated dependency security

**Steps:**
1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/security_analysis
2. Verify enabled:
   - ✅ Dependency graph
   - ✅ Dependabot alerts  
   - ✅ Dependabot security updates
   - ✅ Dependabot version updates
3. Check `.github/dependabot.yml` configuration

**Verification:**
```bash
cat .github/dependabot.yml
gh api /repos/Aries-Serpent/_codex_/vulnerability-alerts
```

---

## 📋 Post-Configuration Checklist

After completing the above configurations, verify each item:

### Token Verification:
- [ ] CODEX_MASTER_KEY appears in repository secrets list
- [ ] ORG_MASTER_KEY appears in organization or repository secrets list
- [ ] Test workflow can access CODEX_MASTER_KEY
- [ ] Test workflow can access ORG_MASTER_KEY

### Configuration Verification:
- [ ] Larger runners (if configured) appear in runner list
- [ ] Audit logging is enabled and capturing events
- [ ] Dependabot alerts are enabled and working

### Testing:
```bash
# Test CODEX_MASTER_KEY access
gh workflow run test-codex-master-key.yml

# Test ORG_MASTER_KEY access
gh workflow run test-org-master-key.yml

# Check workflow run status
gh run list --limit 5
```

---

## 🔄 Token Rotation Schedule

**IMPORTANT:** Set up token rotation reminders

### CODEX_MASTER_KEY Rotation:
- **Frequency:** Monthly (automated via workflow)
- **Workflow:** `.github/workflows/automated-token-rotation.yml`
- **Manual Trigger:** `gh workflow run automated-token-rotation.yml`

### ORG_MASTER_KEY Rotation:
- **Frequency:** Every 90 days (manual)
- **Process:**
  1. Generate new PAT with same scopes
  2. Update ORG_MASTER_KEY secret
  3. Test access with sample workflow
  4. Revoke old PAT
  5. Document in `.codex/key-archive/rotation-log.txt`

**Set Calendar Reminder:**
- [ ] Reminder for 2025-03-27: Rotate ORG_MASTER_KEY
- [ ] Reminder for 2025-04-27: Rotate ORG_MASTER_KEY
- [ ] Reminder for 2025-05-27: Rotate ORG_MASTER_KEY

---

## 📊 Expected Timeline

| Task | Estimated Time | Complexity |
|------|----------------|------------|
| Generate CODEX_MASTER_KEY | 2 minutes | Low |
| Inject CODEX_MASTER_KEY | 3 minutes | Low |
| Create ORG_MASTER_KEY (PAT) | 5 minutes | Medium |
| Inject ORG_MASTER_KEY | 3 minutes | Low |
| Configure larger runners | 10 minutes | Medium |
| Enable audit logging | 5 minutes | Low |
| Verify all configurations | 10 minutes | Low |
| **Total** | **~40 minutes** | **Low-Medium** |

---

## 🚨 Common Issues & Solutions

### Issue 1: "Secret not found" in workflow
**Cause:** Secret name mismatch or incorrect scope
**Solution:** 
```bash
# List all secrets
gh secret list --repo Aries-Serpent/_codex_

# Verify exact name (case-sensitive)
# Re-inject if needed
```

### Issue 2: "Insufficient permissions" when using ORG_MASTER_KEY
**Cause:** PAT missing required scopes
**Solution:**
- Regenerate PAT with ALL required scopes
- Verify scopes: `repo`, `admin:org`, `workflow`, `admin:repo_hook`

### Issue 3: Workflow can't access organization secret
**Cause:** Repository not in allowed list
**Solution:**
```bash
# Update secret visibility
gh api \
  -X PUT \
  /orgs/Aries-Serpent/actions/secrets/ORG_MASTER_KEY/repositories/1040037790
```

---

## 📞 Support & Documentation

**Reference Documents:**
- Comprehensive Audit: `.codex/TOKEN_USAGE_AUDIT_COMPREHENSIVE.md`
- Workflow Templates: `.codex/WORKFLOW_TEMPLATES_ADVANCED_TOKEN_USAGE.md`
- GitHub Docs: https://docs.github.com/en/actions/security-guides/encrypted-secrets

**For Questions:**
- Check audit report first
- Review workflow templates
- Consult GitHub documentation
- Test with minimal workflow before production use

---

## ✅ Completion Confirmation

Once all configurations are complete, confirm by running:

```bash
# Run verification workflow
gh workflow run verify-token-configuration.yml

# Check results
gh run view --log

# Expected output:
# ✅ CODEX_MASTER_KEY: accessible
# ✅ ORG_MASTER_KEY: accessible  
# ✅ Permissions: verified
# ✅ Configuration: complete
```

**After successful verification, notify AI Agent to continue with:**
- Comment on PR #2623: `@copilot Tokens configured. Continue with AI Agent follow-up documented in .codex/AI_AGENT_FOLLOWUP_AFTER_TOKEN_SETUP.md`

---

**Document Status:** Ready for Human Admin Action
**Next Step:** AI Agent continuation after token setup
**Priority:** P0 - Blocking all advanced automation
**Created:** 2025-12-27T21:40:00Z
