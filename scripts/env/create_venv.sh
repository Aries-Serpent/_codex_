#!/usr/bin/env bash
set -euo pipefail

PYTHON=${PYTHON:-python3}

# Ensure Python version >=3.9
$PYTHON - <<'PY'
import sys
if sys.version_info < (3, 9):
    print("Python >=3.9 required", file=sys.stderr)
    sys.exit(1)
PY

if [[ ! -d .venv ]]; then
    $PYTHON -m venv .venv
fi

LOCK_FILE=${1:-requirements.lock}
if [[ ! -f "$LOCK_FILE" ]]; then
    echo "Lock file $LOCK_FILE not found" >&2
    exit 1
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install --no-deps -r "$LOCK_FILE"

echo "Virtual environment created in .venv"
echo "Activate with: source .venv/bin/activate"
