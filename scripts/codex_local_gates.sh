#!/usr/bin/env bash
set -euo pipefail
echo "[Codex] Running local offline gates..."
precommit_available=0
precommit_rc=127
precommit_output="pre-commit not found"
if command -v pre-commit >/dev/null 2>&1; then
  if precommit_output=$(pre-commit --version 2>&1); then
    precommit_available=1
    precommit_rc=0
  else
    precommit_rc=$?
  fi
else
  precommit_output="pre-commit not found on PATH"
fi
PRECOMMIT_AVAILABLE="$precommit_available" \
PRECOMMIT_OUTPUT="$precommit_output" \
PRECOMMIT_RC="$precommit_rc" \
python - <<'PY'
import os
import sys

try:
    from codex.logging.session_logger import get_session_id, log_message
except Exception:
    get_session_id = None  # type: ignore[assignment]
    log_message = None  # type: ignore[assignment]

available = os.environ.get("PRECOMMIT_AVAILABLE") == "1"
output = os.environ.get("PRECOMMIT_OUTPUT", "")
return_code = os.environ.get("PRECOMMIT_RC")
if return_code and return_code.lstrip("-").isdigit():
    parsed_rc = int(return_code)
else:
    parsed_rc = return_code
meta = {
    "tool": "pre-commit",
    "command": "pre-commit --version",
    "available": available,
    "stdout": output.strip(),
    "returncode": parsed_rc,
    "source": "scripts/codex_local_gates.sh",
}
if log_message is not None and get_session_id is not None:
    role = "system" if available else "WARN"
    try:
        log_message(get_session_id(), role, "pre-commit availability check", meta=meta)
    except Exception:
        pass
print(output.strip())
sys.stdout.flush()
PY
if [[ "$precommit_available" == "1" ]]; then
  pre-commit run --all-files
fi
if command -v pytest >/dev/null 2>&1; then
  pytest -q
  pytest --cov=src/codex_ml --cov-fail-under=70
fi
echo "[Codex] Gates complete (offline)."
