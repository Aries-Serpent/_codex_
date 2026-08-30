#!/usr/bin/env python3
"""
Repository Offloaded Files Restoration Script

Purpose:
    Restore files from external storage back to original locations

Usage:
    python scripts/repository_organization/restore_offloaded_files.py [options]

    Examples:
    $ python scripts/repository_organization/restore_offloaded_files.py --category historical-coverage
    $ python scripts/repository_organization/restore_offloaded_files.py --file historical-coverage/phase1_iteration1.json
    $ python scripts/repository_organization/restore_offloaded_files.py --list

Arguments:
    --category: Restore all files from a category
    --file: Restore a specific file by relative path
    --list: List all available categories and files
    --dry-run: Show what would be restored without making changes
    --log-actions: Log restoration to action log (default: True)

Exit Codes:
    0: Success
    1: Error

Author: QA Walkthrough Agent
Last Updated: 2026-01-26
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Canonical archive root after the move; fall back to the legacy path for compatibility.
CANONICAL_OFFLOAD_ROOT = Path(".codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review")
LEGACY_OFFLOAD_ROOT = Path("misc/repo-owner-review")


def resolve_offload_root(repo_root: Path) -> Path:
    canonical = repo_root / CANONICAL_OFFLOAD_ROOT
    legacy = repo_root / LEGACY_OFFLOAD_ROOT
    return canonical if canonical.exists() or not legacy.exists() else legacy


OFFLOAD_ROOT = CANONICAL_OFFLOAD_ROOT
OFFLOAD_INDEX = OFFLOAD_ROOT / "OFFLOAD_INDEX.md"

# Category mappings to original locations
CATEGORY_MAPPINGS = {
    "historical-coverage": {
        "offload_dir": "historical-coverage",
        "restore_dir": "coverage_reports",
        "description": "Historical coverage reports",
    },
    "historical-logs": {
        "offload_dir": "historical-logs",
        "restore_dir": "logs",
        "description": "Historical log extracts",
    },
    "historical-artifacts": {
        "offload_dir": "historical-artifacts",
        "restore_dir": "artifacts",
        "description": "Historical CI/CD artifacts",
    },
    "archive-files": {
        "offload_dir": "archive-files",
        "restore_dir": "misc",  # Original locations varied
        "description": "Archive packages (.zip, .tar.gz)",
    },
    "temp-outputs": {
        "offload_dir": "temp-outputs",
        "restore_dir": "temp",  # or "output" depending on file
        "description": "Temporary outputs",
    },
    "deprecated-reports": {
        "offload_dir": "deprecated-reports",
        "restore_dir": ".codex/reports",
        "description": "Deprecated reports",
    },
}


def list_categories(repo_root: Path) -> None:
    """List all available categories and their files."""
    print("📂 Available Categories:\n")

    offload_root = resolve_offload_root(repo_root)
    for category, config in CATEGORY_MAPPINGS.items():
        offload_path = offload_root / config["offload_dir"]
        if not offload_path.exists():
            continue

        files = list(offload_path.rglob("*"))
        file_count = len([f for f in files if f.is_file() and f.name != "README.md"])

        print(f"  {category}:")
        print(f"    Description: {config['description']}")
        print(f"    Location: {offload_path.relative_to(repo_root)}")
        print(f"    Files: {file_count}")
        print(f"    Restore to: {config['restore_dir']}")
        print()


def get_files_in_category(category: str, repo_root: Path) -> list[Path]:
    """Get all files in a category."""
    config = CATEGORY_MAPPINGS.get(category)
    if not config:
        return []

    offload_path = resolve_offload_root(repo_root) / config["offload_dir"]
    if not offload_path.exists():
        return []

    files = []
    for file_path in offload_path.rglob("*"):
        if file_path.is_file() and file_path.name != "README.md":
            files.append(file_path)

    return files


def restore_file(
    source_path: Path,
    category: str,
    repo_root: Path,
    dry_run: bool = False,
) -> bool:
    """Restore a single file to its original location."""
    config = CATEGORY_MAPPINGS.get(category)
    if config is None:
        print(f"  ⚠️  Unknown category: {category!r}")
        return False
    offload_dir = resolve_offload_root(repo_root) / config["offload_dir"]

    # Calculate relative path within category
    rel_path = source_path.relative_to(offload_dir)

    # Determine destination
    # Special handling for artifacts with subdirectories
    if category == "historical-artifacts":
        dest_path = repo_root / config["restore_dir"] / rel_path
    else:
        dest_path = repo_root / config["restore_dir"] / rel_path.name

    # Check if destination already exists
    if dest_path.exists():
        print(f"  ⚠️  Destination already exists: {dest_path.relative_to(repo_root)}")
        return False

    # Restore file
    if dry_run:
        print(f"  [DRY RUN] Would restore: {source_path.relative_to(repo_root)}")
        print(f"            → {dest_path.relative_to(repo_root)}")
    else:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        print(f"  ✅ Restored: {source_path.relative_to(repo_root)}")
        print(f"            → {dest_path.relative_to(repo_root)}")

    return True


def restore_category(
    category: str,
    repo_root: Path,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Restore all files from a category."""
    files = get_files_in_category(category, repo_root)

    if not files:
        print(f"❌ No files found in category: {category}")
        return 0, 0

    print(f"📦 Restoring category: {category}")
    print(f"   Files to restore: {len(files)}")
    print()

    success_count = 0
    skip_count = 0

    for file_path in files:
        if restore_file(file_path, category, repo_root, dry_run):
            success_count += 1
        else:
            skip_count += 1

    return success_count, skip_count


def log_to_action_log(
    category: str | None,
    file_path: str | None,
    success_count: int,
    repo_root: Path,
) -> None:
    """Log restoration to action log."""
    action_log_path = repo_root / ".codex" / "action_log.ndjson"

    action_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "repository-organization-restore",
        "action": "restore_offloaded_files",
        "category": "repository_organization",
        "details": {
            "category": category,
            "file": file_path,
            "files_restored": success_count,
        },
        "outcome": "success" if success_count > 0 else "no_action",
        "impact": f"Restored {success_count} file(s) from external storage",
    }

    try:
        with open(action_log_path, "a") as f:
            f.write(json.dumps(action_entry) + "\n")
        print(f"✅ Logged to {action_log_path}")
    except Exception as e:
        print(f"⚠️ Failed to log to action log: {e}", file=sys.stderr)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Restore offloaded files from external storage"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=list(CATEGORY_MAPPINGS.keys()),
        help="Restore all files from a category",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Restore a specific file by relative path (e.g., historical-coverage/phase1_iteration1.json)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available categories and files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be restored without making changes",
    )
    parser.add_argument(
        "--log-actions",
        action="store_true",
        help="Log restoration to action log (default: True)",
    )
    parser.add_argument(
        "--no-log-actions",
        action="store_false",
        dest="log_actions",
        help="Do not log restoration to action log",
    )

    parser.set_defaults(log_actions=True)
    args = parser.parse_args()

    repo_root = Path.cwd()

    # List mode
    if args.list:
        list_categories(repo_root)
        return 0

    # Validate arguments
    if not args.category and not args.file:
        print("❌ Error: Must specify --category or --file", file=sys.stderr)
        parser.print_help()
        return 1

    success_count = 0
    skip_count = 0

    # Restore by category
    if args.category:
        success_count, skip_count = restore_category(
            args.category,
            repo_root,
            args.dry_run,
        )

    # Restore specific file
    elif args.file:
        file_parts = Path(args.file).parts
        if len(file_parts) < 2:
            print("❌ Error: File path must include category", file=sys.stderr)
            return 1

        category = file_parts[0]
        if category not in CATEGORY_MAPPINGS:
            print(f"❌ Error: Invalid category: {category}", file=sys.stderr)
            return 1

        source_path = resolve_offload_root(repo_root) / args.file
        if not source_path.exists():
            print(f"❌ Error: File not found: {source_path}", file=sys.stderr)
            return 1

        print(f"📄 Restoring file: {args.file}")
        print()

        if restore_file(source_path, category, repo_root, args.dry_run):
            success_count = 1
        else:
            skip_count = 1

    # Print summary
    print()
    print("📊 Restoration Summary:")
    print(f"  ✅ Successfully restored: {success_count}")
    print(f"  ⏭️  Skipped (already exists): {skip_count}")

    if args.dry_run:
        print("\n⚠️  DRY RUN - No files were actually restored")

    # Log to action log
    if args.log_actions and not args.dry_run and success_count > 0:
        log_to_action_log(
            args.category,
            args.file,
            success_count,
            repo_root,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
