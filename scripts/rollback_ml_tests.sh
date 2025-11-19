#!/bin/bash
# Rollback ML test suite if breaking changes occur

set -e

echo "🔄 Rolling back ML test suite..."

# Disable test workflows in CI
if [ -f .github/workflows/ml-tests.yml ]; then
    mv .github/workflows/ml-tests.yml .github/workflows/ml-tests.yml.disabled
    echo "✓ Disabled ML test CI workflow"
fi

# Optional: Remove test files
read -p "Remove test files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f tests/training/test_engine_hf_trainer_comprehensive.py
    rm -f tests/data/test_dataset_loaders_comprehensive.py
    rm -f tests/metrics/test_metrics_comprehensive.py
    rm -f tests/callbacks/test_callbacks_comprehensive.py
    rm -f tests/checkpointing/test_checkpoint_comprehensive.py
    rm -f tests/integration/test_ml_pipeline_integration.py
    echo "✓ Removed comprehensive test files"
fi

# Create bypass environment variable
cat >> .env << 'EOF'
# ML Test Suite Bypass
SKIP_ML_TESTS=1
EOF

echo "✓ Added SKIP_ML_TESTS bypass variable"

# Update pytest config to skip tests
if [ -f pytest.ini ]; then
    cat >> pytest.ini << 'EOF'

# Temporarily skip ML tests
[pytest]
addopts = -m "not ml_comprehensive"
EOF
    echo "✓ Updated pytest.ini to skip comprehensive tests"
fi

echo ""
echo "✅ Rollback complete"
echo ""
echo "To re-enable:"
echo "  1. mv .github/workflows/ml-tests.yml.disabled .github/workflows/ml-tests.yml"
echo "  2. Remove SKIP_ML_TESTS from .env"
echo "  3. Revert pytest.ini changes"
echo "  4. git checkout tests/"
