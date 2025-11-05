#!/usr/bin/env bash
# Build Python wheel for codex-ml package
# Output: artifacts/dist/*.whl

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/artifacts/dist"

echo "==> Building codex-ml wheel"
echo "Repository: ${REPO_ROOT}"
echo "Output directory: ${OUTPUT_DIR}"

cd "${REPO_ROOT}"

# Upgrade build tools
echo "==> Upgrading build tools"
python -m pip install --upgrade pip setuptools wheel build

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Build wheel
echo "==> Building wheel"
python -m build --wheel --outdir "${OUTPUT_DIR}"

echo "==> Build complete"
ls -lh "${OUTPUT_DIR}"/*.whl

echo ""
echo "Wheel created successfully in ${OUTPUT_DIR}"
echo "Install with: pip install ${OUTPUT_DIR}/*.whl"
