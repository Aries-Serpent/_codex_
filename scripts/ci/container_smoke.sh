#!/usr/bin/env bash
# Smoke test: run container and verify a 200 OK on /health (or / fallback).
# Usage: container_smoke.sh <image> [container_port] [host_port]
set -euo pipefail

IMAGE="${1:-codex:ci}"
C_PORT="${2:-8000}"
H_PORT="${3:-18000}"

LOG_DIR="scripts/ci/smoke_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/container_$(date -u +%Y%m%dT%H%M%SZ).log"

NAME="codex_smoke_$$"

cleanup() {
  docker logs "$NAME" > "$LOG_FILE" 2>&1 || true
  docker rm -f "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[smoke] Starting container ${IMAGE} as ${NAME} (map ${H_PORT}->${C_PORT})"
docker run -d --name "$NAME" -p "${H_PORT}:${C_PORT}" "${IMAGE}" >/dev/null

# Wait for readiness
RETRIES=30
SLEEP=2
URLS=("http://127.0.0.1:${H_PORT}/health" "http://127.0.0.1:${H_PORT}/")
OK=0
for _ in $(seq 1 "$RETRIES"); do
  for url in "${URLS[@]}"; do
    code="$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)"
    if [ "$code" = "200" ]; then
      echo "[smoke] Healthy at $url"
      OK=1
      break 2
    fi
  done
  sleep "$SLEEP"
done

if [ "$OK" -ne 1 ]; then
  echo "[smoke] Failed to get 200 from any health URL" >&2
  docker logs "$NAME" || true
  exit 1
fi

echo "[smoke] Container logs saved to $LOG_FILE"
