# IMDS JSON Schema

## Overview

This document defines the JSON schema for IMDS diagnostic output. All diagnostic tools produce JSON output conforming to this schema.

## Schema Version

**Current Version:** 1.6.0  
**Schema URI:** `https://github.com/Aries-Serpent/_codex_/blob/main/.github/docs/IMDS_JSON_SCHEMA.md`

## Root Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/Aries-Serpent/_codex_/imds-diagnostic-v1.6.0.json",
  "title": "IMDS Diagnostic Result",
  "description": "Results from IMDS diagnostic tool",
  "type": "object",
  "required": [
    "version",
    "timestamp",
    "hostname",
    "imds_accessible",
    "exit_code"
  ],
  "properties": {
    "version": {
      "type": "string",
      "description": "Diagnostic tool version",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "examples": ["1.6.0"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of diagnostic run"
    },
    "hostname": {
      "type": "string",
      "description": "Hostname of the machine running the diagnostic"
    },
    "imds_accessible": {
      "type": "string",
      "enum": ["true", "false", "unknown"],
      "description": "Whether IMDS is accessible"
    },
    "imds_http_code": {
      "type": "string",
      "description": "HTTP status code from IMDS request",
      "pattern": "^\\d{3}$",
      "examples": ["200", "404", "500"]
    },
    "imds_curl_exit": {
      "type": "string",
      "description": "curl command exit code",
      "pattern": "^\\d+$"
    },
    "vm_id": {
      "type": "string",
      "description": "Azure VM unique identifier",
      "examples": ["12345678-1234-1234-1234-123456789abc"]
    },
    "azure_location": {
      "type": "string",
      "description": "Azure region/location",
      "examples": ["eastus", "westeurope", "southeastasia"]
    },
    "network_ping": {
      "type": "string",
      "enum": ["success", "failed"],
      "description": "Result of ping test to IMDS endpoint"
    },
    "dns_check": {
      "type": "string",
      "enum": ["expected", "local_interface", "skipped"],
      "description": "DNS resolution check result"
    },
    "firewall_check": {
      "type": "string",
      "enum": ["passed", "warning", "skipped"],
      "description": "Overall firewall detection result"
    },
    "firewall_iptables": {
      "type": "string",
      "enum": ["none", "detected", "unavailable", "permission_denied"],
      "description": "iptables firewall detection result"
    },
    "firewall_nftables": {
      "type": "string",
      "enum": ["none", "detected", "unavailable", "permission_denied"],
      "description": "nftables firewall detection result"
    },
    "attested_data_accessible": {
      "type": "string",
      "enum": ["true", "false"],
      "description": "Whether attested data endpoint is accessible"
    },
    "error_reason": {
      "type": "string",
      "description": "Specific error reason if IMDS is inaccessible",
      "examples": [
        "connection_failed",
        "timeout",
        "dns_resolution",
        "firewall_blocking"
      ]
    },
    "dependency_check": {
      "type": "string",
      "enum": ["passed", "failed"],
      "description": "Dependency check result"
    },
    "missing_dependencies": {
      "type": "string",
      "description": "Space-separated list of missing dependencies"
    },
    "summary_total_tests": {
      "type": "string",
      "description": "Total number of tests run",
      "pattern": "^\\d+$"
    },
    "summary_passed": {
      "type": "string",
      "description": "Number of tests passed",
      "pattern": "^\\d+$"
    },
    "summary_failed": {
      "type": "string",
      "description": "Number of tests failed",
      "pattern": "^\\d+$"
    },
    "summary_warnings": {
      "type": "string",
      "description": "Number of warnings",
      "pattern": "^\\d+$"
    },
    "exit_code": {
      "type": "string",
      "enum": ["0", "1", "2", "3"],
      "description": "Script exit code"
    },
    "imds_response_sample": {
      "type": "string",
      "description": "Sample of IMDS response (truncated)"
    },
    "imds_json_valid": {
      "type": "string",
      "enum": ["true", "false"],
      "description": "Whether IMDS response is valid JSON"
    }
  }
}
```

## Example Output

### Successful Diagnostic

```json
{
  "version": "1.6.0",
  "timestamp": "2024-01-15T12:00:00Z",
  "hostname": "azure-vm-prod-01",
  "imds_accessible": "true",
  "imds_http_code": "200",
  "imds_curl_exit": "0",
  "vm_id": "12345678-1234-1234-1234-123456789abc",
  "azure_location": "eastus",
  "network_ping": "success",
  "dns_check": "expected",
  "firewall_check": "passed",
  "firewall_iptables": "none",
  "firewall_nftables": "none",
  "attested_data_accessible": "true",
  "dependency_check": "passed",
  "imds_json_valid": "true",
  "imds_response_sample": "{\"compute\":{\"azEnvironment\":\"AzurePublicCloud\",\"vmId\":\"12345678-1234-1234-1234-123456789abc\",...}...",
  "summary_total_tests": "8",
  "summary_passed": "8",
  "summary_failed": "0",
  "summary_warnings": "0",
  "exit_code": "0"
}
```

### Failed Diagnostic

```json
{
  "version": "1.6.0",
  "timestamp": "2024-01-15T12:05:00Z",
  "hostname": "test-vm",
  "imds_accessible": "false",
  "imds_http_code": "000",
  "imds_curl_exit": "7",
  "error_reason": "connection_failed",
  "network_ping": "failed",
  "dns_check": "expected",
  "firewall_check": "warning",
  "firewall_iptables": "detected",
  "firewall_nftables": "none",
  "attested_data_accessible": "false",
  "dependency_check": "passed",
  "summary_total_tests": "7",
  "summary_passed": "3",
  "summary_failed": "3",
  "summary_warnings": "1",
  "exit_code": "1"
}
```

## Aggregated Results Schema

For aggregated reports from multiple hosts:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IMDS Aggregated Results",
  "type": "object",
  "required": [
    "aggregator_version",
    "report_timestamp",
    "summary",
    "diagnostics"
  ],
  "properties": {
    "aggregator_version": {
      "type": "string",
      "description": "Aggregator tool version"
    },
    "report_timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_hosts": {
          "type": "integer",
          "minimum": 0
        },
        "imds_accessible": {
          "type": "integer",
          "minimum": 0
        },
        "imds_inaccessible": {
          "type": "integer",
          "minimum": 0
        },
        "success_rate": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100
        }
      }
    },
    "diagnostics": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/diagnostic"
      }
    }
  },
  "definitions": {
    "diagnostic": {
      "type": "object",
      "description": "Individual diagnostic result"
    }
  }
}
```

## Field Descriptions

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Diagnostic tool version (semver) |
| `timestamp` | string | Yes | ISO 8601 timestamp |
| `hostname` | string | Yes | Machine hostname |
| `imds_accessible` | string | Yes | "true", "false", or "unknown" |
| `exit_code` | string | Yes | "0", "1", "2", or "3" |

### IMDS Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `imds_http_code` | string | No | HTTP status code (e.g., "200") |
| `imds_curl_exit` | string | No | curl exit code |
| `vm_id` | string | No | Azure VM ID (if accessible) |
| `azure_location` | string | No | Azure region (if accessible) |
| `imds_json_valid` | string | No | "true" or "false" |
| `imds_response_sample` | string | No | Truncated response |

### Test Results

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `network_ping` | string | No | "success" or "failed" |
| `dns_check` | string | No | DNS check result |
| `firewall_check` | string | No | Overall firewall status |
| `firewall_iptables` | string | No | iptables detection |
| `firewall_nftables` | string | No | nftables detection |
| `attested_data_accessible` | string | No | "true" or "false" |
| `dependency_check` | string | No | "passed" or "failed" |

### Summary Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `summary_total_tests` | string | No | Total tests run |
| `summary_passed` | string | No | Tests passed |
| `summary_failed` | string | No | Tests failed |
| `summary_warnings` | string | No | Warnings generated |

### Error Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error_reason` | string | No | Specific error (if failed) |
| `missing_dependencies` | string | No | Missing deps (if failed) |

## Validation

### Using jq

```bash
# Validate JSON structure
jq empty imds_results.json

# Check required fields
jq -e '.version and .timestamp and .hostname and .imds_accessible and .exit_code' imds_results.json

# Validate version format
jq -e '.version | test("^\\d+\\.\\d+\\.\\d+$")' imds_results.json
```

### Using JSON Schema Validator

```bash
# Install ajv-cli
npm install -g ajv-cli

# Validate against schema
ajv validate -s imds_schema.json -d imds_results.json
```

## Best Practices

1. **Always include required fields** - Even if values are "unknown"
2. **Use consistent timestamps** - Always UTC, ISO 8601 format
3. **Preserve numeric types** - Store as strings for consistency
4. **Include error_reason** - When imds_accessible is "false"
5. **Truncate long responses** - Keep imds_response_sample under 500 chars

## Related Documentation

- [IMDS Diagnostic Runbook](imds_diagnostic_RUNBOOK.md)
- [Error Reason Codes](imds_error_REASON_CODES.md)
- [CI Integration Guide](imds_ci_INTEGRATION_GUIDE.md)

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
