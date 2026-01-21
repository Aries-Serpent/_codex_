#!/usr/bin/env python3
"""
Rename files with Windows-incompatible characters in filenames.

Usage:
    python scripts/remediation/rename_windows_incompatible_files.py --dry-run
    python scripts/remediation/rename_windows_incompatible_files.py --execute
"""
from pathlib import Path
import argparse
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codex.utils.path_utils import sanitize_filename


def find_incompatible_files(root: Path) -> list[tuple[Path, Path]]:
    """
    Find files with Windows-incompatible characters.
    
    Returns:
        List of (original_path, sanitized_path) tuples
    """
    renames = []
    
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        
        # Check if filename contains illegal characters
        if any(char in path.name for char in '<>:"/\\|?*'):
            sanitized_name = sanitize_filename(path.name)
            new_path = path.parent / sanitized_name
            renames.append((path, new_path))
    
    return renames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without making changes"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the renames"
    )
    
    args = parser.parse_args()
    
    if not (args.dry_run or args.execute):
        parser.error("Must specify either --dry-run or --execute")
    
    repo_root = Path(__file__).resolve().parents[2]
    renames = find_incompatible_files(repo_root)
    
    if not renames:
        print("✅ No files with Windows-incompatible names found")
        return 0
    
    print(f"Found {len(renames)} file(s) to rename:\n")
    
    for old_path, new_path in renames:
        rel_old = old_path.relative_to(repo_root)
        rel_new = new_path.relative_to(repo_root)
        
        print(f"  {rel_old}")
        print(f"    → {rel_new}\n")
    
    if args.execute:
        for old_path, new_path in renames:
            old_path.rename(new_path)
            print(f"✅ Renamed: {old_path.relative_to(repo_root)}")
        
        print(f"\n✅ Successfully renamed {len(renames)} file(s)")
    else:
        print("🔍 Dry run complete. Use --execute to perform renames.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
