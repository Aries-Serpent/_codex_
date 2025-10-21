#!/usr/bin/env bash
# Disable workflows by moving them to .github/_workflows_disabled/ when OWNER approval window has expired.
# Triggers on push/cron/dispatch; applies on push (next user commit) as requested.
set -euo pipefail

WF_DIR=".github/workflows"
DISABLED_DIR=".github/_workflows_disabled"
ENFORCER_FILE="workflow-expiry-enforcer.yml"

mkdir -p "${DISABLED_DIR}"

# Parse approval window from .github/OWNER_APPROVAL.yml (file mode) or env mode as fallback
CFG_FILE=".github/OWNER_APPROVAL.yml"
now_epoch="$(date -u +%s)"

expired="false"

if [ -f "${CFG_FILE}" ]; then
  enabled_val="$(grep -E '^[[:space:]]*enabled:[[:space:]]*' "${CFG_FILE}" | awk -F: '{gsub(/[[:space:]]*/, "", $2); print tolower($2)}' || true)"
  mode_val="$(grep -E '^[[:space:]]*mode:[[:space:]]*' "${CFG_FILE}" | awk -F: '{gsub(/[[:space:]]*/, "", $2); print tolower($2)}' || true)"
  created_at_val="$(grep -E '^[[:space:]]*created_at:[[:space:]]*' "${CFG_FILE}" | awk -F: '{sub(/^[[:space:]]*/, "", $2); print $2}' | tr -d '"' || true)"
  duration_val="$(grep -E '^[[:space:]]*duration:[[:space:]]*' "${CFG_FILE}" | awk -F: '{sub(/^[[:space:]]*/, "", $2); print $2}' | tr -d '"' || true)"
  until_val="$(grep -E '^[[:space:]]*until:[[:space:]]*' "${CFG_FILE}" | awk -F: '{sub(/^[[:space:]]*/, "", $2); print $2}' | tr -d '"' || true)"

  if [ "${enabled_val:-}" = "true" ]; then
    if [ "${mode_val:-}" = "duration" ] && [ -n "${created_at_val:-}" ] && [ -n "${duration_val:-}" ]; then
      exp_epoch="$(date -u -d "${created_at_val} ${duration_val}" +%s 2>/dev/null || true)"
      if [ -z "${exp_epoch:-}" ]; then
        echo "[enforcer] WARN: could not compute expiry from created_at=${created_at_val} duration=${duration_val}"
      elif [ "${now_epoch}" -ge "${exp_epoch}" ]; then
        expired="true"
      fi
    elif [ "${mode_val:-}" = "until" ] && [ -n "${until_val:-}" ]; then
      exp_epoch="$(date -u -d "${until_val}" +%s 2>/dev/null || true)"
      if [ -z "${exp_epoch:-}" ]; then
        echo "[enforcer] WARN: could not parse until=${until_val}"
      elif [ "${now_epoch}" -ge "${exp_epoch}" ]; then
        expired="true"
      fi
    else
      echo "[enforcer] INFO: OWNER_APPROVAL.yml present but not in recognized mode (duration/until). No action."
    fi
  else
    echo "[enforcer] INFO: OWNER_APPROVAL.yml enabled=false or missing; treating as expired=no-op."
  fi
fi

# Fallback to env mode if file didn't yield a decision
if [ "${expired}" = "false" ]; then
  if [ -n "${OWNER_APPROVED_UNTIL:-}" ]; then
    exp_epoch="$(date -u -d "${OWNER_APPROVED_UNTIL}" +%s 2>/dev/null || true)"
    if [ -n "${exp_epoch:-}" ] && [ "${now_epoch}" -ge "${exp_epoch}" ]; then
      expired="true"
    fi
  elif [ -n "${OWNER_APPROVED_DURATION:-}" ]; then
    # Without a reference start, we can't compute absolute expiry. Assume not expired.
    :
  fi
fi

if [ "${expired}" != "true" ]; then
  echo "[enforcer] Approval window active or undetermined; no workflows moved."
  exit 0
fi

echo "[enforcer] Approval window expired — disabling workflows by moving files from ${WF_DIR} to ${DISABLED_DIR}"

# Find workflow files to move, excluding the enforcer itself
shopt -s nullglob
wf_to_move=()
for f in ${WF_DIR}/*.yml ${WF_DIR}/*.yaml; do
  base="$(basename "$f")"
  if [ "${base}" = "${ENFORCER_FILE}" ]; then
    continue
  fi
  wf_to_move+=("$f")
done

if [ "${#wf_to_move[@]}" -eq 0 ]; then
  echo "[enforcer] No workflows to move. Already disabled or none present."
  exit 0
fi

# Configure git
git config user.name "${GIT_AUTHOR_NAME:-codex-bot}"
git config user.email "${GIT_AUTHOR_EMAIL:-codex-bot@users.noreply.github.com}"

# Move files
for f in "${wf_to_move[@]}"; do
  base="$(basename "$f")"
  dest="${DISABLED_DIR}/${base}"
  mkdir -p "${DISABLED_DIR}"
  {
    echo "# Auto-moved by Workflow Expiry Enforcer on $(date -u +"%Y-%m-%dT%H:%M:%SZ") due to approval window expiry"
    cat "$f"
  } > "${dest}"
  git rm -f "$f" >/dev/null
  git add "${dest}" >/dev/null
  echo "[enforcer] moved ${f} -> ${dest}"
done

# Commit and push
branch="${GITHUB_REF_NAME:-}"
if [ -z "${branch}" ]; then
  # Fallback to current HEAD branch name
  branch="$(git rev-parse --abbrev-ref HEAD)"
fi

if ! git diff --cached --quiet; then
  git commit -m "chore(enforcer): auto-disable workflows after approval window expiry" >/dev/null || {
    echo "[enforcer] Nothing to commit."
    exit 0
  }
else
  echo "[enforcer] No staged changes after moving workflows."
  exit 0
fi

set +e
git push origin "HEAD:${branch}"
rc=$?
set -e

if [ ${rc} -ne 0 ]; then
  echo "[enforcer] WARN: push to ${branch} failed (possibly protected). Please open a PR to merge these changes."
  exit 0
fi

echo "[enforcer] Completed moving workflows and pushed commit to ${branch}."
