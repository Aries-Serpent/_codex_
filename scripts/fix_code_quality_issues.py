#!/usr/bin/env python3
"""
Automated code quality fixes for PR #3133.
Addresses 5,650+ Ruff violations across the codebase.

Usage:
    python scripts/fix_code_quality_issues.py [--dry-run] [--phase N]

Options:
    --dry-run    Show what would be fixed without making changes
    --phase N    Run specific phase only (1-4), default: all phases
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], description: str, check: bool = False) -> Tuple[bool, str]:
    """
    Run command and return success status and output.

    Args:
        cmd: Command and arguments to run
        description: Human-readable description of the command
        check: Whether to check return code (default: False for ruff)

    Returns:
        Tuple of (success, output)
    """
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = result.stdout + result.stderr

        print(output)

        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True, output
        # Ruff exits 1 if issues found, but fixes may have been applied
        print(f"⚠️  {description} - Completed with warnings (exit code {result.returncode})")
        return True, output
    except Exception as e:
        print(f"❌ {description} - FAILED: {e}")
        return False, str(e)


def get_ruff_statistics() -> dict:
    """Get current Ruff issue statistics."""
    try:
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/", ".codex/", "--statistics"],
            capture_output=True,
            text=True
        )

        stats = {}
        for line in result.stdout.split('\n'):
            if line.strip():
                # Parse lines like "541  F541  f-string-missing-placeholders"
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    count = int(parts[0])
                    code = parts[1]
                    stats[code] = count

        return stats
    except Exception as e:
        print(f"⚠️  Could not get statistics: {e}")
        return {}


def phase_1_fix_f541(dry_run: bool = False) -> bool:
    """Phase 1: Fix F541 (unnecessary f-strings) - highest volume."""
    cmd = ["ruff", "check", "--select", "F541", "--fix"]
    if not dry_run:
        cmd.append("--unsafe-fixes")
    else:
        cmd.append("--diff")
    cmd.extend(["src/", "tests/", ".codex/"])

    success, _ = run_command(cmd, "Phase 1: Fix F541 (unnecessary f-strings)")
    return success


def phase_2_fix_all_auto(dry_run: bool = False) -> bool:
    """Phase 2: Fix all auto-fixable issues."""
    cmd = ["ruff", "check", "--fix"]
    if not dry_run:
        cmd.append("--unsafe-fixes")
    else:
        cmd.append("--diff")
    cmd.extend(["src/", "tests/", ".codex/"])

    success, _ = run_command(cmd, "Phase 2: Fix all auto-fixable Ruff issues")
    return success


def phase_3_fix_imports(dry_run: bool = False) -> bool:
    """Phase 3: Fix import sorting."""
    cmd = ["ruff", "check", "--select", "I", "--fix"]
    if dry_run:
        cmd.append("--diff")
    cmd.extend(["src/", "tests/", ".codex/"])

    success, _ = run_command(cmd, "Phase 3: Fix import ordering (I)")
    return success


def phase_4_format_code(dry_run: bool = False) -> bool:
    """Phase 4: Format code with ruff formatter."""
    cmd = ["ruff", "format"]
    if dry_run:
        cmd.append("--diff")
    cmd.extend(["src/", "tests/", ".codex/"])

    success, _ = run_command(cmd, "Phase 4: Format code with Ruff")
    return success


def verify_fixes() -> None:
    """Verification: Count remaining issues."""
    print("\n" + "="*70)
    print("📊 VERIFICATION: Counting remaining issues")
    print("="*70)

    stats_after = get_ruff_statistics()

    if stats_after:
        print("\n📈 Remaining issues by code:")
        total = 0
        for code, count in sorted(stats_after.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {code:6s}: {count:5d} issues")
            total += count

        print(f"\n  {'TOTAL':6s}: {total:5d} issues")
    else:
        print("\n✅ No issues remaining or could not parse statistics")

    # Run full check to see summary
    result = subprocess.run(
        ["ruff", "check", "src/", "tests/", ".codex/"],
        capture_output=True,
        text=True
    )

    # Look for summary lines
    for line in result.stdout.split('\n'):
        if 'Found' in line or 'fixed' in line:
            print(f"  {line}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated code quality fixes for PR #3133"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be fixed without making changes"
    )
    parser.add_argument(
        "--phase", type=int, choices=[1, 2, 3, 4],
        help="Run specific phase only (1-4)"
    )

    args = parser.parse_args()

    print("🚀 Starting automated code quality fixes for PR #3133")
    print(f"Working directory: {Path.cwd()}")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'LIVE (will modify files)'}")
    print()

    # Get initial statistics
    print("📊 Initial issue count:")
    stats_before = get_ruff_statistics()
    if stats_before:
        total_before = sum(stats_before.values())
        print(f"  Total issues: {total_before}")
        top_5 = sorted(stats_before.items(), key=lambda x: x[1], reverse=True)[:5]
        for code, count in top_5:
            print(f"    {code}: {count}")

    success = True

    # Run phases
    if args.phase is None or args.phase == 1:
        success = phase_1_fix_f541(args.dry_run) and success

    if args.phase is None or args.phase == 2:
        success = phase_2_fix_all_auto(args.dry_run) and success

    if args.phase is None or args.phase == 3:
        success = phase_3_fix_imports(args.dry_run) and success

    if args.phase is None or args.phase == 4:
        success = phase_4_format_code(args.dry_run) and success

    # Verification
    if not args.dry_run:
        verify_fixes()

    print("\n" + "="*70)
    if success:
        if args.dry_run:
            print("✅ Dry run completed successfully")
            print("\nTo apply fixes, run without --dry-run:")
            print("  python scripts/fix_code_quality_issues.py")
        else:
            print("✅ Code quality fixes completed successfully")
            print("\nNext steps:")
            print("  1. Review changes: git diff")
            print("  2. Run tests: pytest tests/ -v")
            print("  3. Commit: git add -A && git commit -m 'fix: auto-resolve Ruff violations'")
        return 0
    print("⚠️  Code quality fixes completed with warnings")
    print("Review the output above for details")
    return 1


if __name__ == "__main__":
    sys.exit(main())
