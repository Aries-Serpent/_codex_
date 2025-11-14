# IMDS Diagnostic Script - Runbook

## Overview

This runbook provides comprehensive documentation for the IMDS (Instance Metadata Service) diagnostic script located at `.github/scripts/imds_diagnostic.sh`.

The script diagnoses connectivity issues with cloud instance metadata services and provides optional remediation capabilities with proper approval controls.

## Table of Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Modes of Operation](#modes-of-operation)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [Approval Process](#approval-process)
- [Cloud Provider Compatibility](#cloud-provider-compatibility)
- [Exit Codes](#exit-codes)
- [Security Considerations](#security-considerations)

## Purpose

The IMDS diagnostic script helps:

- **Diagnose** IMDS connectivity issues in cloud environments (AWS, Azure, GCP)
- **Identify** network routing, firewall, or configuration problems
- **Test** specific IMDS endpoints for accessibility
- **Remediate** common IMDS issues (with explicit approval)
- **Document** diagnostic results for issue tracking

This tool is particularly useful when:
- Container or VM instances cannot access instance metadata
- Cloud-init or similar services fail to retrieve instance information
- Applications dependent on instance metadata encounter errors
- Network changes may have affected IMDS connectivity

## Prerequisites

### Required Tools

The script requires the following tools to be available:

- `bash` (version 4.0+)
- `curl` - for HTTP requests to IMDS endpoints
- `ip` - for network route diagnostics (iproute2 package)
- `timeout` - for connection timeout handling
- `sudo` - for remediation mode (optional)
- `iptables` - for firewall diagnostics (optional)
- `nslookup` or `dig` - for DNS checks (optional)

### Permissions

- **Read-only mode**: No special permissions required
- **Remediation mode**: Requires root/sudo privileges

### Network Requirements

- Instance must be in a cloud environment with IMDS support
- IMDS endpoint (default: `169.254.169.254`) must be routable
- No firewall rules blocking access to IMDS endpoint

## Usage

### Basic Diagnostic (Read-Only Mode)

Run the script without arguments for read-only diagnostics:

```bash
.github/scripts/imds_diagnostic.sh
```

This will:
- Check IMDS connectivity
- Test network routes
- Verify firewall rules
- Test common IMDS endpoints
- Generate a diagnostic report in `diagnostic_results.txt`

### Remediation Mode

**⚠️ REQUIRES APPROVAL FROM @mbaetiong**

To attempt automatic remediation:

```bash
sudo IMDS_REMEDIATE_APPROVED=true .github/scripts/imds_diagnostic.sh --apply
```

This will:
- Perform all diagnostic checks
- Attempt to fix identified issues
- Require explicit approval via environment variable
- Require root privileges

### Custom Configuration

Override default settings using environment variables:

```bash
# Custom IMDS endpoint
IMDS_ENDPOINT=169.254.169.253 .github/scripts/imds_diagnostic.sh

# Custom timeout (seconds)
IMDS_TIMEOUT=10 .github/scripts/imds_diagnostic.sh

# Custom output file
IMDS_OUTPUT_FILE=/tmp/my_diagnostics.txt .github/scripts/imds_diagnostic.sh
```

### Help

Display help information:

```bash
.github/scripts/imds_diagnostic.sh --help
```

## Modes of Operation

### 1. Read-Only Mode (Default)

**Purpose**: Safe diagnostics without making any system changes

**Behavior**:
- Tests IMDS connectivity
- Checks network routes
- Examines firewall rules
- Tests multiple IMDS endpoints
- Generates diagnostic report
- **Does NOT modify system configuration**

**When to Use**:
- Initial troubleshooting
- Regular health checks
- Issue documentation
- Pre-change validation

**Example**:
```bash
.github/scripts/imds_diagnostic.sh
```

### 2. Remediation Mode (--apply)

**Purpose**: Attempt automatic fixes for common IMDS issues

**Behavior**:
- Performs all read-only diagnostics
- Attempts to add missing routes
- Requires explicit approval
- Requires root privileges
- Verifies fixes after application

**When to Use**:
- After identifying issues in read-only mode
- With explicit approval from @mbaetiong
- When manual intervention is not feasible
- For automated recovery workflows

**Example**:
```bash
sudo IMDS_REMEDIATE_APPROVED=true .github/scripts/imds_diagnostic.sh --apply
```

## Output

### Console Output

The script provides color-coded console output:

- 🔵 **[INFO]** - Informational messages (blue)
- ✅ **[✓]** - Successful checks (green)
- ⚠️ **[WARNING]** - Warnings or non-critical issues (yellow)
- ❌ **[✗]** - Errors or failed checks (red)

### Diagnostic Results File

All output is also saved to `diagnostic_results.txt` (or custom path via `IMDS_OUTPUT_FILE`).

**Example Output Structure**:

```
IMDS Diagnostic Script
======================

[INFO] Detecting cloud provider...
[✓] Cloud provider detected (AWS-compatible IMDS)
[INFO] Checking network routes to IMDS...
[✓] Route to IMDS exists: 169.254.169.254 dev eth0 src 10.0.1.5
[INFO] Checking firewall rules...
[✓] No blocking iptables rules detected
[INFO] Checking IMDS connectivity at 169.254.169.254...
[✓] IMDS endpoint is reachable
[INFO] Testing IMDS endpoints...
[✓] Endpoint accessible: latest/meta-data/
[✓] Endpoint accessible: latest/meta-data/instance-id
[✓] Endpoint accessible: latest/meta-data/instance-type
[✓] Endpoint accessible: latest/meta-data/placement/availability-zone

========================================
DIAGNOSTIC SUMMARY
========================================
Timestamp: 2025-11-14 22:30:00 UTC
Hostname: ip-10-0-1-5
IMDS Endpoint: 169.254.169.254
Mode: Read-only

[✓] IMDS diagnostics completed successfully
```

## Troubleshooting

### Common Issues

#### Issue 1: IMDS Endpoint Not Reachable

**Symptoms**:
```
[✗] IMDS endpoint is NOT reachable
[✗] Endpoint NOT accessible: latest/meta-data/
```

**Possible Causes**:
- Missing network route to IMDS endpoint
- Firewall blocking IMDS traffic
- Running outside cloud environment
- IMDS service disabled by cloud provider

**Resolution**:
1. Verify you're running in a cloud environment
2. Check network routes: `ip route get 169.254.169.254`
3. Check firewall rules: `sudo iptables -L -n`
4. Try remediation mode with approval
5. Contact cloud provider support if issue persists

#### Issue 2: Remediation Requires Approval

**Symptoms**:
```
[✗] Remediation requires explicit approval from @mbaetiong
[INFO] Set IMDS_REMEDIATE_APPROVED=true environment variable to proceed
```

**Resolution**:
1. Contact @mbaetiong for approval
2. Once approved, set environment variable:
   ```bash
   sudo IMDS_REMEDIATE_APPROVED=true .github/scripts/imds_diagnostic.sh --apply
   ```

#### Issue 3: Permission Denied

**Symptoms**:
```
[✗] Remediation mode requires root privileges
[INFO] Please run with sudo: sudo ./imds_diagnostic.sh --apply
```

**Resolution**:
```bash
sudo IMDS_REMEDIATE_APPROVED=true .github/scripts/imds_diagnostic.sh --apply
```

#### Issue 4: Timeout Errors

**Symptoms**:
- Script takes too long to complete
- Connection timeouts reported

**Resolution**:
1. Increase timeout value:
   ```bash
   IMDS_TIMEOUT=10 .github/scripts/imds_diagnostic.sh
   ```
2. Check network connectivity
3. Verify IMDS service is running (cloud provider-specific)

### Debug Mode

For verbose debugging, run with bash debug flags:

```bash
bash -x .github/scripts/imds_diagnostic.sh
```

## Approval Process

### Why Approval is Required

Remediation mode can modify system network configuration, which requires:
- **Explicit approval** to prevent unintended changes
- **Audit trail** of who authorized the change
- **Accountability** for system modifications

### Obtaining Approval

**Step 1: Contact Approver**

Reach out to @mbaetiong via:
- GitHub issue comment on #2226
- Team communication channel
- Email

**Step 2: Provide Context**

Include the following information:
- Instance/environment details
- Diagnostic results from read-only mode
- Business justification for remediation
- Expected impact of changes

**Step 3: Receive Approval**

Once approved, you will receive:
- Explicit "approved" confirmation
- Authorization to set `IMDS_REMEDIATE_APPROVED=true`
- Timeframe for remediation window

**Step 4: Execute Remediation**

```bash
sudo IMDS_REMEDIATE_APPROVED=true .github/scripts/imds_diagnostic.sh --apply
```

**Step 5: Report Results**

After remediation:
- Attach `diagnostic_results.txt` to issue #2226
- Report success/failure to approver
- Document any manual steps taken

## Cloud Provider Compatibility

### Amazon Web Services (AWS)

**IMDS Versions**:
- IMDSv1 (legacy)
- IMDSv2 (recommended, token-based)

**Endpoint**: `http://169.254.169.254`

**Test Command**:
```bash
curl http://169.254.169.254/latest/meta-data/
```

**IMDSv2 Example**:
```bash
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
```

### Microsoft Azure

**Endpoint**: `http://169.254.169.254`

**Test Command**:
```bash
curl -H "Metadata:true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

### Google Cloud Platform (GCP)

**Endpoint**: `http://metadata.google.internal` (resolves to 169.254.169.254)

**Test Command**:
```bash
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/
```

### Other Cloud Providers

Most cloud providers implement AWS-compatible IMDS. The script auto-detects the cloud provider and adjusts accordingly.

## Exit Codes

The script uses the following exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | IMDS is healthy and all checks passed |
| `1` | Connectivity Issues | IMDS connectivity problems detected |
| `2` | Invalid Arguments/Permissions | Invalid arguments or insufficient permissions |
| `3` | Remediation Failed | Remediation attempted but failed to resolve issues |

### Usage in Scripts

```bash
#!/bin/bash

if .github/scripts/imds_diagnostic.sh; then
    echo "IMDS is healthy"
else
    exit_code=$?
    echo "IMDS issues detected (exit code: $exit_code)"
    # Handle error based on exit code
fi
```

## Security Considerations

### Read-Only Mode Security

✅ **Safe Operations**:
- Network connectivity tests
- Route inspection
- Firewall rule inspection (read-only)
- File system reads only

❌ **No System Changes**:
- No network configuration changes
- No firewall modifications
- No service restarts
- No package installations

### Remediation Mode Security

⚠️ **Privileged Operations**:
- Requires root/sudo access
- Can modify network routes
- May affect system connectivity
- Requires explicit approval

🔒 **Safety Mechanisms**:
1. **Approval Gate**: `IMDS_REMEDIATE_APPROVED` environment variable
2. **Permission Check**: Verifies root/sudo access
3. **Audit Trail**: All actions logged to output file
4. **Limited Scope**: Only performs specific, documented changes

### Best Practices

1. **Always start with read-only mode** to understand issues
2. **Obtain approval** before running remediation
3. **Test in non-production** environments first
4. **Review diagnostic output** before and after remediation
5. **Keep audit logs** of all remediation runs
6. **Limit script access** to authorized users only

## Integration with Issue #2226

### Reporting Issues

When encountering IMDS issues:

1. **Run Diagnostic**:
   ```bash
   .github/scripts/imds_diagnostic.sh
   ```

2. **Attach Results**:
   - Attach `diagnostic_results.txt` to issue #2226
   - Include instance/environment details
   - Describe symptoms and impact

3. **Tag Maintainers**:
   - @mbaetiong for remediation approval
   - Relevant team members

### Sample Commands for Issue Comments

**Read-Only Diagnostic**:
```bash
# Run diagnostics without making changes
.github/scripts/imds_diagnostic.sh

# Attach diagnostic_results.txt to this issue
```

**Remediation Mode** (with approval):
```bash
# After receiving approval from @mbaetiong
sudo IMDS_REMEDIATE_APPROVED=true .github/scripts/imds_diagnostic.sh --apply

# Attach diagnostic_results.txt to this issue
```

## Maintenance and Updates

### Script Location

- **Path**: `.github/scripts/imds_diagnostic.sh`
- **Runbook**: `.github/docs/imds_diagnostic_RUNBOOK.md`
- **Issue**: #2226

### Version History

- **v1.0** (2025-11-14): Initial implementation
  - Read-only diagnostic mode
  - Remediation mode with approval gates
  - Multi-cloud provider support
  - Comprehensive logging

### Contributing

To update this script:

1. Test changes in non-production environment
2. Update this runbook with any new features
3. Submit PR with changes
4. Request review from @mbaetiong

## Support and Contacts

### Primary Maintainer

- **@mbaetiong** - Approval authority for remediation mode

### Reviewers

- **@mbaetiong** - Primary reviewer
- **@Copilot** - Secondary reviewer

### Related Issues

- **#2226** - Primary tracking issue for IMDS diagnostics

### Additional Resources

- [AWS IMDS Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)
- [Azure IMDS Documentation](https://docs.microsoft.com/azure/virtual-machines/instance-metadata-service)
- [GCP Metadata Documentation](https://cloud.google.com/compute/docs/metadata/overview)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Author**: Automated IMDS Diagnostic Implementation  
**Related PR**: (to be filled)  
**Status**: ✅ Ready for Use
