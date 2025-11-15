# IMDS Configuration Guide

## Overview

This guide explains how to configure the IMDS diagnostic tools and workflows for your environment. Configuration can be done through the `.github/imds_config.yml` file, environment variables, or workflow inputs.

## Configuration File

The main configuration file is located at `.github/imds_config.yml`. This file controls default behavior for all IMDS diagnostic tools.

### Structure

```yaml
# IMDS Endpoint Configuration
imds:
  endpoint: "169.254.169.254"
  api_version: "2021-02-01"
  timeout: 5
  retry_attempts: 3
  retry_delay: 2

# Diagnostic Test Configuration
diagnostic:
  skip_firewall_check: false
  skip_dns_check: false
  verbose_output: false
  output_format: "json"

# CI/CD Integration
ci:
  enabled: true
  fail_on_inaccessible: true
  upload_artifacts: true
  artifact_retention_days: 30

# Workflow Settings
workflow:
  preflight:
    enabled: true
    run_on_pr: true
    run_on_push: false
    required_status: true
  
  comment_on_issue:
    enabled: true
    auto_comment: true
    include_summary: true
    include_detailed_results: false

# Shellcheck Configuration
shellcheck:
  severity: "warning"
  shell: "bash"
  enable_all_checks: true
  excluded_rules: []

# Firewall Detection
firewall:
  check_iptables: true
  check_nftables: true
  check_ufw: false
  require_sudo: false

# Metrics and Monitoring
metrics:
  enabled: false
  export_format: "prometheus"
  export_path: "/metrics"
  collection_interval: 300

# Advanced Settings
advanced:
  parallel_execution: false
  max_parallel_jobs: 5
  debug_mode: false
  log_level: "info"
```

## Configuration Options

### IMDS Endpoint Settings

#### `imds.endpoint`
- **Type:** String
- **Default:** `"169.254.169.254"`
- **Description:** The IMDS endpoint IP address. Should not be changed unless using a custom IMDS proxy.

#### `imds.api_version`
- **Type:** String
- **Default:** `"2021-02-01"`
- **Description:** Azure IMDS API version to use.
- **Available versions:** `2018-10-01`, `2019-06-01`, `2020-09-01`, `2021-02-01`

#### `imds.timeout`
- **Type:** Integer
- **Default:** `5`
- **Description:** Request timeout in seconds.
- **Range:** 1-60

#### `imds.retry_attempts`
- **Type:** Integer
- **Default:** `3`
- **Description:** Number of retry attempts for failed requests.

#### `imds.retry_delay`
- **Type:** Integer
- **Default:** `2`
- **Description:** Delay between retry attempts in seconds.

### Diagnostic Settings

#### `diagnostic.skip_firewall_check`
- **Type:** Boolean
- **Default:** `false`
- **Description:** Skip firewall rule detection (useful in restricted environments).

#### `diagnostic.skip_dns_check`
- **Type:** Boolean
- **Default:** `false`
- **Description:** Skip DNS resolution checks.

#### `diagnostic.verbose_output`
- **Type:** Boolean
- **Default:** `false`
- **Description:** Enable verbose logging by default.

#### `diagnostic.output_format`
- **Type:** String
- **Default:** `"json"`
- **Description:** Default output format.
- **Options:** `json`, `yaml`, `text`

### CI/CD Settings

#### `ci.enabled`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Enable CI/CD integrations.

#### `ci.fail_on_inaccessible`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Fail CI build if IMDS is inaccessible.

#### `ci.upload_artifacts`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Upload diagnostic results as workflow artifacts.

#### `ci.artifact_retention_days`
- **Type:** Integer
- **Default:** `30`
- **Description:** Days to retain artifacts.
- **Range:** 1-90

### Workflow Configuration

#### Preflight Workflow

```yaml
workflow:
  preflight:
    enabled: true              # Enable preflight checks
    run_on_pr: true           # Run on pull requests
    run_on_push: false        # Run on pushes
    required_status: true     # Make status check required
```

#### Issue Comment Workflow

```yaml
workflow:
  comment_on_issue:
    enabled: true                    # Enable issue commenting
    auto_comment: true               # Automatically comment on IMDS-labeled issues
    include_summary: true            # Include summary in comments
    include_detailed_results: false  # Include full JSON in comments
```

## Environment Variables

Environment variables override configuration file settings:

### Core Variables

```bash
# IMDS endpoint
export IMDS_ENDPOINT="169.254.169.254"

# API version
export IMDS_API_VERSION="2021-02-01"

# Request timeout
export IMDS_TIMEOUT="10"

# Enable verbose mode
export IMDS_VERBOSE="true"

# Skip firewall checks
export IMDS_SKIP_FIREWALL="true"

# Skip DNS checks
export IMDS_SKIP_DNS="true"
```

### CI/CD Variables

```bash
# GitHub Actions
export GITHUB_TOKEN="<token>"
export RUNNER_TEMP="/tmp"

# Fail on inaccessible
export IMDS_FAIL_ON_ERROR="true"

# Output file path
export IMDS_OUTPUT_FILE="/tmp/imds_results.json"
```

## Workflow Configuration

### Preflight Workflow

Customize `.github/workflows/imds_preflight.yml`:

```yaml
on:
  pull_request:
    branches:
      - main
      - develop
      - '0D_base_'
    paths:
      - '.github/scripts/imds_*.sh'
      - '.github/workflows/imds_*.yml'

permissions:
  contents: read
  pull-requests: write
  checks: write
```

### Issue Comment Workflow

Customize `.github/workflows/imds_comment_on_issue.yml`:

```yaml
on:
  issues:
    types: [opened, labeled]
  issue_comment:
    types: [created]

# Trigger on 'imds' label or '/imds-check' comment
if: |
  (github.event_name == 'issues' && contains(github.event.issue.labels.*.name, 'imds')) ||
  (github.event_name == 'issue_comment' && contains(github.event.comment.body, '/imds-check'))
```

## Action Configuration

When using the composite action:

```yaml
- uses: ./.github/actions/imds-check
  with:
    # Enable verbose output
    verbose: true
    
    # Custom timeout
    timeout: 10
    
    # Skip optional tests
    skip-firewall: false
    skip-dns: false
    
    # Custom output file
    output-file: 'custom_results.json'
    
    # Control artifact upload
    output-artifact: true
    
    # Fail on inaccessible
    fail-on-inaccessible: true
```

## Per-Environment Configuration

### Development

```yaml
# .github/imds_config.dev.yml
imds:
  timeout: 10  # Longer timeout for dev
  
diagnostic:
  verbose_output: true  # Always verbose in dev
  
ci:
  fail_on_inaccessible: false  # Don't fail builds in dev
```

### Production

```yaml
# .github/imds_config.prod.yml
imds:
  timeout: 5
  retry_attempts: 5  # More retries in prod
  
ci:
  fail_on_inaccessible: true  # Strict in production
  artifact_retention_days: 90  # Keep longer
```

### Using Environment-Specific Config

```bash
# Load environment-specific config
export IMDS_CONFIG_FILE=".github/imds_config.${ENVIRONMENT}.yml"
```

## Advanced Configuration

### Custom Firewall Detection

Add custom firewall detection logic:

```yaml
firewall:
  check_iptables: true
  check_nftables: true
  check_ufw: true
  check_firewalld: true
  custom_commands:
    - "pfctl -s rules | grep 169.254.169.254"  # BSD/macOS
    - "ipfw list | grep 169.254.169.254"       # FreeBSD
```

### Metrics Export

Enable Prometheus metrics:

```yaml
metrics:
  enabled: true
  export_format: "prometheus"
  export_path: "/var/lib/node_exporter/textfile_collector/imds.prom"
  collection_interval: 300  # 5 minutes
  
  # Metric labels
  labels:
    environment: "production"
    region: "eastus"
    team: "platform"
```

### Custom Notification

Configure custom notifications:

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#imds-alerts"
    on_failure: true
    on_success: false
  
  email:
    enabled: true
    recipients:
      - "ops-team@example.com"
    on_failure: true
    on_success: false
  
  pagerduty:
    enabled: false
    integration_key: "${PAGERDUTY_KEY}"
    severity: "error"
```

## Security Considerations

### Secrets Management

Never commit sensitive values:

```yaml
# ❌ BAD
notifications:
  slack:
    webhook_url: "https://hooks.slack.com/services/ABC/DEF/XYZ"

# ✅ GOOD
notifications:
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
```

Use GitHub Secrets:

```yaml
env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Least Privilege

Configure minimal permissions:

```yaml
firewall:
  require_sudo: false  # Don't require sudo if not needed
  
diagnostic:
  skip_firewall_check: true  # Skip if no sudo access
```

## Validation

Validate your configuration:

```bash
# Check YAML syntax
yamllint .github/imds_config.yml

# Validate against schema (if available)
yq eval .github/imds_config.yml

# Test configuration
./.github/scripts/imds_diagnostic.sh --verbose --timeout 1
```

## Troubleshooting

### Configuration Not Applied

1. Check file path: `.github/imds_config.yml`
2. Verify YAML syntax
3. Check environment variable overrides
4. Review workflow logs

### Permission Issues

If firewall checks fail:

```yaml
firewall:
  require_sudo: true  # Enable if needed
  check_iptables: false  # Disable if no permissions
```

### Timeout Issues

Adjust timeouts for slow networks:

```yaml
imds:
  timeout: 30  # Increase for slow networks
  retry_attempts: 5
  retry_delay: 5
```

## Best Practices

1. **Start with defaults**: Only override what's necessary
2. **Environment-specific configs**: Use separate configs for dev/staging/prod
3. **Version control**: Track all configuration changes
4. **Documentation**: Document custom configurations
5. **Validation**: Always validate before committing
6. **Secrets**: Never commit sensitive data

## Related Documentation

- [IMDS Diagnostic Runbook](imds_diagnostic_RUNBOOK.md)
- [CI Integration Guide](imds_ci_INTEGRATION_GUIDE.md)
- [JSON Schema](IMDS_JSON_SCHEMA.md)
- [Error Reason Codes](imds_error_REASON_CODES.md)

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
