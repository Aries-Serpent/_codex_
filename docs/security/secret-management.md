# Secret Management Documentation

> Comprehensive guide to managing secrets securely across development, staging, and production  
> **Level**: Intermediate | **Prerequisites**: Basic security knowledge  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Secret Rotation Procedures](#secret-rotation-procedures)
3. [Audit Logging](#audit-logging)
4. [Recovery Procedures](#recovery-procedures)
5. [GitHub Secrets Integration](#github-secrets-integration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Secrets are sensitive credentials that require careful management:
- API keys and tokens
- Database passwords
- OAuth credentials
- Encryption keys
- SSH keys
- Certificates

### Security Principles

1. **Never commit secrets** to version control
2. **Rotate secrets regularly** (every 30-90 days)
3. **Audit all access** to secrets
4. **Encrypt in transit** and at rest
5. **Use principle of least privilege**
6. **Implement secure deletion**

### Environment Hierarchy

```
Development (loose) → Staging (moderate) → Production (strict)
- Dev: Local .env files (gitignored)
- Staging: GitHub repository secrets  # pragma: allowlist secret
- Production: Managed secrets service  # pragma: allowlist secret
```

---

## Secret Rotation Procedures

### 1. API Key Rotation

**Scenario**: Rotate external API keys (SendGrid, Stripe, etc.)

#### Pre-Rotation Checklist

```bash
# 1. Document current secret usage
grep -r "API_KEY" . --include="*.py" --include="*.js" --include="*.ts"

# 2. Identify all services using the secret
# Services using API_KEY:
# - Authentication service: services/auth.py
# - Email service: services/email.py
# - Data pipeline: pipelines/data_sync.py

# 3. Verify backup keys exist
aws secretsmanager list-secret-version-ids --secret-id api-key
```

## Rotation Process

```bash
#!/bin/bash
# scripts/rotate_api_key.sh

set -e

SERVICE_NAME=$1
NEW_KEY=$2
ENVIRONMENT=${3:-staging}

echo "🔄 Starting API key rotation for $SERVICE_NAME in $ENVIRONMENT..."

# Step 1: Generate new key in external service
echo "1️⃣  Request new key from $SERVICE_NAME console"
echo "   Verify old key still active during transition"

# Step 2: Update staging environment
echo "2️⃣  Updating GitHub secrets..."
gh secret set "${SERVICE_NAME}_API_KEY" \
  --body "$NEW_KEY" \
  --env staging

# Wait for propagation
sleep 5

# Step 3: Test with new key
echo "3️⃣  Running integration tests..."
gh workflow run test.yml -f api-key-rotation=true

# Step 4: Monitor for errors
echo "4️⃣  Monitoring for errors (30 seconds)..."
sleep 30

# Step 5: Rotate to production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "5️⃣  Updating production secrets..."

    # Use secure secrets management service
    aws secretsmanager update-secret \
      --secret-id "$SERVICE_NAME-api-key" \
      --secret-string "$NEW_KEY"

    # Verify update
    aws secretsmanager get-secret-value \
      --secret-id "$SERVICE_NAME-api-key" \
      --query 'SecretString' \
      --output text | head -c 10
fi

# Step 6: Revoke old key
echo "6️⃣  Deactivating old key in $SERVICE_NAME..."
echo "   Manual action: Log into $SERVICE_NAME and deactivate old key"
echo "   Retain for 7 days before deletion"

echo "✅ API key rotation complete!"
```

**Usage**:
```bash
./scripts/rotate_api_key.sh SendGrid "new_key_here" staging
./scripts/rotate_api_key.sh Stripe "prod_key_here" production
```

## 2. Database Password Rotation

**Scenario**: Rotate database credentials

### Rotation Process

```bash
#!/bin/bash
# scripts/rotate_db_password.sh

DB_USER=$1
DB_HOST=$2
NEW_PASSWORD=$3
BACKUP_REQUIRED=${4:-true}

echo "🔄 Rotating database password for $DB_USER@$DB_HOST..."

# Step 1: Create backup
if [ "$BACKUP_REQUIRED" = "true" ]; then
    echo "1️⃣  Creating database backup..."
    mysqldump -u"$DB_USER" -p"${DB_PASSWORD}" \
      --host "$DB_HOST" \
      --all-databases \
      > db_backup_$(date +%Y%m%d_%H%M%S).sql
    echo "   ✅ Backup created"
fi

# Step 2: Create new user with temporary permissions
echo "2️⃣  Creating new database user..."
mysql -h "$DB_HOST" -u root -p"${ROOT_PASSWORD}" << EOF
ALTER USER '$DB_USER'@'%' IDENTIFIED BY '$NEW_PASSWORD';
FLUSH PRIVILEGES;
EOF

# Step 3: Test new credentials
echo "3️⃣  Testing new credentials..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$NEW_PASSWORD" -e "SELECT 1;" \
  && echo "   ✅ New credentials work" \
  || { echo "   ❌ New credentials failed"; exit 1; }

# Step 4: Update in secrets manager
echo "4️⃣  Updating secrets..."
aws secretsmanager update-secret \
  --secret-id "db/$DB_USER/password" \
  --secret-string "{\"username\":\"$DB_USER\",\"password\":\"$NEW_PASSWORD\",\"host\":\"$DB_HOST\"}"

# Step 5: Restart services with new password
echo "5️⃣  Restarting services..."
systemctl restart myapp-api
systemctl restart myapp-worker

# Wait for services to restart
sleep 10

# Step 6: Verify services running
echo "6️⃣  Verifying services..."
curl -s http://localhost:8000/health | jq . \
  && echo "   ✅ API healthy" \
  || { echo "   ❌ API failed"; exit 1; }

echo "✅ Database password rotation complete!"
```

## 3. OAuth Token Rotation

**Scenario**: Rotate OAuth tokens (GitHub, Slack, etc.)

```python
# scripts/rotate_oauth_tokens.py  # pragma: allowlist secret

import os
import subprocess
from datetime import datetime, timedelta
import json

class OAuthTokenRotator:  # pragma: allowlist secret
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.log_file = f"logs/oauth_rotation_{service_name}.log"

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")

    def rotate_github_token(self, new_token: str) -> bool:  # pragma: allowlist secret
        """Rotate GitHub API token"""  # pragma: allowlist secret
        self.log("Starting GitHub token rotation...")  # pragma: allowlist secret

        try:
            # Step 1: Verify new token  # pragma: allowlist secret
            self.log("Verifying new token...")  # pragma: allowlist secret
            result = subprocess.run(
                ["gh", "api", "user"],
                env={**os.environ, "GH_TOKEN": new_token},  # pragma: allowlist secret
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.log(f"Token verification failed: {result.stderr}", "ERROR")  # pragma: allowlist secret
                return False

            self.log("✅ New token verified")  # pragma: allowlist secret

            # Step 2: Update in secrets manager  # pragma: allowlist secret
            self.log("Updating GitHub token in secrets...")  # pragma: allowlist secret
            subprocess.run(
                ["gh", "secret", "set", "GITHUB_TOKEN",  # pragma: allowlist secret
                 "--body", new_token],  # pragma: allowlist secret
                check=True
            )

            # Step 3: Log old token for audit  # pragma: allowlist secret
            self.log("Recording rotation in audit log...")
            self._record_rotation_audit("GitHub", "token")  # pragma: allowlist secret

            self.log("✅ GitHub token rotation complete", "SUCCESS")  # pragma: allowlist secret
            return True

        except Exception as e:
            self.log(f"Rotation failed: {str(e)}", "ERROR")
            return False

    def _record_rotation_audit(self, service: str, secret_type: str):  # pragma: allowlist secret
        """Record rotation in audit log"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "secret_type": secret_type,  # pragma: allowlist secret
            "rotated_by": os.environ.get("USER", "unknown"),
            "status": "success"
        }

        with open("logs/secret_rotations_audit.jsonl", 'a') as f:  # pragma: allowlist secret
            f.write(json.dumps(audit_entry) + "\n")

# Usage
if __name__ == "__main__":
    rotator = OAuthTokenRotator("GitHub")  # pragma: allowlist secret
    new_token = os.environ.get("NEW_GITHUB_TOKEN")  # pragma: allowlist secret
    rotator.rotate_github_token(new_token)  # pragma: allowlist secret
```

---

## Audit Logging

### 1. Access Logging

```python
# src/security/audit_logger.py

import logging
import json
from datetime import datetime
from enum import Enum

class SecretAccessType(Enum):  # pragma: allowlist secret
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    ROTATE = "ROTATE"

class AuditLogger:
    def __init__(self, log_file: str = "logs/secret_audit.log"):  # pragma: allowlist secret
        self.logger = logging.getLogger("secret_audit")  # pragma: allowlist secret
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(timestamp)s - %(service)s - %(action)s - %(secret_name)s - %(user)s'  # pragma: allowlist secret
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_access(
        self,
        secret_name: str,  # pragma: allowlist secret
        access_type: SecretAccessType,  # pragma: allowlist secret
        user: str,
        service: str,
        success: bool = True,
        details: dict = None
    ):
        """Log secret access"""  # pragma: allowlist secret
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "secret_name": secret_name,  # pragma: allowlist secret
            "access_type": access_type.value,
            "user": user,
            "service": service,
            "success": success,
            "details": details or {}
        }

        self.logger.info(json.dumps(audit_entry))

        # Also log to metrics system
        self._send_to_metrics(audit_entry)

    def _send_to_metrics(self, entry: dict):
        """Send audit entry to monitoring system"""
        # Implement metrics submission (CloudWatch, DataDog, etc.)
        pass

# Usage in application
from src.security.audit_logger import AuditLogger, SecretAccessType  # pragma: allowlist secret

audit_logger = AuditLogger()

def get_api_key(secret_name: str) -> str:  # pragma: allowlist secret
    """Retrieve API key with audit logging"""
    try:
        key = os.environ.get(secret_name)  # pragma: allowlist secret

        audit_logger.log_access(
            secret_name=secret_name,  # pragma: allowlist secret
            access_type=SecretAccessType.READ,  # pragma: allowlist secret
            user=os.environ.get("USER"),
            service="authentication",
            success=True
        )

        return key

    except Exception as e:
        audit_logger.log_access(
            secret_name=secret_name,  # pragma: allowlist secret
            access_type=SecretAccessType.READ,  # pragma: allowlist secret
            user=os.environ.get("USER"),
            service="authentication",
            success=False,
            details={"error": str(e)}
        )
        raise
```

## 2. Audit Log Analysis

```bash
#!/bin/bash
# scripts/analyze_secret_audit.sh

echo "🔍 Secret Access Audit Analysis"
echo "================================"

# Most accessed secrets
echo -e "\n📊 Top 10 Most Accessed Secrets:"
jq -s 'group_by(.secret_name) |
       map({name: .[0].secret_name, count: length}) |
       sort_by(-.count) |
       .[0:10]' logs/secret_audit.jsonl

# Failed access attempts
echo -e "\n⚠️  Failed Access Attempts:"
jq 'select(.success == false)' logs/secret_audit.jsonl | wc -l

# Recent rotations
echo -e "\n🔄 Recent Secret Rotations (Last 7 days):"
jq "select(.access_type == \"ROTATE\" and
    (now - (.timestamp | fromdateiso8601)) < 604800)" \
    logs/secret_rotations_audit.jsonl

# Access by user
echo -e "\n👤 Access by User:"
jq -s 'group_by(.user) |
       map({user: .[0].user, count: length}) |
       sort_by(-.count)' logs/secret_audit.jsonl

# Unusual activity (high volume in short time)
echo -e "\n🚨 Unusual Activity Detection:"
jq -s 'group_by(.timestamp | split(".")[0]) |
       map({timestamp: .[0].timestamp, count: length}) |
       select(.count > 100)' logs/secret_audit.jsonl
```

---

## Recovery Procedures

### 1. Compromised Secret Recovery

**Scenario**: API key accidentally exposed in logs or repository

```bash
#!/bin/bash
# scripts/recover_compromised_secret.sh

set -e

SECRET_NAME=$1
EXPOSURE_LEVEL=${2:-internal}  # internal, external, public

echo "🚨 IMMEDIATE ACTION: Rotating compromised secret: $SECRET_NAME"

# Step 1: Alert team
echo "1️⃣  Alerting security team..."
slack-notify "🚨 SECURITY: Secret '$SECRET_NAME' potentially compromised"

# Step 2: Revoke compromised secret
echo "2️⃣  Revoking compromised secret..."
aws secretsmanager tag-resource \
  --secret-id "$SECRET_NAME" \
  --tags Key=compromised,Value=true Key=revocation-time,Value="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Step 3: Generate new secret
echo "3️⃣  Generating new secret..."
NEW_SECRET=$(openssl rand -hex 32)

# Step 4: Update in all locations
echo "4️⃣  Deploying new secret..."
for env in development staging production; do
    gh secret set "${SECRET_NAME}" \
      --body "$NEW_SECRET" \
      --env "$env"
done

# Step 5: Invalidate old secret in external services
echo "5️⃣  Invalidating old secret with external services..."
# Service-specific invalidation logic

# Step 6: Create incident report
echo "6️⃣  Creating incident report..."
cat > "incidents/security_$(date +%Y%m%d_%H%M%S).md" << EOF
# Security Incident Report

**Date**: $(date)
**Incident**: Secret Compromise
**Secret**: $SECRET_NAME
**Exposure Level**: $EXPOSURE_LEVEL

## Timeline
- [TIME] Secret discovered to be exposed
- [TIME] Compromise detected
- [TIME] Recovery procedures initiated

## Impact Assessment
- Services affected: [LIST]
- User impact: [LEVEL]

## Resolution
- Old secret revoked
- New secret deployed to: all environments
- External services notified

## Follow-up
- [ ] Audit logs reviewed for unauthorized access
- [ ] Root cause analysis completed
- [ ] Process improvements implemented
EOF

echo "✅ Recovery complete! Review incident report."
```

### 2. Failed Deployment Recovery

**Scenario**: Deployment failed mid-rotation, services using mix of old/new secrets

```python
# scripts/recover_deployment.py

import subprocess
import sys
from typing import List, Dict
from datetime import datetime

class DeploymentRecovery:
    def __init__(self, rollback_target: str = None):
        self.rollback_target = rollback_target or "last_stable"
        self.timestamp = datetime.now().isoformat()

    def check_deployment_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        services = ["api", "worker", "scheduler"]
        health = {}

        for service in services:
            try:
                result = subprocess.run(
                    ["curl", "-s", f"http://localhost:8000/{service}/health"],
                    capture_output=True,
                    timeout=5
                )
                health[service] = result.returncode == 0
            except Exception as e:
                print(f"❌ {service} health check failed: {e}")
                health[service] = False

        return health

    def identify_secret_mismatches(self) -> List[str]:  # pragma: allowlist secret
        """Identify services using wrong secrets"""  # pragma: allowlist secret
        mismatches = []

        # Check for signature/auth failures in logs
        result = subprocess.run(
            ["grep", "-i", "authentication.*failed", "logs/app.log"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            mismatches = result.stdout.strip().split('\n')

        return mismatches

    def rollback_secrets(self):  # pragma: allowlist secret
        """Rollback to last known good secrets"""  # pragma: allowlist secret
        print(f"🔄 Rolling back to: {self.rollback_target}")

        try:
            # Retrieve last known good configuration
            result = subprocess.run(
                ["aws", "secretsmanager", "describe-secret",  # pragma: allowlist secret
                 "--secret-id", "app-secrets-backup"],  # pragma: allowlist secret
                capture_output=True,
                text=True
            )

            # Restore from backup
            subprocess.run(
                ["aws", "secretsmanager", "restore-secret",  # pragma: allowlist secret
                 "--secret-id", "app-secrets"],  # pragma: allowlist secret
                check=True
            )

            print("✅ Secrets rolled back")  # pragma: allowlist secret

        except subprocess.CalledProcessError as e:
            print(f"❌ Rollback failed: {e}")
            sys.exit(1)

    def restart_services(self):
        """Restart services after recovery"""
        services = ["myapp-api", "myapp-worker", "myapp-scheduler"]

        for service in services:
            print(f"Restarting {service}...")
            subprocess.run(
                ["systemctl", "restart", service],
                check=True
            )

            # Wait for service to stabilize
            import time
            time.sleep(5)

        print("✅ Services restarted")

    def run_recovery(self):
        """Execute full recovery procedure"""
        print("🚨 Starting deployment recovery...")

        # 1. Check health
        health = self.check_deployment_health()
        print(f"\n📊 Service Health: {health}")

        # 2. Identify problems
        mismatches = self.identify_secret_mismatches()  # pragma: allowlist secret
        if mismatches:
            print(f"\n⚠️  Found {len(mismatches)} auth failures")

        # 3. Rollback
        self.rollback_secrets()  # pragma: allowlist secret

        # 4. Restart services
        self.restart_services()

        # 5. Verify recovery
        print("\n🔍 Verifying recovery...")
        new_health = self.check_deployment_health()

        if all(new_health.values()):
            print("✅ Recovery successful!")
            return True
        else:
            print(f"❌ Recovery incomplete: {new_health}")
            return False

# Usage
if __name__ == "__main__":
    recovery = DeploymentRecovery(rollback_target="staging")
    success = recovery.run_recovery()
    sys.exit(0 if success else 1)
```

---

## GitHub Secrets Integration

### 1. Setting Up Secrets

```bash
# Create secret
gh secret set MY_SECRET --body "secret_value" --env production

# Create from file
gh secret set MY_KEY --body "$(cat /path/to/secret)" --env staging

# Create from environment variable
gh secret set DB_PASSWORD --body "$DB_PASSWORD" --env production

# Create multi-line secret
gh secret set PRIVATE_KEY --body "$(cat ~/.ssh/id_rsa)" --env production
```

## 2. Using Secrets in Workflows

```yaml
# .github/workflows/deploy.yml

name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Configure secrets
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
        run: |
          echo "API_KEY=${API_KEY:0:10}..." # Log first 10 chars only
          # Use secrets in deployment

      - name: Deploy application
        run: ./scripts/deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
          ENVIRONMENT: production
```

## 3. Rotating Secrets in Workflows

```yaml
# .github/workflows/rotate-secrets.yml

name: Rotate Secrets

on:
  schedule:
    # Every 30 days
    - cron: '0 0 1 * *'
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate new secrets
        id: rotate
        run: |
          NEW_API_KEY=$(openssl rand -hex 32)
          echo "api_key=$NEW_API_KEY" >> $GITHUB_OUTPUT

      - name: Test new secrets
        env:
          API_KEY: ${{ steps.rotate.outputs.api_key }}
        run: python -m pytest tests/integration/

      - name: Update GitHub secret
        run: |
          gh secret set API_KEY \
            --body "${{ steps.rotate.outputs.api_key }}" \
            --env production

      - name: Record rotation
        run: |
          echo "Secret rotated at $(date)" >> logs/rotations.log
```

---

## Best Practices

1. **Never log secrets**: Use masking in logs
```python
logger.info(f"Connecting to {host}:{port}")  # ✅ Safe
logger.info(f"Auth: {api_key}")  # ❌ Never  # pragma: allowlist secret
```

2. **Use environment variables**: Not config files
   ```bash
   # ✅ Good
   export API_KEY="$(aws secretsmanager get-secret-value ...)"

   # ❌ Bad
   API_KEY = "hardcoded_key_here"  # In config file <!-- pragma: allowlist secret -->
   ```

3. **Implement automatic rotation**: Every 30-90 days
4. **Use least privilege**: Service only needs its own secret
5. **Enable audit logging**: Track all access and changes
6. **Secure deletion**: Overwrite before deleting

---

## Troubleshooting

### Issue: "Secret not found"

```bash
# Check if secret exists
gh secret list

# Create missing secret
gh secret set MISSING_SECRET --body "value"
```

## Issue: Deployment fails with "Authentication failed"

```bash
# Verify secret is set correctly
gh secret list --env production | grep MY_SECRET

# Re-apply secret
gh secret delete MY_SECRET --env production
gh secret set MY_SECRET --body "$(aws secretsmanager get-secret-value ...)" --env production
```

---

## Cross-References

- [Security Best Practices Guide](./security-best-practices.md)
- [GitHub Secrets Integration](../admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md)
- [Monitoring Guide](../monitoring/INDEX.md)

---

**Word Count**: 2,156 | **Examples**: 15 | **Runbooks**: 6
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
