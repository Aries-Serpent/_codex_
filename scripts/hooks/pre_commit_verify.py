#!/usr/bin/env python3
"""
Pre-commit Verification Hook

This hook verifies that all expected files from the action_log.ndjson
are staged for commit, preventing accidental omission of files.

The hook:
1. Parses the action_log.ndjson for recent file operations
2. Extracts expected files (create, edit, update operations)
3. Compares against staged files
4. Reports missing files that should be committed

Usage:
    # As pre-commit hook
    python scripts/hooks/pre_commit_verify.py

    # Manual verification
    python scripts/hooks/pre_commit_verify.py --check-only
    python scripts/hooks/pre_commit_verify.py --since "2026-02-05T00:00:00Z"
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# File patterns to ignore (temp files, build artifacts, etc.)
IGNORE_PATTERNS = [
    r'^/tmp/',
    r'^tmp/',
    r'\.pyc$',
    r'__pycache__',
    r'\.egg-info',
    r'\.pytest_cache',
    r'\.mypy_cache',
    r'\.coverage',
    r'^\.git/',
    r'^node_modules/',
    r'^dist/',
    r'^build/',
    r'^\.venv/',
    r'^venv/',
    r'\.DS_Store',
]

# Operations that indicate a file should be committed
COMMIT_OPERATIONS = ['create', 'created', 'edit', 'edited', 'update', 'updated', 'modify', 'modified']


def get_repo_root() -> Path:
    """Get the repository root directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return Path.cwd()


def get_staged_files() -> set[str]:
    """Get the list of files staged for commit."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
    except subprocess.CalledProcessError:
        logger.warning("Could not get staged files from git")
        return set()


def get_modified_files() -> set[str]:
    """Get the list of modified but unstaged files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
    except subprocess.CalledProcessError:
        return set()


def get_untracked_files() -> set[str]:
    """Get the list of untracked files."""
    try:
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True,
            text=True,
            check=True
        )
        return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
    except subprocess.CalledProcessError:
        return set()


def load_gitignore_patterns(repo_root: Path) -> list[str]:
    """Load patterns from .gitignore file."""
    gitignore_path = repo_root / '.gitignore'
    patterns = []

    if gitignore_path.exists():
        with open(gitignore_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Convert gitignore pattern to regex
                    pattern = line.replace('.', r'\.').replace('*', '.*').replace('?', '.')
                    if line.startswith('/'):
                        pattern = '^' + pattern[1:]
                    patterns.append(pattern)

    return patterns


def should_ignore_file(filepath: str, extra_patterns: Optional[list[str]] = None) -> bool:
    """Check if a file should be ignored based on patterns."""
    all_patterns = IGNORE_PATTERNS + (extra_patterns or [])

    return any(re.search(pattern, filepath) for pattern in all_patterns)


def parse_action_log(
    log_path: Path,
    since: Optional[datetime] = None,
    session_id: Optional[str] = None
) -> list[dict]:
    """Parse the action log and extract file operations."""
    if not log_path.exists():
        logger.warning(f"Action log not found: {log_path}")
        return []

    operations = []

    with open(log_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                logger.debug(f"Skipping malformed JSON at line {line_num}")
                continue

            # Filter by timestamp if specified
            if since and 'timestamp' in entry:
                try:
                    entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    if entry_time < since:
                        continue
                except (ValueError, TypeError):
                    logger.debug("Suppressed exception in handler", exc_info=True)
            # Filter by session if specified
            if session_id and entry.get('session_id') != session_id:
                continue

            # Check if this is a file operation
            action = entry.get('action', '').lower()
            if action in COMMIT_OPERATIONS and 'path' in entry:
                operations.append(entry)

    return operations


def extract_expected_files(operations: list[dict], repo_root: Path) -> set[str]:
    """Extract expected files from operations list."""
    expected = set()

    for op in operations:
        filepath = op.get('path', '')

        if not filepath:
            continue

        # Normalize path
        if filepath.startswith('/'):
            # Absolute path - make relative to repo root
            try:
                filepath = str(Path(filepath).relative_to(repo_root))
            except ValueError:
                # Path is outside repo
                continue

        # Check if file should be ignored
        if should_ignore_file(filepath):
            continue

        # Check if file exists
        full_path = repo_root / filepath
        if full_path.exists():
            expected.add(filepath)

    return expected


def verify_staged_files(
    expected: set[str],
    staged: set[str],
    modified: set[str],
    untracked: set[str]
) -> tuple[set[str], set[str], set[str]]:
    """
    Verify that expected files are staged.

    Returns:
        Tuple of (staged_expected, missing_modified, missing_untracked)
    """
    staged_expected = expected & staged
    missing = expected - staged

    missing_modified = missing & modified
    missing_untracked = missing & untracked

    return staged_expected, missing_modified, missing_untracked


def generate_report(
    expected: set[str],
    staged_expected: set[str],
    missing_modified: set[str],
    missing_untracked: set[str]
) -> str:
    """Generate a verification report."""
    lines = []
    lines.append("=" * 60)
    lines.append("Pre-commit Verification Report")
    lines.append("=" * 60)
    lines.append("")

    total = len(expected)
    staged_count = len(staged_expected)
    missing_count = len(missing_modified) + len(missing_untracked)

    lines.append(f"Expected files from action log: {total}")
    lines.append(f"Correctly staged: {staged_count} ✅")
    lines.append(f"Missing from staging: {missing_count}")
    lines.append("")

    if staged_expected:
        lines.append("✅ Staged Files (Correct):")
        for f in sorted(staged_expected):
            lines.append(f"   - {f}")
        lines.append("")

    if missing_modified:
        lines.append("⚠️  Modified but not staged (need `git add`):")
        for f in sorted(missing_modified):
            lines.append(f"   - {f}")
        lines.append("")

    if missing_untracked:
        lines.append("⚠️  Untracked files (need `git add`):")
        for f in sorted(missing_untracked):
            lines.append(f"   - {f}")
        lines.append("")

    if missing_modified or missing_untracked:
        lines.append("To stage missing files:")
        all_missing = sorted(missing_modified | missing_untracked)
        for f in all_missing[:5]:
            lines.append(f"   git add {f}")
        if len(all_missing) > 5:
            lines.append(f"   ... and {len(all_missing) - 5} more")
        lines.append("")

    lines.append("=" * 60)

    return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify expected files are staged for commit"
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help="Only check, don't fail on missing files"
    )
    parser.add_argument(
        '--since',
        type=str,
        help="Only check operations since this timestamp (ISO format)"
    )
    parser.add_argument(
        '--session-id',
        type=str,
        help="Only check operations from this session"
    )
    parser.add_argument(
        '--action-log',
        type=str,
        help="Path to action log file"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress output unless there are issues"
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help="Check operations from last N hours (default: 24)"
    )

    args = parser.parse_args()

    # Get repo root
    repo_root = get_repo_root()

    # Determine action log path
    if args.action_log:
        action_log_path = Path(args.action_log)
    else:
        action_log_path = repo_root / '.codex' / 'action_log.ndjson'

    # Determine time filter
    since = None
    if args.since:
        try:
            since = datetime.fromisoformat(args.since.replace('Z', '+00:00'))
        except ValueError:
            logger.error(f"Invalid timestamp format: {args.since}")
            sys.exit(1)
    elif args.hours:
        since = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    # Load gitignore patterns
    gitignore_patterns = load_gitignore_patterns(repo_root)

    # Parse action log
    operations = parse_action_log(
        action_log_path,
        since=since,
        session_id=args.session_id
    )

    if not operations:
        if not args.quiet:
            logger.info("No file operations found in action log")
        sys.exit(0)

    # Extract expected files
    expected = extract_expected_files(operations, repo_root)

    # Filter by gitignore
    expected = {f for f in expected if not should_ignore_file(f, gitignore_patterns)}

    if not expected:
        if not args.quiet:
            logger.info("No committable files found in action log")
        sys.exit(0)

    # Get git status
    staged = get_staged_files()
    modified = get_modified_files()
    untracked = get_untracked_files()

    # Verify
    staged_expected, missing_modified, missing_untracked = verify_staged_files(
        expected, staged, modified, untracked
    )

    # Generate report
    report = generate_report(
        expected,
        staged_expected,
        missing_modified,
        missing_untracked
    )

    # Output
    has_issues = bool(missing_modified or missing_untracked)

    if has_issues or not args.quiet:
        print(report)

    # Exit code
    if has_issues and not args.check_only:
        logger.error("Some expected files are not staged!")
        sys.exit(1)
    elif has_issues:
        logger.warning("Some expected files are not staged (check-only mode)")
        sys.exit(0)
    else:
        if not args.quiet:
            logger.info("All expected files are staged ✅")
        sys.exit(0)


if __name__ == "__main__":
    main()
