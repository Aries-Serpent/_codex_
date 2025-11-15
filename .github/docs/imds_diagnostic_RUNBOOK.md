# IMDS Diagnostic Runbook

## Overview

This runbook provides comprehensive guidance for using the IMDS (Instance Metadata Service) diagnostic tools to troubleshoot connectivity issues with Azure's Instance Metadata Service on Azure VMs.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Running Diagnostics](#running-diagnostics)
4. [Understanding Results](#understanding-results)
5. [Common Issues](#common-issues)
6. [Troubleshooting Steps](#troubleshooting-steps)
7. [Advanced Usage](#advanced-usage)
8. [Support](#support)

## Quick Start

### Basic Diagnostic Run

```bash
# Make script executable
chmod +x .github/scripts/imds_diagnostic.sh

# Run diagnostic
./.github/scripts/imds_diagnostic.sh

# Run with verbose output
./.github/scripts/imds_diagnostic.sh --verbose

# Save results to file
./.github/scripts/imds_diagnostic.sh --output results.json
```

### In CI/CD Pipeline

```yaml
- name: Run IMDS Diagnostic
  uses: ./.github/actions/imds-check
  with:
    verbose: true
    timeout: 10
```

## Prerequisites

### Required Dependencies

- `curl` - For making HTTP requests to IMDS
- `jq` - For JSON parsing and formatting
- `ping` - For network connectivity tests
- `timeout` - For enforcing request timeouts
- `bash` 4.0+ - For running the diagnostic script

### Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y curl jq iputils-ping coreutils
```

**RHEL/CentOS:**
```bash
sudo yum install -y curl jq iputils coreutils
```

**Alpine:**
```bash
apk add --no-cache curl jq iputils bash coreutils
```

### Permissions

Most checks don't require elevated privileges, but firewall detection may need sudo:

```bash
# For full diagnostics including firewall checks
sudo ./.github/scripts/imds_diagnostic.sh
```

## Running Diagnostics

### Command Line Options

```
Usage: imds_diagnostic.sh [OPTIONS]

OPTIONS:
    -v, --verbose           Enable verbose output
    -o, --output FILE       Output results to specified JSON file
    -q, --quiet             Suppress non-error output
    -h, --help              Display help message
    --timeout SECONDS       Set timeout for IMDS requests (default: 5)
    --skip-firewall         Skip firewall detection tests
    --skip-dns              Skip DNS resolution tests
```

### Environment Variables

```bash
# Override IMDS endpoint (default: 169.254.169.254)
export IMDS_ENDPOINT="169.254.169.254"

# Override API version (default: 2021-02-01)
export IMDS_API_VERSION="2021-02-01"

# Set default timeout (default: 5 seconds)
export IMDS_TIMEOUT="10"
```

### Examples

**Standard diagnostic:**
```bash
./.github/scripts/imds_diagnostic.sh --output /tmp/imds_check.json
```

**Quick check with higher timeout:**
```bash
./.github/scripts/imds_diagnostic.sh --timeout 15 --quiet
```

**Skip optional tests:**
```bash
./.github/scripts/imds_diagnostic.sh --skip-firewall --skip-dns
```

**Verbose debugging:**
```bash
./.github/scripts/imds_diagnostic.sh --verbose 2>&1 | tee debug.log
```

## Understanding Results

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | IMDS accessible and working correctly |
| `1` | IMDS inaccessible or errors detected |
| `2` | Invalid arguments or configuration |
| `3` | Missing required dependencies |

### JSON Output Structure

```json
{
  "version": "1.6.0",
  "timestamp": "2024-01-15T12:00:00Z",
  "hostname": "vm-hostname",
  "imds_accessible": "true",
  "imds_http_code": "200",
  "vm_id": "12345678-1234-1234-1234-123456789abc",
  "azure_location": "eastus",
  "network_ping": "success",
  "dns_check": "expected",
  "firewall_check": "passed",
  "firewall_iptables": "none",
  "firewall_nftables": "none",
  "attested_data_accessible": "true",
  "summary_total_tests": "8",
  "summary_passed": "7",
  "summary_failed": "0",
  "summary_warnings": "1",
  "exit_code": "0"
}
```

### Key Fields

- **imds_accessible**: Primary indicator of IMDS availability
- **imds_http_code**: HTTP status code from IMDS request
- **vm_id**: Unique identifier for the Azure VM
- **azure_location**: Azure region where VM is located
- **error_reason**: Specific error if IMDS is inaccessible
- **firewall_check**: Results of firewall detection

## Common Issues

### Issue 1: IMDS Not Accessible (Connection Failed)

**Symptoms:**
```json
{
  "imds_accessible": "false",
  "error_reason": "connection_failed",
  "imds_curl_exit": "7"
}
```

**Possible Causes:**
1. Not running on an Azure VM
2. Firewall blocking 169.254.169.254
3. Network configuration issues
4. IMDS disabled on VM

**Resolution:**
1. Verify you're on an Azure VM: `dmidecode -s system-manufacturer` (should show "Microsoft Corporation")
2. Check firewall rules: `sudo iptables -L -n | grep 169.254.169.254`
3. Test connectivity: `curl -H "Metadata: true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"`

### Issue 2: Timeout

**Symptoms:**
```json
{
  "imds_accessible": "false",
  "error_reason": "timeout",
  "imds_curl_exit": "28"
}
```

**Possible Causes:**
1. Network latency
2. IMDS service slowness
3. Timeout too short

**Resolution:**
```bash
# Increase timeout
./.github/scripts/imds_diagnostic.sh --timeout 30
```

### Issue 3: Firewall Rules Detected

**Symptoms:**
```json
{
  "firewall_check": "warning",
  "firewall_iptables": "detected"
}
```

**Possible Causes:**
- Custom firewall rules blocking IMDS

**Resolution:**
```bash
# Check specific rules
sudo iptables -L OUTPUT -n -v | grep 169.254.169.254

# Temporarily disable (for testing only)
sudo iptables -D OUTPUT -d 169.254.169.254 -j REJECT
```

### Issue 4: Missing Dependencies

**Symptoms:**
```json
{
  "dependency_check": "failed",
  "missing_dependencies": "jq curl"
}
```

**Resolution:**
```bash
# Install missing dependencies
sudo apt-get update && sudo apt-get install -y curl jq iputils-ping
```

## Troubleshooting Steps

### Step 1: Verify Azure VM

```bash
# Check if running on Azure
sudo dmidecode -s system-manufacturer
# Should output: Microsoft Corporation

# Check VM metadata (manual test)
curl -H "Metadata: true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01" | jq '.'
```

### Step 2: Check Network Connectivity

```bash
# Test ping to IMDS (may not work but worth checking)
ping -c 3 169.254.169.254

# Test TCP connectivity
nc -zv 169.254.169.254 80

# Check routing
ip route get 169.254.169.254
```

### Step 3: Examine Firewall Rules

```bash
# Check iptables
sudo iptables -L -n -v | grep 169.254.169.254

# Check nftables
sudo nft list ruleset | grep 169.254.169.254

# Check ufw status
sudo ufw status verbose
```

### Step 4: Test IMDS Manually

```bash
# Instance metadata
curl -H "Metadata: true" \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01"

# Attested data
curl -H "Metadata: true" \
  "http://169.254.169.254/metadata/attested/document?api-version=2021-02-01"

# Scheduled events
curl -H "Metadata: true" \
  "http://169.254.169.254/metadata/scheduledevents?api-version=2019-08-01"
```

### Step 5: Review System Logs

```bash
# Check for network errors
sudo dmesg | grep -i network

# Check systemd journal
sudo journalctl -u walinuxagent -n 50

# Check Azure agent logs
sudo cat /var/log/waagent.log | tail -n 50
```

## Advanced Usage

### Batch Diagnostics

Run diagnostics on multiple hosts and aggregate:

```bash
# Run on multiple hosts
for host in host1 host2 host3; do
  ssh $host '.github/scripts/imds_diagnostic.sh --output /tmp/imds_$host.json'
  scp $host:/tmp/imds_$host.json ./results/
done

# Aggregate results
./.github/scripts/imds_aggregate_json.sh ./results/ aggregate_report.json
```

### Continuous Monitoring

```bash
# Run periodic checks
while true; do
  ./.github/scripts/imds_diagnostic.sh --output /var/log/imds/check_$(date +%s).json --quiet
  sleep 300  # Every 5 minutes
done
```

### Custom Scripts

Integrate into your own scripts:

```bash
#!/bin/bash
result=$(./.github/scripts/imds_diagnostic.sh --quiet --output /tmp/check.json)
exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo "IMDS is accessible"
  vm_id=$(jq -r '.vm_id' /tmp/check.json)
  echo "VM ID: $vm_id"
else
  echo "IMDS is NOT accessible"
  error=$(jq -r '.error_reason' /tmp/check.json)
  echo "Error: $error"
  # Send alert, log, etc.
fi
```

## Support

### Getting Help

1. **Documentation**: Review all IMDS documentation in `.github/docs/`
2. **Issues**: Open an issue with the `imds` label
3. **Logs**: Include full verbose output when reporting issues

### Reporting Issues

When reporting IMDS issues, include:

```bash
# Generate comprehensive diagnostic report
./.github/scripts/imds_diagnostic.sh --verbose --output diagnostic_report.json 2>&1 | tee diagnostic.log

# Include system information
uname -a > system_info.txt
cat /etc/os-release >> system_info.txt
```

### Related Documentation

- [Configuration Guide](imds_config_GUIDE.md)
- [Error Reason Codes](imds_error_REASON_CODES.md)
- [Firewall Detectors](imds_firewall_DETECTORS.md)
- [JSON Schema](IMDS_JSON_SCHEMA.md)
- [CI Integration Guide](imds_ci_INTEGRATION_GUIDE.md)

## References

- [Azure IMDS Documentation](https://docs.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service)
- [IMDS REST API Reference](https://docs.microsoft.com/en-us/rest/api/imds/)
- [Troubleshooting Azure VM connectivity](https://docs.microsoft.com/en-us/azure/virtual-machines/troubleshooting/)

---

**Version:** 1.6.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
