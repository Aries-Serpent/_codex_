# Secret Rotation Policy

**Version**: 1.0.0  
**Effective Date**: 2026-06-14  
**Classification**: Internal — Security Sensitive  
**Owner**: Security Team  
**Last Updated**: 2026-06-14

---

## Table of Contents

1. [Policy Overview](#policy-overview)
2. [Rotation Schedule](#rotation-schedule)
3. [Procedures by Secret Type](#procedures-by-secret-type)
4. [Rotation Process](#rotation-process)
5. [Emergency Rotation](#emergency-rotation)
6. [Monitoring & Compliance](#monitoring--compliance)
7. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Policy Overview

### Purpose

This policy establishes mandatory rotation schedules and procedures for all secrets used in the _codex_ system, including encryption keys, authentication credentials, and API tokens. Regular rotation minimizes the impact of potential credential compromise.

### Scope

This policy applies to:
- All secrets managed by the _codex_ platform
- CI/CD infrastructure and workflows
- Production deployments
- Development and staging environments (at reduced frequency)

### Principles

1. **Least Exposure**: Minimize secret lifespan
2. **Automated Rotation**: Reduce manual error
3. **Graceful Migration**: Support dual-key periods during rotation
4. **Audit Trail**: Record all rotation events
5. **Emergency Response**: Immediate rotation capability for compromised secrets

---

## Rotation Schedule

### Master Schedule

| Secret Type | Frequency | Last Rotated | Next Rotation | Emergency Window | <!-- pragma: allowlist secret -->
|---|---|---|---|---|
| CODEX_MASTER_KEY | Quarterly | 2026-03-15 | 2026-06-15 | Immediate |
| GitHub OAuth Token | Monthly | 2026-05-14 | 2026-06-14 | 4 hours | <!-- pragma: allowlist secret -->
| Database Credentials | Quarterly | 2026-03-14 | 2026-06-14 | 24 hours |
| API Keys (External) | Monthly | 2026-05-14 | 2026-06-14 | 4 hours |
| JWT Signing Key | Quarterly | 2026-03-14 | 2026-06-14 | 12 hours |
| TLS Certificates | Annually | 2026-01-15 | 2027-01-15 | 48 hours |
| Service Account Tokens | Monthly | 2026-05-14 | 2026-06-14 | 4 hours | <!-- pragma: allowlist secret -->
| Webhook Signing Keys | Quarterly | 2026-03-14 | 2026-06-14 | 12 hours |

### Frequency Rationale

- **Quarterly (90 days)**: Master keys, authentication keys, long-lived service tokens
- **Monthly (30 days)**: GitHub tokens, API keys, frequent-access service accounts
- **Annually (365 days)**: TLS certificates (shorter expiry recommended)

**Triggers for Immediate Rotation**:
- ✅ Credential compromise detected
- ✅ Employee separation
- ✅ Unauthorized access attempt
- ✅ Policy violation
- ✅ Regular security audit findings

---

## Procedures by Secret Type

### 1. CODEX_MASTER_KEY Rotation

**Frequency**: Quarterly (90 days)  
**Owner**: Security Lead  
**Duration**: 72 hours total (24h dual-write + 48h grace)

#### Standard Quarterly Rotation

**Phase 1: Pre-Rotation Verification** (24 hours before)
```bash
# 1.1 Verify current key is secure
python scripts/security/verify_key_integrity.py
# Expected output: ✅ Key integrity verified, entropy: 256-bit

# 1.2 Check deployment readiness
python scripts/security/check_rotation_readiness.py
# Expected output:
# ✅ All services can be updated
# ✅ Backup procedures ready
# ✅ Fallback key available

# 1.3 Test rotation scripts in staging
nox -s security -- test-key-rotation-staging
# Expected output: ✅ All rotation steps passed in staging
```

**Phase 2: Generate New Key**
```bash
# 2.1 Generate new master key
python scripts/rotate_jwt_secret.py \
  --generate \
  --output-format=base64 \
  --save-to=.env.new-key

# Example output:
# New Key ID: mk-2026-06-14-001
# Entropy: 256-bit
# Algorithm: AES-256-GCM
# Created: 2026-06-14T14:30:00Z

# 2.2 Backup old key (encrypted)
python scripts/security/backup_key.py \
  --key=CODEX_MASTER_KEY \
  --archive-days=90

# Output: ✅ Key backed up to: .codex/backups/mk-2026-03-14-001.enc
```

**Phase 3: Dual-Write Phase** (24 hours)
```bash
# 3.1 Update GitHub Actions secret with NEW key
gh secret set VAULT_CODEX_MASTER_KEY_NEW \
  --body="$(cat .env.new-key)"

# 3.2 Update deployment to use dual keys
# In .github/workflows/deploy.yml:
# env:
# CODEX_MASTER_KEY_PRIMARY: ${{ secrets.VAULT_CODEX_MASTER_KEY }}
# CODEX_MASTER_KEY_SECONDARY: ${{ secrets.VAULT_CODEX_MASTER_KEY_NEW }}

# 3.3 Deploy dual-key version (accepts both old and new)
git commit -m "security: enable dual-key rotation phase"
git push origin feature/key-rotation-$(date +%Y%m%d)
# Create PR, wait for CI/CD approval, merge

# 3.4 Monitor dual-key operations
python scripts/security/monitor_rotation.py --duration=24h
# Watch for errors or fallback to old key
```

**Phase 4: Primary Key Swap** (after 24h dual-write)
```bash
# 4.1 Swap primary key in GitHub Actions
gh secret set VAULT_CODEX_MASTER_KEY --body="$(cat .env.new-key)"

# 4.2 Update secondary to old key (fallback)
gh secret set VAULT_CODEX_MASTER_KEY_OLD \
  --body="$(cat .env.old-key)"

# 4.3 Deploy single-key version (primary only)
git commit -m "security: complete key rotation primary swap"
git push origin feature/key-rotation-$(date +%Y%m%d)

# 4.4 Verify primary key active
python scripts/security/verify_rotation_complete.py
# Expected: ✅ Primary key active, no encryption errors
```

**Phase 5: Grace Period & Cleanup** (48 hours)
```bash
# 5.1 Monitor for issues (48 hours)
# - Check application logs for decryption errors
# - Verify all services initialized with new key

# 5.2 Revoke old key (after 48h grace)
python scripts/security/revoke_key.py \
  --key-id=mk-2026-03-14-001 \
  --archive-retention=90days

# Output: ✅ Old key revoked, archived for 90 days

# 5.3 Update rotation log
echo "mk-2026-03-14-001 → mk-2026-06-14-001: SUCCESS" >> .codex/rotation.log
```

## Emergency Rotation (Compromised Key)

```bash
# IMMEDIATE ACTION: No dual-write phase
python scripts/rotate_jwt_secret.py \
  --emergency \
  --revoke-old \
  --notify-team

# Output:
# ⚠️ EMERGENCY ROTATION INITIATED
# Old Key: mk-2026-03-14-001 [REVOKED]
# New Key: mk-2026-06-14-emerg-001 [ACTIVE]
# Grace Period: 60 minutes
# Action Required: Re-authenticate all active sessions

# 1. Create emergency ticket
gh issue create \
  --title="SECURITY: Emergency key rotation - $(date)" \
  --body="Emergency master key rotation completed. Impact: All tokens invalidated."

# 2. Notify team via Slack
# Posted to #security channel

# 3. Re-authenticate active users
python scripts/security/invalidate_sessions.py \
  --reason="Key rotation" \
  --grace-period=60min
```

**Test Coverage**: `tests/security/test_key_rotation.py`
- ✅ `test_quarterly_rotation_success`
- ✅ `test_emergency_rotation_immediate`
- ✅ `test_dual_write_phase_integrity`
- ✅ `test_old_key_revocation`

---

## 2. GitHub OAuth Token Rotation

**Frequency**: Monthly (30 days)  
**Owner**: CI/CD Lead  
**Duration**: 48 hours total (24h fallback + 24h revocation)

### Standard Rotation

```bash
# 1. Generate new token in GitHub App settings
# Navigate: Settings → Developer Settings → OAuth Apps → _codex_

# 2. Create new GitHub Action secret
NEW_TOKEN=$(gh api repos/Aries-Serpent/_codex_/actions/secrets/create \
  --input - <<EOF
{
  "name": "GITHUB_TOKEN_NEW",
  "value": "$OAUTH_TOKEN_NEW"
}
EOF)

# 3. Deploy with fallback to old token (24 hours)
# env:
# GITHUB_TOKEN_PRIMARY: ${{ secrets.GITHUB_TOKEN_NEW }}
# GITHUB_TOKEN_FALLBACK: ${{ secrets.GITHUB_TOKEN }}

# 4. After 24 hours, swap primary
gh secret set GITHUB_TOKEN --body="$OAUTH_TOKEN_NEW"

# 5. Revoke old token in GitHub App settings
# Verify no errors in last 24 hours first

# 6. Update rotation log
echo "OAuth Token: $(date +%Y-%m-%d)" >> .codex/rotation.log
```

**Automated Monthly Rotation** (scheduled):
- Trigger: GitHub Actions schedule (2 AM UTC, 14th of month)
- Script: `scripts/rotate_github_tokens.py`
- Rollback: Automatic if GitHub API calls fail

---

## 3. Database Credentials Rotation

**Frequency**: Quarterly (90 days)  
**Owner**: Database Administrator  
**Duration**: 72 hours (24h dual + 48h grace)

### Rotation Procedure

```bash
# 1. Create new database user
# Using: scripts/manage_db_credentials.py

python scripts/manage_db_credentials.py \
  --action=create-user \
  --username=codex-app-2026-q2 \
  --permissions=app-standard

# Output: User created, password generated securely

# 2. Grant same permissions as old user
python scripts/manage_db_credentials.py \
  --action=replicate-permissions \
  --from=codex-app-2026-q1 \
  --to=codex-app-2026-q2

# Output: ✅ Permissions replicated

# 3. Update DATABASE_URL secret (dual-phase)
NEW_DB_URL="******db.example.com/codex"
gh secret set DATABASE_URL_NEW --body="$NEW_DB_URL"

# 4. Deploy with fallback (24 hours)
# env:
# DATABASE_URL: ${{ secrets.DATABASE_URL_NEW }}
# DATABASE_URL_FALLBACK: ${{ secrets.DATABASE_URL }}

# 5. Verify connectivity and performance (24 hours)
python scripts/security/verify_db_rotation.py --duration=24h
# Check: Connection pool healthy, query performance normal

# 6. Swap primary (after 24h)
gh secret set DATABASE_URL --body="$NEW_DB_URL"

# 7. Drop old user (after 48h grace period)
python scripts/manage_db_credentials.py \
  --action=drop-user \
  --username=codex-app-2026-q1 \
  --archive-logs=true

# Output: ✅ Old user dropped, audit logs archived
```

---

## 4. API Keys (External Services)

**Frequency**: Monthly (30 days)  
**Owner**: Service Owner (specific API)  
**Duration**: 24 hours

### Rotation by Service

**For Stable APIs** (most services):
```bash
# 1. Generate new API key in service console
# 2. Update GitHub Actions secret
gh secret set API_KEY_<SERVICE>_NEW --body="$NEW_KEY"

# 3. Deploy with fallback (24 hours)
# 4. Verify API calls successful
# 5. Swap primary after 24 hours
# 6. Revoke old key
```

**For Critical APIs** (payment, billing):
```bash
# Use extended dual-write phase (72 hours)
# Monitor all transactions before revoking old key
# Include manual verification step
```

---

## 5. JWT Signing Key Rotation

**Frequency**: Quarterly (90 days)  
**Owner**: Authentication Team  
**Duration**: 7 days (key algorithm transition period)

### Procedure

```bash
# 1. Generate new JWT key
python scripts/rotate_jwt_key.py --generate

# 2. Add new key as secondary (7-day transition)
# Applications accept tokens from both keys
# but only sign new tokens with new key

# 3. After 7 days, revoke old key
# Existing tokens become invalid (force re-auth)
```

**Test Coverage**: `tests/security/test_jwt_rotation.py`

---

## 6. TLS Certificates

**Frequency**: Annually (365 days) / Before Expiry  
**Owner**: DevOps Team  
**Duration**: Depends on certificate type

### Procedure

```bash
# 1. Check certificate expiry
python scripts/security/check_cert_expiry.py
# Output: Certificate expires in 30 days — recommend renewal

# 2. Request new certificate from CA
# Using existing Certificate Signing Request (CSR)

# 3. Install new certificate
python scripts/security/update_tls_cert.py \
  --cert-file=new-cert.pem \
  --key-file=new-key.pem \
  --backup-old=true

# 4. Verify certificate installation
openssl s_client -connect api.example.com:443 -tls1_3
# Verify certificate chain and dates

# 5. Monitor SSL/TLS handshakes
# Watch for any connection errors in logs
```

---

## Rotation Process

### Pre-Rotation Checklist

- [ ] Scheduled rotation date confirmed
- [ ] All team members notified (if needed)
- [ ] Test environment rotation verified first
- [ ] Backup procedures in place
- [ ] Rollback plan documented
- [ ] Monitoring dashboards ready
- [ ] On-call engineer assigned

### Rotation Steps

1. **Generate**: Create new secret with adequate entropy
2. **Backup**: Securely archive old secret (encrypted)
3. **Validate**: Verify new secret format/entropy
4. **Deploy**: Push to staging environment first
5. **Test**: Execute integration tests
6. **Promote**: Deploy to production
7. **Dual-Write**: Support both old and new (if needed)
8. **Monitor**: Watch for errors/failures
9. **Swap**: Switch primary to new secret
10. **Revoke**: Deactivate old secret (after grace period)
11. **Log**: Record rotation in audit trail
12. **Verify**: Confirm old secret is not being used

### Monitoring During Rotation

**Metrics to Track**:
- ✅ Authentication success rate (should remain >99.9%)
- ✅ Authorization check latency
- ✅ Secret cache hit rate
- ✅ Decryption error count (should be 0)
- ✅ Failed decrypt attempts (investigate any)

**Alert Thresholds**:
- ⚠️ Authentication failures > 1% → Rollback
- ⚠️ Decryption errors > 0 → Investigation
- ⚠️ Latency spike > 500ms → Review

### Post-Rotation Verification

```bash
# 1. Verify no errors in logs
grep -i "decrypt\|credential\|auth.*fail" /var/log/codex/*.log
# Expected: No errors related to secret decryption

# 2. Test all critical paths
nox -s tests -- -k "auth or credential or secret"
# Expected: All tests pass

# 3. Confirm old secret is not used
grep -r "$OLD_SECRET" src/ tests/ scripts/
# Expected: No matches (should be removed)

# 4. Document in rotation log
echo "Secret rotated: $TYPE, date: $(date), status: SUCCESS" >> .codex/rotation.log
```

---

## Emergency Rotation

### When to Trigger

- ✅ Credential found in public repository
- ✅ Unauthorized access detected
- ✅ Disgruntled employee departing
- ✅ Security policy violation
- ✅ Audit findings
- ✅ Suspected compromise

### Emergency Procedure

```bash
# IMMEDIATE (within 1 minute):
python scripts/rotate_secret.py \
  --type=$SECRET_TYPE \
  --emergency \
  --notify=immediate

# Expected steps:
# 1. New secret generated
# 2. Old secret invalidated immediately (no grace period)
# 3. Application updated
# 4. Team notified via Slack
# 5. Incident ticket created

# WITHIN 1 HOUR:
# 1. Investigation started
# 2. Access logs reviewed (7 days)
# 3. Possible exposures identified
# 4. Remediation steps planned

# WITHIN 24 HOURS:
# 1. Root cause analysis complete
# 2. Preventive measures implemented
# 3. Post-incident review
# 4. Documentation updated
```

## Emergency Contact List

| Role | Contact | Escalation |
|------|---------|-------------|
| Security Lead | @security-team (Slack) | Immediate |
| On-call Engineer | PagerDuty | Within 5 min |
| CTO | @cto (Slack) | If escalation needed |

---

## Monitoring & Compliance

### Rotation Tracking

**Location**: `.codex/rotation.log`

**Format**:
```
date,secret_type,old_key_id,new_key_id,reason,status,duration_hours  # pragma: allowlist secret
2026-06-14,CODEX_MASTER_KEY,mk-2026-03-14-001,mk-2026-06-14-001,scheduled,success,72
2026-06-14,GITHUB_TOKEN,ghp_old123,ghp_new456,scheduled,success,48  # pragma: allowlist secret
```

### Audit Logging

All rotation events logged to immutable audit trail:
- ✅ Who performed rotation (user/service account)
- ✅ When rotation occurred
- ✅ Which secret was rotated
- ✅ Old and new key IDs
- ✅ Reason for rotation
- ✅ Status (success/failed)
- ✅ Any errors or warnings

### Compliance Checks

**Monthly Compliance Report**:
```bash
python scripts/security/compliance_report.py --month=$(date +%Y-%m)
# Output: Rotation compliance status

# Expected output:
# ✅ CODEX_MASTER_KEY: Last rotated 2026-06-14 (within schedule)
# ✅ GitHub Tokens: Last rotated 2026-06-14 (within schedule)
# ⚠️ Database Creds: Last rotated 2026-03-14 (DUE 2026-06-14)
# ✅ TLS Certificates: Valid until 2027-01-15
```

**Audit Trail Verification** (quarterly):
```bash
python scripts/security/audit_trail_verify.py --rotations=.codex/rotation.log
# Verify:
# - No gaps in rotation schedule
# - All rotations logged
# - Old keys properly revoked
```

---

## FAQ & Troubleshooting

### Q: What happens to tokens/sessions during rotation?

**A**: It depends on the secret type:
- **Master Key**: Active sessions continue, new authentication requires new key
- **Short-lived tokens** (API keys): Existing requests complete, new requests use new token
- **Long-lived tokens** (service accounts): Existing connections may timeout; auto-reconnect with new token

### Q: Can I rotate early?

**A**: Yes! Rotate immediately if:
- Compromise suspected
- Policy requires
- Audit findings
- Preventive measure desired

Use `--early` flag: `rotate_jwt_secret.py --early`

### Q: What if rotation fails?

**A**: 
1. Check error logs: `tail -100 /var/log/codex/rotation.log`
2. Run verification: `verify_rotation_complete.py`
3. If critical failure: Rollback to old secret immediately
4. Investigate root cause
5. Retry after issue resolved

### Q: How are old secrets stored/archived?

**A**: Encrypted archives in `.codex/backups/`:
- Encrypted with current CODEX_MASTER_KEY
- Retention: 90 days (configurable)
- Accessible only to authorized admins
- Cannot be restored automatically (requires manual approval)

### Q: What's the audit trail retention policy?

**A**:
- Security events (auth, authorization, secret access): **1 year**
- Rotation logs: **7 years** (compliance)
- Immutable archives: **Indefinite** (legal hold)

### Q: Can service accounts have different rotation schedules?

**A**: Yes, based on usage:
- High-frequency access: Monthly (30 days)
- Standard access: Quarterly (90 days)
- Emergency-only access: Annually (365 days)

Configure in `SERVICE_ACCOUNT_ROTATION_SCHEDULE.yaml`

### Q: What happens if I forget to rotate?

**A**:
1. Automated reminders sent 7 days before due date
2. Automated reminders sent on due date (Slack + email)
3. After 3 days overdue: Automated rotation triggered (safe mode)
4. After 7 days overdue: Escalation to security team

---

## Related Documents

- **RBAC Specification**: `docs/production/RBAC_SPECIFICATION.md`
- **Incident Response**: `docs/operations/INCIDENT_RESPONSE_PLAYBOOKS.md`
- **Security Policy**: `SECURITY.md`
- **Batch 2 Summary**: `.codex/BATCH_2_SECURITY_REMEDIATION_SUMMARY.md`

---

**Approved By**: Security Team  
**Effective Date**: 2026-06-14  
**Review Frequency**: Quarterly  
**Next Review**: 2026-09-14

---

*This policy is mandatory for all secret management in the _codex_ platform.*
