# TOKEN HIERARCHY GUIDE
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Quick Reference for Token Selection in CODEX_MASTER_KEY Implementation**

**Document Version**: 1.0.0
**Date**: 2026-02-17
**Target Audience**: Developers, Script Authors, Workflow Authors

---

## Quick Start: Which Token Should I Use?

### The Three-Token Hierarchy

| Token | Level | Use When | Common Operations |
|-------|-------|----------|------------------|
| **CODEX_MASTER_KEY** | Level 3 (Critical) | Org-level admin operations, workflow dispatch, critical changes | Create org variables, update workflows, rotate tokens |
| **CODEX_BACKUP_TOKEN** | Level 2 (Elevated) | Elevated repo operations, cross-repo actions, elevated scopes | Manage repo variables, create check runs, read workflow files |
| **GITHUB_TOKEN** | Level 1 (Standard) | Normal CI/CD operations, public info, repo-scoped actions | Read public data, create PR comments, update commit status |

---

##  Token Scope Comparison

### Operations Matrix: Which Token for Each Operation?

| Operation | GitHub_TOKEN | CODEX_BACKUP_TOKEN | CODEX_MASTER_KEY | Recommended |
|-----------|:---:|:---:|:---:|---|
| **Read Organization Variables** |  |  |  | Level 2+ |
| **Create Organization Variables** |  |  |  | Level 3 |
| **Read Repository Variables** |  |  |  | Level 1 |
| **Create Repository Variables** |  |  |  | Level 1 |
| **Update Workflow Files** |  |  |  | Level 2+ |
| **Dispatch Workflow Run** |  |  |  | Level 3 |
| **Read Public Secrets List** |  |  |  | Level 1 |
| **Access Repository Secrets** |  |  |  | Level 1 |

### Scope Details for Each Token

**GITHUB_TOKEN (Level 1 - Standard)**
```
Scopes: public_repo, repo:status, repo_deployment, security_events
Usage: Standard CI/CD operations, GitHub Actions workflows
Lifespan: Automatically created per workflow run (60 minutes)
Rate Limit: 1,000 requests/hour per action
Best For: Reading public data, updating PR status, creating comments
```

**CODEX_BACKUP_TOKEN (Level 2 - Elevated)**
```
Scopes: repo (full), admin:org_hook (read), workflow, actions:read_self
Permissions: Read/write all repos, read org hooks, manage actions
Lifespan: Long-lived (generated during setup, rotated quarterly)
Rate Limit: 5,000 requests/hour
Best For: Creating variables, managing workflows, cross-repo coordination
```

**CODEX_MASTER_KEY (Level 3 - Critical)**
```
Scopes: admin:org, admin:repo_hook, workflow, repo:full, admin:ssh_signing_key
Permissions: Full org admin, all repo operations, emergency procedures
Lifespan: Emergency use only (auto-rotated after use, 30-minute window)
Rate Limit: 10,000 requests/hour (org-level burst: 100/minute)
Best For: Organization variables, token rotation, emergency dispatch
```

---

##  Decision Tree: Choosing Your Token

```
START: I need to perform an operation

├─ Does it involve ORGANIZATION-level data?
│  ├─ YES: Go to "Organization Operations" (see below)
│  └─ NO: Go to "Repository Operations" (see below)

ORGANIZATION OPERATIONS:
├─ Creating or modifying ORG VARIABLES?
│  ├─ YES: Use CODEX_MASTER_KEY (Level 3)
│  └─ NO: Use CODEX_BACKUP_TOKEN (Level 2)
├─ Reading ORG data only?
│  └─ Use CODEX_BACKUP_TOKEN (Level 2)
├─ Emergency: Rotating tokens or dispatch override?
│  └─ Use CODEX_MASTER_KEY (Level 3)

REPOSITORY OPERATIONS:
├─ Creating REPO VARIABLES?
│  └─ Use GITHUB_TOKEN (Level 1) - sufficient scope
├─ Updating WORKFLOW FILES?
│  ├─ Org-level changes: Use CODEX_MASTER_KEY (Level 3)
│  ├─ Repo-level changes: Use CODEX_BACKUP_TOKEN (Level 2)
│  └─ Status/comment: Use GITHUB_TOKEN (Level 1)
├─ Reading repo secrets/variables?
│  └─ Use GITHUB_TOKEN (Level 1) - sufficient scope
├─ Accessing GitHub API?
│  ├─ Admin operations: Use CODEX_BACKUP_TOKEN (Level 2+)
│  ├─ Standard operations: Use GITHUB_TOKEN (Level 1)
│  └─ Org admin ops: Use CODEX_MASTER_KEY (Level 3)
```

---

##  Common Use Cases & Examples

### Use Case 1: Developer Reading Repository Variables

**Scenario**: Your script needs to read a deployment target variable from a repository.

**Decision**: Use `GITHUB_TOKEN` (Level 1)
- Sufficient scope for reading repo variables
- Automatically available in workflows
- No special setup needed

**Example**:
```python
import os
import requests

# GITHUB_TOKEN is automatically available in GitHub Actions
token = os.environ.get('GITHUB_TOKEN')
repo = os.environ.get('GITHUB_REPOSITORY')
owner, repo_name = repo.split('/')

# Read repository variable
url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/variables"
headers = {"Authorization": f"token {token}"}

response = requests.get(url, headers=headers)
variables = response.json()

if response.status_code == 200:
    for var in variables.get('variables', []):
        if var['name'] == 'DEPLOYMENT_TARGET':
            print(f"Target: {var['value']}")
else:
    print(f"Error: {response.status_code}")
```

---

### Use Case 2: CI Pipeline Creating a Repository Variable

**Scenario**: Your CI pipeline needs to create a new environment-specific variable in the repository.

**Decision**: Use `GITHUB_TOKEN` (Level 1)
- Repository variable creation is repo-scoped
- No org-level access required
- GITHUB_TOKEN has sufficient scope

**Example**:
```bash
#!/bin/bash

# Create a repository variable using GITHUB_TOKEN
TOKEN=${GITHUB_TOKEN}
REPO=${GITHUB_REPOSITORY}
OWNER=$(echo $REPO | cut -d'/' -f1)
REPO_NAME=$(echo $REPO | cut -d'/' -f2)

VARIABLE_NAME="BUILD_ENVIRONMENT"
VARIABLE_VALUE="production"

curl -X POST \
  -H "Authorization: token ${TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/${OWNER}/${REPO_NAME}/actions/variables" \
  -d @- <<EOF
{
  "name": "${VARIABLE_NAME}",
  "value": "${VARIABLE_VALUE}"
}
EOF
```

---

### Use Case 3: Workflow Creating Organization-Level Variable

**Scenario**: Your deployment workflow needs to create an organization-wide variable that multiple repositories will use.

**Decision**: Use `CODEX_MASTER_KEY` (Level 3)
- Organization variables require org admin scope
- Only CODEX_MASTER_KEY has sufficient permission
- Requires special setup and request

**Example**:
```yaml
name: Create Organization Variable

on:
  workflow_dispatch:
    inputs:
      variable_name:
        description: Name of organization variable
        required: true
      variable_value:
        description: Value of organization variable
        required: true

jobs:
  create-org-variable:
    runs-on: ubuntu-latest
    steps:
      - name: Create organization variable
        env:
          ORG_TOKEN: ${{ secrets.CODEX_MASTER_KEY }}  # Requires elevated access
          GITHUB_ORGANIZATION: 'aries-serpent'
        run: |
          VARIABLE_NAME="${{ github.event.inputs.variable_name }}"
          VARIABLE_VALUE="${{ github.event.inputs.variable_value }}"
          
          curl -X POST \
            -H "Authorization: token ${ORG_TOKEN}" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/orgs/${GITHUB_ORGANIZATION}/actions/variables" \
            -d "{\"name\":\"${VARIABLE_NAME}\",\"value\":\"${VARIABLE_VALUE}\"}"
```

---

### Use Case 4: Script with Safe Fallback Token Handling

**Scenario**: Your utility script needs to handle token selection gracefully with fallback logic.

**Decision**: Use token resolver utility (handles fallback automatically)

**Example**:
```python
from scripts.ci._token_resolver import get_token, validate_token_scope

def read_organization_variables():
    """Read org variables with proper token selection."""
    
    # Get appropriate token for org read operation
    # Falls back: CODEX_MASTER_KEY → CODEX_BACKUP_KEY → GH_TOKEN → GITHUB_TOKEN
    token, token_source = get_token(required_elevated=True)
    
    if not token:
        raise Exception("No suitable token available for org variable read")
    
    # Validate token has required scope
    is_valid, msg = validate_token_scope(token, ['admin:org_hook'])
    if not is_valid:
        raise Exception(f"Token validation failed: {msg}")
    
    # Perform operation with selected token
    import requests
    url = "https://api.github.com/orgs/aries-serpent/actions/variables"
    headers = {"Authorization": f"token {token}"}
    
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
```

---

### Use Case 5: Handling Token Scope Errors

**Scenario**: Your operation fails with a scope error - you need to understand why and recover.

**Decision**: Check token level requirements and recover

**Example**:
```python
import requests
import logging

def update_workflow_with_retry():
    """Update workflow file with intelligent token fallback."""
    
    operation_requires_levels = ['elevated', 'critical']  # Levels 2 or 3
    
    from scripts.ci._token_resolver import get_token
    
    # Try each token level from highest to lowest
    for level in operation_requires_levels:
        token = get_token(required_level=level)
        
        if not token:
            logging.warning(f"No {level} token available, trying lower level")
            continue
        
        try:
            # Attempt workflow update
            response = requests.patch(
                "https://api.github.com/repos/owner/repo/contents/.github/workflows/ci.yml",
                headers={"Authorization": f"token {token}"},
                json={
                    "message": "Update workflow",
                    "content": new_workflow_content,
                    "sha": current_sha
                }
            )
            
            if response.status_code == 200:
                logging.info(f"Workflow updated using {level} token")
                return True
            
            elif response.status_code == 403:
                logging.warning(f"Insufficient scope at {level}, trying lower")
                continue
            
            else:
                logging.error(f"Unexpected error: {response.status_code}")
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            logging.debug(f"Attempt with {level} token failed: {e}")
            continue
    
    raise Exception("No suitable token available for workflow update")
```

---

## ️ Error Handling & Recovery

### Error 1: "Token scope insufficient for this request" (403)

**Root Cause**: Using a lower-level token than required for the operation.

**Solution**:
1. Check which operation you're performing
2. Reference the Operations Matrix above
3. Use a higher-level token (see Decision Tree)
4. Re-run the operation

**Example**:
```python
# WRONG: Trying to read org variables with GITHUB_TOKEN
token = os.environ.get('GITHUB_TOKEN')  # Level 1 - insufficient

# RIGHT: Request CODEX_BACKUP_TOKEN for org read
from scripts.ci._token_resolver import get_token
token = get_token(required_level='elevated')  # Level 2
```

---

### Error 2: "Token expired or revoked"

**Root Cause**: Token has been manually revoked or automatically rotated.

**Solution**:
1. For GITHUB_TOKEN: Automatically renewed in next workflow run
2. For CODEX_BACKUP_TOKEN: Contact repo admin for reissue (quarterly rotation)
3. For CODEX_MASTER_KEY: Automatically managed, use emergency procedure

**Example Recovery Script**:
```bash
#!/bin/bash

# Check if token is valid
TOKEN=$1
if [ -z "$TOKEN" ]; then
    echo "Error: No token provided"
    exit 1
fi

# Attempt simple API call to validate
response=$(curl -s -I -H "Authorization: token ${TOKEN}" \
    https://api.github.com/user)

if echo "$response" | grep -q "401 Unauthorized"; then
    echo "Token is invalid/revoked. Contact repo admin."
    exit 1
elif echo "$response" | grep -q "200 OK"; then
    echo "Token is valid"
    exit 0
else
    echo "Token validation inconclusive"
    exit 1
fi
```

---

### Error 3: "Permission denied" (403) vs "Token scope insufficient"

**Key Difference**:
- **Scope Insufficient**: Token doesn't have permission TYPE (e.g., lacks 'admin:org')
- **Permission Denied**: User/token type doesn't have role permission (e.g., not org owner)

**Diagnosis**:
```python
# Check scope error
if "insufficient" in error_message.lower():
    print("Need different token with different scope")
    print("Try: CODEX_BACKUP_TOKEN or CODEX_MASTER_KEY")

# Check permission error  
elif "permission" in error_message.lower():
    print("Current user lacks role permission")
    print("Contact repo admin or use elevated token")
```

---

### Error 4: Rate Limit Exceeded (429)

**Root Cause**: Exceeded request limit for token level.

**Rate Limits by Token**:
- GITHUB_TOKEN: 1,000 requests/hour (repo scope)
- CODEX_BACKUP_TOKEN: 5,000 requests/hour
- CODEX_MASTER_KEY: 10,000 requests/hour

**Solution**: Implement exponential backoff
```python
import time
import requests

def api_call_with_retry(url, token, max_retries=3):
    """Make API call with automatic retry on rate limit."""
    
    for attempt in range(max_retries):
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Rate limited - use exponential backoff
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"Rate limited. Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            continue
        
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    raise Exception("Max retries exceeded")
```

---

##  Security Best Practices

### 1. Token Environment Variables

** DO**: Keep tokens in environment variables
```python
token = os.environ.get('GITHUB_TOKEN')
```

** DON'T**: Hardcode tokens in scripts
```python
# WRONG!
token = "******"
```

### 2. Logging Token Usage Safely

** DO**: Log operation without exposing token
```python
logging.info(f"Using {token_level} token for org variable read")
```

** DON'T**: Log token values
```python
# WRONG!
logging.info(f"Using token: {token}")
```

### 3. Token Scope Validation

** DO**: Validate scope before operation
```python
from scripts.ci._token_resolver import validate_token_scope

if not validate_token_scope(token, ['admin:org']):
    raise Exception("Token lacks required scope")
```

** DON'T**: Assume token has sufficient scope
```python
# WRONG! - Might fail with 403
requests.get(url, headers={"Authorization": f"token {token}"})
```

### 4. Error Messages

** DO**: Include helpful guidance in errors
```python
if response.status_code == 403:
    raise Exception(
        "Scope insufficient for this operation. "
        "Use CODEX_BACKUP_TOKEN or CODEX_MASTER_KEY. "
        "See: TOKEN_HIERARCHY_GUIDE.md"
    )
```

** DON'T**: Expose token in error messages
```python
# WRONG!
raise Exception(f"API failed with token {token}: {response.text}")
```

---

##  Related Documentation

- **SCRIPT_TOKEN_docs/api/reference/INTEGRATION.md** - How to implement token resolution in scripts
- **WORKFLOW_TOKEN_PATTERNS_UPDATE.md** - Token patterns for GitHub Actions workflows
- **API_VARIABLE_OPERATIONS.md** - Complete API guide for variable operations
- **CI_CD_TOKEN_TROUBLESHOOTING.md** - Troubleshooting guide for token issues
- **CUSTOM_AGENT_TOKEN_GUIDANCE.md** - Token requirements for custom agents

---

##  Quick Reference Checklist

Use this checklist when choosing a token:

- [ ] Have I identified if this is an org-level or repo-level operation?
- [ ] Have I checked the Operations Matrix above?
- [ ] Have I followed the Decision Tree?
- [ ] Have I chosen the lowest-level token that works (principle of least privilege)?
- [ ] Have I verified the token is available in my environment?
- [ ] Have I implemented error handling for token failures?
- [ ] Have I ensured I'm not logging token values?
- [ ] Have I tested with the actual token level I'm using?

---

## 📞 Getting Help

**For token selection questions**:
1. Check the Decision Tree (above)
2. Check the Operations Matrix (above)
3. See related documentation for your use case

**For token errors**:
1. See "Error Handling & Recovery" section
2. Check CI_CD_TOKEN_TROUBLESHOOTING.md
3. Contact repo admin with error message

**For implementation questions**:
1. See code examples in "Common Use Cases" section
2. Check SCRIPT_TOKEN_docs/api/reference/INTEGRATION.md for patterns
3. Check WORKFLOW_TOKEN_PATTERNS_UPDATE.md for workflows

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-17
**Maintained By**: CODEX_MASTER_KEY Implementation Team
**Status**: Ready for Use
