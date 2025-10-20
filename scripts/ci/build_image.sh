#!/usr/bin/env bash
# Build a local image for smoke testing. No push.
# Usage: scripts/ci/build_image.sh [image_tag] [dockerfile] [--load]
set -euo pipefail

IMAGE="${1:-codex:local}"
DOCKERFILE="${2:-Dockerfile}"
FLAG="${3:-}"
BUILDX_FLAGS="${BUILDX_FLAGS:-}"
# Auto inject build metadata (VERSION, VCS_REF, BUILD_DATE) unless disabled
AUTO_BUILD_METADATA="${AUTO_BUILD_METADATA:-1}"

# Prepare optional build args for provenance/labels
BUILD_ARGS=()
if [ "${AUTO_BUILD_METADATA}" = "1" ]; then
  VERSION="$(git describe --tags --always --dirty=+ 2>/dev/null || echo "0.0.0")"
  VCS_REF="$(git rev-parse --short=12 HEAD 2>/dev/null || echo "unknown")"
  BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  BUILD_ARGS+=(--build-arg "VERSION=${VERSION}")
  BUILD_ARGS+=(--build-arg "VCS_REF=${VCS_REF}")
  BUILD_ARGS+=(--build-arg "BUILD_DATE=${BUILD_DATE}")
  echo "[build] Injecting build args: VERSION=${VERSION}, VCS_REF=${VCS_REF}, BUILD_DATE=${BUILD_DATE}"
else
  echo "[build] AUTO_BUILD_METADATA=0 (skipping build args)"
fi

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
  docker buildx build ${LOAD_ARG} -f "${DOCKERFILE}" -t "${IMAGE}" "${BUILD_ARGS[@]}" ${BUILDX_FLAGS} .
else
  if [ "${FLAG}" = "--load" ]; then
    echo "[build] Warning: buildx not available, ignoring --load" >&2
  fi
  echo "[build] Using docker build"
  docker build -f "${DOCKERFILE}" -t "${IMAGE}" "${BUILD_ARGS[@]}" .
fi

echo "[build] Image built: ${IMAGE}"
echo "[build] Run locally:"
echo "  docker run --rm -p 8000:8000 ${IMAGE}"
echo "  curl -fsS http://127.0.0.1:8000/health || curl -fsS http://127.0.0.1:8000/"
