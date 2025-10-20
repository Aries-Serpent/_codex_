#!/usr/bin/env bash
# Container smoke test with configurable health path and timeouts.
# Usage: scripts/ci/container_smoke.sh <image> [container_port] [host_port]
# Env:
#   HEALTH_PATH           path to probe (default: /health; falls back to /)
#   FALLBACK_PATH         optional fallback path (default: /)
#   TIMEOUT_STARTUP_SEC   total time to wait for server up (default: 60)
#   TIMEOUT_HEALTH_SEC    per-attempt curl timeout (default: 3)
#   SMOKE_ENFORCE_HEALTH  if "1", also require Docker HEALTHCHECK to be healthy
set -euo pipefail

IMAGE="${1:-codex:ci}"
CONTAINER_PORT="${2:-8000}"
HOST_PORT="${3:-18000}"

if [ -z "${IMAGE}" ]; then
  echo "usage: $0 <image> [container_port] [host_port]" >&2
  exit 2
fi

HEALTH_PATH="${HEALTH_PATH:-/health}"
FALLBACK_PATH="${FALLBACK_PATH:-/}"
TIMEOUT_STARTUP_SEC="${TIMEOUT_STARTUP_SEC:-60}"
TIMEOUT_HEALTH_SEC="${TIMEOUT_HEALTH_SEC:-3}"

LOG_DIR="scripts/ci/smoke_logs"
mkdir -p "${LOG_DIR}"
NAME="codex_smoke_$$"
LOG_FILE="${LOG_DIR}/${NAME}_$(date -u +%Y%m%dT%H%M%SZ).log"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [smoke] $*"
}

cleanup() {
  log "Capturing logs to ${LOG_FILE}"
  docker logs "${NAME}" > "${LOG_FILE}" 2>&1 || true
  docker rm -f "${NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

log "Starting container ${IMAGE} as ${NAME} (map ${HOST_PORT}->${CONTAINER_PORT})"
docker run -d --rm --name "${NAME}" -p "${HOST_PORT}:${CONTAINER_PORT}" "${IMAGE}" >/dev/null

URL_HEALTH="http://127.0.0.1:${HOST_PORT}${HEALTH_PATH}"
URL_FALLBACK="http://127.0.0.1:${HOST_PORT}${FALLBACK_PATH}"

deadline=$(( $(date +%s) + TIMEOUT_STARTUP_SEC ))
ok=0
while [ "$(date +%s)" -le "${deadline}" ]; do
  if curl -fsS --max-time "${TIMEOUT_HEALTH_SEC}" "${URL_HEALTH}" >/dev/null 2>&1 \
     || curl -fsS --max-time "${TIMEOUT_HEALTH_SEC}" "${URL_FALLBACK}" >/dev/null 2>&1; then
    log "Healthy response received"
    ok=1
    break
  fi
  sleep 2
done

if [ "${SMOKE_ENFORCE_HEALTH:-0}" = "1" ]; then
  log "Enforcing Docker HEALTHCHECK status"
  status=""
  for _ in $(seq 1 15); do
    status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "${NAME}" 2>/dev/null || true)"
    status="${status//[[:space:]]/}"
    if [ -z "${status}" ]; then
      log "Container image does not define HEALTHCHECK; skipping enforcement"
      status="skipped"
      break
    fi
    if [ "${status}" = "healthy" ]; then
      log "Container health status: healthy"
      break
    fi
    sleep 2
  done
  if [ "${status}" != "healthy" ] && [ "${status}" != "skipped" ]; then
    log "Container health status not healthy (status='${status}')"
    exit 1
  fi
fi

if [ "${ok}" = "1" ]; then
  log "OK"
  exit 0
fi

log "FAIL: no 200 from ${HEALTH_PATH} or fallback within ${TIMEOUT_STARTUP_SEC}s"
exit 1
