#!/usr/bin/env bash
set -euo pipefail
# Offline-safe wrapper to show the exact commands required to register a self-hosted runner.
# This does not call GitHub Actions or create workflows; it only prints or runs the official runner steps.
#
# Requires:
#   - CODEX_RUNNER_TOKEN  : short-lived runner registration token (provided by your org/repo)
#   - CODEX_RUNNER_URL    : e.g., https://github.com/Aries-Serpent/_codex_
#   - (optional) CODEX_RUNNER_LABELS : comma-separated labels
#   - (optional) CODEX_RUNNER_NAME   : name for this runner
#
# Usage:
#   DRY_RUN=1 tools/github/runner_register.sh   # print without executing
#   tools/github/runner_register.sh             # execute

: "${CODEX_RUNNER_TOKEN:?set CODEX_RUNNER_TOKEN}"
: "${CODEX_RUNNER_URL:?set CODEX_RUNNER_URL}"
: "${CODEX_RUNNER_LABELS:=codex,self-hosted,linux}"
: "${CODEX_RUNNER_NAME:=codex-runner-$(hostname)-$RANDOM}"
: "${CODEX_RUNNER_VERSION:=2.319.1}"
: "${DRY_RUN:=0}"

step() { echo "[$(date -u +%FT%TZ)] $*"; }
run()  {
  if [ "${DRY_RUN}" = "1" ]; then
    printf '+%s' ""
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

main() {
  local runner_version="${CODEX_RUNNER_VERSION}"
  local runner_tarball="actions-runner-linux-x64-${runner_version}.tar.gz"
  local runner_url="https://github.com/actions/runner/releases/download/v${runner_version}/${runner_tarball}"
  step "Downloading runner (Linux x64)"
  run curl -sS -L -o "${runner_tarball}" "${runner_url}"
  run mkdir -p .runner
  run tar xzf "${runner_tarball}" -C .runner --strip-components=0
  step "Configuring runner for ${CODEX_RUNNER_URL}"
  if [ "${DRY_RUN}" = "1" ]; then
    printf '+ cd .runner && ./config.sh --url %s --token %s --labels %s --name %s --unattended --replace\n' \
      "${CODEX_RUNNER_URL}" "${CODEX_RUNNER_TOKEN}" "${CODEX_RUNNER_LABELS}" "${CODEX_RUNNER_NAME}"
  else
    ( cd .runner && ./config.sh --url "${CODEX_RUNNER_URL}" --token "${CODEX_RUNNER_TOKEN}" \
      --labels "${CODEX_RUNNER_LABELS}" --name "${CODEX_RUNNER_NAME}" --unattended --replace )
  fi
  step "To start the runner in the foreground:"
  echo "  cd .runner && ./run.sh"
}

main "$@"
