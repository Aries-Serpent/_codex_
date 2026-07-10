# API_VARIABLE_OPERATIONS.md

**Comprehensive Guide for GitHub API Variable Operations with CODEX_MASTER_KEY**

**Document Version**: 1.0.0
**Date**: 2026-02-17
**Target Audience**: API Developers, Integration Engineers, Automation Specialists

---

## 🎯 Overview

Complete guide for performing GitHub Actions variable operations using the GitHub API with appropriate token levels. Covers repository variables, organization variables, and advanced operations like base64 encoding for complex values.

---

## 📊 Variable Operations Reference

### Operation Matrix: Token Requirements

| Operation | Endpoint | Method | Token Level | Rate Limit |
|-----------|----------|--------|------------|------------|
| **List Repo Variables** | `/repos/{owner}/{repo}/actions/variables` | GET | Level 1 | 1000/hour |
| **Get Repo Variable** | `/repos/{owner}/{repo}/actions/variables/{name}` | GET | Level 1 | 1000/hour |
| **Create Repo Variable** | `/repos/{owner}/{repo}/actions/variables` | POST | Level 1 | 1000/hour |
| **Update Repo Variable** | `/repos/{owner}/{repo}/actions/variables/{name}` | PATCH | Level 1 | 1000/hour |
| **Delete Repo Variable** | `/repos/{owner}/{repo}/actions/variables/{name}` | DELETE | Level 1 | 1000/hour |
| **List Org Variables** | `/orgs/{org}/actions/variables` | GET | Level 2+ | 5000/hour |
| **Create Org Variable** | `/orgs/{org}/actions/variables` | POST | Level 3 | 10000/hour |

---

## 🔐 Repository Variable Operations

### 1. List Repository Variables

**Purpose**: Retrieve all variables defined in a repository

**Endpoint**: `GET /repos/{owner}/{repo}/actions/variables`

**Required Token**: GITHUB_TOKEN (Level 1)

**Python Example**:
```python
import requests
import json

def list_repo_variables(owner, repo, token):
    """List all variables in a repository."""
    
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        variables = response.json().get('variables', [])
        for var in variables:
            print(f"Name: {var['name']}")
            print(f"  Created: {var['created_at']}")
            print(f"  Updated: {var['updated_at']}")
        return variables
    
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage
token = "ghp_your_token_here"
variables = list_repo_variables("aries-serpent", "_codex_", token)
```

**Bash Example**:
```bash
#!/bin/bash

TOKEN="$1"
OWNER="aries-serpent"
REPO="_codex_"

# List all variables
curl -s \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/variables" \
  | jq '.variables[] | {name, created_at, updated_at}'
```

---

### 2. Get Single Repository Variable

**Purpose**: Retrieve a specific variable's metadata

**Endpoint**: `GET /repos/{owner}/{repo}/actions/variables/{name}`

**Required Token**: GITHUB_TOKEN (Level 1)

**Python Example**:
```python
import requests

def get_repo_variable(owner, repo, var_name, token):
    """Get a specific repository variable."""
    
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables/{var_name}"
    headers = {"Authorization": f"token {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        var = response.json()
        print(f"Variable: {var['name']}")
        print(f"Value: {var['value']}")
        return var
    
    elif response.status_code == 404:
        print(f"Variable '{var_name}' not found")
        return None
    
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
var = get_repo_variable("aries-serpent", "_codex_", "DEPLOYMENT_ENV", token)
```

---

### 3. Create Repository Variable

**Purpose**: Create a new variable in repository

**Endpoint**: `POST /repos/{owner}/{repo}/actions/variables`

**Required Token**: GITHUB_TOKEN (Level 1)

**Request Body**:
```json
{
  "name": "VARIABLE_NAME",
  "value": "variable_value"
}
```

**Python Example**:
```python
import requests

def create_repo_variable(owner, repo, name, value, token):
    """Create a new repository variable."""
    
    # Validate variable name
    if not name.isupper() or not all(c.isalnum() or c == '_' for c in name):
        raise ValueError("Variable name must be uppercase alphanumeric with underscores")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
    headers = {"Authorization": f"token {token}"}
    data = {"name": name, "value": value}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"✅ Variable '{name}' created")
        return True
    
    elif response.status_code == 409:
        print(f"⚠️ Variable '{name}' already exists")
        return False
    
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

# Usage
create_repo_variable(
    "aries-serpent", "_codex_",
    "BUILD_TYPE", "production",
    token
)
```

---

### 4. Update Repository Variable

**Purpose**: Modify an existing variable

**Endpoint**: `PATCH /repos/{owner}/{repo}/actions/variables/{name}`

**Required Token**: GITHUB_TOKEN (Level 1)

**Python Example**:
```python
import requests

def update_repo_variable(owner, repo, name, new_value, token):
    """Update an existing repository variable."""
    
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables/{name}"
    headers = {"Authorization": f"token {token}"}
    data = {"value": new_value}
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print(f"✅ Variable '{name}' updated")
        return True
    
    elif response.status_code == 404:
        print(f"❌ Variable '{name}' not found")
        return False
    
    elif response.status_code == 422:
        print(f"⚠️ Validation error: {response.text}")
        return False
    
    else:
        print(f"Error: {response.status_code}")
        return False

# Usage - Update with new value
update_repo_variable(
    "aries-serpent", "_codex_",
    "BUILD_TYPE", "staging",
    token
)
```

---

### 5. Delete Repository Variable

**Purpose**: Remove a variable from repository

**Endpoint**: `DELETE /repos/{owner}/{repo}/actions/variables/{name}`

**Required Token**: GITHUB_TOKEN (Level 1)

**Python Example**:
```python
import requests

def delete_repo_variable(owner, repo, name, token):
    """Delete a repository variable."""
    
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables/{name}"
    headers = {"Authorization": f"token {token}"}
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        print(f"✅ Variable '{name}' deleted")
        return True
    
    elif response.status_code == 404:
        print(f"⚠️ Variable '{name}' not found (already deleted?)")
        return False
    
    else:
        print(f"Error: {response.status_code}")
        return False

# Usage
delete_repo_variable("aries-serpent", "_codex_", "OLD_VAR", token)
```

---

## 🏛️ Organization Variable Operations

### 1. Create Organization Variable

**Purpose**: Create a variable accessible to all org repositories

**Endpoint**: `POST /orgs/{org}/actions/variables`

**Required Token**: CODEX_MASTER_KEY (Level 3)

**Request Body**:
```json
{
  "name": "ORG_VARIABLE_NAME",
  "value": "value",
  "visibility": "all"  // or "selected" or "private"
}
```

**Python Example**:
```python
import requests

def create_org_variable(org, name, value, visibility, token):
    """Create an organization-level variable."""
    
    # Only Level 3 token has this scope
    url = f"https://api.github.com/orgs/{org}/actions/variables"
    headers = {"Authorization": f"token {token}"}
    data = {
        "name": name,
        "value": value,
        "visibility": visibility  # "all", "selected", or "private"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"✅ Organization variable '{name}' created")
        return True
    
    elif response.status_code == 403:
        print(f"❌ Access denied - requires CODEX_MASTER_KEY")
        return False
    
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

# Usage - Requires Level 3 token
create_org_variable(
    "aries-serpent",
    "ORG_DEPLOYMENT_TARGET",
    "production",
    "all",  # Visible to all org repos
    org_token  # CODEX_MASTER_KEY
)
```

---

## 🔒 Base64 Encoding for Complex Values

### When to Use Base64 Encoding

Base64 encoding is necessary when storing complex values (JSON, YAML, multi-line strings) that might contain special characters or newlines.

**Scenario 8 (Phase 5 Test Case): Base64 Round-Trip**

**Use Cases**:
- Storing JSON configuration objects
- Multi-line configuration files
- Binary or special character data
- Complex data structures

### Encoding Strategy

**Python Encoding**:
```python
import json
import base64

def encode_complex_value(data):
    """Encode complex data structure to base64."""
    
    # Convert to JSON string
    json_str = json.dumps(data, indent=2)
    
    # Encode to base64
    encoded = base64.b64encode(json_str.encode()).decode()
    
    return encoded

# Example: Store complex deployment config
config = {
    "environments": {
        "staging": {
            "host": "staging.example.com",
            "timeout": 30
        },
        "production": {
            "host": "prod.example.com",
            "timeout": 60
        }
    },
    "features": {
        "logging": True,
        "metrics": True
    }
}

encoded_config = encode_complex_value(config)
print(f"Base64: {encoded_config}")
```

**Storing in GitHub Variable**:
```python
# Create variable with base64-encoded value
create_repo_variable(
    "aries-serpent", "_codex_",
    "DEPLOYMENT_CONFIG",
    encoded_config,  # Base64-encoded JSON
    token
)
```

**Decoding in Workflow**:
```yaml
# In GitHub Actions workflow
- name: Use complex variable
  run: |
    # Decode base64 value
    CONFIG=$(echo "${{ vars.DEPLOYMENT_CONFIG }}" | base64 -d)
    
    # Parse JSON
    HOST=$(echo "$CONFIG" | jq -r '.environments.production.host')
    
    echo "Deploying to: $HOST"
```

**Python Decoding**:
```python
import base64
import json

def decode_complex_value(encoded_value):
    """Decode base64-encoded data structure."""
    
    # Decode from base64
    json_str = base64.b64decode(encoded_value).decode()
    
    # Parse JSON
    data = json.loads(json_str)
    
    return data

# Retrieve and decode
variable = get_repo_variable("aries-serpent", "_codex_", "DEPLOYMENT_CONFIG", token)
if variable:
    config = decode_complex_value(variable['value'])
    print(config)
```

---

## ⚠️ Error Handling

### Common Errors

**Error 400: Bad Request**
```
Cause: Invalid JSON in request body
Fix: Validate JSON before sending
```

**Error 401: Unauthorized**
```
Cause: Invalid or missing token
Fix: Check token value and format
```

**Error 403: Forbidden**
```
Cause: Token lacks required scope
Fix: Use higher-level token (see Token Hierarchy Guide)
```

**Error 404: Not Found**
```
Cause: Variable doesn't exist
Fix: Create variable first or check variable name
```

**Error 409: Conflict**
```
Cause: Variable name already exists
Fix: Use different name or update existing variable
```

**Error 422: Unprocessable Entity**
```
Cause: Validation error (e.g., invalid variable name)
Fix: Variable names must be uppercase alphanumeric with underscores
```

**Error 429: Too Many Requests**
```
Cause: Rate limit exceeded
Fix: Implement exponential backoff
```

### Handling Rate Limits

```python
import time
import requests

def api_call_with_retry(url, token, max_retries=3):
    """Make API call with exponential backoff on rate limit."""
    
    for attempt in range(max_retries):
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Rate limited - exponential backoff
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        else:
            raise Exception(f"Error: {response.status_code}")
    
    raise Exception("Max retries exceeded")
```

---

## 🔗 Related Documentation

- **TOKEN_HIERARCHY_GUIDE.md** - Token selection
- **SCRIPT_TOKEN_docs/api/reference/INTEGRATION.md** - Integration patterns
- **WORKFLOW_TOKEN_PATTERNS_UPDATE.md** - Workflow patterns
- **CI_CD_TOKEN_TROUBLESHOOTING.md** - Error debugging

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-17
**Status**: Ready for Use
