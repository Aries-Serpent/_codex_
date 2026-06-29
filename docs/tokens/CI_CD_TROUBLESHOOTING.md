# CI_CD_TOKEN_TROUBLESHOOTING.md

**Diagnostic Guide for Token-Related CI/CD Failures**

**Document Version**: 1.0.0
**Date**: 2026-02-17
**Target Audience**: DevOps Engineers, CI/CD Maintainers, On-Call Support Engineers

---

## 🎯 Quick Diagnosis Guide

Use this flowchart to identify token-related failures:

```
Start: CI/CD failure detected

├─ Check error message for token-related keywords
│  ├─ "scope" → Go to: Scope Errors
│  ├─ "permission denied" (403) → Go to: Permission Errors
│  ├─ "rate limit" (429) → Go to: Rate Limit Errors
│  ├─ "expired" / "revoked" → Go to: Token Expiration
│  ├─ "invalid token" → Go to: Token Format Issues
│  └─ "401 Unauthorized" → Go to: Token Missing/Invalid

├─ Check if error is in action setup step
│  └─ YES: Token resolution issue

├─ Check if error is in API call
│  └─ YES: Token scope or permission issue

└─ Check failure logs for token environment variables
   └─ Present: Token availability confirmed, focus on permissions
   └─ Absent: Token resolution failed
```

---

## 🔍 Common Token-Related Failures

### Failure 1: "Token scope insufficient for this request"

**Error Message**:
```
Error: Token scope insufficient for this request (403)
Message: Your token has insufficient permissions. Required scope: admin:org_hook
```

**Root Cause**: Using a lower-level token than required for the operation

**Debugging Steps**:

```bash
#!/bin/bash
# 1. Identify which token was used
echo "Step 1: Check which token was used"
TOKEN_VAR=$(grep -i "TOKEN\|secret" workflow.yml | head -1)
echo "Token variable: $TOKEN_VAR"

# 2. Check token's actual scopes
curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/user/scopes \
  | jq '.scopes'

# 3. Check what operation failed
echo "Operation that failed: create_org_variables"

# 4. Check required scopes
echo "Required scopes: admin:org_hook, admin:org, workflow"

# 5. Compare
echo "Conclusion: GITHUB_TOKEN has insufficient scopes"
```

**Solution**:
```python
# ❌ WRONG: Using GITHUB_TOKEN for org variable read
token = os.environ['GITHUB_TOKEN']  # Level 1 - insufficient

# ✅ CORRECT: Use CODEX_BACKUP_KEY or CODEX_MASTER_KEY
from scripts.ci._token_resolver import get_token

token, token_source = get_token(required_elevated=True)
if not token:
    raise Exception("No elevated token available")
```

**Prevention**:
1. Reference TOKEN_HIERARCHY_GUIDE.md for operation requirements
2. Run `enforce_token_patterns.py` on your workflow
3. Add validation step:
   ```python
   if not validate_token_scope(token, ['admin:org_hook']):
       raise PermissionError("Token lacks required scopes")
   ```

---

### Failure 2: "API rate limit exceeded" (429)

**Error Message**:
```
Error: API rate limit exceeded (429 Too Many Requests)
Retry-After: 300
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1708876800
```

**Root Cause**: Exceeded rate limit for token type

**Rate Limits by Token**:
- GITHUB_TOKEN: 1,000 requests/hour (repo scope)
- CODEX_BACKUP_TOKEN: 5,000 requests/hour
- CODEX_MASTER_KEY: 10,000 requests/hour

**Debugging Steps**:

```bash
#!/bin/bash
# 1. Check rate limit headers
echo "Step 1: Check rate limit headers"
curl -i "https://api.github.com/repos/owner/repo" \
  -H "Authorization: token ${TOKEN}" \
  | grep -i "x-ratelimit"

# Output sample:
# X-RateLimit-Limit: 5000
# X-RateLimit-Remaining: 2847
# X-RateLimit-Reset: 1708876800

# 2. Calculate reset time
RESET_TIME=$(curl -s "https://api.github.com/repos/owner/repo" \
  -H "Authorization: token ${TOKEN}" | grep -i "x-ratelimit-reset")

# 3. Check current request rate
echo "Requests made in last hour: $(( 5000 - 2847 ))"

# 4. Identify rate limit consumer
echo "Which workflow steps are making requests?"
grep -r "api.github.com" .github/workflows/ | grep -v "#"
```

**Solution: Implement Exponential Backoff**

```python
import time
import requests

def api_call_with_backoff(url, token, max_retries=5):
    """Make API call with exponential backoff on rate limit."""
    
    for attempt in range(max_retries):
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Check if server provided retry-after
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                wait_time = int(retry_after)
            else:
                # Use exponential backoff: 1, 2, 4, 8, 16 seconds
                wait_time = 2 ** attempt
            
            print(f"Rate limited. Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
            continue
        
        else:
            raise Exception(f"API error: {response.status_code}")
    
    raise Exception("Max retries exceeded")
```

**Prevention**:
1. Use higher-level token if possible (more requests/hour)
2. Batch API calls to reduce total requests
3. Cache results when possible
4. Schedule non-critical operations during low-usage times

---

### Failure 3: "Permission denied" (403) vs "Scope insufficient"

**The Difference**:
- **Scope Insufficient**: Token TYPE lacks permission (e.g., no 'admin:org' scope)
- **Permission Denied**: User/role lacks permission (e.g., not org owner)

**Example**:
```python
# Scope Error (token problem):
# {"message": "This operation requires 'admin:org_hook' scope"}

# Permission Error (role problem):
# {"message": "Must be an owner or member of the organization"}
```

**Debugging to Distinguish**:

```bash
#!/bin/bash
# Check error message
ERROR_MSG="$1"

if echo "$ERROR_MSG" | grep -q "scope\|requires"; then
    echo "✗ Issue: Token scope insufficient"
    echo "  Solution: Use higher-level token"
    echo "  Action: Get CODEX_BACKUP_TOKEN or CODEX_MASTER_KEY"
    
elif echo "$ERROR_MSG" | grep -q "owner\|member\|permission"; then
    echo "✗ Issue: User lacks role permission"
    echo "  Solution: Request org admin role"
    echo "  Action: Contact org admin for access"
    
else
    echo "? Unknown 403 error - check response body"
fi
```

**Solution**:

```python
import requests

def diagnose_403_error(url, token, org):
    """Diagnose whether 403 is scope or permission issue."""
    
    response = requests.get(url, headers={"Authorization": f"token {token}"})
    
    if response.status_code == 403:
        error_msg = response.json().get('message', '')
        
        if 'scope' in error_msg.lower():
            print("🔑 Token scope issue - need elevated token")
            print("   Current token: GITHUB_TOKEN (Level 1)")
            print("   Try with: CODEX_BACKUP_TOKEN (Level 2)")
            return "scope_insufficient"
        
        elif 'permission' in error_msg.lower() or 'owner' in error_msg.lower():
            print("👤 Permission/role issue")
            print("   Current user lacks required org role")
            print("   Contact org admin")
            return "permission_denied"
        
        else:
            print("❓ Unknown 403 error")
            print(f"   Message: {error_msg}")
            return "unknown"
```

---

### Failure 4: "Token expired or revoked"

**Error Messages**:
```
401 Unauthorized
Bad credentials
Token has expired
Token was revoked
```

**Root Causes**:
- GITHUB_TOKEN: Auto-renewed per run (shouldn't expire)
- CODEX_BACKUP_TOKEN: Manually revoked or rotated
- CODEX_MASTER_KEY: Automatically rotated after use

**Debugging Steps**:

```bash
#!/bin/bash
# 1. Validate token format
if [[ ! $TOKEN =~ ^gh(p|o|u|r|s)_ ]]; then
    echo "❌ Token format invalid"
    echo "   Expected: ghp_... or gho_... or ghu_..." <!-- pragma: allowlist secret -->
    echo "   Got: $TOKEN"
    exit 1
fi

# 2. Check token validity
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token ${TOKEN}" \
  https://api.github.com/user)

if [ "$RESPONSE" == "401" ]; then
    echo "❌ Token invalid or revoked"
    echo "   HTTP Status: 401"
    exit 1
elif [ "$RESPONSE" == "200" ]; then
    echo "✅ Token is valid"
else
    echo "⚠️ Unexpected response: $RESPONSE"
fi
```

**Solutions**:

For GITHUB_TOKEN (auto-renewed):
```
1. Automatically renewed in next workflow run
2. No manual action needed
3. Check if workflow was cached or suspended
```

For CODEX_BACKUP_TOKEN:
```
1. Contact repo admin to reissue
2. Token is rotated quarterly
3. Check if token was manually revoked
4. Verify repo has access to the secret
```

For CODEX_MASTER_KEY:
```
1. Automatically managed (shouldn't require manual recovery)
2. Use emergency procedure: request new master key
3. Check rotation logs for token usage
```

**Recovery Script**:
```bash
#!/bin/bash
# Token recovery procedure

TOKEN="${1:?Token required}"
GITHUB_ORG="aries-serpent"

echo "Checking token validity..."

# Test 1: Basic auth
if ! curl -s -H "Authorization: token $TOKEN" \
    https://api.github.com/user > /dev/null 2>&1; then
    echo "❌ Token failed basic auth - revoked or expired"
    echo "Recovery actions:"
    echo "1. For GITHUB_TOKEN: Automatic in next run"
    echo "2. For CODEX_BACKUP_TOKEN: Contact admin"
    echo "3. For CODEX_MASTER_KEY: Emergency procedure"
    exit 1
fi

echo "✅ Token is valid"

# Test 2: Scope check
SCOPES=$(curl -s -H "Authorization: token $TOKEN" \
  https://api.github.com/user \
  | jq '.scopes // []')

echo "Available scopes: $SCOPES"
```

---

## 🔍 Token Resolution Debugging

### How to Check Which Token is Being Used

**Method 1: Environment Variable Inspection**

```bash
# In workflow
- name: Debug token resolution
  run: |
    echo "GITHUB_TOKEN available: $([[ -z "$GITHUB_TOKEN" ]] && echo "NO" || echo "YES")"
    echo "CODEX_BACKUP_TOKEN available: $([[ -z "$CODEX_BACKUP_TOKEN" ]] && echo "NO" || echo "YES")"
    echo "CODEX_MASTER_KEY available: $([[ -z "$CODEX_MASTER_KEY" ]] && echo "NO" || echo "YES")"
```

**Method 2: Token Resolver Debug Output**

```python
# Enable debug logging
import os
os.environ['DEBUG_TOKEN_RESOLVER'] = '1'

from scripts.ci._token_resolver import get_token

token = get_token(operation="read_org_variables")
# Output includes: Which token sources checked, which one used
```

**Method 3: Token Introspection**

```bash
# Check what a token can access
TOKEN="$1"

curl -s -H "Authorization: token $TOKEN" \
  https://api.github.com/user \
  | jq '{login, type, scopes: .scopes}'

# Sample output:
# {
#   "login": "actions",
#   "type": "Bot",
#   "scopes": ["repo", "workflow"]
# }
```

### Debug Logging Activation

**Python Debug Mode**:
```python
import logging
from scripts.ci._token_resolver import get_token

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now get_token() will output detailed debug info
token = get_token(required_level="elevated")
```

**Bash Debug Mode**:
```bash
#!/bin/bash
set -x  # Enable trace output

# All commands and token operations will be logged
source scripts/ci/_token_resolver.sh

TOKEN=$(get_token "elevated")
```

---

## 🚨 Recovery Procedures

### Emergency Token Rotation

**Scenario**: Token compromised or suspected compromise

**Steps**:
```bash
#!/bin/bash
set -euo pipefail

echo "=== EMERGENCY TOKEN ROTATION PROCEDURE ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Step 1: Identify compromised token
COMPROMISED_TOKEN="$1"
echo "Step 1: Identifying compromised token..."

# Step 2: Revoke compromised token
echo "Step 2: Revoking compromised token..."
curl -X DELETE \
  -H "Authorization: token $CODEX_MASTER_KEY" \
  https://api.github.com/user/installations/$(INSTALLATION_ID)/access_tokens

# Step 3: Generate new token
echo "Step 3: Generating new token..."
NEW_TOKEN=$(curl -s -X POST \
  -H "Authorization: token $CODEX_MASTER_KEY" \
  https://api.github.com/app/installations/$(INSTALLATION_ID)/access_tokens \
  | jq -r '.token')

# Step 4: Update secret storage
echo "Step 4: Updating secret storage..."
curl -X PUT \
  -H "Authorization: token $CODEX_MASTER_KEY" \
  https://api.github.com/repos/owner/repo/actions/secrets/NEW_SECRET \
  -d "{\"encrypted_value\": \"$ENCRYPTED_NEW_TOKEN\"}"

# Step 5: Notify team
echo "Step 5: Notifying security team..."
echo "✅ Token rotation completed"
```

---

### Restoring Failed Workflows

**Steps to restore workflow after token failure**:

```bash
#!/bin/bash
# Workflow restoration procedure

WORKFLOW_ID="$1"
RUN_ID="$2"

echo "Restoring failed workflow: $WORKFLOW_ID (Run: $RUN_ID)"

# Step 1: Check if token is available now
echo "Step 1: Checking token availability..."
TOKEN_AVAILABLE=$([[ -z "${CODEX_BACKUP_TOKEN:-}" ]] && echo "NO" || echo "YES")
echo "Token available: $TOKEN_AVAILABLE"

# Step 2: Re-run workflow
if [ "$TOKEN_AVAILABLE" == "YES" ]; then
    echo "Step 2: Re-running workflow..."
    gh workflow run "$WORKFLOW_ID"
    echo "✅ Workflow re-triggered"
else
    echo "❌ Token still unavailable - cannot re-run"
    echo "Recovery options:"
    echo "1. Request token from admin"
    echo "2. Use alternative approach"
    echo "3. Schedule retry with fallback token"
fi

# Step 3: Verify new run
echo "Step 3: Monitoring new run..."
gh run list --workflow="$WORKFLOW_ID" --limit=1 --json status
```

---

## ✅ Prevention Strategies

### Pre-Deployment Validation

**Script to validate before deployment**:
```bash
#!/bin/bash
# Pre-deployment token validation

validate_tokens() {
    echo "Pre-deployment token validation..."
    
    # Check GITHUB_TOKEN
    if [ -z "${GITHUB_TOKEN:-}" ]; then
        echo "❌ GITHUB_TOKEN not set"
        return 1
    fi
    
    # Validate each token format
    for TOKEN in GITHUB_TOKEN CODEX_BACKUP_TOKEN CODEX_MASTER_KEY; do
        VALUE="${!TOKEN:-}"
        if [ -n "$VALUE" ] && [[ ! "$VALUE" =~ ^gh[pours]_ ]]; then
            echo "❌ $TOKEN has invalid format"
            return 1
        fi
    done
    
    echo "✅ All tokens valid"
    return 0
}

validate_tokens || exit 1
```

### Token Scope Verification

```python
from scripts.ci._token_resolver import validate_token_scope

# Verify token has required scopes before operation
required_scopes = ['admin:org_hook', 'repo:full']

if not validate_token_scope(token, required_scopes):
    raise PermissionError(
        f"Token lacks required scopes: {required_scopes}\n"
        f"Use a higher-level token (see TOKEN_HIERARCHY_GUIDE.md)"
    )
```

### Rate Limit Monitoring

```python
import requests

def check_rate_limits(token):
    """Monitor rate limit consumption."""
    
    response = requests.get(
        "https://api.github.com/rate_limit",
        headers={"Authorization": f"token {token}"}
    )
    
    data = response.json()
    core = data['resources']['core']
    
    remaining_pct = (core['remaining'] / core['limit']) * 100
    
    if remaining_pct < 25:
        print(f"⚠️ Rate limit critical: {remaining_pct:.1f}% remaining")
    elif remaining_pct < 50:
        print(f"⚠️ Rate limit warning: {remaining_pct:.1f}% remaining")
    
    return core
```

---

## 📋 Troubleshooting Checklist

When diagnosing token-related failures:

- [ ] **Check Error Message**
  - [ ] Contains "scope"? → Scope Error
  - [ ] Contains "403"? → Permission/Scope Error
  - [ ] Contains "401"? → Token Invalid/Missing
  - [ ] Contains "429"? → Rate Limit
  - [ ] Contains "revoked"? → Token Revoked

- [ ] **Check Token Availability**
  - [ ] GITHUB_TOKEN present? (should always be)
  - [ ] CODEX_BACKUP_TOKEN present? (check repo secrets)
  - [ ] CODEX_MASTER_KEY present? (check auth)

- [ ] **Check Token Validity**
  - [ ] Token format correct? (ghp_... etc) <!-- pragma: allowlist secret -->
  - [ ] Test with curl 401? → Invalid/revoked
  - [ ] Check expiration? (if applicable)

- [ ] **Check Scope Requirements**
  - [ ] Reference TOKEN_HIERARCHY_GUIDE.md
  - [ ] What operation requires what scope?
  - [ ] Is current token insufficient?

- [ ] **Check Rate Limits**
  - [ ] API response 429?
  - [ ] X-RateLimit-Remaining near 0?
  - [ ] Retry-After header present?

---

## 🔗 Related Documentation

- **TOKEN_HIERARCHY_GUIDE.md** - Token selection and scopes
- **SCRIPT_TOKEN_INTEGRATION.md** - Error handling in scripts
- **WORKFLOW_TOKEN_PATTERNS_UPDATE.md** - Workflow patterns
- **scripts/ci/validate_token_setup.py** - Token validation utility

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-17
**Status**: Ready for Use
