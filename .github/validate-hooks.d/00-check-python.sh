#!/usr/bin/env bash
# Example pre-validation hook: check that the Python environment is healthy.
#
# Arguments:
#   $1 — mode  (fast|full)
#   $2 — stage (pre|post)
#
# Exit non-zero to signal a hook failure (treated as a WARNING by the runner).

set -euo pipefail

MODE="$1"
STAGE="$2"

if [[ "$STAGE" == "pre" ]]; then
    echo "[hook:00-check-python] mode=${MODE} stage=${STAGE}"
    python --version
    echo "[hook:00-check-python] Python check passed"
fi
