#!/usr/bin/env bash
# scripts/install_hooks.sh
#
# Install the RVS pre-push git hook into the local .git/hooks directory.
# Run once after cloning:
#   bash scripts/install_hooks.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SRC="$ROOT/.github/hooks/pre-push"
DST="$ROOT/.git/hooks/pre-push"

if [[ ! -f "$SRC" ]]; then
  echo "ERROR: $SRC not found" >&2
  exit 1
fi

cp "$SRC" "$DST"
chmod +x "$DST"
echo "✅  Installed pre-push hook → $DST"
echo "   The hook runs 'rvs_preflight --changed-only' before every push."
echo "   To uninstall: rm $DST"
