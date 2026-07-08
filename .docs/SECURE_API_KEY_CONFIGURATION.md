# Secure API Key Configuration

**Last Updated:** 2026-07-08  
**Status:** Phase 14 WS1 Security Remediation  
**Authority:** D-tier autonomous (@mbaetiong 2026-07-06)

## Overview

This document describes the secure configuration pattern for API keys in the Codex MCP server. All API keys must be provided via environment variables — no hardcoded defaults are permitted in source code.

## Rationale

Hardcoded credentials in source code represent a **CRITICAL** security vulnerability:

1. **Git History Exposure**: Once committed, credentials remain in git history indefinitely
2. **Unintended Disclosure**: Credentials may be logged, exposed in error messages, or included in deployments
3. **Credential Rotation**: Hardcoded values cannot be rotated without code changes and redeployment
4. **Audit Trail Loss**: Environment variables leave an audit trail; hardcoded values do not

## Configuration

### Production Mode (Online)

**Environment Variable:** `MCP_API_KEY`

```bash
# Set the API key before starting the server
export MCP_API_KEY="<your-production-api-key>"
python -m mcp.server.http
```

The server will:
1. Load the API key from `MCP_API_KEY`
2. Require the key in all authenticated requests
3. Log when the server starts with a valid key (without exposing the key)

### Development Mode (Offline)

**Environment Variable:** `MCP_OFFLINE` = `true`

```bash
# Disable authentication for local development
export MCP_OFFLINE=true
python -m mcp.server.http
```

The server will:
1. Skip all authentication checks
2. Allow anonymous requests
3. Log a warning that authentication is disabled

### Development with Test Keys (Local Testing)

For local testing with authentication:

```bash
# Set a test API key (use only for testing, not production values)
export MCP_API_KEY="test-key-12345"
python -m pytest tests/mcp/test_http_server.py -v
```

**Important:** Never commit actual production API keys to the repository.

### Middleware Development Keys

The `APIKeyAuthMiddleware` supports development key validation:

```bash
# Comma-separated list of valid development keys
export DEV_API_KEY="dev-key-1,dev-key-2,dev-key-3"
python -m uvicorn mcp.server.http:app
```

The middleware will:
1. Load keys from `DEV_API_KEY`
2. Validate incoming requests against those keys
3. Return 401 Unauthorized for unrecognized keys

## Implementation Pattern

### Enforcing Required Environment Variables

When implementing secure configuration:

```python
import os
import logging

logger = logging.getLogger(__name__)

def _get_api_key() -> str:
    """Retrieve API key from environment (required in online mode).
    
    Raises:
        RuntimeError: If MCP_API_KEY is not set in online mode
    """
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    
    key = os.environ.get("MCP_API_KEY")
    if not key:
        raise RuntimeError(
            "MCP_API_KEY is required in online mode. "
            "Set MCP_API_KEY=<key> or MCP_OFFLINE=true"
        )
    
    logger.debug("API key loaded from MCP_API_KEY")
    return key
```

**Key principles:**

1. ✅ **No defaults**: Don't provide hardcoded fallback values
2. ✅ **Fail fast**: Raise an error if required key is missing
3. ✅ **Safe logging**: Log the fact that a key was loaded, not the key itself
4. ✅ **Environment only**: Read from environment variables, never from files/config without encryption

### Safe Logging

When logging authentication-related information:

```python
# ✅ CORRECT: Log operation without exposing secret
logger.info(
    "API authentication validated",
    extra={"source": "MCP_API_KEY", "status": "success"}
)

# ❌ WRONG: Never log the actual key
# logger.info(f"API key: {api_key[:10]}...")
```

## Testing

Tests must provide API keys via environment variables or fixtures:

```python
def test_authenticated_request(monkeypatch):
    """Test authenticated API request using environment injection."""
    # Inject test key via environment (not hardcoded in source)
    monkeypatch.setenv("MCP_API_KEY", "test-key-12345")
    
    # Test reads the injected key from environment
    from src.mcp.config import get_api_key
    api_key = get_api_key()
    
    response = client.post(
        "/mcp/v1/query",
        headers={"X-MCP-API-Key": api_key},
        json={"query": "test"}
    )
    assert response.status_code == 200
```

**Key principle:** Test keys come from environment variables or fixtures, never hardcoded in test source files.

## Deployment

### Docker

Use build arguments or environment variable injection:

```dockerfile
# ❌ WRONG: Hardcoding in Dockerfile
ENV MCP_API_KEY="sk-xxx"

# ✅ CORRECT: Pass at runtime
FROM python:3.11
COPY . /app
WORKDIR /app
# API key provided at runtime via -e or docker-compose env_file
CMD ["python", "-m", "mcp.server.http"]
```

```bash
# Run container with API key
docker run \
  -e MCP_API_KEY="$PRODUCTION_API_KEY" \
  codex-mcp-server
```

### Kubernetes

Use Secrets:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mcp-server
spec:
  containers:
  - name: server
    image: codex-mcp-server:latest
    env:
    - name: MCP_API_KEY
      valueFrom:
        secretKeyRef:
          name: mcp-credentials
          key: api-key
```

### GitHub Actions

Never commit secrets — use repository secrets:

```yaml
# ✅ CORRECT: Use repository secrets
- name: Test MCP Server
  env:
    MCP_API_KEY: ${{ secrets.MCP_TEST_API_KEY }}
  run: pytest tests/mcp/test_http_server.py

# ❌ WRONG: Never hardcode
# env:
#   MCP_API_KEY: "sk-xxx"
```

## Remediation History

| Date | Issue | Fix | Authority |
|------|-------|-----|-----------|
| 2026-07-08 | Hardcoded `DEFAULT_API_KEY = "dev-key"` | Removed; now required via `MCP_API_KEY` env var | Phase 14 WS1 (@mbaetiong) |
| 2026-07-08 | Hardcoded `"dev-key-1"` in auth middleware | Moved to `DEV_API_KEY` env var loading function | Phase 14 WS1 (@mbaetiong) |

## References

- **OWASP**: [A02:2021 - Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- **CWE-798**: [Use of Hard-Coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
- **GitHub**: [Secrets Detection](https://docs.github.com/en/code-security/secret-scanning)

## Questions?

For questions about secure configuration, contact:
- **Security Team**: security@github.com
- **Codex Team**: codex-team@github.com
