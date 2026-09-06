#!/usr/bin/env python3
"""
Pre-Flight CI Validator

Validates changes before CI runs to catch common failure patterns early.
Run this locally before pushing to avoid CI failures.

Usage:
    python scripts/ci/pre_flight_check.py
    python scripts/ci/pre_flight_check.py --fix  # Auto-fix issues where possible
"""

import argparse
import re
import sys
from pathlib import Path


class CheckResult:
    """Result of a validation check."""

    def __init__(self, name: str, passed: bool, message: str, fixable: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable


class PreFlightValidator:
    """Pre-flight validation checks."""

    def __init__(self, repo_root: Path, auto_fix: bool = False):
        self.repo_root = repo_root
        self.auto_fix = auto_fix
        self.results: list[CheckResult] = []

    def add_result(self, result: CheckResult):
        """Add a check result."""
        self.results.append(result)
        symbol = "✅" if result.passed else ("🔧" if result.fixable else "❌")
        print(f"{symbol} {result.name}: {result.message}")

    def check_pytest_plugins_in_workflow(self) -> CheckResult:
        """Check that workflows install compatible plugin ranges and DON'T use explicit -p flags.

        Per PR #3248 root cause analysis:
        - Explicit `-p` flags cause "Plugin already registered" errors
        - Plugins should auto-discover via setuptools entry points
        - Workflows must align with the repo's canonical plugin ranges before package install
        """
        workflow_files = list(self.repo_root.glob(".github/workflows/*.yml"))
        issues = []

        for workflow_file in workflow_files:
            content = workflow_file.read_text()

            # Check if pytest is used
            if "pytest" not in content:
                continue

            # Check for INCORRECT explicit plugin loading (anti-pattern)
            if "-p xdist.plugin" in content or "-p timeout" in content or "-p pytest_timeout" in content:
                issues.append(f"{workflow_file.name}: ❌ Uses explicit -p flags (causes 'Plugin already registered' errors)")

            # Check for plugin version pinning (required for stability)
            # Use a precise regex so bash conditionals like `[ -n "${VAR}" ]` and
            # shell commands like `tail -n 5` are NOT matched.
            # Only match pytest's own `-n` flag: `pytest ... -n <num|auto>` or `--numprocesses`.
            # Note: only `\` line continuations are handled for multi-line cases; other
            # shell continuation formats (pipes, YAML folded blocks) are not matched.
            uses_xdist = bool(
                re.search(
                    r"pytest\b[^\n]*\s-n\s+(?:auto|\d+)"
                    r"|pytest\b[^\n]*\\\n[^\n]*\s-n\s+(?:auto|\d+)"
                    r"|--numprocesses",
                    content,
                )
            )
            uses_timeout = "--timeout=" in content

            if uses_xdist or uses_timeout:
                # Also search composite actions used by this workflow — pins may live
                # in a reusable action rather than in the workflow file itself.
                composite_content = content
                for action_ref in re.findall(r"uses:\s*\./.github/actions/([\w\-]+)", content):
                    action_files = list(self.repo_root.glob(f".github/actions/{action_ref}/action.yml"))
                    action_files += list(self.repo_root.glob(f".github/actions/{action_ref}/action.yaml"))
                    for af in action_files:
                        composite_content += "\n" + af.read_text()

                has_pinning = bool(
                    re.search(r'pytest-xdist(?:==|>=)[^\s"\']+', composite_content)
                )
                has_timeout_pinning = bool(
                    re.search(r'pytest-timeout(?:==|>=)[^\s"\']+', composite_content)
                )

                if uses_xdist and not has_pinning:
                    issues.append(f"{workflow_file.name}: ⚠️ Uses -n flag but doesn't declare a pytest-xdist version/range")
                if uses_timeout and not has_timeout_pinning:
                    issues.append(f"{workflow_file.name}: ⚠️ Uses --timeout flag but doesn't declare a pytest-timeout version/range")

        if issues:
            return CheckResult(
                "Pytest Plugin Configuration",
                False,
                f"Found {len(issues)} workflow(s) with plugin configuration issues:\n  " + "\n  ".join(issues) +
                "\n\nCorrect approach:\n" +
                "  1. Install the repo's compatible plugin ranges from pyproject.toml, e.g. \"pytest>=9.0.3,<10.0.0\" \"pytest-xdist>=3.5.0,<4.0.0\" \"pytest-timeout>=2.2.0,<3.0.0\"\n" +
                "  2. NO -p flags needed (plugins auto-discover)\n" +
                "  3. Install package AFTER the plugin bootstrap\n" +
                "  See: pyproject.toml and the cached setup action",
                fixable=True
            )

        return CheckResult(
            "Pytest Plugin Configuration",
            True,
            "All workflows follow correct plugin configuration (pinned versions, no -p flags)"
        )

    def check_dummy_optimizer_in_tests(self) -> CheckResult:
        """Check that DummyOptimizer mocks have param_groups."""
        test_files = list(self.repo_root.glob("tests/**/*.py"))
        issues = []

        for test_file in test_files:
            content = test_file.read_text()

            # Look for DummyOptimizer class definitions
            if "class DummyOptimizer" in content:
                # Check if it has param_groups
                # Simple heuristic: look for param_groups in the same file
                if "param_groups" not in content:
                    issues.append(f"{test_file.relative_to(self.repo_root)}")

        if issues:
            return CheckResult(
                "DummyOptimizer Mock Interface",
                False,
                f"Found {len(issues)} test file(s) with DummyOptimizer missing param_groups:\n  " + "\n  ".join(issues),
                fixable=True
            )

        return CheckResult(
            "DummyOptimizer Mock Interface",
            True,
            "All DummyOptimizer mocks have param_groups"
        )

    def check_pytest_ini_conflicts(self) -> CheckResult:
        """Check for conflicting pytest configuration."""
        pytest_ini = self.repo_root / "pytest.ini"
        pyproject_toml = self.repo_root / "pyproject.toml"

        issues = []

        # Check for required_plugins directive (known to cause crashes)
        if pytest_ini.exists():
            content = pytest_ini.read_text()
            if re.search(r"^\s*required_plugins\s*=", content, re.MULTILINE):
                issues.append("pytest.ini has 'required_plugins' directive (causes xdist crashes)")

        # Check for duplicate pytest config
        if pytest_ini.exists() and pyproject_toml.exists():
            pyproject_content = pyproject_toml.read_text()
            if "[tool.pytest.ini_options]" in pyproject_content:
                issues.append("Both pytest.ini and pyproject.toml have pytest config (can cause conflicts)")

        if issues:
            return CheckResult(
                "Pytest Configuration",
                False,
                "Configuration conflicts detected:\n  " + "\n  ".join(issues),
                fixable=True
            )

        return CheckResult(
            "Pytest Configuration",
            True,
            "No pytest configuration conflicts detected"
        )

    def check_module_level_importorskip(self) -> CheckResult:
        """Check for module-level pytest.importorskip (causes worker crashes)."""
        conftest_file = self.repo_root / "tests" / "conftest.py"

        if not conftest_file.exists():
            return CheckResult(
                "Module-level importorskip",
                True,
                "No conftest.py to check"
            )

        content = conftest_file.read_text()
        lines = content.split("\n")

        issues = []
        for i, line in enumerate(lines, 1):
            # Check for module-level (not inside function/class) importorskip
            if "pytest.importorskip" in line and not line.strip().startswith("#"):
                # Simple heuristic: if not indented, it's module level
                if not line.startswith(" ") and not line.startswith("\t"):
                    issues.append(f"Line {i}: {line.strip()}")

        if issues:
            return CheckResult(
                "Module-level importorskip",
                False,
                "Found module-level pytest.importorskip (causes xdist crashes):\n  " + "\n  ".join(issues),
                fixable=True
            )

        return CheckResult(
            "Module-level importorskip",
            True,
            "No module-level pytest.importorskip found"
        )

    def check_test_assertion_patterns(self) -> CheckResult:
        """Check for common test assertion anti-patterns."""
        test_files = list(self.repo_root.glob("tests/**/*.py"))
        issues = []

        for test_file in test_files:
            content = test_file.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # Check for pytest.raises with overly broad match patterns
                if "pytest.raises" in line and 'match=' in line:
                    # Look for very short match patterns (likely too broad)
                    match = re.search(r'match\s*=\s*["\'](\w{1,5})["\']', line)
                    if match:
                        pattern = match.group(1)
                        if len(pattern) <= 5:
                            issues.append(
                                f"{test_file.relative_to(self.repo_root)}:{i} - "
                                f"Very broad match pattern: '{pattern}'"
                            )

        if issues:
            return CheckResult(
                "Test Assertion Patterns",
                False,
                f"Found {len(issues)} potential overly-broad match pattern(s):\n  " + "\n  ".join(issues[:5]),
                fixable=False
            )

        return CheckResult(
            "Test Assertion Patterns",
            True,
            "Test assertion patterns look reasonable"
        )

    def check_workflow_timeout_configuration(self) -> CheckResult:
        """Check that workflows have reasonable timeout configurations."""
        workflow_files = list(self.repo_root.glob(".github/workflows/*.yml"))
        issues = []

        for workflow_file in workflow_files:
            content = workflow_file.read_text()

            # Check for jobs without timeout
            if "jobs:" in content:
                # Look for pytest runs without timeout-minutes
                if "pytest" in content and "timeout-minutes:" not in content:
                    issues.append(f"{workflow_file.name}: No timeout-minutes set for pytest job")

        if issues:
            return CheckResult(
                "Workflow Timeouts",
                False,
                "Workflows missing timeout configuration:\n  " + "\n  ".join(issues),
                fixable=True
            )

        return CheckResult(
            "Workflow Timeouts",
            True,
            "All workflows have timeout configurations"
        )

    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print("=" * 60)
        print("🚀 Pre-Flight CI Validation")
        print("=" * 60)
        print()

        # Run all checks
        self.add_result(self.check_pytest_plugins_in_workflow())
        self.add_result(self.check_dummy_optimizer_in_tests())
        self.add_result(self.check_pytest_ini_conflicts())
        self.add_result(self.check_module_level_importorskip())
        self.add_result(self.check_test_assertion_patterns())
        self.add_result(self.check_workflow_timeout_configuration())

        # Summary
        print()
        print("=" * 60)
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        fixable = sum(1 for r in self.results if not r.passed and r.fixable)

        print(f"Results: {passed} passed, {failed} failed")
        if fixable > 0:
            print(f"         {fixable} issue(s) can be auto-fixed with --fix")
        print("=" * 60)

        return failed == 0

    def apply_fixes(self):
        """Apply automatic fixes for fixable issues."""
        print("\n🔧 Applying automatic fixes...\n")

        for result in self.results:
            if not result.passed and result.fixable:
                print(f"Fixing: {result.name}")

                # Apply specific fixes based on check name
                if result.name == "Pytest Plugin Loading":
                    self._fix_pytest_plugin_loading()
                elif result.name == "DummyOptimizer Mock Interface":
                    self._fix_dummy_optimizer()
                elif result.name == "Pytest Configuration":
                    self._fix_pytest_config()
                elif result.name == "Module-level importorskip":
                    self._fix_module_level_importorskip()

                elif result.name == "Workflow Timeouts":
                    self._fix_workflow_timeouts()

        print("\n✅ Fixes applied. Re-run validation to verify.")

    def _fix_workflow_timeouts(self):
        """Add timeout-minutes to jobs in workflows that use pytest but lack it."""
        import re as _re
        workflow_files = list(self.repo_root.glob(".github/workflows/*.yml"))
        for workflow_file in workflow_files:
            content = workflow_file.read_text()
            if "pytest" in content and "timeout-minutes:" not in content:
                # Insert timeout-minutes after the first runs-on line in a job
                fixed = _re.sub(
                    r'(    runs-on: [^\n]+\n)(?!    timeout-minutes:)',
                    r'\1    timeout-minutes: 30\n',
                    content,
                    count=1,
                )
                if fixed != content:
                    workflow_file.write_text(fixed)
                    print(f"  Added timeout-minutes: 30 to {workflow_file.name}")

    def _fix_pytest_plugin_loading(self):
        """Fix pytest plugin loading in workflows."""
        workflow_files = list(self.repo_root.glob(".github/workflows/*.yml"))

        for workflow_file in workflow_files:
            content = workflow_file.read_text()

            # Add -p flags before --timeout and -n flags
            # This is a simplified fix - manual review recommended
            content = re.sub(
                r'pytest([^-\n]*)(--timeout=\d+)',
                r'pytest\1-p timeout \2',
                content
            )
            content = re.sub(
                r'pytest([^-\n]*)(-n \d+)',
                r'pytest\1-p xdist.plugin \2',
                content
            )

            workflow_file.write_text(content)
            print(f"  Updated: {workflow_file.name}")

    def _fix_dummy_optimizer(self):
        """Fix DummyOptimizer classes in tests."""
        test_files = list(self.repo_root.glob("tests/**/*.py"))

        for test_file in test_files:
            content = test_file.read_text()

            if "class DummyOptimizer" in content and "param_groups" not in content:
                # Add __init__ with param_groups to DummyOptimizer
                content = re.sub(
                    r'(class DummyOptimizer:)\s*\n\s*(pass|def)',
                    r'\1\n        def __init__(self):\n            self.param_groups = [{\'lr\': 0.01}]\n\n        \2',
                    content
                )

                test_file.write_text(content)
                print(f"  Updated: {test_file.relative_to(self.repo_root)}")

    def _fix_pytest_config(self):
        """Fix pytest configuration conflicts."""
        pytest_ini = self.repo_root / "pytest.ini"

        if pytest_ini.exists():
            content = pytest_ini.read_text()

            # Comment out required_plugins
            content = re.sub(
                r'^(\s*)(required_plugins\s*=.*)$',
                r'\1# \2  # REMOVED: Causes xdist worker crashes',
                content,
                flags=re.MULTILINE
            )

            pytest_ini.write_text(content)
            print("  Updated: pytest.ini")

    def _fix_module_level_importorskip(self):
        """Fix module-level importorskip in conftest."""
        conftest_file = self.repo_root / "tests" / "conftest.py"

        if conftest_file.exists():
            conftest_file.read_text()

            # This is complex - just warn for now
            print(f"  ⚠️  Manual fix required for: {conftest_file}")
            print("     Replace module-level pytest.importorskip() with try/except imports")


def get_repo_root() -> Path:
    """Find repository root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Pre-flight CI validation")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    args = parser.parse_args()

    try:
        repo_root = get_repo_root()
        validator = PreFlightValidator(repo_root, auto_fix=args.fix)

        all_passed = validator.run_all_checks()

        if args.fix and not all_passed:
            validator.apply_fixes()
            sys.exit(2)  # Exit code 2 means fixes were applied, re-run needed

        sys.exit(0 if all_passed else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
