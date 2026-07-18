# Runbook: Secret Rotation Procedures

**Severity**: HIGH  
**SLA**: <24 hours after compromise detection  
**Category**: PII/Secret Detection & Remediation

---

## Overview

Regular secret rotation reduces the impact of potential compromise. After any security incident involving secrets, immediate rotation is required.

---

## Rotation Schedule

- **API Keys**: Quarterly (or immediately after exposure)
- **Database Passwords**: Quarterly
- **OAuth Tokens**: Automatically refreshed
- **SSH Keys**: Yearly (or when employees leave)
- **Certificates**: At least yearly (before expiration)

---

## Rotation Procedure

### Step 1: Generate New Secret
```bash
# API Key
# Use provider's dashboard or API

# Database Password
# Generate strong password: openssl rand -base64 32

# SSH Key
# ssh-keygen -t ed25519 -f ~/.ssh/id_new

# Certificate
# Use Let's Encrypt auto-renewal or CSR process
```

### Step 2: Deploy New Secret
```bash
# Update deployment configurations
export NEW_API_KEY="..."

# Update environment variables
echo "API_KEY=${NEW_API_KEY}" >> .env

# Deploy to all systems
# Use zero-downtime deployment with secret switchover

# Update in secret manager
aws secretsmanager put-secret-value \
  --secret-id production/api_key \
  --secret-string "${NEW_API_KEY}"
```

### Step 3: Verify Both Secrets Work
```bash
# Test with old secret (should work until grace period expires)
curl -H "Authorization: ******" https://api.example.com/health

# Test with new secret (should work immediately)
curl -H "Authorization: ******" https://api.example.com/health

# Monitor logs during switchover
tail -f /var/log/app.log | grep -i "auth\|secret"
```

### Step 4: Revoke Old Secret
```bash
# After grace period (24-48 hours), revoke old secret
# - Delete from provider console
# - Remove from all configurations
# - Archive in incident report

# Revoke OAuth tokens
# Logout existing sessions
# Force re-authentication

# Revoke SSH keys
# Remove from authorized_keys
# Archive removed key
```

### Step 5: Document and Audit
```bash
# Log rotation event
echo "Secret rotated at $(date): ${SECRET_TYPE}" >> rotation.log

# Verify in audit logs
grep "rotation" /var/log/audit.log | tail -5
```

---

## Emergency Rotation

**If compromise is suspected**:
1. Rotate immediately (no grace period)
2. Check logs for unauthorized use
3. File incident report
4. Notify users if applicable

---

## References

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [Vault by HashiCorp](https://www.vaultproject.io/)
