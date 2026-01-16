# Auth Compliance Report

**Workflow File**: `auth-compliance-report.yml`

## Purpose

Generates weekly compliance reports for authentication security practices including:
- MFA (Multi-Factor Authentication) adoption analysis
- Token lifecycle and rotation compliance
- Security policy adherence metrics
- Automated compliance scoring and alerting

Reports are posted as GitHub issues with visual dashboards and artifact archives.

## Triggers

- **Schedule**: Weekly on Monday at 8 AM UTC (`0 8 * * 1`)
- **Manual**: `workflow_dispatch` for on-demand execution

## Permissions Required

- **contents**: `read`
- **issues**: `write`

## Environment Variables

[None specified at workflow level]

## Jobs

### generate-compliance-report

**Runner**: `ubuntu-latest`

**Steps**: 10

**Key Steps**:
1. Checkout repository
2. Set up Python
3. Install dependencies
4. Generate compliance data
5. Analyze MFA adoption
... and 5 more steps


## Secrets Used

### Required Secrets

1. **GITHUB_TOKEN** (automatic)
   - Purpose: GitHub API access for reading org/repo data and creating issues
   - Scope: Automatically provided by GitHub Actions
   
2. **CODEX_MASTER_KEY** (manual setup required)
   - Purpose: Master encryption key for TokenManager operations
   - Format: Base64-encoded string
   - Setup: Add to repository secrets via Settings → Secrets and variables → Actions
   
3. **COMPLIANCE_REPORT_KEY** (manual setup required)
   - Purpose: Fernet encryption key for securing compliance report data
   - Format: 32-byte URL-safe base64-encoded Fernet key
   - Generation: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   - Setup: Add to repository secrets via Settings → Secrets and variables → Actions
   - Security: Used to encrypt sensitive compliance data (MFA status, token lifecycle, security metrics)
   
### Secret Configuration

To set up this workflow:
```bash
# Generate COMPLIANCE_REPORT_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to GitHub repository secrets:
# 1. Navigate to: Settings → Secrets and variables → Actions → New repository secret
# 2. Add CODEX_MASTER_KEY with your master encryption key
# 3. Add COMPLIANCE_REPORT_KEY with the generated Fernet key
```

## Maintenance

**Last Generated**: 2026-01-16  
**Status**: Active  
**Maintainer**: DevOps Team

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

*This documentation was automatically generated. For detailed configuration, refer to the workflow file.*
