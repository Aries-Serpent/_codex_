#!/usr/bin/env bash
set -euo pipefail

# Archive vacuum: summarizes/prunes stale tombstones and regenerates summaries.
# Tailored for Python-heavy repo with 'src/' layout and Node subtrees.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")"
export PYTHONPATH="$ROOT:$ROOT/src:${PYTHONPATH:-}"
REPORT_DIR="$ROOT/.codex/reports"
mkdir -p "$REPORT_DIR"

timestamp() { date -u +"%Y%m%dT%H%M%SZ"; }
ts="$(timestamp)"
sum="$REPORT_DIR/summary-$ts.json"

echo "==> archive vacuum starting @ $ts"

can_import=$(python3 - <<'PY'
try:
    import codex.cli_archive as _  # noqa: F401
    print("yes")
except Exception:
    print("no")
PY
)

if [ "$can_import" = "yes" ]; then
  echo "-> using codex.cli_archive summary/vacuum"
  # Prefer summary if present; fall back to vacuum
  python3 -m codex.cli_archive summary --output "$sum" 2>/dev/null || {
    echo "summary failed or unavailable; trying vacuum" >&2
    python3 -m codex.cli_archive vacuum --output "$sum" || {
      echo "WARN: codex.cli_archive summary/vacuum failed; wrote no summary" >&2
    }
  }
else
  echo "WARN: codex.cli_archive not found; writing placeholder summary" >&2
  echo '{"status":"noop","reason":"codex.cli_archive not importable","summary":[]}' > "$sum"
fi

echo "==> summary written: $sum"
