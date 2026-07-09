# Secrets Management Guide - Aries-Serpent v0.1.0

**Document Type:** Security & Operations Guide  
**Audience:** Developers, Operations, DevOps Engineers  
**Last Updated:** 2026-07-09

## 1. Overview

This document defines secure practices for managing secrets (API keys, credentials, tokens, passwords) in the Aries-Serpent project.

### 1.1 Secret Types
- **Database Credentials:** PostgreSQL, MongoDB, Redis usernames/passwords
- **API Keys:** Third-party service keys (OpenAI, AWS, GCP, etc.)
- **Authentication Tokens:** OAuth tokens, JWT secrets, session keys
- **Encryption Keys:** Master keys for data encryption
- **SSH Keys:** Deploy keys, service account keys
- **TLS Certificates:** SSL/TLS certs and private keys
  # pragma: allowlist secret  # pragma: allowlist secret
### 1.2 Core Principles
1. **Never Commit Secrets:** Secrets must NEVER be committed to git
2. **Environment-Specific:** Secrets differ per environment (dev, staging, prod)
3. **Rotation Schedule:** Regularly rotate all credentials
4. **Least Privilege:** Grant minimum necessary access
5. **Audit Trail:** Track who accessed secrets and when

## 2. Local Development Setup

### 2.1 Environment Variables
Create a `.env` file in your project root (automatically excluded from git):

```bash
# .env (local development only)
DATABASE_URL=******localhost:5432/aries_dev
REDIS_URL=redis://:password@localhost:6379/0
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
```

### 2.2 Template Files
Reference `.env.example` files (committed to git) as templates:

```bash
# .env.example (safe to commit)
# Copy this file to .env and fill in actual values
DATABASE_URL=******localhost:5432/aries_dev
REDIS_URL=redis://:password@localhost:6379/0
OPENAI_API_KEY=sk-... # Get from https://platform.openai.com/api-keys
AWS_ACCESS_KEY_ID=... # Get from AWS IAM console
AWS_SECRET_ACCESS_KEY=... # Get from AWS IAM console
JWT_SECRET=... # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Git Configuration
The `.gitignore` file already excludes secrets:

```
# .gitignore (already configured)
.env
.env.local
.env.*.local
secrets.txt  # pragma: allowlist secret
*.key
*.pem
```

## 3. CI/CD Secrets Management

### 3.1 GitHub Actions Secrets
Secrets are stored securely in GitHub repository settings:

**URL:** Settings → Secrets and variables → Actions

**Available Scopes:**
- Repository secrets (accessible to all workflows)
- Environment secrets (accessible only to specific environments)
- Organization secrets (shared across repositories)

### 3.2 Setting Repository Secrets

**Example: Adding a database credential**

```bash
# Via GitHub CLI
gh secret set DATABASE_URL -b "******host/db"

# Via GitHub Web UI
1. Go to: Settings → Secrets and variables → Actions
2. Click: New repository secret
3. Name: DATABASE_URL
4. Value: ******host/db
5. Click: Add secret
```

### 3.3 Using Secrets in Workflows

```yaml
# .github/workflows/deploy.yml
name: Deploy

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Make secret available as environment variable
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          # Secrets are automatically masked in logs
          python scripts/deploy.py
```

### 3.4 Secret Masking
GitHub Actions automatically masks secrets in logs:
- Actual value never appears in build logs
- If accidentally logged, it's displayed as `***`
- Masked in console output and artifacts

## 4. Production Deployment

### 4.1 Kubernetes Secrets
Secrets stored in Kubernetes cluster:

```yaml
# manifests/k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0Bkb3N0Z3Jlc2hvc3Q6NTQzMi9kYg==
  API_KEY: c2stYWJjZGVmZ2hpamtsbW5vcA==
```

**Create secret:**
```bash
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL='******db:5432/prod' \
  --from-literal=API_KEY='sk-abcdefghijklmnop' \
  -n production
```

### 4.2 Mounting Secrets in Pods

```yaml
# manifests/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  template:
    spec:
      containers:
      - name: api
        image: aries-serpent:0.1.0
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: API_KEY
```

### 4.3 Secrets Encryption at Rest
Enable encryption for Kubernetes secrets:

```bash
# Configure etcd encryption (managed by cloud provider)
kubectl edit apiserver -n kube-system
# Add: --encryption-provider-config=/etc/kubernetes/secrets/encryption-config.yaml
```

## 5. Secret Rotation

### 5.1 Rotation Schedule
- **Critical Secrets (DB passwords, API keys):** Every 90 days
- **Service Account Keys:** Every 180 days
- **TLS Certificates:** Before expiration (auto-renewal recommended)
- **Immediate Rotation:** If secret is compromised or leaked

### 5.2 Rotation Procedure

**Step 1: Generate New Secret**
```bash
# Example: Generate new JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: AbC1De2FgH3IjK4lm_nOpQrS5tUvWxYz
```

**Step 2: Update in All Locations**
```bash
# Update GitHub secret
gh secret set JWT_SECRET -b "AbC1De2FgH3IjK4lm_nOpQrS5tUvWxYz"

# Update Kubernetes secret
kubectl patch secret app-secrets -p \
  '{"data":{"JWT_SECRET":"'$(echo -n 'AbC1De2FgH3IjK4lm_nOpQrS5tUvWxYz' | base64)'"}}'
```

**Step 3: Verify Access with New Secret**
```bash
# Test with new secret
python scripts/test_auth.py --token-secret "AbC1De2FgH3IjK4lm_nOpQrS5tUvWxYz"
```

**Step 4: Decommission Old Secret**
- After all services are using new secret (24-48 hours)
- Document in audit log
- Delete from all systems

### 5.3 Automated Rotation (Optional)
Using Sealed Secrets or External Secrets Operator:

```yaml
# Using External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets
spec:
  provider:
    aws:
      service: SecretsManager
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-secret
spec:
  secretStoreRef:
    name: aws-secrets
    kind: SecretStore
  target:
    name: database-secret
  data:
  - secretKey: DATABASE_URL
    remoteRef:
      key: prod/database-url
```

## 6. Monitoring & Auditing

### 6.1 Audit Logging
Log all secret access:

```bash
# Enable audit logging in Kubernetes
kubectl create -f - <<EOF
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  verbs: ["get", "list", "watch"]
  resources: ["secrets"]
EOF
```

### 6.2 Access Monitoring
Monitor who accessed secrets and when:

```bash
# Query Kubernetes audit logs
kubectl logs -n kube-system kube-apiserver | grep "secrets" | tail -20

# View GitHub Actions secret access logs
# URL: Settings → Audit log → Filter by "secret"
```

### 6.3 Alerts
Set up alerts for suspicious secret access:
- Multiple failed auth attempts
- Unexpected secret access patterns
- Secrets accessed from unusual locations

## 7. Incident Response

### 7.1 Secret Compromise Detection
Signs that a secret may be compromised:
- Unusual login attempts from unfamiliar locations
- Unexpected API usage or billing charges
- Security tool alerts for suspicious activity

### 7.2 Immediate Response
1. **STOP:** Disable/revoke the compromised secret immediately
2. **ASSESS:** Determine scope and impact
3. **ROTATE:** Generate and deploy new secret
4. **AUDIT:** Review logs for unauthorized access
5. **NOTIFY:** Inform affected teams and stakeholders

### 7.3 Post-Incident
- Update incident report
- Implement preventive measures
- Review secret management procedures
- Conduct team training if needed

## 8. Best Practices Checklist

**Development:**
- [ ] Never commit `.env` files
- [ ] Use `.env.example` templates
- [ ] Rotate local dev secrets regularly
- [ ] Use different secrets for each environment

**CI/CD:**
- [ ] Store all secrets in GitHub Actions
- [ ] Use environment-specific secret sets
- [ ] Enable secret masking in logs
- [ ] Audit secret usage in workflows

**Production:**
- [ ] Use Kubernetes Secrets or external secret vault
- [ ] Enable encryption at rest
- [ ] Implement RBAC for secret access
- [ ] Set up audit logging
- [ ] Monitor secret access patterns
- [ ] Rotate secrets on schedule

**Security:**
- [ ] No secrets in version control
- [ ] No secrets in environment variables in code
- [ ] No secrets in documentation or comments
- [ ] Incident response plan documented
- [ ] Team trained on secret management

## 9. Tools & Resources

### 9.1 Secret Scanning Tools
- **git-secrets:** Prevent secrets in git commits
- **detect-secrets:** Automated secret detection
- **truffleHog:** Find secrets in git history
- **GitGuardian:** Security platform with secret scanning

### 9.2 Secret Management Tools
- **Kubernetes Secrets:** Built-in (baseline security)
- **HashiCorp Vault:** Enterprise secret management
- **AWS Secrets Manager:** AWS-native secret storage
- **GitHub Actions Secrets:** Built-in CI/CD secrets
- **Sealed Secrets:** Encrypted Kubernetes secrets
- **External Secrets Operator:** Multi-provider secret sync

### 9.3 Useful Commands

```bash
# Generate secure random secret (32 bytes)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check for secrets in git history
git-secrets --scan

# Detect secrets in current directory
detect-secrets scan --baseline .secrets.baseline

# Rotate GitHub secret
gh secret set SECRET_NAME -b "new-secret-value"

# View K8s secret (base64 decoded)
kubectl get secret app-secrets -o json | jq '.data | map_values(@base64d)'
```

## 10. Compliance References

- **CIS Kubernetes Benchmark:** 5.2.1-5.2.2 (Secret encryption)
- **NIST Cybersecurity Framework:** PR.DS.1 (Data protection)
- **ISO 27001:** A.10.1.1 (Cryptographic controls)
- **OWASP:** A2 - Cryptographic Failures

---

**Document Status:** ✅ COMPLETE  
**Next Review:** 2026-10-09 (quarterly)  
**Owner:** Security Team / DevOps
