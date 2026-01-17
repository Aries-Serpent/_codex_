# Token Rotation Manual Procedure

## Overview

This document provides step-by-step instructions for manually rotating authentication tokens and secrets in the _codex_ repository.

**⚠️ IMPORTANT**: Only execute these procedures with explicit authorization from repository administrators.

---

## Prerequisites

### 1. Required Access
- Repository admin access
- GitHub Personal Access Token with scopes:
  - `repo` (full repository access)
  - `workflow` (update GitHub Actions workflows)
  - `admin:repo_hook` (if webhook secrets are used)

### 2. Required Environment Variables
```bash
export CODEX_MASTER_KEY="<your-master-encryption-key>"
export GITHUB_TOKEN="<your-github-pat>"
export GITHUB_REPOSITORY="Aries-Serpent/_codex_"
```

### 3. Required Dependencies
```bash
pip install PyGithub PyNaCl cryptography requests
```

### 4. Verify Installation
```bash
# Test imports
python3 -c "from github import Github; from cryptography.fernet import Fernet; print('✅ Dependencies OK')"

# Test scripts load
python3 scripts/rotate_jwt_secret.py --help
python3 scripts/github_secrets_sync.py --help
python3 scripts/phase10/automated_secrets_manager.py --help
```

---

## Procedure 1: JWT Secret Rotation

### Purpose
Rotate the JWT signing secret used for authentication token generation.

### Frequency
Monthly (automated via `.github/workflows/auth-token-rotation.yml`)

### Manual Steps

#### Step 1: Backup Current Secret
```bash
# Navigate to repository root
cd /path/to/_codex_

# Verify backup directory exists
mkdir -p .codex/secrets/backups

# Create backup (automatic when rotating)
python3 scripts/rotate_jwt_secret.py
# This will create: .codex/secrets/backups/jwt_secret_<timestamp>.enc
```

#### Step 2: Verify Current Configuration
```bash
# Check if current secret is set
python3 scripts/rotate_jwt_secret.py --verify

# Expected output:
# ✅ TOKEN_SECRET_KEY is set
# ✅ CODEX_MASTER_KEY is set
# ✅ Backup directory exists
```

#### Step 3: Perform Rotation
```bash
# Standard rotation (will backup automatically)
python3 scripts/rotate_jwt_secret.py

# Force rotation (even if recently rotated)
FORCE_ROTATION=true python3 scripts/rotate_jwt_secret.py
```

#### Step 4: Verify New Secret
```bash
# Verify rotation succeeded
python3 scripts/rotate_jwt_secret.py --verify

# Check backup was created
ls -lh .codex/secrets/backups/
```

#### Step 5: Update GitHub Secrets
The script automatically updates GitHub Secrets via API. Verify in GitHub UI:

1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/secrets/actions`
2. Verify `TOKEN_SECRET_KEY` shows "Updated X minutes ago"
3. Check backup secret `TOKEN_SECRET_KEY_BACKUP_<date>` exists

#### Step 6: Test Authentication
```bash
# Test JWT generation with new secret
python3 -c "
import os
from datetime import datetime, timedelta
import jwt

secret = os.getenv('TOKEN_SECRET_KEY')
payload = {
    'sub': 'test-user',
    'exp': datetime.utcnow() + timedelta(hours=1)
}
token = jwt.encode(payload, secret, algorithm='HS256')
print(f'✅ JWT generated: {token[:50]}...')

# Verify token
decoded = jwt.decode(token, secret, algorithms=['HS256'])
print(f'✅ JWT verified: {decoded}')
"
```

### Rollback Procedure

If rotation fails or causes issues:

#### Option A: Automatic Rollback (Recommended)
```bash
# Rollback to most recent backup
python3 scripts/rotate_jwt_secret.py --rollback

# Rollback to specific backup
python3 scripts/rotate_jwt_secret.py --rollback --backup-file jwt_secret_20260117_120000.enc
```

#### Option B: Manual Rollback via GitHub UI
1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/secrets/actions`
2. Find `TOKEN_SECRET_KEY_BACKUP_<date>` secret
3. Copy value
4. Update `TOKEN_SECRET_KEY` with backup value
5. Delete backup secret after confirming restoration

---

## Procedure 2: GitHub Secrets Rotation

### Purpose
Rotate multiple authentication secrets simultaneously.

### Secrets Managed
- `TOKEN_SECRET_KEY` (JWT signing secret)
- `GITHUB_OAUTH_CLIENT_SECRET` (OAuth client secret)
- `SESSION_ENCRYPTION_KEY` (Session encryption key)

### Frequency
Monthly (automated via `.github/workflows/auth-secret-rotation.yml`)

### Manual Steps

#### Step 1: Backup All Secrets
```bash
# Create encrypted backup of all secrets
python3 scripts/github_secrets_sync.py --backup

# Verify backup created
ls -lh .codex/secrets/backups/secrets_backup_*.json.enc
```

#### Step 2: List Secrets to Rotate
```bash
# All secrets (default)
python3 scripts/github_secrets_sync.py --rotate

# Specific secrets only
python3 scripts/github_secrets_sync.py --rotate --secrets "TOKEN_SECRET_KEY,SESSION_ENCRYPTION_KEY"
```

#### Step 3: Perform Rotation
```bash
# Rotate all configured secrets
python3 scripts/github_secrets_sync.py --rotate

# The script will:
# 1. Generate new secrets
# 2. Encrypt with CODEX_MASTER_KEY
# 3. Update GitHub via API
# 4. Create audit trail
```

#### Step 4: Validate New Secrets
```bash
# Validate all secrets are accessible
python3 scripts/github_secrets_sync.py --validate

# Expected output:
# ✅ TOKEN_SECRET_KEY: accessible
# ✅ GITHUB_OAUTH_CLIENT_SECRET: accessible  
# ✅ SESSION_ENCRYPTION_KEY: accessible
```

#### Step 5: Sync to Downstream Systems
```bash
# Sync secrets to dependent systems (if configured)
python3 scripts/github_secrets_sync.py --sync-downstream
```

#### Step 6: Review Audit Trail
```bash
# Check rotation was logged
cat .codex/audit/phase10/secrets-rotation-*.log

# Check GitHub issue was created (if workflow ran)
# Issue will be tagged: security, audit, automated
```

---

## Procedure 3: Manual Secret Injection

### Purpose
Manually set or update individual secrets via Copilot Agent automation.

### Use Cases
- Initial setup of new secrets
- Emergency secret updates
- Testing secret configurations

### Manual Steps

#### Step 1: Generate New Secret (Optional)
```bash
# Generate a new secure secret (32 bytes = 256 bits)
python3 scripts/phase10/automated_secrets_manager.py \
  --action generate-key \
  --name NEW_SECRET_NAME \
  --key-length 32

# The script will:
# 1. Generate cryptographically secure random key
# 2. Display key (save securely!)
# 3. Optionally inject into GitHub Secrets
```

#### Step 2: Set Existing Secret
```bash
# Set secret with specific value
python3 scripts/phase10/automated_secrets_manager.py \
  --action set \
  --name SECRET_NAME \
  --value "your-secret-value" \
  --method api

# Methods:
# - api: Direct GitHub REST API (requires PyNaCl)
# - cli: GitHub CLI (requires `gh` installed)
# - auto: Try API, fallback to CLI (default)
```

#### Step 3: Verify Secret Was Set
```bash
# Verify secret exists in GitHub
python3 scripts/phase10/automated_secrets_manager.py \
  --action verify \
  --name SECRET_NAME

# Expected output:
# ✅ SECRET_NAME exists in GitHub Secrets
```

#### Step 4: List All Secrets
```bash
# List all configured secrets (names only, no values)
python3 scripts/phase10/automated_secrets_manager.py \
  --action list

# Output example:
# Secrets in Aries-Serpent/_codex_:
# - CODEX_MASTER_KEY
# - GITHUB_OAUTH_CLIENT_SECRET
# - SESSION_ENCRYPTION_KEY
# - TOKEN_SECRET_KEY
```

---

## Troubleshooting

### Issue: "CODEX_MASTER_KEY environment variable required"

**Cause**: Master encryption key not set

**Solution**:
```bash
# Set CODEX_MASTER_KEY (get from secure storage)
export CODEX_MASTER_KEY="<your-master-key>"

# Or create new one (ONLY for new setup)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Save output securely!
```

### Issue: "GITHUB_TOKEN required"

**Cause**: GitHub API token not set or invalid

**Solution**:
```bash
# Set GitHub token
export GITHUB_TOKEN="<your-github-pat>"

# Verify token has required scopes
gh api user
# Should return your user info
```

### Issue: "PyGithub not installed"

**Cause**: Missing Python dependencies

**Solution**:
```bash
pip install PyGithub PyNaCl cryptography requests
```

### Issue: Rotation fails midway

**Cause**: Network error, API rate limit, or permission issue

**Solution**:
```bash
# Rollback immediately
python3 scripts/rotate_jwt_secret.py --rollback

# Check audit logs
cat .codex/secrets/backups/*.log

# Review error message and fix underlying issue
# Retry after fixing
```

### Issue: "Resource not accessible by integration"

**Cause**: GitHub token lacks required scopes

**Solution**:
1. Go to: https://github.com/settings/tokens
2. Edit your token
3. Ensure these scopes are checked:
   - `repo` (full control)
   - `workflow` (update workflows)
4. Regenerate token
5. Update `GITHUB_TOKEN` environment variable

---

## Security Best Practices

### 1. Secure Key Storage
- ✅ Store `CODEX_MASTER_KEY` in password manager (1Password, LastPass)
- ✅ Never commit `CODEX_MASTER_KEY` to version control
- ✅ Rotate `CODEX_MASTER_KEY` annually
- ✅ Use different master keys for dev/staging/production

### 2. GitHub Token Hygiene
- ✅ Use fine-grained PATs with minimal scopes
- ✅ Set expiration dates (30-90 days recommended)
- ✅ Rotate tokens regularly
- ✅ Revoke unused tokens immediately

### 3. Backup Management
- ✅ Verify `.codex/secrets/backups/` in `.gitignore`
- ✅ Keep backups encrypted
- ✅ Store off-site backup of `CODEX_MASTER_KEY`
- ✅ Test backup restoration quarterly

### 4. Audit Logging
- ✅ Review rotation logs after each operation
- ✅ Monitor GitHub audit log for secret access
- ✅ Set up alerts for unexpected secret changes
- ✅ Keep rotation logs for compliance (1+ year)

### 5. Emergency Procedures
- ✅ Document rollback steps (see above)
- ✅ Have backup contact for emergencies
- ✅ Test rollback procedure quarterly
- ✅ Keep offline copy of recovery procedures

---

## Automation

### Scheduled Rotations

Automated rotations run via GitHub Actions:

| Workflow | Schedule | Secrets Rotated |
|----------|----------|-----------------|
| `auth-token-rotation.yml` | 1st of month, midnight UTC | TOKEN_SECRET_KEY |
| `auth-secret-rotation.yml` | 1st of month, 2 AM UTC | All auth secrets |

### Manual Trigger

Trigger workflows manually:
1. Go to: https://github.com/Aries-Serpent/_codex_/actions
2. Select workflow (e.g., "Automated Token Rotation")
3. Click "Run workflow"
4. Optionally check "Force rotation"
5. Click green "Run workflow" button

### Audit Trail

After automated rotation:
1. GitHub issue created with `security`, `audit` labels
2. Backup created in `.codex/secrets/backups/`
3. Audit log in `.codex/audit/phase10/`
4. GitHub Security Log entry

---

## Quick Reference

### Common Commands

```bash
# JWT rotation
python3 scripts/rotate_jwt_secret.py              # Rotate
python3 scripts/rotate_jwt_secret.py --verify     # Verify
python3 scripts/rotate_jwt_secret.py --rollback   # Rollback

# Secrets sync
python3 scripts/github_secrets_sync.py --backup   # Backup
python3 scripts/github_secrets_sync.py --rotate   # Rotate all
python3 scripts/github_secrets_sync.py --validate # Validate

# Manual injection
python3 scripts/phase10/automated_secrets_manager.py --action generate-key --name SECRET
python3 scripts/phase10/automated_secrets_manager.py --action set --name SECRET --value VAL
python3 scripts/phase10/automated_secrets_manager.py --action verify --name SECRET
```

### File Locations

```
.codex/
├── secrets/
│   └── backups/          # Encrypted secret backups
│       ├── jwt_secret_<timestamp>.enc
│       └── secrets_backup_<timestamp>.json.enc
└── audit/
    └── phase10/          # Audit logs
        └── secrets-rotation-<timestamp>.log

.github/workflows/
├── auth-token-rotation.yml      # JWT rotation workflow
├── auth-secret-rotation.yml     # Multi-secret rotation
└── phase10-automated-secrets-setup.yml  # Initial setup
```

---

## Support

### Contacts
- **Repository Admin**: mbaetiong
- **Security Team**: (contact via GitHub Issues with `security` label)
- **Emergency**: Create urgent issue with `urgent` + `security` labels

### Documentation
- Testing Report: `docs/token_rotation_testing_report.md`
- Workflow CI Guide: `.github/agents/workflow-ci-fixer.agent.md`
- Cognitive Brain Status: `COGNITIVE_BRAIN_STATUS_V11_WORKFLOW_CI_FIXES.md`

---

**Last Updated**: 2026-01-17  
**Version**: 1.0  
**Status**: Approved for Production Use
