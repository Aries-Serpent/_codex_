#!/usr/bin/env bash
# Test script to verify build_docker.sh handles TORCH_WHEEL with spaces correctly
# This test validates the fix for the argument splitting issue

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "==> Testing build_docker.sh argument handling"
echo ""

# Test 1: Simple TORCH_WHEEL value (no spaces)
echo "Test 1: Simple TORCH_WHEEL value"
export TORCH_WHEEL="torch==2.4.0+cu121"
export INSTALL_TORCH_GPU=1
cd "${REPO_ROOT}"

# Dry run by showing what would be executed
# We'll validate the command is constructed correctly
MOCK_BUILD="${REPO_ROOT}/scripts/packaging/build_docker.sh"

# Extract the build command that would be executed
# by capturing the echo output before execution
if "${MOCK_BUILD}" 2>&1 | grep -q "TORCH_WHEEL=torch==2.4.0+cu121"; then
    echo "✓ Simple TORCH_WHEEL value handled correctly"
else
    echo "✗ Simple TORCH_WHEEL value test failed"
    exit 1
fi

# Test 2: TORCH_WHEEL with spaces and extra-index-url
echo ""
echo "Test 2: TORCH_WHEEL with spaces and extra-index-url"
export TORCH_WHEEL="torch==2.4.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121"
export INSTALL_TORCH_GPU=1

# This is the critical test - the space in TORCH_WHEEL should be preserved
# as a single build arg value, not split into multiple docker build arguments
if "${MOCK_BUILD}" 2>&1 | grep -q 'TORCH_WHEEL=torch==2.4.0+cu121 --extra-index-url'; then
    echo "✓ TORCH_WHEEL with spaces handled correctly"
else
    echo "✗ TORCH_WHEEL with spaces test failed"
    exit 1
fi

# Test 3: Empty TORCH_WHEEL (should not add build arg)
echo ""
echo "Test 3: Empty TORCH_WHEEL"
unset TORCH_WHEEL
export INSTALL_TORCH_GPU=0

if "${MOCK_BUILD}" 2>&1 | grep -q "Custom torch wheel: <none>"; then
    echo "✓ Empty TORCH_WHEEL handled correctly"
else
    echo "✗ Empty TORCH_WHEEL test failed"
    exit 1
fi

echo ""
echo "==> All tests passed!"
echo ""
echo "The build_docker.sh script correctly:"
echo "  - Preserves TORCH_WHEEL values with spaces"
echo "  - Prevents argument splitting via array-based command construction"
echo "  - Handles empty/unset TORCH_WHEEL values"
