# IMDS Check Action

A composite GitHub Action for running comprehensive Azure Instance Metadata Service (IMDS) diagnostics.

## Description

This action runs the IMDS diagnostic script and provides structured output about the Azure VM's ability to access the Instance Metadata Service. It performs various checks including network connectivity, firewall detection, DNS resolution, and metadata retrieval.

## Usage

### Basic Usage

```yaml
- name: Run IMDS Diagnostic
  uses: ./.github/actions/imds-check
```

### Advanced Usage

```yaml
- name: Run IMDS Diagnostic
  id: imds
  uses: ./.github/actions/imds-check
  with:
    verbose: true
    timeout: 10
    skip-firewall: false
    skip-dns: false
    output-file: 'custom_results.json'
    fail-on-inaccessible: true

- name: Use outputs
  run: |
    echo "IMDS Accessible: ${{ steps.imds.outputs.imds-accessible }}"
    echo "VM ID: ${{ steps.imds.outputs.vm-id }}"
    echo "Location: ${{ steps.imds.outputs.azure-location }}"
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `verbose` | Enable verbose output | No | `false` |
| `timeout` | Timeout for IMDS requests in seconds | No | `5` |
| `skip-firewall` | Skip firewall detection tests | No | `false` |
| `skip-dns` | Skip DNS resolution tests | No | `false` |
| `output-file` | Path to output JSON file | No | `imds_results.json` |
| `output-artifact` | Upload results as workflow artifact | No | `true` |
| `fail-on-inaccessible` | Fail the action if IMDS is inaccessible | No | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `imds-accessible` | Whether IMDS is accessible (`true`/`false`) |
| `vm-id` | Azure VM ID if IMDS is accessible |
| `azure-location` | Azure region/location if IMDS is accessible |
| `exit-code` | Exit code from diagnostic script |
| `results-file` | Path to the results JSON file |

## Examples

### Preflight Check in PR

```yaml
name: IMDS Preflight
on: pull_request

jobs:
  check-imds:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/imds-check
        with:
          verbose: true
          fail-on-inaccessible: false
```

### Conditional Workflow Based on IMDS

```yaml
- name: Check IMDS
  id: imds
  uses: ./.github/actions/imds-check

- name: Deploy to Azure
  if: steps.imds.outputs.imds-accessible == 'true'
  run: |
    echo "Deploying to Azure VM ${{ steps.imds.outputs.vm-id }}"
    # deployment commands
```

### Custom Output File

```yaml
- name: Run Diagnostic
  uses: ./.github/actions/imds-check
  with:
    output-file: 'diagnostics/imds_check.json'
    timeout: 15
    verbose: true
```

## Exit Codes

The action uses the following exit codes from the diagnostic script:

- `0` - IMDS accessible and working correctly
- `1` - IMDS inaccessible or errors detected
- `2` - Invalid arguments or configuration
- `3` - Missing required dependencies

## Output Format

The action generates a JSON file with diagnostic results:

```json
{
  "version": "1.6.0",
  "timestamp": "2024-01-15T12:00:00Z",
  "hostname": "vm-hostname",
  "imds_accessible": "true",
  "vm_id": "12345678-1234-1234-1234-123456789abc",
  "azure_location": "eastus",
  "imds_http_code": "200",
  "network_ping": "success",
  "firewall_check": "passed",
  "summary_total_tests": "8",
  "summary_passed": "7",
  "summary_failed": "0",
  "summary_warnings": "1"
}
```

## Troubleshooting

### IMDS Not Accessible

If IMDS is not accessible, check:

1. **Runner Type**: Ensure you're using an Azure-hosted runner or self-hosted runner on an Azure VM
2. **Firewall Rules**: Check for firewall rules blocking 169.254.169.254
3. **Network Configuration**: Verify network connectivity to the link-local address
4. **VM Configuration**: Ensure IMDS is enabled on the Azure VM

### Dependencies Not Found

The action automatically installs required dependencies (`curl`, `jq`, `ping`). If installation fails:

```yaml
- name: Install dependencies manually
  run: |
    sudo apt-get update
    sudo apt-get install -y curl jq iputils-ping
```

### Permission Issues

Some checks (firewall detection) may require elevated permissions:

```yaml
- name: Run with sudo
  run: sudo .github/scripts/imds_diagnostic.sh
```

## Related Documentation

- [IMDS Diagnostic Runbook](../../docs/imds_diagnostic_RUNBOOK.md)
- [Configuration Guide](../../docs/imds_config_GUIDE.md)
- [Firewall Detectors](../../docs/imds_firewall_DETECTORS.md)
- [Error Reason Codes](../../docs/imds_error_REASON_CODES.md)

## Support

For issues or questions:

1. Check the [troubleshooting guide](../../docs/imds_diagnostic_RUNBOOK.md#troubleshooting)
2. Review [known issues](../../docs/IMDS_CHANGELOG.md)
3. Open an issue with the `imds` label

## License

MIT License - See repository LICENSE file for details.
