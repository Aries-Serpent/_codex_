# IMDS JSON Summary Schema
> Generated: 2025-11-14 23:00:10 UTC | Updated: 2025-11-15 (v1.6.1) | Author: mbaetiong

## Purpose
Define the schema for `diagnostic_results.json` produced by the canonical IMDS diagnostic script for validation, ingestion, and automation gating.

## Schema (v1.6.1)

```json
{
  "timestamp": "ISO8601 timestamp (UTC)",
  "script": "Script filename",
  "version": "Tool version (e.g., '1.6')",
  "status": "One of: 'ok' | 'remediation-recommended' | 'remediation-applied' | 'remediation-failed'",
  "apply": "Boolean - whether --apply mode was used",
  "dry_run": "Boolean - whether --dry-run mode was used",
  "api_version": "IMDS API version (e.g., '2021-02-01')",
  "env_class": "One of: 'azure_vm' | 'gha_runner' | 'container' | 'onprem_vm' | 'unknown'",
  "recommendations": ["Array of recommendation strings"],
  "recommendation_count": "Number of recommendations",
  "actions_applied": ["Array of action strings"],
  "actions_count": "Number of actions applied",
  "error_reasons": ["Array of error reason codes"],
  "metrics_generated": "Boolean - whether metrics file was generated",
  "runtime_ms": "Runtime in milliseconds",
  "mem_total_kb": "Total memory in KB",
  "mem_free_kb": "Free memory in KB",
  "mem_available_kb": "Available memory in KB",
  "issue_ref": "Issue reference (e.g., '#2226')"
}
```

## Status Field Values

### `"ok"`
- **Condition**: No issues detected, no remediation needed
- **Exit Code**: 0
- **Workflow Action**: PASS

### `"remediation-recommended"`
- **Condition**: Issues detected, but `--apply` not used (diagnostic mode only)
- **Exit Code**: 2
- **Workflow Action**: WARN (or FAIL based on workflow config)

### `"remediation-applied"`
- **Condition**: `--apply` used and remediation actions successfully applied
- **Exit Code**: 3
- **Workflow Action**: INFO (changes were made)

### `"remediation-failed"` ✅ NEW in v1.6.1
- **Condition**: `--apply` used, issues detected, but no remediation actions could be applied
- **Exit Code**: 2
- **Workflow Action**: FAIL
- **Critical**: This indicates the script attempted remediation but failed to fix the issues

## CI/CD Workflow Gating

### Recommended Gates

```yaml
# Fail if remediation is needed or failed
- name: Check IMDS Status
  run: |
    STATUS=$(jq -r '.status' diagnostic_results.json)
    if [[ "$STATUS" == "remediation-recommended" ]] || [[ "$STATUS" == "remediation-failed" ]]; then
      echo "::error::IMDS issues detected: $STATUS"
      exit 1
    fi
```

### Backward Compatibility

The new `"remediation-failed"` status maintains backward compatibility:
- Existing workflows checking `status != "ok"` will correctly fail
- Existing workflows checking for specific statuses should add `"remediation-failed"` to their fail conditions

## Example Output

### Success (No Issues)
```json
{
  "timestamp": "2025-11-15T02:00:00Z",
  "script": "imds_diagnostic.sh",
  "version": "1.6",
  "status": "ok",
  "apply": false,
  "dry_run": false,
  "api_version": "2021-02-01",
  "env_class": "azure_vm",
  "recommendations": [],
  "recommendation_count": 0,
  "actions_applied": [],
  "actions_count": 0,
  "error_reasons": [],
  "metrics_generated": true,
  "runtime_ms": 1234,
  "mem_total_kb": 8192000,
  "mem_free_kb": 4096000,
  "mem_available_kb": 5120000,
  "issue_ref": "#2226"
}
```

### Failed Remediation
```json
{
  "timestamp": "2025-11-15T02:00:00Z",
  "script": "imds_diagnostic.sh",
  "version": "1.6",
  "status": "remediation-failed",
  "apply": true,
  "dry_run": false,
  "api_version": "2021-02-01",
  "env_class": "azure_vm",
  "recommendations": ["Remove /etc/hosts overrides", "Review firewall rules"],
  "recommendation_count": 2,
  "actions_applied": [],
  "actions_count": 0,
  "error_reasons": ["hosts_override", "iptables_drop_rule"],
  "metrics_generated": true,
  "runtime_ms": 2456,
  "mem_total_kb": 8192000,
  "mem_free_kb": 4096000,
  "mem_available_kb": 5120000,
  "issue_ref": "#2226"
}
```
