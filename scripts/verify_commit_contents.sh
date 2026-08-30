#!/bin/bash
# Verify commit contents before pushing
# MANDATORY: Run before every commit
# User requirement: "explicitly verify what is being committed"

set -e

echo "🔍 Pre-Commit Verification"
echo "=========================="
echo ""

# 1. Check git status
echo "📊 Git Status:"
git status --short
echo ""

# 2. List files to be committed
STAGED_FILES=$(git diff --cached --name-only)
if [ -z "$STAGED_FILES" ]; then
    echo "⚠️  WARNING: No files staged for commit!"
    exit 1
fi

echo "📁 Files to be committed:"
echo "$STAGED_FILES" | sed 's/^/  - /'
echo ""

# 3. Check for /tmp/ references
echo "🔍 Checking for /tmp/ references..."
TMP_REFS=$(git diff --cached | grep -i "${TMPDIR:-/tmp}/" || true)
if [ -n "$TMP_REFS" ]; then
    echo "❌ POLICY VIOLATION: Found /tmp/ references in staged changes:"
    echo "$TMP_REFS"
    echo ""
    echo "Action required: Remove all /tmp/ usage before committing"
    exit 1
fi
echo "✅ No /tmp/ references found"
echo ""

# 4. Show summary of changes
echo "📝 Change Summary:"
git diff --cached --stat
echo ""

# 5. Verify file locations
echo "🗂️  Verifying file locations..."
WRONG_LOCATION=false
while IFS= read -r file; do
    # Check if important files are in temporary-like or legacy root-report locations
    if [[ "$file" =~ ^(tmp/|temp/|/tmp/|/var/tmp/|\.reports/|reports/|_codex_reports/) ]]; then
        echo "❌ WRONG LOCATION: $file"
        echo "   → Should be in: .codex/, docs/, docs/archive/, or artifacts/"
        WRONG_LOCATION=true
    fi
done <<< "$STAGED_FILES"

if [ "$WRONG_LOCATION" = true ]; then
    echo ""
    echo "❌ Files in wrong locations detected!"
    exit 1
fi
echo "✅ All files in correct locations"
echo ""

# 6. Final confirmation
echo "✅ Pre-commit verification PASSED"
echo ""
echo "Next steps:"
echo "1. Review the changes above"
echo "2. If correct, commit with: git commit -m 'message'"
echo "3. Push with: git push"
echo ""

exit 0
