#!/usr/bin/env bash
set -euo pipefail

# Build a local wheelhouse for offline/hermetic installs.
# Usage:
#   tools/make_wheelhouse.sh [-o WHEEL_DIR] [-c CONSTRAINTS] -r requirements.txt [-r more.txt ...]
#
# Default outputs:
#   ./wheelhouse/         (downloaded wheels)
#   ./constraints.txt     (generated or updated constraints)
#
# Strategy:
#   1) If a constraints file is provided, use it. Otherwise try:
#      a) `uv pip compile` to produce constraints.txt (fast path), else
#      b) fallback to `pip freeze` after a temp install to pin versions.
#   2) Use `python -m pip download ... -d wheelhouse` for all -r files.
#   3) Result can be consumed via:
#        python -m pip install --no-index --find-links ./wheelhouse -r requirements.txt
#
# Notes:
# - uv currently does not implement `pip download`/`pip wheel`; use pip for the wheelhouse step.
# - Constraints clarify exact versions; requirements still decide *what* to install.
#
# Refs: pip cache/wheel/doc + offline install patterns; uv compile; missing uv download/wheel cmds.

wheel_dir="./wheelhouse"
constraints_file=""
reqs=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--out) wheel_dir="$2"; shift 2 ;;
    -c|--constraints) constraints_file="$2"; shift 2 ;;
    -r|--requirement) reqs+=("$2"); shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ ${#reqs[@]} -eq 0 ]]; then
  echo "ERROR: supply at least one -r requirements file" >&2
  exit 2
fi

mkdir -p "$wheel_dir"

# Produce constraints if not supplied.
if [[ -z "${constraints_file}" ]]; then
  constraints_file="constraints.txt"
  echo ">>> Generating ${constraints_file}"
  if command -v uv >/dev/null 2>&1; then
    # Fast path: uv compile requirements into a lock/constraints file.
    # Example: uv pip compile requirements.in --constraint base-constraints.txt
    # If multiple -r files are provided, compile them one-by-one and merge.
    > "${constraints_file}"
    for r in "${reqs[@]}"; do
      echo "    uv pip compile ${r} -> ${constraints_file}"
      # Append compiled pins to constraints (simple merge).
      uv pip compile "${r}" >> "${constraints_file}"
    done
  else
    # Fallback: create a temp venv, install reqs, then freeze.
    tmpdir="$(mktemp -d)"
    python -m venv "${tmpdir}/venv"
    # shellcheck disable=SC1091
    source "${tmpdir}/venv/bin/activate"
    python -m pip install --upgrade pip
    for r in "${reqs[@]}"; do
      python -m pip install -r "${r}"
    done
    python -m pip freeze > "${constraints_file}"
    deactivate
    rm -rf "${tmpdir}"
  fi
fi

echo ">>> Using constraints: ${constraints_file}"

# Download all wheels into the wheelhouse.
for r in "${reqs[@]}"; do
  echo ">>> Downloading wheels for ${r} into ${wheel_dir}"
  # Use pip download (uv lacks 'download' / 'wheel' subcommands).
  python -m pip download -r "${r}" -c "${constraints_file}" -d "${wheel_dir}"
done

echo ">>> Wheelhouse ready at: ${wheel_dir}"
echo ">>> Constraints saved to: ${constraints_file}"
