#!/usr/bin/env bash
set -euo pipefail
OUT=/home/runner/work/_codex_/_codex_/.codex/evidence/institutional-foundation/iteration-006/runtime
ROOT=/home/runner/work/_codex_/_codex_
WHEELS="$ROOT/.codex/evidence/institutional-foundation/iteration-005/package-final/artifacts"
mkdir -p "$OUT/cache" "$OUT/work"
export TMPDIR="$OUT/cache" PIP_CACHE_DIR="$OUT/cache/pip"
unset PYTHONPATH
exec > >(tee "$OUT/meta-execution.log") 2>&1
set -x
"$ROOT/.venv_ci/bin/python" -m venv --without-pip "$OUT/cache/venv"
"$ROOT/.venv_ci/bin/python" -m pip --python "$OUT/cache/venv/bin/python" install --no-deps \
  --report "$OUT/meta-install-report.json" \
  "$WHEELS/codex_ml-0.3.0-py3-none-any.whl" \
  "$WHEELS/codex_contracts-0.1.0a1-py3-none-any.whl" \
  jsonschema==4.25.1 jsonschema-specifications==2025.9.1 referencing==0.37.0 \
  rpds-py==2026.9.1 attrs==26.1.0 typing-extensions==4.16.0
cd "$OUT/work"
"$OUT/cache/venv/bin/python" -I -B "$OUT/meta_workflow.py"
