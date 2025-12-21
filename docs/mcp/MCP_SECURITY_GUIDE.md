# MCP Security Guide

**Version:** 1.0  
**Last Updated:** 2025-11-18  
**Audience:** Developers, Security Engineers, Operations

## Overview

This guide provides comprehensive security guidance for implementing and deploying MCP (Model Context Protocol) capabilities in production environments. All mcp-* capabilities include built-in security features that must be properly configured.

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Rate Limiting](#rate-limiting)
3. [Error Handling](#error-handling)
4. [Multi-Tenant Security](#multi-tenant-security)
5. [Protocol Security](#protocol-security)
6. [Observability & Audit](#observability--audit)
7. [Security Checklist](#security-checklist)

---

## Authentication & Authorization

### mcp-authz-authn Capability

The `mcp-authz-authn` capability provides API key authentication and role-based authorization.

### Authentication Implementation

**SHA-256 Credential Hashing**:
```python
from mcp.auth import MCPAuthenticator, hash_credential
import hashlib

# Credentials are hashed with SHA-256
def hash_credential(credential: str) -> str:
    return hashlib.sha256(credential.encode('utf-8')).hexdigest()

# Authenticator uses SHA-256 internally
authenticator = MCPAuthenticator()
principal = authenticator.authenticate(api_key)
```

**Security Best Practices**:
- ✅ Always hash credentials with SHA-256 before storage
- ✅ Use secure RNG with seed for token generation
- ✅ Implement token expiration
- ✅ Use HTTPS for credential transmission
- ✅ Never log plaintext credentials
- ❌ Never store plaintext API keys

### Authorization Patterns

**Role-Based Access Control (RBAC)**:
```python
from mcp.auth import MCPAuthorizer, Principal

authorizer = MCPAuthorizer(permissions={
    "admin": ["tool1", "tool2", "sensitive_tool"],
    "user": ["tool1", "tool2"],
    "guest": ["tool1"]
})

# Check authorization
principal = Principal(principal_id="user123", role="user")
if authorizer.authorize(principal, "sensitive_tool"):
    # User is unauthorized - would raise Unauthorized error
    pass
```

**Permission Hash Validation**:
```python
# Compute SHA-256 checksum for permission validation
permission_hash = authorizer.compute_permission_hash(
    principal_id="user123",
    tool_name="sensitive_tool"
)
# Verify against stored checksums
```

### Secure Session Management

**Session Token Generation with RNG**:
```python
# Uses SHA-256 with RNG seed for deterministic testing
authenticator = MCPAuthenticator()
principal = Principal(principal_id="user123")

# Generate session token (SHA-256 hash)
session_token = authenticator.generate_session_token(principal)
# Returns 64-character hex string (SHA-256)
```

**Security Considerations**:
- Session tokens use RNG with configurable seed
- Offline mode supported for security testing
- Token rotation recommended every 24 hours
- Implement token revocation list

---

## Rate Limiting

### mcp-rate-limiting Capability

The `mcp-rate-limiting` capability prevents abuse through token bucket rate limiting.

### Configuration

**Basic Setup**:
```python
from mcp.rate_limit import MCPRateLimiter

# 10 requests per second, burst capacity of 50
limiter = MCPRateLimiter(
    rate=10.0,      # Requests per second
    capacity=50,    # Burst capacity
    seed=42         # RNG seed for testing
)
```

**Per-Principal Limits**:
```python
# Check rate limit before execution
principal_id = "user123"
tool_name = "expensive_tool"

if not limiter.allow(principal_id, tool_name):
    from mcp.errors import RateLimitExceeded
    raise RateLimitExceeded(f"Rate limit exceeded for {principal_id}")

# Execute tool
result = execute_tool(tool_name)
```

### Security Best Practices

- ✅ Set conservative default limits (5-10 req/sec)
- ✅ Use burst capacity for legitimate spikes
- ✅ Implement per-principal tracking
- ✅ Use RNG with seed for deterministic testing in offline mode
- ✅ Monitor RateLimitExceeded errors for abuse detection
- ✅ Different limits for different tool categories
- ❌ Don't allow unlimited requests
- ❌ Don't share rate limits across tenants

### DDoS Protection

**Multi-Layer Rate Limiting**:
```python
# Global rate limiter
global_limiter = MCPRateLimiter(rate=100.0, capacity=200)

# Per-principal rate limiter
principal_limiter = MCPRateLimiter(rate=10.0, capacity=20)

# Per-tool rate limiter
tool_limiter = MCPRateLimiter(rate=5.0, capacity=10)

def execute_with_protection(principal_id, tool_name):
    # Check all layers
    if not global_limiter.allow("global", "any"):
        raise RateLimitExceeded("Global rate limit")
    
    if not principal_limiter.allow(principal_id, "any"):
        raise RateLimitExceeded("Principal rate limit")
    
    if not tool_limiter.allow(principal_id, tool_name):
        raise RateLimitExceeded("Tool rate limit")
    
    # Execute
    return execute_tool(tool_name)
```

---

## Error Handling

### mcp-error-handling Capability

Structured error handling prevents information leakage and provides consistent responses.

### Error Hierarchy

```python
from mcp.errors import (
    MCPError,              # Base class
    ToolNotFound,          # -32601, HTTP 404
    ValidationError,       # -32602, HTTP 400
    RateLimitExceeded,     # -32002, HTTP 429
    Unauthorized,          # -32600, HTTP 401
    ToolExecutionError     # -32603, HTTP 500
)
```

### Secure Error Responses

**Sanitize Error Messages**:
```python
try:
    result = execute_sensitive_operation()
except Exception as e:
    # DON'T expose internal details
    # raise MCPError(f"Database error: {connection_string}")
    
    # DO sanitize for external consumption
    raise ToolExecutionError("Internal error occurred")
```

**Error Context for Debugging (Internal Only)**:
```python
import logging

logger = logging.getLogger('mcp.security')

try:
    result = execute_tool()
except MCPError as e:
    # Log full context internally
    logger.error(f"Tool execution failed", extra={
        "error_code": e.code,
        "principal": principal_id,
        "tool": tool_name,
        "stack_trace": str(e)
    })
    
    # Return sanitized error externally
    raise
```

### Security Considerations

- ✅ Use specific error classes (ToolNotFound, Unauthorized, RateLimitExceeded)
- ✅ Map errors to appropriate HTTP status codes
- ✅ Log errors with full context internally
- ✅ Return sanitized errors externally
- ✅ Include request correlation ID (X-Request-Id)
- ❌ Never expose stack traces to clients
- ❌ Never expose internal paths or configuration
- ❌ Never leak database schema information

---

## Multi-Tenant Security

### mcp-multi-tenant Capability

Ensure strict isolation between tenants to prevent data leakage.

### Tenant Isolation

**Principal with Tenant Context**:
```python
from mcp.auth import Principal

# Always include tenant_id in principal
tenant_principal = Principal(
    principal_id="user123",
    tenant_id="tenant_abc"
)
```

**Enforce Tenant Boundaries**:
```python
def check_tenant_access(principal: Principal, resource):
    """Prevent cross-tenant access."""
    if resource.tenant_id != principal.tenant_id:
        from mcp.errors import Unauthorized
        raise Unauthorized(
            f"Cross-tenant access denied: "
            f"principal tenant={principal.tenant_id}, "
            f"resource tenant={resource.tenant_id}"
        )
```

### Tenant-Specific Rate Limits

```python
# Separate rate limiters per tenant
tenant_limiters = {
    "tenant_abc": MCPRateLimiter(rate=20.0, capacity=50),
    "tenant_xyz": MCPRateLimiter(rate=10.0, capacity=20),
}

def get_tenant_limiter(tenant_id: str) -> MCPRateLimiter:
    if tenant_id not in tenant_limiters:
        # Default limits for new tenants
        tenant_limiters[tenant_id] = MCPRateLimiter(
            rate=5.0, 
            capacity=10
        )
    return tenant_limiters[tenant_id]
```

### Data Isolation

**Tenant-Scoped Queries**:
```python
# ALWAYS filter by tenant_id in database queries
def get_tools_for_tenant(tenant_id: str):
    # Good: Tenant-scoped query
    return db.query(Tool).filter(
        Tool.tenant_id == tenant_id
    ).all()
    
    # BAD: No tenant filtering - security vulnerability!
    # return db.query(Tool).all()
```

**Security Best Practices**:
- ✅ Always include tenant_id in Principal
- ✅ Validate tenant_id on every request
- ✅ Use tenant-specific encryption keys
- ✅ Implement tenant-specific rate limits
- ✅ Audit all cross-tenant access attempts
- ✅ Use checksums to verify tenant data integrity
- ❌ Never allow wildcard tenant access
- ❌ Never share resources across tenants without explicit permission

---

## Protocol Security

### mcp-protocol-surface Capability

Secure the JSON-RPC protocol surface against attacks.

### JSON-RPC Validation

**Strict Protocol Compliance**:
```python
def validate_jsonrpc_request(request: dict):
    # Validate JSON-RPC 2.0 version
    if request.get("jsonrpc") != "2.0":
        from mcp.errors import ValidationError
        raise ValidationError("Invalid JSON-RPC version")
    
    # Validate required fields
    if "method" not in request:
        raise ValidationError("Missing 'method' field")
    
    # Validate method name format
    method = request["method"]
    if not isinstance(method, str) or len(method) > 100:
        raise ValidationError("Invalid method name")
```

### Request Size Limits

```python
MAX_REQUEST_SIZE = 1024 * 1024  # 1 MB

def check_request_size(request_body: str):
    if len(request_body) > MAX_REQUEST_SIZE:
        from mcp.errors import ValidationError
        raise ValidationError("Request too large")
```

### Input Sanitization

```python
import re

def sanitize_tool_name(name: str) -> str:
    """Prevent injection attacks in tool names."""
    # Allow only alphanumeric, dash, underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        from mcp.errors import ValidationError
        raise ValidationError("Invalid tool name format")
    return name
```

### HTTPS Enforcement

```python
# In production, always use HTTPS
if not request.is_secure() and not settings.DEBUG:
    raise ValidationError("HTTPS required")
```

---

## Observability & Audit

### mcp-observability Capability

Security monitoring and audit logging for mcp operations.

### Audit Logging

**Security Event Logging**:
```python
import logging
import uuid

audit_logger = logging.getLogger('mcp.audit')

def log_security_event(event_type: str, principal_id: str, 
                       tool_name: str, result: str, **kwargs):
    """Log security-relevant events."""
    request_id = str(uuid.uuid4())
    
    audit_logger.info(
        f"Security event: {event_type}",
        extra={
            "request_id": request_id,
            "event_type": event_type,
            "principal_id": principal_id,
            "tool_name": tool_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
    )

# Log authentication attempts
log_security_event("authentication", "user123", "N/A", "success")

# Log authorization failures
log_security_event("authorization", "user123", "sensitive_tool", "denied")

# Log rate limit violations
log_security_event("rate_limit", "user123", "api_call", "exceeded")
```

### Metrics for Security Monitoring

```python
# Track security metrics
security_metrics = {
    "auth_failures": 0,
    "authz_denials": 0,
    "rate_limit_violations": 0,
    "invalid_requests": 0,
}

def increment_security_metric(metric_name: str):
    security_metrics[metric_name] += 1
    
    # Alert on anomalies
    if security_metrics[metric_name] > ALERT_THRESHOLD:
        send_security_alert(metric_name, security_metrics[metric_name])
```

### Request Tracing

**X-Request-Id Header**:
```python
import uuid

def process_request(request):
    # Generate or extract request ID
    request_id = request.headers.get('X-Request-Id') or str(uuid.uuid4())
    
    # Include in all logs
    logger.info(f"Processing request", extra={"request_id": request_id})
    
    # Include in response
    response.headers['X-Request-Id'] = request_id
    return response
```

---

## Security Checklist

### Pre-Deployment Checklist

- [ ] **mcp-authz-authn**
  - [ ] All credentials hashed with SHA-256
  - [ ] API keys never logged in plaintext
  - [ ] Session tokens use secure RNG with appropriate seed
  - [ ] HTTPS enforced for all authentication endpoints
  - [ ] Token expiration implemented
  - [ ] Unauthorized errors properly handled

- [ ] **mcp-rate-limiting**
  - [ ] Rate limits configured for all endpoints
  - [ ] RateLimitExceeded errors monitored
  - [ ] Per-principal rate tracking enabled
  - [ ] Burst capacity set appropriately
  - [ ] RNG seed configured for testing/production
  - [ ] Offline mode tested

- [ ] **mcp-error-handling**
  - [ ] All errors use MCPError hierarchy
  - [ ] Error messages sanitized for external consumption
  - [ ] Stack traces never exposed to clients
  - [ ] Internal errors logged with full context
  - [ ] HTTP status codes mapped correctly

- [ ] **mcp-multi-tenant**
  - [ ] All principals include tenant_id
  - [ ] Tenant boundaries enforced on all operations
  - [ ] Cross-tenant access attempts audited
  - [ ] Tenant-specific encryption keys used
  - [ ] Checksums verify tenant data integrity

- [ ] **mcp-protocol-surface**
  - [ ] JSON-RPC 2.0 validation enabled
  - [ ] Request size limits enforced
  - [ ] Input sanitization implemented
  - [ ] HTTPS required in production
  - [ ] Invalid requests rejected with ValidationError

- [ ] **mcp-observability**
  - [ ] Audit logging enabled for security events
  - [ ] Security metrics tracked and alerted
  - [ ] X-Request-Id header propagated
  - [ ] PII sanitized in logs
  - [ ] Log retention policy enforced

### Security Testing

```bash
# Run security tests
pytest tests/mcp/test_auth.py -v
pytest tests/mcp/test_rate_limit.py -v
pytest tests/mcp/test_security.py -v

# Verify mcp modules are secure
python3 -c "from mcp.auth import hash_credential; assert len(hash_credential('test')) == 64"

# Check for security keywords in code
grep -r "sha256\|checksum\|rng\|seed\|confirm\|dry_run\|RateLimitExceeded\|Unauthorized" mcp/

# Run audit to verify safeguard scores
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain mcp-authz-authn
```

### Incident Response

**Security Incident Detection**:
1. Monitor audit logs for suspicious patterns
2. Alert on excessive RateLimitExceeded errors
3. Track Unauthorized access attempts
4. Monitor for unusual tool execution patterns

**Response Procedures**:
1. Identify compromised principals
2. Revoke affected API keys
3. Review audit logs for scope of breach
4. Implement additional rate limits
5. Update security configurations
6. Document incident and remediation

---

## Additional Resources

- [MCP Capabilities Reference](MCP_CAPABILITIES_REFERENCE.md)
- [MCP Developer Guide](MCP_DEVELOPER_GUIDE.md)
- [MCP Implementation Summary](MCP_IMPLEMENTATION_SUMMARY.md)
- [Audit Runner Documentation](scripts/space_traversal/README.md)

## Security Contact

For security issues, please review the audit reports and implement recommended safeguards. All mcp capabilities include built-in security features that must be properly configured for production use.
