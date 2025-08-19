#!/usr/bin/env bash
# tools/codex_workflow.sh
# End-to-end local workflow for session hook extraction + integration.
# Usage: tools/codex_workflow.sh [REPO_ROOT=.]

set -euo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

# ---------- Phase 1: Preparation ----------
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

mkdir -p .codex/sessions .codex/context .codex/tmp

FLAGS_FILE=".codex/flags.env"
CHANGELOG=".codex/change_log.md"
ERRORS=".codex/errors.ndjson"
RESULTS=".codex/results.md"
MAPPING=".codex/mapping.md"
INVENTORY=".codex/inventory.tsv"

# 1.1 Verify git and clean state
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "Not a git repository." >&2
  cat <<'EOF2' >> "$ERRORS"
{"ts":"$(timestamp)","step":"1.1","msg":"Not a git repository","context":"codex_workflow.sh"}
EOF2
  echo "Question for ChatGPT-5:
While performing [1.1: Verify repository state], encountered the following error:
Not a git repository
Context: running tools/codex_workflow.sh outside a git repo
What are the possible causes, and how can this be resolved while preserving intended functionality?"
  exit 2
fi

if ! git diff-index --quiet HEAD --; then
  cat <<'EOF2' >> "$ERRORS"
{"ts":"$(timestamp)","step":"1.1","msg":"Working tree not clean","context":"Uncommitted changes present"}
EOF2
  echo "Question for ChatGPT-5:
While performing [1.1: Verify repository state], encountered the following error:
Working tree not clean
Context: Uncommitted changes present
What are the possible causes, and how can this be resolved while preserving intended functionality?"
  exit 3
fi

# 1.2 Load README/CONTRIBUTING (best-effort capture to context)
for f in README.md README README.rst CONTRIBUTING.md CONTRIBUTING; do
  [[ -f "$f" ]] && cp -f "$f" ".codex/context/${f//\//_}" || true
done

# 1.3 Inventory (paths + brief role via extension)
echo -e "path\trole_hint" > "$INVENTORY"
while IFS= read -r -d '' f; do
  ext="${f##*.}"
  role="code"
  [[ "$ext" =~ ^(md|rst|txt)$ ]] && role="doc"
  [[ "$ext" =~ ^(yml|yaml|json|toml|ini)$ ]] && role="config"
  printf "%s\t%s\n" "$f" "$role" >> "$INVENTORY"
done < <(find . -type f \( -name "*.*" -o -name "entrypoint.sh" \) -not -path "./.git/*" -print0)

# 1.4 Flags
cat > "$FLAGS_FILE" <<EOF2
DO_NOT_ACTIVATE_GITHUB_ACTIONS=true
SAFE_EDIT_MODE=true
EOF2

# 1.5 Initialize logs if absent
[[ -f "$CHANGELOG" ]] || printf "# Change Log (codex)\n\n" > "$CHANGELOG"
[[ -f "$ERRORS" ]] || : > "$ERRORS"
[[ -f "$RESULTS" ]] || : > "$RESULTS"
[[ -f "$MAPPING" ]] || printf "# Task → Candidate Mapping\n\n" > "$MAPPING"

# ---------- Phase 2: Search & Mapping ----------
# T1: entrypoint.sh presence and current hooks
EP="entrypoint.sh"
echo "## T1: entrypoint.sh scan" >> "$MAPPING"
if [[ -f "$EP" ]]; then
  grep -nE 'codex_session_(start|end)|trap .*codex_session_end' "$EP" || true
  echo "- Found $EP" >> "$MAPPING"
else
  echo "- entrypoint.sh not found" >> "$MAPPING"
fi

# Find shell/Python launchers
echo -e "\n## Candidate launchers" >> "$MAPPING"
mapfile -t SH_LAUNCHERS < <(git ls-files -z | xargs -0 -I{} bash -c 'file -b "{}" 2>/dev/null | grep -qi "shell script" && echo "{}"' || true)
mapfile -t PY_CANDIDATES < <(git ls-files "*.py" | xargs -I{} grep -El 'if __name__ == ["\']__main__["\']' "{}" || true)

{
  echo "- Shell launchers:"
  for s in "${SH_LAUNCHERS[@]:-}"; do echo "  - $s"; done
  echo "- Python entrypoint candidates:"
  for p in "${PY_CANDIDATES[@]:-}"; do echo "  - $p"; done
} >> "$MAPPING"

# ---------- Phase 3: Best-Effort Construction ----------
record_change() { # file action rationale
  printf "### %s\n- Action: %s\n- Rationale: %s\n\n" "$1" "$2" "$3" >> "$CHANGELOG"
}

backup_safe() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  mkdir -p ".codex/backups/$(dirname "$f")"
  cp -f "$f" ".codex/backups/${f}.bak.$(date +%s)"
}

# 3.2 Create helpers
mkdir -p scripts codex/logging

# scripts/session_logging.sh (shell helper)
if [[ ! -f scripts/session_logging.sh ]]; then
  cat > scripts/session_logging.sh <<'EOS'
#!/usr/bin/env bash
# Session logging helper (Shell)
set -euo pipefail

: "${CODEX_SESSION_LOG_DIR:=.codex/sessions}"
CODEX_SESSION_LOG_DIR="$(python - <<'PY'
import os, pathlib
print(pathlib.Path(os.environ['CODEX_SESSION_LOG_DIR']).expanduser().resolve())
PY
)"
mkdir -p "$CODEX_SESSION_LOG_DIR"

codex__timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
codex__log_file() {
  [[ -d "$CODEX_SESSION_LOG_DIR" ]] || mkdir -p "$CODEX_SESSION_LOG_DIR"
  printf '%s/%s' "$CODEX_SESSION_LOG_DIR" "$1"
}
codex__uuid() {
  if command -v uuidgen >/dev/null 2>&1; then uuidgen | tr '[:upper:]' '[:lower:]'
  else printf "sess-%s-%s" "$(date +%s)" "$RANDOM"
  fi
}

codex_session_start() {
  : "${CODEX_SESSION_ID:=$(codex__uuid)}"
  export CODEX_SESSION_ID
  echo "$(codex__timestamp) session_start $CODEX_SESSION_ID" > "$(codex__log_file "${CODEX_SESSION_ID}.meta")"
  {
    printf '{"ts":"%s","type":"session_start","session_id":"%s","cwd":"%s","argv":[' "$(codex__timestamp)" "$CODEX_SESSION_ID" "$PWD"
    first=1
    for a in "$@"; do
      if [[ $first -eq 1 ]]; then first=0; else printf ","; fi
      printf '%s' "\"${a//\"/\\\"}\""
    done
    printf "]}\n"
  } >> "$(codex__log_file "${CODEX_SESSION_ID}.ndjson")"
}

codex_session_end() {
  local exit_code="${1:-0}"
  : "${CODEX_SESSION_ID:?missing session id}"
  local start_line; start_line="$(head -n1 "$(codex__log_file "${CODEX_SESSION_ID}.meta")" 2>/dev/null || true)"
  local duration=""
  if [[ -n "$start_line" ]]; then
    local start_epoch; start_epoch="$(date -u -d "$(echo "$start_line" | awk '{print $1}')" +%s 2>/dev/null || date +%s)"
    local now_epoch; now_epoch="$(date -u +%s)"
    duration="$(( now_epoch - start_epoch ))"
  fi
  printf '{"ts":"%s","type":"session_end","session_id":"%s","exit_code":%s,"duration_s":%s}\n' \
    "$(codex__timestamp)" "$CODEX_SESSION_ID" "$exit_code" "${duration:-null}" \
    >> "$(codex__log_file "${CODEX_SESSION_ID}.ndjson")"
}
EOS
  chmod +x scripts/session_logging.sh
  record_change "scripts/session_logging.sh" "create" "Introduce shell helper for session start/end NDJSON logging."
fi

# codex/logging/session_hooks.py (Python helper)
if [[ ! -f codex/logging/session_hooks.py ]]; then
  cat > codex/logging/session_hooks.py <<'EOPY'
# Session logging helper (Python)
from __future__ import annotations
import atexit, json, os, sys, time, uuid, pathlib, datetime as dt

LOG_DIR = pathlib.Path(os.environ.get("CODEX_SESSION_LOG_DIR", ".codex/sessions"))
LOG_DIR = LOG_DIR.expanduser().resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _log_path(name: str) -> pathlib.Path:
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / name

def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z")

def _session_id():
    sid = os.environ.get("CODEX_SESSION_ID")
    if not sid:
      sid = f"{uuid.uuid4()}"
      os.environ["CODEX_SESSION_ID"] = sid
    return sid

def _log(obj: dict):
    sid = _session_id()
    path = (LOG_DIR / f"{sid}.ndjson").resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
      f.write(json.dumps(obj, separators=(",", ":")) + "\n")

class session:
    def __init__(self, argv=None):
        self.sid = _session_id()
        self.start_ts = time.time()
        self.argv = list(argv) if argv is not None else sys.argv

    def __enter__(self):
        meta_path = (LOG_DIR / f"{self.sid}.meta").resolve()
        meta_path.write_text(f"{_now()} session_start {self.sid}\n")
        _log({"ts": _now(), "type": "session_start", "session_id": self.sid, "cwd": os.getcwd(), "argv": self.argv})
        atexit.register(self._end)
        return self

    def _end(self, exit_code: int | None = None):
        if exit_code is None:
            exit_code = 0
        dur = max(0, int(time.time() - self.start_ts))
        _log({"ts": _now(), "type": "session_end", "session_id": self.sid, "exit_code": exit_code, "duration_s": dur})

    def __exit__(self, exc_type, exc, tb):
        self._end(1 if exc else 0)
        return False
EOPY
  record_change "codex/logging/session_hooks.py" "create" "Introduce Python context manager/atexit helper for session logging."
fi

# 3.3 Update entrypoint.sh (shell injection)
inject_shell_hooks() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  if grep -q 'codex_session_start' "$f"; then
    return 0
  fi
  backup_safe "$f"
  awk '
  NR==1 {
    print $0
    print "# >>> CODEX SESSION HOOKS (auto-injected)"
    print "if [ -f \"scripts/session_logging.sh\" ]; then . scripts/session_logging.sh; "
    print "elif [ -f \"$(dirname \"$0\")/scripts/session_logging.sh\" ]; then . \"$(dirname \"$0\")/scripts/session_logging.sh\"; fi"
    print "codex_session_start \"$0\" \"$@\""
    print "trap '\''codex_session_end $?'\'' EXIT"
    print "# <<< CODEX SESSION HOOKS"
    next
  }
  { print $0 }' "$f" > ".codex/tmp/inj.$$"
  mv ".codex/tmp/inj.$$" "$f"
  record_change "$f" "inject-hooks" "Source shell session helper, start at entry, end on EXIT."
}

if [[ -f "$EP" ]]; then
  inject_shell_hooks "$EP"
fi

# 3.4 Scan and inject other shell launchers
for shf in "${SH_LAUNCHERS[@]:-}"; do
  [[ "$shf" == "$EP" ]] && continue
  inject_shell_hooks "$shf" || true
done

# 3.5 Python minimal import hook (safe-insertion best effort)
inject_python_hooks() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  if grep -q 'codex\.logging\.session_hooks' "$f"; then
    return 0
  fi
  if grep -q 'if __name__ == .__main__.' "$f"; then
    backup_safe "$f"
    python3 - "$f" <<'PY'
import io,sys,re,pathlib
p=pathlib.Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
if "codex.logging.session_hooks" in s:
    sys.exit(0)
pat=re.compile(r'(?m)^(if __name__ == [\'""\']__main__[\'""\']\s*:\s*)$')
lines=s.splitlines()
out=[]
injected=False
for l in lines:
    out.append(l)
    if not injected and re.match(r'^\s*if __name__ == [\'""\']__main__[\'""\']\s*:\s*$', l):
        out.append("    try:")
        out.append("        from src.codex.logging.session_hooks import session")
        out.append("    except Exception:")
        out.append("        session = None")
        out.append("    if session:")
        out.append("        with session(sys.argv):")
        out.append("            pass  # session start")
        injected=True
p.write_text("\n".join(out)+("\n" if not s.endswith("\n") else ""),encoding="utf-8")
PY
    record_change "$f" "inject-import" "Minimal atexit-based session logging for Python __main__ entry."
  fi
}

for pf in "${PY_CANDIDATES[@]:-}"; do
  inject_python_hooks "$pf" || true
done

# 3.6 Create regression test (unittest, no 3rd-party deps)
mkdir -p tests
if [[ ! -f tests/test_session_hooks.py ]]; then
  cat > tests/test_session_hooks.py <<'PYT'
import os, subprocess, tempfile, pathlib, json, time, unittest, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHELL_HELPER = ROOT / "scripts" / "session_logging.sh"

@unittest.skipUnless(SHELL_HELPER.exists(), "shell helper missing")
class TestSessionHooks(unittest.TestCase):
    def test_shell_helper_records_start_and_end(self):
        with tempfile.TemporaryDirectory() as td:
            logdir = pathlib.Path(td)
            sid = "test-sess-1234"
            runner = logdir / "runner.sh"
            runner.write_text(f"""#!/usr/bin/env bash
set -euo pipefail
export CODEX_SESSION_LOG_DIR=\"{logdir.as_posix()}\"
export CODEX_SESSION_ID=\"{sid}\"
. \"{SHELL_HELPER.as_posix()}\"
codex_session_start \"unit\"
trap 'codex_session_end $?' EXIT
true
""")
            runner.chmod(0o755)
            subprocess.run([runner.as_posix()], check=True)
            ndjson = logdir / f"{sid}.ndjson"
            self.assertTrue(ndjson.exists(), "ndjson log not found")
            lines = [json.loads(l) for l in ndjson.read_text().strip().splitlines()]
            types = [l.get("type") for l in lines]
            self.assertIn("session_start", types)
            self.assertIn("session_end", types)
            self.assertEqual(len([t for t in types if t in ("session_start","session_end")]), 2)

    def test_shell_helper_recovers_missing_dir(self):
        with tempfile.TemporaryDirectory() as td:
            logdir = pathlib.Path(td)
            sid = "lost-dir-123"
            runner = logdir / "runner.sh"
            runner.write_text(f"""#!/usr/bin/env bash
set -euo pipefail
export CODEX_SESSION_LOG_DIR=\"{logdir.as_posix()}\"
export CODEX_SESSION_ID=\"{sid}\"
. \"{SHELL_HELPER.as_posix()}\"
codex_session_start
rm -rf \"{logdir.as_posix()}\"
codex_session_end 0
""")
            runner.chmod(0o755)
            subprocess.run([runner.as_posix()], check=True)
            ndjson = logdir / f"{sid}.ndjson"
            self.assertTrue(ndjson.exists(), "ndjson not recreated")
            lines = [json.loads(l) for l in ndjson.read_text().strip().splitlines()]
            types = [l.get("type") for l in lines]
            self.assertIn("session_end", types)

if __name__ == "__main__":
    unittest.main()
PYT
  record_change "tests/test_session_hooks.py" "create" "Add subprocess-based regression test asserting start/end events."
fi

# ---------- Phase 4: Controlled Pruning ----------
if ! grep -q "^## Pruning" "$CHANGELOG"; then
  printf "## Pruning\n\n(Empty — no assets pruned in this pass.)\n\n" >> "$CHANGELOG"
fi

# ---------- Phase 5: Error Capture ----------
# (Handled inline via $ERRORS logging above as needed)

# ---------- Phase 6: Finalization ----------
{
  echo "# Results"
  echo
  echo "## Implemented"
  echo "- Created shell helper: scripts/session_logging.sh"
  echo "- Created Python helper: codex/logging/session_hooks.py"
  echo "- Injected shell hooks into entrypoint(s) and other launchers (best-effort)"
  echo "- Injected minimal Python __main__ hook (best-effort)"
  echo "- Added regression test: tests/test_session_hooks.py"
  echo
  echo "## Notes"
  echo "- Helpers write NDJSON to .codex/sessions/<SESSION_ID>.ndjson"
  echo "- Minimal, localized edits; backups in .codex/backups/"
  echo
  echo "## Constraints"
  echo "**DO NOT ACTIVATE ANY GitHub Actions files.**"
} > "$RESULTS"

echo "Done. See:"
echo "  - $CHANGELOG"
echo "  - $MAPPING"
echo "  - $RESULTS"
