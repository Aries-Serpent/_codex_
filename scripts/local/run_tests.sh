#!/usr/bin/env bash
# Run MSP tests offline
# Usage:
#   scripts/local/run_tests.sh [pytest_args...]
#
# Examples:
#   scripts/local/run_tests.sh
#   scripts/local/run_tests.sh -k test_retrieval
#   scripts/local/run_tests.sh --verbose --tb=long

set -euo pipefail

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# Load .env if present
if [[ -f ".env" ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
fi

# Set defaults for offline testing
: "${MSP_OFFLINE:=1}"
: "${PYTEST_DISABLE_PLUGIN_AUTOLOAD:=1}"

export MSP_OFFLINE PYTEST_DISABLE_PLUGIN_AUTOLOAD

# Create test directories
mkdir -p .codex/logs
mkdir -p .codex/tenants
mkdir -p artifacts/emb

echo "==================================="
echo "MSP Tests - Offline Runner"
echo "==================================="
echo "Repository:   ${REPO_ROOT}"
echo "Offline Mode: ${MSP_OFFLINE}"
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest not found. Install with:"
    echo "  pip install pytest"
    exit 1
fi

# Default test targets
TEST_FILES=(
    "tests/test_msp_*.py"
    "tests/test_retrieval_pipeline.py"
    "tests/test_policy_enforcement.py"
)

# Additional pytest arguments from command line
PYTEST_ARGS=("$@")

# If no args provided, use defaults
if [[ ${#PYTEST_ARGS[@]} -eq 0 ]]; then
    PYTEST_ARGS=(
        "-v"
        "--tb=short"
        "-m" "not external"
        "--disable-warnings"
    )
fi

echo "Running MSP tests..."
echo "Test files: ${TEST_FILES[*]}"
echo "Pytest args: ${PYTEST_ARGS[*]}"
echo ""

# Run pytest with offline markers
set +e  # Don't exit on test failure
pytest "${TEST_FILES[@]}" "${PYTEST_ARGS[@]}"
EXIT_CODE=$?
set -e

echo ""
if [[ ${EXIT_CODE} -eq 0 ]]; then
    echo "==================================="
    echo "✓ All tests passed!"
    echo "==================================="
else
    echo "==================================="
    echo "✗ Tests failed (exit code: ${EXIT_CODE})"
    echo "==================================="
fi

exit ${EXIT_CODE}
