#!/usr/bin/env bash
# Prune & Consolidate Audit Pipeline (prep/prune-audit) - SAFE operations; review before run.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
echo "[INFO] Dry-run mode recommended. Verify files before executing."
echo "Recommended sequence (dry-run first):"
echo "  DRY_RUN=1 bash .github/prune-and-consolidate.sh"
echo "Then remove DRY_RUN to apply changes."
# (Script contents preserved as provided earlier — run in repo root as needed.)
