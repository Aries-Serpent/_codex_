#!/usr/bin/env bash
# Guard cost-incurring workflows behind owner approval windows.
# Success (0) when approval is currently valid for TOOL_KEY; failure (1/2) otherwise.
# Inputs:
#   - TOOL_KEY (string): logical workflow key e.g., "docker-build-push" (default), "security-scans", "all"
#   - OWNER_APPROVED_UNTIL (ISO8601 UTC) or OWNER_APPROVED_DURATION ("2h", "4h", "1d", "3w") — repo/environment variables
#   - COPILOT_AGENT_AUTH_ENABLED ("true") — set by agent-auth-delegation workflow after owner approval;
#     acts as an implicit approval bypass for cost-gated workflows (S112).
#   - COPILOT_AGENT_AUTH_BYPASS_TOOLS (comma-separated, optional, S113) — allowlist of TOOL_KEYs
#     eligible for the COPILOT_AGENT_AUTH_ENABLED bypass. If unset or empty, all TOOL_KEYs are
#     eligible (backward compatible). Set to e.g. "docker-build-push,security-scans" to restrict.
# Behavior:
#   - If COPILOT_AGENT_AUTH_ENABLED=true AND TOOL_KEY is in COPILOT_AGENT_AUTH_BYPASS_TOOLS
#     (or COPILOT_AGENT_AUTH_BYPASS_TOOLS is unset/empty), bypass is granted.
#   - Else if env overrides exist, they take precedence over file-based config.
#   - Else read .github/OWNER_APPROVAL.yml (simple YAML parsing via grep/sed/awk).
set -euo pipefail

TOOL_KEY="${TOOL_KEY:-docker-build-push}"
APPROVAL_FILE=".github/OWNER_APPROVAL.yml"

# If not provided, try to pick up from GitHub Actions env
WORKFLOW_NAME="${WORKFLOW_NAME:-${GITHUB_WORKFLOW:-}}"
RUN_ID="${RUN_ID:-${GITHUB_RUN_ID:-}}"
RUN_ATTEMPT="${RUN_ATTEMPT:-${GITHUB_RUN_ATTEMPT:-}}"
RUNNER_ENV="${RUNNER_ENV:-${GITHUB_JOB:-}}"
ACTOR="${ACTOR:-${GITHUB_ACTOR:-}}"
REPO="${REPO:-${GITHUB_REPOSITORY:-}}"
REF="${REF:-${GITHUB_REF:-}}"

# Evidence logging (JSONL) to support auditability under .codex/evidence/
CODEX_EVIDENCE="${CODEX_EVIDENCE:-1}"
CODEX_EVIDENCE_DIR="${CODEX_EVIDENCE_DIR:-.codex/evidence}"
evidence() {
  # evidence <decision> <source> <expiry_iso>
  [ "${CODEX_EVIDENCE}" = "1" ] || return 0
  mkdir -p "${CODEX_EVIDENCE_DIR}" 2>/dev/null || true
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  # Compose a compact JSON line (no external deps)
  printf '{"ts":"%s","workflow":"%s","run_id":"%s","run_attempt":"%s","job":"%s","actor":"%s","repo":"%s","ref":"%s","tool_key":"%s","decision":"%s","source":"%s","expiry":"%s","mode":"%s","duration":"%s","until":"%s","created_at":"%s","enabled":"%s","has_cost_key":"%s"}\n' \
    "${ts}" "${WORKFLOW_NAME}" "${RUN_ID}" "${RUN_ATTEMPT}" "${RUNNER_ENV}" "${ACTOR}" "${REPO}" "${REF}" "${TOOL_KEY}" "${1:-unknown}" "${2:-unknown}" "${3:-}" \
    "${mode:-}" "${duration:-}" "${until_ts:-}" "${created_at:-}" "${enabled:-}" "${has_cost_key:-}" \
    >> "${CODEX_EVIDENCE_DIR}/owner_approval.jsonl" 2>/dev/null || true
}

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

  # ── Provenance-chain bypass 1: session token file (A-001) ─────────────────
  # Written by agent-auth-delegation.yml activate-delegation job.
  # Allows one owner approval to cover ALL agent sessions within the TTL
  # (default: 14400s = 4 hours → raised to 43200s = 12 hours). Agent can renew by re-running the workflow.
  local _session_token_file="${CODEX_SESSION_TOKEN_FILE:-.codex/agent_auth_session.json}"
  if [ -f "${_session_token_file}" ]; then
    local _token_expiry
    _token_expiry="$(python3 -c "
import json, sys
try:
    d = json.load(open('${_session_token_file}'))
    print(int(d.get('expires_at', 0)))
except Exception:
    print(0)
" 2>/dev/null || echo 0)"
    if [ "${_token_expiry}" -gt "${now}" ] 2>/dev/null; then
      local _token_tools
      _token_tools="$(python3 -c "
import json
try:
    d = json.load(open('${_session_token_file}'))
    print(d.get('bypass_tools', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")"
      local _token_bypass_allowed="true"
      if [ -n "${_token_tools}" ]; then
        _token_bypass_allowed="false"
        IFS=',' read -ra _tktools <<< "${_token_tools}"
        for _tkt in "${_tktools[@]}"; do
          _tkt_clean="$(printf '%s' "${_tkt}" | trim)"
          if [ "${_tkt_clean}" = "${TOOL_KEY}" ]; then
            _token_bypass_allowed="true"
            break
          fi
        done
      fi
      if [ "${_token_bypass_allowed}" = "true" ]; then
        echo "[approval] APPROVED via session token (provenance-chain) for TOOL_KEY=${TOOL_KEY} (expires $(date -d @"${_token_expiry}" 2>/dev/null || date -r "${_token_expiry}" 2>/dev/null || echo "${_token_expiry}"))"
        evidence "approved" "session-token" ""
        return 0
      fi
    fi
  fi

  # ── Provenance-chain bypass 2: COPILOT_AGENT_AUTH_ENABLED env var ─────────
  # Bypass: COPILOT_AGENT_AUTH_ENABLED=true means the owner already approved agent
  # delegation via the PR checkbox + environment gate (agent-auth-delegation workflow).
  # COPILOT_AGENT_AUTH_BYPASS_TOOLS (optional, S113) restricts which TOOL_KEYs are eligible;
  # if unset or empty every TOOL_KEY is eligible (backward compatible with S112).

  if [ "${COPILOT_AGENT_AUTH_ENABLED:-}" = "true" ]; then
    local bypass_allowed="true"
    local bypass_tools="${COPILOT_AGENT_AUTH_BYPASS_TOOLS:-}"
    if [ -n "${bypass_tools}" ]; then
      # Check whether TOOL_KEY appears in the comma-separated allowlist (exact match).
      bypass_allowed="false"
      while IFS=, read -r -d '' item || [ -n "${item}" ]; do
        item_trimmed="$(printf '%s' "${item}" | trim)"
        if [ "${item_trimmed}" = "${TOOL_KEY}" ]; then
          bypass_allowed="true"
          break
        fi
      done < <(printf '%s\0' "${bypass_tools}")
      # Fallback: use a simple IFS loop for portability
      if [ "${bypass_allowed}" = "false" ]; then
        IFS=',' read -ra _tools <<< "${bypass_tools}"
        for _t in "${_tools[@]}"; do
          _t_clean="$(printf '%s' "${_t}" | trim)"
          if [ "${_t_clean}" = "${TOOL_KEY}" ]; then
            bypass_allowed="true"
            break
          fi
        done
      fi
    fi

    if [ "${bypass_allowed}" = "true" ]; then
      echo "[approval] APPROVED via COPILOT_AGENT_AUTH_ENABLED=true (agent delegation) for TOOL_KEY=${TOOL_KEY}"
      evidence "approved" "env-agent-auth" ""
      return 0
    else
      echo "[approval] COPILOT_AGENT_AUTH_ENABLED=true but TOOL_KEY=${TOOL_KEY} not in COPILOT_AGENT_AUTH_BYPASS_TOOLS allowlist (${bypass_tools}); falling through" >&2
    fi
  fi

  if [ -n "${OWNER_APPROVED_UNTIL:-}" ]; then
    ts="$(parse_iso_to_epoch "${OWNER_APPROVED_UNTIL}")" || {
      echo "[approval] OWNER_APPROVED_UNTIL is invalid: ${OWNER_APPROVED_UNTIL}" >&2
      evidence "denied" "env-until-invalid" ""
      return 2
    }
    if [ "$now" -le "$ts" ]; then
      echo "[approval] APPROVED via OWNER_APPROVED_UNTIL (${OWNER_APPROVED_UNTIL}) for TOOL_KEY=${TOOL_KEY}"
      evidence "approved" "env-until" "${OWNER_APPROVED_UNTIL}"
      return 0
    else
      echo "[approval] OWNER_APPROVED_UNTIL expired (${OWNER_APPROVED_UNTIL})" >&2
      evidence "denied" "env-until-expired" "${OWNER_APPROVED_UNTIL}"
      return 2
    fi
  fi

  if [ -n "${OWNER_APPROVED_DURATION:-}" ]; then
    local secs
    secs="$(parse_duration_to_secs "${OWNER_APPROVED_DURATION}")" || {
      echo "[approval] OWNER_APPROVED_DURATION invalid: ${OWNER_APPROVED_DURATION}" >&2
      evidence "denied" "env-duration-invalid" ""
      return 2
    }
    local until_epoch="$(( now + secs ))"
    local until_iso
    until_iso="$(date -u -d "@$until_epoch" +%Y-%m-%dT%H:%M:%SZ)"
    echo "[approval] APPROVED via OWNER_APPROVED_DURATION=${OWNER_APPROVED_DURATION} until ${until_iso} for TOOL_KEY=${TOOL_KEY}"
    evidence "approved" "env-duration" "${until_iso}"
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
  evidence "denied" "file-missing" ""
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
  evidence "denied" "file-disabled" ""
  exit 2
fi

if [ "${has_cost_key}" != "true" ]; then
  echo "[approval] TOOL_KEY=${TOOL_KEY} not listed in cost_workflows; deny" >&2
  evidence "denied" "file-missing-tool-key" ""
  exit 2
fi

now="$(now_epoch)"
# Compute expiry by mode
if [ "${mode}" = "until" ]; then
  [ -z "${until_ts}" ] && { echo "[approval] mode=until but 'until' not set; deny" >&2; evidence "denied" "file-until-missing" ""; exit 2; }
  exp="$(parse_iso_to_epoch "${until_ts}")" || { echo "[approval] 'until' invalid: ${until_ts}" >&2; evidence "denied" "file-until-invalid" ""; exit 2; }
elif [ "${mode}" = "duration" ]; then
  [ -z "${duration}" ] && { echo "[approval] mode=duration but 'duration' empty; deny" >&2; evidence "denied" "file-duration-missing" ""; exit 2; }
  secs="$(parse_duration_to_secs "${duration}")" || { echo "[approval] duration invalid: ${duration}" >&2; evidence "denied" "file-duration-invalid" ""; exit 2; }
  # Determine start time: created_at (preferred), then git last change time of this file, else file mtime.
  if [ -n "${created_at}" ]; then
    start="$(parse_iso_to_epoch "${created_at}")" || { echo "[approval] created_at invalid: ${created_at}" >&2; evidence "denied" "file-created_at-invalid" ""; exit 2; }
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
  evidence "denied" "file-mode-invalid" ""
  exit 2
fi

if [ "$now" -le "$exp" ]; then
  until_iso="$(date -u -d "@$exp" +%Y-%m-%dT%H:%M:%SZ)"
  echo "[approval] APPROVED until ${until_iso} for TOOL_KEY=${TOOL_KEY}"
  evidence "approved" "file-${mode}" "${until_iso}"
  exit 0
fi

echo "[approval] Window expired at $(date -u -d "@$exp" +%Y-%m-%dT%H:%M:%SZ); deny" >&2
evidence "denied" "file-expired" "$(date -u -d "@$exp" +%Y-%m-%dT%H:%M:%SZ)"
exit 2
