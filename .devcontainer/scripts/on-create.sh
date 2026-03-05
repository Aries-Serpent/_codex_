#!/usr/bin/env bash
# .devcontainer/scripts/on-create.sh
# ─────────────────────────────────────────────────────────────────────────────
# Phase 1+2 equivalent of copilot-setup-steps.yml
# Runs ONCE when the Codespace container is first created.
# Does NOT re-run on rebuild unless the devcontainer definition changes.
#
# Mirrors:
#   - Phase 1: Repository & Code Setup
#   - Phase 2: System Dependencies
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

WORKSPACE="${CODESPACE_VSCODE_FOLDER:-/workspaces/_codex_}"
cd "$WORKSPACE"

echo "══════════════════════════════════════════════════════════"
echo "  Codex Codespace — on-create (Phase 1+2)"
echo "  Workspace : $WORKSPACE"
echo "  User      : $(whoami)"
echo "  Python    : $(python --version 2>&1)"
echo "══════════════════════════════════════════════════════════"

# ── System packages (mirrors Phase 2: System Dependencies) ───────────────────
echo "📦 Installing system packages…"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    git-lfs \
    jq \
    make \
    tree \
    unzip \
    sqlite3 \
    2>/dev/null || true
sudo rm -rf /var/lib/apt/lists/*

# ── Git LFS (mirrors GIT_LFS_SKIP_SMUDGE baseline — pull only text files) ────
git lfs install --skip-smudge 2>/dev/null || true
echo "✅ Git LFS configured (smudge skip — fetch blobs on demand)"

# ── Runtime directories ───────────────────────────────────────────────────────
mkdir -p \
    "$WORKSPACE/.codex/sessions" \
    "$WORKSPACE/artifacts" \
    "$HOME/.codex"

echo "✅ on-create complete"
