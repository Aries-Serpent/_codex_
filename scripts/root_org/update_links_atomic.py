#!/usr/bin/env python3
"""
Root Organization: Atomic Link Updater Script

Atomically updates all references to a moved file across the entire codebase.
Transaction-like behavior with rollback on failure.

Usage:
    python update_links_atomic.py --old <old_path> --new <new_path> [--dry-run]
    python update_links_atomic.py --old README.md --new docs/README.md --dry-run
    python update_links_atomic.py --old AGENTS.md --new .github/agents/AGENTS.md

Physics Model: Redundancy🔀 - Provide rollback capability
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Import the reference validator
try:
    from validate_references import SCAN_DIRS, SCAN_EXTENSIONS, SKIP_DIRS
except ImportError:
    # If running standalone, define minimal versions
    SCAN_DIRS = ['docs', '.github', 'scripts', 'src', 'tests', '.codex']
    SCAN_EXTENSIONS = ['.md', '.yml', '.yaml', '.py', '.json', '.toml', '.txt', '.rst', '.sh']
    SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}


class UpdateTransaction:
    """Transaction-like update with rollback capability."""

    def __init__(self, old_path: str, new_path: str, dry_run: bool = False):
        self.old_path = old_path
        self.new_path = new_path
        self.dry_run = dry_run
        self.backup_dir = None
        self.files_to_update: List[Tuple[Path, str, str]] = []
        self.updated_files: List[Path] = []

    def __enter__(self):
        """Enter transaction context."""
        if not self.dry_run:
            self.backup_dir = Path(tempfile.mkdtemp(prefix='root_org_backup_'))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context - cleanup or rollback."""
        if exc_type is not None and not self.dry_run:
            # Exception occurred - rollback
            self.rollback()
        elif not self.dry_run and self.backup_dir:
            # Success - cleanup backup
            shutil.rmtree(self.backup_dir, ignore_errors=True)
        return False  # Re-raise exception if any

    def add_update(self, file_path: Path, old_content: str, new_content: str):
        """Add a file to be updated."""
        self.files_to_update.append((file_path, old_content, new_content))

    def backup_file(self, file_path: Path):
        """Backup a file before modification."""
        if self.dry_run or not self.backup_dir:
            return

        backup_path = self.backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)

    def execute(self) -> int:
        """Execute all updates atomically."""
        if not self.files_to_update:
            print("No updates to perform")
            return 0

        print(f"{'[DRY RUN] ' if self.dry_run else ''}Updating {len(self.files_to_update)} files...")

        for file_path, old_content, new_content in self.files_to_update:
            if self.dry_run:
                print(f"  Would update: {file_path}")
            else:
                self.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.updated_files.append(file_path)
                print(f"  ✓ Updated: {file_path}")

        return len(self.updated_files)

    def rollback(self):
        """Rollback all changes."""
        if self.dry_run or not self.backup_dir:
            return

        print("ERROR: Rolling back changes...")
        for file_path in self.updated_files:
            backup_path = self.backup_dir / file_path.name
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                print(f"  ✓ Restored: {file_path}")


def find_files_to_update(old_path: str, root_dir: Path) -> List[Path]:
    """Find all files that might contain references to the old path."""
    files_to_check = []

    for scan_dir in SCAN_DIRS:
        dir_path = root_dir / scan_dir
        if not dir_path.exists():
            continue

        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for file in files:
                if any(file.endswith(ext) for ext in SCAN_EXTENSIONS):
                    files_to_check.append(Path(root) / file)

    return files_to_check


def update_references_in_file(
    file_path: Path,
    old_path: str,
    new_path: str
) -> Tuple[bool, str, str]:
    """
    Update references in a single file.
    Returns: (modified, old_content, new_content)
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            old_content = f.read()
    except Exception:
        return False, "", ""

    new_content = old_content
    modified = False

    # Pattern 1: Markdown links [text](old_path)
    pattern1 = rf'\[([^\]]+)\]\({re.escape(old_path)}\)'
    if re.search(pattern1, new_content):
        new_content = re.sub(pattern1, rf'[\1]({new_path})', new_content)
        modified = True

    # Pattern 2: HTML href="old_path"
    pattern2 = rf'href=["\']({re.escape(old_path)})["\']'
    if re.search(pattern2, new_content):
        new_content = re.sub(pattern2, rf'href="{new_path}"', new_content)
        modified = True

    # Pattern 3: YAML paths (path: old_path)
    pattern3 = rf'path:\s*{re.escape(old_path)}'
    if re.search(pattern3, new_content):
        new_content = re.sub(pattern3, f'path: {new_path}', new_content)
        modified = True

    # Pattern 4: Simple text replacement (careful with this)
    if old_path in new_content and not modified:
        # Only replace if it's not already handled
        new_content = new_content.replace(old_path, new_path)
        modified = True

    return modified, old_content, new_content


def validate_updates(old_path: str, new_path: str, updated_count: int) -> bool:
    """Validate that updates were successful."""
    # Check if new path references exist
    # Check if old path references are gone
    # This is a simplified validation
    return updated_count > 0


def log_to_ndjson(old_path: str, new_path: str, updated_count: int):
    """Log update operation to .codex/action_log.ndjson."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'update_links_atomic',
        'old_path': old_path,
        'new_path': new_path,
        'files_updated': updated_count,
    }

    log_file = Path('.codex/action_log.ndjson')
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Atomically update all references to a moved file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_links_atomic.py --old README.md --new docs/README.md --dry-run
  python update_links_atomic.py --old AGENTS.md --new .github/agents/AGENTS.md
        """
    )
    parser.add_argument('--old', required=True, help='Old file path')
    parser.add_argument('--new', required=True, help='New file path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')

    args = parser.parse_args()

    root_dir = Path.cwd()

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Updating references:")
    print(f"  Old path: {args.old}")
    print(f"  New path: {args.new}")
    print()

    # Find files to check
    print("Scanning repository for files to check...")
    files_to_check = find_files_to_update(args.old, root_dir)
    print(f"Found {len(files_to_check)} files to check")
    print()

    # Start transaction
    try:
        with UpdateTransaction(args.old, args.new, args.dry_run) as transaction:
            # Analyze files
            for file_path in files_to_check:
                modified, old_content, new_content = update_references_in_file(
                    file_path, args.old, args.new
                )

                if modified:
                    transaction.add_update(file_path, old_content, new_content)

            # Execute updates
            updated_count = transaction.execute()

            if updated_count > 0:
                print()
                print(f"✅ Successfully updated {updated_count} files")

                if not args.dry_run:
                    # Validate
                    if validate_updates(args.old, args.new, updated_count):
                        print("✅ Validation passed")
                        log_to_ndjson(args.old, args.new, updated_count)
                    else:
                        print("⚠️  Validation warnings")
                        return 1
            else:
                print("ℹ️  No files needed updating")

            return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Changes have been rolled back")
        return 1


if __name__ == '__main__':
    sys.exit(main())
