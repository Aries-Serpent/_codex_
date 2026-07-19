# Runbook: Hardcoded Secrets Remediation (CWE-798)

**Severity**: CRITICAL  
**SLA**: <1 hour (immediate credential rotation)  
**Category**: CodeQL Alert Remediation  
**CWE**: CWE-798 - Use of Hard-Coded Credentials  
**CVSS Score**: 9.8 (Critical)

---

## Overview

Hardcoded secrets (API keys, passwords, tokens, certificates) embedded in source code can be discovered by attackers through GitHub history, build logs, or decompilation. This immediately compromises the security of all systems using those credentials.

---

## Trigger Conditions

CodeQL alert: `py/hardcoded-secret` fired  
Log pattern: `password|api_key|secret|token|credential` found in code  
Severity: CRITICAL (immediate action required)

---

## Remediation Steps

### Step 1: Scan for Secrets
```bash
truffleHog filesystem {repo_path} --json > secrets.json
gitleaks detect --source {file} --verbose
python -m detect_secrets scan --baseline .secrets.baseline
```

### Step 2: Rotate Compromised Credentials
**CRITICAL**: Assume the credential is compromised once it's in git history!

```bash
# Step 2a: Invalidate the credential immediately
# - API keys: Regenerate in provider dashboard
# - Passwords: Change in password manager
# - Tokens: Revoke in OAuth provider
# - Database credentials: Change password

# Step 2b: Check for unauthorized access
# Query logs for access patterns during exposure window
grep -r "{secret_value}" /var/log/auth.log* | head -20

# Step 2c: Document incident
# Create security incident ticket
echo "Secret compromised: ${SECRET_NAME}" > incident.txt
```

### Step 3: Remove from Codebase
```python
# Use environment variables
import os
API_KEY = os.getenv('API_KEY')  # Load from environment

# Use secrets management
from aws_secretsmanager import get_secret
API_KEY = get_secret('production/api_key')

# Use .env files (NOT in git)
from dotenv import load_dotenv
load_dotenv('.env.local')  # Add .env to .gitignore
```

### Step 4: Purge from Git History
```bash
# WARNING: This requires force push and coordination

# Use BFG Repo-Cleaner
bfg --delete-files id_{RSA,DSA,ECDSA,ED25519} --no-blob-protection {repo}
bfg --replace-text passwords.txt {repo}

# Or use git filter-branch
git filter-branch --tree-filter 'rm -f {file_with_secret}' HEAD
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (requires coordination)
git push origin --force --all
```

### Step 5: Validation
```bash
# Verify secret is removed
grep -r "API_KEY" {file} | grep -v ".env" || echo "Secret removed"

# Verify environment variable usage
python -c "import os; print(os.getenv('API_KEY') is not None)"

# Run secret scanner again
truffleHog filesystem {repo_path} --json | wc -l  # Should be 0
```

---

## Incident Response

**CRITICAL ACTIONS** (execute immediately):
1. Rotate credential in provider (AWS/GCP/Azure console)
2. Check access logs for unauthorized activity
3. Create security incident ticket
4. Notify affected systems/teams
5. Update incident response plan with timeline

---

## Escalation Path

Always escalate to security team for:
- Database passwords
- API keys with production access
- OAuth tokens with sensitive scopes
- Certificates/keys used for signing
- AWS/GCP/Azure credentials

---

## Related Patterns

- RP-6002: Hardcoded Secrets Remediation
- RP-6005: Secret Rotation Procedures
- RP-6006: Audit Trail Integrity

---

## References

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [CWE-798](https://cwe.mitre.org/data/definitions/798.html)
