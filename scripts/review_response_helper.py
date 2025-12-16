#!/usr/bin/env python3
"""
Review Response Helper

Automates the process of responding to code review comments by:
- Parsing review comments from structured input
- Creating fix checklist
- Tracking commit resolutions
- Auto-generating reply text with commit references

Usage:
    python scripts/review_response_helper.py --comments review_comments.json
    python scripts/review_response_helper.py --generate-checklist
"""

import argparse
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ReviewComment:
    """Represents a single review comment."""

    comment_id: str
    file_path: str
    line_number: Optional[int]
    comment_text: str
    is_resolved: bool = False
    resolution_commit: Optional[str] = None
    resolution_note: Optional[str] = None


@dataclass
class FixChecklist:
    """Tracks fixes needed for review comments."""

    created_at: str
    comments: List[ReviewComment]
    total_comments: int
    resolved_count: int


def parse_review_comments(comments_file: Path) -> List[ReviewComment]:
    """
    Parse review comments from JSON file.

    Expected format:
    {
        "comments": [
            {
                "id": "123456",
                "file": "path/to/file.py",
                "line": 42,
                "text": "Comment text here"
            }
        ]
    }
    """
    if not comments_file.exists():
        logger.error(f"Comments file not found: {comments_file}")
        return []

    with open(comments_file) as f:
        data = json.load(f)

    comments = []
    for comment_data in data.get("comments", []):
        comment = ReviewComment(
            comment_id=str(comment_data.get("id", "")),
            file_path=comment_data.get("file", ""),
            line_number=comment_data.get("line"),
            comment_text=comment_data.get("text", ""),
        )
        comments.append(comment)

    logger.info(f"Parsed {len(comments)} review comments")
    return comments


def generate_fix_checklist(comments: List[ReviewComment], output_path: Path) -> None:
    """Generate markdown checklist of fixes needed."""
    checklist = FixChecklist(
        created_at=datetime.now().isoformat(),
        comments=comments,
        total_comments=len(comments),
        resolved_count=sum(1 for c in comments if c.is_resolved),
    )

    # Generate markdown
    md_lines = [
        "# Code Review Fix Checklist",
        "",
        f"**Created**: {checklist.created_at}",
        f"**Total Comments**: {checklist.total_comments}",
        f"**Resolved**: {checklist.resolved_count}/{checklist.total_comments}",
        "",
        "## Comments to Address",
        "",
    ]

    for i, comment in enumerate(comments, 1):
        status = "✅" if comment.is_resolved else "⬜"
        md_lines.append(f"### {status} Comment {i} - {comment.file_path}")
        if comment.line_number:
            md_lines.append(f"**Line**: {comment.line_number}")
        md_lines.append(f"**Comment ID**: {comment.comment_id}")
        md_lines.append("")
        md_lines.append(f"> {comment.comment_text}")
        md_lines.append("")
        if comment.is_resolved:
            md_lines.append(f"**Resolved in**: {comment.resolution_commit}")
            if comment.resolution_note:
                md_lines.append(f"**Note**: {comment.resolution_note}")
        md_lines.append("---")
        md_lines.append("")

    # Write to file
    with open(output_path, "w") as f:
        f.write("\n".join(md_lines))

    logger.info(f"Generated checklist: {output_path}")


def track_resolution(
    checklist_path: Path, comment_id: str, commit_sha: str, note: Optional[str] = None
) -> bool:
    """Mark a comment as resolved with commit information."""
    if not checklist_path.exists():
        logger.error(f"Checklist file not found: {checklist_path}")
        return False

    # Load existing checklist
    with open(checklist_path) as f:
        content = f.read()

    # Update the specific comment
    # This is a simple implementation - in production, use structured format
    pattern = f"Comment ID**: {comment_id}"
    if pattern not in content:
        logger.warning(f"Comment ID {comment_id} not found in checklist")
        return False

    # Mark as resolved - replace only the checkbox symbol
    content = re.sub(
        f"^⬜ (Comment \\d+ - [^\\n]+\\n[^>]+{comment_id})", f"✅ \\1", content, flags=re.MULTILINE
    )

    # Add resolution info
    resolution_text = f"\n**Resolved in**: {commit_sha}\n"
    if note:
        resolution_text += f"**Note**: {note}\n"

    content = re.sub(f"(Comment ID\\*\\*: {comment_id}\\n)", f"\\1{resolution_text}", content)

    with open(checklist_path, "w") as f:
        f.write(content)

    logger.info(f"Marked comment {comment_id} as resolved in {commit_sha}")
    return True


def generate_reply_text(comment_id: str, commit_sha: str, description: str) -> str:
    """Generate standardized reply text for a resolved comment."""
    return f"Fixed in commit `{commit_sha}`. {description}"


def get_recent_commits(count: int = 10) -> List[Dict[str, str]]:
    """Get recent git commits with SHA and message."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--pretty=format:%h|%s"],
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                sha, message = line.split("|", 1)
                commits.append({"sha": sha, "message": message})

        return commits

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get git commits: {e}")
        return []


def auto_match_commits_to_comments(
    comments: List[ReviewComment], commits: List[Dict[str, str]]
) -> List[Tuple[ReviewComment, str]]:
    """
    Automatically match commits to comments based on file paths and keywords.

    Returns list of (comment, commit_sha) tuples for likely matches.
    """
    matches = []

    for comment in comments:
        if comment.is_resolved:
            continue

        # Extract file name from path
        file_name = Path(comment.file_path).name

        # Look for commits mentioning the file or related keywords
        for commit in commits:
            commit_msg = commit["message"].lower()

            # Check if file name is in commit message
            if file_name.lower() in commit_msg:
                matches.append((comment, commit["sha"]))
                break

            # Check for keyword matches
            keywords = ["fix", "address", "resolve", "improve"]
            if any(kw in commit_msg for kw in keywords):
                # Check if file path components match
                path_parts = comment.file_path.lower().split("/")
                if any(part in commit_msg for part in path_parts if len(part) > 3):
                    matches.append((comment, commit["sha"]))
                    break

    return matches


def main():
    parser = argparse.ArgumentParser(description="Automate code review response process")
    parser.add_argument("--comments", type=Path, help="JSON file containing review comments")
    parser.add_argument(
        "--generate-checklist", action="store_true", help="Generate fix checklist from comments"
    )
    parser.add_argument(
        "--mark-resolved",
        type=str,
        help="Mark comment as resolved (format: comment_id:commit_sha:note)",
    )
    parser.add_argument(
        "--auto-match", action="store_true", help="Automatically match commits to comments"
    )
    parser.add_argument(
        "--output", type=Path, default=Path("review_checklist.md"), help="Output file for checklist"
    )

    args = parser.parse_args()

    if args.generate_checklist:
        if not args.comments:
            logger.error("--comments required for generating checklist")
            return 1

        comments = parse_review_comments(args.comments)
        if not comments:
            return 1

        generate_fix_checklist(comments, args.output)
        logger.info(f"✅ Checklist generated: {args.output}")
        return 0

    if args.mark_resolved:
        parts = args.mark_resolved.split(":", 2)
        if len(parts) < 2:
            logger.error("Format: comment_id:commit_sha:note")
            return 1

        comment_id = parts[0]
        commit_sha = parts[1]
        note = parts[2] if len(parts) > 2 else None

        if track_resolution(args.output, comment_id, commit_sha, note):
            reply = generate_reply_text(comment_id, commit_sha, note or "Fixed")
            logger.info(f"Suggested reply: {reply}")
            return 0
        return 1

    if args.auto_match:
        if not args.comments:
            logger.error("--comments required for auto-matching")
            return 1

        comments = parse_review_comments(args.comments)
        commits = get_recent_commits(20)

        matches = auto_match_commits_to_comments(comments, commits)

        logger.info(f"\nFound {len(matches)} potential matches:")
        for comment, commit_sha in matches:
            logger.info(f"  Comment {comment.comment_id} ({comment.file_path}) -> {commit_sha}")

        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    exit(main())
