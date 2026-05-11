#!/usr/bin/env python3
"""Rate-Limit Handler for Copilot Cloud Agent sessions.

Detects ``user_weekly_rate_limited`` / ``429`` errors from the Copilot API,
saves a structured checkpoint so the next session can resume where the
rate-limited one left off, and posts a formatted PR comment containing:

  - Completed tasks ✅
  - In-progress task at interruption ⏳ (may be partial — verify before assuming done)
  - Pending tasks ❌ (carry forward to next session)
  - Rate-limit reset time and auto-retry instruction

Observed failure cascade (from PR #4389, runs 3476–3489):
  - 8 sessions fired in rapid succession (~15 min each) → all hit 429
  - Automated CI commits (chore(d00), chore(auth)) pushed during sessions
    → "Changes were pushed while working" push-conflict on top of rate-limit
  - ~15h gap (reset window), then 2 more sessions failed on push conflicts

Usage (CLI):
    python3 scripts/ci/rate_limit_handler.py \\
        --pr-number 4389 \\
        --error-json '{"code":"user_weekly_rate_limited","text":"...reset in 6 hours 5 minutes..."}' \\
        --completed "Fix CodeQL #13447,Resolve merge conflict" \\
        --in-progress "Fix CodeQL #13429" \\
        --pending "Update CHANGELOG,Run parallel_validation" \\
        --session S923

    # Read error JSON from stdin:
    echo "$ERROR_JSON" | python3 scripts/ci/rate_limit_handler.py --pr-number 4389 --stdin-error

    # Check existing checkpoint:
    python3 scripts/ci/rate_limit_handler.py --check

    # Mark resolved at session start:
    python3 scripts/ci/rate_limit_handler.py --resolve
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

CHECKPOINT_FILE = Path(".codex/rate_limit_checkpoint.json")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
GH_TOKEN = (
    os.environ.get("CODEX_MASTER_KEY")
    or os.environ.get("CODEX_BACKUP_KEY")
    or os.environ.get("GITHUB_TOKEN")
    or os.environ.get("GH_TOKEN")
    or ""
)

# Error codes / messages that indicate a weekly rate-limit (not per-minute)
_RATE_LIMIT_CODES: frozenset[str] = frozenset({
    "user_weekly_rate_limited",
    "rate_limit_exceeded",
    "ratelimited",
})
_RATE_LIMIT_PHRASES: tuple[str, ...] = (
    "weekly rate limit",
    "user_weekly_rate_limited",
    "exceeded your weekly",
    "rate limit exceeded",
    "reset in",
)

# Auto-generated files pushed by bots that trigger push conflicts
KNOWN_BOT_COMMIT_SUBJECTS: tuple[str, ...] = (
    "chore(d00): update session context digest",
    "chore(auth): write provenance session token",
    "chore(manifest): auto-refresh CODEX_MANIFEST.json",
    "chore(vars): sync .codex/agent_context.json",
    "fix(ci): universal baseline sweep",
)


# ── Detection helpers ───────────────────────────────────────────────────────────

def is_rate_limit_error(error_data: dict) -> bool:
    """Return True if *error_data* represents a weekly rate-limit response."""
    code = str(error_data.get("code", "")).lower()
    status = str(error_data.get("status", ""))
    text = (
        str(error_data.get("text", ""))
        + " "
        + str(error_data.get("message", ""))
    ).lower()
    return (
        code in _RATE_LIMIT_CODES
        or status == "429"
        or any(phrase in text for phrase in _RATE_LIMIT_PHRASES)
    )


def extract_reset_minutes(error_data: dict) -> int | None:
    """Parse 'reset in X hours Y minutes' from the error text/message."""
    text = str(error_data.get("text", "")) + " " + str(error_data.get("message", ""))
    m = re.search(
        r"reset in\s+(?:(\d+)\s+hours?\s*)?(?:(\d+)\s+minutes?)?",
        text,
        re.IGNORECASE,
    )
    if m and (m.group(1) or m.group(2)):
        hours = int(m.group(1) or 0)
        minutes = int(m.group(2) or 0)
        return hours * 60 + minutes
    return None


def format_retry_time(reset_minutes: int | None) -> str:
    if reset_minutes is None:
        return "unknown — check https://docs.github.com/copilot/concepts/rate-limits"
    reset_at = datetime.now(timezone.utc) + timedelta(minutes=reset_minutes)
    return f"{reset_at.strftime('%Y-%m-%dT%H:%MZ')} (~{reset_minutes} min from now)"


# ── Checkpoint I/O ─────────────────────────────────────────────────────────────

def save_checkpoint(
    pr_number: int,
    error_data: dict,
    completed: list[str],
    in_progress: list[str],
    pending: list[str],
    session: str = "",
) -> dict:
    """Persist rate-limit state to *CHECKPOINT_FILE* and return the record."""
    reset_minutes = extract_reset_minutes(error_data)
    checkpoint: dict = {
        "schema_version": "1.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pr_number": pr_number,
        "session": session or f"rl-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        "rate_limit": {
            "code": error_data.get("code", "unknown"),
            "request_id": (
                error_data.get("ghRequestId")
                or error_data.get("request_id", "")
            ),
            "reset_minutes": reset_minutes,
            "retry_after_utc": format_retry_time(reset_minutes),
            # Keep the raw payload so callers can extract extra fields
            "raw_error": {
                k: v for k, v in error_data.items()
                if k not in {"stack"}  # omit stack trace — too large
            },
        },
        "tasks": {
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
        },
        "push_conflict_risk": {
            "description": (
                "Automated CI commits (chore(d00)/chore(auth)/chore(manifest)) "
                "may have pushed to the branch during the rate-limited session. "
                "Run push_conflict_resolver.py before next session commits."
            ),
            "known_bot_patterns": list(KNOWN_BOT_COMMIT_SUBJECTS),
            "resolver_script": "python3 scripts/ci/push_conflict_resolver.py",
        },
        "resolution": "pending",
    }
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
    print(f"✅ Checkpoint saved → {CHECKPOINT_FILE}", file=sys.stderr)

    # Also record in cooldown manager so the cross-session cooldown timer fires.
    # This is a best-effort call — failures are logged but do not affect the checkpoint.
    try:
        import subprocess as _sp  # noqa: PLC0415
        _cmd = [
            sys.executable, "scripts/ci/rate_limit_cooldown.py", "hit429",
            "--session", checkpoint["session"],
        ]
        if pr_number:
            _cmd += ["--pr", str(pr_number)]
        if reset_minutes:
            _cmd += ["--reset-minutes", str(reset_minutes)]
        if completed:
            _cmd += ["--completed", ",".join(completed)]
        if pending:
            _cmd += ["--pending", ",".join(pending)]
        _sp.run(_cmd, check=False, timeout=20)  # noqa: S603
    except Exception as _exc:
        print(f"⚠️  cooldown manager call failed (non-fatal): {_exc}", file=sys.stderr)

    return checkpoint


def load_checkpoint() -> dict | None:
    """Load and return the checkpoint, or None if it doesn't exist / is corrupt."""
    if not CHECKPOINT_FILE.exists():
        return None
    try:
        return json.loads(CHECKPOINT_FILE.read_text())
    except Exception:
        return None


def mark_checkpoint_resolved(session: str = "") -> None:
    """Mark the current checkpoint as resolved (call at the start of a recovery session)."""
    cp = load_checkpoint()
    if cp:
        cp["resolution"] = "resolved"
        cp["resolved_at"] = datetime.now(timezone.utc).isoformat()
        if session:
            cp["resolved_by_session"] = session
        CHECKPOINT_FILE.write_text(json.dumps(cp, indent=2))
        print(f"✅ Checkpoint marked resolved: {CHECKPOINT_FILE}", file=sys.stderr)
    else:
        print("ℹ️  No checkpoint found to resolve.", file=sys.stderr)


# ── GitHub API ─────────────────────────────────────────────────────────────────

def _gh_api(method: str, path: str, body: dict | None = None) -> tuple[int, object]:
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-rate-limit-handler/1.1",
    }
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def post_pr_comment(pr_number: int, checkpoint: dict) -> bool:
    """Post (or update) a rate-limit checkpoint comment on the PR."""
    if not REPO or not GH_TOKEN:
        print(
            "⚠️  REPO/GH_TOKEN not set — skipping GitHub comment. "
            "Set GITHUB_REPOSITORY and CODEX_MASTER_KEY (or GITHUB_TOKEN).",
            file=sys.stderr,
        )
        return False

    rl = checkpoint["rate_limit"]
    tasks = checkpoint["tasks"]
    completed = tasks.get("completed", [])
    in_progress = tasks.get("in_progress", [])
    pending = tasks.get("pending", [])
    session = checkpoint.get("session", "")

    lines = [
        "<!-- codex-rate-limit-checkpoint -->",
        "## ⚡ Copilot Rate-Limit Checkpoint — Session Interrupted",
        "",
        "> **Root Cause:** Copilot Cloud Agent hit the weekly API rate limit mid-session  ",
        f"> **Request ID:** `{rl.get('request_id') or 'N/A'}`  ",
        f"> **Rate-limit resets:** `{rl.get('retry_after_utc', 'unknown')}`  ",
        f"> **Session:** `{session}`",
        "",
        "---",
        "",
        "### ✅ Completed before interruption",
    ]
    if completed:
        for t in completed:
            lines.append(f"- [x] {t}")
    else:
        lines.append("_None recorded — verify git log for actual commits._")

    lines += [
        "",
        "### ⏳ In-progress at interruption — **verify before assuming complete**",
    ]
    if in_progress:
        for t in in_progress:
            lines.append(f"- [ ] ⚠️  **{t}** — was mid-flight; check if fully committed")
    else:
        lines.append("_None recorded._")

    lines += [
        "",
        "### ❌ Not started — carry forward to next session",
    ]
    if pending:
        for t in pending:
            lines.append(f"- [ ] {t}")
    else:
        lines.append("_None recorded._")

    lines += [
        "",
        "---",
        "",
        "### ⚠️  Push Conflict Risk",
        "",
        "Automated CI commits (`chore(d00)`, `chore(auth)`, `chore(manifest)`) "
        "may have been pushed **during** the rate-limited session. Before the next "
        "agent session commits anything, run:",
        "",
        "```bash",
        "python3 scripts/ci/push_conflict_resolver.py",
        "```",
        "",
        "---",
        "",
        "### 🔄 Recovery Instructions",
        "",
        f"After `{rl.get('retry_after_utc', 'the reset time')}`, post the following comment to restart:",
        "",
        "```",
        f"@copilot Continue from rate-limit checkpoint on PR #{pr_number}.",
        "1. Load .codex/rate_limit_checkpoint.json",
        "2. Run: python3 scripts/ci/push_conflict_resolver.py",
        "3. Mark checkpoint resolved: python3 scripts/ci/rate_limit_handler.py --resolve",
        "4. Resume all pending tasks listed in the checkpoint",
        "```",
        "",
        f"_Checkpoint: `{CHECKPOINT_FILE}` · Generated: {checkpoint.get('created_at', '')}_",
    ]

    body = "\n".join(lines)
    marker = "<!-- codex-rate-limit-checkpoint -->"

    # Update existing comment rather than creating duplicates
    status, comments = _gh_api(
        "GET",
        f"/repos/{REPO}/issues/{pr_number}/comments?per_page=100",
    )
    existing_id: int | None = None
    if status == 200 and isinstance(comments, list):
        for c in comments:
            if marker in (c.get("body") or ""):
                existing_id = c["id"]
                break

    if existing_id:
        status, _ = _gh_api(
            "PATCH",
            f"/repos/{REPO}/issues/comments/{existing_id}",
            {"body": body},
        )
        verb = "updated"
    else:
        status, _ = _gh_api(
            "POST",
            f"/repos/{REPO}/issues/{pr_number}/comments",
            {"body": body},
        )
        verb = "posted"

    ok = status in (200, 201)
    print(
        f"{'✅' if ok else '❌'} GitHub comment {verb} (HTTP {status})",
        file=sys.stderr,
    )
    return ok


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--pr-number", type=int, default=0)
    p.add_argument(
        "--error-json",
        default="",
        help="JSON string of the Copilot error payload",
    )
    p.add_argument(
        "--stdin-error",
        action="store_true",
        help="Read error JSON from stdin instead of --error-json",
    )
    p.add_argument(
        "--completed",
        default="",
        help="Comma-separated completed tasks",
    )
    p.add_argument(
        "--in-progress",
        default="",
        help="Comma-separated tasks that were mid-flight at interruption",
    )
    p.add_argument(
        "--pending",
        default="",
        help="Comma-separated tasks not yet started",
    )
    p.add_argument("--session", default="", help="Session ID (e.g. S923)")
    p.add_argument(
        "--no-comment",
        action="store_true",
        help="Save checkpoint only — do not post GitHub comment",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Print existing checkpoint and exit",
    )
    p.add_argument(
        "--resolve",
        action="store_true",
        help="Mark existing checkpoint as resolved and exit",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    if args.check:
        cp = load_checkpoint()
        if cp:
            print(json.dumps(cp, indent=2))
        else:
            print("No checkpoint found.")
        return 0

    if args.resolve:
        mark_checkpoint_resolved(args.session)
        return 0

    # Parse error JSON
    error_data: dict = {}
    if args.stdin_error:
        raw = sys.stdin.read().strip()
        if raw:
            try:
                error_data = json.loads(raw)
            except json.JSONDecodeError:
                error_data = {"message": raw, "code": "parse_error"}
    elif args.error_json:
        try:
            error_data = json.loads(args.error_json)
        except json.JSONDecodeError:
            error_data = {"message": args.error_json, "code": "parse_error"}

    if error_data and not is_rate_limit_error(error_data):
        print(
            f"⚠️  Payload does not look like a rate-limit error "
            f"(code={error_data.get('code', '?')}). Saving checkpoint anyway.",
            file=sys.stderr,
        )

    if not args.pr_number:
        print("❌ --pr-number is required when saving a checkpoint.", file=sys.stderr)
        return 1

    completed = [t.strip() for t in args.completed.split(",") if t.strip()]
    in_progress = [t.strip() for t in args.in_progress.split(",") if t.strip()]
    pending = [t.strip() for t in args.pending.split(",") if t.strip()]

    checkpoint = save_checkpoint(
        args.pr_number, error_data, completed, in_progress, pending, args.session
    )

    if not args.no_comment:
        post_pr_comment(args.pr_number, checkpoint)

    return 0


if __name__ == "__main__":
    sys.exit(main())
