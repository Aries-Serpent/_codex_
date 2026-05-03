#!/usr/bin/env python3
"""
Validate and fix markdown code fence formatting issues.

Detects:
- Malformed code fences (```text, ```bash, etc. without closing ```)
- Unmatched fence pairs
- Fences inside other fences (nested)
"""

import argparse
import sys
from pathlib import Path
from typing import Any


def check_code_fences(file_path: Path) -> list[dict[str, Any]]:
    """
    Check for malformed code fences in markdown file.

    Returns list of issues: [{line, type, fence, suggestion}]

    Detects:
    - unclosed_fence: Opening fence without matching close
    - nested_fence: Fence inside another fence
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    issues = []
    fence_stack = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for code fence (3 or more backticks)
        if stripped.startswith("```"):
            if not fence_stack:
                # Opening fence - can have language specifier
                fence_stack.append({
                    'line': i + 1,
                    'content': stripped,
                    'has_lang': len(stripped) > 3 and stripped[3:].strip() != ''
                })
            else:
                # Potential closing fence - should be just ```
                # If it has a language specifier, it might be nested
                if len(stripped) > 3 and stripped[3:].strip() != '':
                    # This looks like an opening fence, but we're already in a fence
                    issues.append({
                        'line': i + 1,
                        'type': 'nested_fence',
                        'fence': stripped,
                        'suggestion': 'Nested code fence detected - may cause rendering issues'
                    })
                else:
                    # Proper closing fence
                    fence_stack.pop()

    # Check for unclosed fences
    for fence in fence_stack:
        issues.append({
            'line': fence['line'],
            'type': 'unclosed_fence',
            'fence': fence['content'],
            'suggestion': 'Missing closing ``` fence'
        })

    return issues


def fix_code_fences(file_path: Path, issues: list[dict[str, Any]], dry_run: bool = False) -> bool:
    """
    Fix code fence issues.

    Returns True if fixes were applied or would be applied in dry-run.
    """
    if not issues:
        return False

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return False

    # Track if we made any changes
    changes_made = False

    # Apply fixes for unclosed fences
    for issue in issues:
        if issue['type'] == 'unclosed_fence':
            # Append closing fence at end of file
            if not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append('```\n')
            changes_made = True

    # Don't auto-fix nested fences (too risky)
    # Just report them

    if dry_run:
        if changes_made:
            print(f"[DRY RUN] Would fix {len([i for i in issues if i['type'] == 'unclosed_fence'])} unclosed fences in {file_path}")
        return changes_made

    if not changes_made:
        return False

    # Write back only if changes were made
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}", file=sys.stderr)
        return False


def scan_directory(docs_dir: Path, fix: bool = False, dry_run: bool = False):
    """Scan directory for code fence issues."""
    all_issues = {}

    for md_file in docs_dir.rglob("*.md"):
        issues = check_code_fences(md_file)
        if issues:
            all_issues[md_file] = issues

    files_with_issues = len(all_issues)
    total_issues = sum(len(v) for v in all_issues.values())
    files_fixed = 0

    if not all_issues:
        print("✅ No code fence issues found!")
        return 0, 0, 0

    print(f"\n{'=' * 80}")
    print(f"Found {files_with_issues} files with {total_issues} code fence issues")
    print(f"{'=' * 80}\n")

    for file_path, issues in sorted(all_issues.items(), key=lambda kv: str(kv[0])):
        try:
            rel_path = file_path.relative_to(docs_dir.parent)
        except ValueError:
            rel_path = file_path

        print(f"\n📄 {rel_path}:")
        print(f"   {len(issues)} issue(s) found")

        for issue in issues:
            print(f"   Line {issue['line']}: {issue['type']}")
            print(f"            Fence: '{issue['fence']}'")
            print(f"            Suggestion: {issue['suggestion']}")

        if fix:
            if fix_code_fences(file_path, issues, dry_run):
                files_fixed += 1
                if not dry_run:
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
        description="Validate and fix code fence formatting in markdown files",
        epilog="""
Examples:
  # Check for issues
  python scripts/validate_code_fences.py --check

  # Fix issues (dry run)
  python scripts/validate_code_fences.py --fix --dry-run

  # Apply fixes
  python scripts/validate_code_fences.py --fix
        """,
    )

    parser.add_argument(
        "--check", action="store_true", help="Check for code fence issues"
    )

    parser.add_argument(
        "--fix", action="store_true", help="Fix code fence issues"
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed"
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
