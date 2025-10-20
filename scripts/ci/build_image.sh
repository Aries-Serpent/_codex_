#!/usr/bin/env bash
# Build a local image for smoke testing. No push.
# Usage: scripts/ci/build_image.sh [image_tag] [dockerfile] [--load]
set -euo pipefail

IMAGE="${1:-codex:local}"
DOCKERFILE="${2:-Dockerfile}"
FLAG="${3:-}"
BUILDX_FLAGS="${BUILDX_FLAGS:-}"

if [ -n "${FLAG}" ] && [ "${FLAG}" != "--load" ]; then
  echo "[build] Unknown flag: ${FLAG}" >&2
  exit 2
fi

echo "[build] Dockerfile: ${DOCKERFILE}"
echo "[build] Tag:        ${IMAGE}"

if docker buildx version >/dev/null 2>&1; then
  LOAD_ARG=""
  if [ "${FLAG}" = "--load" ]; then
    LOAD_ARG="--load"
  fi
  if [ -n "${LOAD_ARG}" ]; then
    echo "[build] Using docker buildx ${LOAD_ARG}"
  else
    echo "[build] Using docker buildx"
  fi
  docker buildx build ${LOAD_ARG} -f "${DOCKERFILE}" -t "${IMAGE}" ${BUILDX_FLAGS} .
else
  if [ "${FLAG}" = "--load" ]; then
    echo "[build] Warning: buildx not available, ignoring --load" >&2
  fi
  echo "[build] Using docker build"
  docker build -f "${DOCKERFILE}" -t "${IMAGE}" .
fi

echo "[build] Image built: ${IMAGE}"
echo "[build] Run locally:"
echo "  docker run --rm -p 8000:8000 ${IMAGE}"
echo "  curl -fsS http://127.0.0.1:8000/health || curl -fsS http://127.0.0.1:8000/"
