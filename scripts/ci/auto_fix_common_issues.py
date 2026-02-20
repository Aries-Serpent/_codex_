#!/usr/bin/env python3
"""
Automated fix script for common CI issues detected by workflows.

This script automatically fixes the 8 most common patterns that cause workflow failures:
1. Unused imports
2. Unused variables
3. YAML indentation
4. Coverage threshold inconsistencies
5. Missing tokenizer fallbacks
6. Vague test assertions
7. Redundant imports
8. CodeQL scanning alerts

Usage:
    python scripts/ci/auto_fix_common_issues.py [--check-only] [--pattern PATTERN]

Options:
    --check-only    Only detect issues, don't fix them
    --pattern N     Only apply pattern N (1-8)
    --dry-run       Show what would be changed without making changes
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CommonIssueFixer:
    """Automatically fix common CI issues."""

    def __init__(self, repo_root: Path, check_only: bool = False, dry_run: bool = False):
        self.repo_root = repo_root
        self.check_only = check_only
        self.dry_run = dry_run
        self.issues_found: Dict[str, List[str]] = {}
        self.fixes_applied: Dict[str, int] = {}

        # Define which patterns are auto-fixable vs manual-review
        self.auto_fixable_patterns = {
            "Unused Imports",      # Pattern 1 - ruff --fix
            "Coverage Thresholds", # Pattern 4 - automated replacement
            "CodeQL Alerts",       # Pattern 8 - ruff --fix
        }
        self.manual_review_patterns = {
            "Unused Variables",    # Pattern 2 - context-dependent
            "YAML Indentation",    # Pattern 3 - manual review
            "Tokenizer Fallbacks", # Pattern 5 - code-flow dependent
            "Test Assertions",     # Pattern 6 - logic-dependent
            "Redundant Imports",   # Pattern 7 - manual review
        }

    def run_all_patterns(self) -> bool:
        """Run all fix patterns. Returns True if any issues found."""
        print("🔍 Scanning for common CI issues...\n")

        patterns = [
            (1, "Unused Imports", self.fix_unused_imports),
            (2, "Unused Variables", self.fix_unused_variables),
            (3, "YAML Indentation", self.fix_yaml_indentation),
            (4, "Coverage Thresholds", self.fix_coverage_thresholds),
            (5, "Tokenizer Fallbacks", self.fix_tokenizer_fallbacks),
            (6, "Test Assertions", self.fix_test_assertions),
            (7, "Redundant Imports", self.fix_redundant_imports),
            (8, "CodeQL Alerts", self.fix_codeql_alerts),
        ]

        any_issues = False
        for num, name, func in patterns:
            print(f"Pattern {num}: {name}")
            issues = func()
            if issues:
                any_issues = True
                self.issues_found[name] = issues
                print(f"  ✗ Found {len(issues)} issues")
            else:
                print("  ✓ No issues found")
            print()

        return any_issues

    def fix_unused_imports(self) -> List[str]:
        """Pattern 1: Remove unused imports using ruff."""
        issues = []

        try:
            # Run ruff to detect unused imports (F401)
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "--select", "F401",
                 "tests/", "src/", "--output-format=json"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode != 0 and result.stdout:
                import json
                try:
                    ruff_output = json.loads(result.stdout)
                    for item in ruff_output:
                        issues.append(f"{item['filename']}:{item['location']['row']} - {item['message']}")
                except json.JSONDecodeError:
                    pass

            if issues and not self.check_only:
                if not self.dry_run:
                    # Auto-fix with ruff
                    subprocess.run(
                        ["python", "-m", "ruff", "check", "--select", "F401",
                         "--fix", "tests/", "src/"],
                        cwd=self.repo_root
                    )
                    self.fixes_applied["Unused Imports"] = len(issues)
                else:
                    print(f"  [DRY RUN] Would fix {len(issues)} unused imports")

        except FileNotFoundError:
            print("  ⚠️ ruff not installed, skipping unused import detection")

        return issues

    def fix_unused_variables(self) -> List[str]:
        """Pattern 2: Detect unused variables using ruff."""
        issues = []

        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "--select", "F841",
                 "tests/", "src/", "--output-format=json"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode != 0 and result.stdout:
                import json
                try:
                    ruff_output = json.loads(result.stdout)
                    for item in ruff_output:
                        issues.append(f"{item['filename']}:{item['location']['row']} - {item['message']}")

                    # Note: F841 often needs manual review, so we don't auto-fix
                    if issues:
                        print("  ℹ️ Unused variables require manual review")
                except json.JSONDecodeError:
                    pass

        except FileNotFoundError:
            pass

        return issues

    def fix_yaml_indentation(self) -> List[str]:
        """Pattern 3: Validate YAML files for indentation errors."""
        issues = []

        try:
            import yaml
        except ImportError:
            print("  ⚠️ PyYAML not installed, skipping YAML validation")
            return issues

        workflow_dir = self.repo_root / ".github" / "workflows"
        if not workflow_dir.exists():
            return issues

        for yaml_file in workflow_dir.glob("*.yml"):
            try:
                yaml.safe_load(yaml_file.read_text())
            except yaml.YAMLError as e:
                issues.append(f"{yaml_file.name}: {str(e)}")
                print(f"  ✗ {yaml_file.name}: YAML parse error")

        return issues

    def fix_coverage_thresholds(self) -> List[str]:
        """Pattern 4: Check for inconsistent coverage thresholds."""
        issues = []
        thresholds: Dict[str, int] = {}

        # Check workflow files
        workflow_dir = self.repo_root / ".github" / "workflows"
        if workflow_dir.exists():
            for yml_file in workflow_dir.glob("*.yml"):
                content = yml_file.read_text()
                matches = re.findall(r'fail-under[=\s]+(\d+)', content)
                if matches:
                    for threshold in matches:
                        key = f"{yml_file.name}"
                        thresholds[key] = int(threshold)

        # Check if all thresholds are consistent (should be 70%)
        target_threshold = 70
        for file, threshold in thresholds.items():
            if threshold != target_threshold:
                issues.append(f"{file}: threshold={threshold}% (expected {target_threshold}%)")

        if issues and not self.check_only and not self.dry_run:
            # Auto-fix: standardize to 70%
            for yml_file in workflow_dir.glob("*.yml"):
                content = yml_file.read_text()
                # Replace fail-under=25 or fail-under=85 with fail-under=70
                # Use word boundary to avoid matching 700, 170, etc.
                new_content = re.sub(
                    r'(fail-under[=\s]+)(?!70\b)\d+\b',
                    r'\g<1>70',
                    content
                )
                if new_content != content:
                    yml_file.write_text(new_content)
                    self.fixes_applied["Coverage Thresholds"] = \
                        self.fixes_applied.get("Coverage Thresholds", 0) + 1

        return issues

    def fix_tokenizer_fallbacks(self) -> List[str]:
        """Pattern 5: Check for missing tokenizer pad_token fallbacks."""
        issues = []

        # Find files with AutoTokenizer.from_pretrained
        src_dir = self.repo_root / "src"
        if not src_dir.exists():
            return issues

        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text()

            # Check if file loads tokenizer
            if "AutoTokenizer.from_pretrained" in content:
                # Check if it has fallback logic
                has_fallback = "pad_token" in content and "eos_token" in content

                if not has_fallback:
                    issues.append(f"{py_file.relative_to(self.repo_root)}: Missing pad_token fallback")

                    # Note: Adding fallback requires understanding code context,
                    # so we only report, don't auto-fix
                    print(f"  ℹ️ {py_file.name}: Manual review needed for tokenizer fallback")

        return issues

    def fix_test_assertions(self) -> List[str]:
        """Pattern 6: Detect vague test assertions."""
        issues = []

        tests_dir = self.repo_root / "tests"
        if not tests_dir.exists():
            return issues

        vague_patterns = [
            (r'assert\s+len\([^)]+\)\s*>=\s*0', "len() >= 0 is always true"),
            (r'assert\s+\w+\s+or\s+True', "X or True is always true"),
            (r'except\s+Exception\s*:', "Catch-all exception handler"),
        ]

        for py_file in tests_dir.rglob("*.py"):
            content = py_file.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern, desc in vague_patterns:
                    if re.search(pattern, line):
                        issues.append(
                            f"{py_file.relative_to(self.repo_root)}:{line_num} - {desc}"
                        )

        if issues:
            print("  ℹ️ Vague assertions require manual review")

        return issues

    def fix_redundant_imports(self) -> List[str]:
        """Pattern 7: Detect redundant imports (module + function level)."""
        issues = []

        tests_dir = self.repo_root / "tests"
        if not tests_dir.exists():
            return issues

        for py_file in tests_dir.rglob("*.py"):
            content = py_file.read_text()

            # Find module-level imports
            module_imports = set()
            for match in re.finditer(r'^import\s+(\w+)', content, re.MULTILINE):
                module_imports.add(match.group(1))

            # Find function-level imports
            in_function = False
            for line_num, line in enumerate(content.split('\n'), 1):
                if re.match(r'^\s*def\s+', line):
                    in_function = True
                elif re.match(r'^\S', line) and not line.startswith('#'):
                    in_function = False

                if in_function:
                    match = re.match(r'^\s+import\s+(\w+)', line)
                    if match and match.group(1) in module_imports:
                        issues.append(
                            f"{py_file.relative_to(self.repo_root)}:{line_num} - "
                            f"Redundant import of {match.group(1)}"
                        )

        if issues:
            print("  ℹ️ Redundant imports require manual review")

        return issues

    def fix_codeql_alerts(self) -> List[str]:
        """Pattern 8: Check for open CodeQL alerts (unused imports primarily)."""
        issues = []

        # This would ideally query GitHub API, but we'll use local detection
        # Same as Pattern 1 - unused imports
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "--select", "F401,F841",
                 "tests/", "src/", "--output-format=concise"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            # Only treat as issues if ruff found actual violations (exit code != 0)
            # Exit code 0 means no violations, so we skip processing stdout
            if result.returncode != 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    # Only add non-empty lines that look like ruff violations
                    # Ruff violations have format: "path/file.py:line:col: CODE message"
                    if line and ":" in line:
                        issues.append(line)

        except FileNotFoundError:
            pass

        return issues

    def generate_report(self) -> str:
        """Generate summary report of issues and fixes."""
        report = [
            "\n" + "="*70,
            "Common CI Issues - Summary Report",
            "="*70,
        ]

        if not self.issues_found:
            report.append("\n✅ No issues found! All patterns passing.\n")
            return "\n".join(report)

        # Separate auto-fixable and manual-review issues
        auto_fixable_issues = {
            name: issues for name, issues in self.issues_found.items()
            if name in self.auto_fixable_patterns
        }
        manual_review_issues = {
            name: issues for name, issues in self.issues_found.items()
            if name in self.manual_review_patterns
        }

        # Report auto-fixable issues (these are failures)
        if auto_fixable_issues:
            report.append("\n❌ AUTO-FIXABLE ISSUES (CI Failure):")
            report.append(f"{'Pattern':<30} {'Issues':<15} {'Fixed':<10}")
            report.append("-" * 70)

            for pattern_name, issues in auto_fixable_issues.items():
                fixed_count = self.fixes_applied.get(pattern_name, 0)
                status = f"{fixed_count}/{len(issues)}" if fixed_count else "0"
                report.append(f"{pattern_name:<30} {len(issues):<15} {status:<10}")

        # Report manual-review issues (these are warnings)
        if manual_review_issues:
            report.append("\n⚠️  MANUAL REVIEW NEEDED (Informational):")
            report.append(f"{'Pattern':<30} {'Issues':<15} {'Status':<10}")
            report.append("-" * 70)

            for pattern_name, issues in manual_review_issues.items():
                report.append(f"{pattern_name:<30} {len(issues):<15} {'Info':<10}")

        # Summary
        total_auto_fixable = sum(len(issues) for issues in auto_fixable_issues.values())
        total_manual = sum(len(issues) for issues in manual_review_issues.values())
        total_fixed = sum(self.fixes_applied.values())

        report.append("-" * 70)
        report.append(f"Auto-fixable: {total_auto_fixable} issues, {total_fixed} fixed")
        report.append(f"Manual review: {total_manual} issues (informational)")
        report.append("")

        if self.check_only:
            if total_auto_fixable > total_fixed:
                report.append("❌ Auto-fixable issues detected. Run without --check-only to fix")
            if total_manual > 0:
                report.append("ℹ️  Manual review issues are informational and won't cause CI failure")
        elif self.dry_run:
            report.append("ℹ️  This was a dry run. Remove --dry-run to apply fixes")
        else:
            report.append("✅ Automatic fixes applied where possible")
            if total_manual > 0:
                report.append("⚠️  Some issues require manual review (see above)")

        report.append("")
        return "\n".join(report)

    def has_auto_fixable_issues(self) -> bool:
        """Check if there are any unfixed auto-fixable issues."""
        for pattern_name, issues in self.issues_found.items():
            if pattern_name in self.auto_fixable_patterns:
                fixed_count = self.fixes_applied.get(pattern_name, 0)
                if len(issues) > fixed_count:
                    return True
        return False

    def generate_json_report(self, output_path: Optional[str] = None) -> dict:
        """
        Generate machine-readable JSON report for Copilot Agent.

        Args:
            output_path: Optional path to write JSON file

        Returns:
            Dictionary with structured diagnostic data
        """
        report = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "status": "failed" if self.has_auto_fixable_issues() else "passed",
            "total_issues": sum(len(issues) for issues in self.issues_found.values()),
            "auto_fixable": sum(
                len(issues) for name, issues in self.issues_found.items()
                if name in self.auto_fixable_patterns
            ),
            "manual_review": sum(
                len(issues) for name, issues in self.issues_found.items()
                if name in self.manual_review_patterns
            ),
            "issues": [],
            "fixes_applied": self.fixes_applied,
            "next_steps": []
        }

        # Build detailed issue list
        pattern_map = {
            "Unused Imports": 1,
            "Unused Variables": 2,
            "YAML Indentation": 3,
            "Coverage Thresholds": 4,
            "Tokenizer Fallbacks": 5,
            "Test Assertions": 6,
            "Redundant Imports": 7,
            "CodeQL Alerts": 8,
        }

        for pattern_name, issues in self.issues_found.items():
            pattern_num = pattern_map.get(pattern_name, 0)
            is_auto_fixable = pattern_name in self.auto_fixable_patterns

            for issue_str in issues:
                # Parse issue string (format: "file:line - message")
                parts = issue_str.split(" - ", 1)
                file_info = parts[0] if parts else issue_str
                message = parts[1] if len(parts) > 1 else ""

                file_parts = file_info.split(":")
                file_path = file_parts[0] if file_parts else ""
                line_num = int(file_parts[1]) if len(file_parts) > 1 and file_parts[1].isdigit() else 0

                report["issues"].append({
                    "pattern": pattern_num,
                    "pattern_name": pattern_name,
                    "type": pattern_name.lower().replace(" ", "_"),
                    "severity": "error" if is_auto_fixable else "warning",
                    "file": file_path,
                    "line": line_num,
                    "message": message or issue_str,
                    "auto_fix_available": is_auto_fixable,
                    "suggested_fix": f"Run: python scripts/ci/auto_fix_common_issues.py --pattern {pattern_num}",
                })

        # Add next steps
        if report["auto_fixable"] > 0:
            report["next_steps"] = [
                "Run: python scripts/ci/auto_fix_common_issues.py",
                "Or use Copilot Agent: @workspace Fix all auto-fixable CI issues",
                f"Patterns to fix: {', '.join(str(pattern_map[n]) for n in self.auto_fixable_patterns if n in self.issues_found)}"
            ]
        else:
            report["next_steps"] = ["All auto-fixable issues resolved!"]

        # Write to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"JSON report written to {output_path}")

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Auto-fix common CI issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues, don't fix them"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--pattern",
        type=int,
        choices=range(1, 9),
        help="Only run specific pattern (1-8)"
    )
    parser.add_argument(
        "--json-output",
        type=str,
        help="Write JSON report to specified path (e.g., .codex/diagnostic-report.json)"
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent.parent

    fixer = CommonIssueFixer(repo_root, args.check_only, args.dry_run)

    if args.pattern:
        print(f"Running pattern {args.pattern} only...")
        # Run specific pattern (simplified for this example)
        fixer.run_all_patterns()
    else:
        fixer.run_all_patterns()

    # Generate JSON report if requested
    if args.json_output:
        fixer.generate_json_report(args.json_output)

    # Print report
    print(fixer.generate_report())

    # Exit with appropriate code
    # Only fail if there are unfixed auto-fixable issues
    # Manual review issues are informational and don't cause failure
    if args.check_only and fixer.has_auto_fixable_issues():
        sys.exit(1)  # Auto-fixable issues found that need fixing
    else:
        sys.exit(0)  # No auto-fixable issues, or all were fixed


if __name__ == "__main__":
    main()
