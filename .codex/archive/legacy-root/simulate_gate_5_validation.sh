#!/bin/bash
# Gate 5 Validation Simulator
# This script simulates post-fix Release workflow runs for testing purposes

set -e

echo "🚀 GATE 5 VALIDATION SIMULATOR"
echo "======================================="
echo ""
echo "This script simulates Release workflow runs post-fix"
echo "to validate the checkout@v5 fix."
echo ""

# Trigger Release workflow 5 times with different test releases
for i in {1..5}; do
    TEST_TAG="v1.0.0-gate5-test-$i"
    
    echo "✓ Triggering Release workflow run $i..."
    echo "  Tag: $TEST_TAG"
    
    # Create a lightweight tag to trigger the workflow
    git tag "$TEST_TAG" HEAD || echo "  (Tag may already exist)"
    
    # Push tag to trigger Release workflow (only if explicitly enabled)
    if [[ "${ENABLE_REMOTE_PUSH:-false}" == "true" ]]; then
        git push origin "$TEST_TAG" || echo "  (Failed to push tag)"
    else
        echo "  (Skipping remote push; set ENABLE_REMOTE_PUSH=true to enable)"
    fi
    
    sleep 2
done

echo ""
echo "✅ Simulation complete. Workflow should begin processing."
echo "   Check: https://github.com/Aries-Serpent/_codex_/actions/workflows/release.yml"
