# CORS Configuration Guide

**Document Version**: 1.0  
**Last Updated**: 2026-01-13  
**Status**: Active

## Overview

This document describes the Cross-Origin Resource Sharing (CORS) configuration for the Codex services. Proper CORS configuration is critical for security, preventing unauthorized access while maintaining legitimate functionality.

## Security Context

**Previously**: Services used wildcard CORS (`allow_origins=["*"]`) which allowed any domain to make requests.  
**Current**: Environment-aware CORS with specific origin whitelisting.  
**Remediation**: Part of PR #2827 security fixes (Phase 4, Task 4.1)

## Configuration

### Environment Variables

**CORS_ORIGINS** - Comma-separated list of allowed origins
```bash
# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Production
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

**ENVIRONMENT** - Deployment environment (`development`, `staging`, `production`)
```bash
ENVIRONMENT=development
```

### Default Behavior

If `CORS_ORIGINS` is not set, the configuration defaults based on `ENVIRONMENT`:

| Environment | Default CORS Origins |
|-------------|---------------------|
| `development` | `http://localhost:3000`, `http://localhost:8080`, `http://127.0.0.1:3000`, `http://127.0.0.1:8080` |
| `staging` | No defaults - must explicitly set |
| `production` | Restricted domains (configured per deployment) |

## Implementation

### Services Configured

1. **Internal Tools API (ITA)**  
   File: `services/ita/app/main.py`  
   Binding: `127.0.0.1` (localhost only)

2. **MSP Gateway**  
   File: `services/msp_gateway/app.py`  
   Binding: `127.0.0.1` (localhost only)

### Code Pattern

```python
import os
from fastapi.middleware.cors import CORSMiddleware

# Environment-aware CORS configuration
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    # Use explicit CORS_ORIGINS from environment
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
elif os.getenv("ENVIRONMENT", "development") == "production":
    # Production: Restrict to specific domains
    cors_origins = [
        "https://yourdomain.com",
        "https://api.yourdomain.com"
    ]
else:
    # Development: Allow localhost only
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,  # Disable for security
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-Id"],
)
```

## Security Best Practices

### ✅ DO

1. **Use specific origins** - Always list explicit allowed domains
2. **Use HTTPS in production** - Never allow HTTP origins in production
3. **Disable credentials** - Set `allow_credentials=False` unless absolutely necessary
4. **Restrict methods** - Only allow needed HTTP methods
5. **Restrict headers** - Explicitly list allowed headers
6. **Test configuration** - Verify CORS works before deploying

### ❌ DON'T

1. **Don't use wildcards** - Never use `["*"]` for `allow_origins`
2. **Don't enable credentials with wildcards** - This is a critical security issue
3. **Don't allow all methods** - Avoid `["*"]` for `allow_methods`
4. **Don't hardcode domains** - Use environment variables for flexibility
5. **Don't expose internal services** - Keep services on localhost when possible

## Testing

### Local Development

```bash
# Start service
export CORS_ORIGINS="http://localhost:3000"
uvicorn services.ita.app.main:app --reload

# Test CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/endpoint

# Should see:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE
```

### Production Testing

```bash
# Valid origin (should work)
curl -H "Origin: https://yourdomain.com" \
     -i https://api.yourdomain.com/health

# Invalid origin (should fail)
curl -H "Origin: https://malicious.com" \
     -i https://api.yourdomain.com/health
```

## Deployment

### Docker

```dockerfile
# Dockerfile
ENV ENVIRONMENT=production
ENV CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Kubernetes

```yaml
# deployment.yaml
env:
  - name: ENVIRONMENT
    value: "production"
  - name: CORS_ORIGINS
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: cors_origins
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - ENVIRONMENT=production
      - CORS_ORIGINS=https://yourdomain.com
```

## Troubleshooting

### CORS Errors in Browser

**Symptom**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solutions**:
1. Check `CORS_ORIGINS` includes the requesting origin
2. Verify service is running
3. Check browser console for exact error
4. Inspect response headers

### Testing CORS Configuration

```python
# Test script
import requests

response = requests.options(
    'http://localhost:8000/api/endpoint',
    headers={
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST'
    }
)

print('Allow-Origin:', response.headers.get('Access-Control-Allow-Origin'))
print('Allow-Methods:', response.headers.get('Access-Control-Allow-Methods'))
```

### Verify Configuration

```bash
# Check current CORS origins
python -c "
import os
import sys
sys.path.insert(0, 'services/ita/app')
from main import app

# Find CORS middleware
for middleware in app.user_middleware:
    if 'CORS' in str(middleware):
        print('CORS Middleware Found')
        # Inspect middleware options
        print(middleware)
"
```

## Security Considerations

### Localhost Binding

Both services bind to `127.0.0.1` (localhost only), providing defense-in-depth:
- **Network isolation**: Not accessible from external network
- **Local-only access**: Only processes on same machine can connect
- **CORS as additional layer**: Even localhost requests must be from allowed origins

### Attack Vectors Mitigated

1. **Cross-Site Request Forgery (CSRF)** - CORS prevents unauthorized domains from making requests
2. **Data exfiltration** - Malicious sites cannot read responses
3. **Unauthorized API access** - Only whitelisted origins can interact with API

### Residual Risks

- **Localhost compromises**: If attacker has local access, CORS doesn't help
- **Misconfiguration**: Wrong environment variables can allow unintended origins
- **DNS hijacking**: Attacker controlling DNS for allowed domain can bypass CORS

## Compliance

This CORS configuration supports:
- **OWASP Top 10** - Addresses A01:2021 Broken Access Control
- **CWE-942** - Overly Permissive Cross-domain Whitelist
- **NIST 800-53** - AC-4 Information Flow Enforcement

## Monitoring

### Metrics to Track

1. **CORS rejection rate** - High rate may indicate misconfiguration or attack
2. **Origin diversity** - Unexpected origins attempting access
3. **CORS-related errors** - Application logs for CORS failures

### Alerts

Set up alerts for:
- CORS configuration changes
- High rate of CORS rejections
- Origins not in whitelist attempting access

## Migration Guide

### From Wildcard to Specific Origins

1. **Identify legitimate origins**:
   ```bash
   # Analyze access logs
   grep "Origin:" logs/*.log | sort | uniq -c | sort -rn
   ```

2. **Update environment**:
   ```bash
   export CORS_ORIGINS="https://app1.com,https://app2.com"
   ```

3. **Test gradually**:
   - Enable specific origins in staging
   - Monitor for CORS errors
   - Update whitelist as needed
   - Deploy to production

4. **Remove wildcard**:
   - Verify all legitimate origins listed
   - Deploy new configuration
   - Monitor for 24-48 hours
   - Revert if issues detected

## References

- **PR #2827**: Security remediation initiative
- **OWASP CORS**: https://owasp.org/www-community/attacks/cors-OriginHeaderScrutiny
- **MDN CORS**: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- **FastAPI CORS**: https://fastapi.tiangolo.com/tutorial/cors/

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-01-13 | 1.0 | Initial CORS security configuration | Security Team |

---

**Document Owner**: Security Team (@mbaetiong)  
**Review Frequency**: Quarterly  
**Next Review**: 2026-04-13
