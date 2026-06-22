# HMAC Key Rotation Runbook

**Document**: `docs/ops/HMAC_rotation.md`
**Version**: 1.0
**Status**: Production Readiness — Phase 4
**Owner**: Security Engineering
**Last Updated**: 2026-06-22

---

## Overview

The `QuantumAuditTrail` uses HMAC-SHA256 to chain audit entries cryptographically,
providing tamper-evidence for SOX/GDPR compliance. This runbook describes the key
lifecycle — provisioning, rotation, and emergency revocation — using AWS KMS
(or equivalent cloud KMS).

**Key principle**: The HMAC key is never committed to source control. It must be
injected at runtime via a secrets manager.

---

## Environment Variable

| Variable | Description | Default |
|----------|-------------|---------|
| `CODEX_AUDIT_HMAC_KEY` | HMAC-SHA256 key for audit chain | `""` (SHA-256 fallback) |

> ⚠️ When `CODEX_AUDIT_HMAC_KEY` is empty, entries are chained via SHA-256 only
> (no secret key — not cryptographically tamper-proof). Always set this in
> production.

---

## Initial Provisioning

### 1. Generate the key in AWS KMS

```bash
# Create a symmetric key in KMS (AES-256)
aws kms create-key \
  --description "CODEX Audit Trail HMAC Key" \
  --key-usage GENERATE_VERIFY_MAC \
  --key-spec HMAC_256 \
  --tags TagKey=Project,TagValue=QuantumCompliance \
           TagKey=Environment,TagValue=production

# Note the returned KeyId (e.g., "1234abcd-12ab-34cd-56ef-1234567890ab")
```

## 2. Store in AWS Secrets Manager

```bash
# Generate a 256-bit secret value
HMAC_KEY=$(openssl rand -base64 32)

# Store in Secrets Manager
aws secretsmanager create-secret \
  --name "codex/audit/hmac_key" \
  --description "QuantumAuditTrail HMAC key for tamper-evident chain" \
  --secret-string "$HMAC_KEY" \
  --kms-key-id "alias/codex-audit-hmac"
```

## 3. Grant access to the runtime role

```bash
aws secretsmanager put-resource-policy \
  --secret-id "codex/audit/hmac_key" \
  --resource-policy '{
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::ACCOUNT_ID:role/codex-runtime"},
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "*"
    }]
  }'
```

### 4. Inject at runtime (application bootstrap)

```python
import boto3, os

def load_hmac_key() -> str:
    """Load HMAC key from Secrets Manager at startup."""
    client = boto3.client("secretsmanager", region_name="eu-west-1")
    response = client.get_secret_value(SecretId="codex/audit/hmac_key")
    return response["SecretString"]

os.environ["CODEX_AUDIT_HMAC_KEY"] = load_hmac_key()
```

---

## Rotation Schedule

| Environment | Rotation Frequency | Method |
|-------------|-------------------|--------|
| Production  | Every 90 days     | Automatic via KMS rotation policy |
| Staging     | Every 180 days    | Manual or automatic |
| Development | Not required      | SHA-256 fallback acceptable |

### Enable automatic rotation in KMS

```bash
aws secretsmanager rotate-secret \
  --secret-id "codex/audit/hmac_key" \
  --rotation-rules AutomaticallyAfterDays=90
```

---

## Key Rotation Procedure (Manual)

### Step 1: Generate new key

```bash
NEW_KEY=$(openssl rand -base64 32)
ROTATION_DATE=$(date +%Y%m%d)
```

### Step 2: Create versioned secret

```bash
aws secretsmanager put-secret-value \
  --secret-id "codex/audit/hmac_key" \
  --secret-string "$NEW_KEY" \
  --version-stages AWSPENDING
```

### Step 3: Archive existing audit log

Before switching keys, export and archive the current audit log with the old key:

```bash
# Archive current log with old key signature
python - <<'EOF'
from cognitive_brain.integrations.compliance_integration import QuantumAuditTrail
import json, datetime

trail = QuantumAuditTrail(hmac_key=old_key)
entries = trail.query()
archive = {
    "archived_at": datetime.datetime.utcnow().isoformat() + "Z",
    "key_rotation": True,
    "entry_count": len(entries),
    "entries": [vars(e) for e in entries]
}
with open(f"audit_archive_{datetime.date.today()}.json", "w") as f:
    json.dump(archive, f, indent=2)
EOF
```

## Step 4: Promote new key version

```bash
aws secretsmanager update-secret-version-stage \
  --secret-id "codex/audit/hmac_key" \
  --version-stage AWSCURRENT \
  --move-to-version-id "$NEW_VERSION_ID" \
  --remove-from-version-id "$OLD_VERSION_ID"
```

### Step 5: Restart application and validate

```bash
# Restart runtime with new key
systemctl restart codex-compliance

# Verify chain starts fresh with new key
python -c "
from cognitive_brain.integrations.compliance_integration import QuantumAuditTrail
import os
trail = QuantumAuditTrail(hmac_key=os.environ['CODEX_AUDIT_HMAC_KEY'])
print('Audit trail initialised with rotated key')
"
```

---

## Emergency Revocation

If the HMAC key is compromised:

1. **Immediately** revoke in KMS:
   ```bash
   aws kms disable-key --key-id "alias/codex-audit-hmac"
   ```

2. Generate emergency replacement key and update Secrets Manager.

3. Mark all entries since compromise timestamp as `CHAIN_INTEGRITY_UNKNOWN`:
   ```bash
   python scripts/audit/mark_compromised_window.py \
     --from "2026-02-18T12:00:00Z" \
     --reason "Key compromise — chain integrity unverified"
   ```

4. Notify Compliance and Legal teams within 72 hours (GDPR Art. 33).

5. Re-run audit trail integrity check with new key.

---

## Integrity Verification

To verify audit chain integrity for a date range:

```python
from cognitive_brain.integrations.compliance_integration import QuantumAuditTrail
import hashlib, hmac as hmac_lib, os

key = os.environ["CODEX_AUDIT_HMAC_KEY"].encode()
trail = QuantumAuditTrail(hmac_key=os.environ["CODEX_AUDIT_HMAC_KEY"])
entries = trail.query()

prev_hash = ""
for entry in entries:
    # Recompute expected chain hash
    chain_input = f"{prev_hash}|{entry.input_hash}|{entry.decision}"
    expected = hmac_lib.new(key, chain_input.encode(), hashlib.sha256).hexdigest()[:16]
    if expected != entry.chain_hash:
        print(f"INTEGRITY FAILURE at entry {entry.entry_id}")
        break
    prev_hash = entry.chain_hash
else:
    print("All entries verified — chain intact")
```

---

## SOX / GDPR Compliance Notes

| Requirement | Implementation |
|-------------|---------------|
| SOX Section 302/404 | Immutable audit trail with tamper-evidence |
| GDPR Art. 5(1)(f) | HMAC chain ensures integrity of personal data processing records |
| GDPR Art. 17 (Right to Erasure) | Retention policy configurable; 7-year default for financial compliance |
| Audit retention | 2555 days (~7 years) — configurable in `QuantumAuditTrail(retention_days=...)` |

> **Production Note**: The in-memory `QuantumAuditTrail` must be persisted to
> an append-only WORM store (e.g., AWS S3 Object Lock, Azure Immutable Blob
> Storage) before process restart to satisfy SOX/GDPR retention requirements.
