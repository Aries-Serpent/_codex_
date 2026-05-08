#!/usr/bin/env python3
"""admin_action_probe.py — Generic admin-action gap probe and issue manager.

Probes a GitHub API endpoint and creates/updates/closes a GitHub issue
depending on whether the probe succeeds or fails.  Designed to be
reproducible for any admin-action gap in this repository.

USAGE
-----
  # Probe T-03 security_events scope
  python3 scripts/ci/admin_action_probe.py \\
    --gap-id T-03 \\
    --probe-url "https://api.github.com/repos/Aries-Serpent/_codex_/code-scanning/alerts?per_page=1" \\
    --expected-status 200 \\
    --issue-title "[T-03] CODEX_MASTER_KEY missing security_events scope" \\
    --fix-steps-file docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md \\
    --repo Aries-Serpent/_codex_ \\
    --assignee mbaetiong

  # Probe only (no issue management — just print result)
  python3 scripts/ci/admin_action_probe.py \\
    --gap-id T-03 \\
    --probe-url "..." \\
    --probe-only

  # Close an existing gap issue (after admin confirms fix)
  python3 scripts/ci/admin_action_probe.py \\
    --gap-id T-03 \\
    --probe-url "..." \\
    --close-if-ok

ENVIRONMENT
-----------
  GH_TOKEN    GitHub token — must have `repo` scope for issue CRUD.
              For security_events probe: must also have `security_events` scope.

EXIT CODES
----------
  0   Gap closed (probe returned expected status)
  1   Gap still open (probe returned failure status)
  2   Inconclusive (unexpected HTTP status)
  3   Script error (missing args, auth failure, etc.)

HOW TO ADD A NEW ADMIN-ACTION GAP
----------------------------------
  1. Identify the API endpoint that distinguishes "gap open" from "gap closed".
  2. Create .github/workflows/admin-action-<gap-id>.yml calling
     admin-action-notifier.yml with your gap parameters.
  3. Optionally call this script directly in a workflow step for shell-level
     exit-code gating.
  4. Document the gap in .codex/docs/ADMIN_ACTION_WORKFLOW_PATTERN.md.

See .codex/docs/ADMIN_ACTION_WORKFLOW_PATTERN.md for the full pattern guide.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# GitHub API helpers
# ─────────────────────────────────────────────────────────────────────────────

def _gh_token() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("❌  GH_TOKEN / GITHUB_TOKEN is not set", file=sys.stderr)
        sys.exit(3)
    return token


def _gh_request(
    method: str,
    url: str,
    token: str,
    payload: Optional[dict] = None,
) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "admin_action_probe/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read()) if resp.headers.get("Content-Type", "").startswith("application/json") else {}
            return resp.status, body
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except Exception:
            body = {}
        return exc.code, body


def _api_url(repo: str, path: str) -> str:
    return f"https://api.github.com/repos/{repo}/{path.lstrip('/')}"


# ─────────────────────────────────────────────────────────────────────────────
# Probe
# ─────────────────────────────────────────────────────────────────────────────

def probe(probe_url: str, expected_status: int, token: str) -> tuple[Optional[bool], int, str]:
    """Probe the URL and return (gap_closed, http_status, message).

    Returns:
        True   — gap closed (probe returned expected_status)
        False  — gap open (probe returned 401/403)
        None   — inconclusive (unexpected status)
    """
    status, body = _gh_request("GET", probe_url, token)
    message = body.get("message", "(no message)")
    if status == expected_status:
        return True, status, message
    if status in (401, 403):
        return False, status, message
    return None, status, message


# ─────────────────────────────────────────────────────────────────────────────
# Issue management
# ─────────────────────────────────────────────────────────────────────────────

def _find_open_issue(repo: str, title: str, label: str, token: str) -> Optional[dict]:
    status, data = _gh_request(
        "GET",
        f"https://api.github.com/repos/{repo}/issues?state=open&labels={label}&per_page=50",
        token,
    )
    if status != 200 or not isinstance(data, list):
        return None
    return next((i for i in data if i.get("title") == title), None)


def _ensure_label(repo: str, label: str, token: str) -> None:
    _gh_request("POST", f"https://api.github.com/repos/{repo}/labels", token, {
        "name": label, "color": "e11d48",
        "description": "Requires manual admin action to unblock CI automation",
    })


def build_issue_body(
    gap_id: str,
    http_status: int,
    api_message: str,
    fix_steps: str,
    probe_url: str,
) -> str:
    ts = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    return "\n".join([
        f"## ⚠️ Admin Action Required — {gap_id}",
        "",
        f"**Detected:** `{ts}`",
        f"**Probe:** `GET {probe_url}`",
        f"**Result:** HTTP `{http_status}` — `{api_message}`",
        "",
        fix_steps,
        "",
        "---",
        f"_Auto-managed by `admin_action_probe.py` · Gap: `{gap_id}`_",
        f"_Last checked: {ts}_",
    ])


def create_or_update_issue(
    repo: str,
    title: str,
    body: str,
    label: str,
    assignee: str,
    token: str,
) -> int:
    _ensure_label(repo, label, token)
    existing = _find_open_issue(repo, title, label, token)
    if existing:
        issue_num = existing["number"]
        _gh_request("PATCH", f"https://api.github.com/repos/{repo}/issues/{issue_num}", token, {"body": body})
        print(f"↩️  Updated existing issue #{issue_num} for '{title}'")
        return issue_num
    status, data = _gh_request("POST", f"https://api.github.com/repos/{repo}/issues", token, {
        "title": title, "body": body, "labels": [label], "assignees": [assignee],
    })
    if status not in (200, 201):
        print(f"❌  Failed to create issue: HTTP {status}", file=sys.stderr)
        sys.exit(3)
    issue_num = data["number"]
    print(f"✅ Created issue #{issue_num}: {data.get('html_url', '')}")
    return issue_num


def close_issue(repo: str, title: str, label: str, gap_id: str, token: str) -> None:
    existing = _find_open_issue(repo, title, label, token)
    if not existing:
        print(f"ℹ️  No open issue found for '{title}' — nothing to close")
        return
    issue_num = existing["number"]
    _gh_request("POST", f"https://api.github.com/repos/{repo}/issues/{issue_num}/comments", token, {
        "body": "\n".join([
            f"## ✅ {gap_id} Gap Closed",
            "",
            "Probe returned the expected HTTP status — the admin action has been completed.",
            "",
            f"_Auto-resolved by `admin_action_probe.py` at {datetime.now(tz=timezone.utc).isoformat(timespec='seconds')}_",
        ])
    })
    _gh_request("PATCH", f"https://api.github.com/repos/{repo}/issues/{issue_num}", token, {
        "state": "closed", "state_reason": "completed",
    })
    print(f"✅ Auto-closed issue #{issue_num} for {gap_id}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--gap-id",        required=True,  help="Short gap identifier, e.g. T-03")
    p.add_argument("--probe-url",     required=True,  help="Full GitHub API URL to GET-probe")
    p.add_argument("--expected-status", type=int, default=200,
                   help="HTTP status code that means the gap is CLOSED (default: 200)")
    p.add_argument("--issue-title",   default="",     help="GitHub issue title (unique per gap)")
    p.add_argument("--fix-steps",     default="",     help="Inline markdown fix steps for the issue body")
    p.add_argument("--fix-steps-file", default="",
                   help="Path to a markdown file whose content is used as fix steps")
    p.add_argument("--repo",          default=os.environ.get("GITHUB_REPOSITORY", ""),
                   help="owner/repo (default: $GITHUB_REPOSITORY)")
    p.add_argument("--assignee",      default="mbaetiong",
                   help="GitHub login to assign the issue to (default: mbaetiong)")
    p.add_argument("--label",         default="admin-action-required",
                   help="Issue label (default: admin-action-required)")
    p.add_argument("--probe-only",    action="store_true",
                   help="Only probe — do not create/update/close issues")
    p.add_argument("--close-if-ok",   action="store_true",
                   help="When probe OK, close any open issue for this gap")
    p.add_argument("--dry-run",       action="store_true",
                   help="Print actions without making API calls")
    return p


def main() -> int:
    args = _build_parser().parse_args()
    token = _gh_token()

    if not args.repo:
        print("❌  --repo is required (or set $GITHUB_REPOSITORY)", file=sys.stderr)
        return 3

    # ── Probe ───────────────────────────────────────────────────────────────
    print(f"🔍 Probing {args.gap_id}: GET {args.probe_url}")
    gap_closed, http_status, api_message = probe(args.probe_url, args.expected_status, token)

    status_icon = "✅" if gap_closed is True else ("⚠️" if gap_closed is False else "ℹ️")
    print(f"{status_icon} {args.gap_id}: HTTP {http_status} — {api_message}")

    if args.probe_only:
        if gap_closed is True:
            return 0
        if gap_closed is False:
            return 1
        return 2

    # ── Load fix steps ───────────────────────────────────────────────────────
    fix_steps = args.fix_steps
    if args.fix_steps_file and os.path.isfile(args.fix_steps_file):
        with open(args.fix_steps_file, encoding="utf-8") as fh:
            fix_steps = fh.read()
    if not fix_steps:
        fix_steps = f"_No fix steps provided. See issue title for gap `{args.gap_id}`._"

    issue_title = args.issue_title or f"[{args.gap_id}] Admin action required"

    # ── Gap OPEN → create/update issue ──────────────────────────────────────
    if gap_closed is False:
        body = build_issue_body(args.gap_id, http_status, api_message, fix_steps, args.probe_url)
        if args.dry_run:
            print(f"[dry-run] Would create/update issue: '{issue_title}'")
        else:
            create_or_update_issue(args.repo, issue_title, body, args.label, args.assignee, token)
        return 1

    # ── Gap CLOSED → optionally close issue ─────────────────────────────────
    if gap_closed is True:
        if args.close_if_ok:
            if args.dry_run:
                print(f"[dry-run] Would close issue: '{issue_title}'")
            else:
                close_issue(args.repo, issue_title, args.label, args.gap_id, token)
        return 0

    # ── Inconclusive ─────────────────────────────────────────────────────────
    print(f"ℹ️  {args.gap_id}: probe inconclusive (HTTP {http_status}) — no issue action taken")
    return 2


if __name__ == "__main__":
    sys.exit(main())
