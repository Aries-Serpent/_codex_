#!/usr/bin/env bash
set -euo pipefail
ts="$(date +%Y%m%d-%H%M%S)"

# cd repo root
if [ ! -d .git ]; then
  root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "${root:-}" ] && cd "$root" || { echo "Run from a git repo"; exit 2; }
fi

dest="archive/removed"
mkdir -p "$dest"

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <path1> [path2 ...]" >&2
  exit 2
fi

for p in "$@"; do
  if [ ! -e "$p" ]; then
    echo "Skipping (not found): $p" >&2
    continue
  fi
  echo "→ Archiving (move) $p  ->  $dest/"
  if git ls-files --error-unmatch "$p" >/dev/null 2>&1; then
    mkdir -p "$dest"
    git mv "$p" "$dest/"
  else
    mv "$p" "$dest/"
  fi

done


echo "✅ Archived to $dest. Review 'git status' and commit."
