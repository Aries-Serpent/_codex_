#!/usr/bin/env bash
set -euo pipefail
# Auto-provision ephemeral (single-job) runners until the queue drains.
# Uses GitHub REST (registration token) and repo workflows to derive labels.
# Requires: GH_PAT, curl, jq|python3, tar, shasum.
#
# Usage:
#   GH_PAT=... tools/ephem_autoscaler.sh --branch 0B_base_ --max 2 --poll 10
#   GH_PAT=... tools/ephem_autoscaler.sh --branch 0B_base_ --scale-from-queue --cap 4

OWNER="${OWNER:-Aries-Serpent}"
REPO="${REPO:-_codex_}"
BRANCH="${BRANCH:-0B_base_}"
MAX="${MAX:-2}"
CAP="${CAP:-5}"
POLL="${POLL:-10}"
LABELS_OVERRIDE="${LABELS_OVERRIDE:-}"
SCALE_FROM_QUEUE=0

_die(){ echo "ERROR: $*" >&2; exit 1; }
_need(){ command -v "$1" >/dev/null 2>&1 || _die "Missing dependency: $1"; }
_need curl; _need tar; _need shasum
[[ -n "${GH_PAT:-}" ]] || _die "GH_PAT not set"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2;;
    --repo) REPO="$2"; shift 2;;
    --branch) BRANCH="$2"; shift 2;;
    --max) MAX="$2"; shift 2;;
    --cap) CAP="$2"; shift 2;;
    --poll) POLL="$2"; shift 2;;
    --labels-override) LABELS_OVERRIDE="$2"; shift 2;;
    --scale-from-queue) SCALE_FROM_QUEUE=1; shift;;
    -h|--help)
      sed -n '1,120p' "$0"; exit 0;;
    *) _die "Unknown arg: $1";;
  esac
done

active_pids=()
cleanup(){ for p in "${active_pids[@]:-}"; do kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM

count_queued(){
  local url="https://api.github.com/repos/${OWNER}/${REPO}/actions/runs?status=queued&branch=${BRANCH}&per_page=100"
  local json
  json=$(curl -fsSL -H "Authorization: Bearer ${GH_PAT}" -H "Accept: application/vnd.github+json" "$url")
  if command -v jq >/dev/null 2>&1; then
    echo "$json" | jq '.workflow_runs | length'
  else
    python3 - <<'PY'
import json,sys
print(len(json.load(sys.stdin).get('workflow_runs', [])))
PY
  fi
}

spawn_one(){
  local labels="$1"
  echo "[autoscaler] Spawning ephemeral runner with labels: $labels"
  GH_PAT="$GH_PAT" bash tools/ephem_runner.sh --labels "$labels" --branch "$BRANCH" &
  active_pids+=("$!")
}

while :; do
  if [[ -z "$LABELS_OVERRIDE" ]]; then
    _need python3
    labels=$(python3 tools/preflight_minimal_labels.py --owner "$OWNER" --repo "$REPO" --branch "$BRANCH" --gh-pat "$GH_PAT") || _die "preflight failed"
  else
    labels="$LABELS_OVERRIDE"
  fi

  [[ -n "$labels" ]] || { echo "[autoscaler] No labels returned; sleeping $POLL"; sleep "$POLL"; continue; }

  if (( SCALE_FROM_QUEUE )); then
    queued=$(count_queued)
    (( queued > CAP )) && queued=$CAP
    MAX=$queued
  fi

  live=()
  for p in "${active_pids[@]:-}"; do
    if kill -0 "$p" 2>/dev/null; then live+=("$p"); fi
  done
  active_pids=("${live[@]}")

  need=$(( MAX - ${#active_pids[@]} ))
  if (( need > 0 )); then
    for _ in $(seq 1 "$need"); do spawn_one "$labels"; done
  fi
  sleep "$POLL"
done
