#!/usr/bin/env python3
"""
Validate and fix table spacing issues in markdown files.

This script finds tables that immediately follow text/headers without
a blank line and optionally fixes them by inserting the required spacing.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def check_table_spacing(file_path: Path) -> List[Dict[str, Any]]:
    """
    Check if tables have proper spacing after headers/text.

    Returns list of issues found: [{line, text, next, line_index}]
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    issues = []
    in_code_block = False

    for i in range(len(lines) - 1):
        current = lines[i].rstrip()
        next_line = lines[i + 1].rstrip()

        # Track code block state (handle indented fences)
        if current.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip checks inside code blocks
        if in_code_block:
            continue

        # Check if next line is a table row (starts with |)
        if next_line.startswith("|"):
            # Check if current line is not empty and not a table row
            if current and not current.startswith("|"):
                # This is a problem - text/header followed immediately by table
                issues.append(
                    {
                        "line": i + 1,
                        "text": current[:80],
                        "next": next_line[:80],
                        "line_index": i,
                    }
                )

    return issues


def fix_table_spacing(
    file_path: Path, issues: List[Dict[str, Any]], dry_run: bool = False
) -> bool:
    """
    Fix table spacing issues by inserting blank lines.

    Returns True if fixes were applied or would be applied in dry-run, False otherwise.
    """
    if not issues:
        return False

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return False

    # Sort issues by line index in reverse order to maintain correct indices
    sorted_issues = sorted(issues, key=lambda x: x["line_index"], reverse=True)

    # Insert blank lines after each problematic line
    for issue in sorted_issues:
        idx = issue["line_index"]
        # Insert blank line after current line (before table)
        lines.insert(idx + 1, "\n")

    if dry_run:
        print(f"[DRY RUN] Would fix {len(issues)} issues in {file_path}")
        return True  # Return True to count as "would be fixed"

    # Write back to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}", file=sys.stderr)
        return False


def scan_directory(
    docs_dir: Path, fix: bool = False, dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Scan directory for markdown files with table spacing issues.

    Returns tuple: (files_with_issues, total_issues, files_fixed)
    """
    all_issues = {}

    for md_file in docs_dir.rglob("*.md"):
        issues = check_table_spacing(md_file)
        if issues:
            all_issues[md_file] = issues

    files_with_issues = len(all_issues)
    total_issues = sum(len(v) for v in all_issues.values())
    files_fixed = 0

    if not all_issues:
        print("✅ No table spacing issues found!")
        return 0, 0, 0

    print(f"\n{'=' * 80}")
    print(f"Found {files_with_issues} files with {total_issues} table spacing issues")
    print(f"{'=' * 80}\n")

    for file_path, issues in sorted(all_issues.items(), key=lambda kv: str(kv[0])):
        try:
            rel_path = file_path.relative_to(docs_dir.parent)
        except ValueError:
            # Fallback if relative_to fails
            rel_path = file_path
        print(f"\n📄 {rel_path}:")
        print(f"   {len(issues)} issue(s) found")

        for issue in issues[:3]:  # Show first 3 issues per file
            print(f"   Line {issue['line']}: '{issue['text']}'")
            print(f"            -> '{issue['next']}'")

        if len(issues) > 3:
            print(f"   ... and {len(issues) - 3} more")

        if fix:
            if fix_table_spacing(file_path, issues, dry_run):
                files_fixed += 1
                print(f"   ✅ Fixed {len(issues)} issues")
            elif not dry_run:
                print("   ❌ Failed to fix")

    print(f"\n{'=' * 80}")
    print(f"Summary: {files_with_issues} files, {total_issues} issues")
    if fix:
        if dry_run:
            print(f"[DRY RUN] Would fix: {files_fixed} files")
        else:
            print(f"Fixed: {files_fixed} files")
    print(f"{'=' * 80}\n")

    return files_with_issues, total_issues, files_fixed


def main():
    parser = argparse.ArgumentParser(
        description="Validate and fix table spacing in markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check for issues
  python scripts/validate_table_spacing.py --check

  # Fix issues (dry run)
  python scripts/validate_table_spacing.py --fix --dry-run

  # Apply fixes
  python scripts/validate_table_spacing.py --fix

  # Scan specific directory
  python scripts/validate_table_spacing.py --check --dir docs/review
        """,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for table spacing issues (default if no --fix)",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix table spacing issues by inserting blank lines",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )

    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("docs"),
        help="Directory to scan (default: docs)",
    )

    args = parser.parse_args()

    # Default to check mode if neither specified
    if not args.check and not args.fix:
        args.check = True

    docs_dir = args.dir
    if not docs_dir.exists():
        print(f"❌ Error: Directory {docs_dir} does not exist", file=sys.stderr)
        return 1

    if args.check and not args.fix:
        files_with_issues, total_issues, _ = scan_directory(docs_dir, fix=False)
        return 0 if files_with_issues == 0 else 1

    if args.fix:
        files_with_issues, total_issues, files_fixed = scan_directory(
            docs_dir, fix=True, dry_run=args.dry_run
        )

        if args.dry_run:
            return 0

        return 0 if files_fixed == files_with_issues else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
