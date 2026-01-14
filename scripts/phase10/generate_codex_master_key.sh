#!/bin/bash
# Generate CODEX_MASTER_KEY
# Creates cryptographically secure 256-bit key for autonomous operations

echo "🔑 Generating CODEX_MASTER_KEY"
echo "================================"

# Check if openssl is available
if ! command -v openssl >/dev/null 2>&1; then
    echo "❌ OpenSSL not installed"
    echo "Install with: brew install openssl (macOS) or apt-get install openssl (Linux)"
    exit 1
fi

# Generate 256-bit key (32 bytes base64-encoded)
KEY=$(openssl rand -base64 32)

echo "✅ Key generated successfully"
echo ""
echo "🔒 CODEX_MASTER_KEY (store securely):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Security Notice:"
echo "- Do NOT commit this key to version control"
echo "- Store in GitHub Secrets immediately"
echo "- Rotate every 90 days"
echo "- Document rotation in .codex/key-archive/rotation-log.txt"
echo ""
echo "Add to GitHub Secrets:"
echo "1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name: CODEX_MASTER_KEY"
echo "4. Value: [paste key above]"
echo "5. Click 'Add secret'"
echo ""
echo "OR use GitHub CLI:"
echo "  echo '$KEY' | gh secret set CODEX_MASTER_KEY --repo Aries-Serpent/_codex_"
echo ""
echo "Verify configuration:"
echo "  gh secret list --repo Aries-Serpent/_codex_ | grep CODEX_MASTER_KEY"
