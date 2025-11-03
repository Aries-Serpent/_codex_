#!/usr/bin/env bash
set -euo pipefail
python tools/env_snapshot.py
echo "[OK] Environment snapshot written to env_snapshot.json"
