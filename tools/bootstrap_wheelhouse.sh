#!/usr/bin/env bash
set -euo pipefail

# Opinionated wrapper around make_wheelhouse.sh for common repo layouts.
# Detects typical files, builds a wheelhouse, and shows "next step" commands.
#
# Detect requirements candidates:
candidates=()
[[ -f "requirements.txt" ]] && candidates+=("requirements.txt")
[[ -f "requirements-dev.txt" ]] && candidates+=("requirements-dev.txt")
[[ -f "dev-requirements.txt" ]] && candidates+=("dev-requirements.txt")

if [[ ${#candidates[@]} -eq 0 ]]; then
  echo "No requirements*.txt files found. Supply explicit -r files to make_wheelhouse.sh." >&2
  exit 2
fi

args=()
for r in "${candidates[@]}"; do
  args+=("-r" "$r")
done

tools/make_wheelhouse.sh "${args[@]}"

echo
echo "=== Offline install examples ==="
echo "python -m pip install --no-index --find-links ./wheelhouse -r requirements.txt"
if [[ -f "requirements-dev.txt" ]]; then
  echo "python -m pip install --no-index --find-links ./wheelhouse -r requirements-dev.txt"
fi
echo
echo "Wheelhouse built. See ./wheelhouse and ./constraints.txt"
