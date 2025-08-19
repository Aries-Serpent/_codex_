#!/usr/bin/env bash
# Shell session hooks that log start/end events via Python.
# Captures exit codes from Python logging calls and reports failures.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure log dir env var is exported so Python can read it
: "${CODEX_SESSION_LOG_DIR:=.codex/sessions}"
export CODEX_SESSION_LOG_DIR
CODEX_SESSION_LOG_DIR="$(python3 - <<'PY'
import os, pathlib
print(pathlib.Path(os.environ['CODEX_SESSION_LOG_DIR']).expanduser().resolve())
PY
)"
py_status=$?
if [[ $py_status -ne 0 ]]; then
  echo "codex session hooks: failed to resolve log dir (exit $py_status)" >&2
fi
mkdir -p "$CODEX_SESSION_LOG_DIR"

codex__uuid() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]'
  else
    printf "sess-%s-%s" "$(date +%s)" "$RANDOM"
  fi
}

codex_session_start() {
  : "${CODEX_SESSION_ID:=$(codex__uuid)}"
  export CODEX_SESSION_ID
  export CODEX_SESSION_START_EPOCH="$(date -u +%s)"
  python3 - "$CODEX_SESSION_LOG_DIR" "$CODEX_SESSION_ID" "$PWD" "$@" <<'PY'
import json, os, pathlib, sys
from datetime import datetime, timezone
log_dir = pathlib.Path(sys.argv[1])
sid = sys.argv[2]
cwd = sys.argv[3]
argv = list(sys.argv[4:])
ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
log_dir.mkdir(parents=True, exist_ok=True)
meta = log_dir / f"{sid}.meta"
meta.write_text(f"{ts} session_start {sid}\n", encoding="utf-8")
ndjson = log_dir / f"{sid}.ndjson"
line = json.dumps({"ts": ts, "type": "session_start", "session_id": sid, "cwd": cwd, "argv": argv})
with ndjson.open("a", encoding="utf-8") as f:
    f.write(line + "\n")
PY
  status=$?
  if [[ $status -ne 0 ]]; then
    echo "codex_session_start: logging failed with exit code $status" >&2
  fi
}

codex_session_end() {
  local exit_code="${1:-0}"
  : "${CODEX_SESSION_ID:?missing session id}"
  local now_epoch="$(date -u +%s)"
  local start_epoch="${CODEX_SESSION_START_EPOCH:-$now_epoch}"
  local duration="$(( now_epoch - start_epoch ))"
  python3 - "$CODEX_SESSION_LOG_DIR" "$CODEX_SESSION_ID" "$exit_code" "$duration" <<'PY'
import json, pathlib, sys
from datetime import datetime, timezone
log_dir = pathlib.Path(sys.argv[1])
sid = sys.argv[2]
exit_code = int(sys.argv[3])
duration = int(sys.argv[4])
ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
ndjson = log_dir / f"{sid}.ndjson"
ndjson.parent.mkdir(parents=True, exist_ok=True)
line = json.dumps({"ts": ts, "type": "session_end", "session_id": sid, "exit_code": exit_code, "duration_s": duration})
with ndjson.open("a", encoding="utf-8") as f:
    f.write(line + "\n")
PY
  status=$?
  if [[ $status -ne 0 ]]; then
    echo "codex_session_end: logging failed with exit code $status" >&2
  fi
}
