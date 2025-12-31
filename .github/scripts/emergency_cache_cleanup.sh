#!/bin/bash
# Emergency Cache Cleanup Script
# Purpose: Reduce cache usage to under 7 GB (70% capacity)
# Priority: P0 CRITICAL - Repository cache management

set -euo pipefail

echo "=========================================="
echo "🚨 EMERGENCY CACHE CLEANUP - PHASE 1"
echo "=========================================="
echo ""
echo "Target: < 7 GB (70% of 10 GB limit)"
echo "Strategy: Remove old, duplicate, and PR-specific caches"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "   Install: https://cli.github.com/"
    exit 1
fi

# Verify authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Step 1: List all caches with sizes
echo "📊 Step 1: Analyzing current caches..."
echo ""

# Create temp directory following anti-/tmp/ protection system
TEMP_DIR=".github/tmp"
mkdir -p "$TEMP_DIR"

gh cache list --json key,id,sizeInBytes,createdAt,ref,lastAccessedAt --limit 50 > "$TEMP_DIR/cache_list.json"

echo "Cache Summary:"
echo "=============="
jq -r '.[] | "\(.sizeInBytes / 1024 / 1024 | floor) MB\t\(.key[:60])\t\(.ref)"' "$TEMP_DIR/cache_list.json" | \
    sort -rn | head -20

echo ""
echo "Total caches:" $(jq length "$TEMP_DIR/cache_list.json")
TOTAL_SIZE=$(jq '[.[].sizeInBytes] | add' "$TEMP_DIR/cache_list.json")
TOTAL_SIZE_MB=$((TOTAL_SIZE / 1024 / 1024))
echo "Total size: ${TOTAL_SIZE_MB} MB"
echo ""

# Step 2: Delete PR #2668 cache (4.4 GB)
echo "🗑️  Step 2: Deleting PR #2668 cache (4.4 GB)..."
echo ""

PR_CACHE_IDS=$(jq -r '.[] | select(.ref == "refs/pull/2668/merge") | select(.key | contains("Unified Security Suite")) | .id' "$TEMP_DIR/cache_list.json")

if [ -n "$PR_CACHE_IDS" ]; then
    for CACHE_ID in $PR_CACHE_IDS; do
        echo "Deleting cache ID: $CACHE_ID"
        gh cache delete "$CACHE_ID" --confirm || echo "  ⚠️  Already deleted or not found"
    done
    echo "✅ PR #2668 cache deleted (~4.4 GB freed)"
else
    echo "⚠️  PR #2668 cache not found (may already be deleted)"
fi

echo ""

# Step 3: Delete duplicate pip caches (keep only most recent)
echo "🗑️  Step 3: Cleaning duplicate pip caches..."
echo ""

# Group pip caches by branch and keep only the most recent
jq -r '.[] | select(.key | startswith("Linux-pip")) | "\(.ref)\t\(.createdAt)\t\(.id)"' "$TEMP_DIR/cache_list.json" | \
    sort -k1,1 -k2,2r | \
    awk '{
        if (seen[$1]++ > 0) {
            print $3
        }
    }' > "$TEMP_DIR/duplicate_cache_ids.txt"

if [ -s "$TEMP_DIR/duplicate_cache_ids.txt" ]; then
    echo "Found $(wc -l < "$TEMP_DIR/duplicate_cache_ids.txt") duplicate pip caches to delete"
    while IFS= read -r CACHE_ID; do
        echo "Deleting duplicate cache ID: $CACHE_ID"
        gh cache delete "$CACHE_ID" --confirm || echo "  ⚠️  Already deleted or not found"
    done < "$TEMP_DIR/duplicate_cache_ids.txt"
    echo "✅ Duplicate pip caches cleaned"
else
    echo "✅ No duplicate pip caches found"
fi

echo ""

# Step 4: Delete old caches (older than 7 days)
echo "🗑️  Step 4: Deleting caches older than 7 days..."
echo ""

SEVEN_DAYS_AGO=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v -7d +%Y-%m-%dT%H:%M:%SZ)

jq -r --arg cutoff "$SEVEN_DAYS_AGO" '.[] | select(.createdAt < $cutoff) | .id' "$TEMP_DIR/cache_list.json" > "$TEMP_DIR/old_cache_ids.txt"

if [ -s "$TEMP_DIR/old_cache_ids.txt" ]; then
    echo "Found $(wc -l < "$TEMP_DIR/old_cache_ids.txt") caches older than 7 days"
    while IFS= read -r CACHE_ID; do
        echo "Deleting old cache ID: $CACHE_ID"
        gh cache delete "$CACHE_ID" --confirm || echo "  ⚠️  Already deleted or not found"
    done < "$TEMP_DIR/old_cache_ids.txt"
    echo "✅ Old caches deleted"
else
    echo "✅ No caches older than 7 days"
fi

echo ""

# Step 5: Final status check
echo "📊 Step 5: Verifying cleanup results..."
echo ""

sleep 3  # Wait for GitHub to update cache list

gh cache list --json key,sizeInBytes --limit 50 > "$TEMP_DIR/cache_list_after.json"

TOTAL_SIZE_AFTER=$(jq '[.[].sizeInBytes] | add // 0' "$TEMP_DIR/cache_list_after.json")
TOTAL_SIZE_AFTER_MB=$((TOTAL_SIZE_AFTER / 1024 / 1024))
TOTAL_SIZE_AFTER_GB=$(echo "scale=2; $TOTAL_SIZE_AFTER_MB / 1024" | bc)

echo "=========================================="
echo "✅ CLEANUP COMPLETE"
echo "=========================================="
echo ""
echo "Before: ${TOTAL_SIZE_MB} MB ($(echo "scale=2; $TOTAL_SIZE_MB / 1024" | bc) GB)"
echo "After:  ${TOTAL_SIZE_AFTER_MB} MB (${TOTAL_SIZE_AFTER_GB} GB)"
echo "Freed:  $((TOTAL_SIZE_MB - TOTAL_SIZE_AFTER_MB)) MB"
echo ""

if [ "$TOTAL_SIZE_AFTER_MB" -lt 7000 ]; then
    echo "✅ SUCCESS: Cache usage is now under 7 GB (70% capacity)"
    echo "   Safe to proceed with Phase 3C-Lite"
else
    echo "⚠️  WARNING: Cache usage still high (${TOTAL_SIZE_AFTER_GB} GB)"
    echo "   Consider manual review of remaining caches"
fi

echo ""
echo "Remaining caches:"
jq -r '.[] | "\(.sizeInBytes / 1024 / 1024 | floor) MB\t\(.key[:60])"' "$TEMP_DIR/cache_list_after.json" | \
    sort -rn | head -10

# Cleanup temp files (keep in .github/tmp for audit trail)
echo ""
echo "Temp files retained in $TEMP_DIR for audit trail"

echo ""
echo "=========================================="
echo "Next Steps:"
echo "1. Verify cache status in GitHub Actions UI"
echo "2. Proceed with Phase 3C-Lite implementation"
echo "=========================================="
