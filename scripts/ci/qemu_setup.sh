#!/usr/bin/env bash
# Install binfmt for emulation to enable multi-arch builds.
set -euo pipefail

# Requires privileged docker on the self-hosted runner
docker run --privileged --rm tonistiigi/binfmt --install all

docker buildx inspect --bootstrap || true

echo "[qemu] installed binfmt emulation for multi-arch"
