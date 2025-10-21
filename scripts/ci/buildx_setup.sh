#!/usr/bin/env bash
# Ensure Docker Buildx is available and a builder is selected.
set -euo pipefail

docker info >/dev/null
if ! docker buildx version >/dev/null 2>&1; then
  echo "[buildx] WARN: docker buildx not reported; attempting to continue."
fi

BUILDER_NAME="${BUILDER_NAME:-ci_builder}"

if ! docker buildx inspect "${BUILDER_NAME}" >/dev/null 2>&1; then
  docker buildx create --name "${BUILDER_NAME}" --use
else
  docker buildx use "${BUILDER_NAME}"
fi

docker buildx inspect --bootstrap || true

echo "[buildx] active builder:"
docker buildx ls
