#!/usr/bin/env python3
"""
Root Organization: Rollback Script

Automatically rollback file moves if validation fails.
Can restore from git history or backup directory.

Usage:
    python rollback_move.py --file <file> [--commit <sha>]
    python rollback_move.py --file docs/README.md
    python rollback_move.py --batch --commits <file>
    python rollback_move.py --last-operation

Physics Model: Redundancy🔀 - Provide safe rollback
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def get_last_operation() -> Optional[Dict]:
    """Get the last organization operation from action log."""
    log_file = Path('.codex/action_log.ndjson')
    if not log_file.exists():
        return None

    last_op = None
    with open(log_file, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get('action') == 'organize_root_incremental':
                    last_op = entry
            except json.JSONDecodeError:
                continue

    return last_op


def rollback_git_mv(source: str, target: str, dry_run: bool = False) -> bool:
    """Rollback a git mv operation."""
    print(f"Rolling back: {target} → {source}")

    if dry_run:
        print(f"  [DRY RUN] Would execute: git mv {target} {source}")
        return True

    try:
        # Move back
        result = subprocess.run(
            ['git', 'mv', target, source],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✓ Rolled back: {target} → {source}")
            return True
        print(f"  ❌ Rollback failed: {result.stderr}")

        # Try git checkout as fallback
        print("  Trying git checkout fallback...")
        result = subprocess.run(
            ['git', 'checkout', 'HEAD', '--', source],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✓ Restored from HEAD: {source}")
            return True
        print(f"  ❌ Checkout fallback failed: {result.stderr}")
        return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def rollback_from_commit(file_path: str, commit_sha: str = 'HEAD~1', dry_run: bool = False) -> bool:
    """Rollback a file to a specific commit."""
    print(f"Rolling back {file_path} to {commit_sha}")

    if dry_run:
        print(f"  [DRY RUN] Would execute: git checkout {commit_sha} -- {file_path}")
        return True

    try:
        result = subprocess.run(
            ['git', 'checkout', commit_sha, '--', file_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✓ Restored from {commit_sha}")
            return True
        print(f"  ❌ Rollback failed: {result.stderr}")
        return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def rollback_last_operation(dry_run: bool = False) -> bool:
    """Rollback the last organization operation."""
    last_op = get_last_operation()

    if not last_op:
        print("No previous operations found in action log")
        return False

    print(f"Last operation: {last_op['timestamp']}")
    print(f"Operation: {last_op['operation']}")
    print()

    last_op.get('details', {})

    # Extract moves to rollback
    # This depends on the structure of the logged operation
    # For now, we'll need to check git log

    print("Checking git log for recent moves...")
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '--name-status', '-10'],
            capture_output=True,
            text=True
        )

        print(result.stdout)
        print()

        response = input("Proceed with rollback of last commit? (yes/no): ")
        if response.lower() != 'yes':
            print("Rollback cancelled")
            return False

        if not dry_run:
            result = subprocess.run(
                ['git', 'reset', '--soft', 'HEAD~1'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ Successfully rolled back last commit")
                return True
            print(f"❌ Rollback failed: {result.stderr}")
            return False
        print("[DRY RUN] Would execute: git reset --soft HEAD~1")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def rollback_batch_from_file(commits_file: Path, dry_run: bool = False) -> bool:
    """Rollback multiple operations from a file listing commits."""
    if not commits_file.exists():
        print(f"Error: File not found: {commits_file}")
        return False

    with open(commits_file, 'r') as f:
        commits = [line.strip() for line in f if line.strip()]

    print(f"Rolling back {len(commits)} commits...")
    successes = 0
    failures = 0

    for commit in commits:
        parts = commit.split()
        if len(parts) >= 2:
            sha, file_path = parts[0], ' '.join(parts[1:])
            if rollback_from_commit(file_path, sha, dry_run):
                successes += 1
            else:
                failures += 1

    print(f"\nSummary: {successes} successes, {failures} failures")
    return failures == 0


def log_rollback(file_path: str, success: bool):
    """Log rollback operation."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'rollback_move',
        'file': file_path,
        'success': success,
    }

    log_file = Path('.codex/action_log.ndjson')
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Rollback file moves with validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rollback a single file to previous commit
  python rollback_move.py --file docs/README.md

  # Rollback to specific commit
  python rollback_move.py --file docs/README.md --commit abc123

  # Rollback last organization operation
  python rollback_move.py --last-operation

  # Rollback batch from file
  python rollback_move.py --batch --commits rollback_list.txt
        """
    )

    parser.add_argument('--file', type=str, help='File to rollback')
    parser.add_argument('--commit', type=str, default='HEAD~1', help='Commit SHA to restore from')
    parser.add_argument('--last-operation', action='store_true', help='Rollback last operation')
    parser.add_argument('--batch', action='store_true', help='Rollback batch from file')
    parser.add_argument('--commits', type=Path, help='File with commits to rollback')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    args = parser.parse_args()

    if args.last_operation:
        success = rollback_last_operation(args.dry_run)
        return 0 if success else 1

    if args.batch and args.commits:
        success = rollback_batch_from_file(args.commits, args.dry_run)
        return 0 if success else 1

    if args.file:
        success = rollback_from_commit(args.file, args.commit, args.dry_run)
        if success and not args.dry_run:
            log_rollback(args.file, success)
        return 0 if success else 1

    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
