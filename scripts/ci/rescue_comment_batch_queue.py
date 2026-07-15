#!/usr/bin/env python3
"""Rescue comment batching queue manager.

Manages queuing and flushing of rescue comment sections when cascading errors
are detected, allowing comments to be batched and posted as single appends
rather than individual posts.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import pathlib
import time
from dataclasses import dataclass, asdict
from typing import Optional


QUEUE_DIR = pathlib.Path(".codex/rescue-comment-queue")
"""Directory where batched rescue comment items are stored as JSON files."""
BATCH_WAIT_DEFAULT = 3  # seconds
"""Default time in seconds to wait before flushing batched items.
Can be tuned based on workflow patterns; higher values reduce API calls but delay posting."""
# Note: UTC_TIMESTAMP_FORMAT is also defined in post_rescue_comment.py.
# We keep both to maintain module independence and avoid circular imports.
UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)


@dataclass
class BatchQueueItem:
    """Single queued rescue comment section."""
    pr_number: int
    commit_sha: str
    workflow_name: str
    run_id: str
    run_url: str
    section_title: Optional[str]
    section_content: Optional[str]
    timestamp: str

    def to_section_markdown(self) -> str:
        """Convert queue item to markdown section for appending."""
        now = self.timestamp
        if self.section_title and self.section_content:
            return (
                f"<details><summary>📋 <code>{self.section_title}</code> — {now} · "
                f"<a href=\"{self.run_url}\">Run #{self.run_id}</a></summary>\n\n"
                f"{self.section_content}\n\n"
                f"</details>"
            )
        else:
            return (
                f"<details><summary>🔴 <code>{self.workflow_name}</code> — {now} · "
                f"<a href=\"{self.run_url}\">Run #{self.run_id}</a></summary>\n\n"
                f"@copilot **{self.workflow_name}** failed on commit `{self.commit_sha[:12]}`. "
                f"Check [run #{self.run_id}]({self.run_url}) for details.\n\n"
                f"</details>"
            )


def init_queue_dir() -> None:
    """Ensure batch queue directory exists."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def get_queue_file(pr_number: int, commit_sha: str) -> pathlib.Path:
    """Get the queue file path for a specific PR and commit."""
    init_queue_dir()
    sha_short = commit_sha[:12]
    return QUEUE_DIR / f"queue_{pr_number}_{sha_short}.json"


def queue_item(
    pr_number: int,
    commit_sha: str,
    workflow_name: str,
    run_id: str,
    run_url: str,
    section_title: Optional[str] = None,
    section_content: Optional[str] = None,
) -> None:
    """Queue a rescue comment section for batch posting."""
    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime(UTC_TIMESTAMP_FORMAT)

    item = BatchQueueItem(
        pr_number=pr_number,
        commit_sha=commit_sha,
        workflow_name=workflow_name,
        run_id=str(run_id),
        run_url=run_url,
        section_title=section_title,
        section_content=section_content,
        timestamp=now,
    )
    
    queue_file = get_queue_file(pr_number, commit_sha)
    items = []
    
    # Load existing items if queue file exists
    if queue_file.exists():
        try:
            with open(queue_file, "r") as f:
                data = json.load(f)
                items = [BatchQueueItem(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Queue file corrupted ({queue_file}): {e}. Starting fresh.")
    
    # Add new item
    items.append(item)
    
    # Save updated queue
    with open(queue_file, "w") as f:
        json.dump([asdict(item) for item in items], f, indent=2)
    
    print(f"✅ Queued `{workflow_name}` failure for batch posting (PR #{pr_number}, {commit_sha[:12]})")


def get_queued_items(pr_number: int, commit_sha: str) -> list[BatchQueueItem]:
    """Get all queued items for a specific PR and commit."""
    queue_file = get_queue_file(pr_number, commit_sha)
    
    if not queue_file.exists():
        return []
    
    try:
        with open(queue_file, "r") as f:
            data = json.load(f)
            return [BatchQueueItem(**item) for item in data]
    except (json.JSONDecodeError, ValueError):
        return []


def should_flush_queue(pr_number: int, commit_sha: str, batch_wait_seconds: int = BATCH_WAIT_DEFAULT) -> bool:
    """Check if batch queue should be flushed (all items ready or timeout expired)."""
    queue_file = get_queue_file(pr_number, commit_sha)
    
    if not queue_file.exists():
        return False
    
    # Check file age — if older than batch_wait_seconds, flush
    file_age = time.time() - queue_file.stat().st_mtime
    return file_age >= batch_wait_seconds


def flush_queue(pr_number: int, commit_sha: str) -> list[BatchQueueItem]:
    """Get and clear all queued items for a specific PR and commit."""
    items = get_queued_items(pr_number, commit_sha)
    queue_file = get_queue_file(pr_number, commit_sha)
    
    if queue_file.exists():
        queue_file.unlink()
    
    return items


def clear_queue(pr_number: int, commit_sha: str) -> None:
    """Clear the queue for a specific PR and commit (e.g., if posting succeeded)."""
    queue_file = get_queue_file(pr_number, commit_sha)
    if queue_file.exists():
        queue_file.unlink()


def queue_has_items(pr_number: int, commit_sha: str) -> bool:
    """Check if queue has any items."""
    queue_file = get_queue_file(pr_number, commit_sha)
    return queue_file.exists() and queue_file.stat().st_size > 0
