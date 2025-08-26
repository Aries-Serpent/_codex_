#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${IMAGE:=codex-api:local}"
: "${PORT:=8000}"
if command -v nvidia-smi >/dev/null 2>&1; then
  GPU_FLAG="--gpus all"
else
  GPU_FLAG=""
fi
docker compose $GPU_FLAG up -d
echo "Waiting for API to become healthy..."
for i in $(seq 1 30); do
  if curl -fsS "http://localhost:${PORT}/status" >/dev/null; then
    echo "API is healthy."
    exit 0
  fi
  sleep 2
done
echo "API failed to become healthy in time"; exit 1
