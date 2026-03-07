#!/usr/bin/env python3
"""
Phase 2: Session-Based Execution — Session Tracker

Tracks session lifecycle with start/end markers, persists state to
memory/sessions/ as JSON and Markdown, and supports auto-resume from
the last recorded state.

Usage:
    python scripts/session_tracker.py start [--label LABEL]
    python scripts/session_tracker.py end   [--session-id ID] [--outcome success|failure|partial]
    python scripts/session_tracker.py status
    python scripts/session_tracker.py resume
    python scripts/session_tracker.py list [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).parent.parent
SESSION_DIR = REPO_ROOT / "memory" / "sessions"
CURRENT_SESSION_FILE = SESSION_DIR / ".current_session.json"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Optional[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")


def _session_path(session_id: str) -> Path:
    return SESSION_DIR / f"session_{session_id}.json"


def _write_markdown(session: dict) -> None:
    sid = session["session_id"]
    path = SESSION_DIR / f"session_{sid}.md"
    lines = [
        f"# Session {sid[:12]}",
        f"**Label:** {session.get('label', 'unlabeled')}",
        f"**Started:** {session.get('started_at', 'unknown')}",
        f"**Ended:** {session.get('ended_at', 'in-progress')}",
        f"**Status:** {session.get('status', 'unknown')}",
        f"**Outcome:** {session.get('outcome', 'pending')}",
        "",
        "## Events",
    ]
    for ev in session.get("events", []):
        lines.append(f"- `{ev['timestamp']}` [{ev['type']}] {ev.get('detail', '')}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(label: str = "") -> int:
    session_id = str(uuid.uuid4())
    session: dict[str, Any] = {
        "session_id": session_id,
        "label": label or f"session-{session_id[:8]}",
        "started_at": _now(),
        "ended_at": None,
        "status": "active",
        "outcome": "pending",
        "events": [{"timestamp": _now(), "type": "start", "detail": label or ""}],
    }
    _save_json(_session_path(session_id), session)
    _save_json(CURRENT_SESSION_FILE, {"session_id": session_id})
    _write_markdown(session)
    print(f"Session started: {session_id}")
    print(f"  Label: {session['label']}")
    print(f"  State file: {_session_path(session_id)}")
    return 0


def cmd_end(session_id: Optional[str] = None, outcome: str = "success") -> int:
    if session_id is None:
        current = _load_json(CURRENT_SESSION_FILE)
        if current is None:
            print("ERROR: No current session. Pass --session-id or run 'start' first.", file=sys.stderr)
            return 1
        session_id = current["session_id"]

    path = _session_path(session_id)
    session = _load_json(path)
    if session is None:
        print(f"ERROR: Session {session_id} not found at {path}", file=sys.stderr)
        return 1

    session["ended_at"] = _now()
    session["status"] = "completed"
    session["outcome"] = outcome
    session["events"].append({"timestamp": _now(), "type": "end", "detail": outcome})

    _save_json(path, session)
    _write_markdown(session)
    CURRENT_SESSION_FILE.unlink(missing_ok=True)

    print(f"Session ended: {session_id}")
    print(f"  Outcome: {outcome}")
    started = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
    ended = datetime.fromisoformat(session["ended_at"].replace("Z", "+00:00"))
    elapsed = (ended - started).total_seconds()
    print(f"  Duration: {elapsed:.0f}s")
    return 0


def cmd_status() -> int:
    current = _load_json(CURRENT_SESSION_FILE)
    if current is None:
        print("No active session.")
        return 0
    session_id = current["session_id"]
    session = _load_json(_session_path(session_id))
    if session is None:
        print(f"WARNING: Current session file references {session_id} but state file is missing.")
        return 1
    print(f"Active session: {session_id}")
    print(f"  Label:    {session.get('label', 'unlabeled')}")
    print(f"  Started:  {session.get('started_at')}")
    print(f"  Status:   {session.get('status')}")
    print(f"  Events:   {len(session.get('events', []))}")
    return 0


def cmd_resume() -> int:
    """Print the last session state so the agent can restore context."""
    current = _load_json(CURRENT_SESSION_FILE)
    if current:
        session_id = current["session_id"]
        session = _load_json(_session_path(session_id))
        if session:
            print(f"Resuming session: {session_id}")
            print(json.dumps(session, indent=2, default=str))
            return 0

    # No active session — find the most recent completed session
    sessions = sorted(SESSION_DIR.glob("session_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in sessions:
        if ".current" in path.name:
            continue
        session = _load_json(path)
        if session and session.get("status") == "completed":
            print(f"Last completed session: {session['session_id']}")
            print(json.dumps(session, indent=2, default=str))
            return 0

    print("No sessions found to resume.")
    return 0


def cmd_list(limit: int = 10) -> int:
    sessions = sorted(SESSION_DIR.glob("session_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    shown = 0
    for path in sessions:
        if ".current" in path.name:
            continue
        session = _load_json(path)
        if session is None:
            continue
        status_icon = {"active": "🟡", "completed": "✅", "error": "❌"}.get(session.get("status", ""), "❓")
        print(f"{status_icon}  {session['session_id'][:12]}  {session.get('started_at', '')[:19]}  {session.get('label', '')}")
        shown += 1
        if shown >= limit:
            break
    if shown == 0:
        print("No sessions recorded yet.")
    return 0


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Begin a new session")
    p_start.add_argument("--label", default="")

    p_end = sub.add_parser("end", help="End the current session")
    p_end.add_argument("--session-id", default=None)
    p_end.add_argument("--outcome", choices=["success", "failure", "partial"], default="success")

    sub.add_parser("status", help="Show current session status")
    sub.add_parser("resume", help="Resume or inspect the last session")

    p_list = sub.add_parser("list", help="List recent sessions")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if args.cmd == "start":
        return cmd_start(label=args.label)
    elif args.cmd == "end":
        return cmd_end(session_id=args.session_id, outcome=args.outcome)
    elif args.cmd == "status":
        return cmd_status()
    elif args.cmd == "resume":
        return cmd_resume()
    elif args.cmd == "list":
        return cmd_list(limit=args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
