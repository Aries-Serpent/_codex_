#!/usr/bin/env bash
# Install binfmt emulation for multi-arch builds (requires privileged docker).
# Usage: bash scripts/runner/install_binfmt.sh
set -euo pipefail

docker info >/dev/null
echo "[binfmt] Installing QEMU emulation via tonistiigi/binfmt"
docker run --privileged --rm tonistiigi/binfmt --install all
docker buildx inspect --bootstrap || true
echo "[binfmt] Installed. Verify with: ls /proc/sys/fs/binfmt_misc"
