#!/usr/bin/env python3
"""Consolidate cascading Copilot error comments into a single appended thread.

This script proactively detects and consolidates multiple Copilot error comments
that occur when Copilot crashes repeatedly while processing a PR. Instead of
leaving 10+ error comments, this consolidates them into ONE comment with all
error IDs documented, allowing the user to understand the full scope of the
cascade without comment sprawl.

Usage:
    python scripts/ci/consolidate_cascade_errors.py

Required environment variables:
    GH_TOKEN        GitHub token (PAT or github.token)
    REPO            owner/repo slug
    PR_NUMBER       Pull request number (integer)

The script will:
1. Detect all "comment-generic-error" comments from Copilot user
2. If 5+ found, consolidate into first comment with markers for others
3. Delete duplicate error comments to prevent sprawl
4. Post a consolidation summary comment explaining the cascade
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Optional

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_COMMENT_LEN = 65_536
DUPLICATE_DIGEST_LENGTH = 16
CASCADE_THRESHOLD = 5
CONSOLIDATION_MARKER_PREFIX = "<!-- cascade-consolidated-error:"


def _gh(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
) -> tuple[int, object]:
    """Make a GitHub API call."""
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"******",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            if raw:
                return resp.status, json.loads(raw)
            return resp.status, {}
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        return exc.code, err_body


def _find_copilot_error_comments(
    token: str,
    repo: str,
    pr_number: int,
) -> list[dict]:
    """Find all Copilot error comments on the PR."""
    error_comments = []
    page = 1
    
    while True:
        status, comments = _gh(
            "GET",
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
            token,
        )
        if status != 200:
            break
        if not isinstance(comments, list) or not comments:
            break
        
        for c in comments:
            body = c.get("body") or ""
            if "comment-generic-error" in body and c.get("user", {}).get("login") == "Copilot":
                error_comments.append(c)
        
        if len(comments) < 100:
            break
        page += 1
    
    return sorted(error_comments, key=lambda c: c.get("created_at", ""))


def _build_consolidation_comment(
    error_comments: list[dict],
    repo: str,
    pr_number: int,
) -> str:
    """Build a consolidation comment documenting all error IDs."""
    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime(UTC_TIMESTAMP_FORMAT)
    error_count = len(error_comments)
    
    # Extract UUIDs from error comments
    uuids = []
    for c in error_comments:
        body = c.get("body", "")
        # Extract identifier from format: "identifier so they can better serve you: `UUID`"
        if "identifier so they can better serve you:" in body:
            parts = body.split("identifier so they can better serve you:")
            if len(parts) > 1:
                uuid_part = parts[1].strip().strip("`")
                if uuid_part:
                    uuids.append(uuid_part)
    
    # Build error list with links
    error_list = ""
    for i, c in enumerate(error_comments, 1):
        error_id = c.get("id")
        created_at = c.get("created_at", "unknown")
        error_url = c.get("html_url", "#")
        uuid = uuids[i-1] if i-1 < len(uuids) else "unknown"
        error_list += f"{i}. [Error #{error_id}]({error_url}) — {created_at} (UUID: `{uuid}`)\n"
    
    consolidation_body = (
        f"<!-- cascade-consolidated-error:{pr_number}:{error_count} -->\n"
        f"## 🚨 Copilot Cascade Consolidation — {error_count} Errors\n\n"
        f"@mbaetiong Copilot encountered **{error_count} sequential errors** while processing your PR. "
        f"Instead of leaving {error_count} separate error comments, we've consolidated them into this single thread.\n\n"
        f"**Error Timeline:**\n\n"
        f"{error_list}\n\n"
        f"**What This Means:**\n"
        f"- Copilot attempted to process your comments/requests {error_count} times\n"
        f"- Each attempt encountered an internal error and crashed\n"
        f"- All error IDs have been consolidated here for debugging\n\n"
        f"**Recommended Action:**\n"
        f"1. Please reach out to GitHub support with the error UUIDs listed above\n"
        f"2. Try mentioning @copilot again in a fresh comment to retry\n"
        f"3. The rescue CI system will continue to post workflow failure updates as needed\n\n"
        f"_Auto-consolidated by cascade-error consolidation system · {now}_"
    )
    
    return consolidation_body


def _consolidate_cascade(
    token: str,
    repo: str,
    pr_number: int,
    error_comments: list[dict],
) -> bool:
    """Consolidate error comments: keep first, append digest markers, delete rest."""
    if len(error_comments) < CASCADE_THRESHOLD:
        return False
    
    print(
        f"🔄 CASCADE CONSOLIDATION: Found {len(error_comments)} Copilot error comments. "
        f"Consolidating into first comment..."
    )
    
    first_comment = error_comments[0]
    canonical_id = first_comment.get("id")
    canonical_body = (first_comment.get("body") or "").rstrip()
    
    # Add digest markers for all subsequent comments
    for duplicate in error_comments[1:]:
        duplicate_id = duplicate.get("id")
        duplicate_body = duplicate.get("body", "")
        
        # Create unique digest for this error
        duplicate_digest = hashlib.sha256(
            f"{duplicate_id}:{duplicate.get('created_at')}".encode()
        ).hexdigest()[:DUPLICATE_DIGEST_LENGTH]
        
        # Extract UUID from duplicate comment
        uuid = "unknown"
        if "identifier so they can better serve you:" in duplicate_body:
            parts = duplicate_body.split("identifier so they can better serve you:")
            if len(parts) > 1:
                uuid = parts[1].strip().strip("`")
        
        # Add marker to canonical comment
        marker = f"{CONSOLIDATION_MARKER_PREFIX}{duplicate_digest} -->"
        if marker not in canonical_body:
            canonical_body = (
                canonical_body
                + f"\n<!-- cascade-error-id:{duplicate_id}:uuid:{uuid}:{duplicate_digest} -->"
            )
    
    # Update canonical comment with consolidated markers
    status, _ = _gh(
        "PATCH",
        f"/repos/{repo}/issues/comments/{canonical_id}",
        token,
        {"body": canonical_body[:MAX_COMMENT_LEN]},
    )
    
    if status not in (200, 201):
        print(f"⚠️  Failed to update canonical comment: HTTP {status}")
        return False
    
    print(f"✅ Updated canonical comment #{canonical_id} with error markers")
    
    # Delete all duplicate error comments
    deleted_count = 0
    for duplicate in error_comments[1:]:
        duplicate_id = duplicate.get("id")
        delete_status, _ = _gh(
            "DELETE",
            f"/repos/{repo}/issues/comments/{duplicate_id}",
            token,
        )
        
        if delete_status in (200, 204):
            deleted_count += 1
            print(f"✅ Deleted duplicate error comment #{duplicate_id}")
        else:
            print(f"⚠️  Failed to delete comment #{duplicate_id}: HTTP {delete_status}")
    
    print(f"✅ CASCADE CONSOLIDATION COMPLETE: Kept 1 comment, deleted {deleted_count} duplicates")
    return True


def main() -> None:
    """Main entry point."""
    token = os.environ.get("GH_TOKEN", "").strip()
    repo = os.environ.get("REPO", "").strip()
    pr_number_raw = os.environ.get("PR_NUMBER", "").strip()
    
    if not token or not repo or not pr_number_raw:
        print(
            "❌ Missing required env vars: GH_TOKEN, REPO, PR_NUMBER",
            file=sys.stderr,
        )
        sys.exit(1)
    
    try:
        pr_number = int(pr_number_raw)
    except ValueError:
        print(f"❌ Invalid PR_NUMBER: {pr_number_raw}", file=sys.stderr)
        sys.exit(1)
    
    print(f"🔍 Scanning PR #{pr_number} for cascading Copilot error comments...")
    
    # Find all error comments
    error_comments = _find_copilot_error_comments(token, repo, pr_number)
    
    if not error_comments:
        print("✅ No Copilot error comments found on PR")
        return
    
    print(f"Found {len(error_comments)} Copilot error comments")
    
    if len(error_comments) >= CASCADE_THRESHOLD:
        # Consolidate the cascade
        if _consolidate_cascade(token, repo, pr_number, error_comments):
            print(f"✅ Consolidation successful")
        else:
            print(f"⚠️  Consolidation failed — cascade still active", file=sys.stderr)
            sys.exit(1)
    else:
        print(
            f"ℹ️  Found {len(error_comments)} error comments (threshold: {CASCADE_THRESHOLD}) "
            f"— no consolidation needed yet"
        )


if __name__ == "__main__":
    main()
