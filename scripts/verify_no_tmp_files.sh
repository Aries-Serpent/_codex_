#!/bin/bash
# Verify no important files are left in /tmp/
# MANDATORY: Run before every commit
# Policy: .github/TEMPORARY_FILES_POLICY.md

set -e

echo "🔍 Checking for important files in /tmp/..."

# Check for common important file types in /tmp/
TMP_FILES=$(find /tmp -type f \( \
    -name "*.md" -o \
    -name "*.txt" -o \
    -name "*.json" -o \
    -name "*.yaml" -o \
    -name "*.yml" -o \
    -name "*.py" -o \
    -name "*.sh" -o \
    -name "*analysis*" -o \
    -name "*report*" -o \
    -name "*summary*" -o \
    -name "*followup*" -o \
    -name "*plan*" -o \
    -name "*guide*" \
\) 2>/dev/null || true)

if [ -n "$TMP_FILES" ]; then
    echo "❌ POLICY VIOLATION: Important files found in /tmp/"
    echo ""
    echo "Files found:"
    echo "$TMP_FILES" | head -20
    echo ""
    echo "📋 Policy: .github/TEMPORARY_FILES_POLICY.md"
    echo "⚠️  These files will be LOST when /tmp/ is cleared!"
    echo ""
    echo "Action required:"
    echo "1. Move these files to proper repository locations:"
    echo "   - .codex/           → Session data, analysis, reports"
    echo "   - docs/             → Documentation"
    echo "   - .codex/reports/    → Generated reports"
    echo "   - artifacts/        → Build artifacts"
    echo ""
    echo "2. Run: mv /tmp/filename .codex/filename"
    echo "3. Commit: git add .codex/filename && git commit"
    echo "4. Clean up: rm /tmp/filename"
    echo ""
    exit 1
fi

echo "✅ No important files in /tmp/ - Policy compliant"
exit 0
