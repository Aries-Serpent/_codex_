#!/usr/bin/env bash
set -euo pipefail

# ==== Config & Flags ====
DO_NOT_ACTIVATE_GITHUB_ACTIONS=${DO_NOT_ACTIVATE_GITHUB_ACTIONS:-true}
SAFE_MODE=${SAFE_MODE:-true}
WANT_COMMIT=false
if [[ "${1:-}" == "--commit" ]]; then
  WANT_COMMIT=true
fi

# ==== Phase 1 — Preparation ====
STEP="1.1 Identify repository root and clean state"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"
mkdir -p .codex scripts src/codex/logging data || true

HAS_DIRTY=0
if [[ -n "$(git status --porcelain 2>/dev/null || true)" ]]; then HAS_DIRTY=1; fi

README_PATH="$REPO_ROOT/README.md"
README_PRESENT=false
if [[ -f "$README_PATH" ]]; then README_PRESENT=true; fi

# Init logs
CHANGE_LOG=".codex/change_log.md"
ERRORS_LOG=".codex/errors.ndjson"
RESULTS_MD=".codex/results.md"
: > "$ERRORS_LOG"
if [[ ! -f "$CHANGE_LOG" ]]; then
  cat > "$CHANGE_LOG" <<'MD'
# .codex/change_log.md
This log captures file-level changes performed by Codex workflow.
MD
fi

log_change() {
  local file="$1"; local action="$2"; local rationale="$3"
  {
    echo "## $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    echo "- **File:** $file"
    echo "- **Action:** $action"
    echo "- **Rationale:** $rationale"
  } >> "$CHANGE_LOG"
}

log_error() {
  local step="$1"; local desc="$2"; local errmsg="$3"; local ctx="$4"
  local ts; ts="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  printf '{"timestamp":"%s","step":"%s","description":"%s","error":"%s","context":"%s"}\n' \
    "$ts" "$step" "$desc" "$errmsg" "$ctx" >> "$ERRORS_LOG"
  cat <<EOF
Question for ChatGPT-5:
While performing [$step: $desc], encountered the following error:
$errmsg
Context: $ctx
What are the possible causes, and how can this be resolved while preserving intended functionality?
EOF
}

if [[ -d ".github/workflows" ]]; then
  echo "NOTICE: .github/workflows/ is present. Per constraints, no actions will be modified or run."
fi

# ==== Phase 2 — Search & Mapping ====
MAPPING_MD=".codex/mapping.md"
cat > "$MAPPING_MD" <<'MD'
# Mapping Table
| Task | candidate_assets[] | Rationale |
|---|---|---|
| Add `query_logs.py` | (new) `src/codex/logging/query_logs.py` | No prior logging module; standard src layout; localized change |
| SQL on `session_events` | `data/*.db` if present; else `$CODEX_DB_PATH` | Probe SQLite DB path; adapt to schema via PRAGMA |
| README CLI docs | `README.md` | Append a “Logging / Query CLI” section |
MD
log_change "$MAPPING_MD" "create" "Record mapping decisions"

# ==== Phase 3 — Best-Effort Construction ====

PY_PATH="src/codex/logging/query_logs.py"
cat > "$PY_PATH" <<'PY'
#!/usr/bin/env python3
"""
codex.logging.query_logs: Query transcripts from a SQLite 'session_events' table.

Usage examples:
  python -m src.codex.logging.query_logs --help
  python -m src.codex.logging.query_logs --db data/codex.db --session-id S123 --role user --after 2025-01-01 --format json

Behavior:
- Adapts to unknown schemas via PRAGMA table_info(session_events)
- Accepts filters: session_id, role, after/before (ISO-8601), limit/offset, order
- Outputs 'text' (default) or 'json'

Environment:
- CODEX_DB_PATH may point to the SQLite file (default: data/codex.db)
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# --- utilities ---
def parse_when(s: Optional[str]) -> Optional[str]:
    if not s: return None
    try:
        if len(s) == 10 and s[4] == '-' and s[7] == '-':
            return f"{s}T00:00:00"
        dt = datetime.fromisoformat(s)
        return dt.replace(microsecond=0).isoformat()
    except Exception:
        raise SystemExit(f"Invalid datetime: {s}. Use ISO 8601 (e.g., 2025-08-18T09:00:00 or 2025-08-18).")

LIKELY_MAP = {
    "timestamp": ["created_at","timestamp","ts","event_time","time","date","datetime"],
    "role":      ["role","type","speaker"],
    "content":   ["content","message","text","body","value"],
    "session_id":["session_id","session","conversation_id","conv_id","sid"],
    "id":        ["id","rowid","event_id"],
    "metadata":  ["metadata","meta","attrs","json","extra"],
}

def open_db(path: str) -> sqlite3.Connection:
    if not os.path.exists(path):
        raise SystemExit(f"Database file not found: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def resolve_columns(conn: sqlite3.Connection) -> Dict[str,str]:
    cur = conn.execute("PRAGMA table_info(session_events)")
    cols = [r[1] for r in cur.fetchall()]
    if not cols:
        raise SystemExit("Table 'session_events' not found in database.")
    mapping: Dict[str,str] = {}
    for want, candidates in LIKELY_MAP.items():
        for c in candidates:
            if c in cols:
                mapping[want] = c
                break
    required = ["timestamp","role","content"]
    missing = [k for k in required if k not in mapping]
    if missing:
        raise SystemExit(f"Missing required columns in 'session_events': {missing}; found columns: {cols}")
    return mapping

def build_query(mapcol: Dict[str,str],
               session_id: Optional[str],
               role: Optional[str],
               after: Optional[str],
               before: Optional[str],
               order: str,
               limit: Optional[int],
               offset: Optional[int]) -> Tuple[str,List[Any]]:
    cols = [mapcol.get("id", "NULL AS id"),
            mapcol["timestamp"], mapcol["role"], mapcol["content"],
            mapcol.get("session_id","NULL AS session_id"),
            mapcol.get("metadata","NULL AS metadata")]
    select = ", ".join(cols)
    sql = f"SELECT {select} FROM session_events"
    where, params = [], []
    if session_id and "session_id" in mapcol:
        where.append(f"{mapcol['session_id']} = ?")
        params.append(session_id)
    if role:
        where.append(f"{mapcol['role']} = ?")
        params.append(role)
    if after:
        where.append(f"{mapcol['timestamp']} >= ?")
        params.append(after)
    if before:
        where.append(f"{mapcol['timestamp']} <= ?")
        params.append(before)
    if where:
        sql += " WHERE " + " AND ".join(where)
    if order.lower() not in ("asc","desc"):
        order = "asc"
    sql += f" ORDER BY {mapcol['timestamp']} {order.upper()}"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(int(limit))
    if offset is not None:
        sql += " OFFSET ?"
        params.append(int(offset))
    return sql, params

def format_text(rows: List[sqlite3.Row], mapcol: Dict[str,str]) -> str:
    lines = []
    ts = mapcol["timestamp"]; role = mapcol["role"]; content = mapcol["content"]
    sid = mapcol.get("session_id")
    for r in rows:
        t = r[ts]; rr = r[role]; c = r[content]
        ss = f" [{r[sid]}]" if sid and r[sid] is not None else ""
        lines.append(f"{t} ({rr}){ss}: {c}")
    return "\n".join(lines)

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Query transcripts from session_events.")
    p.add_argument("--db", default=os.environ.get("CODEX_DB_PATH","data/codex.db"),
                   help="Path to SQLite DB (default: env CODEX_DB_PATH or data/codex.db)")
    p.add_argument("--session-id", help="Filter by session_id")
    p.add_argument("--role", help="Filter by role (e.g., user, assistant, system, tool)")
    p.add_argument("--after", help="Start time (ISO 8601 or YYYY-MM-DD)")
    p.add_argument("--before", help="End time (ISO 8601 or YYYY-MM-DD)")
    p.add_argument("--format", choices=["text","json"], default="text", help="Output format")
    p.add_argument("--limit", type=int)
    p.add_argument("--offset", type=int)
    p.add_argument("--order", choices=["asc","desc"], default="asc")
    args = p.parse_args(argv)

    try:
        if args.after: args.after = parse_when(args.after)
        if args.before: args.before = parse_when(args.before)
        conn = open_db(args.db)
        with conn:
            mapcol = resolve_columns(conn)
            sql, params = build_query(mapcol, args.session_id, args.role, args.after, args.before, args.order, args.limit, args.offset)
            rows = list(conn.execute(sql, params))
            if args.format == "json":
                print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
            else:
                print(format_text(rows, mapcol))
        return 0
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x "$PY_PATH"
log_change "$PY_PATH" "create" "Add CLI to query session_events with adaptive schema and filters"

SMOKE="scripts/smoke_query_logs.sh"
cat > "$SMOKE" <<'SH2'
#!/usr/bin/env bash
set -euo pipefail
python3 -m src.codex.logging.query_logs --help >/dev/null
echo "[OK] query_logs --help executed"
SH2
chmod +x "$SMOKE"
log_change "$SMOKE" "create" "Add smoke check for query CLI"

CLI_SECTION=$(cat <<'MD'
## Logging: Querying transcripts

This repository includes a CLI to query a SQLite table named `session_events` and render chat transcripts.

### Installation / Invocation
```bash
python3 -m src.codex.logging.query_logs --help
# Specify DB path explicitly or via env:
#   export CODEX_DB_PATH=data/codex.db
#   python3 -m src.codex.logging.query_logs --session-id S123 --role user --after 2025-01-01 --format json
```

### Filters

* `--session-id`: exact match on session identifier
* `--role`: one of your stored roles (e.g., `user`, `assistant`, `system`, `tool`)
* `--after`, `--before`: ISO-8601 or `YYYY-MM-DD` boundaries
* `--format {text,json}`: choose plain text or JSON (default `text`)
* `--limit/--offset`, `--order {asc,desc}`

> The tool auto-adapts to columns in `session_events` (e.g., it tolerates `created_at` vs `timestamp`, `content` vs `message`, etc.). If the table or required columns are missing, it will explain what’s expected.
MD
)

if $README_PRESENT; then
  if ! grep -q "## Logging: Querying transcripts" "$README_PATH"; then
    printf "\n%s\n" "$CLI_SECTION" >> "$README_PATH"
    log_change "$README_PATH" "append section" "Add CLI usage for querying transcripts"
  fi
else
  printf "# *codex*\n\n%s\n" "$CLI_SECTION" > "$README_PATH"
  log_change "$README_PATH" "create" "Create README with CLI usage"
fi

# ==== Phase 4 — Controlled Pruning (none expected) ====

echo "No pruning performed."

# ==== Phase 5 — Error capture ====

DB_PATH="${CODEX_DB_PATH:-data/codex.db}"
if [[ ! -f "$DB_PATH" ]]; then
  log_error "5.1" "Optional DB probe" "Database not found" "Looked at '$DB_PATH'. Provide a SQLite DB with a 'session_events' table."
fi

# ==== Phase 6 — Finalization ====

cat > "$RESULTS_MD" <<'MD'
# Results Summary

## Implemented

* src/codex/logging/query_logs.py
* scripts/smoke_query_logs.sh
* README.md: appended "Logging: Querying transcripts"
* .codex/mapping.md

## Residual gaps

* SQLite database is not included. Provide a DB at $CODEX_DB_PATH (default: data/codex.db) with a 'session_events' table.

## Pruning

* None

## Next recommended steps

* Add a minimal sample DB for CI-less validation.
* Extend query output to include metadata fields when present.

**DO NOT ACTIVATE ANY GitHub Actions files.**
MD
log_change "$RESULTS_MD" "create" "Record results summary"

if $WANT_COMMIT; then
  if [[ "$DO_NOT_ACTIVATE_GITHUB_ACTIONS" == "true" ]]; then
    echo "Committing locally (no push)."
  fi
  git add src/codex/logging/query_logs.py scripts/smoke_query_logs.sh "$README_PATH" .codex/mapping.md "$CHANGE_LOG" "$RESULTS_MD" "$ERRORS_LOG" || true
  git commit -m "feat(logging): add query_logs CLI, smoke checks, and docs [no-actions]" || true
else
  echo "Skipping git commit. Run again with --commit to record changes locally."
fi

echo "Workflow complete."
exit 0
