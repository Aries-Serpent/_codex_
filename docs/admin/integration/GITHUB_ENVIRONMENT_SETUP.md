# GitHub Environment Setup Guide for MCP Integration

> **Purpose**: Configure GitHub Organization and Repository environment variables/secrets for MCP integration  
> **Audience**: Human Administrators with org/repo admin permissions  
> **Last Updated**: 2024-12-30

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Required Environment Variables](#required-environment-variables)
3. [Required Secrets](#required-secrets)
4. [Configuration Instructions](#configuration-instructions)
5. [Python Helper Script](#python-helper-script)
6. [Verification Steps](#verification-steps)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides step-by-step instructions for configuring GitHub environment variables and secrets required for MCP (Model Context Protocol) integration with GitHub Copilot Agent in the `_codex_` repository.

### Prerequisites

- GitHub account with **admin** access to `Aries-Serpent/_codex_` repository
- Python 3.10+ installed locally (for helper script)
- GitHub Personal Access Token or GitHub App credentials

---

## Required Environment Variables

Environment variables are **non-sensitive** configuration values visible to workflow runs.

### Organization-Level Variables

Configure at: `https://github.com/organizations/Aries-Serpent/settings/variables/actions`

| Variable Name | Type | Purpose | Required | Default Value | Example Value |
|--------------|------|---------|----------|---------------|---------------|
| `CODEX_ENV` | string | Environment identifier | No | `production` | `production`, `staging`, `development` |
| `CODEX_LOG_LEVEL` | string | Logging verbosity | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CODEX_MCP_ENABLED` | boolean | Enable MCP server | No | `true` | `true`, `false` |
| `CODEX_SESSION_LOG_DIR` | string | Session log directory | No | `.codex/sessions` | `.codex/sessions` |
| `CODEX_LOG_DB_PATH` | string | SQLite database path | No | `.codex/logs.db` | `.codex/logs.db` |
| `CODEX_SQLITE_POOL` | integer | Enable SQLite pooling | No | `1` | `0`, `1` |
| `MCP_CACHE_DIR` | string | MCP cache directory | No | `/tmp/mcp-cache` | `/tmp/mcp-cache` |
| `PLAYWRIGHT_BROWSERS_PATH` | string | Playwright browser location | No | `/opt/playwright` | `/opt/playwright`, `~/.cache/ms-playwright` |

### Repository-Level Variables

Configure at: `https://github.com/Aries-Serpent/_codex_/settings/variables/actions`

| Variable Name | Type | Purpose | Required | Default Value | Example Value |
|--------------|------|---------|----------|---------------|---------------|
| `MCP_ENDPOINT` | string | MCP service endpoint | No | `http://localhost:8080` | `http://localhost:8080`, `http://localhost:8080` |
| `MCP_VERSION` | string | MCP protocol version | No | `1.0` | `1.0`, `2.0` |
| `CACHE_WARM_SCHEDULE` | string | Cache warming cron | No | `15 3 * * *` | `15 3 * * *` (3:15 AM daily) |
| `RATE_LIMIT_RPM` | integer | Rate limit (requests/min) | No | `60` | `60`, `100` |
| `CONTEXT_SIZE_LIMIT` | integer | Max context tokens | No | `100000` | `100000`, `128000` |

---

## Required Secrets

Secrets are **sensitive** values encrypted at rest and masked in logs.

### Organization-Level Secrets

Configure at: `https://github.com/organizations/Aries-Serpent/settings/secrets/actions`

| Secret Name | Type | Purpose | Required | How to Generate | Rotation Schedule |
|------------|------|---------|----------|-----------------|-------------------|
| `CODEX_MASTER_KEY` | hex string (32 bytes) | Encryption key for tokens | **Yes** | See Python script below | Every 90 days |
| `CODEX_GHP_TOKEN_BASE64` | base64 string | Base64-encoded GitHub PAT | **Yes** | See Python script below | Every 90 days |
| `CODEX_GHP_TOKEN_CONFIG` | JSON string | Token metadata | No | See Python script below | When token rotated |
| `CODEX_GITHUB_APP_ID` | integer | GitHub App ID | No | From GitHub App settings | N/A (static) |
| `CODEX_GITHUB_APP_PRIVATE_KEY` | PEM string | GitHub App private key | No | Generated when creating App | Every 180 days |
| `MCP_SERVICE_TOKEN` | string | MCP service auth token | No | Generated via `openssl rand -hex 32` | Every 90 days |

### Repository-Level Secrets

Configure at: `https://github.com/Aries-Serpent/_codex_/settings/secrets/actions`

| Secret Name | Type | Purpose | Required | How to Generate | Rotation Schedule |
|------------|------|---------|----------|-----------------|-------------------|
| `PINECONE_API_KEY` | string | Pinecone vector DB API key | No | From Pinecone dashboard | Every 180 days |
| `PLAYWRIGHT_LICENSE_KEY` | string | Playwright commercial license | No | From Playwright purchase | Per license term |

---

## Configuration Instructions

### Step 1: Generate Secrets Using Python Script

1. Download the helper script from this guide (see Python Helper Script section below)
2. Save as `generate_mcp_secrets.py`
3. Run: `python3 generate_mcp_secrets.py`
4. Copy the generated values (displayed in terminal)

### Step 2: Configure Organization-Level Variables

1. Navigate to: https://github.com/organizations/Aries-Serpent/settings/variables/actions
2. Click **"New organization variable"**
3. For each variable in the "Organization-Level Variables" table:
   - **Name**: Enter variable name exactly as shown (case-sensitive)
   - **Value**: Enter value from table or script output
   - **Repository access**: Select **"All repositories"** or specific repositories
   - Click **"Add variable"**

### Step 3: Configure Organization-Level Secrets

1. Navigate to: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
2. Click **"New organization secret"**
3. For each secret in the "Organization-Level Secrets" table:
   - **Name**: Enter secret name exactly as shown (case-sensitive)
   - **Secret**: Paste value from Python script output
   - **Repository access**: Select **"All repositories"** or specific repositories
   - Click **"Add secret"**

### Step 4: Configure Repository-Level Variables

1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
2. Click **"New repository variable"**
3. For each variable in the "Repository-Level Variables" table:
   - **Name**: Enter variable name
   - **Value**: Enter value from table
   - Click **"Add variable"**

### Step 5: Configure Repository-Level Secrets

1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
2. Click **"New repository secret"**
3. For each secret in the "Repository-Level Secrets" table:
   - **Name**: Enter secret name
   - **Secret**: Paste value from Python script or external source
   - Click **"Add secret"**

---

## Python Helper Script

### Script: `generate_mcp_secrets.py`

```python
#!/usr/bin/env python3
"""
GitHub MCP Secrets Generator

Generates secure values for GitHub organization/repository secrets.
Run this script locally and copy-paste the output into GitHub settings.

Usage:
    python3 generate_mcp_secrets.py

Requirements:
    pip install cryptography
"""

import base64
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: cryptography not installed. Some features will be limited.")
    print("   Install with: pip install cryptography")
    CRYPTO_AVAILABLE = False


def generate_master_key() -> str:
    """Generate a 32-byte hex encryption key."""
    return secrets.token_hex(32)


def generate_service_token() -> str:
    """Generate a secure service token."""
    return secrets.token_hex(32)


def encode_github_token(token: str, master_key: str = None) -> Dict[str, str]:
    """
    Encode GitHub Personal Access Token to base64.
    
    Args:
        token: Raw GitHub PAT (e.g., ghp_abc123...)
        master_key: Optional encryption key
    
    Returns:
        Dictionary with encoded token and metadata
    """
    if not token.startswith(('ghp_', 'github_pat_')):
        print("⚠️  Warning: Token doesn't look like a GitHub PAT")
    
    # Base64 encode
    token_bytes = token.encode('utf-8')
    encoded_token = base64.b64encode(token_bytes).decode('utf-8')
    
    # Generate metadata
    expiry_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    config = {
        "created": datetime.now().strftime('%Y-%m-%d'),
        "expires": expiry_date,
        "scopes": ["repo", "workflow", "read:org", "write:discussion"],
        "rotation_schedule": "90 days",
        "encrypted": bool(master_key)
    }
    
    # Optionally encrypt with master key
    if master_key and CRYPTO_AVAILABLE:
        # Use Fernet for symmetric encryption
        fernet_key = base64.urlsafe_b64encode(bytes.fromhex(master_key)[:32])
        cipher = Fernet(fernet_key)
        encrypted_bytes = cipher.encrypt(token_bytes)
        encoded_token = base64.b64encode(encrypted_bytes).decode('utf-8')
        config["encryption_method"] = "fernet"
    
    return {
        "CODEX_GHP_TOKEN_BASE64": encoded_token,
        "CODEX_GHP_TOKEN_CONFIG": json.dumps(config, indent=2)
    }


def generate_github_app_config(app_id: int = None, private_key_path: str = None) -> Dict[str, Any]:
    """
    Generate GitHub App configuration.
    
    Args:
        app_id: GitHub App ID (from App settings)
        private_key_path: Path to private key PEM file
    
    Returns:
        Dictionary with App configuration
    """
    config = {}
    
    if app_id:
        config["CODEX_GITHUB_APP_ID"] = str(app_id)
    else:
        config["CODEX_GITHUB_APP_ID"] = "<ENTER_YOUR_GITHUB_APP_ID>"
    
    if private_key_path:
        try:
            with open(private_key_path, 'r') as f:
                private_key = f.read()
            config["CODEX_GITHUB_APP_PRIVATE_KEY"] = private_key
        except FileNotFoundError:
            config["CODEX_GITHUB_APP_PRIVATE_KEY"] = "<PASTE_PRIVATE_KEY_PEM_HERE>"
    else:
        config["CODEX_GITHUB_APP_PRIVATE_KEY"] = "<PASTE_PRIVATE_KEY_PEM_HERE>"
    
    return config


def print_config_table(config: Dict[str, str], title: str):
    """Print configuration in a readable table format."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print(f"{'=' * 80}\n")
    
    for key, value in config.items():
        # Truncate long values for display
        display_value = value if len(str(value)) < 100 else str(value)[:97] + "..."
        
        print(f"Secret Name:  {key}")
        print(f"Secret Value: {display_value}")
        print(f"{'-' * 80}")
        
        # Also provide copy-paste friendly format
        if len(str(value)) < 100:
            print(f"\n📋 Copy-paste value:\n{value}\n")
        else:
            print(f"\n📋 Copy-paste value (full):\n{value}\n")
    
    print(f"{'=' * 80}\n")


def main():
    """Main script execution."""
    print("\n" + "=" * 80)
    print(" GitHub MCP Secrets Generator for _codex_ Repository")
    print("=" * 80)
    print("\nThis script generates secure values for GitHub secrets.")
    print("Copy the generated values and paste them into GitHub settings.\n")
    
    # Generate master encryption key
    master_key = generate_master_key()
    print(f"✅ Generated CODEX_MASTER_KEY: {master_key}\n")
    
    # Generate MCP service token
    service_token = generate_service_token()
    print(f"✅ Generated MCP_SERVICE_TOKEN: {service_token}\n")
    
    # Prompt for GitHub PAT
    print("\n" + "-" * 80)
    print("GitHub Personal Access Token Setup")
    print("-" * 80)
    print("\n📌 Instructions:")
    print("1. Go to: https://github.com/settings/tokens/new")
    print("2. Select scopes: repo, workflow, read:org, write:discussion")
    print("3. Set expiration: 90 days")
    print("4. Click 'Generate token' and copy the token\n")
    
    github_token = input("Enter your GitHub Personal Access Token (or press Enter to skip): ").strip()
    
    if github_token:
        token_config = encode_github_token(github_token, master_key)
        print("\n✅ Encoded GitHub token successfully!")
    else:
        print("\n⚠️  Skipped GitHub token encoding.")
        token_config = {
            "CODEX_GHP_TOKEN_BASE64": "<GENERATED_AFTER_CREATING_PAT>",
            "CODEX_GHP_TOKEN_CONFIG": json.dumps({
                "created": "<FILL_IN>",
                "expires": "<FILL_IN>",
                "scopes": ["repo", "workflow", "read:org", "write:discussion"]
            }, indent=2)
        }
    
    # GitHub App configuration (optional)
    print("\n" + "-" * 80)
    print("GitHub App Setup (Optional - Recommended for Production)")
    print("-" * 80)
    print("\n📌 To create a GitHub App:")
    print("1. Go to: https://github.com/settings/apps/new")
    print("2. Set permissions as described in GITHUB_MCP_INTEGRATION_GUIDE.md")
    print("3. Generate private key and note the App ID\n")
    
    use_app = input("Do you have a GitHub App? (y/n): ").strip().lower()
    
    if use_app == 'y':
        try:
            app_id = int(input("Enter GitHub App ID: ").strip())
            key_path = input("Enter path to private key PEM file (or press Enter to skip): ").strip()
            app_config = generate_github_app_config(app_id, key_path if key_path else None)
            print("\n✅ GitHub App configuration generated!")
        except ValueError:
            print("\n⚠️  Invalid App ID. Skipping GitHub App configuration.")
            app_config = {}
    else:
        print("\n⚠️  Skipped GitHub App configuration.")
        app_config = {}
    
    # Compile all secrets
    all_secrets = {
        "CODEX_MASTER_KEY": master_key,
        "MCP_SERVICE_TOKEN": service_token,
        **token_config,
        **app_config
    }
    
    # Print configuration tables
    print_config_table(
        {"CODEX_MASTER_KEY": master_key},
        "🔐 Organization Secret: Encryption Key"
    )
    
    print_config_table(
        {
            "CODEX_GHP_TOKEN_BASE64": token_config["CODEX_GHP_TOKEN_BASE64"],
            "CODEX_GHP_TOKEN_CONFIG": token_config["CODEX_GHP_TOKEN_CONFIG"]
        },
        "🔐 Organization Secrets: GitHub Token"
    )
    
    print_config_table(
        {"MCP_SERVICE_TOKEN": service_token},
        "🔐 Organization Secret: MCP Service Authentication"
    )
    
    if app_config:
        print_config_table(
            app_config,
            "🔐 Organization Secrets: GitHub App (Optional)"
        )
    
    # Save to file for reference (optional)
    save_file = input("\nSave configuration to file for reference? (y/n): ").strip().lower()
    
    if save_file == 'y':
        filename = f"mcp_secrets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(" GitHub MCP Secrets Configuration\n")
            f.write(" Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            f.write("=" * 80 + "\n\n")
            f.write("⚠️  WARNING: This file contains sensitive secrets!\n")
            f.write("   - Do NOT commit to git\n")
            f.write("   - Delete after copying to GitHub\n")
            f.write("   - Store securely if archiving\n\n")
            
            for key, value in all_secrets.items():
                f.write(f"{key}:\n{value}\n\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"\n✅ Configuration saved to: {filename}")
        print("⚠️  Remember to delete this file after copying secrets to GitHub!")
    
    print("\n" + "=" * 80)
    print(" Next Steps:")
    print("=" * 80)
    print("\n1. Copy each secret value from above")
    print("2. Navigate to GitHub organization/repository settings")
    print("3. Paste into corresponding secret fields")
    print("4. Verify configuration using verification steps in guide")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
```

### Installation Instructions

1. Save the script above as `generate_mcp_secrets.py`
2. Install dependencies:
   ```bash
   pip install cryptography
   ```
3. Run the script:
   ```bash
   python3 generate_mcp_secrets.py
   ```
4. Follow the interactive prompts
5. Copy-paste the generated values into GitHub settings

---

## Verification Steps

### 1. Verify Variables Are Set

```bash
# In a GitHub Actions workflow, add this step:
- name: Verify Environment Variables
  run: |
    echo "CODEX_ENV: ${{ vars.CODEX_ENV }}"
    echo "CODEX_LOG_LEVEL: ${{ vars.CODEX_LOG_LEVEL }}"
    echo "CODEX_MCP_ENABLED: ${{ vars.CODEX_MCP_ENABLED }}"
    echo "MCP_ENDPOINT: ${{ vars.MCP_ENDPOINT }}"
```

### 2. Verify Secrets Are Accessible

```bash
# In a GitHub Actions workflow, add this step:
- name: Verify Secrets (masked)
  run: |
    if [ -z "${{ secrets.CODEX_MASTER_KEY }}" ]; then
      echo "❌ CODEX_MASTER_KEY not set"
      exit 1
    else
      echo "✅ CODEX_MASTER_KEY is set"
    fi
    
    if [ -z "${{ secrets.CODEX_GHP_TOKEN_BASE64 }}" ]; then
      echo "❌ CODEX_GHP_TOKEN_BASE64 not set"
      exit 1
    else
      echo "✅ CODEX_GHP_TOKEN_BASE64 is set"
    fi
```

### 3. Test Token Decryption

```bash
# In a GitHub Actions workflow:
- name: Test Token Decryption
  env:
    CODEX_GHP_TOKEN_BASE64: ${{ secrets.CODEX_GHP_TOKEN_BASE64 }}
    CODEX_GHP_TOKEN_CONFIG: ${{ secrets.CODEX_GHP_TOKEN_CONFIG }}
  run: |
    python3 -c "
    from scripts.security.copilot_token_decoder import copilot_get_github_token_safe
    token = copilot_get_github_token_safe()
    print('✅ Token decryption successful' if token else '❌ Token decryption failed')
    "
```

### 4. Test MCP Service Connection

```bash
# In a workflow with MCP service container:
- name: Test MCP Connection
  run: |
    curl -f http://localhost:8080/health || (echo "❌ MCP service not reachable" && exit 1)
    echo "✅ MCP service is healthy"
```

---

## Troubleshooting

### Issue: Secret Not Found in Workflow

**Symptom**: Workflow fails with "Secret not found" error

**Solution**:
1. Verify secret is created at correct level (org vs. repo)
2. Check secret name spelling (case-sensitive)
3. Verify repository has access to organization secret
4. Check if secret is available to current branch (branch protection rules)

### Issue: Token Decryption Fails

**Symptom**: `copilot_get_github_token_safe()` returns None

**Solution**:
1. Verify `CODEX_MASTER_KEY` is set correctly
2. Check `CODEX_GHP_TOKEN_BASE64` format (valid base64)
3. Ensure `cryptography` package is installed
4. Check if token was encrypted with same master key

### Issue: MCP Service Won't Start

**Symptom**: Health check fails, container exits

**Solution**:
1. Check container logs: `docker logs <container_id>`
2. Verify all required secrets are set
3. Check GHCR image exists and is accessible
4. Verify port 8080 is not already in use

### Issue: Rate Limit Errors

**Symptom**: GitHub API returns 429 errors

**Solution**:
1. Verify token has correct scopes
2. Check token is not expired
3. Reduce request frequency in workflows
4. Use GraphQL batching for multiple requests

---

## Additional Resources

- [GitHub MCP Integration Guide](./GITHUB_MCP_INTEGRATION_GUIDE.md) - Complete MCP integration documentation
- [Token Security Guide](../security/ADMIN_TOKEN_SETUP.md) - Token encryption and management
- [Copilot Token Usage](../security/COPILOT_TOKEN_USAGE.md) - Using tokens in Copilot workflows
- [GitHub Actions Secrets Docs](https://docs.github.com/en/actions/security-guides/encrypted-secrets) - Official documentation

---

**Last Updated**: 2024-12-30  
**Maintainer**: @mbaetiong  
**Version**: 1.0.0
