#!/usr/bin/env bash
# Session logging helper (Shell)
set -euo pipefail

: "${CODEX_SESSION_LOG_DIR:=.codex/sessions}"
mkdir -p "$CODEX_SESSION_LOG_DIR"

codex__timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

codex__uuid() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]'
  else
    printf "sess-%s-%s" "$(date +%s)" "$RANDOM"
  fi
}

codex_session_start() {
  : "${CODEX_SESSION_ID:=$(codex__uuid)}"
  export CODEX_SESSION_ID
  echo "$(codex__timestamp) session_start $CODEX_SESSION_ID" > "$CODEX_SESSION_LOG_DIR/${CODEX_SESSION_ID}.meta"
  {
    printf '{"ts":"%s","type":"session_start","session_id":"%s","cwd":"%s","argv":[' "$(codex__timestamp)" "$CODEX_SESSION_ID" "$PWD"
    first=1
    for a in "$@"; do
      if [[ $first -eq 1 ]]; then first=0; else printf ","; fi
      printf '%s' "\"${a//\"/\\\"}\""
    done
    printf "]}\n"
  } >> "$CODEX_SESSION_LOG_DIR/${CODEX_SESSION_ID}.ndjson"
}

codex_session_end() {
  local exit_code="${1:-0}"
  : "${CODEX_SESSION_ID:?missing session id}"
  local start_line
  start_line="$(head -n1 "$CODEX_SESSION_LOG_DIR/${CODEX_SESSION_ID}.meta" 2>/dev/null || true)"
  local duration=""
  if [[ -n "$start_line" ]]; then
    local start_epoch
    start_epoch="$(date -u -d "$(echo "$start_line" | awk '{print $1}')" +%s 2>/dev/null || date +%s)"
    local now_epoch
    now_epoch="$(date -u +%s)"
    duration="$(( now_epoch - start_epoch ))"
  fi
  printf '{"ts":"%s","type":"session_end","session_id":"%s","exit_code":%s,"duration_s":%s}\n' \
    "$(codex__timestamp)" "$CODEX_SESSION_ID" "$exit_code" "${duration:-null}" \
    >> "$CODEX_SESSION_LOG_DIR/${CODEX_SESSION_ID}.ndjson"
}
