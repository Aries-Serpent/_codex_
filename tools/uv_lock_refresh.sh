#!/usr/bin/env bash
set -euo pipefail
echo "[uv] refreshing lock + requirements snapshots"
if [[ -f "pyproject.toml" ]]; then
  uv lock ${UV_OFFLINE:+--offline}
fi
if [[ -f "requirements.in" ]]; then
  uv pip compile requirements.in -o requirements.txt
fi
if [[ -f "requirements-dev.in" ]]; then
  uv pip compile requirements-dev.in -o requirements-dev.txt
fi
echo "Done. Next: run 'make lock-refresh && pre-commit run -a' (in Codex env)."
