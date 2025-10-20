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

# Optionally enforce Docker health status if HEALTHCHECK is configured in the image.
# Enable by setting SMOKE_ENFORCE_HEALTH=1
if [ "${SMOKE_ENFORCE_HEALTH:-0}" = "1" ]; then
  HEALTH_RAW="$(docker inspect --format '{{if .State.Health}}{{json .State.Health}}{{end}}' "$NAME" 2>/dev/null || true)"
  HEALTH_RAW_STRIPPED="${HEALTH_RAW//[[:space:]]/}"
  if [ -n "$HEALTH_RAW_STRIPPED" ] && [ "$HEALTH_RAW_STRIPPED" != "null" ]; then
    echo "[smoke] Enforcing container health status..."
    STATUS=""
    for _ in $(seq 1 15); do
      STATUS="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$NAME" 2>/dev/null || echo "")"
      if [ "$STATUS" = "healthy" ]; then
        echo "[smoke] Container health status: healthy"
        break
      fi
      sleep 2
    done
    if [ "$STATUS" != "healthy" ]; then
      echo "[smoke] Container health status not healthy (status='$STATUS')" >&2
      docker inspect "$NAME" || true
      exit 1
    fi
  else
    echo "[smoke] Healthcheck not configured in image; skipping SMOKE_ENFORCE_HEALTH"
  fi
fi

echo "[smoke] Container logs saved to $LOG_FILE"
