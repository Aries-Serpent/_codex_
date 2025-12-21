# Deployment Guide - GitHub Agent PR Reviewer

Complete infrastructure deployment using Terraform and AWS.

---

## 📋 Prerequisites

### Required Tools
- **Terraform** >= 1.0 ([Install](https://www.terraform.io/downloads))
- **AWS CLI** >= 2.0 ([Install](https://aws.amazon.com/cli/))
- **Python** >= 3.11
- **GitHub App** credentials

### AWS Requirements
- AWS account with appropriate permissions
- AWS credentials configured (`aws configure`)
- S3 bucket for Terraform state (optional but recommended)

### GitHub Requirements
- GitHub App created ([Guide](https://docs.github.com/en/developers/apps/creating-a-github-app))
- App ID
- Webhook secret
- Private key (PEM file)

---

## 🚀 Quick Start

### 1. Create GitHub App

```bash
# Navigate to GitHub Settings > Developer settings > GitHub Apps
# Or visit: https://github.com/settings/apps/new

# Required permissions:
# - Contents: Read-only
# - Pull requests: Read & write
# - Issues: Read & write
# - Checks: Read & write

# Webhook URL: (will get after deployment)
# Webhook secret: Generate a strong random string
```

### 2. Store GitHub Private Key in AWS Secrets Manager

```bash
# Store the private key
aws secretsmanager create-secret \
    --name github-app-private-key-dev \
    --description "GitHub App private key for Codex Reviewer (dev)" \
    --secret-string file://path/to/private-key.pem \
    --region us-east-1

# For staging
aws secretsmanager create-secret \
    --name github-app-private-key-staging \
    --secret-string file://path/to/private-key.pem \
    --region us-east-1

# For production
aws secretsmanager create-secret \
    --name github-app-private-key-prod \
    --secret-string file://path/to/private-key.pem \
    --region us-east-1
```

### 3. Set Environment Variables

```bash
# GitHub App credentials
export TF_VAR_github_app_id="123456"
export TF_VAR_github_webhook_secret="your-webhook-secret-here"

# AWS credentials (if not using aws configure)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 4. Deploy to Development

```bash
# Using deployment script (recommended)
cd .github/agents/deploy/scripts
./deploy.sh dev apply

# Or manually with Terraform
cd .github/agents/deploy/terraform
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

### 5. Configure GitHub App Webhook

```bash
# Get the webhook URL from Terraform output
terraform output webhook_url

# Update GitHub App settings:
# 1. Go to your GitHub App settings
# 2. Update Webhook URL with the output from above
# 3. Ensure webhook secret matches TF_VAR_github_webhook_secret
# 4. Save changes
```

### 6. Validate Deployment

```bash
# Test the webhook endpoint
./deploy.sh dev validate

# Or manually
WEBHOOK_URL=$(cd terraform && terraform output -raw webhook_url)
curl -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d '{"test": true}'
```

---

## 📦 Infrastructure Components

### AWS Resources Created

| Resource | Purpose | Cost Impact |
|----------|---------|-------------|
| **Lambda Function** | Agent execution | ~$0.20/1M requests |
| **API Gateway** | Webhook endpoint | ~$3.50/1M requests |
| **S3 Bucket** | Metrics storage | ~$0.023/GB/month |
| **CloudWatch Logs** | Logging | ~$0.50/GB ingested |
| **CloudWatch Dashboard** | Monitoring | ~$3/month |
| **Secrets Manager** | Private key storage | ~$0.40/secret/month |

**Estimated Monthly Cost (Low Traffic):** $5-10/month  
**Estimated Monthly Cost (High Traffic):** $20-50/month

### Architecture

```
GitHub → API Gateway → Lambda → S3 (Metrics)
                         ↓
                    CloudWatch (Logs/Metrics)
                         ↓
                    Secrets Manager (Keys)
```

---

## 🔧 Configuration

### Environment Files

- `dev.tfvars` - Development configuration
- `staging.tfvars` - Staging configuration
- `prod.tfvars` - Production configuration

### Customization

Edit `main.tf` to customize:
- Lambda memory size (default: 512MB)
- Lambda timeout (default: 300s)
- Log retention (default: 7 days dev, 30 days prod)
- Metrics archive policy (default: 90 days → Glacier)

---

## 📊 Monitoring

### CloudWatch Dashboard

Access via Terraform output:
```bash
terraform output cloudwatch_dashboard_url
```

**Metrics Tracked:**
- Lambda invocations
- Error count
- Duration (avg, p95, p99)
- Concurrent executions
- API Gateway requests
- 4XX/5XX errors
- Latency

### Alarms

Two alarms configured by default:
1. **Lambda Errors** - Triggers if >5 errors in 5 minutes
2. **Lambda Duration** - Triggers if avg duration >30s

Add SNS topic ARN to `alarm_actions` in `main.tf` for notifications.

### Logs

View Lambda logs:
```bash
aws logs tail /aws/lambda/codex-reviewer-agent-dev --follow
```

View API Gateway logs:
```bash
aws logs tail /aws/apigateway/codex-reviewer-dev --follow
```

---

## 🔒 Security

### Secrets Management

- GitHub private key stored in AWS Secrets Manager
- Lambda IAM role has minimal required permissions
- S3 bucket encrypted at rest (AES256)
- API Gateway uses HTTPS only
- CloudWatch logs encrypted

### Best Practices

1. **Rotate Secrets Regularly**
   ```bash
   aws secretsmanager rotate-secret \
       --secret-id github-app-private-key-prod
   ```

2. **Enable AWS CloudTrail** (for audit logging)
3. **Use IAM roles** instead of access keys where possible
4. **Restrict S3 bucket access** with bucket policies
5. **Enable VPC endpoints** for production (optional)

---

## 🧪 Testing

### Smoke Test

```bash
# Test webhook endpoint
WEBHOOK_URL=$(cd terraform && terraform output -raw webhook_url)

curl -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Event: ping" \
    -d '{"zen": "Design for failure."}'

# Expected response: 200 OK
```

### Integration Test

```bash
# Trigger a test PR review
# 1. Create a test PR in a repository where the app is installed
# 2. Check CloudWatch logs for activity
# 3. Verify review is posted to PR
```

---

## 🔄 Updates & Rollback

### Deploying Updates

```bash
# Plan changes
./deploy.sh dev plan

# Apply changes
./deploy.sh dev apply

# Updates are deployed with zero downtime (blue-green)
```

### Rollback

```bash
# Option 1: Revert code changes and redeploy
git revert <commit-hash>
./deploy.sh dev apply

# Option 2: Restore previous Lambda version
aws lambda update-function-code \
    --function-name codex-reviewer-agent-dev \
    --s3-bucket <previous-version-bucket> \
    --s3-key <previous-version-key>
```

---

## 🗑️ Cleanup

### Destroy Infrastructure

```bash
# Destroy environment
./deploy.sh dev destroy

# Or manually
cd terraform
terraform destroy -var-file=dev.tfvars
```

**Warning:** This will permanently delete all resources including S3 data!

### Cleanup Checklist

- [ ] Export important metrics from S3
- [ ] Delete GitHub App (if no longer needed)
- [ ] Delete secrets from Secrets Manager
- [ ] Remove webhook from GitHub App settings
- [ ] Verify all AWS resources deleted (check console)

---

## 📖 Troubleshooting

### Common Issues

#### "Webhook returns 403"
- **Cause:** Missing or invalid webhook secret
- **Fix:** Verify `TF_VAR_github_webhook_secret` matches GitHub App settings

#### "Lambda timeout"
- **Cause:** PR review taking longer than 300s
- **Fix:** Increase `timeout` in `main.tf`

#### "Access Denied to Secrets Manager"
- **Cause:** IAM role missing permissions
- **Fix:** Verify `lambda_policy` includes Secrets Manager permissions

#### "S3 bucket already exists"
- **Cause:** Bucket name collision
- **Fix:** Bucket names include account ID, check for typos

### Debug Commands

```bash
# Check Lambda function status
aws lambda get-function \
    --function-name codex-reviewer-agent-dev

# View recent Lambda invocations
aws lambda get-function-event-invoke-config \
    --function-name codex-reviewer-agent-dev

# Test Lambda directly
aws lambda invoke \
    --function-name codex-reviewer-agent-dev \
    --payload '{"test": true}' \
    response.json
```

---

## 📞 Support

### Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/)
- [GitHub Apps Documentation](https://docs.github.com/en/developers/apps)
- [Project README](../../README.md)

### Getting Help

1. Check CloudWatch logs for error details
2. Review Terraform output for resource ARNs
3. Consult TROUBLESHOOTING.md (if available)
4. Open GitHub issue with logs and configuration

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] GitHub App created
- [ ] Private key stored in Secrets Manager
- [ ] Environment variables set
- [ ] AWS credentials configured
- [ ] Terraform installed and working
- [ ] Code tested locally

### Deployment
- [ ] Terraform init successful
- [ ] Terraform plan reviewed
- [ ] Terraform apply successful
- [ ] Webhook URL configured in GitHub App
- [ ] Smoke test passed
- [ ] Integration test passed
- [ ] Monitoring dashboard accessible
- [ ] Alarms configured

### Post-Deployment
- [ ] Documentation updated
- [ ] Team notified
- [ ] Runbook created/updated
- [ ] Metrics baseline established
- [ ] Backup/recovery tested

---

**Deployment Status:** Infrastructure code complete ✅  
**Next:** Execute deployment to dev environment
