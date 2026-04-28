#!/usr/bin/env python3
"""
Resolve Merge Conflicts

Purpose:
    Main execution script

Usage:
    python scripts/security/resolve_merge_conflicts.py [options]

    Examples:
    $ python scripts/security/resolve_merge_conflicts.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class ConflictStats(NamedTuple):
    """Statistics for conflict resolution."""

    total_files: int
    conflicted_files: int
    resolved_files: int
    failed_files: int


def run_command(cmd: list[str], check: bool = True) -> tuple[int, str, str]:
    """
    Run a shell command and return (returncode, stdout, stderr).

    Args:
        cmd: Command and arguments as list
        check: Whether to raise exception on non-zero exit code

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent.parent.parent,
    )

    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"STDOUT: {result.stdout}", file=sys.stderr)
        print(f"STDERR: {result.stderr}", file=sys.stderr)

    return result.returncode, result.stdout, result.stderr


def get_conflicted_files() -> list[str]:
    """
    Get list of files with merge conflicts.

    Returns:
        List of file paths with conflicts
    """
    returncode, stdout, stderr = run_command(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False
    )

    if returncode != 0:
        return []

    files = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
    return files


def get_all_pr_files() -> list[str]:
    """
    Get list of all files changed in this PR.

    Returns:
        List of file paths changed in PR
    """
    # Get the base commit (parent of our first commit)
    returncode, stdout, stderr = run_command(
        ["git", "log", "--oneline", "--reverse", "--format=%H"],
        check=False
    )

    if returncode != 0:
        print("Error: Could not get commit history", file=sys.stderr)
        return []

    commits = stdout.strip().split('\n')
    if len(commits) < 2:
        print("Error: Not enough commits to determine base", file=sys.stderr)
        return []

    # Our first commit in this PR branch
    first_commit = commits[-3] if len(commits) >= 3 else commits[0]

    # Get parent of first commit (the base)
    returncode, stdout, stderr = run_command(
        ["git", "rev-parse", f"{first_commit}^"],
        check=False
    )

    if returncode != 0:
        # Try alternative: use the merge base
        returncode, stdout, stderr = run_command(
            ["git", "merge-base", "HEAD", "HEAD~3"],
            check=False
        )

        if returncode != 0:
            print("Error: Could not determine base commit", file=sys.stderr)
            return []

    base_commit = stdout.strip()

    # Get all files changed from base to HEAD
    returncode, stdout, stderr = run_command(
        ["git", "diff", "--name-only", f"{base_commit}..HEAD"],
        check=False
    )

    if returncode != 0:
        print(f"Error: Could not get changed files from {base_commit}", file=sys.stderr)
        return []

    files = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
    return files


def resolve_conflict_accept_ours(filepath: str) -> bool:
    """
    Resolve conflict in a file by accepting our version (--ours).

    Args:
        filepath: Path to conflicted file

    Returns:
        True if resolved successfully, False otherwise
    """
    # Use git checkout --ours to accept our version
    returncode, stdout, stderr = run_command(
        ["git", "checkout", "--ours", filepath],
        check=False
    )

    if returncode != 0:
        print(f"Failed to resolve {filepath}: {stderr}", file=sys.stderr)
        return False

    # Stage the resolved file
    returncode, stdout, stderr = run_command(
        ["git", "add", filepath],
        check=False
    )

    if returncode != 0:
        print(f"Failed to stage {filepath}: {stderr}", file=sys.stderr)
        return False

    return True


def check_merge_in_progress() -> bool:
    """
    Check if a merge is currently in progress.

    Returns:
        True if merge is in progress, False otherwise
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    merge_head = repo_root / ".git" / "MERGE_HEAD"
    return merge_head.exists()


def print_status_report(stats: ConflictStats, pr_files: list[str]):
    """Print a summary report of the conflict resolution."""
    print()
    print("=" * 70)
    print("MERGE CONFLICT RESOLUTION REPORT")
    print("=" * 70)
    print()
    print(f"Total files in PR:        {len(pr_files)}")
    print(f"Files with conflicts:     {stats.conflicted_files}")
    print(f"Successfully resolved:    {stats.resolved_files}")
    print(f"Failed to resolve:        {stats.failed_files}")
    print()

    if stats.failed_files == 0:
        print("✅ All conflicts resolved successfully!")
        print()
        print("Next steps:")
        print("  1. Review the resolved files")
        print("  2. Complete the merge with: git merge --continue")
        print("  3. Or commit the resolution with: git commit")
    else:
        print("⚠️  Some conflicts could not be automatically resolved")
        print()
        print("Manual intervention required for failed files")

    print()
    print("=" * 70)


def main():
    """Main entry point for merge conflict resolution."""
    print("Merge Conflict Resolution Tool for PR #2717")
    print("=" * 70)
    print()

    # Check if merge is in progress
    if not check_merge_in_progress():
        print("ℹ️  No merge in progress detected")
        print()
        print("This script should be run AFTER attempting a merge/rebase")
        print("that results in conflicts.")
        print()
        print("To use this script:")
        print("  1. First attempt the merge: git merge <target-branch>")
        print("  2. If conflicts occur, run this script")
        print("  3. The script will accept all 'ours' (incoming) changes")
        print()

        # Get list of files that would be affected
        pr_files = get_all_pr_files()
        if pr_files:
            print(f"Files changed in this PR: {len(pr_files)}")
            print()
            print("Sample files:")
            for f in pr_files[:10]:
                print(f"  - {f}")
            if len(pr_files) > 10:
                print(f"  ... and {len(pr_files) - 10} more")

        return 0

    print("✓ Merge in progress detected")
    print()

    # Get conflicted files
    conflicted = get_conflicted_files()

    if not conflicted:
        print("✓ No unresolved conflicts found")
        print()
        print("The merge may already be resolved.")
        return 0

    print(f"Found {len(conflicted)} files with conflicts")
    print()

    # Get all PR files for reference
    pr_files = get_all_pr_files()

    # Resolve each conflict by accepting our version
    resolved = 0
    failed = 0

    print("Resolving conflicts by accepting our (incoming) changes...")
    print()

    for i, filepath in enumerate(conflicted, 1):
        print(f"[{i}/{len(conflicted)}] Resolving {filepath}...", end=" ")

        if resolve_conflict_accept_ours(filepath):
            print("✓")
            resolved += 1
        else:
            print("✗")
            failed += 1

    # Print summary
    stats = ConflictStats(
        total_files=len(pr_files),
        conflicted_files=len(conflicted),
        resolved_files=resolved,
        failed_files=failed,
    )

    print_status_report(stats, pr_files)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
