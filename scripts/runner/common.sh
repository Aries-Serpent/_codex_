#!/usr/bin/env bash
# Common helpers for runner scripts (token resolution and GitHub API calls)
set -euo pipefail

# Resolve PAT: prefer GH_PAT, fallback to _CODEX_BOT_RUNNER
resolve_pat() {
  if [[ -n "${GH_PAT:-}" ]]; then
    echo "${GH_PAT}"
  elif [[ -n "${_CODEX_BOT_RUNNER:-}" ]]; then
    echo "${_CODEX_BOT_RUNNER}"
  else
    echo ""
  fi
}

# Basic GitHub API call with PAT (prints response body to stdout)
# Usage: api_call METHOD URL [DATA_JSON]
api_call() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local pat; pat="$(resolve_pat)"
  if [[ -z "${pat}" ]]; then
    echo "[api] ERROR: GH_PAT or _CODEX_BOT_RUNNER not set" >&2
    return 2
  fi
  if [[ -n "${data}" ]]; then
    curl -fsSL -X "${method}" \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer ${pat}" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "Content-Type: application/json" \
      --data "${data}" \
      "${url}"
  else
    curl -fsSL -X "${method}" \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer ${pat}" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "${url}"
  fi
}

# JSON pretty-print if jq exists
json_pp() {
  if command -v jq >/dev/null 2>&1; then
    jq .
  else
    cat
  fi
}
