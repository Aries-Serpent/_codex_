# CREDENTIAL ROTATION PLAN — CODEX PLATFORM

**Severity:** CRITICAL  
**Timeline:** URGENT (0-8 hours from remediation completion)  
**Owner:** DevOps Lead / Security Operations  

---

## EXECUTIVE SUMMARY

28 hardcoded secrets were identified in the codebase. **2 CRITICAL secrets** were found in source code and must be rotated **immediately** to prevent unauthorized access.
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
**Affected Credentials:**
1. JWT Auth Secret (`codex-auth-change-me-in-production`)
2. Dev Secret Key (`codex-dev-secret-key-change-in-production`)

**Additional Credentials Requiring Audit:**
- API keys (OpenAI, GitHub, Stripe, etc.) — 26 instances
- Database passwords
- Service tokens (D365, Slack, etc.)

---

## CRITICAL PATH (0-2 HOURS)

### Phase 1: Immediate Credential Revocation

#### 1.1 Revoke Exposed JWT Secrets

```bash
# SSH into production environment
ssh ops@production.codex.example.com

# Step 1: Identify all systems using the old AUTH_SECRET_KEY
grep -r "codex-auth-change-me-in-production" /var/codex/secrets/ || echo "Not found in secrets store (good)"
grep -r "codex-dev-secret-key-change-in-production" /var/codex/secrets/ || echo "Not found in secrets store (good)"

# Step 2: Check application logs for recent authentication activity
tail -1000 /var/log/codex/auth.log | grep -i "secret\|token\|auth" | tail -20

# Step 3: Audit database for sessions/tokens issued with old key
# (Skip if using stateless JWT without DB tracking)
SELECT COUNT(*) FROM sessions WHERE created_at > NOW() - INTERVAL 30 DAY;

# Step 4: Generate new JWT secret
NEW_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
echo "New AUTH_SECRET_KEY: $NEW_SECRET"
```

#### 1.2 Update Secret Store

**Option A: AWS Secrets Manager**
```bash
# Update the secret (recommended: create new version)
aws secretsmanager update-secret \
  --secret-id codex/auth-secret-key \
  --secret-string "{\"AUTH_SECRET_KEY\": \"$NEW_SECRET\"}"

# Verify update
aws secretsmanager get-secret-value --secret-id codex/auth-secret-key
```

**Option B: GitHub Secrets (for CI/CD)**
```bash
# Update GitHub secret
gh secret set AUTH_SECRET_KEY --body "$NEW_SECRET"

# Verify (only shows last 4 chars)
gh secret list | grep AUTH_SECRET_KEY
```

**Option C: HashiCorp Vault**
```bash
# Authenticate to Vault
vault login -method=github

# Update secret
vault kv put secret/codex/auth AUTH_SECRET_KEY="$NEW_SECRET"

# Verify
vault kv get secret/codex/auth
```

#### 1.3 Deploy Updated Code & Configuration

```bash
# 1. Ensure code with hardcoded secrets removed is deployed
#    (Already done in remediation step)
git log -1 --oneline -- src/codex/api/auth_routes.py src/codex/auth/middleware.py
# Should show: "Remove hardcoded secrets, replace with env vars"

# 2. Set AUTH_SECRET_KEY environment variable
export AUTH_SECRET_KEY="$NEW_SECRET"

# 3. Restart application services
sudo systemctl restart codex-api
sudo systemctl restart codex-worker
sudo systemctl status codex-api codex-worker

# 4. Verify application is running
curl -s http://localhost:8000/health | jq .
# Expected: {"status":"healthy","timestamp":"..."}

# 5. Check logs for any authentication errors
tail -100 /var/log/codex/auth.log | grep -i error
# Expected: No "invalid token" or "secret" errors
```

---

## STANDARD ROTATION (2-8 HOURS)

### Phase 2: Audit & Rotate Additional Credentials

#### 2.1 Credentials Inventory & Status

| # | Type | Service | Count | Exposed | Priority | Status |
|----|------|---------|-------|---------|----------|--------|
| 1 | JWT Secrets | Internal | 2 | YES | CRITICAL | ⏳ In progress |
| 2 | API Keys | OpenAI | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 3 | API Keys | GitHub | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 4 | API Keys | Stripe | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 5 | API Keys | AWS | 2 | UNKNOWN | HIGH | ⏳ Pending |
| 6 | DB Passwords | PostgreSQL | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 7 | DB Passwords | MongoDB | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 8 | API Keys | Pinecone | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 9 | API Keys | Weaviate | 1 | UNKNOWN | HIGH | ⏳ Pending |
| 10 | Tokens | D365 | 1 | UNKNOWN | MEDIUM | ⏳ Pending |
| 11 | Tokens | Slack | 1 | UNKNOWN | MEDIUM | ⏳ Pending |
| 12 | Tokens | Twilio | 1 | UNKNOWN | MEDIUM | ⏳ Pending |

#### 2.2 Service-Specific Rotation Procedures

### GitHub Personal Access Token (PAT)

**Current Status:** Potentially exposed in git history  
**Impact:** Read/write access to repositories  
**Timeline:** Rotate within 1 hour

**Step 1: Generate new PAT**
```bash
# Via GitHub Web UI:
# 1. Go to: https://github.com/settings/tokens
# 2. Click "Generate new token (classic)"
# 3. Select scopes:
#    - repo (full control)
#    - admin:repo_hook
#    - read:user
# 4. Click "Generate token"
# 5. Copy token (can only see once)

NEW_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxx"
```

**Step 2: Update secret store**
```bash
# GitHub Secrets
gh secret set GITHUB_TOKEN --body "$NEW_GITHUB_TOKEN"

# AWS Secrets Manager
aws secretsmanager update-secret \
  --secret-id codex/github-token \
  --secret-string "{\"GITHUB_TOKEN\": \"$NEW_GITHUB_TOKEN\"}"
```

**Step 3: Verify new token works**
```bash
# Test authentication
curl -H "Authorization: token $NEW_GITHUB_TOKEN" \
  https://api.github.com/user

# Should return: { "login": "codex-bot", ... }
```

**Step 4: Revoke old token**
```bash
# Via GitHub Web UI:
# 1. Go to: https://github.com/settings/tokens
# 2. Find old token (if visible)
# 3. Click "Delete"

# Via API (if you have list permissions):
curl -X DELETE \
  -H "Authorization: token $NEW_GITHUB_TOKEN" \
  https://api.github.com/applications/CLIENT_ID/grants/TOKEN_ID
```

---

### OpenAI API Key

**Current Status:** Potentially exposed in git history  
**Impact:** Ability to use OpenAI API (cost implications)  
**Timeline:** Rotate within 2 hours

**Step 1: Generate new API key**
```bash
# Via OpenAI Web UI:
# 1. Go to: https://platform.openai.com/account/api-keys
# 2. Click "Create new secret key"
# 3. Copy key (can only see once)
# 4. Save in secure location

NEW_OPENAI_KEY="sk-xxxxxxxxxxxxxxxxxxxxx"
```

**Step 2: Update secret store**
```bash
# GitHub Secrets
gh secret set OPENAI_API_KEY --body "$NEW_OPENAI_KEY"

# AWS Secrets Manager
aws secretsmanager update-secret \
  --secret-id codex/openai-api-key \
  --secret-string "{\"OPENAI_API_KEY\": \"$NEW_OPENAI_KEY\"}"
```

**Step 3: Verify new key works**
```bash
export OPENAI_API_KEY="$NEW_OPENAI_KEY"

# Test API call
curl https://api.openai.com/v1/models \
  -H "Authorization: ******" | jq '.data | length'

# Should return: number of available models (expected: 20+)
```

**Step 4: Revoke old key**
```bash
# Via OpenAI Web UI:
# 1. Go to: https://platform.openai.com/account/api-keys
# 2. Find old key in the list
# 3. Click trash icon to delete
```

**Step 5: Monitor for unexpected usage**
```bash
# Via OpenAI Usage Dashboard:
# 1. Go to: https://platform.openai.com/account/billing/overview
# 2. Check usage timeline
# 3. Alert if unexpected spikes in usage with old key
```

---

### AWS Access Keys

**Current Status:** Potentially exposed in git history  
**Impact:** Full AWS account access  
**Timeline:** Rotate IMMEDIATELY (within 1 hour)

**Step 1: Generate new access key pair**
```bash
# Via AWS Console:
# 1. Go to: IAM > Users > [codex-bot user]
# 2. Security credentials tab
# 3. Click "Create access key"
# 4. Save Access Key ID and Secret Access Key

# Via AWS CLI (if you have credentials):
aws iam create-access-key --user-name codex-bot
# Output: AccessKeyId, SecretAccessKey
```

**Step 2: Update secret store**
```bash
# AWS Secrets Manager
aws secretsmanager update-secret \
  --secret-id codex/aws-credentials \
  --secret-string "{
    \"AWS_ACCESS_KEY_ID\": \"AKIAIOSFODNN7NEWEXAMPLE\",  <!-- pragma: allowlist secret -->
    \"AWS_SECRET_ACCESS_KEY\": \"new-secret-key-here\"
  }"

# GitHub Secrets
gh secret set AWS_ACCESS_KEY_ID --body "AKIAIOSFODNN7NEWEXAMPLE"
gh secret set AWS_SECRET_ACCESS_KEY --body "new-secret-key-here"
```

**Step 3: Verify new credentials work**
```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7NEWEXAMPLE"
export AWS_SECRET_ACCESS_KEY="new-secret-key-here"  <!-- pragma: allowlist secret -->

# Test AWS access
aws sts get-caller-identity
# Expected: { "UserId": "AIDAI...", "Account": "123456789", "Arn": "arn:aws:iam::..." }
```

**Step 4: Revoke old access key**
```bash
# Via AWS Console:
# 1. Go to: IAM > Users > [codex-bot user]
# 2. Security credentials tab
# 3. Find old access key
# 4. Click "Deactivate" (wait 24h before deleting)
# 5. After 24h, click "Delete"

# Or via CLI:
aws iam delete-access-key --user-name codex-bot --access-key-id AKIAIOSFODNN7OLDEXAMPLE  <!-- pragma: allowlist secret -->
```

---

### Database Passwords

**Current Status:** Potentially exposed in git history  
**Impact:** Direct database access  
**Timeline:** Rotate within 4 hours

#### PostgreSQL

```bash
# Step 1: Generate new password
NEW_DB_PASSWORD=$(openssl rand -base64 32)
echo "New password: $NEW_DB_PASSWORD"

# Step 2: Update password in database
psql -h production.db.example.com -U postgres << EOF
ALTER USER codex_user WITH PASSWORD '$NEW_DB_PASSWORD';
\du+ codex_user
EOF

# Step 3: Update secret store
aws secretsmanager update-secret \
  --secret-id codex/postgres-password \
  --secret-string "{
    \"POSTGRES_PASSWORD\": \"$NEW_DB_PASSWORD\",
    \"DATABASE_URL\": \"******db.example.com:5432/codex_db\"
  }"

# Step 4: Verify new password works
psql -h db.example.com -U codex_user -d codex_db -c "SELECT VERSION();"

# Step 5: Update application configuration
# (Restart application with new DATABASE_URL env var)
```

#### MongoDB

```bash
# Step 1: Generate new password
NEW_DB_PASSWORD=$(openssl rand -base64 32)
echo "New password: $NEW_DB_PASSWORD"

# Step 2: Update password in MongoDB
mongo -u admin -p "$OLD_PASSWORD" << EOF
use admin
db.changeUserPassword("codex_user", "$NEW_DB_PASSWORD")
EOF

# Step 3: Update secret store
aws secretsmanager update-secret \
  --secret-id codex/mongodb-password \
  --secret-string "{
    \"MONGODB_PASSWORD\": \"$NEW_DB_PASSWORD\",
    \"MONGODB_URL\": \"******db.example.com:27017/codex_db\"
  }"

# Step 4: Verify new password works
mongo -u codex_user -p "$NEW_DB_PASSWORD" --authenticationDatabase codex_db
```

---

### Stripe API Keys

**Current Status:** Potentially exposed in git history  
**Impact:** Ability to process payments, view customer data  
**Timeline:** Rotate within 3 hours

```bash
# Step 1: Generate new API keys
# Via Stripe Dashboard:
# 1. Go to: https://dashboard.stripe.com/account/apikeys
# 2. Under "Secret key", click "Reveal test/live key"
# 3. To rotate: no direct rotation option; must create new key:
#    - Go to: https://dashboard.stripe.com/account/apikeys/create
#    - Create new restricted key with same permissions
#    - Copy new key

NEW_STRIPE_SK="sk_live_new_secret_key_here"
NEW_STRIPE_PK="pk_live_new_public_key_here"

# Step 2: Update secret store
aws secretsmanager update-secret \
  --secret-id codex/stripe-keys \
  --secret-string "{
    \"STRIPE_API_KEY\": \"$NEW_STRIPE_SK\",
    \"STRIPE_PUBLISHABLE_KEY\": \"$NEW_STRIPE_PK\"
  }"

# Step 3: Verify new keys work
curl https://api.stripe.com/v1/customers \
  -H "Authorization: ******" | jq '.data | length'

# Step 4: Monitor for unauthorized charges
# Via Stripe Dashboard:
# 1. Go to: https://dashboard.stripe.com/payments
# 2. Filter by date (since old key was potentially exposed)
# 3. Review all charges for authorization
# 4. If unauthorized: https://stripe.com/docs/disputes

# Step 5: Optionally revoke old API key
# Note: Stripe doesn't support revocation; old key will continue to work
# Recommendation: Track which application uses which key to detect misuse
```

---

## VERIFICATION CHECKLIST

After rotating each credential, verify:

```bash
# General verification script
verify_credential_rotation() {
  local service=$1
  local test_cmd=$2
  
  echo "Verifying $service..."
  if eval "$test_cmd"; then
    echo "✅ $service: OK"
    return 0
  else
    echo "❌ $service: FAILED"
    return 1
  fi
}

# Example verifications
verify_credential_rotation "GitHub" "gh auth status"
verify_credential_rotation "OpenAI" "curl -s https://api.openai.com/v1/models -H 'Authorization: ******' | jq -e '.data' > /dev/null"
verify_credential_rotation "AWS" "aws sts get-caller-identity"
verify_credential_rotation "PostgreSQL" "psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c 'SELECT 1' > /dev/null"
```

---

## AUDIT & MONITORING

### Post-Rotation Audit

```bash
# 1. Check for unexpected API usage with old credentials
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::IAM::AccessKey

# 2. Review authentication failures
tail -1000 /var/log/codex/auth.log | grep -i "invalid\|unauthorized\|failed" | wc -l

# 3. Check for unauthorized Stripe charges
# (See Stripe Dashboard: Payments > filter by date)

# 4. Review GitHub API calls
gh api user/authorizations --paginate | grep -i "scopes\|app"

# 5. Check OpenAI API usage
# (See OpenAI Dashboard: Usage > breakdown by model/endpoint)
```

### Monitoring Setup

```bash
# Enable CloudWatch alarms for suspicious activity
aws cloudwatch put-metric-alarm \
  --alarm-name "Codex-API-Auth-Failures" \
  --alarm-description "Alert on unusual authentication failures" \
  --metric-name "AuthenticationFailures" \
  --namespace "Codex/API" \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold

# Enable VPC Flow Logs to detect unusual network patterns
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs
```

---

## INCIDENT RESPONSE

### If Credential Compromise is Detected

1. **IMMEDIATE:**
   - Revoke compromised credential immediately
   - Generate new credential
   - Update all systems using old credential
   - Restart affected services

2. **WITHIN 1 HOUR:**
   - Review access logs for unauthorized activity
   - Check for data exfiltration
   - Monitor service metrics for anomalies
   - Notify security team and management

3. **WITHIN 4 HOURS:**
   - Complete incident report
   - Review security controls that failed to prevent this
   - Implement additional monitoring
   - Brief affected teams

4. **WITHIN 24 HOURS:**
   - Post-mortem analysis
   - Root cause analysis
   - Process improvements
   - Update security policies

---

## SIGN-OFF

**Rotation Status:**

| Credential | Rotation Date | Rotated By | Verified By | Status |
|-----------|---------------|-----------|------------|--------|
| AUTH_SECRET_KEY | [DATE] | [NAME] | [NAME] | ⏳ Pending |
| GITHUB_TOKEN | [DATE] | [NAME] | [NAME] | ⏳ Pending |
| OPENAI_API_KEY | [DATE] | [NAME] | [NAME] | ⏳ Pending |
| AWS Keys | [DATE] | [NAME] | [NAME] | ⏳ Pending |
| DB Passwords | [DATE] | [NAME] | [NAME] | ⏳ Pending |
| Stripe Keys | [DATE] | [NAME] | [NAME] | ⏳ Pending |
| [Others] | [DATE] | [NAME] | [NAME] | ⏳ Pending |

---

**Document Version:** 1.0  
**Created:** 2026-06-17  
**Last Updated:** 2026-06-17  
**Next Review:** 2026-07-17 (monthly rotation review)
