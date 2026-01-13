#!/bin/bash
# Validate Google Drive Secrets Configuration
# Checks if required secrets exist and are properly formatted

echo "🔒 Validating Google Drive Secrets"
echo "===================================="

# Check if gh CLI is available
if ! command -v gh >/dev/null 2>&1; then
    echo "❌ GitHub CLI (gh) not installed"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Check required secrets
REPO="Aries-Serpent/_codex_"
REQUIRED_SECRETS=(
    "GDRIVE_SERVICE_ACCOUNT_JSON"
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
)

OPTIONAL_SECRETS=(
    "NOTEBOOKLM_WEBHOOK_URL"
    "CODEX_MASTER_KEY"
)

echo "Checking required secrets..."
MISSING_REQUIRED=0

for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if gh secret list --repo "$REPO" | grep -q "^$SECRET"; then
        echo "✅ $SECRET configured"
    else
        echo "❌ $SECRET missing"
        MISSING_REQUIRED=1
    fi
done

echo ""
echo "Checking optional secrets..."
for SECRET in "${OPTIONAL_SECRETS[@]}"; do
    if gh secret list --repo "$REPO" | grep -q "^$SECRET"; then
        echo "✅ $SECRET configured"
    else
        echo "ℹ️  $SECRET not configured (optional)"
    fi
done

echo ""
if [ $MISSING_REQUIRED -eq 1 ]; then
    echo "❌ Missing required secrets!"
    echo ""
    echo "Setup instructions:"
    echo "1. Create Google Cloud Project: https://console.cloud.google.com/"
    echo "2. Enable Drive API"
    echo "3. Create Service Account and download JSON key"
    echo "4. Create OAuth 2.0 Client ID (Desktop app)"
    echo "5. Add secrets via GitHub UI:"
    echo "   https://github.com/$REPO/settings/secrets/actions"
    echo ""
    echo "OR use gh CLI:"
    echo "  cat service-account.json | gh secret set GDRIVE_SERVICE_ACCOUNT_JSON --repo $REPO"
    echo "  echo 'your-client-id' | gh secret set GOOGLE_CLIENT_ID --repo $REPO"
    echo "  echo 'your-client-secret' | gh secret set GOOGLE_CLIENT_SECRET --repo $REPO"
    exit 1
else
    echo "✅ All required secrets configured!"
    echo ""
    echo "Next steps:"
    echo "1. Trigger notebooklm-sync.yml workflow"
    echo "2. Verify XML uploaded to Google Drive"
    echo "3. Add XML source to NotebookLM"
fi
