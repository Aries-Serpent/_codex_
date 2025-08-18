#!/usr/bin/env python3
"""Minimal SQLite/NDJSON log viewer for codex."""

import argparse, os, sys, json, sqlite3, pathlib, time


def print_rows(rows):
    if not rows:
        print("(no rows)")
        return
    for ts, session, kind, message in rows:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        print(f"{stamp} [{session}] {kind}: {message}")


def view_sqlite(db_path, session=None, tail=None):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    base = "SELECT ts, session, kind, message FROM logs"
    where = []
    args = []
    if session:
        where.append("session = ?")
        args.append(session)
    sql = base + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY ts DESC"
    if tail:
        sql += f" LIMIT {int(tail)}"
    rows = list(cur.execute(sql, args))
    print_rows(reversed(rows))
    con.close()


def view_ndjson(file_path, session=None, tail=None):
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ts = float(obj.get("ts") or obj.get("time") or 0)
            rows.append((ts, obj.get("session", ""), obj.get("kind", ""), obj.get("message", "")))
    if session:
        rows = [r for r in rows if r[1] == session]
    rows.sort(key=lambda r: r[0])
    if tail:
        rows = rows[-int(tail):]
    print_rows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.getenv("CODEX_LOG_DB_PATH", ".codex/codex_logs.sqlite"))
    ap.add_argument("--session", default=os.getenv("CODEX_SESSION_ID"))
    ap.add_argument("--tail", type=int)
    args = ap.parse_args()

    p = pathlib.Path(args.db)
    if p.suffix.lower() == ".sqlite":
        if not p.exists():
            print(f"SQLite DB not found at {p}", file=sys.stderr)
            return 1
        view_sqlite(str(p), session=args.session, tail=args.tail)
    else:
        if not p.exists():
            print(f"NDJSON file not found at {p}", file=sys.stderr)
            return 1
        view_ndjson(str(p), session=args.session, tail=args.tail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
