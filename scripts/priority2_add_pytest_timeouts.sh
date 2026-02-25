#!/usr/bin/env bash
# Priority 2.2: Add --timeout flag to pytest executions
# Created: 2026-02-14 for PR #3248 Priority 2 validation

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/.github/workflows"

echo "=== Priority 2.2: Add --timeout to pytest executions ==="
echo "Starting systematic pytest timeout addition..."

# Counter
MODIFIED=0
SKIPPED=0

# Find workflows with pytest but no --timeout
WORKFLOWS_NEEDING_TIMEOUT=$(grep -l "pytest" *.yml | xargs grep -L "\--timeout" || true)

if [ -z "$WORKFLOWS_NEEDING_TIMEOUT" ]; then
    echo "✓ All pytest executions already have --timeout configured"
    exit 0
fi

echo ""
echo "Found workflows needing pytest --timeout:"
echo "$WORKFLOWS_NEEDING_TIMEOUT" | nl
echo ""

# Process each workflow
for workflow in $WORKFLOWS_NEEDING_TIMEOUT; do
    echo "Processing: $workflow"

    # Check if workflow actually has pytest commands
    if ! grep -q "pytest" "$workflow"; then
        echo "  - No pytest found"
        ((SKIPPED++))
        continue
    fi

    # Add --timeout=300 to pytest commands that don't have it
    # Handle various pytest invocation patterns
    sed -i.bak '
        # Pattern 1: pytest with arguments
        s/pytest \([^|&]*\)$/pytest \1 --timeout=300/
        # Pattern 2: python -m pytest
        s/python -m pytest \([^|&]*\)$/python -m pytest \1 --timeout=300/
        # Pattern 3: Remove duplicate --timeout flags
        s/--timeout=[0-9]* --timeout=[0-9]*/--timeout=300/g
        # Pattern 4: Clean up trailing spaces before timeout
        s/  *--timeout=300/ --timeout=300/g
    ' "$workflow"

    # Check if changes were made
    if ! cmp -s "$workflow" "$workflow.bak"; then
        rm "$workflow.bak"

        # Verify at least one pytest now has --timeout
        if grep -q "pytest.*--timeout" "$workflow"; then
            echo "  ✓ Added --timeout=300 to pytest commands"
            ((MODIFIED++))
        else
            echo "  ⚠️ No pytest commands modified"
            ((SKIPPED++))
        fi
    else
        rm "$workflow.bak"
        echo "  - Already has --timeout"
        ((SKIPPED++))
    fi
done

echo ""
echo "=== Summary ==="
echo "Modified: $MODIFIED workflows"
echo "Skipped: $SKIPPED workflows"
echo ""

if [ $MODIFIED -gt 0 ]; then
    echo "✓ Priority 2.2 complete - $MODIFIED workflows updated with pytest timeout protection"
else
    echo "✓ Priority 2.2 complete - All pytest executions already configured"
fi
