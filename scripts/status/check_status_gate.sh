#!/usr/bin/env bash
set -euo pipefail

if [ ! -f ".coverage.json" ]; then
  echo "[INFO] .coverage.json not found; run coverage first"
fi

python tools/status_gate_from_statusrc.py
