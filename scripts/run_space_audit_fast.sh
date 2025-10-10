#!/usr/bin/env bash
# Fast space audit runner (S1, S3, S4, S6 only)
# Author: mbaetiong
# Generated: 2025-10-10 06:11:06

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Running fast space audit (S1→S3→S4→S6)..."

# S1: Context Index
echo "[S1] Building context index..."
python scripts/space_traversal/audit_runner.py stage S1

# S3: Capability Extraction (includes dynamic detectors)
echo "[S3] Extracting capabilities..."
python scripts/space_traversal/audit_runner.py stage S3

# S4: Scoring
echo "[S4] Scoring capabilities..."
python scripts/space_traversal/audit_runner.py stage S4

# S6: Render Report
echo "[S6] Rendering capability matrix..."
python scripts/space_traversal/audit_runner.py stage S6

echo "Fast audit complete! Check reports/ for output."

# Show top 3 lowest scoring capabilities
echo ""
echo "Lowest scoring capabilities:"
jq -r '.capabilities | sort_by(.score) | .[:3] | .[] | "\(.id): \(.score)"' \
    audit_artifacts/capabilities_scored.json
