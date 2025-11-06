#!/usr/bin/env bash
#
# Offline API documentation build script
#
# Environment variables:
#   SKIP_OPTIONAL   - Set to 1 to skip optional modules (codex_ml extras)
#   FAIL_ON_MISSING - Set to 1 for strict mode (fail if any requested modules missing)
#   OUTPUT_DIR      - Custom output directory (default: artifacts/docs/api)
#
# Exit codes:
#   0 - Success (docs built for available modules)
#   1 - Build error (pdoc or script failure)
#   2 - No importable modules found
#   3 - Strict failure (missing modules with FAIL_ON_MISSING=1)
#
# Usage:
#   bash scripts/docs_build.sh
#   SKIP_OPTIONAL=1 bash scripts/docs_build.sh
#   FAIL_ON_MISSING=1 bash scripts/docs_build.sh

set -euo pipefail

# Repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Default output directory
OUTPUT_DIR="${OUTPUT_DIR:-artifacts/docs/api}"

# Build flags
SKIP_OPTIONAL="${SKIP_OPTIONAL:-0}"
FAIL_ON_MISSING="${FAIL_ON_MISSING:-0}"

echo "[docs_build] Starting API documentation build"
echo "[docs_build] SKIP_OPTIONAL=$SKIP_OPTIONAL"
echo "[docs_build] FAIL_ON_MISSING=$FAIL_ON_MISSING"
echo "[docs_build] OUTPUT_DIR=$OUTPUT_DIR"

# Prepare output directory
mkdir -p "$OUTPUT_DIR"

# Build command using existing build_api_docs.py tool
BUILD_CMD=(python tools/build_api_docs.py --output-dir "$OUTPUT_DIR" --verbose)

# Add flags based on environment
if [ "$SKIP_OPTIONAL" = "1" ]; then
    BUILD_CMD+=(--skip-optional)
    echo "[docs_build] Skipping optional modules"
fi

if [ "$FAIL_ON_MISSING" = "1" ]; then
    BUILD_CMD+=(--fail-on-missing)
    echo "[docs_build] Strict mode enabled"
fi

# Run build
echo "[docs_build] Running: ${BUILD_CMD[*]}"
"${BUILD_CMD[@]}"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[docs_build] ✓ Documentation build successful"
    echo "[docs_build] Output: $OUTPUT_DIR/index.html"
elif [ $EXIT_CODE -eq 2 ]; then
    echo "[docs_build] ✗ No importable modules found"
    exit 2
elif [ $EXIT_CODE -eq 3 ]; then
    echo "[docs_build] ✗ Strict mode failure: missing required modules"
    exit 3
else
    echo "[docs_build] ✗ Build failed with exit code $EXIT_CODE"
    exit 1
fi

exit 0
