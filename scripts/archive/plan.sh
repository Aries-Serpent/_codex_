#!/usr/bin/env bash
set -euo pipefail

# Archive planner: generates a candidate list and writes a report.
# Tailored for Python-heavy repo with 'src/' layout and Node subtrees.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")"
export PYTHONPATH="$ROOT:$ROOT/src:${PYTHONPATH:-}"
REPORT_DIR="$ROOT/.codex/reports"
mkdir -p "$REPORT_DIR"

timestamp() { date -u +"%Y%m%dT%H%M%SZ"; }
ts="$(timestamp)"
out="$REPORT_DIR/plan-$ts.json"

echo "==> archive planner starting @ $ts"

can_import=$(python3 - <<'PY'
try:
    import codex.cli_archive as _  # noqa: F401
    print("yes")
except Exception:
    print("no")
PY
)

if [ "$can_import" = "yes" ]; then
  echo "-> using codex.cli_archive plan"
  python3 -m codex.cli_archive plan --output "$out" || {
    echo "WARN: codex.cli_archive plan failed; wrote no report" >&2
  }
else
  echo "WARN: codex.cli_archive not found; writing placeholder plan" >&2
  echo '{"status":"noop","reason":"codex.cli_archive not importable","candidates":[]}' > "$out"
fi

echo "==> plan written: $out"
