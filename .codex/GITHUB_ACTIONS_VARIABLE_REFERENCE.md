# GITHUB_ACTIONS_VARIABLE_REFERENCE.md

**Technical Reference for GitHub Actions Variables API**

**Document Version**: 1.0.0
**Date**: 2026-02-17
**Target Audience**: API Engineers, Integration Developers, Technical Reference Users

---

## 🎯 Quick Reference

All GitHub Actions variable operations and their token requirements:

| Operation | Endpoint | Method | Token Required | Rate Limit |
|-----------|----------|--------|----------------|------------|
| List Repo Variables | `/repos/{o}/{r}/actions/variables` | GET | L1 | 1K/hr |
| Get Repo Variable | `/repos/{o}/{r}/actions/variables/{n}` | GET | L1 | 1K/hr |
| Create Repo Variable | `/repos/{o}/{r}/actions/variables` | POST | L1 | 1K/hr |
| Update Repo Variable | `/repos/{o}/{r}/actions/variables/{n}` | PATCH | L1 | 1K/hr |
| Delete Repo Variable | `/repos/{o}/{r}/actions/variables/{n}` | DELETE | L1 | 1K/hr |
| List Org Variables | `/orgs/{o}/actions/variables` | GET | L2+ | 5K/hr |
| Create Org Variable | `/orgs/{o}/actions/variables` | POST | L3 | 10K/hr |
| Update Org Variable | `/orgs/{o}/actions/variables/{n}` | PATCH | L3 | 10K/hr |
| Delete Org Variable | `/orgs/{o}/actions/variables/{n}` | DELETE | L3 | 10K/hr |

---

## 📖 Complete API Reference

### Repository Variables API

#### GET /repos/{owner}/{repo}/actions/variables

**List all variables in a repository**

**Parameters**:
```
owner:    string (required)      # Repository owner
repo:     string (required)      # Repository name
per_page: integer (optional)     # Results per page (1-30, default: 30)
page:     integer (optional)     # Page number (default: 1)
```

**Response** (200 OK):
```json
{
  "total_count": 2,
  "variables": [
    {
      "name": "DEPLOY_ENV",
      "value": "production",
      "created_at": "2026-02-17T10:00:00Z",
      "updated_at": "2026-02-17T10:00:00Z",
      "visibility": "all"
    },
    {
      "name": "BUILD_TYPE",
      "value": "release",
      "created_at": "2026-02-17T10:00:00Z",
      "updated_at": "2026-02-17T10:00:00Z",
      "visibility": "selected"
    }
  ]
}
```

**Error Responses**:
- 401 Unauthorized: Invalid token
- 403 Forbidden: Insufficient scope
- 404 Not Found: Repository not found

---

#### GET /repos/{owner}/{repo}/actions/variables/{name}

**Get a specific repository variable**

**Parameters**:
```
owner: string (required)    # Repository owner
repo:  string (required)    # Repository name
name:  string (required)    # Variable name (case-sensitive)
```

**Response** (200 OK):
```json
{
  "name": "DEPLOY_ENV",
  "value": "production",
  "created_at": "2026-02-17T10:00:00Z",
  "updated_at": "2026-02-17T10:00:00Z",
  "visibility": "all"
}
```

**Error Responses**:
- 404 Not Found: Variable not found

---

#### POST /repos/{owner}/{repo}/actions/variables

**Create a new repository variable**

**Parameters**:
```
owner: string (required)    # Repository owner
repo:  string (required)    # Repository name
```

**Request Body**:
```json
{
  "name": "VARIABLE_NAME",
  "value": "variable_value"
}
```

**Constraints**:
- Name: 1-255 chars, uppercase alphanumeric + underscore
- Value: up to 48 KB
- Name must not begin with number or reserved prefix

**Response** (201 Created):
```json
{
  "name": "VARIABLE_NAME",
  "value": "variable_value",
  "created_at": "2026-02-17T10:00:00Z",
  "updated_at": "2026-02-17T10:00:00Z",
  "visibility": "all"
}
```

**Error Responses**:
- 400 Bad Request: Invalid input
- 409 Conflict: Variable already exists
- 422 Unprocessable Entity: Invalid variable name format

---

#### PATCH /repos/{owner}/{repo}/actions/variables/{name}

**Update an existing repository variable**

**Parameters**:
```
owner: string (required)    # Repository owner
repo:  string (required)    # Repository name
name:  string (required)    # Variable name
```

**Request Body**:
```json
{
  "value": "new_value"
}
```

**Response** (204 No Content)

**Concurrency Notes**:
- Last write wins (no locking)
- For atomic updates, use transactions at application level
- Consider versioning for critical values

---

#### DELETE /repos/{owner}/{repo}/actions/variables/{name}

**Delete a repository variable**

**Parameters**:
```
owner: string (required)    # Repository owner
repo:  string (required)    # Repository name
name:  string (required)    # Variable name
```

**Response** (204 No Content)

**Effects**:
- Variable removed immediately
- Workflows using this variable will fail at runtime
- Consider deprecation period before deletion

---

### Organization Variables API

#### GET /orgs/{org}/actions/variables

**List organization variables**

**Parameters**:
```
org:      string (required)      # Organization name
per_page: integer (optional)     # Results per page (1-30, default: 30)
page:     integer (optional)     # Page number (default: 1)
```

**Response** (200 OK):
```json
{
  "total_count": 3,
  "variables": [
    {
      "name": "ORG_DEPLOY_TARGET",
      "value": "production",
      "created_at": "2026-02-17T10:00:00Z",
      "updated_at": "2026-02-17T10:00:00Z",
      "visibility": "all"
    }
  ]
}
```

**Required Scope**: admin:org_hook, repo:full
**Token Level**: Level 2+ (CODEX_BACKUP_TOKEN)

---

#### POST /orgs/{org}/actions/variables

**Create an organization variable**

**Parameters**:
```
org: string (required)          # Organization name
```

**Request Body**:
```json
{
  "name": "ORG_VARIABLE",
  "value": "value",
  "visibility": "all"
}
```

**Visibility Options**:
- "all": Available to all organization repositories
- "private": Only organization administrators can access
- "selected": Available only to specified repositories

**Response** (201 Created)

**Required Scope**: admin:org
**Token Level**: Level 3 (CODEX_MASTER_KEY)

---

## 🔐 Scope Requirements Matrix

### Comprehensive Scope Matrix

| Operation | GITHUB_TOKEN | CODEX_BACKUP_TOKEN | CODEX_MASTER_KEY |
|-----------|:---:|:---:|:---:|
| **Get Repo Variables** | ✅ repo | ✅ repo | ✅ repo |
| **Create Repo Variables** | ✅ repo | ✅ repo | ✅ repo |
| **Update Repo Variables** | ✅ repo | ✅ repo | ✅ repo |
| **Delete Repo Variables** | ✅ repo | ✅ repo | ✅ repo |
| **Get Org Variables** | ❌ | ✅ admin:org_hook | ✅ admin:org |
| **Create Org Variables** | ❌ | ❌ | ✅ admin:org |
| **Update Org Variables** | ❌ | ❌ | ✅ admin:org |
| **Delete Org Variables** | ❌ | ❌ | ✅ admin:org |

### Detailed Scope Explanations

**Level 1 (GITHUB_TOKEN)**:
- Scope: `repo` (full repository access)
- Operations: Read/write all repo-scoped resources
- Rate Limit: 1,000 requests/hour
- Auto-available: Yes (per-run)

**Level 2 (CODEX_BACKUP_TOKEN)**:
- Scopes: `repo`, `admin:org_hook`, `workflow`, `actions:read_self`
- Operations: Cross-repo, org hook read, workflow management
- Rate Limit: 5,000 requests/hour
- Auto-available: No (stored secret)

**Level 3 (CODEX_MASTER_KEY)**:
- Scopes: `admin:org`, `admin:repo_hook`, `workflow`, `repo:full`
- Operations: Org admin, all repo operations, emergency procedures
- Rate Limit: 10,000 requests/hour
- Auto-available: No (special request)

---

## ⏱️ Rate Limiting & Throttling

### Rate Limit Headers

**Standard Response Headers**:
```
X-RateLimit-Limit:     1000          # Requests allowed per hour
X-RateLimit-Remaining: 950           # Requests remaining
X-RateLimit-Reset:     1708876800    # Unix timestamp when limit resets
X-RateLimit-Used:      50            # Requests used
```

### Rate Limit by Token Type

**Repository Variables** (repo scope):
- GITHUB_TOKEN: 1,000/hour (per repo)
- CODEX_BACKUP_TOKEN: 5,000/hour (org-wide)
- CODEX_MASTER_KEY: 10,000/hour (org-wide burst: 100/min)

**Organization Variables**:
- CODEX_BACKUP_TOKEN: 5,000/hour
- CODEX_MASTER_KEY: 10,000/hour

### Rate Limit Handling

**Check Current Limits**:
```python
import requests

def get_rate_limits(token):
    """Get current rate limit status."""
    response = requests.get(
        "https://api.github.com/rate_limit",
        headers={"Authorization": f"token {token}"}
    )
    return response.json()['resources']
```

**Implement Exponential Backoff**:
```python
import time

def api_call_with_backoff(url, token, max_retries=5):
    """Make API call with automatic backoff on rate limit."""
    
    for attempt in range(max_retries):
        response = requests.get(
            url,
            headers={"Authorization": f"token {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        else:
            raise Exception(f"API error: {response.status_code}")
    
    raise Exception("Max retries exceeded")
```

---

## 🔍 Complete Error Reference

### HTTP Status Codes

**200 OK**
```
GET request succeeded
Variable returned successfully
```

**201 Created**
```
POST request succeeded
Variable created successfully
Response body includes created variable
```

**204 No Content**
```
PATCH or DELETE succeeded
No response body
```

**400 Bad Request**
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "message": "name is too long",
      "field": "name",
      "code": "too_long"
    }
  ]
}
```
**Fixes**:
- Check field lengths
- Validate JSON format
- Check required fields

**401 Unauthorized**
```json
{
  "message": "Bad credentials",
  "documentation_url": "https://docs.github.com/rest"
}
```
**Fixes**:
- Check token format
- Verify token is not revoked
- Confirm token is passed in header

**403 Forbidden**
```json
{
  "message": "This operation requires 'admin:org_hook' scope",
  "documentation_url": "https://docs.github.com/rest"
}
```
**Fixes**:
- Use higher-level token
- Check token scopes
- Verify user has required role

**404 Not Found**
```json
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest"
}
```
**Fixes**:
- Check variable name (case-sensitive)
- Verify repository exists
- Verify organization exists

**409 Conflict**
```json
{
  "message": "Variable already exists",
  "documentation_url": "https://docs.github.com/rest"
}
```
**Fixes**:
- Use different variable name
- Use PATCH to update instead
- Check for name typos

**422 Unprocessable Entity**
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "message": "name is not in a valid format",
      "field": "name",
      "code": "invalid"
    }
  ]
}
```
**Fixes**:
- Variable name must be uppercase alphanumeric with underscores
- Cannot start with number
- Cannot exceed 255 characters

**429 Too Many Requests**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Remaining: 0
```
**Fixes**:
- Implement exponential backoff
- Reduce request rate
- Use higher-level token (more requests/hour)

**500 Internal Server Error**
```
GitHub API internal error
```
**Fixes**:
- Retry request after delay
- Contact GitHub support if persists

---

## 📚 Usage Examples

### Python with requests

```python
import requests
import time

class GitHubVariablesAPI:
    """GitHub Variables API client."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def list_variables(self, owner, repo):
        """List all variables in a repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/actions/variables"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)
    
    def create_variable(self, owner, repo, name, value):
        """Create a new variable."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/actions/variables"
        data = {"name": name, "value": value}
        response = requests.post(url, headers=self.headers, json=data)
        return self._handle_response(response)
    
    def _handle_response(self, response):
        """Handle API response and errors."""
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else None
        
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            # Retry (simplified)
            return None
        
        else:
            error = response.json().get('message', 'Unknown error')
            raise Exception(f"API error: {error}")
```

### Bash/curl

```bash
#!/bin/bash

TOKEN="$1"
OWNER="$2"
REPO="$3"

API_URL="https://api.github.com"

# List variables
curl -s \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "$API_URL/repos/$OWNER/$REPO/actions/variables" \
  | jq '.variables[] | {name, value}'

# Create variable
curl -X POST \
  -H "Authorization: token $TOKEN" \
  "$API_URL/repos/$OWNER/$REPO/actions/variables" \
  -d '{"name":"VAR_NAME","value":"var_value"}'

# Update variable
curl -X PATCH \
  -H "Authorization: token $TOKEN" \
  "$API_URL/repos/$OWNER/$REPO/actions/variables/VAR_NAME" \
  -d '{"value":"new_value"}'
```

---

## 📋 Troubleshooting Index

| Error | Likely Cause | Solution |
|-------|---|---|
| 401 | Invalid token | Check token value and format |
| 403 scope | Token level too low | Use higher-level token |
| 403 permission | User lacks role | Contact org admin |
| 404 | Variable not found | Check variable name (case-sensitive) |
| 409 | Name conflict | Use different name or PATCH |
| 422 | Invalid name format | Use UPPERCASE_WITH_UNDERSCORES |
| 429 | Rate limit | Implement backoff, use higher token |

---

## 🔗 Related Documentation

- **TOKEN_HIERARCHY_GUIDE.md** - Token selection
- **API_VARIABLE_OPERATIONS.md** - Operations patterns
- **CI_CD_TOKEN_TROUBLESHOOTING.md** - Error debugging

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-17
**Status**: Ready for Use
