# Token Hierarchy & Scopes Management
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated: 2026-07-08
**Author:** Phase 12 WS3 Documentation Team

---

## Table of Contents

1. [Overview](#overview)
2. [Token Types](#token-types)
3. [Token Lifecycle](#token-lifecycle)
4. [Scope Model](#scope-model)
5. [Token Management API](#token-management-api)
6. [Implementation Examples](#implementation-examples)
7. [Security Considerations](#security-considerations)

---

## Overview

### Token Architecture

The Codex token system provides multiple token types, each with specific purposes, lifetimes, and scopes:

```
┌─────────────────────────────────────────────┐
│         Token Management System             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ Access Token │  │ Refresh Token│       │
│  │ (15 min TTL) │  │ (30 day TTL) │       │
│  └──────────────┘  └──────────────┘       │
│         │                  │               │
│         └──────────┬───────┘               │
│                    │                       │
│          ┌─────────▼────────┐             │
│          │  Session Token   │             │
│          │  (24 hour TTL)   │             │
│          └──────────────────┘             │
│                    │                       │
│          ┌─────────▼────────┐             │
│          │   API Token      │             │
│          │  (90 day TTL)    │             │
│          └──────────────────┘             │
│                                             │
└─────────────────────────────────────────────┘
```

### Key Principles

1. **Principle of Least Privilege:** Each token has minimal scopes needed
2. **Short Lifetimes:** Access tokens expire quickly (15 min)
3. **Refresh Isolation:** Refresh tokens are opaque and never used for API calls
4. **Immutable Scopes:** Token scopes cannot be modified after issuance
5. **Audit Trail:** All token operations logged (issue, use, refresh, revoke)

---

## Token Types

### Access Token

**Purpose:** Authenticate API requests and grant temporary access

**Format:** JWT (RS256) with RS256 signature

**TTL:** 15 minutes (default, configurable)

**Scopes:** Specific API permissions (read, write, admin)

**Content:**
```json
{
  "user_id": "alice@company.com",
  "username": "alice",
  "roles": ["agent_operator", "ci_operator"],
  "scopes": [
    "api:agents:read",
    "api:agents:write",
    "api:workflows:exec"
  ],
  "issued_at": 1720000000,
  "expires_at": 1720000900,
  "iss": "codex-auth",
  "sub": "alice@company.com"
}
```

**Usage:**
```bash
curl -H "Authorization: ******" \
  https://api.codex.local/v1/agents
```

**Refresh:** Via refresh token
```bash
POST /api/v1/auth/token/refresh
{
  "refresh_token": "refresh_token_value"
}
→ Returns new access_token
```

### Refresh Token

**Purpose:** Obtain new access tokens without re-authenticating

**Format:** Opaque token (random, cryptographically secure)

**TTL:** 30 days (default, configurable)

**Scopes:** Limited to token refresh only (no API calls)

**Characteristics:**
- Never used directly for API calls
- Stored securely (HTTP-only cookie or secure storage)
- Revoked immediately on logout
- Survives client restart (long-lived session)

**Usage:**
```python
# Client obtains access token
response = requests.post("/api/v1/auth/login", json={
    "username": "alice",
    "password": "secret123"
})

access_token = response.json()["access_token"]
refresh_token = response.json()["refresh_token"]  # Store securely

# Use access token for API calls (15 min)
headers = {"Authorization": f"******"}
response = requests.get("/api/v1/agents", headers=headers)

# Access token expires, refresh it
response = requests.post("/api/v1/auth/token/refresh", json={
    "refresh_token": refresh_token
})

new_access_token = response.json()["access_token"]
```

**Security Properties:**
- Opaque (attacker cannot guess or decode)
- Single-use (revoked after use)
- Rotation on every refresh (prevents token replay)
- Automatic revocation on password change

### Session Token

**Purpose:** Track user session across multiple requests

**Format:** JWT with session_id claim

**TTL:** 24 hours (default, configurable)

**Scopes:** Session-specific metadata (user_id, roles, permissions)

**Content:**
```json
{
  "session_id": "sess-uuid-12345",
  "user_id": "alice@company.com",
  "username": "alice",
  "roles": ["agent_operator"],
  "issued_at": 1720000000,
  "expires_at": 1720086400,
  "ip_address": "10.20.30.40",
  "user_agent": "Mozilla/5.0...",
  "iss": "codex-session"
}
```

**Characteristics:**
- Automatically issued on login
- Tracked in session database
- Can be revoked immediately (logout)
- Contains client metadata (IP, user agent)

**Revocation:**
```python
# Logout revokes session
POST /api/v1/auth/logout
{
  "session_token": "session_token_value"
}
→ Session marked as revoked
→ Token is blacklisted
```

### API Token

**Purpose:** Service-to-service authentication (applications, scripts)

**Format:** Base64-encoded (similar to GitHub PAT)

**TTL:** Long-lived (90 days, configurable)

**Scopes:** Service-specific permissions (e.g., "read_agents", "execute_workflows")

**Creation:**
```bash
POST /api/v1/auth/tokens
{
  "name": "DataPipeline Service",
  "scopes": ["api:agents:read", "api:workflows:exec"],
  "expires_in": 7776000  # 90 days in seconds
}

→ {
  "token": "codex_pat_abc123def456ghi789",
  "created_at": 1720000000,
  "expires_at": 1727776000,
  "scopes": ["api:agents:read", "api:workflows:exec"]
}
```

**Usage:**
```bash
# Service makes API call with API token
curl -H "Authorization: ******" \
  https://api.codex.local/v1/agents
```

**Security:**
- Cannot be revoked without manual request
- Survives across service restarts
- Typically stored in environment variables
- Rotation recommended monthly

**Rotation Process:**
```bash
# Create new token
POST /api/v1/auth/tokens (new token issued)

# Update service configuration (new token)
# Verify service works with new token

# Revoke old token
DELETE /api/v1/auth/tokens/{old_token_id}
```

---

## Token Lifecycle

### Complete Token Flow

```
User Login
    ↓
┌───────────────────────────────────────┐
│ Issue Tokens                          │
│ - Access Token (15 min)               │
│ - Refresh Token (30 days)             │
│ - Session Token (24 hours)            │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ Access Token Active                   │
│ - Use for all API calls               │
│ - Verify signature on each request    │
│ - Check expiration time               │
└───────────────────────────────────────┘
    ↓
[15 minutes]
    ↓
┌───────────────────────────────────────┐
│ Access Token Expired                  │
│ - API calls with expired token fail   │
│ - Return 401 Unauthorized             │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ Refresh Access Token                  │
│ - Use refresh token to get new token  │
│ - Issue new access token (15 min)     │
│ - Refresh token refreshed (30 days)   │
└───────────────────────────────────────┘
    ↓
[Continue using new access token]
    ↓
[After 30 days of no refresh activity]
    ↓
┌───────────────────────────────────────┐
│ Refresh Token Expired                 │
│ - User must re-authenticate           │
│ - New login required                  │
└───────────────────────────────────────┘
    ↓
User Login Again
```

### Expiration & Refresh

```python
class TokenManager:
    """Manage token lifecycle."""
    
    def validate_token(self, token: str) -> dict:
        """Validate token and return claims."""
        try:
            payload = jwt.decode(token, self.public_key, algorithms=["RS256"])
            
            # Check expiration
            if payload["exp"] < time.time():
                raise TokenExpiredError("Token expired")
            
            return payload
            
        except jwt.InvalidSignatureError:
            raise TokenInvalidError("Invalid signature")
        except jwt.DecodeError:
            raise TokenInvalidError("Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Get new access token from refresh token."""
        # Validate refresh token
        if not self._validate_refresh_token(refresh_token):
            raise TokenInvalidError("Invalid refresh token")
        
        # Check if refresh token has been revoked
        if self._is_revoked(refresh_token):
            raise TokenRevokedError("Refresh token revoked")
        
        # Issue new access token
        return self.issue_token(
            user_id=self.refresh_token_user(refresh_token),
            ttl=900  # 15 minutes
        )
```

---

## Scope Model

### Scope Hierarchy

Scopes are organized in a hierarchical structure:

```
api:*                        (All API scopes)
  ├── api:agents:*           (All agent scopes)
  │   ├── api:agents:read    (Read agents)
  │   ├── api:agents:write   (Create/update agents)
  │   └── api:agents:exec    (Execute agents)
  ├── api:workflows:*        (All workflow scopes)
  │   ├── api:workflows:read
  │   ├── api:workflows:exec
  │   └── api:workflows:approve
  └── api:secrets:*          (All secret scopes)
      ├── api:secrets:read
      └── api:secrets:rotate

governance:*                 (All governance scopes)
  ├── governance:approve     (Approve requests)
  └── governance:audit       (Access audit logs)

admin:*                      (Admin scopes)
  ├── admin:users:*
  ├── admin:roles:*
  └── admin:config:*
```

### Scope Definitions

#### api:agents:read
**Permission:** Read agent definitions and status  
**Resources:** Agent metadata, configurations, logs  
**Denied:** Agent modification, execution (unless write scope)

#### api:agents:write
**Permission:** Create, update, delete agents  
**Requires:** api:agents:read (implied)  
**Resources:** Agent metadata, parameters  
**Denied:** Agent execution, role assignment

#### api:agents:exec
**Permission:** Execute agents and run tasks  
**Requires:** api:agents:read (implied)  
**Resources:** Agent executions, task runs  
**Denied:** Agent definition modification

#### api:workflows:read
**Permission:** Read workflow definitions  
**Resources:** Workflow metadata, execution history  

#### api:workflows:exec
**Permission:** Trigger workflow execution  
**Requires:** api:workflows:read (implied)  

#### api:workflows:approve
**Permission:** Approve pending workflow approvals  
**Resources:** Approval requests  

#### api:secrets:read
**Permission:** Read secrets (metadata only, not values)  
**Resources:** Secret metadata (name, type, rotation date)  
**Never:** Secret values in logs

#### api:secrets:rotate
**Permission:** Rotate/update secrets  
**Requires:** api:secrets:read (implied)  
**Audit:** All rotations logged with details

#### governance:approve
**Permission:** Approve governance requests  
**Scope:** Approval workflows  
**Authority:** Limited to policy scope

#### governance:audit
**Permission:** Read audit logs  
**Resources:** Complete audit trail  
**Retention:** 90 days (configurable)

### Scope Assignment Rules

Scopes are assigned based on user roles:

```python
ROLE_SCOPE_MAPPING = {
    CodexRole.SYSTEM_ADMIN: [
        "api:*",
        "governance:*",
        "admin:*"
    ],
    CodexRole.AGENT_OPERATOR: [
        "api:agents:read",
        "api:agents:write",
        "api:agents:exec",
        "api:workflows:read",
        "api:workflows:exec",
        "governance:audit"
    ],
    CodexRole.CI_OPERATOR: [
        "api:workflows:read",
        "api:workflows:exec",
        "api:workflows:approve",
        "governance:audit"
    ],
    CodexRole.SECURITY_REVIEWER: [
        "api:agents:read",
        "api:workflows:read",
        "api:workflows:approve",
        "api:secrets:read",
        "governance:approve",
        "governance:audit"
    ],
    CodexRole.DOC_MAINTAINER: [
        "api:docs:*"
    ],
    CodexRole.AGENT_READER: [
        "api:agents:read",
        "api:workflows:read",
        "governance:audit"
    ],
    CodexRole.GUEST: [
        "api:public:read"
    ]
}
```

### Scope Validation

```python
def check_scope(token: str, required_scope: str) -> bool:
    """Check if token has required scope."""
    
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    token_scopes = payload.get("scopes", [])
    
    # Direct scope match
    if required_scope in token_scopes:
        return True
    
    # Wildcard scope match
    # e.g., "api:*" matches "api:agents:read"
    parts = required_scope.split(":")
    for i in range(len(parts)):
        wildcard = ":".join(parts[:i+1]) + ":*"
        if wildcard in token_scopes:
            return True
    
    return False
```

---

## Token Management API

### Issue Access Token

```bash
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "alice@company.com",
  "password": "secure_password_123",
  "mfa_code": "123456"  # Optional if MFA enabled
}

# Response
{
  "access_token": "eyJhbGc...",
  "refresh_token": "opaque_token_xyz",
  "session_token": "eyJzZXNz...",
  "token_type": "Bearer",
  "expires_in": 900,
  "scope": "api:agents:read api:agents:write api:workflows:exec"
}
```

### Issue API Token (Service Account)

```bash
POST /api/v1/auth/tokens
Content-Type: application/json
Authorization: ******

{
  "name": "DataPipeline Service",
  "scopes": ["api:agents:read", "api:workflows:exec"],
  "expires_in": 7776000  # 90 days
}

# Response
{
  "token": "codex_pat_abc123def456ghi789",
  "name": "DataPipeline Service",
  "scopes": ["api:agents:read", "api:workflows:exec"],
  "created_at": 1720000000,
  "expires_at": 1727776000
}
```

### Validate Token

```bash
POST /api/v1/auth/token/validate
Content-Type: application/json

{
  "token": "eyJhbGc..."
}

# Response (valid token)
{
  "valid": true,
  "user_id": "alice@company.com",
  "roles": ["agent_operator"],
  "scopes": ["api:agents:*", "api:workflows:exec"],
  "expires_at": 1720000900
}

# Response (invalid/expired token)
{
  "valid": false,
  "error": "Token expired",
  "error_code": "TOKEN_EXPIRED"
}
```

### Refresh Access Token

```bash
POST /api/v1/auth/token/refresh
Content-Type: application/json

{
  "refresh_token": "opaque_token_xyz"
}

# Response
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### Revoke Token

```bash
POST /api/v1/auth/token/revoke
Content-Type: application/json
Authorization: ******

{
  "token": "codex_pat_abc123def456ghi789"  # For API tokens
  # OR
  "session_token": "eyJzZXNz..."  # For session tokens
}

# Response
{
  "revoked": true,
  "revoked_at": 1720000100
}
```

### List Tokens

```bash
GET /api/v1/auth/tokens
Authorization: ******

# Response
{
  "tokens": [
    {
      "token_id": "token_001",
      "name": "DataPipeline Service",
      "type": "api_token",
      "created_at": 1720000000,
      "expires_at": 1727776000,
      "last_used_at": 1720086400,
      "scopes": ["api:agents:read", "api:workflows:exec"]
    }
  ]
}
```

---

## Implementation Examples

### Example 1: Python Client with Token Refresh

```python
import requests
from datetime import datetime

class CodexClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def login(self):
        """Authenticate and obtain tokens."""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/token",
            json={"username": self.username, "password": self.password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expires_at = datetime.now().timestamp() + data["expires_in"]
    
    def _refresh_if_needed(self):
        """Refresh access token if expiring soon."""
        if datetime.now().timestamp() >= self.token_expires_at - 60:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/token/refresh",
                json={"refresh_token": self.refresh_token}
            )
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires_at = datetime.now().timestamp() + data["expires_in"]
    
    def get_agents(self) -> list:
        """Fetch agents (refreshes token automatically)."""
        self._refresh_if_needed()
        
        response = requests.get(
            f"{self.base_url}/api/v1/agents",
            headers={"Authorization": f"******"}
        )
        response.raise_for_status()
        return response.json()["agents"]

# Usage
client = CodexClient("https://api.codex.local", "alice", "password")
client.login()
agents = client.get_agents()  # Token auto-refreshes if needed
```

### Example 2: Service Account with API Token

```python
import os
import requests

class CodexService:
    def __init__(self, service_name: str, api_token: str = None):
        self.base_url = os.getenv("CODEX_API_URL", "https://api.codex.local")
        self.api_token = api_token or os.getenv("CODEX_API_TOKEN")
        self.service_name = service_name
    
    def execute_agent(self, agent_id: str) -> dict:
        """Execute an agent."""
        response = requests.post(
            f"{self.base_url}/api/v1/agents/{agent_id}/execute",
            headers={"Authorization": f"******"}
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_workflow(self, workflow_id: str) -> dict:
        """Trigger a workflow."""
        response = requests.post(
            f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
            headers={"Authorization": f"******"}
        )
        response.raise_for_status()
        return response.json()

# Usage
service = CodexService("DataPipeline")
result = service.execute_agent("agent_001")
print(f"Execution: {result['execution_id']}")
```

### Example 3: Token Scope Validation in Middleware

```python
from functools import wraps
import jwt

def require_scope(*required_scopes):
    """Decorator to check token has required scope."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Extract token from header
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return {"error": "Missing token"}, 401
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            try:
                # Decode and validate token
                payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
                token_scopes = payload.get("scopes", [])
                
                # Check if token has required scopes
                has_scope = False
                for required_scope in required_scopes:
                    if required_scope in token_scopes:
                        has_scope = True
                        break
                    
                    # Check for wildcard scopes
                    parts = required_scope.split(":")
                    for i in range(len(parts)):
                        wildcard = ":".join(parts[:i+1]) + ":*"
                        if wildcard in token_scopes:
                            has_scope = True
                            break
                
                if not has_scope:
                    return {"error": f"Insufficient scope"}, 403
                
                # Attach user info to request
                request.user_id = payload["user_id"]
                request.roles = payload["roles"]
                
                return func(request, *args, **kwargs)
            
            except jwt.ExpiredSignatureError:
                return {"error": "Token expired"}, 401
            except jwt.InvalidSignatureError:
                return {"error": "Invalid token"}, 401
        
        return wrapper
    return decorator

# Usage
@require_scope("api:agents:read")
def get_agents(request):
    """Get agents (requires api:agents:read scope)."""
    return {"agents": [...]}, 200

@require_scope("api:agents:write", "admin:*")
def create_agent(request):
    """Create agent (requires write scope or admin)."""
    return {"agent_id": "new_agent"}, 201
```

---

## Security Considerations

### 1. Token Storage

**Do NOT store sensitive tokens in:**
- Browser localStorage (vulnerable to XSS)
- Browser cookies without HTTPOnly flag
- Application logs
- Configuration files

**Secure Storage:**
- HTTP-only cookies (for web apps)
- Secure enclave/keychain (mobile apps)
- Environment variables (services)
- Secret management system (infrastructure)

### 2. Token Transmission

**Always use HTTPS:**
```bash
#  GOOD
curl -H "Authorization: ******" https://api.codex.local/...

#  BAD
curl -H "Authorization: ******" http://api.codex.local/...
```

**Never in URLs:**
```bash
#  BAD
https://api.codex.local/api/v1/agents?token=secret_token

#  GOOD
curl -H "Authorization: ******" https://api.codex.local/api/v1/agents
```

### 3. Token Rotation

**Access Tokens:** Auto-refresh every 15 minutes  
**Refresh Tokens:** Rotate on every refresh (old token revoked)  
**API Tokens:** Rotate monthly (manual process)

```python
# Monthly rotation for API tokens
def rotate_api_token():
    # Create new token with same scopes
    new_token = api_client.create_token(
        name="DataPipeline Service (rotated)",
        scopes=old_token_scopes
    )
    
    # Update service configuration
    update_environment("CODEX_API_TOKEN", new_token)
    
    # Verify service works
    test_service_connectivity()
    
    # Revoke old token
    api_client.revoke_token(old_token)
```

### 4. Scope Minimization

Always request minimum scopes needed:

```python
#  GOOD: Specific scopes
scopes = ["api:agents:read", "api:workflows:exec"]

#  BAD: Overly broad
scopes = ["api:*"]

#  WORSE: Admin scope for non-admin task
scopes = ["admin:*"]
```

### 5. Token Revocation on Logout

Always revoke session tokens on logout:

```python
def logout(session_token: str):
    """Revoke session token on logout."""
    revoke_response = requests.post(
        "/api/v1/auth/token/revoke",
        json={"session_token": session_token}
    )
    
    if revoke_response.status_code == 200:
        # Clear local session
        clear_session()
    else:
        logger.error("Failed to revoke session token")
```

---

## References

- [Governance API Reference](../api/governance-api-reference.md)
- [RBAC Design](../arch/RBAC-design-detailed.md)
- [Security Best Practices](../ops/security-runbooks.md)
- [Audit Logging](../ops/security-runbooks.md#audit-logging)

---

**Last Updated: 2026-07-08
**Version:** 1.0.0  
**Status:** Production Ready
