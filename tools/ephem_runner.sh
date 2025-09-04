#!/usr/bin/env bash
set -euo pipefail
# Ephemeral (single-job) GitHub Actions runner bring-up for Aries-Serpent/_codex_.
# No workflow edits. Requires GH_PAT and minimal label set.
#
# Usage (auto labels from queued jobs):
#   GH_PAT=... tools/ephem_runner.sh --auto-labels --branch 0B_base_
#
# Or provide labels explicitly:
#   GH_PAT=... tools/ephem_runner.sh --labels linux,x64,codex
#
# Required: GH_PAT in env (repo/org admin for registration token).

OWNER="${OWNER:-Aries-Serpent}"
REPO="${REPO:-_codex_}"
BRANCH="${BRANCH:-0B_base_}"
RUNNER_VERSION="${RUNNER_VERSION:-2.328.0}"
RUNNER_PKG="actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
RUNNER_SHA256_DEFAULT="01066fad3a2893e63e6ca880ae3a1fad5bf9329d60e77ee15f2b97c148c3cd4e"  # pragma: allowlist secret
# Allow env secret to override expected checksum
RUNNER_SHA256="${CODEX_RUNNER_SHA256:-${RUNNER_SHA256:-$RUNNER_SHA256_DEFAULT}}"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_PKG}"
WORK_DIR="${WORK_DIR:-_work}"
DISABLE_UPDATE="${DISABLE_UPDATE:-1}"
NAME_PREFIX="${NAME_PREFIX:-codex-ephem}"
LABELS="${LABELS:-}"
AUTO_LABELS=0
RUNNER_TOKEN_OVERRIDE="${CODEX_RUNNER_TOKEN:-}"

# Print error and exit
_die() {
  echo "ERROR: $*" >&2
  exit 1
}

# Ensure dependency exists
_need() {
  command -v "$1" >/dev/null 2>&1 || _die "Missing dependency: $1"
}

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner)
      OWNER="$2"
      shift 2
      ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --labels)
      LABELS="$2"
      shift 2
      ;;
    --auto-labels)
      AUTO_LABELS=1
      shift
      ;;
    --runner-version)
      RUNNER_VERSION="$2"
      RUNNER_PKG="actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
      RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_PKG}"
      shift 2
      ;;
    --work-dir)
      WORK_DIR="$2"
      shift 2
      ;;
    --name-prefix)
      NAME_PREFIX="$2"
      shift 2
      ;;
    --no-disable-update)
      DISABLE_UPDATE=0
      shift
      ;;
    -h|--help)
      sed -n '1,120p' "$0"
      exit 0
      ;;
    *)
      _die "Unknown arg: $1"
      ;;
  esac
done

[[ -n "${GH_PAT:-}" ]] || { [[ -n "$RUNNER_TOKEN_OVERRIDE" ]] || _die "GH_PAT not set (or CODEX_RUNNER_TOKEN missing)."; }

_need curl
_need tar
command -v sha256sum >/dev/null 2>&1 || command -v shasum >/dev/null 2>&1 || _die "Missing sha256sum/shasum"

if [[ ${AUTO_LABELS} -eq 1 ]]; then
  _need python3
  LABELS="$(python3 tools/preflight_minimal_labels.py \
    --owner "$OWNER" --repo "$REPO" --branch "$BRANCH" \
    --gh-pat "$GH_PAT")" || _die "preflight label computation failed"
  [[ -n "$LABELS" ]] || _die "preflight returned empty labels"
fi

REPO_URL="https://github.com/${OWNER}/${REPO}"
mkdir -p actions-runner
cd actions-runner

# Prefer explicit override token if provided; otherwise create a short-lived
# registration token via the documented REST endpoint (expires ~1h).
# Ref: REST – Create a registration token for a repository.
# https://docs.github.com/en/rest/actions/self-hosted-runners
if [[ -n "$RUNNER_TOKEN_OVERRIDE" ]]; then
  REG_TOKEN="$RUNNER_TOKEN_OVERRIDE"
else
  REG_TOKEN_JSON="$(curl -fsSL -X POST \
    -H "Authorization: Bearer ${GH_PAT}" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${OWNER}/${REPO}/actions/runners/registration-token")"
  if command -v jq >/dev/null 2>&1; then
    REG_TOKEN="$(printf '%s' "$REG_TOKEN_JSON" | jq -r '.token')"
  else
    REG_TOKEN="$(python3 - <<'PY'
import json,sys
print(json.load(sys.stdin)['token'])
PY
)"
  fi
fi

[[ -n "$REG_TOKEN" && "$REG_TOKEN" != "null" ]] || _die "Failed to fetch registration token"

curl -fsSL -o "$RUNNER_PKG" "$RUNNER_URL"
# Verify archive integrity (prefer sha256sum; fallback to shasum -a 256)
if command -v sha256sum >/dev/null 2>&1; then
  echo "${RUNNER_SHA256}  ${RUNNER_PKG}" | sha256sum -c
else
  echo "${RUNNER_SHA256}  ${RUNNER_PKG}" | shasum -a 256 -c
fi

tar xzf "$RUNNER_PKG"

./config.sh --check --url "$REPO_URL" || true

NAME="${NAME_PREFIX}-$(hostname)-$RANDOM"
# --ephemeral ensures a runner performs exactly one job then auto-deregisters.
# GitHub documents ephemeral one-job behavior and the --ephemeral flag
# (self-hosted runner security / JIT/ephemeral guidance).
CONFIG_ARGS=(--url "$REPO_URL" --token "$REG_TOKEN" --name "$NAME" --work "$WORK_DIR" --unattended --ephemeral)
[[ -n "$LABELS" ]] && CONFIG_ARGS+=(--labels "$LABELS")
[[ $DISABLE_UPDATE -eq 1 ]] && CONFIG_ARGS+=(--disableupdate)

./config.sh "${CONFIG_ARGS[@]}"

# Run once; after the job completes, the runner deregisters server-side.
# Local artifacts remain in $WORK_DIR and may be cleaned by a janitor.
exec ./run.sh
