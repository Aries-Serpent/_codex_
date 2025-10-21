#!/usr/bin/env bash
# List repository Actions variables (json or pretty).
# Usage:
#   bash scripts/runner/list_repo_vars.sh --owner Aries-Serpent --repo _codex_ [--format json|pretty]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

OWNER=""
REPO=""
FORMAT="pretty" # default

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  echo "Usage: $0 --owner <owner> --repo <repo> [--format json|pretty]" >&2
  exit 2
fi

url="https://api.github.com/repos/${OWNER}/${REPO}/actions/variables?per_page=100"
json="$(api_call GET "${url}" || true)"
if [[ -z "${json}" ]]; then
  echo "[vars] No data returned" >&2
  exit 0
fi

if [[ "${FORMAT}" == "json" ]]; then
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "${json}" | jq .
  elif command -v python >/dev/null 2>&1; then
    python - <<'PY'
import json, sys
print(json.dumps(json.loads(sys.stdin.read()), indent=2))
PY
  else
    printf '%s' "${json}"
  fi
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  echo "=== Repo variables: ${OWNER}/${REPO} ==="
  printf '%s' "${json}" | jq -r '
    .variables[]? | [
      .name,
      (.value|tostring),
      .updated_at
    ] | @tsv
  ' | awk -F'\t' 'BEGIN{printf("%-32s %-40s %-25s\n","NAME","VALUE","UPDATED_AT")} {printf("%-32s %-40s %-25s\n",$1,substr($2,1,40),$3)}'
else
  printf '%s\n' "${json}"
fi
