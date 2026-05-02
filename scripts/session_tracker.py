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
    python scripts/session_tracker.py archive --session-id ID [--reason REASON] [--pr-number N]
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

# ── Session status constants ──────────────────────────────────────────────────
# Use these constants instead of bare string literals to ensure consistency
# across cmd_* CLI functions, start_session/end_session programmatic API,
# and any test assertions.

STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_ERROR = "error"
STATUS_ARCHIVED = "archived"


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
        "status": STATUS_ACTIVE,
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
    session["status"] = STATUS_COMPLETED
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
        if session and session.get("status") == STATUS_COMPLETED:
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
        status_icon = {STATUS_ACTIVE: "🟡", STATUS_COMPLETED: "✅", STATUS_ERROR: "❌", STATUS_ARCHIVED: "🗄"}.get(session.get("status", ""), "❓")
        print(f"{status_icon}  {session['session_id'][:12]}  {session.get('started_at', '')[:19]}  {session.get('label', '')}")
        shown += 1
        if shown >= limit:
            break
    if shown == 0:
        print("No sessions recorded yet.")
    return 0


def cmd_archive(
    session_id: str,
    reason: str = "",
    pr_number: Optional[int] = None,
    dry_run: bool = False,
) -> int:
    """Force-archive a session by ID.

    Works for both locally tracked sessions and stale/cached sessions that only
    exist in an external system (e.g. a GitHub Copilot task that can no longer
    be archived via the UI).  When no local session file is found a tombstone
    record is created so the decision is permanently documented in the repo.

    Pass ``--dry-run`` to preview the action without writing any files.
    """
    path = _session_path(session_id)
    session = _load_json(path)

    now = _now()
    is_tombstone = session is None
    if is_tombstone:
        # Session does not exist locally — create a tombstone record so the
        # archive action is traceable in the repository's own audit trail.
        session = {
            "session_id": session_id,
            "label": f"archived-stale-{session_id[:8]}",
            "started_at": now,
            "ended_at": now,
            "status": STATUS_ARCHIVED,
            "outcome": "archived",
            "tombstone": True,
            "events": [],
        }
        print(f"NOTE: No local session file found for {session_id}; creating tombstone record.")
    else:
        session["ended_at"] = session.get("ended_at") or now
        session["status"] = STATUS_ARCHIVED
        session["outcome"] = "archived"

    session["archived_at"] = now
    if reason:
        session["archive_reason"] = reason
    if pr_number is not None:
        session["pr_number"] = pr_number

    session.setdefault("events", []).append(
        {"timestamp": now, "type": "archive", "detail": reason or "force-archived"}
    )

    if dry_run:
        print(f"[DRY RUN] Would archive session: {session_id}")
        print(f"  Tombstone: {is_tombstone}")
        if reason:
            print(f"  Reason: {reason}")
        if pr_number is not None:
            print(f"  PR: #{pr_number}")
        print(f"  Archive record would be written to: {path}")
        print(f"  Preview payload:\n{json.dumps(session, indent=4, default=str)}")
        return 0

    _save_json(path, session)
    _write_markdown(session)

    # Remove from current-session pointer if it referenced this session.
    # Use SESSION_DIR dynamically so test patches to SESSION_DIR are respected.
    current_session_file = SESSION_DIR / ".current_session.json"
    current = _load_json(current_session_file)
    if current and current.get("session_id") == session_id:
        current_session_file.unlink(missing_ok=True)

    print(f"Session archived: {session_id}")
    if reason:
        print(f"  Reason: {reason}")
    if pr_number is not None:
        print(f"  PR: #{pr_number}")
    print(f"  Archive record: {path}")
    return 0


def cmd_metrics(output_format: str = "text") -> int:
    """Print lifecycle counts for all local sessions.

    Output includes counts for each status (active, completed, error, archived)
    plus a total, giving a quick health-check of the session audit trail.
    Supports ``--format json`` for machine consumption in CI dashboards.
    """
    counts: dict[str, int] = {
        STATUS_ACTIVE: 0,
        STATUS_COMPLETED: 0,
        STATUS_ERROR: 0,
        STATUS_ARCHIVED: 0,
        "unknown": 0,
    }
    tombstones = 0

    for path in SESSION_DIR.glob("session_*.json"):
        if ".current" in path.name:
            continue
        session = _load_json(path)
        if session is None:
            continue
        status = session.get("status", "unknown")
        if status in counts:
            counts[status] += 1
        else:
            counts["unknown"] += 1
        if session.get("tombstone"):
            tombstones += 1

    total = sum(counts.values())

    if output_format == "json":
        import json as _json

        print(
            _json.dumps(
                {
                    "total": total,
                    "active": counts[STATUS_ACTIVE],
                    "completed": counts[STATUS_COMPLETED],
                    "error": counts[STATUS_ERROR],
                    "archived": counts[STATUS_ARCHIVED],
                    "tombstones": tombstones,
                    "unknown": counts["unknown"],
                },
                indent=2,
            )
        )
    else:
        print("── Session Lifecycle Metrics ──────────────────────────")
        print(f"  🟡 Active    : {counts[STATUS_ACTIVE]}")
        print(f"  ✅ Completed : {counts[STATUS_COMPLETED]}")
        print(f"  ❌ Error     : {counts[STATUS_ERROR]}")
        print(f"  🗄  Archived  : {counts[STATUS_ARCHIVED]}")
        if counts["unknown"]:
            print(f"  ❓ Unknown   : {counts['unknown']}")
        print("  ──────────────────────────────────────────────────────")
        print(f"  📊 Total     : {total}  (of which {tombstones} are tombstones)")
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

    p_archive = sub.add_parser(
        "archive",
        help="Force-archive a session (including stale/cached sessions without a local file)",
    )
    p_archive.add_argument("--session-id", required=True, help="Session UUID to archive")
    p_archive.add_argument("--reason", default="", help="Human-readable reason for archiving")
    p_archive.add_argument("--pr-number", type=int, default=None, help="Associated PR number")
    p_archive.add_argument(
        "--dry-run", action="store_true", default=False,
        help="Preview what would be archived without writing any files",
    )

    p_metrics = sub.add_parser("metrics", help="Show session lifecycle counts (active/completed/archived/error)")
    p_metrics.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    if args.cmd == "start":
        return cmd_start(label=args.label)
    if args.cmd == "end":
        return cmd_end(session_id=args.session_id, outcome=args.outcome)
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "resume":
        return cmd_resume()
    if args.cmd == "list":
        return cmd_list(limit=args.limit)
    if args.cmd == "archive":
        return cmd_archive(
            session_id=args.session_id,
            reason=args.reason,
            pr_number=args.pr_number,
            dry_run=args.dry_run,
        )
    if args.cmd == "metrics":
        return cmd_metrics(output_format=args.format)
    return 0


# ── Programmatic API (for test harness and external callers) ──────────────────

def start_session(label: str = "") -> str:
    """Start a new session and return its UUID string.

    Unlike ``cmd_start`` (which is the CLI entry point returning an exit code),
    this function returns the session_id directly so callers can reference the
    session in subsequent ``end_session`` or ``list_sessions`` calls.
    """
    session_id = str(uuid.uuid4())
    session: dict[str, Any] = {
        "session_id": session_id,
        "label": label or f"session-{session_id[:8]}",
        "started_at": _now(),
        "ended_at": None,
        "status": STATUS_ACTIVE,
        "outcome": "pending",
        "events": [{"timestamp": _now(), "type": "start", "detail": label or ""}],
    }
    _save_json(_session_path(session_id), session)
    # Use SESSION_DIR dynamically so test patches to SESSION_DIR are respected.
    _save_json(SESSION_DIR / ".current_session.json", {"session_id": session_id})
    _write_markdown(session)
    return session_id


def end_session(session_id: Optional[str] = None, outcome: str = "success") -> None:
    """End a session by ID (or the current session if *session_id* is None).

    Unlike ``cmd_end`` (CLI entry point), this function raises ``ValueError``
    on error rather than returning a non-zero exit code.
    """
    if session_id is None:
        current = _load_json(SESSION_DIR / ".current_session.json")
        if current is None:
            raise ValueError("No current session. Pass session_id explicitly.")
        session_id = current["session_id"]

    path = _session_path(session_id)
    session = _load_json(path)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")

    session["ended_at"] = _now()
    session["status"] = STATUS_COMPLETED
    session["outcome"] = outcome
    session["events"].append({"timestamp": _now(), "type": "end", "detail": outcome})
    _save_json(path, session)
    _write_markdown(session)


def list_sessions(limit: int = 10) -> list[dict[str, Any]]:
    """Return a list of recent session dicts (most recent first).

    Unlike ``cmd_list`` (CLI entry point), this function returns the parsed
    session data directly for programmatic inspection.
    """
    paths = sorted(SESSION_DIR.glob("session_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    result: list[dict[str, Any]] = []
    for path in paths:
        if ".current" in path.name:
            continue
        session = _load_json(path)
        if session is not None:
            result.append(session)
        if len(result) >= limit:
            break
    return result


def archive_session(
    session_id: str,
    reason: str = "",
    pr_number: Optional[int] = None,
) -> dict[str, Any]:
    """Force-archive a session by ID and return the final session dict.

    Unlike ``cmd_archive`` (CLI entry point), this function returns the
    archived session data directly for programmatic inspection and raises
    ``RuntimeError`` only on unrecoverable I/O errors.

    When no local session file is found a tombstone record is created so
    the archive action is permanently documented in the repository's own
    audit trail.  This is specifically designed to handle stale/cached
    sessions that exist only in an external system (e.g. a GitHub Copilot
    task whose "Archive" button is unavailable due to stale data).
    """
    path = _session_path(session_id)
    session = _load_json(path)

    now = _now()
    if session is None:
        session = {
            "session_id": session_id,
            "label": f"archived-stale-{session_id[:8]}",
            "started_at": now,
            "ended_at": now,
            "status": STATUS_ARCHIVED,
            "outcome": "archived",
            "tombstone": True,
            "events": [],
        }
    else:
        session["ended_at"] = session.get("ended_at") or now
        session["status"] = STATUS_ARCHIVED
        session["outcome"] = "archived"

    session["archived_at"] = now
    if reason:
        session["archive_reason"] = reason
    if pr_number is not None:
        session["pr_number"] = pr_number

    session.setdefault("events", []).append(
        {"timestamp": now, "type": "archive", "detail": reason or "force-archived"}
    )

    _save_json(path, session)
    _write_markdown(session)

    # Remove from current-session pointer if it referenced this session.
    current_ptr = SESSION_DIR / ".current_session.json"
    current = _load_json(current_ptr)
    if current and current.get("session_id") == session_id:
        current_ptr.unlink(missing_ok=True)

    return session


def session_metrics() -> dict[str, int]:
    """Return lifecycle counts for all local sessions as a dict.

    Provides a programmatic counterpart to ``cmd_metrics --format json`` for
    use in dashboards, monitoring scripts, or CI health checks.

    Returns:
        dict with keys: total, active, completed, error, archived, tombstones, unknown
    """
    counts: dict[str, int] = {
        STATUS_ACTIVE: 0,
        STATUS_COMPLETED: 0,
        STATUS_ERROR: 0,
        STATUS_ARCHIVED: 0,
        "unknown": 0,
    }
    tombstones = 0

    for path in SESSION_DIR.glob("session_*.json"):
        if ".current" in path.name:
            continue
        session = _load_json(path)
        if session is None:
            continue
        status = session.get("status", "unknown")
        if status in counts:
            counts[status] += 1
        else:
            counts["unknown"] += 1
        if session.get("tombstone"):
            tombstones += 1

    return {
        "total": sum(counts.values()),
        "active": counts[STATUS_ACTIVE],
        "completed": counts[STATUS_COMPLETED],
        "error": counts[STATUS_ERROR],
        "archived": counts[STATUS_ARCHIVED],
        "tombstones": tombstones,
        "unknown": counts["unknown"],
    }


if __name__ == "__main__":
    sys.exit(main())
