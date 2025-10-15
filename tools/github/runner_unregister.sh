#!/usr/bin/env bash
set -euo pipefail
# Remove a self-hosted runner configuration using the official runner script.
# This does NOT create or run any GitHub Actions. It simply executes:
#   .runner/config.sh remove --token <TOKEN>
#
# Required env:
#   CODEX_RUNNER_TOKEN  : runner removal token (short-lived from org/repo settings)
# Optional env:
#   CODEX_RUNNER_DIR    : directory of the installed runner (default: .runner)
#   DRY_RUN             : set to 1 to print commands without executing
#
# Usage:
#   DRY_RUN=1 tools/github/runner_unregister.sh
#   tools/github/runner_unregister.sh

: "${CODEX_RUNNER_TOKEN:?set CODEX_RUNNER_TOKEN}"
: "${CODEX_RUNNER_DIR:=.runner}"
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
  if [ ! -x "${CODEX_RUNNER_DIR}/config.sh" ]; then
    echo "[runner_unregister] missing ${CODEX_RUNNER_DIR}/config.sh" >&2
    exit 2
  fi
  step "Removing runner from $(pwd)/${CODEX_RUNNER_DIR}"
  if [ "${DRY_RUN}" = "1" ]; then
    printf '+ cd %q && ./config.sh remove --token %q\n' "${CODEX_RUNNER_DIR}" "${CODEX_RUNNER_TOKEN}"
  else
    ( cd "${CODEX_RUNNER_DIR}" && ./config.sh remove --token "${CODEX_RUNNER_TOKEN}" )
  fi
  step "Done. You can delete ${CODEX_RUNNER_DIR} if no longer needed."
}

main "$@"
