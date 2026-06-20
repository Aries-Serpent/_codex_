# Registry Connectivity Test Guide

**Version:** 1.0.0  
**Last Updated:** 2026-06-20  
**Status:** Active

---

## Overview

This guide documents the registry connectivity testing process and provides instructions for validating registry connectivity and authentication for all supported registry types.

---

## Supported Registries

1. **DockerHub** - Public container registry
2. **GitHub Container Registry (GHCR)** - GitHub's native registry
3. **Private Docker Registry** - Self-hosted registries
4. **Amazon ECR** - AWS container registry
5. **Google Container Registry (GCR)** - Google Cloud registry

---

## Connectivity Test Types

### Test 1: DNS Resolution

**Purpose:** Verify that the registry endpoint is resolvable via DNS  
**Severity:** Critical  
**Timeout:** 5 seconds

**What it tests:**
- Endpoint hostname can be resolved to IP address
- DNS server connectivity working
- Endpoint name is correct and valid

**Passes when:**
- Hostname resolves to valid IP address
- Resolution completes within 100ms
- No DNS timeout or NXDOMAIN errors

**Fails when:**
- Hostname cannot be resolved
- DNS timeout
- "Hostname not found" error

**Remediation:**
1. Verify endpoint URL spelling
2. Check DNS configuration: `nslookup <endpoint>`
3. Try alternate DNS servers (8.8.8.8, 1.1.1.1)
4. Check network connectivity to internet

---

### Test 2: Endpoint Availability

**Purpose:** Verify that the registry endpoint is accessible and responding  
**Severity:** Critical  
**Timeout:** 5 seconds

**What it tests:**
- Endpoint accepts HTTPS connections
- Port 443 (HTTPS) is open and listening
- Endpoint is responding to network requests
- Network firewall allows connections

**Passes when:**
- TCP connection to port 443 succeeds
- Response received within 500ms
- No connection refused errors

**Fails when:**
- Connection refused (port not open)
- Connection timeout (no response)
- Firewall blocking connections
- Endpoint offline

**Remediation:**
1. Check endpoint is online: `curl -I https://<endpoint>`
2. Verify firewall allows HTTPS: `telnet <endpoint> 443`
3. Check network routing: `traceroute <endpoint>`
4. Contact registry provider if endpoint unavailable

---

### Test 3: Authentication

**Purpose:** Verify that credentials work with the registry  
**Severity:** Critical

**What it tests:**
- Credentials are provided in configuration
- Authentication method matches registry type
- Credentials can authenticate successfully
- Token/password is valid and not expired

**Authentication Methods:**
- **DockerHub:** username + password
- **GHCR:** GitHub token + username
- **Private Registry:** HTTP Basic or OAuth2
- **ECR:** IAM role or access key
- **GCR:** Service account key

**Passes when:**
- Credentials provided and non-empty
- Authentication method matches registry type
- Credentials validate successfully
- Token not expired

**Fails when:**
- No credentials provided
- Credentials do not match registry type
- Invalid or expired credentials
- Authentication server unreachable

**Remediation:**
1. Provide credentials: `export REGISTRY_USERNAME=...`
2. Verify credentials stored in GitHub Secrets
3. Check credentials are not expired
4. Regenerate/rotate credentials if needed
5. Verify authentication method matches registry type

---

### Test 4: Image Pull Permission

**Purpose:** Verify that registry credentials allow pulling images  
**Severity:** High

**What it tests:**
- Credentials have read permission
- Specified namespace is accessible
- Image pull operations allowed
- Pull rate limits not exceeded

**Passes when:**
- Namespace exists and is accessible
- Test image can be pulled successfully
- Pull completes within 5 seconds
- No permission denied errors

**Fails when:**
- Namespace does not exist
- Access denied for namespace
- Pull rate limit exceeded
- Test image not found

**Remediation:**
1. Verify namespace exists and is correct
2. Check credentials have read permissions
3. Verify image name and tag are correct
4. Check rate limits and retry if needed
5. Contact registry admin if access denied

---

### Test 5: Image Push Permission

**Purpose:** Verify that registry credentials allow pushing images  
**Severity:** High

**What it tests:**
- Credentials have write permission
- Namespace is accessible for writes
- Image push operations allowed
- Push rate limits not exceeded

**Push Considerations by Registry:**
- **DockerHub:** Rate limited (10 pushes/day for free tier)
- **GHCR:** No per-minute limit; daily limit applies
- **Private:** Depends on storage backend capacity
- **ECR:** Per-region and per-account quotas apply
- **GCR:** Regional storage quotas apply

**Passes when:**
- Namespace is writable
- Push permission verified
- Test push succeeds
- No quota errors

**Fails when:**
- Namespace not writable
- Access denied for writes
- Storage quota exceeded
- Rate limit exceeded

**Remediation:**
1. Verify credentials have write permissions
2. Check push rate limits and quota
3. Review storage backend capacity
4. Upgrade account tier if needed
5. Contact registry admin for quota increases

---

## Running Connectivity Tests

### Quick Test

```bash
# Run connectivity tests with default configuration
python scripts/registry/test_connectivity.py
```

### Test Specific Registry

```bash
# Test GHCR
python scripts/registry/test_connectivity.py --registry-type ghcr --endpoint ghcr.io

# Test DockerHub
python scripts/registry/test_connectivity.py --registry-type dockerhub --endpoint docker.io

# Test ECR
python scripts/registry/test_connectivity.py --registry-type ecr --endpoint 123456789.dkr.ecr.us-east-1.amazonaws.com

# Test private registry
python scripts/registry/test_connectivity.py --registry-type private --endpoint registry.company.internal
```

### With Credentials

```bash
# Test with credentials
python scripts/registry/test_connectivity.py \
  --registry-type ghcr \
  --endpoint ghcr.io \
  --username octocat \
  --token $GITHUB_TOKEN \
  --namespace myorg/myimage
```

### Generate Report

```bash
# Save test results to file
python scripts/registry/test_connectivity.py --output registry_connectivity_report.json
```

---

## Test Results Interpretation

### Overall Status

| Status | Meaning | Action |
|--------|---------|--------|
| `passed` | All 5 tests passed | Registry ready for use ✅ |
| `failed` | One or more tests failed | See detailed results; fix issues |

### Test Status

- **✅ passed:** Test succeeded; no action needed
- **❌ failed:** Test failed; review remediation steps
- **⚠️ warning:** Test passed with warnings; review details

### Success Rate

- **100%:** Perfect - no issues
- **80-99%:** Good - minor issues to address
- **60-79%:** Fair - multiple issues found
- **<60%:** Poor - significant problems; cannot use registry

---

## Sample Test Report

```json
{
  "timestamp": "2026-06-20T09:35:04Z",
  "tester_version": "1.0.0",
  "test_results": {
    "registry_type": "ghcr",
    "endpoint": "ghcr.io",
    "overall_status": "passed",
    "summary": {
      "total_tests": 5,
      "passed": 5,
      "failed": 0,
      "success_rate": "100.0%"
    },
    "tests": {
      "dns_resolution": {
        "passed": true,
        "hostname": "ghcr.io",
        "resolved_ip": "140.82.112.34"
      },
      "endpoint_availability": {
        "passed": true,
        "endpoint": "ghcr.io",
        "protocol": "HTTPS"
      },
      "authentication": {
        "passed": true,
        "method": "github_token",
        "status": "authenticated"
      },
      "image_pull_permission": {
        "passed": true,
        "namespace": "org/imagename",
        "status": "pull_allowed"
      },
      "image_push_permission": {
        "passed": true,
        "namespace": "org/imagename",
        "status": "push_allowed"
      }
    }
  }
}
```

---

## Troubleshooting

### DNS Resolution Fails

```bash
# Test DNS
nslookup ghcr.io
dig ghcr.io

# Check DNS servers
cat /etc/resolv.conf

# Try alternate DNS
nslookup ghcr.io 8.8.8.8
```

### Endpoint Not Available

```bash
# Test connectivity
curl -I https://ghcr.io
ping ghcr.io
telnet ghcr.io 443

# Check routing
traceroute ghcr.io
mtr ghcr.io
```

### Authentication Fails

```bash
# Verify credentials
echo $GITHUB_TOKEN
echo $REGISTRY_USERNAME

# Test Docker login
docker login ghcr.io

# Check credentials file
cat ~/.docker/config.json
```

### Permission Denied

```bash
# Check namespace exists
docker search org/imagename

# List accessible images
docker images

# Check account permissions
# (Registry-specific command)
```

---

## Best Practices

### Before Running Tests
1. ✅ Ensure registry endpoint is correct
2. ✅ Verify credentials are valid and current
3. ✅ Check network connectivity to internet
4. ✅ Confirm firewall allows HTTPS (port 443)

### During Tests
1. ✅ Monitor test output for errors
2. ✅ Note any warnings or issues
3. ✅ Save test results for documentation
4. ✅ Check recommendations provided

### After Tests
1. ✅ Review all failed tests
2. ✅ Apply recommended fixes
3. ✅ Re-run tests to verify fixes
4. ✅ Document any configuration changes

---

## Integration with Other Tasks

### Task 4.2 (Validation Script)
- Connectivity tests validate configuration endpoint
- Uses credentials from validation script
- Complements validation confidence scoring

### Task 4.4 (Workflow Template)
- Workflow calls connectivity tests after validation
- Uses test results in approval gate logic
- Determines if registry is ready for deployment

### Task 4.5 (Webhook Integration)
- Reports connectivity test results to Cognitive Brain
- Tracks test trends over time
- Enables infrastructure monitoring

---

## Performance Benchmarks

| Test | Expected Duration | Acceptable Range |
|------|-------------------|------------------|
| DNS Resolution | 50-100ms | <500ms |
| Endpoint Availability | 200-500ms | <1000ms |
| Authentication | 100-300ms | <1000ms |
| Image Pull Permission | 500-2000ms | <5000ms |
| Image Push Permission | 1000-5000ms | <10000ms |
| **Total** | **2-8 seconds** | **<15 seconds** |

---

## Security Considerations

### Credential Handling
- ✅ Never log credentials
- ✅ Use GitHub Secrets for storage
- ✅ Rotate credentials periodically
- ✅ Revoke unused tokens immediately

### Test Safety
- ✅ Tests use read-only operations when possible
- ✅ Test images are temporary
- ✅ No permanent changes made
- ✅ Connectivity only; no container execution

### Network Safety
- ✅ HTTPS only (port 443)
- ✅ No proxy bypass
- ✅ Standard DNS resolution
- ✅ Firewall rules respected

---

## Maintenance & Updates

**Last Updated:** 2026-06-20T09:35:04Z  
**Review Frequency:** Quarterly  
**Next Review:** 2026-09-20

**Maintainer:** Cognitive Brain Registry Team  
**Escalation:** @mbaetiong
