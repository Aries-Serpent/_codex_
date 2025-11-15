# IMDS Host Environment Matrix (Updated)
> Generated: 2025-11-14 23:06:24 UTC | Author: mbaetiong

## Purpose
Map expected diagnostic outcomes by environment type to reduce false positives.

## Environments
| Env Type | Classifier | HTTP | TCP | WALinuxAgent | Notes |
|----------|-----------|------|-----|--------------|-------|
| Azure VM | azure_vm | ✓ | ✓ | ✓ | Target baseline |
| Azure Scale Set | azure_scaleset | ✓ | ✓ | ✓ | Large fleet |
| GitHub Hosted Runner | gha_runner | ✗ | ✗ | ✗ | Expected unreachable |
| On-Prem VM | onprem_vm | ✗ | ✗ | ✗ | Ignore IMDS failures |
| Container | container | ✗ | ✗ | ✗ | Network isolation |
| WSL2 | wsl2 | ✗ | ✗ | ✗ | Non-target scenario |
| Edge Device | edge | ✗ | ✗ | ✗ | Out of scope |

## Interpretation Rules
| Condition | Action |
|-----------|--------|
| Azure VM + HTTP unreachable | Treat as failure; remediation recommended |
| GitHub Hosted + HTTP unreachable | Do not remediate; annotate environment |
| Non-Azure + hosts override | Remove if interfering with other services |
| WALinuxAgent inactive on Azure | Attempt restart after approval |

Relates to issue: #2226
