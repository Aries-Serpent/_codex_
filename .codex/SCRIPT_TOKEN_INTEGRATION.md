# SCRIPT TOKEN INTEGRATION GUIDE

**How Scripts Should Use Token Utilities in CODEX_MASTER_KEY**

**Document Version**: 1.0.0
**Date**: 2026-02-17
**Target Audience**: Script Authors, Python/Bash Developers, DevOps Engineers

---

## 🎯 Overview

This guide explains how to properly integrate the CODEX_MASTER_KEY token utility into your scripts. It covers import patterns, error handling, logging, and best practices for both Python and Bash scripts.

### Token Utility Architecture

**Core Components**:
- `scripts/ci/_token_resolver.py` - Core token resolution logic (Python)
- `validate_token_scope()` - Pre-operation scope validation
- `get_token()` - Retrieve appropriate token with fallback
- Token search order: Environment variables → Context → Fallback

**Token Resolution Strategy**:
```
1. Check CODEX_MASTER_KEY (emergency/critical)
2. Check CODEX_BACKUP_TOKEN (elevated)
3. Check GITHUB_TOKEN (standard)
4. Check PAT_TOKEN (backup standard)
```

---

## 📦 Python Import Patterns

### Pattern 1: Basic Token Retrieval

**Import Statement**:
```python
from scripts.ci._token_resolver import get_token

# Most basic usage
token = get_token()

# With error handling
token = get_token(operation="read_org_variables", required_level="elevated")
if not token:
    raise RuntimeError("No suitable token available")
```

### Pattern 2: Scope Validation

**Import and Validate Before Operation**:
```python
from scripts.ci._token_resolver import get_token, validate_token_scope

def perform_admin_operation():
    token = get_token(required_level="critical")
    
    # Validate scope before proceeding
    required_scopes = ['admin:org', 'workflow', 'repo:full']
    if not validate_token_scope(token, required_scopes):
        raise PermissionError(
            f"Token lacks required scopes: {required_scopes}\n"
            f"Use CODEX_MASTER_KEY or CODEX_BACKUP_TOKEN"
        )
    
    # Proceed with operation
    return perform_operation(token)
```

### Pattern 3: Context-Aware Token Resolution

**Get Token with Operational Context**:
```python
from scripts.ci._token_resolver import get_token

def create_repository_variable(owner, repo, name, value):
    """Create a repo variable with appropriate token."""
    
    # Token resolver picks appropriate level based on context
    token = get_token(
        operation="create_repository_variable",
        context={
            "owner": owner,
            "repo": repo,
            "scope": "repository"  # Repo-level → Level 1 sufficient
        }
    )
    
    if not token:
        raise RuntimeError("Token resolution failed")
    
    # Make API call
    import requests
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
    response = requests.post(
        url,
        headers={"Authorization": f"token {token}"},
        json={"name": name, "value": value}
    )
    
    return response.json()
```

### Pattern 4: Fallback with Multiple Attempts

**Graceful Degradation Strategy**:
```python
from scripts.ci._token_resolver import get_token

def perform_operation_with_fallback(priority_levels=['critical', 'elevated', 'standard']):
    """Try operation with multiple token levels."""
    
    for level in priority_levels:
        token = get_token(required_level=level)
        
        if not token:
            continue
        
        try:
            result = perform_api_operation(token)
            return result
        
        except PermissionError:
            # Insufficient scope - try next level
            continue
        
        except Exception as e:
            # Unexpected error - raise
            raise RuntimeError(f"Operation failed: {e}")
    
    raise RuntimeError("No suitable token available after all attempts")
```

---

## 🛠️ Common Python Integration Examples

### Example 1: GitHub API Call with Proper Error Handling

**Complete Script with Error Handling**:
```python
#!/usr/bin/env python3
"""
Script: Read organization variables with CODEX_MASTER_KEY token utility.
Purpose: Demonstrate proper token integration in scripts.
"""

import os
import sys
import json
import logging
import requests
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import token utility
try:
    from scripts.ci._token_resolver import get_token, validate_token_scope
except ImportError:
    logger.error("Failed to import token resolver. Ensure scripts/ci/ is in PYTHONPATH")
    sys.exit(1)


def read_org_variables(org_name: str) -> Optional[List[Dict]]:
    """
    Read organization variables using appropriate token level.
    
    Args:
        org_name: Organization name (e.g., 'aries-serpent')
    
    Returns:
        List of variables or None on error
    
    Raises:
        PermissionError: If token lacks required scope
        RuntimeError: If token resolution fails
    """
    
    logger.info(f"Reading organization variables for {org_name}")
    
    # Get token with appropriate level for org read
    token = get_token(
        operation="read_org_variables",
        required_level="elevated"  # Level 2+ needed
    )
    
    if not token:
        raise RuntimeError("Token resolution failed: no suitable token available")
    
    # Validate token has required scope
    required_scopes = ['admin:org_hook', 'repo:full']
    if not validate_token_scope(token, required_scopes):
        raise PermissionError(
            f"Token lacks required scopes: {required_scopes}\n"
            f"Request CODEX_BACKUP_TOKEN or CODEX_MASTER_KEY"
        )
    
    logger.debug("Token validation passed")
    
    try:
        # Make API request
        url = f"https://api.github.com/orgs/{org_name}/actions/variables"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        logger.debug(f"Making request to {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        # Handle response
        if response.status_code == 200:
            variables = response.json().get('variables', [])
            logger.info(f"Successfully read {len(variables)} organization variables")
            return variables
        
        elif response.status_code == 403:
            logger.error("Access forbidden. Token may lack required scope.")
            raise PermissionError("Token scope insufficient for org variable read")
        
        elif response.status_code == 404:
            logger.error(f"Organization not found: {org_name}")
            raise ValueError(f"Organization not found: {org_name}")
        
        elif response.status_code == 429:
            logger.error("Rate limit exceeded. Try again later.")
            raise RuntimeError("GitHub API rate limit exceeded")
        
        else:
            logger.error(f"Unexpected HTTP status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise RuntimeError(f"API error: {response.status_code}")
    
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise RuntimeError(f"Failed to read organization variables: {e}")


def main():
    """Main entry point."""
    
    org_name = os.environ.get("GITHUB_ORG", "aries-serpent")
    
    try:
        variables = read_org_variables(org_name)
        
        if variables:
            logger.info("\nOrganization Variables:")
            for var in variables:
                logger.info(f"  - {var['name']} (created: {var['created_at']})")
        
        logger.info("Operation completed successfully")
        return 0
    
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        return 1
    
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

### Example 2: Script with Scope Validation Before Operation

**Scope Checking Pattern**:
```python
#!/usr/bin/env python3
"""
Script: Create repository variable with pre-operation scope validation.
"""

import os
import sys
import requests
import logging
from scripts.ci._token_resolver import get_token, validate_token_scope

logger = logging.getLogger(__name__)


def create_repo_variable_safe(owner: str, repo: str, name: str, value: str):
    """Create repo variable with comprehensive validation."""
    
    # Determine minimum token level needed
    min_level = "standard"  # Level 1 for repo operations
    
    # Get token
    token = get_token(
        operation="create_repository_variable",
        required_level=min_level
    )
    
    if not token:
        raise RuntimeError("No token available")
    
    # Pre-operation validation
    logger.info("Validating token scope before operation...")
    required_scopes = ['repo', 'actions:write']
    
    if not validate_token_scope(token, required_scopes):
        # If standard token fails, try elevated
        logger.warning("Standard token insufficient, requesting elevated token")
        token = get_token(required_level="elevated")
        
        if not validate_token_scope(token, required_scopes):
            raise PermissionError(f"Token lacks scope: {required_scopes}")
    
    logger.info("Token validation passed. Proceeding with operation.")
    
    # Perform operation
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
    headers = {"Authorization": f"token {token}"}
    
    response = requests.post(
        url,
        headers=headers,
        json={"name": name, "value": value}
    )
    
    if response.status_code in [201, 204]:
        logger.info(f"Variable '{name}' created successfully")
        return True
    else:
        logger.error(f"Failed to create variable: {response.status_code}")
        return False


# Run example
if __name__ == "__main__":
    create_repo_variable_safe(
        owner="aries-serpent",
        repo="_codex_",
        name="EXAMPLE_VAR",
        value="example_value"
    )
```

---

## 📝 Bash Integration Patterns

### Pattern 1: Basic Bash Script with Token

**Simple Bash Integration**:
```bash
#!/bin/bash
set -euo pipefail

# Get token using token resolver (Python via subprocess)
get_token() {
    local level="${1:-standard}"
    python3 -c "
from scripts.ci._token_resolver import get_token
token = get_token(required_level='$level')
print(token or '')
"
}

# Use token in API call
TOKEN=$(get_token "elevated")

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to obtain token"
    exit 1
fi

# Make API call
curl -X GET \
    -H "Authorization: token ${TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/owner/repo/actions/variables"
```

### Pattern 2: Bash with Error Handling

**Robust Bash Integration**:
```bash
#!/bin/bash
set -euo pipefail

# Helper: Get token with logging
get_token_with_logging() {
    local level="${1:-standard}"
    local token
    
    echo "[INFO] Requesting token level: $level" >&2
    
    token=$(python3 -c "
import sys
from scripts.ci._token_resolver import get_token
token = get_token(required_level='$level')
if token:
    print(token)
else:
    sys.exit(1)
" 2>/dev/null || echo "")
    
    if [ -z "$token" ]; then
        echo "[ERROR] Failed to obtain $level token" >&2
        return 1
    fi
    
    echo "[INFO] Successfully obtained token" >&2
    echo "$token"
}

# Helper: Make API call with error handling
api_call() {
    local method="$1"
    local url="$2"
    local token="$3"
    local data="${4:-}"
    
    local args=(-X "$method" -H "Authorization: token ${token}")
    
    if [ -n "$data" ]; then
        args+=(-H "Content-Type: application/json" -d "$data")
    fi
    
    local response
    response=$(curl -s -w "\n%{http_code}" "${args[@]}" "$url")
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ] || [ "$http_code" -eq 204 ]; then
        echo "$body"
        return 0
    else
        echo "[ERROR] API call failed with status $http_code" >&2
        echo "[ERROR] Response: $body" >&2
        return 1
    fi
}

# Main operation
main() {
    local owner="aries-serpent"
    local repo="_codex_"
    
    # Get token
    local token
    token=$(get_token_with_logging "elevated") || exit 1
    
    # Make API call
    local url="https://api.github.com/repos/${owner}/${repo}/actions/variables"
    
    if api_call GET "$url" "$token"; then
        echo "[INFO] Successfully retrieved variables"
    else
        echo "[ERROR] Failed to retrieve variables"
        exit 1
    fi
}

main "$@"
```

---

## 🚨 Error Handling Best Practices

### Best Practice 1: Catch and Log Token Errors Safely

**✅ Correct Error Handling**:
```python
try:
    token = get_token(required_level="elevated")
    if not token:
        logger.error("Token resolution failed for elevated level")
        logger.info("Falling back to standard level token")
        token = get_token(required_level="standard")

except Exception as e:
    # Log error details safely (NO TOKEN VALUES)
    logger.error(f"Unexpected error during token resolution: {type(e).__name__}")
    logger.debug(f"Error details: {e}")
    raise
```

**❌ Wrong - Exposes Token Information**:
```python
try:
    # DON'T DO THIS!
    logger.error(f"Token resolution failed: {token}")
except Exception as e:
    # DON'T DO THIS!
    logger.error(f"Token operation failed: {e} using token {token}")
```

### Best Practice 2: Distinguishing Error Types

**Handle Different Error Scenarios**:
```python
from scripts.ci._token_resolver import get_token, validate_token_scope

def safe_api_operation():
    try:
        # Get token
        token = get_token(required_level="elevated")
        
        if not token:
            raise RuntimeError("Token resolution exhausted all options")
        
        # Validate scope
        if not validate_token_scope(token, ['admin:org']):
            raise PermissionError("Token lacks required 'admin:org' scope")
        
        # Perform operation
        result = api_call(token)
        return result
    
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        logger.info("Consider requesting elevated token access")
        raise
    
    except RuntimeError as e:
        logger.error(f"Token resolution failed: {e}")
        logger.info("Ensure CODEX_BACKUP_TOKEN or GITHUB_TOKEN is set")
        raise
    
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            logger.error("API returned 403 Forbidden - likely insufficient scope")
        elif e.response.status_code == 429:
            logger.error("Rate limited - implement backoff")
        raise
```

---

## 🔐 Safe Logging Patterns

### Pattern: Log Operations Without Exposing Tokens

**Safe Logging Example**:
```python
import logging
from scripts.ci._token_resolver import get_token

logger = logging.getLogger(__name__)


def perform_operation(operation_name):
    """Perform operation with safe logging."""
    
    # Get token
    token = get_token()
    token_hash = hash(token) if token else None
    
    # ✅ GOOD: Log without token value
    logger.info(f"Starting operation: {operation_name}")
    logger.debug(f"Token hash: {token_hash}")  # Useful for debugging without exposing
    
    # ✅ GOOD: Include context
    logger.info(f"Using token for GitHub API call")
    
    # Make API call
    try:
        result = make_api_call(token, operation_name)
        logger.info(f"Operation '{operation_name}' completed successfully")
        return result
    
    except Exception as e:
        # ✅ GOOD: Log error without token
        logger.error(f"Operation '{operation_name}' failed: {type(e).__name__}")
        logger.debug(f"Error details: {e}")
        raise


# Configure detailed logging for debugging
def setup_debug_logging():
    """Enable debug logging for troubleshooting."""
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    # ✅ GOOD: Detailed debug info without secrets
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

---

## ✅ Anti-Patterns to Avoid

### Anti-Pattern 1: Hardcoding Tokens

**❌ WRONG**:
```python
# NEVER DO THIS!
GITHUB_TOKEN = "ghp_1234567890abcdef"
CODEX_MASTER_KEY = "ghp_secret_token_here"

requests.get(
    url,
    headers={"Authorization": f"token {GITHUB_TOKEN}"}
)
```

**✅ CORRECT**:
```python
from scripts.ci._token_resolver import get_token

token = get_token()
requests.get(
    url,
    headers={"Authorization": f"token {token}"}
)
```

---

### Anti-Pattern 2: Storing Tokens in Logs

**❌ WRONG**:
```python
logger.info(f"Using token {token} for API call to {url}")
print(f"DEBUG: Token is {token}")
```

**✅ CORRECT**:
```python
logger.info(f"Making API call to {url}")
token_indicator = "***" if token else "none"
logger.debug(f"Token present: {token_indicator}")
```

---

### Anti-Pattern 3: Token String Interpolation in Commands

**❌ WRONG**:
```python
# Token visible in process list!
os.system(f"curl -H 'Authorization: token {token}' {url}")
```

**✅ CORRECT**:
```python
import subprocess
import requests

# Use requests library (token not in process list)
response = requests.get(url, headers={"Authorization": f"token {token}"})

# Or: Pass token via stdin/env
env = os.environ.copy()
env['API_TOKEN'] = token
subprocess.run(['curl', '-H', 'Authorization: token ${API_TOKEN}', url], env=env)
```

---

### Anti-Pattern 4: Not Handling Elevated Token Fallback

**❌ WRONG**:
```python
# Fails if standard token insufficient
token = get_token(required_level="standard")
result = perform_admin_operation(token)  # Will fail with 403
```

**✅ CORRECT**:
```python
# Try elevated, fall back gracefully
for level in ["elevated", "standard"]:
    token = get_token(required_level=level)
    try:
        result = perform_operation(token)
        return result
    except PermissionError:
        continue

raise RuntimeError("No suitable token available")
```

---

## 🧪 Testing Token Integration

### Test Pattern 1: Mock Token Resolver

**Testing with Mock Tokens**:
```python
import unittest
from unittest.mock import patch, MagicMock
from my_script import perform_operation


class TestTokenIntegration(unittest.TestCase):
    """Test script with token resolver mocking."""
    
    @patch('scripts.ci._token_resolver.get_token')
    def test_operation_with_elevated_token(self, mock_get_token):
        """Test operation with mocked elevated token."""
        
        # Mock token resolver to return test token
        mock_get_token.return_value = "test_token_level_2"
        
        # Perform operation
        result = perform_operation()
        
        # Verify token was requested with correct level
        mock_get_token.assert_called_with(required_level="elevated")
        
        # Verify result
        self.assertIsNotNone(result)
    
    @patch('scripts.ci._token_resolver.get_token')
    def test_operation_with_fallback(self, mock_get_token):
        """Test fallback when elevated token insufficient."""
        
        # Mock resolver to fail first, succeed second
        mock_get_token.side_effect = [None, "test_token_level_1"]
        
        # Operation should succeed with fallback
        result = perform_operation()
        
        # Verify both token levels were attempted
        self.assertEqual(mock_get_token.call_count, 2)
```

### Test Pattern 2: Integration Test with Real Token

**Testing with Real Tokens** (CI environment):
```python
def test_with_real_token():
    """Test with actual GitHub token (CI environment only)."""
    
    import os
    
    # Only run in CI
    if not os.environ.get('GITHUB_ACTIONS'):
        pytest.skip("Real token test only in CI")
    
    from scripts.ci._token_resolver import get_token
    
    # Get real token
    token = get_token()
    assert token is not None
    
    # Test basic connectivity
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    
    assert response.status_code == 200
```

---

## 📋 Integration Checklist for New Scripts

When adding token integration to a script, verify:

- [ ] **Import Correct Module**
  ```python
  from scripts.ci._token_resolver import get_token, validate_token_scope
  ```

- [ ] **Get Token with Error Handling**
  ```python
  token = get_token(operation="...", required_level="...")
  if not token:
      raise RuntimeError("Token resolution failed")
  ```

- [ ] **Validate Scope Before Operation**
  ```python
  if not validate_token_scope(token, required_scopes):
      raise PermissionError("Token lacks required scope")
  ```

- [ ] **Handle Token Errors Safely**
  ```python
  except PermissionError as e:
      logger.error("Scope error - consider elevated token")
  ```

- [ ] **Never Log Token Values**
  ```python
  # DON'T: logger.info(f"Token: {token}")
  logger.info("Token obtained successfully")
  ```

- [ ] **Test with Mock Tokens**
  ```python
  @patch('scripts.ci._token_resolver.get_token')
  def test_operation(self, mock_token):
      mock_token.return_value = "test_token"
  ```

- [ ] **Test with Real Token (CI)**
  ```python
  if os.environ.get('GITHUB_ACTIONS'):
      token = get_token()
      # Test real operation
  ```

---

## 🔗 Related Documentation

- **TOKEN_HIERARCHY_GUIDE.md** - Overview of token levels and selection
- **API_VARIABLE_OPERATIONS.md** - API patterns using tokens
- **CI_CD_TOKEN_TROUBLESHOOTING.md** - Debugging token issues
- **scripts/ci/_token_resolver.py** - Token resolver implementation

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-17
**Maintained By**: CODEX_MASTER_KEY Implementation Team
**Status**: Ready for Use
