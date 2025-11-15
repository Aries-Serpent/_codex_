# IMDS Error Reason Codes

## Overview

This document catalogs all error reason codes that can be returned by the IMDS diagnostic tool, along with their meanings, causes, and recommended remediation steps.

## Error Code Format

Error reasons are returned in the `error_reason` field of the JSON output:

```json
{
  "error_reason": "connection_failed",
  "imds_accessible": "false",
  "imds_curl_exit": "7"
}
```

## Error Codes

### Network Errors

#### `connection_failed`
- **curl Exit Code:** 7
- **HTTP Code:** N/A
- **Meaning:** Failed to connect to IMDS endpoint
- **Common Causes:**
  - Not running on an Azure VM
  - Firewall blocking 169.254.169.254
  - Network interface down
  - Routing issues
- **Remediation:**
  1. Verify running on Azure VM: `dmidecode -s system-manufacturer`
  2. Check firewall rules: `sudo iptables -L -n | grep 169.254.169.254`
  3. Test connectivity: `ping -c 3 169.254.169.254`
  4. Check routing: `ip route get 169.254.169.254`

#### `timeout`
- **curl Exit Code:** 28
- **HTTP Code:** N/A
- **Meaning:** Request timed out
- **Common Causes:**
  - Network latency
  - IMDS service overloaded
  - Timeout setting too short
  - Network congestion
- **Remediation:**
  1. Increase timeout: `--timeout 30`
  2. Check network latency: `ping -c 10 169.254.169.254`
  3. Retry with longer timeout
  4. Check for network congestion

#### `dns_resolution`
- **curl Exit Code:** 6
- **HTTP Code:** N/A
- **Meaning:** Could not resolve hostname
- **Common Causes:**
  - DNS misconfiguration
  - Using hostname instead of IP
  - DNS server issues
- **Remediation:**
  1. Verify using IP address (169.254.169.254)
  2. Check DNS configuration: `cat /etc/resolv.conf`
  3. Test DNS: `nslookup 169.254.169.254`

---

### HTTP Errors

#### `http_400_bad_request`
- **curl Exit Code:** 0
- **HTTP Code:** 400
- **Meaning:** Bad request to IMDS
- **Common Causes:**
  - Missing `Metadata: true` header
  - Invalid API version
  - Malformed request
- **Remediation:**
  1. Ensure `Metadata: true` header is set
  2. Verify API version is valid
  3. Check request format

#### `http_401_unauthorized`
- **curl Exit Code:** 0
- **HTTP Code:** 401
- **Meaning:** Unauthorized request
- **Common Causes:**
  - Missing authentication (shouldn't happen with IMDS)
  - Invalid credentials
- **Remediation:**
  1. Verify `Metadata: true` header
  2. Check for proxy authentication issues

#### `http_403_forbidden`
- **curl Exit Code:** 0
- **HTTP Code:** 403
- **Meaning:** Access forbidden
- **Common Causes:**
  - IMDS disabled on VM
  - Policy restriction
  - Regional restriction
- **Remediation:**
  1. Check VM configuration in Azure Portal
  2. Verify IMDS is enabled
  3. Check Azure policies

#### `http_404_not_found`
- **curl Exit Code:** 0
- **HTTP Code:** 404
- **Meaning:** Endpoint not found
- **Common Causes:**
  - Invalid API endpoint
  - Wrong API version
  - Unsupported endpoint
- **Remediation:**
  1. Verify endpoint URL
  2. Check API version compatibility
  3. Review Azure IMDS documentation

#### `http_429_too_many_requests`
- **curl Exit Code:** 0
- **HTTP Code:** 429
- **Meaning:** Rate limit exceeded
- **Common Causes:**
  - Too many requests to IMDS
  - Rate limiting active
  - Script running in tight loop
- **Remediation:**
  1. Implement exponential backoff
  2. Add delays between requests
  3. Reduce request frequency
  4. Check for script loops

#### `http_500_internal_error`
- **curl Exit Code:** 0
- **HTTP Code:** 500
- **Meaning:** IMDS internal server error
- **Common Causes:**
  - IMDS service issue
  - Azure infrastructure problem
  - Temporary service disruption
- **Remediation:**
  1. Retry after brief delay
  2. Check Azure service health
  3. Contact Azure support if persists

#### `http_503_service_unavailable`
- **curl Exit Code:** 0
- **HTTP Code:** 503
- **Meaning:** IMDS service unavailable
- **Common Causes:**
  - IMDS service down
  - Maintenance window
  - Service overload
- **Remediation:**
  1. Retry after delay
  2. Check Azure service status
  3. Implement retry logic with backoff
  4. Contact Azure support

---

### Configuration Errors

#### `invalid_endpoint`
- **curl Exit Code:** 6 or 7
- **HTTP Code:** N/A
- **Meaning:** Invalid IMDS endpoint configured
- **Common Causes:**
  - Wrong IP address
  - Typo in configuration
  - Environment variable override
- **Remediation:**
  1. Verify endpoint is 169.254.169.254
  2. Check environment variables: `echo $IMDS_ENDPOINT`
  3. Review configuration file

#### `invalid_api_version`
- **curl Exit Code:** 0
- **HTTP Code:** 400
- **Meaning:** Unsupported API version
- **Common Causes:**
  - Old/deprecated API version
  - Future API version
  - Typo in version string
- **Remediation:**
  1. Use supported version (2021-02-01 recommended)
  2. Check Azure IMDS documentation for supported versions
  3. Update configuration

---

### Dependency Errors

#### `missing_curl`
- **curl Exit Code:** N/A
- **HTTP Code:** N/A
- **Meaning:** curl command not found
- **Common Causes:**
  - curl not installed
  - Not in PATH
- **Remediation:**
  1. Install curl: `sudo apt-get install curl`
  2. Verify installation: `which curl`

#### `missing_jq`
- **curl Exit Code:** N/A
- **HTTP Code:** N/A
- **Meaning:** jq command not found
- **Common Causes:**
  - jq not installed
  - Not in PATH
- **Remediation:**
  1. Install jq: `sudo apt-get install jq`
  2. Verify installation: `which jq`

#### `missing_dependencies`
- **curl Exit Code:** N/A
- **HTTP Code:** N/A
- **Meaning:** Multiple dependencies missing
- **Common Causes:**
  - Fresh system installation
  - Minimal container image
- **Remediation:**
  1. Install all dependencies:
     ```bash
     sudo apt-get update
     sudo apt-get install -y curl jq iputils-ping coreutils
     ```

---

### Firewall Errors

#### `firewall_blocking`
- **curl Exit Code:** 7
- **HTTP Code:** N/A
- **Meaning:** Firewall rules blocking IMDS
- **Common Causes:**
  - iptables DROP/REJECT rules
  - nftables blocking rules
  - ufw deny rules
  - firewalld blocking
- **Remediation:**
  1. Check firewall rules: `sudo iptables -L -n`
  2. Allow IMDS: `sudo iptables -I OUTPUT -d 169.254.169.254 -j ACCEPT`
  3. Make persistent (depends on system)

#### `firewall_permission_denied`
- **curl Exit Code:** N/A
- **HTTP Code:** N/A
- **Meaning:** Cannot check firewall (no sudo)
- **Common Causes:**
  - No sudo privileges
  - Sudo password required
- **Remediation:**
  1. Run with sudo: `sudo ./.github/scripts/imds_diagnostic.sh`
  2. Or skip firewall checks: `--skip-firewall`

---

### Curl-Specific Errors

#### `curl_error_1`
- **Meaning:** Unsupported protocol
- **Remediation:** Verify URL uses http://

#### `curl_error_3`
- **Meaning:** URL malformed
- **Remediation:** Check endpoint URL format

#### `curl_error_5`
- **Meaning:** Couldn't resolve proxy
- **Remediation:** Check proxy settings

#### `curl_error_23`
- **Meaning:** Failed writing received data
- **Remediation:** Check disk space and permissions

#### `curl_error_26`
- **Meaning:** Failed reading data
- **Remediation:** Check source file permissions

#### `curl_error_35`
- **Meaning:** SSL connection error
- **Remediation:** IMDS uses HTTP, not HTTPS - verify URL

#### `curl_error_52`
- **Meaning:** Empty reply from server
- **Remediation:** IMDS returned empty response, retry

#### `curl_error_56`
- **Meaning:** Failure in receiving network data
- **Remediation:** Check network connectivity

---

## Error Recovery Strategies

### Retry Logic

```bash
# Exponential backoff example
attempt=1
max_attempts=5
delay=1

while [ $attempt -le $max_attempts ]; do
  if ./.github/scripts/imds_diagnostic.sh --output result.json; then
    echo "Success on attempt $attempt"
    break
  fi
  
  if [ $attempt -lt $max_attempts ]; then
    echo "Attempt $attempt failed, retrying in ${delay}s..."
    sleep $delay
    delay=$((delay * 2))  # Exponential backoff
  fi
  
  attempt=$((attempt + 1))
done
```

### Fallback Strategies

```bash
# Try with increased timeout
./.github/scripts/imds_diagnostic.sh --timeout 30 || \
  # Skip optional tests if still failing
  ./.github/scripts/imds_diagnostic.sh --skip-firewall --skip-dns || \
  # Last resort: basic connectivity test
  curl -H "Metadata: true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

## Debugging

### Verbose Mode

Enable verbose output to see detailed error information:

```bash
./.github/scripts/imds_diagnostic.sh --verbose 2>&1 | tee debug.log
```

### Manual Testing

Test IMDS manually to isolate issues:

```bash
# Basic test
curl -v -H "Metadata: true" \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01"

# With timeout
timeout 5 curl -v -H "Metadata: true" \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01"

# Save response headers
curl -v -H "Metadata: true" \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01" \
  -o response.json -D headers.txt 2>&1
```

## Related Documentation

- [IMDS Diagnostic Runbook](imds_diagnostic_RUNBOOK.md)
- [Configuration Guide](imds_config_GUIDE.md)
- [Firewall Detectors](imds_firewall_DETECTORS.md)
- [JSON Schema](IMDS_JSON_SCHEMA.md)

## References

- [curl error codes](https://curl.se/libcurl/c/libcurl-errors.html)
- [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Azure IMDS documentation](https://docs.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service)

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
