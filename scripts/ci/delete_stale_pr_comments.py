#!/usr/bin/env python3
"""
Delete stale / redundant github-actions[bot] PR comments.

The script fetches all comments on a given PR, classifies each one using a
set of configurable rules, and deletes those that are no longer useful.

Usage
-----
    # Dry-run (prints what *would* be deleted, no changes)
    python scripts/ci/delete_stale_pr_comments.py --pr-number 4289 --dry-run

    # Live run — delete stale comments
    python scripts/ci/delete_stale_pr_comments.py --pr-number 4289

    # Also clean up CI-Rescue comments for old commit SHAs
    python scripts/ci/delete_stale_pr_comments.py --pr-number 4289 --include-rescue

Environment
-----------
    GITHUB_TOKEN   Required.  Must have *issues: write* scope.
                   In a GitHub Actions workflow add:
                       permissions:
                         issues: write
                   to the job that runs this script.

Exit codes
----------
    0  Success (or dry-run completed).
    1  Error (missing token, API failure, etc.).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "Aries-Serpent")
REPO = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_").split("/")[-1]
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"

# Authors whose comments this script is allowed to delete.
# Only bot / machine accounts are listed here on purpose — we never auto-delete
# comments written by human maintainers.
DELETABLE_AUTHORS: set[str] = {
    "github-actions[bot]",
    "copilot-swe-agent[bot]",
    "dependabot[bot]",
}


# ---------------------------------------------------------------------------
# Stale-comment rules
# ---------------------------------------------------------------------------
# Each rule is a dict with:
#   pattern   str | re.Pattern  — matched against the comment body
#   strategy  str               — how to handle matched comments (see below)
#   label     str               — human-readable name used in output
#
# Strategies
# ----------
# "delete_all"       Delete every comment that matches, regardless of position.
# "keep_latest"      Keep the single newest comment that matches; delete the rest.
# "keep_latest_sha"  Like keep_latest but groups by the commit SHA embedded in
#                    the comment (used for per-commit CI Rescue messages).
# "delete_if_resolved"  Delete only when a matching "resolved" pattern also
#                    exists in the PR (implies the condition has been cleared).

_WEC_PLAN_HEADING = "## ⚙️ Workflow Execution Gate — Execution Plan"
_REBASE_REQUIRED = "BRANCH_REBASE_REQUIRED"
_REBASE_RESOLVED = "Branch Rebase Resolved"

STALE_RULES: list[dict[str, Any]] = [
    # 1. Workflow Execution Gate plans — accumulate quickly; keep only newest
    {
        "label": "WEC Execution Plan (keep latest only)",
        "pattern": _WEC_PLAN_HEADING,
        "strategy": "keep_latest",
    },
    # 2. Branch-rebase-required notice — obsolete once branch is rebased
    {
        "label": "Branch Rebase Required (resolved)",
        "pattern": _REBASE_REQUIRED,
        "strategy": "delete_if_resolved",
        "resolved_by": _REBASE_RESOLVED,
    },
    # 3. Branch-rebase-resolved banner — purely informational; safe to remove
    {
        "label": "Branch Rebase Resolved banner",
        "pattern": _REBASE_RESOLVED,
        "strategy": "delete_all",
    },
    # 4. Follow-up prompt notification — one-shot; no ongoing value
    {
        "label": "Follow-up prompt generated notice",
        "pattern": "Follow-up prompt has been generated for this PR",
        "strategy": "delete_all",
    },
    # 5. Bare workflow-run link comment  (body is just "--- 🔗 Workflow run ---")
    {
        "label": "Bare workflow-run link",
        "pattern": re.compile(r"^\s*---\s*_.*Workflow run.*_\s*$", re.DOTALL),
        "strategy": "delete_all",
    },
    # 6. Cognitive pre-flight checklist — keep only the most recent one
    {
        "label": "Cognitive Pre-flight Checklist (keep latest only)",
        "pattern": "COGNITIVE PRE-FLIGHT CHECKLIST",
        "strategy": "keep_latest",
    },
    # 7. Pre-merge validation summary — keep only the most recent run result
    {
        "label": "Pre-Merge Validation Summary (keep latest only)",
        "pattern": "Pre-Merge Validation Summary",
        "strategy": "keep_latest",
    },
    # 8. Root-org validation result — keep only the most recent run result
    {
        "label": "Root Organization Validation (keep latest only)",
        "pattern": "Root Organization Validation",
        "strategy": "keep_latest",
    },
]

# CI-Rescue rule added separately so it can be toggled via --include-rescue
CI_RESCUE_RULE: dict[str, Any] = {
    "label": "CI Rescue (@copilot) for superseded commits (keep latest SHA)",
    "pattern": "CI Rescue — @copilot Fix Required",
    "strategy": "keep_latest_sha",
}

# SHA-extraction regex for CI Rescue comments
_SHA_RE = re.compile(
    r"[Cc]ommit[`\s]+([0-9a-f]{12,40})|sha[:\s]+([0-9a-f]{12,40})",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_all_comments(pr_number: int, token: str) -> list[dict[str, Any]]:
    """Return all issue comments on *pr_number* (handles pagination)."""
    comments: list[dict[str, Any]] = []
    url: str | None = f"{API_BASE}/issues/{pr_number}/comments?per_page=100"
    while url:
        resp = requests.get(url, headers=_headers(token), timeout=30)
        resp.raise_for_status()
        comments.extend(resp.json())
        # Follow Link: <next_url>; rel="next"
        link = resp.headers.get("Link", "")
        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = next_match.group(1) if next_match else None
    return comments


def _delete_comment(comment_id: int, token: str, dry_run: bool) -> bool:
    """Delete a single comment.  Returns True on success."""
    if dry_run:
        return True
    url = f"{API_BASE}/issues/comments/{comment_id}"
    resp = requests.delete(url, headers=_headers(token), timeout=30)
    return resp.status_code == 204


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------


def _matches(body: str, pattern: str | re.Pattern) -> bool:  # type: ignore[type-arg]
    if isinstance(pattern, re.Pattern):
        return bool(pattern.search(body))
    return pattern in body


def _extract_sha(body: str) -> str | None:
    m = _SHA_RE.search(body)
    if m:
        return m.group(1) or m.group(2)
    return None


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify_comments(
    comments: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> dict[int, str]:
    """
    Return a mapping of comment-id → reason for every comment that should be deleted.

    Comments are processed newest-first so "keep_latest" strategies can mark
    the first-seen (newest) as safe and flag everything else.
    """
    to_delete: dict[int, str] = {}

    for rule in rules:
        label = rule["label"]
        pattern = rule["pattern"]
        strategy = rule["strategy"]

        matched = [c for c in comments if _matches(c["body"], pattern)]
        if not matched:
            continue

        if strategy == "delete_all":
            for c in matched:
                to_delete[c["id"]] = label

        elif strategy == "keep_latest":
            # Sort descending by creation time; keep the first, delete the rest
            ordered = sorted(matched, key=lambda c: c["created_at"], reverse=True)
            for c in ordered[1:]:  # skip index 0 (newest)
                to_delete[c["id"]] = label

        elif strategy == "keep_latest_sha":
            # Group by SHA; within each SHA group keep newest, delete rest.
            # Also delete all entries for any SHA that is NOT the most recently
            # seen SHA across ALL groups (old commit SHAs are superseded).
            by_sha: dict[str, list[dict]] = {}
            no_sha: list[dict] = []
            for c in matched:
                sha = _extract_sha(c["body"])
                if sha:
                    by_sha.setdefault(sha[:12], []).append(c)
                else:
                    no_sha.append(c)

            # Determine the most recent SHA across all groups
            all_with_sha = [c for lst in by_sha.values() for c in lst]
            if all_with_sha:
                latest_sha_comment = max(all_with_sha, key=lambda c: c["created_at"])
                latest_sha = _extract_sha(latest_sha_comment["body"])
                latest_sha_key = latest_sha[:12] if latest_sha else None
            else:
                latest_sha_key = None

            for sha_key, group in by_sha.items():
                ordered_group = sorted(group, key=lambda c: c["created_at"], reverse=True)
                if sha_key == latest_sha_key:
                    # Keep the newest entry for the current SHA, delete rest
                    for c in ordered_group[1:]:
                        to_delete[c["id"]] = f"{label} (older entry for SHA {sha_key})"
                else:
                    # Entire SHA group is superseded — delete all
                    for c in ordered_group:
                        to_delete[c["id"]] = f"{label} (superseded SHA {sha_key})"

            # No-SHA matches: delete all (can't verify currency)
            for c in no_sha:
                to_delete[c["id"]] = f"{label} (no SHA found)"

        elif strategy == "delete_if_resolved":
            resolved_by = rule.get("resolved_by", "")
            is_resolved = any(_matches(c["body"], resolved_by) for c in comments)
            if is_resolved:
                for c in matched:
                    to_delete[c["id"]] = f"{label} (resolved)"

    return to_delete


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Delete stale github-actions[bot] comments from a PR.",
    )
    parser.add_argument("--pr-number", type=int, required=True, help="Pull-request number")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be deleted without making any API calls",
    )
    parser.add_argument(
        "--include-rescue",
        action="store_true",
        help="Also clean up CI-Rescue comments for superseded commit SHAs",
    )
    parser.add_argument(
        "--owner",
        default=OWNER,
        help=f"Repo owner (default: {OWNER})",
    )
    parser.add_argument(
        "--repo",
        default=REPO,
        help=f"Repo name (default: {REPO})",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN (or GH_TOKEN) must be set.", file=sys.stderr)
        return 1

    # Allow owner/repo override from CLI
    global OWNER, REPO, API_BASE  # noqa: PLW0603
    OWNER = args.owner
    REPO = args.repo
    API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"

    print(f"📋 Fetching comments for PR #{args.pr_number} …")
    try:
        comments = _get_all_comments(args.pr_number, token)
    except requests.HTTPError as exc:
        print(f"ERROR: Failed to fetch comments: {exc}", file=sys.stderr)
        return 1

    # Filter to only comments from allowed bot authors
    bot_comments = [c for c in comments if c["user"]["login"] in DELETABLE_AUTHORS]
    print(
        f"   Found {len(comments)} total comments, "
        f"{len(bot_comments)} from deletable bot accounts."
    )

    # Build the active rule set
    active_rules = list(STALE_RULES)
    if args.include_rescue:
        active_rules.append(CI_RESCUE_RULE)

    to_delete = classify_comments(bot_comments, active_rules)

    if not to_delete:
        print("✅ No stale comments found — nothing to delete.")
        return 0

    print(f"\n{'DRY-RUN: ' if args.dry_run else ''}🗑  Deleting {len(to_delete)} stale comment(s):\n")
    deleted = 0
    failed = 0
    for comment_id, reason in sorted(to_delete.items()):
        # Find full comment for display
        comment = next((c for c in comments if c["id"] == comment_id), None)
        preview = (comment["body"][:80].replace("\n", " ") if comment else "?").strip()
        print(f"  {'[DRY-RUN] ' if args.dry_run else ''}ID {comment_id}: {reason}")
        print(f"    ↳ {preview!r}")

        ok = _delete_comment(comment_id, token, args.dry_run)
        if ok:
            deleted += 1
        else:
            print(f"    ⚠️  Failed to delete comment {comment_id}", file=sys.stderr)
            failed += 1

    print(
        f"\n{'[DRY-RUN] ' if args.dry_run else ''}Summary: "
        f"{deleted} deleted, {failed} failed."
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
