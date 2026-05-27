#!/usr/bin/env bash
# safe_git_show.sh — Guard wrapper for `git show <ref> -- <file>`
#
# Problem: `git show <base_sha> -- <file>` exits 128 when <file> was added
# AFTER <base_sha>.  This poisons diffs in CI steps and agent sessions.
#
# Sourcing contract:
#   When sourced (e.g., `source scripts/ci/safe_git_show.sh`), this script does
#   NOT set shell options (set -euo pipefail). Callers are responsible for their
#   own shell option state. This is intentional — sourced helpers should not
#   mutate caller shell state. Both `.github/workflows/copilot-setup-steps.yml`
#   and `.devcontainer/scripts/post-start.sh` set their own `set -euo pipefail`.
#
# Usage:
#   source scripts/ci/safe_git_show.sh
#   safe_git_show "$BASE_SHA" "path/to/file.py"    # prints content or empty
#   safe_git_diff "$BASE_SHA" "HEAD" "path/to/file" # prints diff or full file
#   safe_git_show_with_head_fallback "$BASE_SHA" "path/to/file.py" # best-available
#
# Or run directly:
#   bash scripts/ci/safe_git_show.sh <ref> <file>

# safe_git_show REF FILE
#   Outputs the file content at REF, or nothing if the file doesn't exist at REF.
#   Exit code: 0 always (never exits 128).
safe_git_show() {
  local ref="${1:?ref required}"
  local file="${2:?file path required}"

  # Check whether the file exists in the given ref's tree
  if git cat-file -e "${ref}:${file}" 2>/dev/null; then
    git show "${ref}:${file}"
  else
    # File does not exist at this ref (new file) — return empty
    return 0
  fi
}

# safe_git_diff BASE_REF HEAD_REF FILE
#   Produces a diff between BASE_REF and HEAD_REF for FILE.
#   If the file is new (doesn't exist at BASE_REF), diffs against /dev/null.
safe_git_diff() {
  local base_ref="${1:?base ref required}"
  local head_ref="${2:?head ref required}"
  local file="${3:?file path required}"

  if git cat-file -e "${base_ref}:${file}" 2>/dev/null; then
    # File exists at both refs — normal diff
    git diff "${base_ref}" "${head_ref}" -- "${file}" || true
  else
    # File is new (added after base_ref) — diff against /dev/null
    if git cat-file -e "${head_ref}:${file}" 2>/dev/null; then
      git diff --no-index /dev/null <(git show "${head_ref}:${file}") 2>/dev/null || true
    else
      echo "warning: ${file} does not exist at ${base_ref} or ${head_ref}" >&2
      return 1
    fi
  fi
}

# safe_git_show_with_head_fallback REF FILE
#   Like safe_git_show, but falls back to HEAD content if FILE doesn't exist at REF.
#   Useful when you want the "best available" version (e.g., for diff context).
#   Exit code: 0 always.
safe_git_show_with_head_fallback() {
  local ref="${1:?ref required}"
  local file="${2:?file path required}"

  if git cat-file -e "${ref}:${file}" 2>/dev/null; then
    git show "${ref}:${file}"
  elif git cat-file -e "HEAD:${file}" 2>/dev/null; then
    # File not at ref but present at HEAD — use HEAD version as fallback
    git show "HEAD:${file}"
  elif [ -f "${file}" ]; then
    # Not in git at all yet — use working tree copy
    cat "${file}" || true
  else
    return 0
  fi
}

# If invoked directly (not sourced), run safe_git_show with args
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -euo pipefail
  if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <ref> <file>" >&2
    exit 1
  fi
  safe_git_show "$1" "$2"
fi
