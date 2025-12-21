# GitHub App Setup Guide

## Create GitHub App

1. Go to https://github.com/settings/apps/new
2. Fill in details:
   - **Name:** Codex PR Reviewer
   - **Homepage:** https://github.com/Aries-Serpent/_codex_
   - **Webhook URL:** (get after deployment)
   - **Webhook Secret:** Generate strong random string

3. **Permissions:**
   - Contents: Read-only
   - Pull requests: Read & write
   - Issues: Read & write
   - Checks: Read & write

4. **Subscribe to events:**
   - Pull request
   - Pull request review
   - Issue comment

5. **Create App** → Save App ID and generate private key

## Store Secrets

```bash
# Store private key in AWS Secrets Manager
aws secretsmanager create-secret \
    --name github-app-private-key-dev \
    --secret-string file://private-key.pem \
    --region us-east-1

# Set environment variables
export TF_VAR_github_app_id="YOUR_APP_ID"
export TF_VAR_github_webhook_secret="YOUR_WEBHOOK_SECRET"
```

## Deploy

```bash
cd deploy/scripts
./deploy.sh dev apply
```

## Configure Webhook

After deployment, get webhook URL:
```bash
cd ../terraform
terraform output webhook_url
```

Update GitHub App webhook URL with this value.

## Install App

1. Go to app settings
2. Click "Install App"
3. Select repositories
4. Authorize

✅ Done! Agent will now review PRs.
