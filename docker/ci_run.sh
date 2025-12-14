#!/usr/bin/env bash
# docker/ci_run.sh — CI-friendly script to build test image and run pytest
# Maintainer note: This script ensures deterministic test execution in Docker.
# CI should call this script to maintain pip install path parity with the Dockerfile.
#
# Usage:
#   ./docker/ci_run.sh                    # Use defaults
#   IMAGE_NAME=my-test:v1 ./docker/ci_run.sh   # Custom image name
#   DOCKERFILE_PATH=Dockerfile.prod ./docker/ci_run.sh  # Use production Dockerfile
#
# Environment Variables:
#   IMAGE_NAME      - Docker image name/tag (default: codex-test:latest)
#   ARTIFACTS_DIR   - Directory to write coverage reports (default: ./artifacts)
#   DOCKERFILE_PATH - Path to Dockerfile (default: Dockerfile)
#   PYTEST_ARGS     - Additional arguments to pass to pytest (optional)
#
# Exit Codes:
#   Returns the exit code from pytest inside the container.
#   CI will fail if tests fail (non-zero exit).

set -euo pipefail

# Configuration with defaults
IMAGE_NAME="${IMAGE_NAME:-codex-test:latest}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-$(pwd)/artifacts}"
DOCKERFILE_PATH="${DOCKERFILE_PATH:-Dockerfile}"
PYTEST_ARGS="${PYTEST_ARGS:-}"

# Ensure we're in the repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "=============================================="
echo "Codex Docker Test Runner"
echo "=============================================="
echo "Image:      ${IMAGE_NAME}"
echo "Dockerfile: ${DOCKERFILE_PATH}"
echo "Artifacts:  ${ARTIFACTS_DIR}"
echo "=============================================="

# Create artifacts directory if it doesn't exist
mkdir -p "${ARTIFACTS_DIR}"

# Build the test image
echo ""
echo "[1/2] Building test image ${IMAGE_NAME} from ${DOCKERFILE_PATH}..."
echo ""
docker build \
    --progress=plain \
    -f "${DOCKERFILE_PATH}" \
    -t "${IMAGE_NAME}" \
    .

echo ""
echo "[2/2] Running tests inside container..."
echo "      Coverage reports will be written to: ${ARTIFACTS_DIR}"
echo ""

# Run container with artifacts directory mounted
# The container runs pytest and writes coverage to /workspace/artifacts
# which is bind-mounted to the host's artifacts directory
# Disable exit on error temporarily to capture the exit code
set +e
if [ -n "${PYTEST_ARGS}" ]; then
    # Custom pytest arguments provided
    docker run --rm \
        -v "${ARTIFACTS_DIR}":/workspace/artifacts \
        -e COVERAGE_DIR=/workspace/artifacts \
        "${IMAGE_NAME}" \
        bash -c "pytest ${PYTEST_ARGS} --cov=src --cov-report=xml:/workspace/artifacts/coverage.xml --cov-report=html:/workspace/artifacts/htmlcov"
    CODE=$?
else
    # Use default CMD from Dockerfile
    docker run --rm \
        -v "${ARTIFACTS_DIR}":/workspace/artifacts \
        -e COVERAGE_DIR=/workspace/artifacts \
        "${IMAGE_NAME}"
    CODE=$?
fi
set -e

echo ""
echo "=============================================="
echo "Test run complete"
echo "Exit code: ${CODE}"
echo "=============================================="

if [ ${CODE} -eq 0 ]; then
    echo "✓ All tests passed"
    echo ""
    echo "Coverage reports available at:"
    echo "  - HTML: ${ARTIFACTS_DIR}/htmlcov/index.html"
    echo "  - XML:  ${ARTIFACTS_DIR}/coverage.xml"
else
    echo "✗ Tests failed"
fi

exit "$CODE"
