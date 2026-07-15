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
import re
import sys
import urllib.error
import urllib.request
from typing import Any, Optional

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_COMMENT_LEN = 65_536
DUPLICATE_DIGEST_LENGTH = 16
CASCADE_THRESHOLD = 5
CONSOLIDATION_MARKER_PREFIX = "<!-- cascade-consolidated-error:"
CASCADE_ERROR_ID_MARKER_PREFIX = "<!-- cascade-error-id:"


def _extract_uuid_from_error(comment_body: str) -> str:
    """Extract UUID from Copilot error comment.

    Copilot error comments contain a UUID after "identifier so they can better serve you:"
    This function uses regex to extract UUID-like patterns (hex strings or standard UUID format).
    Falls back to "unknown" if no UUID found.
    """
    # Try standard format first: "identifier so they can better serve you: `UUID`"
    # Pattern: at least one hex digit, optionally followed by (hyphen + hex digits) groups
    # This ensures no standalone hyphens (e.g., 'abc' matches, 'abc-' doesn't, 'abc-def' matches)
    match = re.search(r"identifier so they can better serve you:\s*[`'\"]?([a-fA-F0-9]+(?:-[a-fA-F0-9]+)*)[`'\"]?", comment_body)
    if match:
        uuid = match.group(1).strip()
        if uuid:
            return uuid
    
    # Fall back to looking for any hex string that might be a UUID
    # Matches two formats: (1) Standard UUID 8-4-4-4-12 hex digits, OR (2) 32 continuous hex digits
    hex_match = re.search(
        r"([a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}|[a-fA-F0-9]{32})",
        comment_body
    )
    if hex_match:
        return hex_match.group(1)
    
    return "unknown"


def _gh(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
) -> tuple[int, object]:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"token {token}",
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
            # Successful GitHub GET requests used by this script return JSON.
            # Empty bodies are expected for 204-style mutation responses.
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

        # Extract UUID from duplicate comment using robust pattern matching
        uuid = _extract_uuid_from_error(duplicate_body)

        # Add marker to canonical comment
        error_id_marker = f"{CASCADE_ERROR_ID_MARKER_PREFIX}{duplicate_id}:uuid:{uuid}:{duplicate_digest} -->"
        if error_id_marker not in canonical_body:
            canonical_body = (
                canonical_body
                + f"\n{error_id_marker}"
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
