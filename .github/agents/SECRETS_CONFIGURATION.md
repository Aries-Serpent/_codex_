# Secrets Configuration Guide

Complete guide for configuring all required secrets for the GitHub Agent PR Reviewer.

---

## 📋 Overview

**Required Secrets:**
1. GitHub App ID
2. GitHub Webhook Secret
3. GitHub Private Key (PEM file)
4. AWS Credentials (for deployment)

**Storage Locations:**
- GitHub App credentials → AWS Secrets Manager
- Deployment credentials → Environment variables
- Local development → `.env` file (not committed)

---

## 🔑 1. GitHub App Secrets

### Create GitHub App

1. **Navigate to GitHub Settings**
   ```
   https://github.com/settings/apps/new
   ```

2. **Fill in App Details:**
   - **Name:** `codex-pr-reviewer-dev` (or your choice)
   - **Description:** `Automated PR review agent with quantum pattern analysis`
   - **Homepage URL:** `https://github.com/Aries-Serpent/_codex_`
   - **Webhook URL:** `https://PLACEHOLDER` (update after deployment)
   - **Webhook Secret:** Generate with:
     ```bash
     python3 -c "import secrets; print(secrets.token_urlsafe(32))"
     ```

3. **Set Permissions:**
   ```
   Repository permissions:
   - Contents: Read-only
   - Pull requests: Read & write
   - Issues: Read & write
   - Checks: Read & write
   - Metadata: Read-only
   
   Subscribe to events:
   - Pull request
   - Pull request review
   - Pull request review comment
   - Issue comment
   ```

4. **Create App**
   - Click "Create GitHub App"
   - Note the **App ID** (e.g., `123456`)
   - Generate and download **Private Key** (saves as `.pem` file)

---

## 🗝️ 2. Store Secrets in AWS Secrets Manager

### Store GitHub Private Key

```bash
# Development environment
aws secretsmanager create-secret \
    --name github-app-private-key-dev \
    --description "GitHub App private key for Codex Reviewer (dev)" \
    --secret-string file://path/to/your-app-name.YYYY-MM-DD.private-key.pem \
    --region us-east-1

# Verify storage
aws secretsmanager describe-secret \
    --secret-id github-app-private-key-dev \
    --region us-east-1

# Expected output shows ARN and creation date
```

### Store App ID and Webhook Secret (Alternative Method)

While we pass these as environment variables, you can also store in Secrets Manager:

```bash
# Create composite secret (optional)
aws secretsmanager create-secret \
    --name github-app-config-dev \
    --description "GitHub App configuration" \
    --secret-string '{
        "app_id": "123456",
        "webhook_secret": "your-webhook-secret-here"
    }' \
    --region us-east-1
```

---

## 🔐 3. Set Environment Variables

### For Terraform Deployment

```bash
# Export required variables
export TF_VAR_github_app_id="123456"
export TF_VAR_github_webhook_secret="your-webhook-secret-from-step-1"
export AWS_PROFILE="default"  # or your AWS profile name
export AWS_REGION="us-east-1"

# Verify they're set
echo "App ID: ${TF_VAR_github_app_id}"
echo "Webhook Secret: ${TF_VAR_github_webhook_secret:0:10}..."  # Show first 10 chars
echo "AWS Profile: ${AWS_PROFILE}"
echo "AWS Region: ${AWS_REGION}"
```

### Persist in Shell Profile (Optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Add to end of file
export TF_VAR_github_app_id="123456"
export TF_VAR_github_webhook_secret="your-secret-here"

# Reload
source ~/.bashrc  # or source ~/.zshrc
```

---

## 🔒 4. Secure Storage Best Practices

### Use a .env File for Local Development

```bash
# Create .env file (NEVER commit this)
cat > .github/agents/.env << 'EOF'
GITHUB_APP_ID=123456
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
AWS_PROFILE=default
AWS_REGION=us-east-1
EOF

# Add to .gitignore
echo ".env" >> .github/agents/.gitignore

# Load in scripts
set -a
source .github/agents/.env
set +a
```

### Rotate Secrets Regularly

```bash
# Rotate webhook secret
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "New webhook secret: ${NEW_SECRET}"

# Update in GitHub App settings
# Update in AWS Secrets Manager
aws secretsmanager update-secret \
    --secret-id github-app-config-dev \
    --secret-string "{\"app_id\": \"123456\", \"webhook_secret\": \"${NEW_SECRET}\"}"

# Update environment variable
export TF_VAR_github_webhook_secret="${NEW_SECRET}"

# Redeploy
cd .github/agents/deploy/scripts
./deploy.sh dev apply
```

### Rotate Private Key

```bash
# In GitHub App settings:
# 1. Generate new private key
# 2. Download new .pem file
# 3. Update Secrets Manager

aws secretsmanager update-secret \
    --secret-id github-app-private-key-dev \
    --secret-string file://new-private-key.pem

# No redeployment needed - Lambda reads from Secrets Manager at runtime
```

---

## ✅ 5. Verification Checklist

### Pre-Deployment Verification

```bash
# Check all required environment variables
cat << 'VERIFY' | bash
#!/bin/bash
echo "=== Secret Verification ==="
errors=0

if [[ -z "${TF_VAR_github_app_id}" ]]; then
    echo "❌ TF_VAR_github_app_id not set"
    ((errors++))
else
    echo "✅ TF_VAR_github_app_id set"
fi

if [[ -z "${TF_VAR_github_webhook_secret}" ]]; then
    echo "❌ TF_VAR_github_webhook_secret not set"
    ((errors++))
else
    echo "✅ TF_VAR_github_webhook_secret set"
fi

if aws secretsmanager describe-secret --secret-id github-app-private-key-dev &>/dev/null; then
    echo "✅ Private key exists in Secrets Manager"
else
    echo "❌ Private key NOT found in Secrets Manager"
    ((errors++))
fi

if [[ $errors -eq 0 ]]; then
    echo ""
    echo "✅ All secrets configured correctly"
    exit 0
else
    echo ""
    echo "❌ ${errors} error(s) found - fix before deploying"
    exit 1
fi
VERIFY
```

### Post-Deployment Verification

```bash
# Verify Lambda can access secrets
aws lambda invoke \
    --function-name codex-reviewer-agent-dev \
    --payload '{"test": "secret_access"}' \
    /tmp/response.json

# Check response
cat /tmp/response.json
```

---

## 🚨 Troubleshooting

### Error: "Secret not found"

```bash
# List all secrets
aws secretsmanager list-secrets --region us-east-1

# Check specific secret
aws secretsmanager get-secret-value \
    --secret-id github-app-private-key-dev \
    --region us-east-1

# If not found, recreate:
aws secretsmanager create-secret \
    --name github-app-private-key-dev \
    --secret-string file://private-key.pem \
    --region us-east-1
```

### Error: "Access denied"

```bash
# Check IAM permissions
aws iam get-role-policy \
    --role-name codex-reviewer-lambda-role-dev \
    --policy-name codex-reviewer-lambda-policy

# Verify policy includes:
# - secretsmanager:GetSecretValue
# - secretsmanager:DescribeSecret
```

### Error: "Invalid private key format"

```bash
# Verify PEM format
head -n 1 private-key.pem
# Should show: -----BEGIN RSA PRIVATE KEY-----

# Convert if needed (OpenSSH format → PEM)
ssh-keygen -p -m PEM -f private-key.pem
```

---

## 📊 Security Audit Checklist

- [ ] Private key stored in Secrets Manager (not in code)
- [ ] Webhook secret is strong (>= 32 characters)
- [ ] Environment variables not committed to git
- [ ] IAM role follows least privilege principle
- [ ] Secrets Manager access logged in CloudTrail
- [ ] Regular rotation schedule established
- [ ] Backup of secrets stored securely offline
- [ ] Access to secrets limited to required personnel

---

## 🔄 Multi-Environment Setup

### Development
```bash
export TF_VAR_github_app_id="123456"
export TF_VAR_github_webhook_secret="dev-secret"
aws secretsmanager create-secret --name github-app-private-key-dev --secret-string file://dev-key.pem
```

### Staging
```bash
export TF_VAR_github_app_id="123457"
export TF_VAR_github_webhook_secret="staging-secret"
aws secretsmanager create-secret --name github-app-private-key-staging --secret-string file://staging-key.pem
```

### Production
```bash
export TF_VAR_github_app_id="123458"
export TF_VAR_github_webhook_secret="prod-secret"
aws secretsmanager create-secret --name github-app-private-key-prod --secret-string file://prod-key.pem
```

---

## 📝 Quick Reference

**Environment Variables:**
```bash
TF_VAR_github_app_id          # GitHub App ID
TF_VAR_github_webhook_secret  # Webhook secret
AWS_PROFILE                   # AWS profile name
AWS_REGION                    # AWS region
```

**AWS Secrets:**
```
github-app-private-key-dev     # Dev private key
github-app-private-key-staging # Staging private key
github-app-private-key-prod    # Prod private key
```

**Files (NEVER commit):**
```
*.pem                          # Private keys
.env                           # Environment variables
terraform.tfstate              # Terraform state (use S3 backend)
```

---

**Status:** Ready for execution  
**Estimated Time:** 10 minutes  
**Next:** Run verification checklist, then proceed to deployment
