#!/usr/bin/env bash
# Guard cost-incurring workflows behind owner approval windows.
# Success (0) when approval is currently valid for TOOL_KEY; failure (1/2) otherwise.
# Inputs:
#   - TOOL_KEY (string): logical workflow key e.g., "docker-build-push" (default), "security-scans", "all"
#   - OWNER_APPROVED_UNTIL (ISO8601 UTC) or OWNER_APPROVED_DURATION ("2h", "4h", "1d", "3w") — protected workflow/environment inputs
#   - COPILOT_AGENT_AUTH_ENABLED ("true") — caller must guarantee protected owner approval;
#     retains the environment bypass for cost-gated workflows (S112).
#   - COPILOT_AGENT_AUTH_BYPASS_TOOLS (comma-separated, optional, S113) — allowlist of TOOL_KEYs
#     eligible for the COPILOT_AGENT_AUTH_ENABLED bypass. If unset or empty, all TOOL_KEYs are
#     eligible (backward compatible). Set to e.g. "docker-build-push,security-scans" to restrict.
# Behavior:
#   - If COPILOT_AGENT_AUTH_ENABLED=true AND TOOL_KEY is in COPILOT_AGENT_AUTH_BYPASS_TOOLS
#     (or COPILOT_AGENT_AUTH_BYPASS_TOOLS is unset/empty), bypass is granted.
#   - Else evaluate explicit environment approval windows; missing approval denies.
#   - Worktree JSON/YAML files are evidence only, never approval authority.
# In CI, run this guard from trusted code before executing PR content. Supply
# approval inputs only through protected workflow/environment configuration.
set -euo pipefail

TOOL_KEY="${TOOL_KEY:-docker-build-push}"

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

  # ── Protected environment: COPILOT_AGENT_AUTH_ENABLED ────────────────────
  # The caller must establish owner approval through a protected environment;
  # a delegation flag or PR checkbox alone does not establish that guarantee.
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

# Environment approval is the only authority; preserve explicit denial.
if approve_via_env; then
  exit 0
else
  rc=$?
fi

if [ "${rc}" -ne 3 ]; then
  exit "${rc}"
fi

echo "[approval] No protected environment approval; worktree files cannot authorize TOOL_KEY=${TOOL_KEY}" >&2
evidence "denied" "env-missing" ""
exit 2
