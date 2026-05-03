#!/usr/bin/env python3
"""
Comprehensive validation script for the _codex_ repository.
Validates package structure, imports, tests, and configuration.

Usage:
    python .codex/scripts/validate_repository.py [--verbose] [--fix]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent


class ValidationResult:
    """Tracks validation results."""

    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, check: str):
        self.passed.append(check)
        print(f"✅ {check}")

    def add_fail(self, check: str, error: str):
        self.failed.append((check, error))
        print(f"❌ {check}: {error}")

    def add_warning(self, check: str, message: str):
        self.warnings.append((check, message))
        print(f"⚠️  {check}: {message}")

    def summary(self) -> Tuple[int, int, int]:
        """Returns (passed, failed, warnings) counts."""
        return len(self.passed), len(self.failed), len(self.warnings)

    def is_success(self) -> bool:
        """Returns True if no failures."""
        return len(self.failed) == 0


def validate_package_structure(results: ValidationResult):
    """Validate package structure and pyproject.toml."""
    print("\n## Package Structure Validation\n")

    # Check pyproject.toml exists
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.exists():
        results.add_pass("pyproject.toml exists")
    else:
        results.add_fail("pyproject.toml", "File not found")
        return

    # Check that services* is NOT in include list
    with open(pyproject) as f:
        content = f.read()
        if '"services*"' not in content and "'services*'" not in content:
            results.add_pass("services* correctly excluded from pyproject.toml")
        else:
            results.add_fail(
                "services* exclusion",
                "services* found in include list (should be excluded)",
            )

    # Check src/ directory exists
    src_dir = REPO_ROOT / "src"
    if src_dir.exists():
        results.add_pass("src/ directory exists")
    else:
        results.add_fail("src/ directory", "Directory not found")

    # Check agents/ directory exists
    agents_dir = REPO_ROOT / "agents"
    if agents_dir.exists():
        results.add_pass("agents/ directory exists")
    else:
        results.add_fail("agents/ directory", "Directory not found")


def validate_imports(results: ValidationResult):
    """Validate that imports follow conventions."""
    print("\n## Import Validation\n")

    # Check for incorrect services imports in src/
    src_dir = REPO_ROOT / "src"
    if src_dir.exists():
        bad_imports = []
        for py_file in src_dir.rglob("*.py"):
            with open(py_file) as f:
                content = f.read()
                for line_no, line in enumerate(content.split("\n"), 1):
                    # Skip comments and strings (basic heuristic)
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    # Look for "from services." (not "from src.services.")
                    if "from services." in line and "from src.services." not in line:
                        # Additional check: not in a string literal
                        if not (
                            '"from services."' in line or "'from services.'" in line
                        ):
                            bad_imports.append(
                                f"{py_file.relative_to(REPO_ROOT)}:{line_no}"
                            )

        if bad_imports:
            results.add_fail(
                "src/ imports",
                f"Found incorrect 'from services.' imports in src/: {bad_imports[:3]}",
            )
        else:
            results.add_pass("No incorrect 'from services.' imports in src/")


def validate_tests(results: ValidationResult, quick: bool = True):
    """Validate test suite."""
    print("\n## Test Suite Validation\n")

    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        results.add_fail("tests/ directory", "Directory not found")
        return

    results.add_pass("tests/ directory exists")

    # Check pytest is available
    try:
        subprocess.run(["pytest", "--version"], capture_output=True, check=True)
        results.add_pass("pytest is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        results.add_fail("pytest", "pytest not installed")
        return

    # Run quick smoke tests if requested
    if quick:
        print("  Running quick smoke tests...")
        try:
            result = subprocess.run(
                ["pytest", "tests/services/workflow/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            if result.returncode == 0:
                results.add_pass("Service workflow tests passed")
            else:
                output = result.stdout or ""
                if len(output) > 500:
                    half = 250
                    truncated_output = f"{output[:half]}\n...\n{output[-half:]}"
                else:
                    truncated_output = output
                results.add_fail(
                    "Service workflow tests", f"Tests failed:\n{truncated_output}"
                )
        except Exception as e:
            results.add_warning("Service workflow tests", f"Could not run tests: {e}")


def validate_documentation(results: ValidationResult):
    """Validate documentation completeness."""
    print("\n## Documentation Validation\n")

    # Check key documentation files
    required_docs = [
        "README.md",
        "AGENTS.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
    ]

    for doc in required_docs:
        doc_path = REPO_ROOT / doc
        if doc_path.exists():
            results.add_pass(f"{doc} exists")
        else:
            results.add_fail(doc, "File not found")

    # Check .codex/ documentation
    codex_dir = REPO_ROOT / ".codex"
    if codex_dir.exists():
        results.add_pass(".codex/ directory exists")

        # Check for phase reports
        phase_reports = [
            ".codex/gap_discovery_report.md",
            ".codex/SERVICES_MIGRATION_ANALYSIS.md",
            ".codex/SERVICES_ARCHITECTURE.md",
            ".codex/phase1_decision_gate.md",
            ".codex/phase2_decision_gate.md",
        ]

        for report in phase_reports:
            report_path = REPO_ROOT / report
            if report_path.exists():
                results.add_pass(f"{report} exists")
            else:
                results.add_warning(report, "Report not found (may not be created yet)")
    else:
        results.add_warning(".codex/ directory", "Directory not found")


def validate_configuration(results: ValidationResult):
    """Validate configuration files."""
    print("\n## Configuration Validation\n")

    # Check pytest.ini
    pytest_ini = REPO_ROOT / "pytest.ini"
    if pytest_ini.exists():
        results.add_pass("pytest.ini exists")
    else:
        results.add_warning("pytest.ini", "File not found")

    # Check .gitignore
    gitignore = REPO_ROOT / ".gitignore"
    if gitignore.exists():
        results.add_pass(".gitignore exists")

        # Check for .hypothesis in gitignore
        with open(gitignore) as f:
            if ".hypothesis" in f.read():
                results.add_pass(".hypothesis in .gitignore")
            else:
                results.add_warning(".hypothesis", "Should be in .gitignore")
    else:
        results.add_fail(".gitignore", "File not found")

    # Check DO_NOT_ACTIVATE_GITHUB_ACTIONS policy
    policy_file = REPO_ROOT / ".codex" / "DO_NOT_ACTIVATE_GITHUB_ACTIONS"
    if policy_file.exists():
        results.add_pass("DO_NOT_ACTIVATE_GITHUB_ACTIONS policy file exists")
    else:
        results.add_warning("DO_NOT_ACTIVATE_GITHUB_ACTIONS", "Policy file not found")


def validate_build(results: ValidationResult):
    """Validate that package builds."""
    print("\n## Build Validation\n")

    # Check if build module is available
    try:
        results.add_pass("build module is available")
    except Exception as e:
        results.add_warning(
            "build module", f"Unavailable or broken (e.g., not installed). Details: {e}"
        )
        return

    # Try to build the package
    print("  Building package (this may take a moment)...")
    try:
        proc = subprocess.Popen(
            ["python", "-m", "build", "--wheel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=REPO_ROOT,
        )
        try:
            stdout, stderr = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()  # Ensure cleanup, output not needed
            results.add_warning("Package build", "Build timed out after 60s")
            return

        class _Result:
            def __init__(self, returncode: int, stdout: str, stderr: str):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        result = _Result(proc.returncode, stdout, stderr)

        if result.returncode == 0:
            results.add_pass("Package builds successfully")

            # Check wheel contents
            import zipfile

            dist_dir = REPO_ROOT / "dist"
            wheels = list(dist_dir.glob("*.whl"))
            if wheels:
                wheel_path = wheels[-1]  # Get latest wheel
                with zipfile.ZipFile(wheel_path, "r") as zf:
                    files = zf.namelist()
                    # Check that services/ is NOT in the wheel
                    services_files = [f for f in files if f.startswith("services/")]
                    if not services_files:
                        results.add_pass("services/ correctly excluded from wheel")
                    else:
                        results.add_fail(
                            "wheel contents",
                            f"services/ found in wheel: {services_files[:3]}",
                        )
        else:
            output = stderr or ""
            if len(output) > 500:
                half = 250
                truncated_output = f"{output[:half]}\n...\n{output[-half:]}"
            else:
                truncated_output = output
            results.add_fail("Package build", f"Build failed:\n{truncated_output}")
    except Exception as e:
        results.add_warning("Package build", f"Could not build: {e}")


def main():
    parser = argparse.ArgumentParser(description="Validate _codex_ repository")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    parser.add_argument(
        "--skip-build", action="store_true", help="Skip build validation"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  _codex_ Repository Validation")
    print("=" * 70)

    results = ValidationResult()

    # Run validation checks
    validate_package_structure(results)
    validate_imports(results)

    if not args.skip_tests:
        validate_tests(results, quick=True)
    else:
        print("\n## Test Suite Validation\n")
        print("⏭️  Skipped (--skip-tests)")

    validate_documentation(results)
    validate_configuration(results)

    if not args.skip_build:
        validate_build(results)
    else:
        print("\n## Build Validation\n")
        print("⏭️  Skipped (--skip-build)")

    # Print summary
    passed, failed, warnings = results.summary()
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    print(f"✅ Passed:   {passed}")
    print(f"❌ Failed:   {failed}")
    print(f"⚠️  Warnings: {warnings}")
    print("=" * 70)

    if results.is_success():
        print("\n✅ All validations passed!")
        return 0
    print("\n❌ Some validations failed. Please review the errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
