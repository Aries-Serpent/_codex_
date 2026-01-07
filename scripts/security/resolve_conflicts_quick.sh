#!/bin/bash
#
# Quick Merge Conflict Resolution for PR #2717
#
# This script automatically resolves merge conflicts by accepting
# all incoming changes (--ours) from the PR branch.
#
# Usage:
#   1. Attempt merge: git merge origin/0D_base_
#   2. Run this script: bash scripts/security/resolve_conflicts_quick.sh
#   3. Complete merge: git merge --continue
#

set -e  # Exit on error

echo "=========================================="
echo "PR #2717 Merge Conflict Resolver"
echo "=========================================="
echo ""

# Check if we're in a merge
if [ ! -f .git/MERGE_HEAD ]; then
    echo "❌ No merge in progress"
    echo ""
    echo "Please run this script AFTER starting a merge that has conflicts."
    echo ""
    echo "Example:"
    echo "  git merge origin/0D_base_"
    echo "  bash scripts/security/resolve_conflicts_quick.sh"
    echo ""
    exit 1
fi

echo "✓ Merge in progress detected"
echo ""

# Get list of conflicted files
CONFLICTS=$(git diff --name-only --diff-filter=U)

if [ -z "$CONFLICTS" ]; then
    echo "✓ No unresolved conflicts found"
    echo ""
    echo "The merge may already be resolved."
    echo "Run 'git merge --continue' to complete."
    exit 0
fi

# Count conflicts
NUM_CONFLICTS=$(echo "$CONFLICTS" | wc -l)
echo "Found $NUM_CONFLICTS files with conflicts"
echo ""

# Resolve each conflict by accepting our version
echo "Resolving conflicts (accepting incoming changes)..."
echo ""

RESOLVED=0
FAILED=0

while IFS= read -r file; do
    if [ -n "$file" ]; then
        echo -n "  Resolving $file... "
        
        if git checkout --ours "$file" 2>/dev/null && git add "$file" 2>/dev/null; then
            echo "✓"
            ((RESOLVED++))
        else
            echo "✗"
            ((FAILED++))
        fi
    fi
done <<< "$CONFLICTS"

echo ""
echo "=========================================="
echo "RESOLUTION SUMMARY"
echo "=========================================="
echo ""
echo "Total conflicts:      $NUM_CONFLICTS"
echo "Successfully resolved: $RESOLVED"
echo "Failed:               $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All conflicts resolved successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Complete merge: git merge --continue"
    echo ""
    exit 0
else
    echo "⚠️  Some conflicts could not be resolved automatically"
    echo ""
    echo "Please manually resolve failed files and then:"
    echo "  git merge --continue"
    echo ""
    exit 1
fi
