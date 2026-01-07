# 🔐 Admin Token Setup Guide for _codex_

> **Generated**: Previous Cycle-12-29  
> **Repository**: Aries-Serpent/_codex_  
> **Security Level**: 🔐🔐🔐🔐🔐 (5/5)  
> **Roles**: [Org Admin], [Security Officer]

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup Process](#setup-process)
4. [Verification](#verification)
5. [Token Rotation](#token-rotation)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This guide walks administrators through setting up **secure GitHub token storage** for the `_codex_` repository. The system supports multiple security levels:

| Method | Security | Complexity | Recommended |
|--------|----------|------------|-------------|
| **AES-256-GCM** | 🔐🔐🔐🔐🔐 | Medium | ✅ Production |
| **Base64** | 🔐🔐 | Low | Development/Testing |
| **Hex** | 🔐🔐 | Low | Alternative encoding |

---

## Prerequisites

### Required Access

- [x] GitHub Organization Owner or Admin role
- [x] Repository Admin access to `Aries-Serpent/_codex_`
- [x] GitHub CLI (`gh`) installed and authenticated

### Required Tools

```bash
# Check installed tools
gh --version          # GitHub CLI
python3 --version     # Python 3.8+
pip3 --version        # Python package manager

# Install cryptography library (for AES encryption)
pip3 install cryptography
```

---

## Setup Process

### Step 1: Generate GitHub Personal Access Token

1. Navigate to: https://github.com/settings/tokens/new
2. Configure token:
   - **Note**: `_codex_ Copilot Agent Token`
   - **Expiration**: 90 days (recommended)
   - **Scopes**: Select:
     - [x] `repo` (Full control of private repositories)
     - [x] `workflow` (Update GitHub Action workflows)
     - [x] `admin:org` (if org-level operations needed)
3. Click **Generate token**
4. **COPY THE TOKEN** (you won't see it again)

### Step 2: Run Encryption Tool

```bash
# Clone repository if not already done
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install dependencies
pip3 install -r scripts/security/requirements.txt

# Run encryption tool
python3 scripts/security/token_encryption_tool.py

# When prompted, paste your GitHub token
# The tool will generate encrypted values
```

**Example output**:

```
🔐 _CODEX_ TOKEN ENCRYPTION TOOL v2.0
⚡ Energy: 5/5 | 🧠 Security Mode Active
================================================================================

Enter GitHub token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

✅ Encryption complete!

📋 COPY THESE VALUES TO GITHUB SECRETS:

🥇 RECOMMENDED - Base64 Encoding:
   Secret Name:  CODEX_GHP_TOKEN_BASE64
   Secret Value: Z2hwX3h4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4

🔐 MOST SECURE - AES-256-GCM Encryption:
   Secret Name: CODEX_GHP_TOKEN_AES_KEY
   Secret Value: dGVzdGtleXZhbHVlZm9yZGVtb25zdHJhdGlvbnB1cnBvc2VzMTIz
   ...
```

### Step 3: Add Secrets to GitHub

#### Option A: Automated (Recommended)

The encryption tool generates a setup script:

```bash
# Run the generated setup script
bash ~/codex_token_setup.sh
```

#### Option B: Manual via GitHub CLI

```bash
# Set repository secrets using gh CLI
gh secret set CODEX_GHP_TOKEN_BASE64 --body "YOUR_BASE64_VALUE" --repo Aries-Serpent/_codex_

gh secret set CODEX_GHP_TOKEN_AES_KEY --body "YOUR_AES_KEY" --repo Aries-Serpent/_codex_

# Add other secrets as needed...
```

#### Option C: Manual via Web UI

1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
2. Click **New repository secret**
3. For each secret:
   - **Name**: (from encryption tool output)
   - **Value**: (from encryption tool output)
   - Click **Add secret**

---

### Step 4: Revoke Original Token

**CRITICAL**: After verifying the setup works, revoke the original token:

1. Navigate to: https://github.com/settings/tokens
2. Find the token you just created
3. Click **Delete** or **Revoke**
4. Generate a new token if needed for other purposes

---

## Verification

### Test Token Retrieval

```bash
# Method 1: Direct test
python3 -c "
from scripts.security.copilot_token_decoder import copilot_get_github_token_safe
token = copilot_get_github_token_safe()
print('✅ Token retrieved successfully' if token else '❌ Token retrieval failed')
"

# Method 2: Full integration test
python3 scripts/security/copilot_token_decoder.py
```

### Test in Workflow

Trigger a test workflow run:

```bash
gh workflow run copilot-automation.yml --repo Aries-Serpent/_codex_

# Check workflow logs
gh run list --workflow=copilot-automation.yml --limit 1
```

---

## Token Rotation

**Recommendation**: Rotate tokens every 90 days.

### Rotation Process

1. Generate new GitHub token (see Step 1)
2. Run encryption tool with new token
3. Update GitHub secrets with new values
4. Test token retrieval
5. Revoke old token
6. Document rotation in security log

### Automated Rotation (Future Enhancement)

Create calendar reminder or use GitHub Actions scheduled workflow to alert when rotation is due.

---

## Troubleshooting

### Issue: "No GitHub token found in environment secrets"

**Symptoms**: Copilot Agent cannot retrieve token

**Solutions**:
1. Verify secrets are set in repository settings
2. Check secret names match exactly (case-sensitive)
3. Confirm workflow has correct `env:` mapping
4. Test locally with environment variables

```bash
# Test locally
export CODEX_GHP_TOKEN_BASE64="your_base64_value"
python3 scripts/security/copilot_token_decoder.py
```

### Issue: "Token verification failed: invalid format or hash mismatch"

**Symptoms**: Token retrieved but fails validation

**Solutions**:
1. Regenerate encryption with same token
2. Ensure SHA-256 secret is correct
3. Check for whitespace/newlines in secret values
4. Verify token hasn't been revoked

### Issue: "AES decryption unavailable: cryptography library not installed"

**Symptoms**: AES encrypted token cannot be decrypted

**Solutions**:
1. Install cryptography library:
   ```bash
   pip3 install cryptography
   ```
2. Add to workflow:
   ```yaml
   - name: Install cryptography
     run: pip install cryptography
   ```
3. Use Base64 encoding as fallback

---

## Security Best Practices

### Token Permissions

- ✅ Use **least privilege principle** (minimum required scopes)
- ✅ Set **expiration date** (90 days recommended)
- ✅ Enable **SSO/SAML** if available
- ✅ Use **fine-grained tokens** when possible

### Secret Management

- ✅ Never commit tokens to repository
- ✅ Use repository secrets (not hardcoded in workflows)
- ✅ Rotate tokens regularly
- ✅ Revoke compromised tokens immediately
- ✅ Enable audit logging for secret access

### Access Control

- ✅ Limit repository admin access
- ✅ Review secret access logs regularly
- ✅ Use environment protection rules
- ✅ Enable branch protection with required reviews

---

## Support & Resources

**Documentation**:
- Encryption Tool: `scripts/security/token_encryption_tool.py`
- Decoder Module: `scripts/security/copilot_token_decoder.py`
- Copilot Usage Guide: `docs/admin/security/COPILOT_TOKEN_USAGE.md`

**GitHub Resources**:
- [Creating a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

**Contact**:
- Security Issues: Create issue with `security` label
- General Questions: Discussion board

---

**Last Updated**: Previous Cycle-12-29  
**Version**: 2.0.0  
**Maintainer**: Security Team
