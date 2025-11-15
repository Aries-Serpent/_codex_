# IMDS File Consolidation Matrix

## Overview

This matrix documents all IMDS-related files consolidated in this repository, their purpose, and relationships.

## Core Scripts

| File | Type | Purpose | Dependencies |
|------|------|---------|--------------|
| `.github/scripts/imds_diagnostic.sh` | Script | Main diagnostic tool | bash, curl, jq, ping |
| `.github/scripts/imds_aggregate_json.sh` | Script | Aggregate multiple results | bash, jq |

## Workflows

| File | Type | Trigger | Purpose |
|------|------|---------|---------|
| `.github/workflows/imds_preflight.yml` | Workflow | PR, manual | Run diagnostics on PRs |
| `.github/workflows/imds_comment_on_issue.yml` | Workflow | Issue label, comment | Comment diagnostic results on issues |
| `.github/workflows/shellcheck.yml` | Workflow | PR, push | Lint shell scripts |

## Actions

| File | Type | Purpose | Used By |
|------|------|---------|---------|
| `.github/actions/imds-check/action.yml` | Composite Action | Reusable IMDS check | All workflows |
| `.github/actions/imds-check/README.md` | Documentation | Action usage guide | Developers |

## Configuration

| File | Type | Purpose | Format |
|------|------|---------|--------|
| `.github/imds_config.yml` | Config | Default settings | YAML |
| `.shellcheckrc` | Config | ShellCheck settings | INI-style |

## Documentation

| File | Category | Audience |
|------|----------|----------|
| `.github/docs/imds_diagnostic_RUNBOOK.md` | Operations | Operators, SREs |
| `.github/docs/imds_config_GUIDE.md` | Configuration | DevOps, Developers |
| `.github/docs/imds_firewall_DETECTORS.md` | Technical | Security, Network |
| `.github/docs/IMDS_CHANGELOG.md` | Release | All users |
| `.github/docs/imds_error_REASON_CODES.md` | Reference | Operators, Developers |
| `.github/docs/imds_ci_INTEGRATION_GUIDE.md` | Integration | DevOps, CI/CD |
| `.github/docs/IMDS_JSON_SCHEMA.md` | Reference | Developers |
| `.github/docs/imds_metrics_EXPORTER.md` | Monitoring | SREs, Operations |
| `.github/docs/imds_future_ENHANCEMENTS.md` | Planning | Contributors |
| `.github/docs/imds_host_ENV_MATRIX.md` | Compatibility | All users |
| `.github/docs/imds_shellcheck_GUIDE.md` | Development | Contributors |
| `.github/docs/IMDS_FILE_CONSOLIDATION_MATRIX.md` | Reference | Maintainers |
| `.github/docs/IMDS_IMPLEMENTATION_MERGE_PLAN.md` | Planning | Maintainers |
| `.github/docs/IMDS_MANIFEST.md` | Reference | All users |
| `.github/docs/IMDS_IMPLEMENTATION_SUMMARY.md` | Overview | Stakeholders |

## File Relationships

```
imds_diagnostic.sh
├── Called by: imds-check/action.yml
├── Configured by: imds_config.yml
├── Documented in: imds_diagnostic_RUNBOOK.md
└── Linted by: shellcheck.yml

imds-check/action.yml
├── Uses: imds_diagnostic.sh
├── Called by: imds_preflight.yml
├── Called by: imds_comment_on_issue.yml
└── Documented in: imds-check/README.md

imds_config.yml
├── Read by: imds_diagnostic.sh (future)
└── Documented in: imds_config_GUIDE.md
```

## Version Control

| Component | Version | Status |
|-----------|---------|--------|
| Scripts | 1.6.0 | Stable |
| Workflows | 1.0.0 | Stable |
| Actions | 1.0.0 | Stable |
| Documentation | 1.0.0 | Complete |

## File Sizes

| File | Approx. Size | Lines |
|------|--------------|-------|
| `imds_diagnostic.sh` | ~14KB | ~450 |
| `imds_aggregate_json.sh` | ~8KB | ~260 |
| `imds_preflight.yml` | ~5KB | ~150 |
| `imds_comment_on_issue.yml` | ~6KB | ~180 |
| `shellcheck.yml` | ~5KB | ~160 |

## Integration Points

### With GitHub Features
- **Actions**: Composite action for reusability
- **Workflows**: Automated testing and commenting
- **Issues**: Auto-commenting on IMDS issues
- **PRs**: Preflight checks on pull requests

### With External Tools
- **ShellCheck**: Code quality
- **jq**: JSON processing
- **curl**: HTTP requests
- **Prometheus**: Metrics (planned)

## Maintenance

### Update Frequency
- **Scripts**: As needed for bugs/features
- **Workflows**: Quarterly review
- **Documentation**: With each release
- **Configuration**: Rarely

### Deprecation Policy
- Scripts: 6-month notice
- Workflows: 3-month notice
- Documentation: Archive only

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
