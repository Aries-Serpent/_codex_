#!/usr/bin/env bash
# Push a previously built image to a registry (opt-in).
# Usage: scripts/ci/push_image.sh <ghcr.io/OWNER/REPO:tag> [--dry-run]
set -euo pipefail

IMAGE="${1:-}"
DRY_RUN="${2:-}"
if [ -z "${IMAGE}" ]; then
  echo "usage: $0 <registry/owner/repo:tag>" >&2
  exit 2
fi

REGISTRY="$(echo "${IMAGE}" | awk -F/ '{print $1}')"
echo "[push] Target: ${IMAGE}"
echo "[push] Registry: ${REGISTRY}"

if ! docker info >/dev/null 2>&1; then
  echo "[push] docker not available or not running" >&2
  exit 2
fi

# Optional GHCR login if CI env provided
if [ "${REGISTRY}" = "ghcr.io" ] && [ -n "${GITHUB_ACTOR:-}" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
  echo "[push] Logging into GHCR as ${GITHUB_ACTOR}"
  echo "${GITHUB_TOKEN}" | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin
fi

if [ "${DRY_RUN}" = "--dry-run" ]; then
  echo "[push] Dry-run: would push ${IMAGE}"
  exit 0
fi

# Ensure docker login done externally when not GHCR or no creds provided

echo "[push] Pushing image (ensure you are logged-in via 'docker login' or CI login action)"
docker push "${IMAGE}"
echo "[push] Done."
