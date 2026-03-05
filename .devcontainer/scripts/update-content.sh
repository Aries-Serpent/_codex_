#!/usr/bin/env bash
# .devcontainer/scripts/update-content.sh
# ─────────────────────────────────────────────────────────────────────────────
# Phase 3+4 equivalent of copilot-setup-steps.yml
# Runs on every Codespace rebuild AND on branch switch (content update).
# This is the right place for anything that depends on the checked-out code.
#
# Mirrors:
#   - Phase 3: Python venv + pip install (Standard profile)
#   - Phase 4: Node / Rust / optional ML deps
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

WORKSPACE="${CODESPACE_VSCODE_FOLDER:-/workspaces/_codex_}"
cd "$WORKSPACE"

echo "══════════════════════════════════════════════════════════"
echo "  Codex Codespace — update-content (Phase 3+4)"
echo "══════════════════════════════════════════════════════════"

# ── Python — upgrade pip, install project + dev dependencies ─────────────────
echo "🐍 Installing Python dependencies…"
python -m pip install --upgrade pip --quiet

# Core project + all dev extras (matches copilot-setup-steps.yml standard profile)
pip install --cache-dir "$HOME/.cache/pip" \
    pytest==8.4.2 \
    pytest-timeout==2.4.0 \
    pytest-xdist==3.8.0 \
    pytest-cov==5.0.0 \
    pytest-asyncio==1.3.0 \
    pytest-mock==3.15.1 \
    pytest-randomly \
    pytest-rerunfailures \
    --quiet

pip install --cache-dir "$HOME/.cache/pip" -e ".[dev]" --quiet 2>/dev/null || \
pip install --cache-dir "$HOME/.cache/pip" -e "." --quiet

# Code quality tools (same as copilot-setup-steps.yml)
pip install --cache-dir "$HOME/.cache/pip" \
    ruff \
    black \
    mypy \
    pre-commit \
    detect-secrets \
    --quiet

# Cognitive Brain server deps (always needed for CLI API server)
pip install --cache-dir "$HOME/.cache/pip" \
    "fastapi>=0.110.0,<1.0" \
    "uvicorn[standard]>=0.29.0,<1.0" \
    "httpx>=0.27.0,<1.0" \
    "cryptography>=42.0.0,<47.0.0" \
    --quiet

echo "  Python packages installed:"
pip list --format=columns 2>/dev/null | grep -E "^(pytest|ruff|black|mypy|fastapi|uvicorn|httpx|cryptography|codex)" || true

# ── Node.js ───────────────────────────────────────────────────────────────────
if command -v npm &>/dev/null && [ -f package.json ]; then
    echo "📦 Installing Node.js dependencies…"
    npm ci --prefer-offline --no-audit --quiet || npm install --no-audit --quiet
    echo "✅ Node.js deps installed"
fi

# ── Rust ─────────────────────────────────────────────────────────────────────
if command -v cargo &>/dev/null && [ -f Cargo.toml ]; then
    echo "🦀 Building Rust components…"
    cargo build --release --quiet
    echo "✅ Rust build complete"
fi

# ── pre-commit hooks ─────────────────────────────────────────────────────────
if [ -f .pre-commit-config.yaml ] && command -v pre-commit &>/dev/null; then
    echo "🔗 Installing pre-commit hooks…"
    pre-commit install --install-hooks --quiet || true
    echo "✅ pre-commit hooks installed"
fi

echo "✅ update-content complete"
