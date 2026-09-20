#!/usr/bin/env bash
set -euo pipefail
python3 tools/apply_patch_safely.py "${1:-fallback_patch_4.1-4.8.diff}"
