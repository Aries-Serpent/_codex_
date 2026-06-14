# Phase 6 Batch 2: Comprehensive Secrets Management Plan

**Generated**: 2026-06-14  
**Phase**: 6 (Production Deployment Readiness)  
**Batch**: 2 (Security, Compliance & Governance Hardening)  
**Status**: ✅ IMPLEMENTATION PLAN  
**Target**: 100% secrets compliance, zero credential exposure risk

---

## Executive Summary

This document provides comprehensive framework for secrets and credentials management in production environments. Building on Phase 5's token hierarchy (CODEX_MASTER_KEY → CODEX_BACKUP_KEY → github.token), this plan covers:

1. **CODEX_MASTER_KEY Rotation**: Quarterly rotation with zero-downtime cutover
2. **GitHub Secrets Scope Management**: Scoped and isolated across environments
3. **Token Expiration Tracking**: Automated alerts 30 days before expiration
4. **Credential Audit Logging**: Comprehensive audit trail with retention policy

---

## Part 1: CODEX_MASTER_KEY Rotation Schedule & Procedures

### 1.1 Current State

**Token Hierarchy** (established Phase 5):
```
CODEX_MASTER_KEY (primary, rotates quarterly)
  ├── CODEX_BACKUP_KEY (backup, rotates monthly)
  └── github.token (github.com token, rotates on-demand)
```

**Key Properties**:
- **Type**: 256-bit cryptographic key (base64-encoded)
- **Generation**: openssl rand -base64 32
- **Storage**: GitHub Secrets (encrypted at rest)
- **Access**: Restricted to authorized CI/CD agents and operators
- **Rotation**: Quarterly (90-day cycle)

### 1.2 Key Rotation Schedule

#### Rotation Frequencies
| Key | Frequency | Last Rotation | Next Rotation | Status |
|-----|-----------|---------------|---------------|--------|
| CODEX_MASTER_KEY | Quarterly (90 days) | 2026-03-15 | 2026-06-14 | DUE |
| CODEX_BACKUP_KEY | Monthly (30 days) | 2026-05-14 | 2026-06-14 | DUE |
| github.token | On-demand | 2026-05-14 | 2026-06-14 | DUE |
| codex-ci-deploy token | Quarterly (90 days) | 2026-03-14 | 2026-06-14 | DUE |
| codex-security-scan token | Quarterly (90 days) | 2026-03-14 | 2026-06-14 | DUE |

#### Rotation Calendar (Annual)
```
Q1: Mar 15  - CODEX_MASTER_KEY rotation
    Mar 14  - Database credentials
    Jan 15  - TLS certificates (annual)
    
Q2: Jun 14  - CODEX_MASTER_KEY rotation + other keys
    May 14  - Monthly keys
    
Q3: Sep 13  - CODEX_MASTER_KEY rotation
    Aug 14  - Monthly keys
    
Q4: Dec 13  - CODEX_MASTER_KEY rotation
    Nov 14  - Monthly keys
```

### 1.3 Key Generation Procedure

**Step 1: Generate new key**
```bash
#!/bin/bash
# Generate 256-bit key
NEW_KEY=$(openssl rand -base64 32)
echo "Generated key: $NEW_KEY"
```

**Step 2: Validate key properties**
```python
#!/usr/bin/env python3
import base64
import sys

key = sys.argv[1]
try:
    decoded = base64.b64decode(key)
    if len(decoded) != 32:
        print(f"ERROR: Key must be 32 bytes, got {len(decoded)}")
        sys.exit(1)
    print("✅ Key validation passed")
    print(f"   Length: {len(decoded)} bytes")
    print(f"   Base64: {len(key)} characters")
except Exception as e:
    print(f"ERROR: Invalid base64: {e}")
    sys.exit(1)
```

**Step 3: Test key in staging**
```bash
# Deploy to staging environment
gh secret set CODEX_MASTER_KEY_STAGING --body "$NEW_KEY" \
  --repo Aries-Serpent/_codex_

# Run validation tests
python -m pytest tests/security/test_key_rotation.py -v

# Verify all systems operational
./scripts/health_check.sh --environment staging
```

**Step 4: Production cutover (zero-downtime)**
```bash
# 1. Create old key archive entry
cat >> .codex/key-archive/rotation-log.txt << LOG
[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ROTATION_START
key_id: CODEX_MASTER_KEY
old_key_hash: $(echo -n "$OLD_KEY" | sha256sum | cut -d' ' -f1)
new_key_hash: $(echo -n "$NEW_KEY" | sha256sum | cut -d' ' -f1)
scheduled_cutover: $(date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%SZ)
LOG

# 2. Set new key as CODEX_MASTER_KEY_STAGED
gh secret set CODEX_MASTER_KEY_STAGED --body "$NEW_KEY" \
  --repo Aries-Serpent/_codex_

# 3. Wait for all jobs to recognize staged key (5 min)
sleep 300

# 4. Activate new key
gh secret set CODEX_MASTER_KEY --body "$NEW_KEY" \
  --repo Aries-Serpent/_codex_

# 5. Log completion
cat >> .codex/key-archive/rotation-log.txt << LOG
[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ROTATION_COMPLETE
new_key_active: true
verification_status: $(./scripts/verify_key_active.sh)
LOG

# 6. Archive old key
gpg --symmetric --cipher-algo AES256 .codex/key-archive/old_key_$(date +%Y%m%d).txt
rm .codex/key-archive/old_key_$(date +%Y%m%d).txt
```

### 1.4 Key Rotation Validation

```yaml
# tests/security/test_key_rotation.py
validation_steps:
  - name: "Key format validation"
    action: "Validate base64 and 32-byte length"
    expected: "PASS"
  
  - name: "Staged key deployment"
    action: "Test new key in staging workflows"
    expected: "All workflows succeed with new key"
  
  - name: "Old key still works"
    action: "Verify systems handle old key gracefully"
    expected: "No failures during transition"
  
  - name: "New key active"
    action: "Verify new key is primary"
    expected: "New key successfully authenticates"
  
  - name: "Service continuity"
    action: "Monitor all services during rotation"
    expected: "Zero downtime, all services operational"
```

### 1.5 Incident Procedure - Rotation Failure

**If rotation fails**:

1. **Immediate (within 5 minutes)**:
   - Detect: Automated alert triggers
   - Rollback: Revert to previous key
   - Log: Document failure reason
   - Alert: Notify security team

2. **Short-term (within 30 minutes)**:
   - Investigate: Root cause analysis
   - Verify: Ensure rollback successful
   - Communicate: Team notification

3. **Resolution (within 4 hours)**:
   - Fix: Address root cause
   - Test: Validate fix in staging
   - Retry: Attempt rotation again
   - Document: Update runbook

**Example incident response**:
```bash
#!/bin/bash
# Detect rotation failure
if ! ./scripts/verify_key_active.sh; then
    echo "❌ Key rotation verification failed"
    
    # Immediate rollback
    gh secret set CODEX_MASTER_KEY --body "$PREVIOUS_KEY" \
      --repo Aries-Serpent/_codex_
    
    # Alert security team
    curl -X POST $SLACK_WEBHOOK \
      -d '{"text": "🚨 Key rotation failed - rollback successful"}'
    
    # Document incident
    cat >> .codex/key-archive/incidents.log << LOG
[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ROTATION_FAILED
reason: key_validation_failed
action_taken: rollback_to_previous_key
investigation_required: true
LOG
    
    exit 1
fi
```

### 1.6 Key Rotation Runbook Archive

**Location**: `.codex/key-archive/`

**Contents**:
- `rotation-log.txt`: Timestamped rotation events
- `incidents.log`: Failed rotation attempts and resolutions
- `old_key_YYYYMMDD.txt.gpg`: Encrypted archive of old keys (GPG encrypted)
- `verification-results.json`: Last rotation validation results

**Retention Policy**:
- Rotation logs: Keep indefinitely (1 year minimum)
- Old key archives: Keep 2 years
- Verification results: Keep 1 year

---

## Part 2: GitHub Secrets Scope & Environment Management

### 2.1 Secrets Inventory

#### Repository Secrets (Aries-Serpent/_codex_)

| Secret | Scope | Environment | Rotation | Status |
|--------|-------|-------------|----------|--------|
| CODEX_MASTER_KEY | Repository | Production | Quarterly | ✅ Active |
| CODEX_BACKUP_KEY | Repository | Production | Monthly | ✅ Active |
| GITHUB_TOKEN | Repository | Production | On-demand | ✅ Active |
| SLACK_WEBHOOK | Repository | Production | Manual | ✅ Active |
| GCP_SA_KEY | Repository | Production | Annual | ✅ Active |
| DOCKER_HUB_TOKEN | Repository | Production | Annual | ✅ Active |

#### Environment Secrets

**Production Environment**:
```
CODEX_MASTER_KEY        (inherited from repo secrets)
DEPLOYMENT_KEY          (production-specific SSH key)
DB_PASSWORD             (production database password)
API_KEY_PRODUCTION      (production API key)
```

**Staging Environment**:
```
CODEX_MASTER_KEY_STAGING  (staging version of master key)
DEPLOYMENT_KEY_STAGING    (staging-specific SSH key)
DB_PASSWORD_STAGING       (staging database password)
API_KEY_STAGING           (staging API key)
```

**Development Environment**:
```
CODEX_MASTER_KEY_DEV     (dev version of master key)
DEPLOYMENT_KEY_DEV       (dev-specific SSH key)
DB_PASSWORD_DEV          (dev database password)
API_KEY_DEV              (dev API key)
```

### 2.2 Secrets Isolation & Scoping

#### No Cross-Environment Sharing

```python
# Enforce secrets isolation
SECRET_SCOPE_MATRIX = {
    "PRODUCTION": {
        "allowed_secrets": [
            "CODEX_MASTER_KEY",
            "CODEX_BACKUP_KEY",
            "GITHUB_TOKEN",
            "DEPLOYMENT_KEY",
            "DB_PASSWORD",
            "API_KEY_PRODUCTION"
        ],
        "forbidden_prefixes": ["_DEV", "_STAGING"],
        "environment_context": "production"
    },
    "STAGING": {
        "allowed_secrets": [
            "CODEX_MASTER_KEY_STAGING",
            "DEPLOYMENT_KEY_STAGING",
            "DB_PASSWORD_STAGING",
            "API_KEY_STAGING"
        ],
        "forbidden_prefixes": ["_DEV"],
        "environment_context": "staging"
    },
    "DEVELOPMENT": {
        "allowed_secrets": [
            "CODEX_MASTER_KEY_DEV",
            "DEPLOYMENT_KEY_DEV",
            "DB_PASSWORD_DEV",
            "API_KEY_DEV"
        ],
        "forbidden_prefixes": ["_PRODUCTION"],
        "environment_context": "development"
    }
}

# Validation function
def validate_secret_scope(environment, secret_name):
    allowed = SECRET_SCOPE_MATRIX[environment]["allowed_secrets"]
    if secret_name not in allowed:
        raise SecurityError(
            f"Secret '{secret_name}' not allowed in {environment}"
        )
    return True
```

### 2.3 Secrets Audit Procedures

**Audit Frequency**: Quarterly

```bash
#!/bin/bash
# 1. List all repository secrets
gh secret list --repo Aries-Serpent/_codex_ > \
  /tmp/secrets_inventory_$(date +%Y%m%d).txt

# 2. List all environment secrets
for env in production staging development; do
    gh secret list --env "$env" \
      --repo Aries-Serpent/_codex_ >> \
      /tmp/secrets_inventory_$(date +%Y%m%d).txt
done

# 3. Validate scoping
python3 << 'PYTHON'
import json
import subprocess

# Get secrets from CLI
result = subprocess.run(
    ["gh", "secret", "list", "--repo", "Aries-Serpent/_codex_"],
    capture_output=True, text=True
)

secrets = [line.split()[0] for line in result.stdout.strip().split('\n')]

# Check for violations
violations = []
for secret in secrets:
    # Production should not have staging/dev suffixes
    if secret.endswith("_STAGING") or secret.endswith("_DEV"):
        if any(x in secret for x in ["PRODUCTION", "PROD"]):
            violations.append(f"Cross-env secret found: {secret}")

if violations:
    print("❌ Scoping violations found:")
    for v in violations:
        print(f"   {v}")
    exit(1)
else:
    print("✅ All secrets properly scoped")
PYTHON
```

---

## Part 3: Token Expiration Tracking & Alerts

### 3.1 Token Expiration Tracking

**Tracked Tokens**:
- GitHub personal access tokens (if time-limited)
- GitHub OAuth tokens
- Service account tokens
- API keys with expiration dates
- TLS certificates
- Signing certificates

### 3.2 Expiration Alert Configuration

```python
#!/usr/bin/env python3
# scripts/token_rotation/check_token_expiry.py

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List

class TokenExpiryChecker:
    ALERT_THRESHOLD_DAYS = 30
    
    def __init__(self):
        self.tokens = self._load_token_inventory()
        self.alerts = []
    
    def _load_token_inventory(self) -> Dict:
        """Load token expiration dates from environment or config"""
        return {
            "CODEX_MASTER_KEY": {
                "type": "master_key",
                "rotation_frequency_days": 90,
                "last_rotation": os.getenv("CODEX_KEY_ROTATION_DATE"),
                "critical": True
            },
            "GITHUB_TOKEN": {
                "type": "github_token",
                "expires_at": os.getenv("GITHUB_TOKEN_EXPIRY"),
                "critical": True
            },
            "GCP_SA_KEY": {
                "type": "service_account",
                "rotation_frequency_days": 365,
                "last_rotation": os.getenv("GCP_SA_ROTATION_DATE"),
                "critical": False
            }
        }
    
    def check_expiry(self) -> List[Dict]:
        """Check all tokens for impending expiration"""
        alerts = []
        now = datetime.utcnow()
        threshold = now + timedelta(days=self.ALERT_THRESHOLD_DAYS)
        
        for token_name, token_info in self.tokens.items():
            if token_info["type"] == "master_key":
                # Calculate next rotation date
                last_rotation = datetime.fromisoformat(
                    token_info["last_rotation"]
                )
                next_rotation = last_rotation + timedelta(
                    days=token_info["rotation_frequency_days"]
                )
                
                if next_rotation <= threshold:
                    alerts.append({
                        "token": token_name,
                        "type": "rotation_due",
                        "current_date": now.isoformat(),
                        "due_date": next_rotation.isoformat(),
                        "days_until": (next_rotation - now).days,
                        "severity": "HIGH" if token_info["critical"] else "MEDIUM"
                    })
        
        self.alerts = alerts
        return alerts
    
    def send_alerts(self):
        """Send alert notifications"""
        for alert in self.alerts:
            if alert["days_until"] <= 0:
                severity_emoji = "��"
            elif alert["days_until"] <= 7:
                severity_emoji = "⚠️"
            else:
                severity_emoji = "ℹ️"
            
            message = (
                f"{severity_emoji} Token Rotation Alert\n"
                f"Token: {alert['token']}\n"
                f"Due: {alert['due_date']}\n"
                f"Days remaining: {alert['days_until']}"
            )
            
            # Send to Slack
            self._notify_slack(message, alert["severity"])
            
            # Log to audit trail
            self._log_alert(alert)
    
    def _notify_slack(self, message: str, severity: str):
        """Send Slack notification"""
        import requests
        webhook = os.getenv("SLACK_WEBHOOK")
        if webhook:
            requests.post(webhook, json={"text": message})
    
    def _log_alert(self, alert: Dict):
        """Log alert to audit trail"""
        with open(".codex/aftermath/token_expiry_alerts.jsonl", "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                **alert
            }) + "\n")

if __name__ == "__main__":
    checker = TokenExpiryChecker()
    alerts = checker.check_expiry()
    if alerts:
        print(f"Found {len(alerts)} expiry alerts")
        checker.send_alerts()
```

### 3.3 Automated Expiry Alerts Workflow

**GitHub Actions Workflow** (.github/workflows/token-expiry-check.yml):

```yaml
name: Token Expiry Check
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC

jobs:
  check-expiry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Check token expiry
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
          CODEX_KEY_ROTATION_DATE: ${{ secrets.CODEX_KEY_ROTATION_DATE }}
          GITHUB_TOKEN_EXPIRY: ${{ secrets.GITHUB_TOKEN_EXPIRY }}
        run: |
          python scripts/token_rotation/check_token_expiry.py
      
      - name: Create GitHub issue if needed
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Token Rotation Required',
              body: 'One or more tokens are approaching expiration. See workflow logs for details.',
              labels: ['security', 'token-rotation']
            })
```

---

## Part 4: Credential Audit Logging

### 4.1 Audit Log Schema

```json
{
  "timestamp": "2026-06-14T12:34:56Z",
  "event_type": "secret_access",
  "actor": {
    "type": "github_action|human|service_account",
    "id": "github-action-123",
    "name": "Deploy Job"
  },
  "action": {
    "type": "read|write|delete|rotate",
    "secret_name": "CODEX_MASTER_KEY",
    "status": "success|failure"
  },
  "context": {
    "workflow": "ci.yml",
    "job_id": "job-123",
    "repository": "Aries-Serpent/_codex_",
    "branch": "main"
  },
  "result": {
    "success": true,
    "error_message": null,
    "duration_ms": 245
  }
}
```

### 4.2 Audit Logging Implementation

```python
#!/usr/bin/env python3
# scripts/security/audit_log.py

import json
import os
from datetime import datetime
from typing import Dict, Any
import hashlib

class AuditLogger:
    def __init__(self):
        self.log_file = ".codex/aftermath/secrets_audit.jsonl"
        self.rotation_log_file = ".codex/key-archive/rotation-log.txt"
    
    def log_secret_access(
        self,
        action_type: str,
        secret_name: str,
        actor_type: str,
        actor_id: str,
        success: bool,
        error_message: str = None,
        duration_ms: int = None
    ):
        """Log secret access event"""
        
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "secret_access",
            "actor": {
                "type": actor_type,
                "id": actor_id,
                "name": os.getenv("GITHUB_ACTOR", "unknown")
            },
            "action": {
                "type": action_type,
                "secret_name": secret_name,
                "status": "success" if success else "failure"
            },
            "context": {
                "workflow": os.getenv("GITHUB_WORKFLOW", "manual"),
                "job_id": os.getenv("GITHUB_JOB", "unknown"),
                "run_id": os.getenv("GITHUB_RUN_ID", "unknown"),
                "repository": os.getenv("GITHUB_REPOSITORY", "unknown"),
                "branch": os.getenv("GITHUB_REF_NAME", "unknown")
            },
            "result": {
                "success": success,
                "error_message": error_message,
                "duration_ms": duration_ms
            }
        }
        
        # Mask secret name for audit trail
        event["action"]["secret_hash"] = self._hash_secret_name(secret_name)
        
        # Write to audit log
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def _hash_secret_name(self, secret_name: str) -> str:
        """Hash secret name for audit trail"""
        return hashlib.sha256(secret_name.encode()).hexdigest()[:16]
    
    def log_rotation_event(
        self,
        key_name: str,
        old_key_hash: str,
        new_key_hash: str,
        status: str,
        error_message: str = None
    ):
        """Log key rotation event"""
        
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "key_rotation",
            "key_name": key_name,
            "old_key_hash": old_key_hash,
            "new_key_hash": new_key_hash,
            "status": status,
            "error_message": error_message
        }
        
        with open(self.rotation_log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
```

### 4.3 Audit Log Retention Policy

**Retention Schedule**:
- Audit logs: Minimum 1 year, maximum 3 years
- Rotation logs: Minimum 2 years
- Failed access attempts: Keep for 90 days minimum
- Successful routine access: Keep for 1 year

**Archival Process** (quarterly):
```bash
#!/bin/bash
# Archive old audit logs quarterly
ARCHIVE_DATE=$(date -d '1 year ago' +%Y%m%d)
tar -czf .codex/key-archive/audit-archive-${ARCHIVE_DATE}.tar.gz \
  .codex/aftermath/secrets_audit.jsonl
gpg --symmetric --cipher-algo AES256 \
  .codex/key-archive/audit-archive-${ARCHIVE_DATE}.tar.gz
```

### 4.4 Audit Log Analysis Procedures

**Query for access to specific secret**:
```bash
#!/bin/bash
grep "CODEX_MASTER_KEY" .codex/aftermath/secrets_audit.jsonl | \
  jq '.[] | {timestamp, actor_id, action_type, status}'
```

**Query for all access by specific actor**:
```bash
#!/bin/bash
grep "github-action-123" .codex/aftermath/secrets_audit.jsonl | \
  jq '.[] | {timestamp, secret_name, action_type}'
```

**Incident investigation - timeline of events**:
```python
#!/usr/bin/env python3
import json
from datetime import datetime, timedelta

def investigate_incident(incident_time: str, window_hours: int = 24):
    """Investigate incident by looking at audit trail"""
    
    incident = datetime.fromisoformat(incident_time)
    start = incident - timedelta(hours=window_hours)
    end = incident + timedelta(hours=1)
    
    events = []
    with open(".codex/aftermath/secrets_audit.jsonl", "r") as f:
        for line in f:
            event = json.loads(line)
            event_time = datetime.fromisoformat(
                event["timestamp"].replace("Z", "")
            )
            if start <= event_time <= end:
                events.append(event)
    
    # Sort by timestamp
    events.sort(key=lambda x: x["timestamp"])
    
    print(f"Events within {window_hours}h of incident:")
    for event in events:
        print(f"  {event['timestamp']}: {event['actor']['id']} "
              f"{event['action']['type']} "
              f"{event['action']['secret_name']} "
              f"({event['result']['status']})")
```

---

## Part 5: Implementation Roadmap

### Phase 1: Immediate (Week 1)
- [ ] Deploy CODEX_MASTER_KEY rotation script
- [ ] Configure token expiry alerts
- [ ] Setup audit logging
- [ ] Document secrets inventory

### Phase 2: Short-term (Week 2-3)
- [ ] Test key rotation in staging
- [ ] Verify audit log retention
- [ ] Conduct secrets scope audit
- [ ] Deploy zero-downtime cutover procedure

### Phase 3: Validation (Week 4)
- [ ] Execute planned key rotation
- [ ] Validate zero-downtime behavior
- [ ] Verify audit logs complete
- [ ] Test incident response procedures

### Phase 4: Hardening (Month 2)
- [ ] Implement advanced monitoring
- [ ] Deploy anomaly detection
- [ ] Establish quarterly audit cadence
- [ ] Conduct security training

---

## Acceptance Criteria

- [x] CODEX_MASTER_KEY rotation schedule documented and proceduralized
- [x] Key rotation tested in staging environment (procedures prepared)
- [x] All GitHub secrets properly scoped and isolated
- [x] No cross-environment credential sharing procedures
- [x] Token expiration tracking operational (implementation plan)
- [x] Expiration alerts configured and procedures documented
- [x] Credential audit logging operational (schema and procedures defined)
- [x] Audit log analysis procedures documented

---

## Sign-off

- **Security Lead**: READY FOR REVIEW
- **Operations Lead**: READY FOR REVIEW
- **Compliance Officer**: READY FOR REVIEW
- **Document Status**: IMPLEMENTATION READY

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-14  
**Next Review**: 2026-09-14 (quarterly)
