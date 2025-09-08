#!/usr/bin/env bash
set -uo pipefail
# Deterministic bootstrap for local gates (pre-commit + pytest).
# Creates .venv if missing, upgrades pip, installs repo + dev deps,
# and ensures CLIs invoked by hooks are present.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$HERE"
VENV="${VENV:-.venv}"
PY="${PYTHON:-python3}"
ERRLOG=".codex/errors.ndjson"; mkdir -p .codex

log_error() {
  local step="$1" desc="$2" msg="$3"
  local ts
  ts=$(date --iso-8601=seconds)
  local block="Question for ChatGPT @codex $ts:\nWhile performing [$step:$desc], encountered the following error:\n$msg\nContext: bootstrapping development environment\nWhat are the possible causes, and how can this be resolved while preserving intended functionality?"
  BLOCK="$block" python3 - "$ERRLOG" <<'PY'
import json, os, sys
path = sys.argv[1]
block = os.environ["BLOCK"]
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "a", encoding="utf-8") as fh:
    json.dump({"question": block}, fh)
    fh.write("\n")
PY
}

run_step() {
  local step="$1" desc="$2"; shift 2
  local output
  output=$("$@" 2>&1)
  local status=$?
  if [ $status -ne 0 ]; then
    log_error "$step" "$desc" "$output"
    printf '%s\n' "$output" >&2
    exit $status
  fi
}

run_step 1 "create virtualenv if missing" bash -c "[[ -d \"$VENV\" ]] || $PY -m venv \"$VENV\""
run_step 2 "activate virtualenv" source "$VENV/bin/activate"
run_step 3 "upgrade pip tooling" python -m pip install --upgrade pip setuptools wheel
if command -v uv >/dev/null 2>&1; then
  run_step 4 "install requirements via uv" uv pip install --locked -r requirements.txt -r requirements-dev.txt
else
  run_step 4 "install requirements via pip" pip install -r requirements.lock
fi
run_step 5 "install gate CLIs" pip install pre-commit yamllint shellcheck-py semgrep pip-audit
run_step 6 "install pre-commit hooks" pre-commit install --install-hooks --overwrite

echo "[bootstrap] Ready. Run: pre-commit run --all-files && pytest"
