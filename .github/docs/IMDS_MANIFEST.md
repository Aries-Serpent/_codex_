# IMDS Manifest

## Repository Information

**Repository**: Aries-Serpent/_codex_  
**Component**: IMDS Diagnostic Tooling  
**Version**: 1.6.0  
**Release Date**: 2024-01-15  
**License**: MIT

## Components

### Scripts (2)
1. **imds_diagnostic.sh**
   - Version: 1.6.0
   - Purpose: Main IMDS diagnostic tool
   - Language: Bash
   - Size: ~14KB
   - Location: `.github/scripts/imds_diagnostic.sh`

2. **imds_aggregate_json.sh**
   - Version: 1.0.0
   - Purpose: Aggregate diagnostic results
   - Language: Bash
   - Size: ~8KB
   - Location: `.github/scripts/imds_aggregate_json.sh`

### Workflows (3)
1. **imds_preflight.yml**
   - Purpose: PR preflight checks
   - Triggers: pull_request, workflow_dispatch
   - Location: `.github/workflows/imds_preflight.yml`

2. **imds_comment_on_issue.yml**
   - Purpose: Auto-comment on issues
   - Triggers: issues, issue_comment
   - Location: `.github/workflows/imds_comment_on_issue.yml`

3. **shellcheck.yml**
   - Purpose: Shell script linting
   - Triggers: pull_request, push
   - Location: `.github/workflows/shellcheck.yml`

### Actions (1)
1. **imds-check**
   - Type: Composite Action
   - Purpose: Reusable IMDS diagnostic check
   - Location: `.github/actions/imds-check/`

### Configuration (2)
1. **imds_config.yml**
   - Purpose: Default IMDS configuration
   - Location: `.github/imds_config.yml`

2. **.shellcheckrc**
   - Purpose: ShellCheck configuration
   - Location: `.shellcheckrc`

### Documentation (15)
1. imds_diagnostic_RUNBOOK.md - Operations guide
2. imds_config_GUIDE.md - Configuration guide
3. imds_firewall_DETECTORS.md - Firewall detection guide
4. IMDS_CHANGELOG.md - Release history
5. imds_error_REASON_CODES.md - Error reference
6. imds_ci_INTEGRATION_GUIDE.md - CI/CD integration
7. IMDS_JSON_SCHEMA.md - JSON schema reference
8. imds_metrics_EXPORTER.md - Metrics documentation
9. imds_future_ENHANCEMENTS.md - Roadmap
10. imds_host_ENV_MATRIX.md - Compatibility matrix
11. imds_shellcheck_GUIDE.md - Linting guide
12. IMDS_FILE_CONSOLIDATION_MATRIX.md - File relationships
13. IMDS_IMPLEMENTATION_MERGE_PLAN.md - Merge strategy
14. IMDS_MANIFEST.md - This file
15. IMDS_IMPLEMENTATION_SUMMARY.md - Implementation overview

## Dependencies

### Required
- bash (>= 4.0)
- curl (>= 7.0)
- jq (>= 1.5)
- coreutils
- iputils-ping

### Optional
- sudo (for firewall detection)
- iptables (for firewall detection)
- nftables (for firewall detection)

## Installation

```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Checkout IMDS branch
git checkout imds/v1.6-canonical

# Install dependencies (Ubuntu/Debian)
sudo apt-get install -y curl jq iputils-ping coreutils

# Make scripts executable
chmod +x .github/scripts/imds_*.sh

# Run diagnostic
./.github/scripts/imds_diagnostic.sh
```

## Usage

### Command Line
```bash
# Basic check
./.github/scripts/imds_diagnostic.sh

# Verbose mode with output file
./.github/scripts/imds_diagnostic.sh --verbose --output results.json

# Skip optional tests
./.github/scripts/imds_diagnostic.sh --skip-firewall --skip-dns
```

### GitHub Actions
```yaml
- uses: ./.github/actions/imds-check
  with:
    verbose: true
    timeout: 10
```

## Support

### Issues
Report issues at: https://github.com/Aries-Serpent/_codex_/issues  
Label: `imds`

### Documentation
All documentation: `.github/docs/imds_*.md`

### Contacts
- **Maintainer**: IMDS Diagnostic Team
- **Assignee**: @mbaetiong
- **Reviewer**: @Copilot

## Release Notes

### Version 1.6.0 (2024-01-15)
- Initial canonical release
- Comprehensive diagnostic tool
- GitHub Actions integration
- Complete documentation suite
- ShellCheck linting
- Composite action for reusability

## Checksums

```
# Generate checksums
find .github/scripts -name "*.sh" -exec sha256sum {} \;
find .github/workflows -name "*.yml" -exec sha256sum {} \;
```

## License

MIT License - See repository LICENSE file

---

**Manifest Version**: 1.0.0  
**Generated**: 2024-01-15  
**Maintained By**: IMDS Diagnostic Team
