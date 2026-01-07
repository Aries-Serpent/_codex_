#!/bin/bash
#
# Cherry-Pick Ideal Versions into Current Branch
#
# This script checks out the corrected file versions from commit 723f131
# (the main revert commit) and applies them to the current branch.
#
# This effectively "cherry-picks" the ideal file versions without doing
# an actual git cherry-pick (which can cause conflicts).
#

set -e  # Exit on error

echo "=========================================="
echo "Cherry-Pick Ideal File Versions"
echo "=========================================="
echo ""

# The commit with all our corrections
IDEAL_COMMIT="723f131"
BASE_COMMIT="bb92fab"

echo "Source commit: $IDEAL_COMMIT (Main revert with 2,515 fixes)"
echo "Base commit:   $BASE_COMMIT (Starting point)"
echo ""

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Confirm with user (or skip if running automated)
if [ -t 0 ]; then
    read -p "Proceed to checkout ideal versions? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

echo "Getting list of changed files from $IDEAL_COMMIT..."
echo ""

# Get list of all files that were changed in the ideal commit
CHANGED_FILES=$(git diff --name-only $BASE_COMMIT $IDEAL_COMMIT)

if [ -z "$CHANGED_FILES" ]; then
    echo "No files found to update"
    exit 0
fi

# Count files
NUM_FILES=$(echo "$CHANGED_FILES" | wc -l)
echo "Found $NUM_FILES files to update from ideal commit"
echo ""

# Confirm again for large number of files
if [ $NUM_FILES -gt 100 ] && [ -t 0 ]; then
    echo "⚠️  This will update $NUM_FILES files!"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

echo "Checking out files from $IDEAL_COMMIT..."
echo ""

SUCCESS=0
FAILED=0

# Checkout each file from the ideal commit
while IFS= read -r file; do
    if [ -n "$file" ]; then
        echo -n "  Updating $file... "
        
        if git checkout $IDEAL_COMMIT -- "$file" 2>/dev/null; then
            echo "✓"
            ((SUCCESS++))
        else
            echo "✗"
            ((FAILED++))
        fi
    fi
done <<< "$CHANGED_FILES"

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""
echo "Files updated:   $SUCCESS"
echo "Files failed:    $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All files successfully updated to ideal versions!"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Review diff: git diff"
    echo "  3. Commit: git commit -m 'Apply ideal versions from 723f131'"
    echo "  4. Push: git push origin $CURRENT_BRANCH"
    echo ""
else
    echo "⚠️  Some files failed to update"
    echo ""
    echo "You may need to manually handle these files."
    echo ""
fi

# Show status
echo "Current git status:"
git status --short | head -20
if [ $(git status --short | wc -l) -gt 20 ]; then
    echo "... and more"
fi

exit 0
