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
