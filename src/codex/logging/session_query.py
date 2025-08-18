"""Session query CLI.

Usage:
    python -m codex.logging.session_query --session-id S123 [--last 50] [--db path/to.db]

This uses a simple SELECT against the `session_events` table and prints rows ordered by timestamp.
"""
from __future__ import annotations
import argparse, os, sqlite3, json, sys
from pathlib import Path
from typing import Optional

def infer_db_path(cli_db: Optional[str]) -> Path:
    if cli_db:
        return Path(cli_db)
    env = os.getenv("CODEX_LOG_DB_PATH")
    if env:
        return Path(env)
    return Path(".codex/session_logs.db")

def main(argv=None):
    p = argparse.ArgumentParser(prog="codex.logging.session_query", description="Query logged session events.")
    p.add_argument("--session-id", required=True, help="Exact session identifier to filter.")
    p.add_argument("--last", type=int, default=0, help="Return only the last N rows (0 = all).")
    p.add_argument("--db", help="Path to SQLite DB.")
    p.add_argument("--format", choices=["text","json"], default="text")
    args = p.parse_args(argv)

    db = infer_db_path(args.db)
    con = sqlite3.connect(db)
    try:
        cur = con.cursor()
        sql = "SELECT ts, role, message FROM session_events WHERE session_id = ? ORDER BY ts ASC"
        rows = list(cur.execute(sql, (args.session_id,)))
    finally:
        con.close()

    if args.last and len(rows) > args.last:
        rows = rows[-args.last:]

    if args.format == "json":
        print(json.dumps([{"ts": r[0], "role": r[1], "message": r[2]} for r in rows], ensure_ascii=False, indent=2))
    else:
        for ts, role, message in rows:
            print(f"{ts:.3f}	{role:9s}	{message}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
