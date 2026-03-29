#!/usr/bin/env python3
"""
scripts/ci/check_pr_comments.py
────────────────────────────────
Hardened PR Comment Review Gate (REQ-13 / S227)

Scans ALL comments on the active PR and classifies each as:
  - UNADDRESSED: comment from mbaetiong or any bot that has not received a
    reply from copilot-swe-agent[bot] or github-copilot[bot]
  - ADDRESSED: comment that has a subsequent reply from a Copilot agent
  - REVIEW_THREAD: unresolved PR review thread

Exit codes:
  0 — all high-priority comments addressed
  1 — unaddressed blocking comment from mbaetiong or critical bot
  2 — unaddressed warning-level comments (bot informational)
  3 — usage / API error

Usage:
  python scripts/ci/check_pr_comments.py --pr NUMBER --repo OWNER/REPO
  python scripts/ci/check_pr_comments.py --pr NUMBER --repo OWNER/REPO --output-json FILE
  python scripts/ci/check_pr_comments.py --pr NUMBER --repo OWNER/REPO --post-checklist

Environment:
  GITHUB_TOKEN or GH_TOKEN — required for API access
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any
from urllib import error, request

# ── Constants ─────────────────────────────────────────────────────────────────

# Authors whose unaddressed comments are BLOCKING (exit code 1)
BLOCKING_AUTHORS: set[str] = {"mbaetiong"}

# Bot authors whose unaddressed comments are BLOCKING when they are CI gates
BLOCKING_BOTS: set[str] = {
    "github-actions[bot]",
    "copilot-pull-request-reviewer[bot]",
    "github-advanced-security[bot]",
    "github-code-quality[bot]",
}

# Bot authors whose unaddressed comments are WARNING-level (exit code 2)
WARNING_BOTS: set[str] = {
    "dependabot[bot]",
    "codecov[bot]",
    "snyk-bot",
    "renovate[bot]",
}

# Authors who count as "Copilot responded"
COPILOT_AGENTS: set[str] = {
    "copilot-swe-agent[bot]",
    "github-copilot[bot]",
    "Copilot",
}

GITHUB_API = "https://api.github.com"


# ── GitHub API helper ─────────────────────────────────────────────────────────

def gh_get(path: str, token: str) -> Any:
    url = f"{GITHUB_API}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"HTTP {e.code} GET {path}: {body}") from e


def gh_get_all_pages(path: str, token: str) -> list[Any]:
    """Fetch all pages of a paginated endpoint."""
    results: list[Any] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        data = gh_get(f"{path}{sep}per_page=100&page={page}", token)
        if not isinstance(data, list):
            # Some endpoints wrap in a dict
            if isinstance(data, dict) and "comments" in data:
                data = data["comments"]
            else:
                results.append(data)
                break
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ── Core logic ────────────────────────────────────────────────────────────────

def classify_comment(comment: dict[str, Any]) -> dict[str, Any]:
    """Return enriched comment record with classification metadata."""
    login: str = (comment.get("user") or {}).get("login", "unknown")
    user_type: str = (comment.get("user") or {}).get("type", "User")
    created_at: str = comment.get("created_at", "")
    body: str = (comment.get("body") or "")[:500]
    url: str = comment.get("html_url", "")
    comment_id: int = comment.get("id", 0)

    is_bot = login.endswith("[bot]") or user_type == "Bot"
    is_blocking_human = login in BLOCKING_AUTHORS
    is_blocking_bot = login in BLOCKING_BOTS
    is_warning_bot = login in WARNING_BOTS

    category: str
    if is_blocking_human:
        category = "blocking_human"
    elif is_blocking_bot:
        category = "blocking_bot"
    elif is_bot and is_warning_bot:
        category = "warning_bot"
    elif is_bot:
        category = "info_bot"
    else:
        category = "human"

    return {
        "id": comment_id,
        "author": login,
        "category": category,
        "created_at": created_at,
        "url": url,
        "body_preview": body[:120].replace("\n", " "),
        "addressed": False,  # will be updated below
    }


def find_unaddressed_comments(
    pr_number: int,
    repo: str,
    token: str,
) -> dict[str, Any]:
    """
    Fetch all PR comments and review comments, then determine which
    are unaddressed by a Copilot agent.

    Returns a report dict.
    """
    # 1. PR issue comments (general conversation)
    issue_comments = gh_get_all_pages(
        f"/repos/{repo}/issues/{pr_number}/comments", token
    )

    # 2. PR review comments (inline code review)
    review_comments = gh_get_all_pages(
        f"/repos/{repo}/pulls/{pr_number}/comments", token
    )

    # 3. PR reviews (review-level bodies)
    reviews = gh_get_all_pages(
        f"/repos/{repo}/pulls/{pr_number}/reviews", token
    )

    # Build timeline of Copilot responses (by timestamp)
    copilot_response_times: list[datetime] = []
    for c in issue_comments:
        login = (c.get("user") or {}).get("login", "")
        if login in COPILOT_AGENTS:
            ts = c.get("created_at", "")
            try:
                copilot_response_times.append(
                    datetime.fromisoformat(ts.replace("Z", "+00:00"))
                )
            except ValueError:
                pass

    def was_addressed(comment_ts_str: str) -> bool:
        """True if a Copilot agent posted AFTER this comment."""
        if not comment_ts_str:
            return False
        try:
            comment_ts = datetime.fromisoformat(
                comment_ts_str.replace("Z", "+00:00")
            )
        except ValueError:
            return False
        return any(rt > comment_ts for rt in copilot_response_times)

    # Classify all comments
    all_records: list[dict[str, Any]] = []

    for c in issue_comments:
        login = (c.get("user") or {}).get("login", "")
        if login in COPILOT_AGENTS:
            continue  # Copilot's own comments don't need addressing
        rec = classify_comment(c)
        rec["comment_type"] = "issue_comment"
        rec["addressed"] = was_addressed(c.get("created_at", ""))
        all_records.append(rec)

    for c in review_comments:
        login = (c.get("user") or {}).get("login", "")
        if login in COPILOT_AGENTS:
            continue
        rec = classify_comment(c)
        rec["comment_type"] = "review_comment"
        rec["addressed"] = was_addressed(c.get("created_at", ""))
        all_records.append(rec)

    for r in reviews:
        login = (r.get("user") or {}).get("login", "")
        if login in COPILOT_AGENTS:
            continue
        body = (r.get("body") or "").strip()
        if not body:
            continue  # Skip empty review bodies
        rec = classify_comment(r)
        rec["comment_type"] = "review"
        rec["addressed"] = was_addressed(r.get("submitted_at", ""))
        all_records.append(rec)

    # Separate by category
    unaddressed_blocking: list[dict] = []
    unaddressed_warning: list[dict] = []
    unaddressed_info: list[dict] = []
    addressed: list[dict] = []

    for rec in all_records:
        if rec["addressed"]:
            addressed.append(rec)
            continue
        cat = rec["category"]
        if cat in ("blocking_human", "blocking_bot"):
            unaddressed_blocking.append(rec)
        elif cat == "warning_bot":
            unaddressed_warning.append(rec)
        else:
            unaddressed_info.append(rec)

    return {
        "pr_number": pr_number,
        "repo": repo,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "total_comments": len(all_records),
        "addressed_count": len(addressed),
        "unaddressed_blocking": unaddressed_blocking,
        "unaddressed_warning": unaddressed_warning,
        "unaddressed_info": unaddressed_info,
        "addressed": addressed,
        "exit_code": (
            1 if unaddressed_blocking else
            2 if unaddressed_warning else
            0
        ),
    }


# ── Checklist poster ──────────────────────────────────────────────────────────

def build_checklist_body(report: dict[str, Any]) -> str:
    """Build the markdown checklist posted to the PR."""
    total = report["pr_number"]  # kept for context; use pr_number in header
    total = report["total_comments"]
    addressed = report["addressed_count"]
    blocking = report["unaddressed_blocking"]
    warning = report["unaddressed_warning"]
    info = report["unaddressed_info"]
    run_url = os.environ.get(
        "GITHUB_RUN_URL",
        f"https://github.com/{report['repo']}/actions"
    )

    lines = [
        "<!-- comment-review-gate-checklist -->",
        "## 🔍 PR Comment Review Gate — Copilot Must Address All Items",
        "",
        "> **Policy (§0 Codebase Agency Policy):** ALL comments from `mbaetiong` and "
        "ALL bot-posted comments MUST be reviewed and addressed before new work begins.",
        "",
        f"**Scan results:** {addressed}/{total} comments addressed · "
        f"Scanned at {report['scanned_at'][:16]} UTC",
        "",
    ]

    if not blocking and not warning and not info:
        lines += [
            "### ✅ All Comments Addressed",
            "",
            "No unaddressed comments found. You may proceed with new work.",
        ]
    else:
        if blocking:
            lines += [
                "### 🚨 BLOCKING — Must address before ANY new commits",
                "",
                "| # | Author | Type | Preview | Link |",
                "|---|--------|------|---------|------|",
            ]
            for i, c in enumerate(blocking, 1):
                author = c["author"]
                ctype = c["comment_type"].replace("_", " ")
                preview = c["body_preview"][:80].replace("|", "╎")
                url = c["url"]
                lines.append(
                    f"| {i} | `@{author}` | {ctype} | {preview} | [View]({url}) |"
                )
            lines += [
                "",
                "**Instructions:** Reply to each row above with your resolution before committing.",
                "",
            ]

        if warning:
            lines += [
                "### ⚠️ WARNINGS — Bot comments requiring review",
                "",
                "| # | Author | Type | Preview | Link |",
                "|---|--------|------|---------|------|",
            ]
            for i, c in enumerate(warning, 1):
                author = c["author"]
                ctype = c["comment_type"].replace("_", " ")
                preview = c["body_preview"][:80].replace("|", "╎")
                url = c["url"]
                lines.append(
                    f"| {i} | `@{author}` | {ctype} | {preview} | [View]({url}) |"
                )
            lines.append("")

        if info:
            lines += [
                "<details>",
                f"<summary>ℹ️ Informational comments ({len(info)}) — click to expand</summary>",
                "",
                "| # | Author | Type | Preview | Link |",
                "|---|--------|------|---------|------|",
            ]
            for i, c in enumerate(info, 1):
                author = c["author"]
                ctype = c["comment_type"].replace("_", " ")
                preview = c["body_preview"][:60].replace("|", "╎")
                url = c["url"]
                lines.append(
                    f"| {i} | `@{author}` | {ctype} | {preview} | [View]({url}) |"
                )
            lines += ["</details>", ""]

    lines += [
        "---",
        "",
        "**To dismiss this checklist:** Reply to every blocking item above, "
        "then push a new commit. The gate will re-scan on the next push.",
        "",
        f"_[🔗 Workflow run]({run_url})_",
    ]

    return "\n".join(lines)


def post_checklist(
    report: dict[str, Any],
    pr_number: int,
    repo: str,
    token: str,
) -> None:
    """Upsert the checklist comment on the PR."""
    MARKER = "<!-- comment-review-gate-checklist -->"
    body = build_checklist_body(report)

    # Get existing comments
    comments = gh_get_all_pages(
        f"/repos/{repo}/issues/{pr_number}/comments", token
    )
    existing = next(
        (c for c in comments if MARKER in (c.get("body") or "")), None
    )

    import json as _json
    payload = _json.dumps({"body": body}).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    if existing:
        url = f"{GITHUB_API}/repos/{repo}/issues/comments/{existing['id']}"
        req = request.Request(url, data=payload, headers=headers, method="PATCH")
        action = "Updated"
    else:
        url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
        req = request.Request(url, data=payload, headers=headers, method="POST")
        action = "Created"

    try:
        with request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        print(f"{action} comment #{result.get('id')} on PR #{pr_number}")
    except error.HTTPError as e:
        body_err = e.read().decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"HTTP {e.code} posting checklist: {body_err}") from e


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="PR Comment Review Gate — enforce that all mbaetiong/bot comments are addressed"
    )
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--output-json", metavar="FILE", help="Write JSON report to FILE")
    parser.add_argument("--post-checklist", action="store_true",
                        help="Post/update checklist comment on the PR")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print checklist body without posting")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GH_TOKEN or GITHUB_TOKEN environment variable required", file=sys.stderr)
        return 3

    try:
        report = find_unaddressed_comments(args.pr, args.repo, token)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    if args.output_json:
        with open(args.output_json, "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"Report written to {args.output_json}")

    # Print summary
    blocking = report["unaddressed_blocking"]
    warning = report["unaddressed_warning"]
    info = report["unaddressed_info"]
    total = report["total_comments"]
    addressed = report["addressed_count"]

    print(f"\nPR #{args.pr} comment scan — {report['repo']}")
    print(f"  Total comments   : {total}")
    print(f"  Addressed        : {addressed}")
    print(f"  Blocking unaddressed : {len(blocking)}")
    print(f"  Warning unaddressed  : {len(warning)}")
    print(f"  Info unaddressed     : {len(info)}")

    if blocking:
        print("\nBLOCKING — must address before proceeding:")
        for c in blocking:
            print(f"  [{c['category']}] @{c['author']} ({c['comment_type']}): {c['body_preview'][:80]}")
            print(f"    → {c['url']}")

    if warning:
        print("\nWARNING — bot comments requiring review:")
        for c in warning:
            print(f"  @{c['author']}: {c['body_preview'][:80]}")

    checklist_body = build_checklist_body(report)

    if args.dry_run:
        print("\n--- CHECKLIST BODY (dry-run) ---")
        print(checklist_body)
    elif args.post_checklist:
        post_checklist(report, args.pr, args.repo, token)

    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
