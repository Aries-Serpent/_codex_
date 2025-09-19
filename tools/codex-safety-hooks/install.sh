#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOK_DIR="$ROOT/.git/hooks"
SRC_DIR="$ROOT/tools/codex-safety-hooks"

mkdir -p "$HOOK_DIR"

install_hook() {
  local name="$1"
  local target="$HOOK_DIR/$name"
  if [ -f "$target" ] && [ ! -f "$target.backup" ]; then
    mv "$target" "$target.backup"
  fi
  cp "$SRC_DIR/$name" "$target"
  chmod +x "$target"
  echo "Installed $name hook."
}

install_hook "pre-commit"
install_hook "pre-push"

echo "Codex Safety Hooks installed."
