#!/usr/bin/env python3
"""
Phase 22.1 — Automated Stale Session Detection & Archive

Scans local session files and (optionally) the GitHub Pull Requests REST API for
sessions that remain ``active`` past their PR's merge date, then automatically
invokes ``archive_session()`` to create a tombstone and mark them archived.

Usage
-----
    # Dry-run: report what would be archived
    python scripts/stale_session_detector.py --dry-run

    # Archive everything older than 30 days
    python scripts/stale_session_detector.py

    # Stricter: archive sessions older than 7 days
    python scripts/stale_session_detector.py --max-age-days 7

    # Also cross-reference GitHub PR merge dates (requires GITHUB_TOKEN)
    python scripts/stale_session_detector.py --check-prs
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from scripts.ci._token_resolver import get_token


# Allow running from repo root without installing the package
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.session_tracker import (  # noqa: E402
    STATUS_ARCHIVED,
    STATUS_COMPLETED,
    archive_session,
    list_sessions,
)

# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _pr_merged_at(pr_number: int) -> Optional[datetime]:
    """Return merge timestamp for a GitHub PR using the REST API.

    Requires a ``GITHUB_TOKEN`` environment variable.  Returns ``None`` if the
    token is missing, the PR is not found, or the PR has not been merged.
    """
    token = os.environ.get("GITHUB_TOKEN") or get_token(required_elevated=True)[0]
    if not token:
        return None

    try:
        import urllib.request

        repo = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 — localhost or GH
            data = json.loads(resp.read())
        return _parse_iso(data.get("merged_at"))
    except Exception:  # noqa: BLE001
        return None


# ── core detection logic ──────────────────────────────────────────────────────

def detect_stale_sessions(
    max_age_days: int = 30,
    check_prs: bool = False,
) -> list[dict[str, Any]]:
    """Return session dicts that should be archived.

    A session is considered stale when **any** of the following is true:

    * Its status is ``active`` and it was started more than *max_age_days* ago.
    * ``check_prs=True``, the session has a ``pr_number`` field, and that PR
      has already been merged on GitHub.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    stale: list[dict[str, Any]] = []

    all_sessions = list_sessions(limit=500)
    for session in all_sessions:
        status = session.get("status", "")
        if status in (STATUS_COMPLETED, STATUS_ARCHIVED):
            continue  # already handled

        started_at = _parse_iso(session.get("started_at"))

        # Age-based staleness
        if started_at and started_at < cutoff:
            session["_stale_reason"] = (
                f"active session started {started_at.date()} "
                f"({(datetime.now(timezone.utc) - started_at).days}d ago) "
                f"exceeds max_age_days={max_age_days}"
            )
            stale.append(session)
            continue

        # PR-merge-based staleness
        if check_prs and session.get("pr_number"):
            merged = _pr_merged_at(session["pr_number"])
            if merged:
                session["_stale_reason"] = (
                    f"associated PR #{session['pr_number']} merged at {merged.date()}"
                )
                stale.append(session)

    return stale


def archive_stale_sessions(
    max_age_days: int = 30,
    check_prs: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[str]:
    """Detect and archive stale sessions; return list of archived session IDs.

    Args:
        max_age_days: Archive active sessions older than this many days.
        check_prs: Cross-reference GitHub PR merge dates (requires GITHUB_TOKEN).
        dry_run: Preview what would be archived without writing any files.
        verbose: Print progress to stdout (disabled by default so callers that
            import this as a library do not receive unexpected output).
    """
    stale = detect_stale_sessions(max_age_days=max_age_days, check_prs=check_prs)

    if not stale:
        if verbose:
            print("✅  No stale sessions found.")
        return []

    archived_ids: list[str] = []
    for session in stale:
        sid = session["session_id"]
        reason = session.get("_stale_reason", "stale session auto-archived")
        pr = session.get("pr_number")

        if dry_run:
            if verbose:
                print(f"[DRY RUN] Would archive: {sid}")
                print(f"          Reason: {reason}")
        else:
            archive_session(session_id=sid, reason=reason, pr_number=pr)
            if verbose:
                print(f"🗄  Archived: {sid}")
                print(f"   Reason: {reason}")

        archived_ids.append(sid)

    return archived_ids


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=30,
        help="Archive active sessions older than N days (default: 30)",
    )
    parser.add_argument(
        "--check-prs",
        action="store_true",
        default=False,
        help="Cross-reference GitHub PR merge dates (requires GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report stale sessions without archiving them",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        metavar="PATH",
        help="Write detection results to a JSON file",
    )

    args = parser.parse_args()

    # Auto-enable --check-prs when GITHUB_TOKEN is available in the environment
    # (unblocked by COPILOT_AGENT_AUTH_ENABLED=true token delegation)
    check_prs = args.check_prs or bool(
        os.environ.get("GITHUB_TOKEN") or get_token(required_elevated=True)[0]
    )

    stale = detect_stale_sessions(
        max_age_days=args.max_age_days,
        check_prs=check_prs,
    )

    if check_prs and not args.check_prs:
        print("ℹ️  --check-prs auto-enabled (GITHUB_TOKEN detected in environment)")

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "stale_count": len(stale),
                    "sessions": [
                        {
                            "session_id": s["session_id"],
                            "started_at": s.get("started_at"),
                            "status": s.get("status"),
                            "reason": s.get("_stale_reason", ""),
                            "pr_number": s.get("pr_number"),
                        }
                        for s in stale
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Results written to {args.output_json}")

    archived = archive_stale_sessions(
        max_age_days=args.max_age_days,
        check_prs=check_prs,
        dry_run=args.dry_run,
        verbose=True,
    )

    if args.dry_run:
        print(f"\nSummary: {len(stale)} stale session(s) detected (dry-run — no changes made).")
    else:
        print(f"\nSummary: {len(archived)} session(s) archived.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
