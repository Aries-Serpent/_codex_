#!/usr/bin/env bash
set -euo pipefail

export NO_NETWORK=${NO_NETWORK:-1}
export PYTHONHASHSEED=${PYTHONHASHSEED:-0}
ERRLOG=".codex/errors.ndjson"; mkdir -p .codex

ts() { date -u +"%Y-%m-%dT%H:%MZ"; }
err_block() {
  printf '{"ts":"%s","step":"%s:%s","error":"%s","context":"%s"}\n' "$(ts)" "$1" "$2" "$3" "$4" >> "$ERRLOG"
  cat <<EOF

Question for ChatGPT-5 $(ts):
While performing [$1:$2], encountered the following error:
$3
Context: $4
What are the possible causes, and how can this be resolved while preserving intended functionality?
EOF
}

python -m venv .venv || true
source .venv/bin/activate || true
python -m pip install --upgrade pip >/dev/null
pip install -U pre-commit pytest pytest-cov >/dev/null || true
export PYTHONPATH=.

if command -v chatgpt-codex >/dev/null 2>&1; then
  if ! chatgpt-codex --prompt-file AUDIT_PROMPT.md; then
    err_block "1" "run chatgpt-codex" "CLI returned non-zero" "generating audit file"
  fi
else
  err_block "1" "run chatgpt-codex" "bash: command not found: chatgpt-codex" "generating audit file"
  if ! python tools/audit_builder.py --prompt-file AUDIT_PROMPT.md; then
    err_block "1" "audit_builder fallback" "audit_builder failed" "fallback audit run"
  fi
fi

set +e
pre-commit run --all-files --verbose
rc=$?
if [ $rc -ne 0 ]; then
  pre-commit clean
  pre-commit run --all-files --verbose
  rc=$?
fi
set -e
if [ $rc -ne 0 ]; then
  err_block "2" "pre-commit run --all-files" "command hung or failed" "executing repository hooks"
fi

if ! pytest --version 2>/dev/null | grep -qi "pytest-cov"; then
  err_block "3" "pytest coverage flags" "pytest: plugin 'pytest-cov' not active" "running unit tests with coverage"
  pip install pytest-cov >/dev/null
fi
set +e
pytest --cov=src/codex_ml --cov-report=term --cov-fail-under=70
rc=$?
set -e
if [ $rc -ne 0 ]; then
  err_block "3" "pytest" "pytest failed with coverage flags" "unit tests and coverage"
  pytest -q --maxfail=1 --disable-warnings || true
fi

echo "Run complete. Errors (if any) recorded in $ERRLOG"
