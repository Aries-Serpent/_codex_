#!/usr/bin/env bash
# Push a previously built image to a registry (opt-in).
# Usage: scripts/ci/push_image.sh <ghcr.io/OWNER/REPO:tag>
set -euo pipefail

IMAGE="${1:-}"
if [ -z "${IMAGE}" ]; then
  echo "usage: $0 <registry/owner/repo:tag>" >&2
  exit 2
fi

REGISTRY="$(echo "${IMAGE}" | awk -F/ '{print $1}')"
echo "[push] Target: ${IMAGE}"
echo "[push] Registry: ${REGISTRY}"

echo "[push] Pushing image (ensure you are logged-in via 'docker login' or CI login action)"
docker push "${IMAGE}"
echo "[push] Done."
