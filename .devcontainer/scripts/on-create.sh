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

# Resolve sudo — in GitHub Codespaces prebuilds the container user may already
# be root (no sudo binary).  Define a safe wrapper once.
if command -v sudo &>/dev/null; then
  SUDO="sudo"
else
  SUDO=""
fi

echo "══════════════════════════════════════════════════════════"
echo "  Codex Codespace — on-create (Phase 1+2)"
echo "  Workspace : $WORKSPACE"
echo "  User      : $(whoami)"
echo "  Python    : $(python --version 2>&1)"
echo "══════════════════════════════════════════════════════════"

# ── APT state repair + update with retry ─────────────────────────────────────
# During Codespaces prebuilds the APT lists directory can be missing or have the
# wrong permissions, causing apt-get update to fail with:
#   E: List directory /var/lib/apt/lists/partial is missing. - Acquire (13: Permission denied)
#   onCreateCommand … failed with exit code 100  → prebuild error 1309
#
# Behaviour is controlled by repository variables (documented in
# .codex/CRITICAL_REPOSITORY_VARIABLES.md § "Codespaces Container Setup"):
#   CODESPACES_APT_UPDATE_RETRY       (default: true)  — retry update on failure
#   CODESPACES_APT_CLEANUP_AGGRESSIVE (default: true)  — purge lists after install
APT_UPDATE_RETRY="${CODESPACES_APT_UPDATE_RETRY:-true}"
APT_CLEANUP_AGGRESSIVE="${CODESPACES_APT_CLEANUP_AGGRESSIVE:-true}"

# Idempotent — safe to run multiple times.  Recreates the APT lists directory
# tree with correct permissions and clears any stale cache/locks.  Works in both
# root and non-root containers via the $SUDO wrapper resolved above.
apt_repair_state() {
  $SUDO rm -rf /var/lib/apt/lists/partial
  $SUDO mkdir -p /var/lib/apt/lists/partial
  $SUDO chmod 0755 /var/lib/apt/lists /var/lib/apt/lists/partial
  $SUDO apt-get clean
}

# Run apt-get update, repairing state and retrying once when retry is enabled.
# Logs every attempt and fails explicitly (no silent masking) so genuine
# failures (e.g. network down) surface instead of corrupting later steps.
apt_update_with_retry() {
  local attempt=1 max_attempts
  if [ "$APT_UPDATE_RETRY" = "true" ]; then
    max_attempts=2
  else
    max_attempts=1
  fi
  while [ "$attempt" -le "$max_attempts" ]; do
    echo "🔄 apt-get update (attempt ${attempt}/${max_attempts})…"
    if $SUDO apt-get update -qq; then
      return 0
    fi
    echo "⚠️  apt-get update failed on attempt ${attempt}." >&2
    if [ "$attempt" -lt "$max_attempts" ]; then
      echo "🛠️  Repairing APT state before retry…"
      apt_repair_state
    fi
    attempt=$((attempt + 1))
  done
  echo "❌ apt-get update failed after ${max_attempts} attempt(s)." >&2
  return 1
}

# ── System packages (mirrors Phase 2: System Dependencies) ───────────────────
echo "📦 Installing system packages…"
apt_repair_state
apt_update_with_retry

if $SUDO apt-get install -y --no-install-recommends \
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
    sqlite3; then
  echo "✅ System packages installed"
  # Cleanup ONLY after a successful install so a failed run leaves APT state
  # intact for inspection / retry.
  if [ "$APT_CLEANUP_AGGRESSIVE" = "true" ]; then
    $SUDO rm -rf /var/lib/apt/lists/*
  fi
else
  echo "⚠️  Some system packages failed to install (non-fatal); leaving APT lists intact." >&2
fi

# ── Git LFS (mirrors GIT_LFS_SKIP_SMUDGE baseline — pull only text files) ────
git lfs install --skip-smudge 2>/dev/null || true
echo "✅ Git LFS configured (smudge skip — fetch blobs on demand)"

# ── Runtime directories ───────────────────────────────────────────────────────
mkdir -p \
    "$WORKSPACE/.codex/sessions" \
    "$WORKSPACE/artifacts" \
    "$HOME/.codex"

echo "✅ on-create complete"
