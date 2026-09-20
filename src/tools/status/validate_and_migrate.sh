#!/usr/bin/env bash
set -euo pipefail
in="$1"
out="${2:-/dev/stdout}"

python3 tools/status/validate_codex_status.py --schema v1.1 "$in"
python3 tools/status/migrate_v1_1_to_v1_2.py "$in" "$out"
python3 tools/status/validate_codex_status.py --schema v1.2 "$out"
echo "[validate_and_migrate] done: $in -> $out"
