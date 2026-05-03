#!/usr/bin/env python3
"""
Copilot Agent Auto-Fix Helper
Orchestrates automated fixes for CI issues with progress tracking.
"""

import json
import subprocess
import sys
from pathlib import Path


def parse_diagnostic_report(json_path: str) -> dict:
    """Load and parse diagnostic JSON report."""
    try:
        with open(json_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading diagnostic report: {e}")
        sys.exit(1)


def apply_fixes_by_pattern(pattern: int, repo_root: Path) -> bool:
    """
    Apply fixes for specific pattern.

    Returns:
        True if fixes applied successfully
    """
    print(f"\n🔧 Applying fixes for Pattern {pattern}...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/ci/auto_fix_common_issues.py",
                "--pattern", str(pattern)
            ],
            cwd=repo_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Pattern {pattern} fixes applied successfully")
            return True
        print(f"⚠️  Pattern {pattern} fixes completed with warnings")
        print(result.stdout)
        return True

    except Exception as e:
        print(f"❌ Error applying Pattern {pattern} fixes: {e}")
        return False


def validate_fixes(repo_root: Path) -> bool:
    """Run check-only mode to validate all fixes."""
    print("\n🔍 Validating fixes...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/ci/auto_fix_common_issues.py",
                "--check-only"
            ],
            cwd=repo_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ All auto-fixable issues resolved!")
            return True
        print("⚠️  Some issues remain:")
        print(result.stdout)
        return False

    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def main():
    """Main entry point for Copilot Agent auto-fix."""
    print("🤖 Copilot Agent Auto-Fix Helper\n")

    repo_root = Path(__file__).parent.parent.parent
    report_path = repo_root / ".codex" / "diagnostic-report.json"

    if not report_path.exists():
        print("❌ No diagnostic report found.")
        print("   Run: python scripts/ci/auto_fix_common_issues.py --check-only --json-output .codex/diagnostic-report.json")
        sys.exit(1)

    # Parse report
    report = parse_diagnostic_report(str(report_path))

    print(f"📊 Status: {report['status']}")
    print(f"📊 Total Issues: {report['total_issues']}")
    print(f"📊 Auto-Fixable: {report['auto_fixable']}")
    print(f"📊 Manual Review: {report['manual_review']}")

    if report['auto_fixable'] == 0:
        print("\n✅ No auto-fixable issues to resolve!")
        sys.exit(0)

    # Get unique auto-fixable patterns
    patterns = sorted(set(
        issue['pattern']
        for issue in report['issues']
        if issue['auto_fix_available']
    ))

    print(f"\n🎯 Patterns to fix: {', '.join(map(str, patterns))}")

    # Apply fixes for each pattern
    success_count = 0
    for pattern in patterns:
        if apply_fixes_by_pattern(pattern, repo_root):
            success_count += 1

    print(f"\n📈 Applied fixes for {success_count}/{len(patterns)} patterns")

    # Validate all fixes
    if validate_fixes(repo_root):
        print("\n🎉 All auto-fixable issues resolved successfully!")
        print("\n📋 Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Run tests: nox -s tests")
        print("   3. Commit: git commit -am 'fix(ci): resolve auto-fixable issues [Copilot]'")
        print("   4. Push: git push")
        sys.exit(0)
    else:
        print("\n⚠️  Some issues may require manual intervention")
        sys.exit(1)


if __name__ == "__main__":
    main()
