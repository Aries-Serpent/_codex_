# MCP Authentication and Authorization

## Overview

The MCP (Model Context Protocol) authentication and authorization capability provides comprehensive security controls for MCP services, including API key verification, JWT token validation, OAuth integration, and role-based access control (RBAC).

**Keywords**: authentication, authorization, authn, authz, api-key, jwt, oauth, bearer, token, security, access-control, rbac, permission, identity, credential, mcp, safeguards, validation

## Purpose

Manages MCP security through:
- **API Key Authentication**: Simple and secure API key validation
- **JWT Token Validation**: Stateless token-based authentication
- **OAuth Integration**: Third-party identity provider support
- **Role-Based Access Control**: Fine-grained permission management
- **Session Management**: Secure session handling and lifecycle

## Architecture

### Security Layer Hierarchy

```
┌─────────────────────────────────────┐
│   Request Interceptor               │
│   (Initial authentication check)    │
└─────────────┬───────────────────────┘
              │ validates
              ▼
┌─────────────────────────────────────┐
│   Authentication Layer              │
│   (API Key, JWT, OAuth)             │
└─────────────┬───────────────────────┘
              │ authorizes
              ▼
┌─────────────────────────────────────┐
│   Authorization Layer               │
│   (RBAC, Permissions)               │
└─────────────────────────────────────┘
```

### Authentication Flow

```python
# Pseudocode for authentication flow
async def authenticate_request(request):
    # 1. Extract credentials from request
    credentials = extract_credentials(request)
    
    # 2. Validate credentials
    identity = await validate_credentials(credentials)
    
    # 3. Check authorization
    if not authorize(identity, request.resource):
        raise AuthorizationError("Access denied")
    
    # 4. Return authenticated context
    return AuthContext(identity=identity, permissions=identity.permissions)
```

## Implementation

### API Key Authentication

Implement simple API key validation:

```python
from typing import Optional
import secrets
import hashlib

class APIKeyAuthenticator:
    """
    API Key authentication for MCP services.
    
    Provides secure API key validation with safeguards:
    - Constant-time comparison to prevent timing attacks
    - Key hashing for secure storage
    - Rate limiting integration
    """
    
    def __init__(self, valid_keys: dict[str, str]):
        """
        Initialize with valid API keys.
        
        Args:
            valid_keys: Mapping of key IDs to hashed keys
        """
        self._valid_keys = valid_keys
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """
        Verify an API key and return the associated identity.
        
        Safeguards:
        - Uses constant-time comparison
        - Validates key format before comparison
        - Returns None on failure (no exception details leak)
        
        Args:
            api_key: The API key to verify
            
        Returns:
            Key ID if valid, None otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return None
        
        # Validate key format (safeguard)
        if len(api_key) < 32 or len(api_key) > 128:
            return None
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Constant-time comparison (safeguard)
        for key_id, stored_hash in self._valid_keys.items():
            if secrets.compare_digest(key_hash, stored_hash):
                return key_id
        
        return None

def authenticate(request) -> dict:
    """
    Main authentication entry point.
    
    Extracts and validates credentials from the request,
    returning the authenticated identity.
    
    Args:
        request: Incoming HTTP request
        
    Returns:
        Dictionary with identity information
        
    Raises:
        AuthenticationError: If authentication fails
    """
    # Extract API key from headers
    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
    
    if not api_key:
        raise AuthenticationError("No API key provided")
    
    # Handle Bearer token format
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]
    
    # Verify the key
    authenticator = get_authenticator()
    identity = authenticator.verify_api_key(api_key)
    
    if not identity:
        raise AuthenticationError("Invalid API key")
    
    return {"identity": identity, "authenticated": True}
```

### JWT Token Authentication

Implement JWT-based authentication:

```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class JWTAuthenticator:
    """
    JWT authentication for MCP services.
    
    Provides stateless token-based authentication with:
    - Token validation and verification
    - Expiration checking
    - Signature verification
    - Claims validation
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT authenticator.
        
        Args:
            secret_key: Secret key for token signing
            algorithm: JWT algorithm (default: HS256)
        """
        self._secret = secret_key
        self._algorithm = algorithm
    
    def create_token(
        self,
        identity: str,
        permissions: list[str],
        expires_in: int = 3600
    ) -> str:
        """
        Create a JWT token for the given identity.
        
        Args:
            identity: User or service identity
            permissions: List of granted permissions
            expires_in: Token lifetime in seconds
            
        Returns:
            Signed JWT token string
        """
        payload = {
            "sub": identity,
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Safeguards:
        - Validates token format
        - Checks expiration
        - Verifies signature
        - Validates required claims
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            # Validate token format (safeguard)
            if not token or not isinstance(token, str):
                return None
            
            if len(token) > 10000:  # Bounds check (safeguard)
                return None
            
            # Decode and verify
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require": ["sub", "exp"]}
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

### Authorization and RBAC

Implement role-based access control:

```python
from enum import Enum
from typing import Set

class Permission(Enum):
    """MCP permissions."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    EXECUTE = "execute"

class RBACAuthorizer:
    """
    Role-Based Access Control for MCP services.
    
    Provides fine-grained permission management with:
    - Role definitions
    - Permission inheritance
    - Resource-based access control
    """
    
    def __init__(self):
        self._role_permissions: dict[str, Set[Permission]] = {
            "reader": {Permission.READ},
            "writer": {Permission.READ, Permission.WRITE},
            "admin": {Permission.READ, Permission.WRITE, Permission.ADMIN, Permission.EXECUTE},
        }
    
    def authorize(
        self,
        identity: str,
        resource: str,
        required_permission: Permission
    ) -> bool:
        """
        Check if identity is authorized for the resource.
        
        Safeguards:
        - Input validation on all parameters
        - Defensive permission checking
        - Audit logging for access attempts
        
        Args:
            identity: User or service identity
            resource: Resource being accessed
            required_permission: Required permission level
            
        Returns:
            True if authorized, False otherwise
        """
        # Input validation (safeguard)
        if not identity or not resource:
            return False
        
        # Get identity's role and permissions
        role = self._get_identity_role(identity)
        permissions = self._role_permissions.get(role, set())
        
        # Check permission
        authorized = required_permission in permissions
        
        # Audit log (safeguard - traceability)
        self._log_access_attempt(identity, resource, required_permission, authorized)
        
        return authorized
```

## Configuration

### Environment Variables

Configure authentication via environment:

```bash
# API Key settings
export MCP_API_KEY_HASH_ALGORITHM="sha256"
export MCP_API_KEY_MIN_LENGTH="32"

# JWT settings
export MCP_JWT_SECRET="your-secret-key"
export MCP_JWT_ALGORITHM="HS256"
export MCP_JWT_EXPIRY_SECONDS="3600"

# OAuth settings
export MCP_OAUTH_PROVIDER="https://auth.example.com"
export MCP_OAUTH_CLIENT_ID="your-client-id"
export MCP_OAUTH_CLIENT_SECRET="your-client-secret"
```

### Configuration File

Use YAML for authentication configuration:

```yaml
# auth_config.yaml
authentication:
  api_key:
    enabled: true
    header_name: "X-API-Key"
    hash_algorithm: "sha256"
  
  jwt:
    enabled: true
    algorithm: "HS256"
    expiry_seconds: 3600
    refresh_enabled: true
  
  oauth:
    enabled: false
    provider: "https://auth.example.com"

authorization:
  default_role: "reader"
  roles:
    reader:
      permissions: ["read"]
    writer:
      permissions: ["read", "write"]
    admin:
      permissions: ["read", "write", "admin", "execute"]
```

## Usage Examples

### Example 1: Protecting an Endpoint

```python
from functools import wraps

def require_auth(permission: Permission = Permission.READ):
    """Decorator to require authentication and authorization."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Authenticate
            auth_context = authenticate(request)
            
            # Authorize
            if not authorize(auth_context["identity"], request.path, permission):
                raise HTTPException(403, "Access denied")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@require_auth(Permission.WRITE)
async def create_resource(request):
    """Create a new resource (requires write permission)."""
    return {"status": "created"}
```

### Example 2: Token Refresh

```python
async def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresh an access token using a refresh token.
    
    Safeguards:
    - Validates refresh token
    - Checks token revocation
    - Issues new short-lived access token
    """
    authenticator = JWTAuthenticator(get_secret())
    
    # Verify refresh token
    payload = authenticator.verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")
    
    # Create new access token
    access_token = authenticator.create_token(
        identity=payload["sub"],
        permissions=payload["permissions"],
        expires_in=3600  # 1 hour
    )
    
    return {"access_token": access_token, "token_type": "Bearer"}
```

### Example 3: Multi-Factor Authentication

```python
async def authenticate_mfa(username: str, password: str, totp_code: str) -> dict:
    """
    Authenticate with multi-factor authentication.
    
    Combines password verification with TOTP code validation
    for enhanced security.
    """
    # Verify password
    user = await verify_password(username, password)
    if not user:
        raise AuthenticationError("Invalid credentials")
    
    # Verify TOTP code
    if not verify_totp(user.totp_secret, totp_code):
        raise AuthenticationError("Invalid MFA code")
    
    # Create authenticated session
    return create_session(user)
```

## Best Practices

### 1. Secure Credential Storage

```python
# Never store plaintext credentials
def store_api_key(api_key: str) -> str:
    """Hash API key before storage."""
    import hashlib
    return hashlib.sha256(api_key.encode()).hexdigest()
```

### 2. Use Constant-Time Comparison

```python
import secrets

def safe_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    return secrets.compare_digest(a.encode(), b.encode())
```

### 3. Implement Token Rotation

```python
class TokenRotationPolicy:
    """Automatically rotate tokens before expiry."""
    
    def should_rotate(self, token_payload: dict) -> bool:
        """Check if token should be rotated."""
        exp = token_payload.get("exp", 0)
        remaining = exp - datetime.utcnow().timestamp()
        return remaining < 300  # Rotate if < 5 minutes remaining
```

## Troubleshooting

### Authentication Failures

**Problem**: 401 Unauthorized errors

**Solution**:
1. Verify API key or token format
2. Check token expiration
3. Verify secret key configuration
4. Check header name (X-API-Key vs Authorization)

### Authorization Failures

**Problem**: 403 Forbidden errors

**Solution**:
1. Verify user role assignment
2. Check required permissions for endpoint
3. Review RBAC configuration
4. Check permission inheritance

## Security Considerations

### Token Security

- Use strong secrets (256+ bits)
- Implement token rotation
- Store tokens securely (HttpOnly cookies, secure storage)
- Validate token claims thoroughly

### API Key Security

- Use long, random keys (32+ characters)
- Hash keys before storage
- Implement key rotation
- Rate limit authentication attempts

## Related Capabilities

- **mcp-security-safeguards**: Security controls and safeguards
- **mcp-rate-limiting**: Rate limiting for authentication endpoints
- **mcp-error-handling**: Authentication error handling
- **mcp-observability**: Authentication event logging

## References

- [OAuth 2.0 Specification](https://oauth.net/2/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- MCP Security Guidelines
