# GitHub Token Regeneration Configuration Guide

> **Last Updated**: 2026-01-26T19:00:00Z  
> **Status**: Active - Token Refreshed  
> **Audience**: Human Admin (@mbaetiong)

---

## 🎯 Overview

This guide provides comprehensive instructions for updating all repository components after GitHub token regeneration. Follow these steps to ensure proper configuration across workflows, scripts, documentation, and agent systems.

---

## 📋 Token Types & Scopes

### Personal Access Token (PAT) - Classic

**Required Scopes:**
- ✅ `repo` (Full control of private repositories)
- ✅ `workflow` (Update GitHub Action workflows)
- ✅ `write:packages` (Upload packages to GitHub Package Registry)
- ✅ `delete:packages` (Delete packages from GitHub Package Registry)
- ✅ `admin:org` (Full control of orgs and teams)
- ✅ `admin:public_key` (Full control of user public keys)
- ✅ `admin:repo_hook` (Full control of repository hooks)
- ✅ `admin:org_hook` (Full control of organization hooks)
- ✅ `gist` (Create gists)
- ✅ `notifications` (Access notifications)
- ✅ `user` (Update ALL user data)
- ✅ `delete_repo` (Delete repositories)
- ✅ `write:discussion` (Read and write team discussions)
- ✅ `read:packages` (Download packages from GitHub Package Registry)
- ✅ `read:org` (Read org and team membership, read org projects)
- ✅ `write:org` (Read and write org and team membership, read and write org projects)
- ✅ `admin:gpg_key` (Full control of user gpg keys)
- ✅ `codespace` (Full control of codespaces)
- ✅ `project` (Full control of projects)
- ✅ `security_events` (Read and write security events)

### Fine-Grained Personal Access Token (Recommended)

**Repository Permissions:**
- ✅ Actions: Read and write
- ✅ Contents: Read and write
- ✅ Issues: Read and write
- ✅ Metadata: Read-only (automatic)
- ✅ Pull requests: Read and write
- ✅ Secrets: Read and write
- ✅ Workflows: Read and write
- ✅ Code scanning alerts: Read and write
- ✅ Dependabot alerts: Read and write
- ✅ Secret scanning alerts: Read and write

**Organization Permissions:**
- ✅ Members: Read-only (for team operations)
- ✅ Administration: Read and write (for org-level operations)

---

## 🔐 Step 1: Generate New Token

### Via GitHub UI

1. Navigate to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)" OR "Fine-grained tokens"
3. **Token Name**: `_codex_-master-key-2026-01-26`
4. **Expiration**: Custom → 1 year (2027-01-26)
5. Select all required scopes (see above)
6. Click "Generate token"
7. **⚠️ CRITICAL**: Copy token immediately (shown only once)

### Via GitHub CLI

```bash
# Generate fine-grained token (recommended)
gh auth token

# Or create PAT via API (requires existing authentication)
gh api -X POST /user/tokens \
  -f note="_codex_ Master Key $(date +%Y-%m-%d)" \
  -f scopes="repo,workflow,admin:org,security_events,write:packages"
```

---

## 🔧 Step 2: Update Repository Secrets

### Method 1: GitHub UI

1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
2. Find existing secret: `CODEX_MASTER_KEY` <!-- pragma: allowlist secret -->
3. Click "Update" (or create if doesn't exist)
4. Paste new token value
5. Click "Update secret"

### Method 2: GitHub CLI (Recommended)

```bash
# Set token as environment variable first
export NEW_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" <!-- pragma: allowlist secret -->

# Update repository secret
gh secret set CODEX_MASTER_KEY \
  --repo Aries-Serpent/_codex_ \
  --body "$NEW_TOKEN"

# Verify secret was updated
gh secret list --repo Aries-Serpent/_codex_ | grep CODEX_MASTER_KEY
```

### Method 3: Using Script

```bash
# Use the repository's secret rotation script
cd /home/runner/work/_codex_/_codex_
python scripts/rotate_github_token.py \
  --token "$NEW_TOKEN" \
  --secret-name CODEX_MASTER_KEY \
  --verify
```

---

## 📝 Step 3: Update Configuration Files

### 3.1 Update `.codex/flags.json`

```bash
# Update token timestamp
jq '.token_last_refreshed = "2026-01-26T19:00:00Z"' .codex/flags.json > .codex/flags.json.tmp
mv .codex/flags.json.tmp .codex/flags.json

# Update token status
jq '.codex_master_key_configured = true' .codex/flags.json > .codex/flags.json.tmp
mv .codex/flags.json.tmp .codex/flags.json
```

### 3.2 Update `.codex/flags.yml`

```yaml
# Update in .codex/flags.yml
token_last_refreshed: "2026-01-26T19:00:00Z"
codex_master_key_configured: true
token_expiry: "2027-01-26T00:00:00Z"
```

### 3.3 Update `.codex/autonomous_agent.yaml`

```yaml
# Update token configuration
github:
  token_secret_name: CODEX_MASTER_KEY
  token_last_rotated: "2026-01-26T19:00:00Z"
  token_rotation_interval_days: 90
```

---

## ✅ Step 4: Verify Token Configuration

### 4.1 Test GitHub API Access

```bash
# Test token has correct permissions
export GITHUB_TOKEN="$NEW_TOKEN"

# Test repository access
gh api /repos/Aries-Serpent/_codex_ | jq '.permissions'

# Test security events access
gh api /repos/Aries-Serpent/_codex_/code-scanning/alerts \
  -H "Accept: application/vnd.github+json" | jq '.[] | {number, state, rule_id}'

# Test workflow access
gh api /repos/Aries-Serpent/_codex_/actions/workflows | jq '.workflows[] | {name, state, path}'

# Test secrets access (list only - cannot read values)
gh api /repos/Aries-Serpent/_codex_/actions/secrets | jq '.secrets[] | .name'
```

### 4.2 Run Validation Scripts

```bash
# Validate token permissions
python scripts/security/validate_token_permissions.py \
  --token "$NEW_TOKEN" \
  --required-scopes repo,workflow,security_events,admin:org

# Test workflow trigger with new token
gh workflow run phase34-codeql-alert-fetch.yml \
  --field max_pages=1 \
  --field severity_filter=all

# Check workflow run status
gh run list --workflow=phase34-codeql-alert-fetch.yml --limit 1
```

### 4.3 Verify Secret Updates in Workflows

```bash
# Trigger test workflow that uses CODEX_MASTER_KEY
gh workflow run test-token-access.yml

# Monitor workflow execution
gh run watch

# Check for permission errors in logs
gh run view --log | grep -i "permission\|403\|401\|unauthorized"
```

---

## 🚀 Step 5: Update Agent Systems

### 5.1 Update Autonomous Agent Configuration

```bash
# Update agent config with new token timestamp
python scripts/autonomous_agent.py update-token-config \
  --timestamp "2026-01-26T19:00:00Z" \
  --expiry "2027-01-26T00:00:00Z"

# Restart agent services (if running)
python scripts/autonomous_agent.py restart --safe-mode
```

### 5.2 Update Cognitive Brain System

```bash
# Update cognitive brain token awareness
python scripts/cognitive/update_token_state.py \
  --status active \
  --last-refreshed "2026-01-26T19:00:00Z"

# Verify cognitive brain can access GitHub API
python scripts/cognitive/test_github_integration.py
```

### 5.3 Update Custom Copilot Agents

Update agent configuration files in `.github/agents/`:

```markdown
# In .github/agents/codeql-alert-resolution-agent.md
## Token Configuration

**Token Secret**: `CODEX_MASTER_KEY`  
**Last Refreshed**: 2026-01-26T19:00:00Z  
**Expiry**: 2027-01-26T00:00:00Z  
**Status**: ✅ Active

## Verification

To verify token access:
\`\`\`bash
gh api /repos/Aries-Serpent/_codex_/code-scanning/alerts --paginate | jq 'length'
\`\`\`
```

---

## 📚 Step 6: Update Documentation

### 6.1 Update Token Status Documents

Update the following documentation files:

1. **`.codex/QUICK_REFERENCE_TOKEN_STATUS.md`**
   - Update "Last Refreshed" timestamp
   - Update "Expiry Date"
   - Update "Status" to ✅ Active

2. **`.codex/HUMAN_ADMIN_REQUIRED_TOKEN_SETUP.md`**
   - Add completion timestamp
   - Mark token setup as complete
   - Document new token generation date

3. **`docs/admin/GENESIS_SETUP_GUIDE.md`**
   - Update token configuration section
   - Add latest token refresh timestamp

### 6.2 Update Workflow Documentation

Update workflow documentation to reflect token configuration:

```bash
# Update workflow README
cat >> .github/workflows/README.md <<EOF

## Token Configuration (Updated: 2026-01-26)

All workflows requiring elevated permissions use the \`CODEX_MASTER_KEY\` secret.

**Last Token Refresh**: 2026-01-26T19:00:00Z  
**Token Expiry**: 2027-01-26T00:00:00Z  
**Next Rotation**: 2026-04-26 (90 days)

**Workflows Using CODEX_MASTER_KEY**:
- phase34-codeql-alert-fetch.yml
- auth-token-rotation.yml
- phase10-automated-secrets-setup.yml

EOF
```

---

## 🔄 Step 7: Test Integration Points

### 7.1 Test Workflow Execution

```bash
# Test Phase 34 workflow (primary use case)
gh workflow run phase34-codeql-alert-fetch.yml \
  --field max_pages=5 \
  --field severity_filter=high

# Wait for completion
sleep 60

# Check results
gh run view --log-failed | head -50

# Verify artifacts created
gh run download --name codeql-alert-inventory
ls -lh codeql-alert-inventory/
```

### 7.2 Test Issue Creation

```bash
# Verify workflow can create issues
gh issue list --label "phase-34" --limit 5

# Test manual issue creation with token
gh issue create \
  --title "[Test] Token Verification $(date +%Y-%m-%d)" \
  --body "Testing CODEX_MASTER_KEY after regeneration" \
  --label "test,token-verification"
```

### 7.3 Test Code Scanning Operations

```bash
# Fetch CodeQL alerts (requires security_events scope)
python scripts/security/fetch_codeql_alerts.py \
  --owner Aries-Serpent \
  --repo _codex_ \
  --state open \
  --max-pages 1 \
  --output-dir /tmp/test-alerts \
  --verbose

# Verify output
cat /tmp/test-alerts/alert_summary.md
```

---

## 🧪 Step 8: Comprehensive Validation

### 8.1 Run Full Test Suite

```bash
# Run token-dependent tests
pytest tests/integration/test_github_token_access.py -v

# Run workflow integration tests
pytest tests/workflows/test_phase34_execution.py -v

# Run security script tests
pytest tests/security/test_codeql_alert_management.py -v
```

### 8.2 Verify All Permissions

Create and run a comprehensive validation script:

```bash
cat > /tmp/validate_all_permissions.sh <<'EOF'
#!/bin/bash
set -e

echo "🔍 Validating GitHub Token Permissions..."
echo "============================================"

# Test each required permission
echo "✅ Testing repo access..."
gh api /repos/Aries-Serpent/_codex_ > /dev/null

echo "✅ Testing workflow access..."
gh api /repos/Aries-Serpent/_codex_/actions/workflows > /dev/null

echo "✅ Testing security events access..."
gh api /repos/Aries-Serpent/_codex_/code-scanning/alerts > /dev/null

echo "✅ Testing issues access..."
gh api /repos/Aries-Serpent/_codex_/issues > /dev/null

echo "✅ Testing pull requests access..."
gh api /repos/Aries-Serpent/_codex_/pulls > /dev/null

echo "✅ Testing secrets access..."
gh api /repos/Aries-Serpent/_codex_/actions/secrets > /dev/null

echo ""
echo "🎉 All permissions validated successfully!"
echo "Token is properly configured."
EOF

chmod +x /tmp/validate_all_permissions.sh
/tmp/validate_all_permissions.sh
```

---

## 📊 Step 9: Update Monitoring & Logging

### 9.1 Log Token Rotation Event

```bash
# Add to change log
cat >> .codex/change_log.md <<EOF

## 2026-01-26T19:00:00Z - GitHub Token Rotated

**Event**: CODEX_MASTER_KEY token regenerated and updated  
**Trigger**: Scheduled rotation / Security update  
**New Expiry**: 2027-01-26T00:00:00Z  
**Verified By**: @mbaetiong

**Components Updated**:
- ✅ Repository secret (CODEX_MASTER_KEY)
- ✅ Configuration files (.codex/flags.json, .codex/flags.yml)
- ✅ Autonomous agent config
- ✅ Cognitive brain system
- ✅ Documentation
- ✅ Workflow integrations

**Validation**:
- ✅ GitHub API access confirmed
- ✅ Workflow execution successful
- ✅ Code scanning operations functional
- ✅ Issue creation tested
- ✅ All permission scopes verified

EOF
```

### 9.2 Update Token Expiry Monitoring

```bash
# Set up token expiry reminder
cat >> .codex/monitoring/token_expiry_check.py <<'EOF'
import datetime

def check_token_expiry():
    """Check if token is approaching expiry."""
    expiry = datetime.datetime(2027, 1, 26, 0, 0, 0, tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    days_until_expiry = (expiry - now).days

    if days_until_expiry <= 30:
        print(f"⚠️ WARNING: Token expires in {days_until_expiry} days!")
        print(f"   Expiry Date: {expiry.isoformat()}")
        print(f"   Action Required: Regenerate token before expiry")
        return False
    else:
        print(f"✅ Token valid for {days_until_expiry} days")
        return True

if __name__ == "__main__":
    check_token_expiry()
EOF

# Run check
python .codex/monitoring/token_expiry_check.py
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Bad credentials" or 401 Errors

**Symptom**: API requests return 401 Unauthorized  
**Cause**: Token not properly updated or has expired  
**Solution**:
```bash
# Verify token is set correctly
gh auth status

# Re-login with new token
gh auth login --with-token < token.txt

# Test API access
gh api /user | jq '.login'
```

#### Issue 2: "Resource not accessible by integration" or 403 Errors

**Symptom**: API requests return 403 Forbidden  
**Cause**: Token missing required scopes  
**Solution**:
```bash
# Check token scopes
gh api /user --include | grep -i "x-oauth-scopes"

# If scopes missing, regenerate token with all required scopes
# Then update secret again (see Step 2)
```

#### Issue 3: Workflow Fails with "Not Found" Error

**Symptom**: Workflow runs but cannot access repository resources  
**Cause**: Workflow using old token or wrong secret name  
**Solution**:
```bash
# Verify secret exists
gh secret list | grep CODEX_MASTER_KEY

# Check workflow uses correct secret name
grep -n "CODEX_MASTER_KEY" .github/workflows/phase34-codeql-alert-fetch.yml

# Re-run workflow
gh workflow run phase34-codeql-alert-fetch.yml
```

#### Issue 4: Token Permissions Inconsistent Between UI and CLI

**Symptom**: Operations work in UI but fail in CLI or workflows  
**Cause**: Different tokens being used  
**Solution**:
```bash
# Ensure same token everywhere
export GITHUB_TOKEN="$NEW_TOKEN"

# Update gh CLI authentication
echo "$NEW_TOKEN" | gh auth login --with-token

# Verify
gh auth status
```

---

## 📅 Token Rotation Schedule

### Recommended Rotation Frequency

- **Standard**: Every 90 iterations (quarterly)
- **High Security**: Every 30 iterations (monthly)
- **Emergency**: Immediately if token compromised

### Next Rotation Date

**Current Token**: 2026-01-26  
**Next Scheduled Rotation**: 2026-04-26 (90 days)  
**Expiry Date**: 2027-01-26 (1 year)

### Rotation Reminder

Set calendar reminders:
- **30 iterations before expiry**: Start planning rotation
- **14 iterations before expiry**: Execute rotation
- **7 iterations before expiry**: Emergency rotation window

---

## 🔗 Related Documentation

- **Token Setup Guide**: `.codex/HUMAN_ADMIN_REQUIRED_TOKEN_SETUP.md`
- **Genesis Setup**: `docs/admin/GENESIS_SETUP_GUIDE.md`
- **Quick Reference**: `.codex/QUICK_REFERENCE_TOKEN_STATUS.md`
- **Security Policy**: `.codex/CODEBASE_AGENCY_POLICY.md`
- **Workflow Documentation**: `.github/workflows/README.md`
- **Agent Configuration**: `.github/agents/README.md`

---

## ✅ Completion Checklist

After completing all steps, verify:

- [ ] New token generated with all required scopes
- [ ] Repository secret `CODEX_MASTER_KEY` updated
- [ ] Configuration files updated (flags.json, flags.yml, autonomous_agent.yaml)
- [ ] GitHub API access verified
- [ ] Workflow execution tested successfully
- [ ] Code scanning operations functional
- [ ] Issue creation tested
- [ ] All documentation updated
- [ ] Change log entry added
- [ ] Token expiry monitoring configured
- [ ] Next rotation date scheduled in calendar
- [ ] Team notified of token update

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-26T19:00:00Z  
**Maintained By**: @mbaetiong  
**Next Review**: 2026-04-26 (before next rotation)

---

**End of Token Regeneration Guide** ✅
