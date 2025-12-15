#!/usr/bin/env bash
# Docker-specific pytest runner script
# Extracted from Dockerfile CMD for maintainability and reusability
#
# Usage:
#   ./scripts/ci/docker_pytest.sh [additional pytest args...]
#
# Environment Variables:
#   COVERAGE_DIR     - Directory for coverage reports (default: /workspace/artifacts)
#   COVERAGE_THRESHOLD - Minimum coverage percentage (default: 90)
#   PYTEST_MAXFAIL   - Stop after N failures (default: 1)
#
# This script is designed for deterministic behavior in CI environments:
# - Uses bash -c (not -lc) to avoid login shell initialization
# - Minimal output with --tb=short --no-header -q to prevent token limit issues
# - Generates both XML and HTML coverage reports

set -euo pipefail

# Default configuration
COVERAGE_DIR="${COVERAGE_DIR:-/workspace/artifacts}"
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-90}"
PYTEST_MAXFAIL="${PYTEST_MAXFAIL:-1}"

echo "[INFO] Running pytest with coverage..."
echo "[INFO] Coverage directory: ${COVERAGE_DIR}"
echo "[INFO] Coverage threshold: ${COVERAGE_THRESHOLD}%"

# Ensure coverage directory exists
mkdir -p "${COVERAGE_DIR}"

# Run pytest with coverage
# Note: Coverage is configured for both 'src' and 'agents' directories
# to capture all source code in the repository
pytest \
    --maxfail="${PYTEST_MAXFAIL}" \
    --disable-warnings \
    --tb=short \
    --no-header \
    --cov=src \
    --cov=agents \
    --cov-report="xml:${COVERAGE_DIR}/coverage.xml" \
    --cov-report="html:${COVERAGE_DIR}/htmlcov" \
    -q \
    "$@"

echo "[INFO] Pytest completed successfully"
echo "[INFO] Coverage reports available in: ${COVERAGE_DIR}"
