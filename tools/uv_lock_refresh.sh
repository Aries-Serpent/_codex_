#!/usr/bin/env bash
set -euo pipefail

# Refresh the project's dependency lock deterministically.
# Preferred flow:
#   A) If pyproject.toml exists: produce/refresh uv.lock
#        uv lock
#      (Optionally validate without updating using: uv lock --check)
#   B) If no pyproject.toml, fall back to requirements-style locking:
#        uv pip compile <inputs> -o <outputs>
#      This won't create uv.lock, but will create pinned requirement files.
#
# Notes:
# - Use on a clean working tree; commit the resulting lock files.
# - Combine with wheelhouse for fully offline installs after locking.
#
# Usage examples:
#   tools/uv_lock_refresh.sh
#   tools/uv_lock_refresh.sh -i requirements.in -o requirements.txt
#   tools/uv_lock_refresh.sh -i requirements.txt -o requirements.lock
#
# After running, this script prints "next steps" guidance for Codex.

has_pyproject=0
[[ -f "pyproject.toml" ]] && has_pyproject=1

IN_FILE=""
OUT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--input)  IN_FILE="$2"; shift 2 ;;
    -o|--output) OUT_FILE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 'uv' not found on PATH. Install uv first: https://docs.astral.sh/uv/" >&2
  exit 127
fi

if [[ $has_pyproject -eq 1 ]]; then
  echo ">>> pyproject.toml detected — refreshing uv.lock"
  uv lock
  echo
  echo "=== Next steps (project lock) ==="
  echo "1) Review and commit uv.lock"
  echo "2) For deterministic installs: uv sync --frozen"
  echo "3) Optional validation: uv lock --check"
else
  if [[ -z "${IN_FILE}" || -z "${OUT_FILE}" ]]; then
    echo ">>> No pyproject.toml; requirements-mode locking requires -i and -o."
    echo "Example: tools/uv_lock_refresh.sh -i requirements.in -o requirements.txt"
    exit 2
  fi
  if [[ ! -f "${IN_FILE}" ]]; then
    echo "ERROR: Input file not found: ${IN_FILE}" >&2
    exit 2
  fi
  echo ">>> requirements-mode locking — compiling ${IN_FILE} -> ${OUT_FILE}"
  uv pip compile "${IN_FILE}" -o "${OUT_FILE}"
  echo
  echo "=== Next steps (requirements lock) ==="
  echo "1) Review and commit ${OUT_FILE}"
  echo "2) For deterministic installs: uv pip sync ${OUT_FILE}"
fi
