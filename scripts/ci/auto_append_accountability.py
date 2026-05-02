"""
scripts/ci/auto_append_accountability.py
Phase 5 — Auto-append W-NNN entry to AGENT_ACCOUNTABILITY_REPORT.md.

Called on session close (chatops_copilot_trigger.yml or CI post-session hook).
Reads session data from SQLite agent_sessions table and appends a structured
W-NNN accountability row to docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md.

Usage:
  python scripts/ci/auto_append_accountability.py --session-id <uuid>
  python scripts/ci/auto_append_accountability.py --list-recent  # show last 10 sessions
  python scripts/ci/auto_append_accountability.py --dry-run --session-id <uuid>

If SESSION_ID is not provided, uses the most recent unclosed session in the DB.
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import sqlite3
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
DB_PATH = REPO_ROOT / ".codex" / "codex_corpus.db"


def get_next_w_number(report_text: str) -> int:
    """Return the next sequential W-NNN number from the report."""
    matches = re.findall(r"\| W-(\d+) \|", report_text)
    return max((int(m) for m in matches), default=0) + 1


def format_entry(
    w_num: int,
    session_id: str,
    agent_id: str,
    pr_num: int | None,
    start: str,
    end: str | None,
    violations: int,
    tier: str,
    handoffs: int,
    summary_posted: bool,
) -> str:
    """Format a single W-NNN accountability row."""
    pr_ref = f"PR #{pr_num}" if pr_num else "—"
    end_str = end or "in-progress"
    return (
        f"| W-{w_num:03d} | Session `{session_id[:8]}` | Agent: `{agent_id}` | "
        f"{pr_ref} | Tier: `{tier}` | "
        f"Violations: {violations} | Handoffs: {handoffs} | "
        f"Summary: {'✅' if summary_posted else '❌'} | "
        f"Start: {start[:10]} | End: {end_str[:10]} | "
        f"Auto-appended: {datetime.datetime.now(datetime.timezone.utc).date()} |\n"
    )


def fetch_session(session_id: str) -> dict | None:
    """Fetch session data from SQLite by session_id."""
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT agent_id, pr_number, start_time, end_time, "
            "violation_count, tier_at_close, handoff_count, summary_posted "
            "FROM agent_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        conn.close()
    except Exception:  # noqa: BLE001
        return None

    if not row:
        return None
    return {
        "session_id": session_id,
        "agent_id": row[0] or "unknown",
        "pr_number": row[1],
        "start_time": row[2] or "",
        "end_time": row[3],
        "violation_count": row[4] or 0,
        "tier_at_close": row[5] or "SOFT",
        "handoff_count": row[6] or 0,
        "summary_posted": bool(row[7]),
    }


def fetch_latest_session() -> dict | None:
    """Fetch the most recent session from SQLite."""
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT session_id, agent_id, pr_number, start_time, end_time, "
            "violation_count, tier_at_close, handoff_count, summary_posted "
            "FROM agent_sessions ORDER BY start_time DESC LIMIT 1",
        ).fetchone()
        conn.close()
    except Exception:  # noqa: BLE001
        return None

    if not row:
        return None
    return {
        "session_id": row[0],
        "agent_id": row[1] or "unknown",
        "pr_number": row[2],
        "start_time": row[3] or "",
        "end_time": row[4],
        "violation_count": row[5] or 0,
        "tier_at_close": row[6] or "SOFT",
        "handoff_count": row[7] or 0,
        "summary_posted": bool(row[8]),
    }


def list_recent_sessions(n: int = 10) -> None:
    """Print the last N sessions from SQLite."""
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT session_id, agent_id, pr_number, start_time, tier_at_close "
            "FROM agent_sessions ORDER BY start_time DESC LIMIT ?",
            (n,),
        ).fetchall()
        conn.close()
    except Exception as exc:  # noqa: BLE001
        print(f"DB error: {exc}")
        return

    if not rows:
        print("No sessions found in database.")
        return
    print(f"Last {n} sessions:\n{'─' * 70}")
    for row in rows:
        print(
            f"  {row[0][:8]}  agent={row[1]}  pr={row[2]}  "
            f"started={row[3][:10] if row[3] else '?'}  tier={row[4]}"
        )


def append_entry(session_data: dict, dry_run: bool = False) -> None:
    """Append a W-NNN entry to the accountability report."""
    if not REPORT.exists():
        print(f"WARNING: Accountability report not found: {REPORT}")
        print("Creating minimal report...")
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            "# Agent Accountability Report\n\n"
            "| W-ID | Session | Agent | PR | Tier | Violations | Handoffs | "
            "Summary | Start | End | Appended |\n"
            "|------|---------|-------|----|------|-----------|----------|"
            "---------|-------|-----|----------|\n\n---\n",
            encoding="utf-8",
        )

    report_text = REPORT.read_text(encoding="utf-8")
    w_num = get_next_w_number(report_text)
    entry = format_entry(
        w_num=w_num,
        session_id=session_data["session_id"],
        agent_id=session_data["agent_id"],
        pr_num=session_data.get("pr_number"),
        start=session_data.get("start_time", ""),
        end=session_data.get("end_time"),
        violations=session_data.get("violation_count", 0),
        tier=session_data.get("tier_at_close", "SOFT"),
        handoffs=session_data.get("handoff_count", 0),
        summary_posted=session_data.get("summary_posted", False),
    )

    if dry_run:
        print(f"DRY-RUN: Would append to {REPORT}:\n{entry}")
        return

    # Insert before the last --- separator
    parts = report_text.rsplit("---", 1)
    updated = parts[0] + entry + "---" + parts[1] if len(parts) == 2 else report_text + entry

    REPORT.write_text(updated, encoding="utf-8")
    print(f"Appended W-{w_num:03d} for session {session_data['session_id'][:8]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Auto-append W-NNN entry to AGENT_ACCOUNTABILITY_REPORT.md"
    )
    ap.add_argument("--session-id", type=str, default=None, help="Session UUID to record")
    ap.add_argument("--list-recent", action="store_true", help="List last 10 sessions and exit")
    ap.add_argument("--dry-run", action="store_true", help="Print entry without modifying file")
    args = ap.parse_args()

    if args.list_recent:
        list_recent_sessions()
        sys.exit(0)

    if args.session_id:
        session = fetch_session(args.session_id)
        if not session:
            print(f"Session not found: {args.session_id}")
            sys.exit(1)
    else:
        session = fetch_latest_session()
        if not session:
            print("No sessions found in database — nothing to append.")
            sys.exit(0)

    append_entry(session, dry_run=args.dry_run)
