# Secrets and Environment Variables Documentation

## Overview

This document provides comprehensive documentation for all secrets and environment variables used in the Codex repository, particularly for authentication, security, and CI/CD workflows.

## Required GitHub Secrets

### Core Authentication Secrets

#### `CODEX_MASTER_KEY`
- **Purpose**: Master encryption key for token management and sensitive data
- **Format**: Base64-encoded 32-byte key (Fernet-compatible)
- **Used In**:
  - `auth-compliance-report.yml`
  - `auth-token-rotation.yml`
  - Token management scripts
  - Authentication modules
- **Generation**: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- **Security Level**: CRITICAL - Rotate every 90 days

#### `COMPLIANCE_REPORT_KEY`
- **Purpose**: Encryption key specifically for compliance reports
- **Format**: Base64-encoded Fernet key
- **Used In**:
  - `auth-compliance-report.yml`
  - `scripts/compliance_reporter.py`
- **Generation**: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- **Security Level**: HIGH - Rotate every 90 days
- **Note**: Must be set for compliance reporter to function

#### `TOKEN_SECRET_KEY`
- **Purpose**: JWT token signing secret
- **Format**: Minimum 32-character random string
- **Used In**:
  - `auth-token-rotation.yml`
  - `scripts/rotate_jwt_secret.py`
  - OAuth2 authentication flows
- **Generation**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Security Level**: CRITICAL - Rotated automatically by workflow
- **Rotation**: Monthly (automated via workflow)

#### `GITHUB_TOKEN`
- **Purpose**: GitHub Actions default token for API access
- **Format**: Automatically provided by GitHub Actions
- **Permissions**: Configured per workflow
- **Used In**: All workflows requiring GitHub API access
- **Security Level**: HIGH - Managed by GitHub

### Optional Secrets

#### `CODECOV_TOKEN`
- **Purpose**: Upload coverage reports to Codecov
- **Used In**: `rust_swarm_ci.yml`
- **Required**: No (workflow continues without it)

#### `NOTEBOOKLM_API_KEY`
- **Purpose**: NotebookLM integration for documentation sync
- **Used In**: `notebooklm-sync.yml`
- **Required**: No (sync skipped if not available)

## Environment Variables

### Runtime Configuration

#### `CODEX_ENV_*`
- **Purpose**: Select language versions during environment setup
- **Variables**:
  - `CODEX_ENV_PYTHON_VERSION` (default: 3.11)
  - `CODEX_ENV_NODE_VERSION` (default: 18)
  - `CODEX_ENV_RUST_VERSION` (default: 1.92)
  - `CODEX_ENV_GO_VERSION` (default: 1.21)
  - `CODEX_ENV_SWIFT_VERSION` (default: 5.9)

#### `CODEX_SESSION_*`
- **Purpose**: Session management and logging
- **Variables**:
  - `CODEX_SESSION_ID`: Unique session identifier
  - `CODEX_SESSION_LOG_DIR`: Log directory (default: `.codex/sessions`)

#### `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH`
- **Purpose**: SQLite database path for logging
- **Default**: `.codex/logs.db`

#### `CODEX_SQLITE_POOL`
- **Purpose**: Enable per-session SQLite connection pooling
- **Values**: `1` (enabled) or `0` (disabled)
- **Default**: `0`

### CI/CD Environment Variables

#### `CARGO_TERM_COLOR`
- **Purpose**: Enable colored output in Cargo
- **Value**: `always`
- **Used In**: Rust CI workflows

#### `RUST_BACKTRACE`
- **Purpose**: Enable full backtraces for Rust panics
- **Value**: `1` or `full`
- **Used In**: Rust testing and debugging

#### `RUST_TEST_THREADS`
- **Purpose**: Control test parallelism
- **Value**: `1` (sequential) for deterministic tests
- **Used In**: `rust_swarm_ci.yml`

## Workflow Permissions

### Required Permissions by Workflow

#### `auth-token-rotation.yml`
```yaml
permissions:
  contents: write     # Read/write repository contents
  issues: write       # Create audit issues
  secrets: write      # Update GitHub secrets
```

#### `auth-secret-rotation.yml`
```yaml
permissions:
  contents: write     # Read/write repository contents
  secrets: write      # Rotate secrets
  issues: write       # Create audit trail
```

#### `auth-compliance-report.yml`
```yaml
permissions:
  contents: read      # Read repository data
  issues: write       # Post compliance reports
```

#### `phase10-automated-secrets-setup.yml`
```yaml
permissions:
  contents: read      # Read configuration
  actions: write      # Manage workflow state
  secrets: write      # Initialize secrets
```

## Security Best Practices

### Secret Rotation Schedule

| Secret | Rotation Frequency | Method |
|--------|-------------------|--------|
| `CODEX_MASTER_KEY` | Every 90 days | Manual via GitHub UI |
| `COMPLIANCE_REPORT_KEY` | Every 90 days | Manual via GitHub UI |
| `TOKEN_SECRET_KEY` | Monthly | Automated workflow |
| GitHub Secrets | Monthly | Automated workflow |

### Secret Management Guidelines

1. **Never commit secrets** to the repository
2. **Use environment-specific secrets** for dev/staging/prod
3. **Rotate compromised secrets immediately**
4. **Audit secret access** via GitHub audit logs
5. **Use least privilege** for workflow permissions
6. **Document all secrets** in this file
7. **Test rotation procedures** regularly

### MFA and Authentication

#### MFA Enrollment Process

The MFA enrollment automation (`scripts/mfa_enrollment_automation.py`) generates TOTP secrets and backup codes but **does not store or transmit them automatically**. In production:

1. Credentials must be delivered via secure, authenticated channels:
   - Encrypted email with PGP
   - SMS to verified numbers
   - Secure internal portal with authentication
   - Physical security keys

2. The current implementation is a **placeholder** - implement secure delivery before production use.

3. Never log or expose MFA secrets in plain text.

## Troubleshooting

### Missing Secret Errors

**Error**: `COMPLIANCE_REPORT_KEY environment variable must be set`
- **Solution**: Add `COMPLIANCE_REPORT_KEY` to GitHub repository secrets
- **Generation**: See "Required GitHub Secrets" section above

**Error**: `RuntimeError: No token secret key available`
- **Solution**: Ensure `TOKEN_SECRET_KEY` is set in repository secrets
- **Note**: Will be generated automatically by rotation workflow

### Permission Errors

**Error**: `Resource not accessible by integration`
- **Solution**: Check workflow `permissions` section matches requirements
- **Verify**: Token has required scopes in workflow YAML

### Rotation Failures

**Error**: Rotation workflow fails to update secrets
- **Check**: `secrets: write` permission is enabled
- **Verify**: `GITHUB_TOKEN` has organization admin rights (if org-level secrets)
- **Note**: Repository secrets require repo admin; org secrets require org admin

## Monitoring and Auditing

### Audit Log Locations

1. **GitHub Audit Log**: Settings → Security → Audit log
2. **Workflow Runs**: Actions tab → Select workflow
3. **Secret Access**: Audit log → Filter by "secret"
4. **Issue Tracker**: Auto-created audit issues for rotations

### Alert Conditions

- Failed secret rotation (creates GitHub issue)
- Low MFA adoption rate (< 80%)
- Expired tokens detected
- Anomalous access patterns

## References

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Fernet Encryption](https://cryptography.io/en/latest/fernet/)
- [TOTP RFC 6238](https://tools.ietf.org/html/rfc6238)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-16 | Initial documentation created | @copilot |
| 2026-01-16 | Added COMPLIANCE_REPORT_KEY documentation | @copilot |
| 2026-01-16 | Documented MFA credential handling | @copilot |

---

**Last Updated**: 2026-01-16  
**Maintainer**: @mbaetiong  
**Review Frequency**: Quarterly
