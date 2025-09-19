#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOK_DIR="$ROOT/.git/hooks"
SRC_DIR="$ROOT/tools/codex-safety-hooks"

mkdir -p "$HOOK_DIR"

install_hook() {
  local name="$1"
  if [ -f "$HOOK_DIR/$name" ] && [ ! -f "$HOOK_DIR/$name.backup" ]; then
    mv "$HOOK_DIR/$name" "$HOOK_DIR/$name.backup"
  fi
  cp "$SRC_DIR/$name" "$HOOK_DIR/$name"
  chmod +x "$HOOK_DIR/$name"
  echo "Installed $name hook."
}

install_hook "pre-commit"
install_hook "pre-push"

echo "Codex Safety Hooks installed."
