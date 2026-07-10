"""
PR Comment Processing Utilities

This module provides reusable functions for PR comment processing that were
previously embedded in check_pr_comments.py. Extracting these improves
cyclomatic complexity and promotes code reuse.

Functions:
    - parse_iso_timestamp: Parse ISO-8601 timestamps
    - extract_copilot_response_times: Build timeline of Copilot responses
    - extract_copilot_reply_index: Build reply index from review comments
    - check_if_addressed: Determine if comment was addressed by Copilot
    - classify_and_validate_comment: Process comment with validation

Author: Codex Team
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def parse_iso_timestamp(ts: str) -> Optional[datetime]:
    """
    Parse an ISO-8601 timestamp, returning None on failure.

    Args:
        ts: ISO-8601 timestamp string

    Returns:
        datetime object or None if parsing fails
    """
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        print(
            f"[check_pr_comments] Warning: unparseable timestamp {ts!r} — skipping",
            file=sys.stderr,
        )
        return None


def extract_copilot_response_times(
    issue_comments: list[dict[str, Any]],
    review_comments: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    pr_commits: list[dict[str, Any]],
    copilot_agents: set[str],
) -> list[datetime]:
    """
    Build timeline of Copilot responses from all comment sources AND commits.

    When a Copilot agent pushes a commit after a review comment, that commit
    IS a response: it means the agent addressed the concern in code.

    Args:
        issue_comments: List of issue comments
        review_comments: List of review comments
        reviews: List of reviews
        pr_commits: List of commits
        copilot_agents: Set of Copilot agent usernames

    Returns:
        List of datetime objects representing Copilot response times
    """
    copilot_response_times: list[datetime] = []

    # Extract from issue comments
    for c in issue_comments:
        login = (c.get("user") or {}).get("login", "")
        if login in copilot_agents:
            dt = parse_iso_timestamp(c.get("created_at", ""))
            if dt is not None:
                copilot_response_times.append(dt)

    # Extract from review comments
    for c in review_comments:
        login = (c.get("user") or {}).get("login", "")
        if login in copilot_agents:
            dt = parse_iso_timestamp(c.get("created_at", ""))
            if dt is not None:
                copilot_response_times.append(dt)

    # Extract from reviews
    for r in reviews:
        login = (r.get("user") or {}).get("login", "")
        if login in copilot_agents:
            dt = parse_iso_timestamp(r.get("submitted_at", ""))
            if dt is not None:
                copilot_response_times.append(dt)

    # Include commit timestamps from Copilot agents as response signals
    for commit in pr_commits:
        author_login = (
            (commit.get("author") or {}).get("login", "")
            or (commit.get("committer") or {}).get("login", "")
        )
        if author_login in copilot_agents:
            commit_data = commit.get("commit", {})
            committer_ts = (commit_data.get("committer") or {}).get("date", "")
            author_ts = (commit_data.get("author") or {}).get("date", "")
            dt = parse_iso_timestamp(committer_ts or author_ts)
            if dt is not None:
                copilot_response_times.append(dt)

    return copilot_response_times


def extract_copilot_reply_index(
    review_comments: list[dict[str, Any]],
    copilot_agents: set[str],
) -> dict[int, list[datetime]]:
    """
    Build explicit reply index from review_comments.

    Uses GitHub's `in_reply_to_id` field so that direct thread replies are
    detected without relying solely on a global timestamp heuristic.

    Args:
        review_comments: List of review comments
        copilot_agents: Set of Copilot agent usernames

    Returns:
        Dict mapping parent comment ID to list of Copilot reply timestamps
    """
    copilot_reply_index: dict[int, list[datetime]] = {}
    
    for c in review_comments:
        login = (c.get("user") or {}).get("login", "")
        if login in copilot_agents:
            parent_id = c.get("in_reply_to_id")
            dt = parse_iso_timestamp(c.get("created_at", ""))
            if parent_id is not None and dt is not None:
                copilot_reply_index.setdefault(int(parent_id), []).append(dt)

    return copilot_reply_index


def check_if_addressed(
    comment_ts_str: str,
    comment_id: Optional[int],
    copilot_response_times: list[datetime],
    copilot_reply_index: dict[int, list[datetime]],
) -> tuple[bool, Optional[float]]:
    """
    Determine if comment was addressed by Copilot.

    For review comments, first checks whether a Copilot agent posted a direct
    reply (matched via `in_reply_to_id`). Falls back to the global timestamp
    heuristic for all other comment types.

    Args:
        comment_ts_str: Comment creation timestamp
        comment_id: Comment ID (for review comments)
        copilot_response_times: List of Copilot response timestamps
        copilot_reply_index: Index of direct replies

    Returns:
        Tuple of (addressed: bool, latency_seconds: Optional[float])
    """
    if not comment_ts_str:
        return False, None

    comment_ts = parse_iso_timestamp(comment_ts_str)
    if comment_ts is None:
        return False, None

    # 1. Explicit reply check (review comments with in_reply_to_id)
    if comment_id is not None:
        direct_replies = copilot_reply_index.get(comment_id, [])
        if direct_replies:
            first_reply = min(direct_replies)
            latency = (first_reply - comment_ts).total_seconds()
            return True, max(latency, 0.0)

    # 2. Global timestamp heuristic fallback
    candidates = [rt for rt in copilot_response_times if rt > comment_ts]
    if candidates:
        first_response = min(candidates)
        latency = (first_response - comment_ts).total_seconds()
        return True, max(latency, 0.0)

    return False, None


def should_skip_comment(
    body: str,
    skip_body_markers: list[str],
    skip_text_patterns: list[str],
) -> bool:
    """
    Check if comment should be skipped from analysis.

    Args:
        body: Comment body text
        skip_body_markers: List of markers that indicate self-referential content
        skip_text_patterns: List of patterns that indicate operational text

    Returns:
        True if comment should be skipped, False otherwise
    """
    body_start = body[:80]
    
    if any(body_start.lstrip().startswith(m) for m in skip_body_markers):
        return True
    
    if any(body_start.lstrip().startswith(p) for p in skip_text_patterns):
        return True
    
    return False
