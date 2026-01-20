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
- **Format**: Codecov repository upload token
- **Used In**: 
  - `test-comprehensive.yml`
  - `test-rag.yml`
  - `rust_swarm_ci.yml`
  - `auth-tests.yml`
- **Security Level**: MEDIUM - Rotate as needed via Codecov dashboard
- **Required**: No (workflow continues without it, but coverage won't upload)
- **Note**: Updated to codecov-action@v5 requiring explicit token

#### `SESSION_ENCRYPTION_KEY`
- **Purpose**: Encrypt session data for secure storage
- **Format**: Base64-encoded Fernet key
- **Used In**: `auth-secret-rotation.yml`
- **Generation**: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- **Security Level**: HIGH - Rotate every 90 days
- **Required**: Yes (for session security features)

#### `ENABLE_LIVE_TESTS`
- **Purpose**: Feature flag to enable live integration tests
- **Format**: Boolean string ("true" or "false")
- **Used In**: `integration-gated.yml`
- **Security Level**: LOW (configuration flag)
- **Required**: No (defaults to false)

### Third-Party Integration Secrets

#### `NOTEBOOKLM_WEBHOOK_URL`
- **Purpose**: NotebookLM webhook URL for documentation sync
- **Format**: HTTPS webhook URL
- **Used In**: `notebooklm-sync.yml`
- **Security Level**: LOW - Regenerate webhook as needed
- **Required**: No (sync skipped if not available)

#### `GOOGLE_CLIENT_SECRET`
- **Purpose**: Google OAuth client secret for API access
- **Format**: Google OAuth 2.0 client secret
- **Used In**: `notebooklm-sync.yml`
- **Security Level**: MEDIUM - Rotate every 180 days
- **Required**: No (for Google Drive integration features)

#### `GDRIVE_SERVICE_ACCOUNT_JSON`
- **Purpose**: Google Drive service account credentials
- **Format**: JSON key file content (base64 or raw JSON)
- **Used In**: `notebooklm-sync.yml`
- **Security Level**: MEDIUM - Rotate annually
- **Required**: No (for automated Drive operations)

#### `GITHUB_OAUTH_CLIENT_ID`
- **Purpose**: GitHub OAuth app client ID (public identifier)
- **Format**: 20-character hex string
- **Used In**: `auth-oauth-app-sync.yml`
- **Security Level**: LOW (public identifier, not secret)
- **Required**: Yes (for OAuth flow)

#### `GITHUB_OAUTH_CLIENT_SECRET`
- **Purpose**: GitHub OAuth app client secret
- **Format**: 40-character hex string
- **Used In**: 
  - `auth-oauth-app-sync.yml`
  - `auth-secret-rotation.yml`
- **Generation**: Via GitHub OAuth App settings
- **Security Level**: HIGH - Rotate every 180 days
- **Required**: Yes (for OAuth authentication)

### AWS Integration Secrets

#### `AWS_ACCESS_KEY_ID`
- **Purpose**: AWS IAM access key ID (public identifier)
- **Format**: 20-character uppercase alphanumeric
- **Used In**: `zendesk-knowledge-sync.yml`
- **Security Level**: LOW (public identifier, paired with SECRET)
- **Required**: Yes (for AWS S3/service access)

#### `AWS_SECRET_ACCESS_KEY`
- **Purpose**: AWS IAM secret access key
- **Format**: 40-character base64-encoded string
- **Used In**: `zendesk-knowledge-sync.yml`
- **Generation**: Via AWS IAM Console
- **Security Level**: HIGH - Rotate every 90 days
- **Required**: Yes (for AWS authentication)

### Zendesk Integration Secrets

#### `ZENDESK_TOKEN`
- **Purpose**: Zendesk API authentication token
- **Format**: Zendesk API token string
- **Used In**: `zendesk-knowledge-sync.yml`
- **Generation**: Via Zendesk Admin → API settings
- **Security Level**: MEDIUM - Rotate annually
- **Required**: Yes (for knowledge base sync)

#### `ZENDESK_USER`
- **Purpose**: Zendesk account email for API authentication
- **Format**: Email address
- **Used In**: `zendesk-knowledge-sync.yml`
- **Security Level**: LOW (username, public)
- **Required**: Yes (paired with ZENDESK_TOKEN)

#### `ZENDESK_URL`
- **Purpose**: Zendesk instance URL
- **Format**: HTTPS URL (e.g., https://company.zendesk.com)
- **Used In**: `zendesk-knowledge-sync.yml`
- **Security Level**: LOW (public URL)
- **Required**: Yes (to specify Zendesk instance)

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

Comprehensive rotation schedule with all 17 secrets: **[.codex/security/rotation_schedule.md](https://github.com/Aries-Serpent/_codex_/blob/main/.codex/security/rotation_schedule.md)**

| Secret Category | Examples | Rotation Frequency | Method |
|----------------|----------|-------------------|--------|
| **Critical** | `CODEX_MASTER_KEY`, `TOKEN_SECRET_KEY` | Every 90 days (JWT: monthly) | Manual / Automated workflow |
| **High Priority** | `COMPLIANCE_REPORT_KEY`, `SESSION_ENCRYPTION_KEY`, `AWS_SECRET_ACCESS_KEY` | Every 90 days | Manual via service provider |
| **Medium Priority** | `CODECOV_TOKEN`, `ZENDESK_TOKEN`, `GOOGLE_CLIENT_SECRET` | Annually or as needed | Manual via service dashboard |
| **Config/Public IDs** | `GITHUB_TOKEN`, `AWS_ACCESS_KEY_ID`, `ZENDESK_URL` | N/A or with paired secret | GitHub auto / Manual |

### Secrets Usage Matrix

Complete mapping of all secrets to workflows: **[.codex/security/secrets_usage_matrix.json](https://github.com/Aries-Serpent/_codex_/blob/main/.codex/security/secrets_usage_matrix.json)**

**Summary**:
- Total Secrets: 17
- Total Workflows: 86
- Secret References: 107
- Most Used: `GITHUB_TOKEN` (20 workflows)
- Newly Documented: `SESSION_ENCRYPTION_KEY`, `ENABLE_LIVE_TESTS`, AWS/Zendesk/Google integration secrets

### Secret Management Guidelines

1. **Never commit secrets** to the repository
2. **Use environment-specific secrets** for dev/staging/prod
3. **Rotate compromised secrets immediately** (see emergency procedures in https://github.com/Aries-Serpent/_codex_/blob/main/.codex/security/rotation_schedule.md)
4. **Audit secret access** via GitHub audit logs
5. **Use least privilege** for workflow permissions
6. **Document all secrets** in this file
7. **Test rotation procedures** regularly
8. **Review usage matrix** monthly for unauthorized secret sprawl

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
| 2026-01-20 | **Phase 22 Secrets Audit Complete**: Added 11 undocumented secrets (SESSION_ENCRYPTION_KEY, ENABLE_LIVE_TESTS, AWS, Zendesk, Google integrations) | @copilot |
| 2026-01-20 | Created secrets usage matrix (.codex/security/secrets_usage_matrix.json) mapping 17 secrets across 86 workflows | @copilot |
| 2026-01-20 | Created comprehensive rotation schedule (.codex/security/rotation_schedule.md) with emergency procedures | @copilot |
| 2026-01-20 | Updated CODECOV_TOKEN documentation for v5 migration (4 workflows) | @copilot |

---

**Last Updated**: 2026-01-20  
**Maintainer**: @mbaetiong  
**Review Frequency**: Quarterly
