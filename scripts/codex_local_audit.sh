#!/usr/bin/env bash
set -euo pipefail

# Codex-local offline audit runner
# - Creates a local venv (if missing)
# - Runs pre-commit (if configured)
# - Executes the audit CLI
# - Captures deterministic artifacts under ./reports
#
# Determinism & offline guards
export PYTHONHASHSEED="${PYTHONHASHSEED:-0}"
export CODEX_OFFLINE=1
export CODEX_NO_NETWORK=1
export NO_NETWORK=1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p reports .codex

# Optional: create venv if not already active
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# Install runtime + dev deps if manifests exist (best-effort, offline where possible)
if [[ -f "requirements.txt" ]]; then
  pip install -r requirements.txt || true
fi
if [[ -f "requirements-dev.txt" ]]; then
  pip install -r requirements-dev.txt || true
fi
if [[ -f "pyproject.toml" || -f "setup.cfg" || -f "setup.py" ]]; then
  pip install -e . || true
fi

# Run pre-commit locally if configured (non-fatal)
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install || true
  pre-commit run --all-files || true
fi

# Fence validator (optional)
if [[ -f "tools/validate_fences.py" ]]; then
  python3 tools/validate_fences.py --strict-inner || true
fi

# Save a copy of the prompt used
if [[ -f "AUDIT_PROMPT.md" ]]; then
  cp AUDIT_PROMPT.md reports/prompt_copy.md
fi

# Execute the audit CLI
set +e
scripts/codex-audit --root . --out reports/audit.json
EXIT_CODE=$?
set -e

if [[ $EXIT_CODE -ne 0 ]]; then
  {
    TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '{"ts":"%s","step":"codex-audit","level":"error","exit_code":%d}\n' "$TS" "$EXIT_CODE"
  } >> .codex/errors.ndjson
  echo "codex-audit failed with exit code $EXIT_CODE (see .codex/errors.ndjson)" >&2
  exit $EXIT_CODE
fi

echo "Audit complete. Artifacts in ./reports"
