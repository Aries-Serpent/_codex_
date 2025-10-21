#!/usr/bin/env bash
# Show self-hosted runner status for org and/or repo.
# Requirements: GH_PAT or _CODEX_BOT_RUNNER in env, curl; jq optional.
#
# Examples:
#   bash scripts/runner/runner_status.sh --org Aries-Serpent
#   bash scripts/runner/runner_status.sh --owner Aries-Serpent --repo _codex_
#   bash scripts/runner/runner_status.sh --org Aries-Serpent --format pretty
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

ORG=""
OWNER=""
REPO=""
FORMAT="json"  # json|pretty

while [[ $# -gt 0 ]]; do
  case "$1" in
    --org) ORG="$2"; shift 2 ;;
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac

done

print_pretty() {
  local scope="$1"
  local json="$2"
  if [[ -z "${json}" ]]; then
    echo "[${scope}] No data returned" >&2
    return 0
  fi
  if ! command -v jq >/dev/null 2>&1; then
    echo "[${scope}] (raw json below)"
    echo "${json}"
    return 0
  fi
  echo "=== ${scope} runners ==="
  echo "${json}" | jq -r '
    .runners[]? | [
      (.id|tostring),
      .name,
      (if .busy then "busy" else "idle" end),
      (if .online then "online" else "offline" end),
      (.labels|map(.name)|join(","))
    ] | @tsv
  ' | awk -F'\t' 'BEGIN{printf("%-8s %-30s %-6s %-7s %s\n","ID","NAME","BUSY","ONLINE","LABELS")} {printf("%-8s %-30s %-6s %-7s %s\n",$1,$2,$3,$4,$5)}'
}

# Org scope
if [[ -n "${ORG}" ]]; then
  org_json="$(api_call GET "https://api.github.com/orgs/${ORG}/actions/runners" || true)"
  if [[ "${FORMAT}" == "pretty" ]]; then
    print_pretty "org:${ORG}" "${org_json}"
  else
    if [[ -n "${org_json}" ]]; then
      echo "${org_json}" | json_pp
    else
      echo "[org:${ORG}] No data returned" >&2
    fi
  fi
fi

# Repo scope
if [[ -n "${OWNER}" && -n "${REPO}" ]]; then
  repo_json="$(api_call GET "https://api.github.com/repos/${OWNER}/${REPO}/actions/runners" || true)"
  if [[ "${FORMAT}" == "pretty" ]]; then
    print_pretty "repo:${OWNER}/${REPO}" "${repo_json}"
  else
    if [[ -n "${repo_json}" ]]; then
      echo "${repo_json}" | json_pp
    else
      echo "[repo:${OWNER}/${REPO}] No data returned" >&2
    fi
  fi
fi

if [[ -z "${ORG}" && ( -z "${OWNER}" || -z "${REPO}" ) ]]; then
  echo "Usage: $0 [--org <org>] [--owner <owner> --repo <repo>] [--format json|pretty]" >&2
  exit 2
fi
