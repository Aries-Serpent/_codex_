#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-}"
DST="${2:-visual_baseline/status_report_themed.png}"

if [ -z "${SRC}" ]; then
  echo "Usage: $0 <candidate_png> [baseline_path]"
  exit 2
fi

mkdir -p "$(dirname "${DST}")"
cp -f "${SRC}" "${DST}"
echo "[OK] Updated baseline ${DST} from ${SRC}"
