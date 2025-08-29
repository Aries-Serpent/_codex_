#!/usr/bin/env bash
set -euo pipefail

# Local-only runner for Codex Orchestrator. No GitHub Actions are created/enabled.

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PY="${PYTHON:-python3}"
export PYTHONHASHSEED=${PYTHONHASHSEED:-0}

# Optional: encourage pre-commit caches to keep runs snappy (see upstream docs).
# First run can be slow while hook environments are installed.

echo "[codex] Orchestrating in: $ROOT"
cd "$ROOT"

# Ensure .codex exists early so logs can be written even if later steps fail.
mkdir -p .codex

# (Optional) install the commit-msg trailer hook
if [ "${CODEX_INSTALL_HOOK:-1}" = "1" ]; then
  if [ -f "tools/install_codex_hooks.py" ]; then
    "$PY" tools/install_codex_hooks.py || true
  fi
fi

# Main run (no Actions; all local artifacts)
RUN_ARGS=()
[ "${CODEX_RUN_PRECOMMIT:-0}" = "1" ] && RUN_ARGS+=( --run-precommit )
[ "${CODEX_RUN_PYTEST:-0}" = "1" ] && RUN_ARGS+=( --run-pytest )
[ -n "${CODEX_COV_PKG:-}" ] && RUN_ARGS+=( --cov-pkg "$CODEX_COV_PKG" )
[ -n "${CODEX_COV_THRESHOLD:-}" ] && RUN_ARGS+=( --cov-threshold "$CODEX_COV_THRESHOLD" )

"$PY" tools/codex_exec.py --project-root "$ROOT" "${RUN_ARGS[@]}"

echo "[codex] Complete. Artifacts:"
echo "  - Codex_Questions.md"
echo "  - codex_commit_comment.txt"
echo "  - .codex/errors.ndjson"
echo "  - .codex/findings.json"
echo "  - codex_suggested_patches.diff"
echo "  - CHANGELOG_Codex.md"
