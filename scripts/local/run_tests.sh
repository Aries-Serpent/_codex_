#!/bin/bash
# Run MSP tests offline
# Usage: bash scripts/local/run_tests.sh

set -e

echo "==================================="
echo "MSP Tests - Offline Runner"
echo "==================================="

# Set environment for offline testing
export MSP_OFFLINE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# Create test directories
mkdir -p .codex/logs
mkdir -p .codex/tenants
mkdir -p artifacts/emb

echo "Running MSP tests..."
echo ""

# Run pytest with offline markers
if command -v pytest &> /dev/null; then
    pytest tests/test_msp_*.py \
        tests/test_retrieval_pipeline.py \
        tests/test_policy_enforcement.py \
        -v \
        --tb=short \
        -m "not external" \
        --disable-warnings
else
    echo "Warning: pytest not installed. Skipping tests."
    echo "Install with: pip install pytest"
    exit 1
fi

echo ""
echo "==================================="
echo "Tests complete!"
echo "==================================="
