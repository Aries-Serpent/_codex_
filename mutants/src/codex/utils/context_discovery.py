"""
Context discovery utilities for Codex session initialization.

Purpose:
  Automatically detect or prompt for required session context
  (PR number, branch name, user, commit hash) at session start.

References:
  - Analysis finding: CODEX-008 - PR number guessing mid-session
  - Best practice: Gather critical inputs upfront

Functions:
  - get_pr_number(): Attempt detection or prompt user
  - get_session_info(): Gather all context
  - discover_git_context(): Parse git state
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from typing import Any, Optional

from codex.logging.structured_logger import logger


def run_git_command(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning(f"Git command failed: {cmd} - <ERROR_TYPE>")
        return None


def get_pr_number(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            type(e).__name__
            logger.debug("EOFError: <ERROR_TYPE>")
            logger.warning("EOFError: <ERROR_TYPE>", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def discover_git_context() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def get_session_info(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(
        "Session context discovered: pr=%s branch=%s short_commit=%s",
        session_info["pr_number"],
        session_info["branch"],
        session_info["short_commit"],
    )
    return session_info


if __name__ == "__main__":
    # Demo usage
    import json

    info = get_session_info()
    logger.info(json.dumps(info, indent=2))
