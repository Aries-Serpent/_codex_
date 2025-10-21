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

# Ensure a command exists in PATH (fails fast with a readable error)
require_cmd() {
  local binary="$1"
  if ! command -v "${binary}" >/dev/null 2>&1; then
    echo "[common] ERROR: required command '${binary}' not found" >&2
    exit 1
  fi
}

# Extract the owner and repository name from a GitHub URL or slug.
# Supports https/http/git/ssh URLs as well as plain "owner/repo" strings and
# tolerates optional trailing slashes, ".git" suffixes, and query fragments.
parse_owner_repo() {
  local input="$1"
  # Drop query or fragment components early.
  local cleaned="${input%%[?#]*}"
  # Trim trailing slashes and optional .git suffix.
  cleaned="${cleaned%/}"
  cleaned="${cleaned%.git}"

  case "${cleaned}" in
    git@github.com:*)
      cleaned="${cleaned#git@github.com:}"
      ;;
    ssh://git@github.com/*)
      cleaned="${cleaned#ssh://git@github.com/}"
      ;;
    https://github.com/*)
      cleaned="${cleaned#https://github.com/}"
      ;;
    http://github.com/*)
      cleaned="${cleaned#http://github.com/}"
      ;;
    git://github.com/*)
      cleaned="${cleaned#git://github.com/}"
      ;;
    github.com/*)
      cleaned="${cleaned#github.com/}"
      ;;
    *)
      # Fall back to stripping everything before the github.com host if present,
      # which keeps support for credentialed URLs like https://token@github.com/owner/repo
      # or git@github.com:owner/repo.
      local with_host="${cleaned#*github.com/}"
      if [[ "${with_host}" != "${cleaned}" ]]; then
        cleaned="${with_host}"
      else
        with_host="${cleaned#*github.com:}"
        if [[ "${with_host}" != "${cleaned}" ]]; then
          cleaned="${with_host}"
        else
          cleaned="${cleaned#https://}"
          cleaned="${cleaned#http://}"
          cleaned="${cleaned#ssh://}"
          cleaned="${cleaned#git://}"
        fi
      fi
      ;;
  esac

  # Remove any lingering github.com prefix variants or leading separators.
  cleaned="${cleaned#github.com/}"
  cleaned="${cleaned#github.com:}"
  cleaned="${cleaned#/}"

  # Organization URLs from the GitHub UI include an "orgs" prefix. Drop it so the
  # owner segment resolves to the actual organization name instead of "orgs".
  if [[ "${cleaned}" == orgs/* ]]; then
    cleaned="${cleaned#orgs/}"
  fi

  local owner="${cleaned%%/*}"
  local repo=""
  if [[ -n "${owner}" && "${cleaned}" != "${owner}" ]]; then
    repo="${cleaned#*/}"
    repo="${repo%%/*}"
  fi
  repo="${repo%.git}"
  repo="${repo%/}"

  echo "${owner}" "${repo}"
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
