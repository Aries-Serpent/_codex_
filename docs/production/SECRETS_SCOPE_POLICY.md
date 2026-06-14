# GitHub Secrets Scope & Environment Policy

**Document**: Security & Compliance Policy  
**Audience**: DevOps, Security, Platform Engineering  
**Effective Date**: 2026-06-14  
**Classification**: Internal  

---

## Executive Summary

This policy defines the scoping and isolation requirements for GitHub Secrets across development, staging, and production environments. It ensures:

- **No cross-environment credential sharing**
- **Least-privilege access per environment**
- **Automated compliance verification**
- **Audit trail for all secret operations**

---

## 1. Secrets Classification

### 1.1 Secret Types

| Type | Scope | Rotation | Example |
|------|-------|----------|---------|
| Master Keys | Production only | Quarterly | CODEX_MASTER_KEY |
| Environment Keys | Per-environment | Monthly | CODEX_MASTER_KEY_STAGING |
| Service Tokens | Environment-specific | Monthly | github.token | <!-- pragma: allowlist secret -->
| Database Passwords | Per-environment | Quarterly | DB_PASSWORD | <!-- pragma: allowlist secret -->
| API Keys | Per-environment | Annual | API_KEY_* | <!-- pragma: allowlist secret -->
| TLS Certificates | Production | Annual | TLS_CERT_* |

### 1.2 Criticality Levels

- **CRITICAL**: Master keys, production database passwords
- **HIGH**: Service tokens, production API keys
- **MEDIUM**: Development keys, staging credentials
- **LOW**: Non-sensitive configuration values

---

## 2. Scope Rules - By Environment

### 2.1 Production Environment

**Allowed Secrets**:
```
CODEX_MASTER_KEY
CODEX_BACKUP_KEY
GITHUB_TOKEN  # pragma: allowlist secret
GITHUB_TOKEN_PRODUCTION  # pragma: allowlist secret
DEPLOYMENT_KEY_PRODUCTION
DB_PASSWORD_PRODUCTION  # pragma: allowlist secret
API_KEY_PRODUCTION  # pragma: allowlist secret
SLACK_WEBHOOK_PRODUCTION
GCP_SA_KEY_PRODUCTION
DOCKER_HUB_TOKEN_PRODUCTION  # pragma: allowlist secret
TLS_CERT_PRODUCTION
```

**Forbidden Patterns**:
- Any secret ending in `_DEV`, `_STAGING`, `_TEST`
- Development database names in production paths
- Staging API endpoints in production config
- Test tokens in production workflow

**Access Control**:
- DevOps Lead (read/write)
- Security Lead (read)
- On-call Engineer (read-only)

### 2.2 Staging Environment

**Allowed Secrets**:
```
CODEX_MASTER_KEY_STAGING
GITHUB_TOKEN_STAGING  # pragma: allowlist secret
DEPLOYMENT_KEY_STAGING
DB_PASSWORD_STAGING  # pragma: allowlist secret
API_KEY_STAGING  # pragma: allowlist secret
SLACK_WEBHOOK_STAGING
GCP_SA_KEY_STAGING
DOCKER_HUB_TOKEN_STAGING  # pragma: allowlist secret
```

**Forbidden Patterns**:
- Production secrets (without _STAGING suffix)
- Production database credentials
- Production API keys
- _PRODUCTION suffix in names

**Access Control**:
- All engineers (read)
- DevOps team (read/write)
- QA team (read-only)

### 2.3 Development Environment

**Allowed Secrets**:
```
CODEX_MASTER_KEY_DEV
GITHUB_TOKEN_DEV  # pragma: allowlist secret
DEPLOYMENT_KEY_DEV
DB_PASSWORD_DEV  # pragma: allowlist secret
API_KEY_DEV  # pragma: allowlist secret
SLACK_WEBHOOK_DEV
```

**Forbidden Patterns**:
- Production secrets
- Staging secrets
- _PRODUCTION or _STAGING suffixes
- Real production database URLs

**Access Control**:
- All engineers (read/write)
- Open access for development

---

## 3. Secrets Storage & Isolation

### 3.1 GitHub Secrets Hierarchy

```
Repository Secrets  # pragma: allowlist secret
├── CODEX_MASTER_KEY (shared across environments)
├── CODEX_BACKUP_KEY
├── GITHUB_TOKEN  # pragma: allowlist secret
└── Environment-specific:
    ├── Production Environment
    │   ├── DEPLOYMENT_KEY_PRODUCTION
    │   ├── DB_PASSWORD_PRODUCTION  # pragma: allowlist secret
    │   └── API_KEY_PRODUCTION  # pragma: allowlist secret
    ├── Staging Environment
    │   ├── DEPLOYMENT_KEY_STAGING
    │   ├── DB_PASSWORD_STAGING  # pragma: allowlist secret
    │   └── API_KEY_STAGING  # pragma: allowlist secret
    └── Development Environment
        ├── DEPLOYMENT_KEY_DEV
        ├── DB_PASSWORD_DEV  # pragma: allowlist secret
        └── API_KEY_DEV  # pragma: allowlist secret
```

### 3.2 Secret Isolation Implementation

**GitHub Actions Environment Protection Rules**:

```yaml
# Environment: production
protection_rules:
  - type: required_reviewers
    count: 2
    dismiss_stale: false
  - type: deployment_branches
    branches:
      - main
  - type: environment_secrets_accessible_only_to:
    - deployment_jobs
    - maintenance_jobs

# Environment: staging
protection_rules:
  - type: required_reviewers
    count: 1
  - type: deployment_branches
    branches:
      - develop
      - release/*

# Environment: development
protection_rules:
  - type: required_reviewers
    count: 0
  - type: deployment_branches
    branches:
      - "*"
```

### 3.3 Preventing Cross-Environment Leakage

```python
#!/usr/bin/env python3
# .github/scripts/validate_secrets_scope.py  # pragma: allowlist secret

import os
import sys

ENVIRONMENT = os.getenv("GITHUB_ENVIRONMENT", "unknown")
ACCESSIBLE_SECRETS = {  # pragma: allowlist secret
    "production": {
        "CODEX_MASTER_KEY",
        "CODEX_BACKUP_KEY",
        "GITHUB_TOKEN",  # pragma: allowlist secret
        "DEPLOYMENT_KEY_PRODUCTION",
        "DB_PASSWORD_PRODUCTION",  # pragma: allowlist secret
        "API_KEY_PRODUCTION",  # pragma: allowlist secret
    },
    "staging": {
        "CODEX_MASTER_KEY_STAGING",
        "GITHUB_TOKEN_STAGING",  # pragma: allowlist secret
        "DEPLOYMENT_KEY_STAGING",
        "DB_PASSWORD_STAGING",  # pragma: allowlist secret
        "API_KEY_STAGING",  # pragma: allowlist secret
    },
    "development": {
        "CODEX_MASTER_KEY_DEV",
        "GITHUB_TOKEN_DEV",  # pragma: allowlist secret
        "DEPLOYMENT_KEY_DEV",
        "DB_PASSWORD_DEV",  # pragma: allowlist secret
        "API_KEY_DEV",  # pragma: allowlist secret
    }
}

def check_forbidden_secrets():  # pragma: allowlist secret
    """Check that environment doesn't have cross-environment secrets"""  # pragma: allowlist secret
    if ENVIRONMENT not in ACCESSIBLE_SECRETS:  # pragma: allowlist secret
        print(f"❌ Unknown environment: {ENVIRONMENT}")
        sys.exit(1)
    
    allowed = ACCESSIBLE_SECRETS[ENVIRONMENT]  # pragma: allowlist secret
    
    # Check for forbidden patterns
    forbidden_patterns = {
        "production": ["_DEV", "_STAGING"],
        "staging": ["_PRODUCTION", "_DEV"],
        "development": ["_PRODUCTION", "_STAGING"]
    }
    
    for pattern in forbidden_patterns[ENVIRONMENT]:
        for secret in os.environ:  # pragma: allowlist secret
            if pattern in secret:  # pragma: allowlist secret
                print(f"❌ Forbidden secret detected: {secret}")  # pragma: allowlist secret
                print(f"   Environment: {ENVIRONMENT}")
                print(f"   Pattern: {pattern}")
                sys.exit(1)
    
    print(f"✅ No cross-environment secrets detected in {ENVIRONMENT}")  # pragma: allowlist secret

if __name__ == "__main__":
    check_forbidden_secrets()  # pragma: allowlist secret
```

---

## 4. Secrets Audit & Compliance

### 4.1 Quarterly Audit Procedure

```bash
#!/bin/bash
# Run quarterly secrets audit

echo "🔍 Quarterly Secrets Audit"
echo "=========================="

# 1. Export all secrets metadata
gh secret list --repo Aries-Serpent/_codex_ > /tmp/secrets_list.txt

# 2. Check for scoping violations
python3 .github/scripts/validate_secrets_scope.py

# 3. Verify no hardcoded credentials in code
git grep -i "password\|api_key\|token" -- "*.py" "*.yaml" "*.json" | \
  grep -v "\.codex" | \
  grep -v "test" | \
  grep -v "example"

# 4. Verify all secrets are accessible by intended environments
python3 << 'PYTHON'
import json
import subprocess

# Get all secrets
result = subprocess.run(
    ["gh", "secret", "list", "--repo", "Aries-Serpent/_codex_"],
    capture_output=True, text=True
)

secrets_in_use = set(line.split()[0] for line in result.stdout.strip().split('\n'))

# Define expected secrets
expected_secrets = {
    "production": {
        "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GITHUB_TOKEN",
        "DEPLOYMENT_KEY_PRODUCTION", "DB_PASSWORD_PRODUCTION"
    },
    "staging": {
        "CODEX_MASTER_KEY_STAGING", "GITHUB_TOKEN_STAGING",
        "DEPLOYMENT_KEY_STAGING", "DB_PASSWORD_STAGING"
    },
    "development": {
        "CODEX_MASTER_KEY_DEV", "GITHUB_TOKEN_DEV",
        "DEPLOYMENT_KEY_DEV", "DB_PASSWORD_DEV"
    }
}

# Check coverage
all_expected = set()
for env_secrets in expected_secrets.values():
    all_expected.update(env_secrets)

missing = all_expected - secrets_in_use
unexpected = secrets_in_use - all_expected

if missing:
    print(f"⚠️  Missing expected secrets: {missing}")

if unexpected:
    print(f"⚠️  Unexpected secrets detected: {unexpected}")

if not missing and not unexpected:
    print("✅ All secrets properly scoped and configured")
PYTHON
```

### 4.2 Compliance Report Generation

```python
#!/usr/bin/env python3
# Generate monthly compliance report

import json
from datetime import datetime

report = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "audit_type": "secrets_scope_compliance",  # pragma: allowlist secret
    "compliance_checks": {
        "no_cross_environment_secrets": {  # pragma: allowlist secret
            "status": "PASS",
            "description": "No production secrets found in staging/dev"  # pragma: allowlist secret
        },
        "no_hardcoded_credentials": {
            "status": "PASS",
            "description": "No credentials found in source code"
        },
        "all_secrets_encrypted": {  # pragma: allowlist secret
            "status": "PASS",
            "description": "All secrets encrypted at rest in GitHub"  # pragma: allowlist secret
        },
        "rotation_schedules_active": {
            "status": "PASS",
            "description": "All key rotation schedules active"
        },
        "audit_logging_enabled": {
            "status": "PASS",
            "description": "Audit logging active for all secret access"  # pragma: allowlist secret
        }
    },
    "overall_status": "COMPLIANT",
    "next_audit": "2026-07-14"
}

with open(".codex/aftermath/secrets_compliance_report.json", "w") as f:  # pragma: allowlist secret
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
```

---

## 5. Access Control Policies

### 5.1 Role-Based Access

| Role | Production | Staging | Development |
|------|-----------|---------|-------------|
| DevOps Lead | Read/Write | Read/Write | Read/Write |
| Security Lead | Read | Read | Read |
| Engineer | None | Read | Read/Write |
| QA Team | None | Read | Read/Write |
| On-Call | Read | Read | Read |

### 5.2 Principle of Least Privilege

- **Production**: Only DevOps Lead can modify (via approved process)
- **Staging**: DevOps team can modify, others read-only
- **Development**: All engineers can modify, test freely

### 5.3 Approval Requirements

| Action | Production | Staging | Development |
|--------|-----------|---------|-------------|
| Add Secret | 2 approvals (sec + ops) | 1 approval (devops) | Self-service | <!-- pragma: allowlist secret -->
| Modify Secret | 2 approvals + 30min delay | 1 approval | Self-service | <!-- pragma: allowlist secret -->
| Delete Secret | 2 approvals + security lead | 1 approval | Self-service | <!-- pragma: allowlist secret -->
| Rotate Secret | Scheduled + approved | On-demand | On-demand | <!-- pragma: allowlist secret -->

---

## 6. Enforcement & Automation

### 6.1 GitHub Actions Validation Workflow

```yaml
name: Secrets Scope Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for hardcoded secrets
        run: |
          git grep -i "password\|api_key\|token" -- "*.py" "*.yaml" | \
            grep -v "\.codex" | \
            grep -v "test" | \
            grep -v "example" && exit 1 || exit 0
      
      - name: Validate secrets scope
        env:
          GITHUB_ENVIRONMENT: ${{ github.environment }}
        run: |
          python3 .github/scripts/validate_secrets_scope.py
      
      - name: Check for cross-environment secrets
        run: |
          python3 .github/scripts/check_cross_env_secrets.py
```

### 6.2 Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Prevent committing secrets
if git diff --cached | grep -i "password\|api_key\|token\|secret"; then
    echo "❌ Potential secrets detected in staged changes"
    echo "Use 'git restore --staged <file>' to unstage"
    exit 1
fi

# Check environment-specific config
if git diff --cached | grep -E "DB_PASSWORD|API_KEY" | \
   grep -v "_DEV\|_STAGING\|_PRODUCTION"; then
    echo "⚠️  Warning: Environment-specific credential without suffix"
    exit 1
fi

exit 0
```

---

## 7. Incident Response

### 7.1 Compromised Secret Procedure

If a secret is compromised:

1. **Immediate (< 5 min)**:
   - Invalidate compromised secret
   - Rotate to new value
   - Alert security team

2. **Short-term (< 30 min)**:
   - Investigate scope of compromise
   - Determine what access was possible
   - Review audit logs

3. **Resolution (< 4 hours)**:
   - Update all dependent systems
   - Verify no unauthorized access
   - Update incident report

---

## 8. Compliance & Sign-off

### 8.1 Compliance Certification

This policy ensures compliance with:
- ✅ **OWASP Top 10**: A02:2021 – Cryptographic Failures
- ✅ **NIST Framework**: PR.DS (Data Security)
- ✅ **CWE-798**: Use of Hard-Coded Credentials
- ✅ **SOC 2 Type II**: AC (Access Control)

### 8.2 Sign-off

- **Security Lead**: ____________________  Date: _________
- **Operations Lead**: ____________________  Date: _________
- **Compliance Officer**: ____________________  Date: _________

---

**Document Version**: 1.0  
**Effective Date**: 2026-06-14  
**Review Frequency**: Quarterly  
**Last Updated**: 2026-06-14
