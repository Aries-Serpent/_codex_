#!/usr/bin/env bash
set -euo pipefail

# Reproducible local build with checksum manifest
# Usage: scripts/build_wheel.sh

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${HERE}/.." && pwd)"
DIST="${ROOT}/dist"

echo "[build] Cleaning previous artifacts..."
rm -rf "${ROOT}"/build "${ROOT}"/.eggs "${ROOT}"/*.egg-info "${DIST}"
mkdir -p "${DIST}"

echo "[build] Verifying packaging metadata..."
if ! command -v python >/dev/null 2>&1; then
  echo "python not found" >&2
  exit 2
fi

echo "[build] Building sdist and wheel..."
python -m build

echo "[build] Generating SHA256SUMS..."
cd "${DIST}"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum * > SHA256SUMS
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 * > SHA256SUMS
else
  echo "No sha256sum/shasum found; skipping checksum generation" >&2
fi

echo "[build] Done. Artifacts:"
ls -lh "${DIST}"
