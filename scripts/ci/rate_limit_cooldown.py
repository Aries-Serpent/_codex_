#!/usr/bin/env python3
"""Rate-Limit Cooldown Manager — PR pre-warning + cooldown timer + repo variable sync.

Three problems solved in one tool:

  1. PRE-WARNING: Posts a structured PR comment BEFORE hitting the weekly limit,
     giving the next session a "cooldown timer" so it doesn't retry blindly.

  2. COOLDOWN TIMER: Calculates and stores the exact UTC timestamp when it is
     safe to start the next session, written to the ``COPILOT_COOLDOWN_UNTIL_UTC``
     repo variable so any workflow/agent can read it without parsing files.

  3. REPO VARIABLE SYNC: Uses ``github_var_writer.upsert_var`` (same API pattern
     as the rest of the codebase) to keep these variables in sync:

       COPILOT_COOLDOWN_UNTIL_UTC       — ISO-8601 "safe to retry" timestamp
       COPILOT_RATE_LIMIT_HIT_COUNT     — cumulative 429 hit count this week
       COPILOT_LAST_SESSION_START_UTC   — most recent session start
       COPILOT_SESSION_COOLDOWN_MINUTES — recommended wait between sessions

Observed cascade (PR #4389, runs 3476–3489) that motivated this tool:
  - 8 sessions in rapid succession, all hitting 429 within ~15 min of each other
  - No inter-session delay because no shared state existed between runs
  - Push conflicts on top of 429 created a compound failure

Design
------
  State is persisted to ``.codex/rate_limit_cooldown.json`` (local to the runner).
  Repo variables are the cross-session, cross-runner source of truth.

Usage
-----
    # Record a session starting (call at D-00 gate, before any work):
    python3 scripts/ci/rate_limit_cooldown.py start --pr 4389 --session S924

    # Check if cooldown is active before triggering another session:
    python3 scripts/ci/rate_limit_cooldown.py check
    python3 scripts/ci/rate_limit_cooldown.py check --json

    # Record a 429 hit and set cooldown (call inside rate_limit_handler.py flow):
    python3 scripts/ci/rate_limit_cooldown.py hit429 \\
        --pr 4389 --session S923 --reset-minutes 365

    # Record clean session end:
    python3 scripts/ci/rate_limit_cooldown.py end --session S924 --outcome ok

    # Post pre-warning comment to PR (call when budget > 70% used):
    python3 scripts/ci/rate_limit_cooldown.py warn --pr 4389 --budget-pct 75

    # Post cooldown comment to PR after 429:
    python3 scripts/ci/rate_limit_cooldown.py post-cooldown --pr 4389 --cooldown-minutes 365

    # Sync repo variables from local state (requires CODEX_MASTER_KEY):
    python3 scripts/ci/rate_limit_cooldown.py sync-vars

Exit codes
----------
    0  No cooldown active — safe to start session
    1  Cooldown active — do NOT start session
    2  Cooldown unknown — proceed with caution
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Paths & constants ──────────────────────────────────────────────────────────

STATE_FILE = Path(".codex/rate_limit_cooldown.json")
RATE_LIMIT_LOG = Path(".codex/rate_limit_log.jsonl")

REPO = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
GH_TOKEN = (
    os.environ.get("CODEX_ADMIN_KEY")
    or os.environ.get("CODEX_MASTER_KEY")
    or os.environ.get("CODEX_BACKUP_KEY")
    or os.environ.get("GITHUB_TOKEN")
    or os.environ.get("GH_TOKEN")
    or ""
)

# Repo variable names (written by this tool, read by any workflow/agent)
VAR_COOLDOWN_UNTIL = "COPILOT_COOLDOWN_UNTIL_UTC"
VAR_HIT_COUNT = "COPILOT_RATE_LIMIT_HIT_COUNT"
VAR_LAST_START = "COPILOT_LAST_SESSION_START_UTC"
VAR_COOLDOWN_MINS = "COPILOT_SESSION_COOLDOWN_MINUTES"

# Conservative defaults
DEFAULT_COOLDOWN_MINUTES = 30    # wait between sessions even without a 429
POST_429_BUFFER_MINUTES = 15     # extra buffer added on top of reported reset window
WARNING_SESSION_COUNT = 6        # warn after this many sessions in a week


# ── State I/O ──────────────────────────────────────────────────────────────────

def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {
            "schema_version": "1.0",
            "sessions": [],
            "hit429_count": 0,
            "cooldown_until_utc": None,
            "cooldown_minutes": DEFAULT_COOLDOWN_MINUTES,
            "last_updated": None,
        }
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {"schema_version": "1.0", "sessions": [], "hit429_count": 0,
                "cooldown_until_utc": None, "cooldown_minutes": DEFAULT_COOLDOWN_MINUTES,
                "last_updated": None}


def _save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _append_log(event: dict) -> None:
    RATE_LIMIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with RATE_LIMIT_LOG.open("a") as f:
        f.write(json.dumps(event) + "\n")


# ── GitHub API (PR comments + repo variables) ───────────────────────────────────

def _gh(method: str, path: str, body: dict | None = None) -> tuple[int, object]:
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-rate-limit-cooldown/1.0",
    }
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except Exception as exc:
        return -1, {"error": str(exc)}


def _upsert_repo_var(name: str, value: str) -> bool:
    """PATCH (or POST) a repo Actions variable. Returns True on success."""
    if not GH_TOKEN:
        print(f"  ⚠️  No token — skipping var write: {name}", file=sys.stderr)
        return False
    base = f"/repos/{REPO}/actions/variables"
    status, _ = _gh("PATCH", f"{base}/{name}", {"value": value})
    if status == 404:
        status, _ = _gh("POST", base, {"name": name, "value": value})
    ok = status in (201, 204)
    icon = "✅" if ok else "❌"
    print(f"  {icon} repo var {name} = {value[:60]}  (HTTP {status})", file=sys.stderr)
    return ok


def _get_repo_var(name: str) -> str | None:
    """GET a single repo variable value. Returns None if missing."""
    if not GH_TOKEN:
        return None
    status, data = _gh("GET", f"/repos/{REPO}/actions/variables/{name}")
    if status == 200 and isinstance(data, dict):
        return data.get("value")
    return None


def _post_or_update_pr_comment(pr_number: int, body: str, marker: str) -> bool:
    """Post or update a PR comment identified by a unique HTML marker."""
    if not GH_TOKEN or not REPO:
        print("  ⚠️  No token/repo — skipping PR comment", file=sys.stderr)
        return False

    status, comments = _gh("GET", f"/repos/{REPO}/issues/{pr_number}/comments?per_page=100")
    existing_id: int | None = None
    if status == 200 and isinstance(comments, list):
        for c in comments:
            if marker in (c.get("body") or ""):
                existing_id = c["id"]
                break

    if existing_id:
        status, _ = _gh("PATCH", f"/repos/{REPO}/issues/comments/{existing_id}", {"body": body})
        verb = "updated"
    else:
        status, _ = _gh("POST", f"/repos/{REPO}/issues/{pr_number}/comments", {"body": body})
        verb = "posted"

    ok = status in (200, 201)
    print(f"  {'✅' if ok else '❌'} PR #{pr_number} comment {verb} (HTTP {status})", file=sys.stderr)
    return ok


# ── Cooldown logic ─────────────────────────────────────────────────────────────

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%S+00:00"):
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def cooldown_status(state: dict) -> dict:
    """Compute current cooldown status from local state + remote repo var."""
    now = _now_utc()

    # Prefer repo variable (cross-runner source of truth) over local file
    remote_val = _get_repo_var(VAR_COOLDOWN_UNTIL)
    cooldown_until_ts = remote_val or state.get("cooldown_until_utc")
    cooldown_dt = _parse_iso(cooldown_until_ts)

    if cooldown_dt and now < cooldown_dt:
        mins_remaining = int((cooldown_dt - now).total_seconds() / 60)
        return {
            "active": True,
            "cooldown_until_utc": cooldown_until_ts,
            "mins_remaining": mins_remaining,
            "message": f"🔴 COOLDOWN ACTIVE — wait {mins_remaining} min until {cooldown_dt.strftime('%H:%MZ')}",
            "hit429_count": state.get("hit429_count", 0),
            "session_count_this_week": _sessions_this_week(state),
            "source": "repo_var" if remote_val else "local_state",
        }

    sessions_this_week = _sessions_this_week(state)
    hit_count = state.get("hit429_count", 0)
    warning = sessions_this_week >= WARNING_SESSION_COUNT or hit_count > 0

    return {
        "active": False,
        "cooldown_until_utc": cooldown_until_ts,
        "mins_remaining": 0,
        "message": (
            f"⚠️  {sessions_this_week} sessions this week — monitor closely"
            if warning
            else "✅ No cooldown — safe to start session"
        ),
        "warning": warning,
        "hit429_count": hit_count,
        "session_count_this_week": sessions_this_week,
        "source": "repo_var" if remote_val else "local_state",
    }


def _sessions_this_week(state: dict) -> int:
    """Count sessions started within the last 7 days."""
    cutoff = _now_utc() - timedelta(days=7)
    return sum(
        1 for s in state.get("sessions", [])
        if (_parse_iso(s.get("started_at")) or datetime.min.replace(tzinfo=timezone.utc)) > cutoff
    )


def set_cooldown(state: dict, minutes: int, reason: str = "429") -> dict:
    """Set the cooldown timer and write it to repo variables."""
    until_dt = _now_utc() + timedelta(minutes=minutes)
    until_str = until_dt.strftime("%Y-%m-%dT%H:%MZ")

    state["cooldown_until_utc"] = until_str
    state["cooldown_minutes"] = minutes

    # Write to repo variables
    _upsert_repo_var(VAR_COOLDOWN_UNTIL, until_str)
    _upsert_repo_var(VAR_COOLDOWN_MINS, str(minutes))

    _append_log({
        "event": f"cooldown_set_{reason}",
        "cooldown_until_utc": until_str,
        "minutes": minutes,
    })

    return state


# ── PR Comment bodies ───────────────────────────────────────────────────────────

def _pre_warning_body(
    pr_number: int,
    session_count: int,
    hit_count: int,
    cooldown_minutes: int,
    session: str = "",
) -> str:
    marker = "<!-- codex-rate-limit-prewarning -->"
    now_str = _now_utc().strftime("%Y-%m-%dT%H:%MZ")
    safe_after = (_now_utc() + timedelta(minutes=cooldown_minutes)).strftime("%H:%MZ")

    return "\n".join([
        marker,
        "## ⚠️ Rate-Limit Pre-Warning — Approaching Weekly Budget",
        "",
        f"> **Session:** `{session or 'current'}`  ",
        f"> **Generated:** `{now_str}`  ",
        f"> **Sessions this week:** `{session_count}`  ",
        f"> **Prior 429 hits:** `{hit_count}`",
        "",
        "---",
        "",
        "### ⏳ Recommended Cooldown",
        "",
        f"Wait **{cooldown_minutes} minutes** between sessions to avoid hitting the weekly rate limit.",
        "",
        "| | |",
        "|---|---|",
        f"| 🕐 Current time | `{now_str}` |",
        f"| ✅ Safe to retry after | `{safe_after}` |",
        f"| ⏳ Cooldown | **{cooldown_minutes} min** |",
        "",
        "---",
        "",
        "### 🔄 Recovery Sequence",
        "",
        "Before triggering the next session:",
        "",
        "```bash",
        "# 1. Check current cooldown status",
        "python3 scripts/ci/rate_limit_cooldown.py check",
        "",
        "# 2. Check for push conflicts from automated bot commits",
        "python3 scripts/ci/push_conflict_resolver.py",
        "",
        "# 3. View full rate-limit status",
        "python3 scripts/ci/rate_limit_status.py",
        "```",
        "",
        f"Repo variable `{VAR_COOLDOWN_UNTIL}` has been updated with the safe retry time.",
        "",
        "_This comment is auto-updated by `scripts/ci/rate_limit_cooldown.py`._",
    ])


def _post_429_body(
    pr_number: int,
    session: str,
    reset_minutes: int,
    cooldown_minutes: int,
    hit_count: int,
    request_id: str = "",
    completed: list[str] | None = None,
    pending: list[str] | None = None,
) -> str:
    marker = "<!-- codex-rate-limit-cooldown -->"
    now_str = _now_utc().strftime("%Y-%m-%dT%H:%MZ")
    safe_after_dt = _now_utc() + timedelta(minutes=cooldown_minutes)
    safe_after = safe_after_dt.strftime("%Y-%m-%dT%H:%MZ")

    lines = [
        marker,
        "## 🔴 Rate-Limit Hit — Cooldown Timer Active",
        "",
        f"> **Session:** `{session}`  ",
        f"> **Request ID:** `{request_id or 'N/A'}`  ",
        f"> **Hit at:** `{now_str}`  ",
        f"> **429 hit count (cumulative):** `{hit_count}`",
        "",
        "---",
        "",
        "### ⏳ Cooldown Timer",
        "",
        "| | |",
        "|---|---|",
        f"| 🔴 Hit at | `{now_str}` |",
        f"| 🕐 GitHub reset window | `~{reset_minutes} min` |",
        f"| ➕ Safety buffer | `+{POST_429_BUFFER_MINUTES} min` |",
        f"| ✅ **Safe to retry after** | **`{safe_after}`** |",
        f"| ⏳ **Wait** | **{cooldown_minutes} min** |",
        "",
        f"> Repo variable `{VAR_COOLDOWN_UNTIL}` = `{safe_after}`",
        "",
        "---",
        "",
    ]

    if completed:
        lines += ["### ✅ Completed before rate-limit hit", ""]
        for t in completed:
            lines.append(f"- [x] {t}")
        lines.append("")

    if pending:
        lines += ["### ❌ Pending — carry forward to next session", ""]
        for t in pending:
            lines.append(f"- [ ] {t}")
        lines.append("")

    lines += [
        "---",
        "",
        "### 🔄 Next Session — Recovery Sequence",
        "",
        f"After `{safe_after}` post the following comment to restart:",
        "",
        "```",
        f"@copilot Continue from rate-limit cooldown on PR #{pr_number}.",
        "1. python3 scripts/ci/rate_limit_cooldown.py check",
        "2. python3 scripts/ci/push_conflict_resolver.py",
        "3. python3 scripts/ci/rate_limit_handler.py --resolve",
        "4. python3 scripts/ci/rate_limit_cooldown.py start --pr {pr_number}",
        "5. Resume all pending tasks listed above",
        "```",
        "",
        "_Auto-generated by `scripts/ci/rate_limit_cooldown.py`_",
    ]
    return "\n".join(lines)


# ── Sub-commands ────────────────────────────────────────────────────────────────

def cmd_start(args: argparse.Namespace) -> int:
    """Record session start; block if cooldown is active."""
    state = _load_state()
    status = cooldown_status(state)

    if status["active"]:
        print(f"\n{status['message']}", file=sys.stderr)
        print(
            f"  ⛔  Do NOT start session — {status['mins_remaining']} min remaining",
            file=sys.stderr,
        )
        if not args.force:
            return 1

    session_entry = {
        "session": args.session or f"S{_now_utc().strftime('%Y%m%d%H%M')}",
        "pr_number": args.pr,
        "started_at": _now_utc().isoformat(),
        "outcome": "in_progress",
    }
    state.setdefault("sessions", []).append(session_entry)

    # Write repo variable: last session start
    _upsert_repo_var(VAR_LAST_START, session_entry["started_at"])

    _save_state(state)
    _append_log({"event": "session_start", **session_entry})
    print(f"✅ Session started: {session_entry['session']}", file=sys.stderr)
    return 0


def cmd_end(args: argparse.Namespace) -> int:
    """Record session end; update state."""
    state = _load_state()

    # Update the most recent in-progress session
    sessions = state.get("sessions", [])
    for s in reversed(sessions):
        if s.get("outcome") == "in_progress" and (
            not args.session or s.get("session") == args.session
        ):
            s["outcome"] = args.outcome
            s["ended_at"] = _now_utc().isoformat()
            break

    # Apply default inter-session cooldown (prevents rapid retries)
    cooldown_mins = state.get("cooldown_minutes", DEFAULT_COOLDOWN_MINUTES)
    state = set_cooldown(state, cooldown_mins, reason="normal_end")

    _save_state(state)
    _append_log({"event": f"session_end_{args.outcome}", "session": args.session})
    print(f"✅ Session ended ({args.outcome}). Next session safe after {cooldown_mins} min.", file=sys.stderr)
    return 0


def cmd_hit429(args: argparse.Namespace) -> int:
    """Record a 429 hit, set extended cooldown, post PR comment."""
    state = _load_state()
    state["hit429_count"] = state.get("hit429_count", 0) + 1
    hit_count = state["hit429_count"]

    reset_mins = args.reset_minutes or 365  # default: ~6h if unknown
    cooldown_mins = reset_mins + POST_429_BUFFER_MINUTES
    state = set_cooldown(state, cooldown_mins, reason="429")

    _upsert_repo_var(VAR_HIT_COUNT, str(hit_count))

    # Update most recent session outcome
    for s in reversed(state.get("sessions", [])):
        if s.get("outcome") == "in_progress":
            s["outcome"] = "rate_limited"
            s["ended_at"] = _now_utc().isoformat()
            break

    _save_state(state)
    _append_log({"event": "429_hit", "session": args.session, "hit_count": hit_count,
                 "reset_minutes": reset_mins, "cooldown_minutes": cooldown_mins})

    # Post PR comment with cooldown timer
    if args.pr:
        body = _post_429_body(
            pr_number=args.pr,
            session=args.session or "unknown",
            reset_minutes=reset_mins,
            cooldown_minutes=cooldown_mins,
            hit_count=hit_count,
            request_id=args.request_id or "",
            completed=[t.strip() for t in (args.completed or "").split(",") if t.strip()],
            pending=[t.strip() for t in (args.pending or "").split(",") if t.strip()],
        )
        _post_or_update_pr_comment(args.pr, body, "<!-- codex-rate-limit-cooldown -->")

    safe_after = (_now_utc() + timedelta(minutes=cooldown_mins)).strftime("%H:%MZ")
    print(f"\n🔴 429 recorded. Cooldown set: {cooldown_mins} min. Safe after {safe_after}", file=sys.stderr)
    return 0


def cmd_warn(args: argparse.Namespace) -> int:
    """Post a pre-warning comment to a PR when budget is running low."""
    state = _load_state()
    session_count = _sessions_this_week(state)
    hit_count = state.get("hit429_count", 0)
    cooldown_mins = state.get("cooldown_minutes", DEFAULT_COOLDOWN_MINUTES)

    # Set a soft cooldown even for pre-warning
    state = set_cooldown(state, cooldown_mins, reason="prewarning")
    _save_state(state)

    if args.pr:
        body = _pre_warning_body(
            pr_number=args.pr,
            session_count=session_count,
            hit_count=hit_count,
            cooldown_minutes=cooldown_mins,
            session=args.session or "",
        )
        _post_or_update_pr_comment(args.pr, body, "<!-- codex-rate-limit-prewarning -->")
        print(f"✅ Pre-warning posted to PR #{args.pr}", file=sys.stderr)
    else:
        print("⚠️  --pr required to post comment", file=sys.stderr)

    return 0


def cmd_post_cooldown(args: argparse.Namespace) -> int:
    """Post a cooldown comment directly (without a 429 error payload)."""
    state = _load_state()
    cooldown_mins = args.cooldown_minutes or state.get("cooldown_minutes", DEFAULT_COOLDOWN_MINUTES)
    state = set_cooldown(state, cooldown_mins, reason="manual")
    _save_state(state)

    if args.pr:
        body = _post_429_body(
            pr_number=args.pr,
            session=args.session or "manual",
            reset_minutes=cooldown_mins,
            cooldown_minutes=cooldown_mins,
            hit_count=state.get("hit429_count", 0),
        )
        _post_or_update_pr_comment(args.pr, body, "<!-- codex-rate-limit-cooldown -->")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Check current cooldown status."""
    state = _load_state()
    status = cooldown_status(state)

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        _print_check(status, state)

    if status["active"]:
        return 1
    return 0


def cmd_sync_vars(args: argparse.Namespace) -> int:
    """Sync local state to repo variables."""
    state = _load_state()
    ok = True
    ok &= _upsert_repo_var(VAR_COOLDOWN_UNTIL, state.get("cooldown_until_utc") or "none")
    ok &= _upsert_repo_var(VAR_HIT_COUNT, str(state.get("hit429_count", 0)))
    ok &= _upsert_repo_var(VAR_COOLDOWN_MINS, str(state.get("cooldown_minutes", DEFAULT_COOLDOWN_MINUTES)))
    return 0 if ok else 1


def _print_check(status: dict, state: dict) -> None:
    now = _now_utc().strftime("%Y-%m-%dT%H:%MZ")
    print(f"\n{'═'*58}")
    print(f"  ⏱️  Rate-Limit Cooldown Status — {now}")
    print(f"{'═'*58}\n")

    print(f"  {status['message']}")
    if status["active"]:
        mins = status["mins_remaining"]
        until = status.get("cooldown_until_utc", "?")
        bar_filled = min(20, int(20 * (1 - mins / max(state.get("cooldown_minutes", 30), 1))))
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        print(f"\n  Cooldown progress:  [{bar}]  {mins} min remaining")
        print(f"  Safe to retry:      {until}")
        print(f"  Data source:        {status.get('source', 'local')}")
        print()
        print("  To retry (after cooldown):")
        print("     python3 scripts/ci/rate_limit_cooldown.py check")
        print("     python3 scripts/ci/push_conflict_resolver.py")
        print("     python3 scripts/ci/rate_limit_handler.py --resolve")
    else:
        sw = status.get("session_count_this_week", 0)
        h = status.get("hit429_count", 0)
        print(f"\n  Sessions this week: {sw}")
        print(f"  Prior 429 hits:     {h}")
        if sw >= WARNING_SESSION_COUNT:
            print(f"\n  ⚠️  {sw} sessions this week — approaching limit. Observe cooldown gaps.")
    print(f"\n{'═'*58}\n")


# ── Entry point ─────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # start
    ps = sub.add_parser("start", help="Record session start; block if cooldown active")
    ps.add_argument("--pr", type=int, default=0)
    ps.add_argument("--session", default="")
    ps.add_argument("--force", action="store_true", help="Start even if cooldown active")

    # end
    pe = sub.add_parser("end", help="Record session end")
    pe.add_argument("--session", default="")
    pe.add_argument("--outcome", default="ok", choices=["ok", "partial", "failed", "rate_limited"])

    # hit429
    ph = sub.add_parser("hit429", help="Record a 429 hit, set cooldown, post PR comment")
    ph.add_argument("--pr", type=int, default=0)
    ph.add_argument("--session", default="")
    ph.add_argument("--reset-minutes", type=int, default=0,
                    help="Minutes until rate limit resets (from error message)")
    ph.add_argument("--request-id", default="")
    ph.add_argument("--completed", default="", help="Comma-separated completed tasks")
    ph.add_argument("--pending", default="", help="Comma-separated pending tasks")

    # warn
    pw = sub.add_parser("warn", help="Post pre-warning PR comment (before hitting limit)")
    pw.add_argument("--pr", type=int, default=0)
    pw.add_argument("--session", default="")
    pw.add_argument("--budget-pct", type=int, default=70,
                    help="Estimated budget % used (for comment context)")

    # post-cooldown
    pc = sub.add_parser("post-cooldown", help="Post cooldown timer comment manually")
    pc.add_argument("--pr", type=int, default=0)
    pc.add_argument("--session", default="")
    pc.add_argument("--cooldown-minutes", type=int, default=0)

    # check
    pck = sub.add_parser("check", help="Check current cooldown status")
    pck.add_argument("--json", action="store_true", dest="json", help="JSON output")

    # sync-vars
    sub.add_parser("sync-vars", help="Sync local state to repo variables")

    return p


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    dispatch = {
        "start": cmd_start,
        "end": cmd_end,
        "hit429": cmd_hit429,
        "warn": cmd_warn,
        "post-cooldown": cmd_post_cooldown,
        "check": cmd_check,
        "sync-vars": cmd_sync_vars,
    }
    handler = dispatch.get(args.cmd)
    if not handler:
        parser.print_help()
        return 2
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
