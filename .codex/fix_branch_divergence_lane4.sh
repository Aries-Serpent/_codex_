#!/bin/bash
# REMEDIATION SCRIPT — FIX #2: BRANCH REPAIR
# ===========================================
#
# This script repairs the 0D_base_ branch which is currently orphaned
# (has no merge base with main branch).
#
# PREREQUISITES:
#   - Full repository access (not shallow clone)
#   - Write permission to origin/0D_base_
#   - Git 2.40+
#
# EXECUTION:
#   bash .codex/fix_branch_divergence_lane4.sh
#
# TIME ESTIMATE: 2-5 minutes depending on network
#

set -e

echo "════════════════════════════════════════════════════════════════"
echo "BRANCH REPAIR SCRIPT — Fix #2 for PR #5325 LANE 4"
echo "════════════════════════════════════════════════════════════════"
echo

# Step 1: Verify we have full history
echo "Step 1: Checking repository state..."
SHALLOW=$(git rev-parse --is-shallow-repository 2>/dev/null || echo "unknown")
if [ "$SHALLOW" = "true" ]; then
    echo "  ⚠️  Repository is shallow. Fetching full history..."
    echo "     This may take 2-5 minutes..."
    git fetch --unshallow
    echo "  ✅ Full history fetched"
else
    echo "  ✅ Repository has full history"
fi
echo

# Step 2: Verify current state
echo "Step 2: Verifying branch divergence..."
if git merge-base --is-ancestor origin/main origin/0D_base_ 2>/dev/null; then
    echo "  ✅ Branches already have common ancestor — no repair needed!"
    echo "     Exiting."
    exit 0
else
    echo "  ❌ Branches are orphaned (no merge base)"
    echo "     Proceeding with repair..."
fi
echo

# Step 3: Check for uncommitted changes
echo "Step 3: Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    echo "  ❌ ERROR: You have uncommitted changes"
    echo "     Please commit or stash them first"
    exit 1
fi
echo "  ✅ Working directory clean"
echo

# Step 4: Repair the branch
echo "Step 4: Repairing 0D_base_ branch..."
echo "  Strategy: Create new 0D_base_ based on main"
echo

# Save current branch in case we need to rollback
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "  Current branch: $CURRENT_BRANCH"

# Create new branch from main
echo "  Creating new 0D_base_ from origin/main..."
git checkout -b 0D_base_new origin/main
echo "  ✅ New branch created"
echo

# Step 5: Verify the new branch
echo "Step 5: Verifying new branch state..."
echo "  Checking merge base with main..."
if git merge-base --is-ancestor origin/main HEAD; then
    echo "  ✅ Merge base verified"
else
    echo "  ❌ ERROR: Merge base verification failed"
    echo "     Cleaning up and exiting"
    git checkout "$CURRENT_BRANCH"
    git branch -D 0D_base_new
    exit 1
fi
echo

# Step 6: Force-push the repair
echo "Step 6: Force-pushing repaired branch..."
echo "  ⚠️  WARNING: This will FORCE-PUSH to origin/0D_base_"
read -p "  Do you want to proceed? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "  Cancelled. Cleaning up..."
    git checkout "$CURRENT_BRANCH"
    git branch -D 0D_base_new
    exit 0
fi
echo

echo "  Force-pushing 0D_base_new → origin/0D_base_..."
git push -f origin 0D_base_new:0D_base_
echo "  ✅ Force-push successful"
echo

# Step 7: Cleanup
echo "Step 7: Cleaning up..."
git checkout "$CURRENT_BRANCH" 2>/dev/null || git checkout main
git branch -D 0D_base_new
echo "  ✅ Cleanup complete"
echo

# Step 8: Final verification
echo "Step 8: Final verification..."
git fetch origin main 0D_base_
if git merge-base --is-ancestor origin/main origin/0D_base_; then
    echo "  ✅ SUCCESS: 0D_base_ is now properly based on main"
    echo
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ BRANCH REPAIR COMPLETE"
    echo "════════════════════════════════════════════════════════════════"
    echo
    echo "NEXT STEPS:"
    echo "  1. Go to PR #5325"
    echo "  2. Click 'Re-run failed jobs' to trigger branch-rebase-gate"
    echo "  3. Monitor for ✅ on the branch-rebase-gate check"
    echo
else
    echo "  ❌ ERROR: Verification failed"
    echo "     Manual investigation needed"
    exit 1
fi
