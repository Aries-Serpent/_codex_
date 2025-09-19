#!/usr/bin/env bash
set -euo pipefail

# === Guardrails ===
export NO_NETWORK=${NO_NETWORK:-1}            # keep runs offline
export PYTHONHASHSEED=${PYTHONHASHSEED:-0}    # reproducibility
ERRLOG=".codex/errors.ndjson"; mkdir -p .codex

ts() { date -u +"%Y-%m-%dT%H:%MZ"; }
err_block() {
  # $1 step_no, $2 desc, $3 msg, $4 ctx
  cat >> "$ERRLOG" <<EOF
{"ts":"$(ts)","step":"$1:$2","error":"$3","context":"$4"}
EOF
  cat <<EOF

Question for ChatGPT-5 $(ts):
While performing [$1:$2], encountered the following error:
$3
Context: $4
What are the possible causes, and how can this be resolved while preserving intended functionality?
EOF
}

echo "== PREP =="
python -m venv .venv || true
# shellcheck disable=SC1091
source .venv/bin/activate || true
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt -r requirements-dev.txt >/dev/null || true

echo "== STEP 1: AUDIT GENERATION =="
if command -v chatgpt-codex >/dev/null 2>&1; then
  if ! chatgpt-codex --prompt-file AUDIT_PROMPT.md; then
    err_block "1" "run chatgpt-codex" "CLI returned non-zero" "generating audit file"
  fi
else
  err_block "1" "run chatgpt-codex" "bash: command not found: chatgpt-codex" "generating audit file"
  # Fallback to internal entrypoint
  if ! python tools/audit_builder.py --prompt-file AUDIT_PROMPT.md; then
    err_block "1" "audit_builder fallback" "audit_builder failed" "fallback audit run"
  fi
fi

echo "== STEP 2: PRE-COMMIT GATE =="
# Diagnose in verbose mode; if it appears to hang, clean envs and retry once.
set +e
pre-commit run --all-files --verbose
rc=$?
if [ $rc -ne 0 ]; then
  # Clean hook envs and retry; if a hook name is known to stall, you can SKIP it:
  pre-commit clean
  pre-commit run --all-files --verbose
  rc=$?
fi
set -e
if [ $rc -ne 0 ]; then
  err_block "2" "pre-commit run --all-files" "command hung or failed" "executing repository hooks"
fi

echo "== STEP 3: TESTS + COVERAGE =="
if ! pytest --version 2>/dev/null | grep -qi "pytest-cov"; then
  err_block "3" "pytest coverage flags" "pytest: plugin 'pytest-cov' not active" "running unit tests with coverage"
  pip install pytest-cov==7.0.0 >/dev/null
fi

set +e
pytest --cov=src/codex_ml --cov-report=term --cov-fail-under=70
rc=$?
set -e
if [ $rc -ne 0 ]; then
  err_block "3" "pytest" "pytest failed with coverage flags" "unit tests and coverage"
  # Fallback: run minimal tests to unblock, then raise an issue
  pytest -q --maxfail=1 --disable-warnings || true
fi

echo "== FINALIZATION =="
# No GitHub Actions; all checks are local/offline by design.
echo "Run complete. Errors (if any) recorded in $ERRLOG"

