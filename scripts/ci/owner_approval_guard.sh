#!/usr/bin/env bash
# Guard cost-incurring workflows behind owner approval windows.
# Success (0) when approval is currently valid for TOOL_KEY; failure (1/2) otherwise.
# Inputs:
#   - TOOL_KEY (string): logical workflow key e.g., "docker-build-push" (default), "security-scans", "all"
#   - OWNER_APPROVED_UNTIL (ISO8601 UTC) or OWNER_APPROVED_DURATION ("2h", "4h", "1d", "3w") — repo/environment variables
# Behavior:
#   - If env overrides exist, they take precedence over file-based config.
#   - Else read .github/OWNER_APPROVAL.yml (simple YAML parsing via grep/sed/awk).
set -euo pipefail

TOOL_KEY="${TOOL_KEY:-docker-build-push}"
APPROVAL_FILE=".github/OWNER_APPROVAL.yml"

now_epoch() { date -u +%s; }

trim() { awk '{$1=$1;print}'; } # trim leading/trailing whitespace on a single line

strip_quotes() {
  local line
  while IFS= read -r line; do
    local len=${#line}
    if (( len >= 2 )); then
      local first="${line:0:1}"
      local last="${line:len-1:1}"
      if [[ "$first" == "$last" && ( "$first" == '"' || "$first" == "'" ) ]]; then
        line="${line:1:len-2}"
      fi
    fi
    printf '%s\n' "$line"
  done
}

parse_iso_to_epoch() {
  # Usage: parse_iso_to_epoch "2025-10-21T04:00:00Z"
  date -u -d "$1" +%s 2>/dev/null || return 1
}

parse_duration_to_secs() {
  # Accepts patterns like "90s", "30m", "2h", "1d", "3w"
  local dur="$1"
  if [[ "$dur" =~ ^([0-9]+)([smhdw])$ ]]; then
    local n="${BASH_REMATCH[1]}"
    local u="${BASH_REMATCH[2]}"
    case "$u" in
      s) echo "$((n))" ;;
      m) echo "$((n*60))" ;;
      h) echo "$((n*3600))" ;;
      d) echo "$((n*86400))" ;;
      w) echo "$((n*604800))" ;;
    esac
  else
    return 1
  fi
}

approve_via_env() {
  local now ts
  now="$(now_epoch)"

  if [ -n "${OWNER_APPROVED_UNTIL:-}" ]; then
    ts="$(parse_iso_to_epoch "${OWNER_APPROVED_UNTIL}")" || {
      echo "[approval] OWNER_APPROVED_UNTIL is invalid: ${OWNER_APPROVED_UNTIL}" >&2
      return 2
    }
    if [ "$now" -le "$ts" ]; then
      echo "[approval] APPROVED via OWNER_APPROVED_UNTIL (${OWNER_APPROVED_UNTIL}) for TOOL_KEY=${TOOL_KEY}"
      return 0
    else
      echo "[approval] OWNER_APPROVED_UNTIL expired (${OWNER_APPROVED_UNTIL})" >&2
      return 2
    fi
  fi

  if [ -n "${OWNER_APPROVED_DURATION:-}" ]; then
    local secs
    secs="$(parse_duration_to_secs "${OWNER_APPROVED_DURATION}")" || {
      echo "[approval] OWNER_APPROVED_DURATION invalid: ${OWNER_APPROVED_DURATION}" >&2
      return 2
    }
    local until_epoch="$(( now + secs ))"
    echo "[approval] APPROVED via OWNER_APPROVED_DURATION=${OWNER_APPROVED_DURATION} until $(date -u -d "@$until_epoch" +%Y-%m-%dT%H:%M:%SZ) for TOOL_KEY=${TOOL_KEY}"
    return 0
  fi

  return 3
}

# Attempt env-based approval first.
if approve_via_env; then
  exit 0
fi

# Parse minimal YAML (no external deps).
if [ ! -f "${APPROVAL_FILE}" ]; then
  echo "[approval] ${APPROVAL_FILE} not found; deny" >&2
  exit 2
fi

# Parse "key: value" while stripping comments and quotes
val_of() {
  local key="$1"
  local line
  line="$(sed -n -E "s/^[[:space:]]*${key}:[[:space:]]*([^#]+).*$/\1/p" "${APPROVAL_FILE}" | head -n1 | strip_quotes | trim || true)"
  echo "${line:-}"
}

enabled="$(val_of enabled | tr '[:upper:]' '[:lower:]' || true)"
mode="$(val_of mode || true)"
duration="$(val_of duration || true)"
until_ts="$(val_of until || true)"
created_at="$(val_of created_at || true)"

# cost_workflows parsing — support inline list "[...]" and bullet list "- key"
declare -a costs
inline="$(sed -n -E 's/^[[:space:]]*cost_workflows:[[:space:]]*\[([^\]]*)\].*$/\1/p' "${APPROVAL_FILE}" | head -n1 || true)"
if [ -n "${inline}" ]; then
  # Split by comma, strip quotes/spaces
  while IFS=, read -r item; do
    item_clean="$(echo "$item" | strip_quotes | trim)"
    [ -n "${item_clean}" ] && costs+=("${item_clean}")
  done <<< "${inline}"
fi
# Also parse bullet list entries
while IFS= read -r k; do
  [ -n "$k" ] && costs+=("$k")
done < <(sed -n -E 's/^[[:space:]]*-[[:space:]]*([A-Za-z0-9_.-]+)[[:space:]]*$/\1/p' "${APPROVAL_FILE}")

has_cost_key="false"
for k in "${costs[@]:-}"; do
  if [ "$k" = "all" ] || [ "$k" = "$TOOL_KEY" ]; then
    has_cost_key="true"
    break
  fi
done

if [ "${enabled}" != "true" ]; then
  echo "[approval] OWNER_APPROVAL.yml enabled=false; deny" >&2
  exit 2
fi

if [ "${has_cost_key}" != "true" ]; then
  echo "[approval] TOOL_KEY=${TOOL_KEY} not listed in cost_workflows; deny" >&2
  exit 2
fi

now="$(now_epoch)"
# Compute expiry by mode
if [ "${mode}" = "until" ]; then
  [ -z "${until_ts}" ] && { echo "[approval] mode=until but 'until' not set; deny" >&2; exit 2; }
  exp="$(parse_iso_to_epoch "${until_ts}")" || { echo "[approval] 'until' invalid: ${until_ts}" >&2; exit 2; }
elif [ "${mode}" = "duration" ]; then
  [ -z "${duration}" ] && { echo "[approval] mode=duration but 'duration' empty; deny" >&2; exit 2; }
  secs="$(parse_duration_to_secs "${duration}")" || { echo "[approval] duration invalid: ${duration}" >&2; exit 2; }
  # Determine start time: created_at (preferred), then git last change time of this file, else file mtime.
  if [ -n "${created_at}" ]; then
    start="$(parse_iso_to_epoch "${created_at}")" || { echo "[approval] created_at invalid: ${created_at}" >&2; exit 2; }
  else
    if git log -1 --format=%ct -- "${APPROVAL_FILE}" >/dev/null 2>&1; then
      start="$(git log -1 --format=%ct -- "${APPROVAL_FILE}")"
    else
      start="$(date -u -r "${APPROVAL_FILE}" +%s)"
    fi
  fi
  exp="$(( start + secs ))"
else
  echo "[approval] Unknown mode: ${mode} (expected 'until' or 'duration')" >&2
  exit 2
fi

if [ "$now" -le "$exp" ]; then
  echo "[approval] APPROVED until $(date -u -d "@$exp" +%Y-%m-%dT%H:%M:%SZ) for TOOL_KEY=${TOOL_KEY}"
  exit 0
fi

echo "[approval] Window expired at $(date -u -d "@$exp" +%Y-%m-%dT%H:%M:%SZ); deny" >&2
exit 2
