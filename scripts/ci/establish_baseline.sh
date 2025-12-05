#!/usr/bin/env bash
# Establish regression baseline for audit system
# Usage: ./scripts/ci/establish_baseline.sh [--force]
#
# This script:
# 1. Runs the full audit pipeline (S1-S7)
# 2. Copies capabilities_scored.json to baseline directory
# 3. Validates the baseline was created successfully
#
# Use --force to overwrite existing baseline

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASELINE_DIR="${REPO_ROOT}/audit_artifacts/baselines"
BASELINE_FILE="${BASELINE_DIR}/capabilities_scored.json"
AUDIT_OUTPUT="${REPO_ROOT}/audit_artifacts/capabilities_scored.json"

FORCE=false
if [[ "${1:-}" == "--force" ]]; then
    FORCE=true
    echo "⚠️  Force mode enabled - will overwrite existing baseline"
fi

# Check if baseline already exists
if [[ -f "${BASELINE_FILE}" ]] && [[ "${FORCE}" != "true" ]]; then
    echo "❌ Baseline already exists at: ${BASELINE_FILE}"
    echo "   Use --force to overwrite, or manually remove the file."
    exit 1
fi

echo "🔍 Running full audit pipeline (S1-S7)..."
cd "${REPO_ROOT}"
python scripts/space_traversal/audit_runner.py run

# Validate that audit produced the required file
if [[ ! -f "${AUDIT_OUTPUT}" ]]; then
    echo "❌ Audit did not produce capabilities_scored.json"
    echo "   Expected at: ${AUDIT_OUTPUT}"
    exit 2
fi

# Create baseline directory
mkdir -p "${BASELINE_DIR}"

# Copy to baseline
echo "📦 Establishing baseline..."
cp "${AUDIT_OUTPUT}" "${BASELINE_FILE}"

# Validate baseline
if [[ ! -f "${BASELINE_FILE}" ]]; then
    echo "❌ Failed to create baseline file"
    exit 3
fi

# Check file is valid JSON
if ! python -c "import json; json.load(open('${BASELINE_FILE}'))" 2>/dev/null; then
    echo "❌ Baseline file is not valid JSON"
    exit 4
fi

echo "✅ Baseline established successfully!"
echo "   Location: ${BASELINE_FILE}"
echo ""
echo "📊 Baseline stats:"
CAPABILITY_COUNT=$(python -c "import json; data=json.load(open('${BASELINE_FILE}')); print(len(data.get('capabilities', [])))")
echo "   - Capabilities tracked: ${CAPABILITY_COUNT}"
echo ""
echo "ℹ️  Next steps:"
echo "   1. Commit the baseline: git add ${BASELINE_FILE}"
echo "   2. Push to repository: git commit -m 'feat: Establish audit baseline' && git push"
echo "   3. CI will now use this baseline for regression detection"
