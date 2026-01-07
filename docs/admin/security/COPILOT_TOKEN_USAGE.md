# 🤖 Copilot Agent Token Usage Guide

> **Generated**: 2024-12-29  
> **Repository**: Aries-Serpent/_codex_  
> **Audience**: Copilot Agent, Automation Engineers  
> **Security Level**: 🔐🔐🔐🔐🔐 (5/5)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Automatic Token Retrieval](#automatic-token-retrieval)
3. [Integration Patterns](#integration-patterns)
4. [Workflow Examples](#workflow-examples)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)

---

## Overview

The _codex_ repository provides **automatic secure token decryption** for Copilot Agent operations. The system:

- ✅ **Auto-detects** available encryption method
- ✅ **Fallback chain** for reliability (AES → Base64 → Hex → Plaintext)
- ✅ **Zero configuration** required in most cases
- ✅ **Backward compatible** with existing code
- ✅ **Token validation** with SHA-256 verification

---

## Automatic Token Retrieval

### Basic Usage

```python
from scripts.security.copilot_token_decoder import copilot_get_github_token

# Automatically retrieves and decrypts token
token = copilot_get_github_token()

# Use token for GitHub API operations
print(f"Token retrieved: {token[:10]}...")  # Safe to show prefix
```

### Safe Retrieval (No Exception)

```python
from scripts.security.copilot_token_decoder import copilot_get_github_token_safe

# Returns None instead of raising exception
token = copilot_get_github_token_safe()

if token:
    print("✅ Token retrieved successfully")
    # Use token...
else:
    print("⚠️ No token configured, using fallback method")
    # Handle gracefully...
```

### Advanced: Manual Method Selection

```python
from scripts.security.copilot_token_decoder import CodexTokenDecoder

decoder = CodexTokenDecoder()

# Try specific method
token = decoder.get_token(method='base64')

# Or auto-detect
token = decoder.get_token()  # Auto-detects best method
```

---

## Integration Patterns

### Pattern 1: GitHub API Operations

```python
#!/usr/bin/env python3
"""
Copilot script for GitHub API operations
"""
from scripts.security.copilot_token_decoder import copilot_get_github_token
import requests

def main():
    # Get token
    token = copilot_get_github_token()
    
    # Setup headers
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Example: Get user info
    response = requests.get('https://api.github.com/user', headers=headers)
    user = response.json()
    
    print(f"✅ Authenticated as: {user['login']}")
    
    # Example: List repository issues
    response = requests.get(
        'https://api.github.com/repos/Aries-Serpent/_codex_/issues',
        headers=headers
    )
    issues = response.json()
    
    print(f"📋 Found {len(issues)} open issues")

if __name__ == '__main__':
    main()
```

### Pattern 2: PyGithub Integration

```python
#!/usr/bin/env python3
"""
Copilot script using PyGithub library
"""
from scripts.security.copilot_token_decoder import copilot_get_github_token
from github import Github

def main():
    # Get token
    token = copilot_get_github_token()
    
    # Initialize PyGithub
    g = Github(token)
    
    # Get repository
    repo = g.get_repo("Aries-Serpent/_codex_")
    
    # Example operations
    print(f"Repository: {repo.full_name}")
    print(f"Stars: {repo.stargazers_count}")
    
    # List recent commits
    commits = repo.get_commits()
    for commit in commits[:5]:
        print(f"- {commit.sha[:8]}: {commit.commit.message.split()[0]}")

if __name__ == '__main__':
    main()
```

### Pattern 3: Subprocess with gh CLI

```python
#!/usr/bin/env python3
"""
Copilot script using GitHub CLI
"""
from scripts.security.copilot_token_decoder import copilot_get_github_token
import subprocess
import os

def main():
    # Get token
    token = copilot_get_github_token()
    
    # Set environment for gh CLI
    env = os.environ.copy()
    env['GH_TOKEN'] = token
    
    # Example: List pull requests
    result = subprocess.run(
        ['gh', 'pr', 'list', '--repo', 'Aries-Serpent/_codex_'],
        env=env,
        capture_output=True,
        text=True
    )
    
    print("📋 Open Pull Requests:")
    print(result.stdout)

if __name__ == '__main__':
    main()
```

---

## Workflow Examples

### Example 1: Simple Token Usage in Workflow

```yaml
name: Copilot Task Example

on:
  workflow_dispatch:

jobs:
  copilot-task:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install cryptography requests
      
      - name: Execute Copilot task
        env:
          # Use recommended Base64 encoding
          CODEX_GHP_TOKEN_BASE64: ${{ secrets.CODEX_GHP_TOKEN_BASE64 }}
        run: |
          python3 -c "
          from scripts.security.copilot_token_decoder import copilot_get_github_token
          import requests
          
          token = copilot_get_github_token()
          headers = {'Authorization': f'token {token}'}
          
          response = requests.get('https://api.github.com/user', headers=headers)
          print(f'✅ Authenticated as: {response.json()[\"login\"]}')
          "
```

### Example 2: Using AES-256-GCM Encryption

```yaml
name: Copilot Secure Task

on:
  workflow_dispatch:

jobs:
  copilot-secure-task:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install cryptography requests
      
      - name: Execute Copilot task with AES encryption
        env:
          # Use combined AES config (most secure)
          CODEX_GHP_TOKEN_CONFIG: ${{ secrets.CODEX_GHP_TOKEN_CONFIG }}
        run: |
          python3 scripts/copilot_secure_task.py
```

---

## Error Handling

### Handling Missing Token

```python
from scripts.security.copilot_token_decoder import copilot_get_github_token_safe

def main():
    token = copilot_get_github_token_safe()
    
    if not token:
        print("❌ ERROR: No GitHub token configured")
        print("Please configure CODEX_GHP_TOKEN_* secrets")
        print("See: docs/admin/security/ADMIN_TOKEN_SETUP.md")
        return 1
    
    # Continue with token...
    print("✅ Token retrieved successfully")
    return 0

if __name__ == '__main__':
    exit(main())
```

### Handling Decryption Failure

```python
from scripts.security.copilot_token_decoder import CodexTokenDecoder
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    decoder = CodexTokenDecoder()
    
    # Try AES first
    token = decoder.get_token(method='aes_config')
    
    if not token:
        print("⚠️ AES decryption failed, trying Base64...")
        token = decoder.get_token(method='base64')
    
    if not token:
        print("⚠️ Base64 failed, trying plaintext fallback...")
        token = decoder.get_token(method='plaintext')
    
    if not token:
        print("❌ All decryption methods failed")
        return 1
    
    print("✅ Token retrieved via fallback chain")
    return 0

if __name__ == '__main__':
    exit(main())
```

---

## Best Practices

### 1. Never Log or Print Full Token

```python
# ❌ BAD - Exposes token in logs
print(f"Token: {token}")

# ✅ GOOD - Shows only prefix
print(f"Token: {token[:10]}... (length: {len(token)})")
```

### 2. Use Try-Except for Production

```python
try:
    token = copilot_get_github_token()
    # Use token...
except ValueError as e:
    logging.error(f"Token retrieval failed: {e}")
    # Implement fallback or alert...
```

### 3. Validate Token Before Use

```python
from scripts.security.copilot_token_decoder import CodexTokenDecoder

decoder = CodexTokenDecoder()
token = decoder.get_token()

if token and decoder.verify_token(token):
    # Token is valid, proceed
    pass
else:
    # Token is invalid, handle error
    raise ValueError("Invalid or missing token")
```

### 4. Use Environment-Specific Secrets

```yaml
# Different secrets for different environments
environments:
  development:
    CODEX_GHP_TOKEN_BASE64: ${{ secrets.DEV_TOKEN_BASE64 }}
  production:
    CODEX_GHP_TOKEN_CONFIG: ${{ secrets.PROD_TOKEN_CONFIG }}
```

---

## Troubleshooting

### Issue: "No GitHub token found in environment secrets"

**Cause**: No token secrets configured

**Solution**:
```bash
# Verify secrets are set
gh secret list --repo Aries-Serpent/_codex_
# Expected: CODEX_GHP_TOKEN_BASE64 or similar
```

### Issue: "AES decryption unavailable"

**Cause**: `cryptography` library not installed

**Solution**:
```bash
pip install cryptography

# Or in workflow:
- name: Install cryptography
  run: pip install cryptography
```

### Issue: "Token verification failed"

**Cause**: SHA-256 hash mismatch

**Solution**:
1. Regenerate encryption with same token
2. Ensure SHA-256 secret matches
3. Check for whitespace in secret values

---

## Security Considerations

### Token Permissions

Only request minimum required scopes:
- `repo` - Repository access
- `workflow` - Workflow updates
- `read:org` - Read organization data (if needed)

### Token Expiration

Set token expiration (90 days recommended). Implement rotation process.

### Audit Logging

Monitor token usage:
```python
import logging
logging.info(f"Token retrieved at {datetime.now().isoformat()}")
logging.info(f"Token method: {CodexTokenDecoder.detect_encoding_type()}")
```

---

## Support & Resources

**Documentation**:
- Admin Setup Guide: `docs/admin/security/ADMIN_TOKEN_SETUP.md`
- Encryption Tool: `scripts/security/token_encryption_tool.py`
- Decoder Module: `scripts/security/copilot_token_decoder.py`

**GitHub Resources**:
- [GitHub REST API](https://docs.github.com/en/rest)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [GitHub CLI Manual](https://cli.github.com/manual/)

**Contact**:
- Issues: Create with `security` label
- Questions: Repository discussions

---

**Last Updated**: 2024-12-29  
**Version**: 2.0.0  
**Maintainer**: Security Team
