# Security Validation Report

**Generated**: 2026-01-13T20:16:00.770770Z
**Status**: ⚠️ WARNING

## Validation Results

### ✅ Audit Logging
- **Status**: PASSED
- **Enabled**: True
- **Audit Documentation**: 3
- **Audit Documentation Total**: 3
- **Docs Found**: ['docs/SECRETS_RUNBOOK.md', 'SECURITY.md', '.github/agents/SECRETS_CONFIGURATION.md']
- **Retention Days**: 90
- **Siem Streaming**: False
- **Compliance**: documented

### ⚠️ Codeql Suppressions
- **Status**: WARNING
- **Total Suppressions**: 1
- **Expired Suppressions**: 1
- **Max Age Days**: 90

### ℹ️ Branch Protection
- **Status**: INFO
- **Protected Branches**: ['main', 'develop', 'production']
- **Protection Configured**: False
- **Required Checks**: {'require_reviews': True, 'min_approvals': 1, 'dismiss_stale_reviews': True, 'require_code_owner_reviews': True, 'require_status_checks': True}

### ✅ Secret Scanning
- **Status**: PASSED
- **Enabled**: True
- **Push Protection**: False
- **Configs Found**: 2
- **Config Files**: ['.secrets.baseline', '.gitleaks.toml']

## Recommendations

1. Review 1 CodeQL suppressions older than 90 days
2. Document branch protection rules in .github/branch_protection.yml
