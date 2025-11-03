#!/usr/bin/env bash
set -euo pipefail
echo "[INFO] Preparing minimal offline environment"
python -m pip install --upgrade pip
pip install jsonschema pyyaml pytest coverage || true
echo "[OK] Base tooling installed (best-effort for offline)"
