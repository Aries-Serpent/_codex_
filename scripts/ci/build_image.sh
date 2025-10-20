#!/usr/bin/env bash
# Build a local image for smoke testing. No push.
# Usage: scripts/ci/build_image.sh [image_tag] [dockerfile]
set -euo pipefail

IMAGE="${1:-codex:local}"
DOCKERFILE="${2:-Dockerfile}"
BUILDX_FLAGS="${BUILDX_FLAGS:-}"

echo "[build] Dockerfile: ${DOCKERFILE}"
echo "[build] Tag:        ${IMAGE}"

# If buildx is available, we can pass through flags from BUILDX_FLAGS.
if docker buildx version >/dev/null 2>&1; then
  echo "[build] Using docker buildx"
  docker buildx build -f "${DOCKERFILE}" -t "${IMAGE}" ${BUILDX_FLAGS} .
else
  echo "[build] Using docker build"
  docker build -f "${DOCKERFILE}" -t "${IMAGE}" .
fi

echo "[build] Image built: ${IMAGE}"
echo "[build] Run locally:"
echo "  docker run --rm -p 8000:8000 ${IMAGE}"
echo "  curl -fsS http://127.0.0.1:8000/health || curl -fsS http://127.0.0.1:8000/"
