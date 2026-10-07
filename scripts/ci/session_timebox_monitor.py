#!/usr/bin/env python3
"""Time-boxed session monitor for a 60-minute Copilot coding session.

This utility keeps an eye on the active coding session and warns the primary
agent when the remaining time enters the final 5-10 minute window. At that point
it prints the wrap/push checklist and writes a continuation prompt file so a
follow-up session can continue without losing context.

Example:
    python scripts/ci/session_timebox_monitor.py --limit-minutes 60 --warning-window 10
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_LIMIT_MINUTES = 60
DEFAULT_WARNING_WINDOW_MINUTES = 10
DEFAULT_POLL_SECONDS = 30
DEFAULT_PROMPT_PATH = Path(".codex/continuation_prompt.md")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_branch() -> str:
    return run_git(["branch", "--show-current"]) or "detached-head"


def get_status_summary() -> str:
    return run_git(["status", "--short", "--branch"]) or "git status unavailable"


def get_repo_slug() -> str:
    remote = run_git(["remote", "get-url", "origin"]) or ""
    remote = remote.rstrip("/")
    if remote.endswith(".git"):
        remote = remote[:-4]
    if ":" in remote and "//" not in remote:
        remote = remote.split(":", 1)[1]
    if remote.startswith("https://github.com/"):
        remote = remote.removeprefix("https://github.com/")
    elif remote.startswith("git@github.com:"):
        remote = remote.removeprefix("git@github.com:")
    return remote.strip()


def build_prompt(branch: str, repo: str, started_at: datetime, remaining: timedelta, status_summary: str) -> str:
    deadline = started_at + timedelta(minutes=DEFAULT_LIMIT_MINUTES)
    prompt = f"""# Continuation Prompt for the Active Session

**Status:** Time-box reached; wrap and push before continuing.
**Branch:** `{branch}`
**Repository:** `{repo}`
**Session started:** {started_at.isoformat().replace('+00:00', 'Z')}
**Planned deadline:** {deadline.isoformat().replace('+00:00', 'Z')}
**Remaining before limit:** {remaining}

## Summarize current state
- The active session reached its time box and should be wrapped up now.
- Preserve the branch state, run a final sanity check, and push the current work.
- If additional work remains, continue from this note in the next session.

## What to do now
1. Review the current diff and verify that the work is in a safe state.
2. `git status --short --branch`
3. `git add -A`
4. `git commit -m "WIP: session wrap at <time>"` if the work is not ready to merge.
5. `git push`
6. If more work is still needed, continue from the checklist below in the next session.

## Current branch status
```text
{status_summary}
```

## Remaining work / next session checklist
- [ ] Confirm the migration or fix is complete enough for the next handoff.
- [ ] Capture any unresolved blockers, build/test failures, or manual follow-ups.
- [ ] Re-run the narrow validation relevant to the current branch.
- [ ] State the next command or next PR to open after the handoff.

## Suggested handoff message
@copilot continue from the current branch `{branch}` in `{repo}`.
The prior session reached its time box. Preserve the current work, push any WIP,
then continue from the remaining instructions in this prompt.
"""
    return prompt


def write_prompt(path: Path, branch: str, repo: str, started_at: datetime, remaining: timedelta, status_summary: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_prompt(branch, repo, started_at, remaining, status_summary),
        encoding="utf-8",
    )


def warn_and_prepare(started_at: datetime, limit_minutes: int, warning_window_minutes: int, prompt_path: Path) -> None:
    repo = get_repo_slug() or "unknown/repo"
    branch = get_branch()
    status_summary = get_status_summary()
    remaining = timedelta(minutes=limit_minutes)
    print("\n============================================================")
    print("SESSION TIMEBOX WARNING")
    print("============================================================")
    print(f"Remaining time is within the final {warning_window_minutes} minutes of the {limit_minutes}-minute budget.")
    print("Wrap the work, run a final git status, push the branch, and prepare a handoff if more work remains.")
    print("\nSuggested actions:")
    print("  1. git status --short --branch")
    print("  2. git add -A")
    print("  3. git commit -m \"WIP: session wrap\"")
    print("  4. git push")
    print("  5. Post or save a continuation prompt for the next session")
    print("\nCurrent branch:", branch)
    print("Repository:", repo)
    print("============================================================\n")

    write_prompt(prompt_path, branch, repo, started_at, remaining, status_summary)
    print(f"Continuation prompt written to: {prompt_path}")


def monitor(limit_minutes: int, warning_window_minutes: int, poll_seconds: int, prompt_path: Path, once: bool) -> int:
    started_at = utc_now()
    deadline = started_at + timedelta(minutes=limit_minutes)
    warning_trigger = timedelta(minutes=warning_window_minutes)
    warned = False

    while True:
        now = utc_now()
        remaining = deadline - now
        if remaining <= timedelta(0):
            print(f"\nSession limit reached at {deadline.isoformat().replace('+00:00', 'Z')}. Please wrap and push now.")
            if prompt_path.exists():
                print(f"The continuation prompt is available at {prompt_path}.")
            return 0

        if remaining <= warning_trigger and not warned:
            warned = True
            warn_and_prepare(started_at, limit_minutes, warning_window_minutes, prompt_path)
            if once:
                return 0

        if once:
            remaining_human = max(remaining, timedelta(0))
            print(f"Time remaining: {remaining_human} (warning window: {warning_trigger})")
            return 0

        time.sleep(poll_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Warn the primary agent before a 60-minute session limit expires.")
    parser.add_argument("--limit-minutes", type=int, default=DEFAULT_LIMIT_MINUTES, help="Total session window in minutes (default: 60)")
    parser.add_argument("--warning-window", type=int, default=DEFAULT_WARNING_WINDOW_MINUTES, help="Warn when only this many minutes remain (default: 10)")
    parser.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS, help="Seconds between checks (default: 30)")
    parser.add_argument("--prompt-path", type=Path, default=DEFAULT_PROMPT_PATH, help="Path to write the continuation prompt file")
    parser.add_argument("--once", action="store_true", help="Print the current state once and exit without waiting for the deadline")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.limit_minutes <= 0:
        print("--limit-minutes must be > 0", file=sys.stderr)
        raise SystemExit(2)
    if args.warning_window <= 0 or args.warning_window > args.limit_minutes:
        print("--warning-window must be between 1 and --limit-minutes", file=sys.stderr)
        raise SystemExit(2)
    if args.poll_seconds <= 0:
        print("--poll-seconds must be > 0", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(monitor(args.limit_minutes, args.warning_window, args.poll_seconds, args.prompt_path, args.once))
