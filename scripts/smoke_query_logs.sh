#!/usr/bin/env bash
set -euo pipefail
python3 -m src.codex.logging.query_logs --help >/dev/null
echo "[OK] query_logs --help executed"
