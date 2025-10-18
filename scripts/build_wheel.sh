#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$here"

echo "[build] Cleaning old artifacts"
rm -rf dist build *.egg-info

echo "[build] Building sdist and wheel"
python -m build

echo "[build] Artifacts:"
ls -lh dist

echo "[build] Generating SHA256SUMS"
cd dist
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum * > SHA256SUMS
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 * > SHA256SUMS
else
  echo "No sha256sum/shasum found; skipping checksums" >&2
fi
cat SHA256SUMS || true

echo "[build] Done"
