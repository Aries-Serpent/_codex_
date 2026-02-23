#!/usr/bin/env bash
# Priority 2: Apply timeout-minutes to workflows missing it
# Created: 2026-02-14 for PR #3248 Priority 2 validation

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/.github/workflows"

echo "=== Priority 2.1: Apply timeout-minutes to workflows ==="
echo "Starting systematic timeout addition..."

# Create backup
BACKUP_DIR="../workflows.backup.$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *.yml "$BACKUP_DIR/"
echo "✓ Backup created: $BACKUP_DIR"

# Counter
MODIFIED=0
SKIPPED=0

# Get workflows without timeout-minutes
WORKFLOWS_WITHOUT_TIMEOUT=$(grep -L "timeout-minutes" *.yml || true)

if [ -z "$WORKFLOWS_WITHOUT_TIMEOUT" ]; then
    echo "✓ All workflows already have timeout-minutes configured"
    exit 0
fi

echo ""
echo "Found workflows needing timeout-minutes:"
echo "$WORKFLOWS_WITHOUT_TIMEOUT" | nl
echo ""

# Process each workflow
for workflow in $WORKFLOWS_WITHOUT_TIMEOUT; do
    echo "Processing: $workflow"
    
    # Check if workflow has jobs section
    if ! grep -q "^jobs:" "$workflow"; then
        echo "  ⚠️ Skipped (no jobs section found)"
        ((SKIPPED++))
        continue
    fi
    
    # Find all job definitions and add timeout after runs-on
    # Use awk to process YAML structure carefully
    awk '
    /^  [a-zA-Z0-9_-]+:/ {
        in_job = 1
        job_has_timeout = 0
        print
        next
    }
    in_job && /^    runs-on:/ {
        print
        if (!job_has_timeout) {
            print "    timeout-minutes: 60"
            job_has_timeout = 1
        }
        next
    }
    in_job && /^    timeout-minutes:/ {
        job_has_timeout = 1
    }
    /^[a-zA-Z]/ && in_job {
        in_job = 0
    }
    { print }
    ' "$workflow" > "$workflow.tmp"
    
    # Check if changes were made
    if ! cmp -s "$workflow" "$workflow.tmp"; then
        mv "$workflow.tmp" "$workflow"
        echo "  ✓ Added timeout-minutes: 60"
        ((MODIFIED++))
    else
        rm "$workflow.tmp"
        echo "  - No changes needed"
        ((SKIPPED++))
    fi
done

echo ""
echo "=== Summary ==="
echo "Modified: $MODIFIED workflows"
echo "Skipped: $SKIPPED workflows"
echo "Backup: $BACKUP_DIR"
echo ""

if [ $MODIFIED -gt 0 ]; then
    echo "✓ Priority 2.1 complete - $MODIFIED workflows updated with timeout protection"
else
    echo "✓ Priority 2.1 complete - All workflows already configured"
fi
