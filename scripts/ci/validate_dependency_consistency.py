#!/usr/bin/env python3
"""
Dependency Consistency Validator

Validates that all dependency files (pyproject.toml, requirements*.txt) have consistent
version constraints for critical packages. Prevents accidental downgrades or misalignments.

Usage:
    python scripts/ci/validate_dependency_consistency.py              # Validate only
    python scripts/ci/validate_dependency_consistency.py --report    # Generate JSON report
    python scripts/ci/validate_dependency_consistency.py --strict    # Fail on any issues
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Critical packages that must be consistent across all files
CRITICAL_PACKAGES = {
    "pandas": ">=3.0.3,<4",
    "numpy": ">=2.4.6,<3",
    "transformers": ">=5.12.1,<6",
    "peft": ">=0.19.1,<1",
    "accelerate": ">=1.14.0,<2",
    "datasets": ">=5.0.0,<6",
    "mlflow": ">=2.22.4,<4",
    "torch": ">=2.6.1,<3.0.0",
}

# Files to validate
FILES_TO_CHECK = [
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "requirements-optional.txt",
    "requirements-ml-lite.txt",
    "requirements-ml-cpu.txt",
    "requirements-eval.txt",
]


class DependencyValidator:
    """Validates dependency consistency across all requirement files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results = {}
        self.issues = []

    def parse_requirement(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse a requirement line into (package_name, version_spec).

        Handles pip options like --index-url and --extra-index-url by extracting
        the requirement spec before the options, allowing lines like:
            torch==2.11.0+cpu --index-url https://...
        to be properly parsed as (torch, ==2.11.0+cpu).
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        # Split on common pip options to isolate the requirement part
        # This allows lines like "torch==2.11.0+cpu --index-url ..." to be parsed
        requirement_part = line
        for option in ['--index-url', '--extra-index-url', '--find-links', '--no-index']:
            if option in line:
                requirement_part = line[:line.index(option)].strip()
                break

        # Match package==version or package>=version,<version patterns
        match = re.match(
            r'([a-zA-Z0-9\-_.]+)\s*([=<>!~\[\]0-9.,+\s\+a-zA-Z]*)',
            requirement_part.split('#')[0]  # Remove inline comments
        )
        if match:
            pkg = match.group(1).lower().replace('_', '-')
            version = match.group(2).strip()
            if version:
                return (pkg, version)
        return None

    def read_pyproject_deps(self, filepath: Path) -> Dict[str, str]:
        """Extract dependencies from pyproject.toml.

        Handles:
        - TOML quoted strings (e.g., "pandas>=...")
        - Both [project.dependencies] and [project.optional-dependencies]
        """
        deps = {}
        with open(filepath) as f:
            content = f.read()

        # Parse [project.dependencies]
        in_deps_section = False
        for line in content.split('\n'):
            if line.strip() == 'dependencies = [':
                in_deps_section = True
                continue
            if in_deps_section:
                if line.strip().startswith(']'):
                    break
                # Remove TOML quotes and parse
                clean_line = line.strip().strip('"\'').strip(',')
                if clean_line:
                    parsed = self.parse_requirement(clean_line)
                    if parsed:
                        deps[parsed[0]] = parsed[1]

        # Parse [project.optional-dependencies] sections
        in_optional_section = False
        for line in content.split('\n'):
            if '[project.optional-dependencies' in line:
                in_optional_section = True
                continue
            if in_optional_section:
                if line.strip().startswith('['):
                    in_optional_section = False
                    continue
                if '=' in line and '[' in line:  # Start of dependencies list
                    in_optional_section = True
                    continue
                if in_optional_section and line.strip().startswith(']'):
                    in_optional_section = False
                    continue
                # Remove TOML quotes and parse
                clean_line = line.strip().strip('"\'').strip(',')
                if clean_line and not clean_line.startswith('['):
                    parsed = self.parse_requirement(clean_line)
                    if parsed:
                        deps[parsed[0]] = parsed[1]

        return deps

    def read_requirements_file(self, filepath: Path) -> Dict[str, str]:
        """Extract dependencies from requirements.txt."""
        deps = {}
        with open(filepath) as f:
            for line in f:
                parsed = self.parse_requirement(line)
                if parsed:
                    deps[parsed[0]] = parsed[1]
        return deps

    def validate_file(self, filepath: Path) -> Dict[str, str]:
        """Read and parse dependencies from a file."""
        if not filepath.exists():
            return {}

        if filepath.name == 'pyproject.toml':
            return self.read_pyproject_deps(filepath)
        else:
            return self.read_requirements_file(filepath)

    def check_consistency(self) -> bool:
        """Check all files for consistency.

        Uses semantic version checking: an exact pin like ==2.11.0+cpu
        is considered valid if it falls within the expected range like >=2.6.1,<3.0.0
        """
        print("=" * 70)
        print("DEPENDENCY CONSISTENCY VALIDATION")
        print("=" * 70)

        # Read all files
        all_deps = {}
        for filename in FILES_TO_CHECK:
            filepath = self.repo_root / filename
            if filepath.exists():
                all_deps[filename] = self.validate_file(filepath)
                print(f"\n✓ Loaded {filename}")
            else:
                print(f"\n⊘ Skipped {filename} (not found)")

        # Check critical packages
        print("\n" + "=" * 70)
        print("CRITICAL PACKAGE VALIDATION")
        print("=" * 70)

        issues_found = False
        for pkg, expected_version in CRITICAL_PACKAGES.items():
            print(f"\n{pkg}:")
            print(f"  Expected: {expected_version}")

            for filename, deps in all_deps.items():
                if pkg in deps:
                    actual = deps[pkg]
                    # Use range-based validation instead of string equality
                    if actual == expected_version or self._version_in_range(actual, expected_version):
                        print(f"  ✓ {filename}: {actual}")
                    else:
                        print(f"  ✗ {filename}: {actual}")
                        self.issues.append({
                            'file': filename,
                            'package': pkg,
                            'current': actual,
                            'expected': expected_version,
                            'severity': 'error' if self._is_downgrade(actual, expected_version) else 'warning'
                        })
                        issues_found = True

        # Summary
        print("\n" + "=" * 70)
        print(f"SUMMARY: {len(self.issues)} issues found")
        print("=" * 70)

        if self.issues:
            print("\nIssues by severity:")
            for issue in self.issues:
                print(f"\n[{issue['severity'].upper()}] {issue['file']}")
                print(f"  Package: {issue['package']}")
                print(f"  Current: {issue['current']}")
                print(f"  Expected: {issue['expected']}")

        return not issues_found

    def _version_in_range(self, actual: str, expected_range: str) -> bool:
        """Check if actual version satisfies expected range.

        Examples:
            actual="2.11.0+cpu", expected_range=">=2.6.1,<3.0.0" -> True
            actual="==2.10.0", expected_range=">=2.6.1,<3.0.0" -> True (within range)
            actual="==1.5.0", expected_range=">=2.6.1,<3.0.0" -> False (below range)
        """
        try:
            # Extract version numbers from actual spec
            # Handle cases like "==2.11.0+cpu", ">=2.10", etc.
            actual_nums = re.findall(r'\d+', actual.split('+')[0].split(',')[0])

            # Parse expected range constraints
            lower_bound = None
            upper_bound = None

            for constraint in expected_range.split(','):
                constraint = constraint.strip()
                if constraint.startswith('>='):
                    lower_nums = re.findall(r'\d+', constraint[2:])
                    if lower_nums:
                        lower_bound = [int(n) for n in lower_nums]
                elif constraint.startswith('>'):
                    lower_nums = re.findall(r'\d+', constraint[1:])
                    if lower_nums:
                        lower_bound = [int(n) for n in lower_nums]
                elif constraint.startswith('<'):
                    upper_nums = re.findall(r'\d+', constraint[1:])
                    if upper_nums:
                        upper_bound = [int(n) for n in upper_nums]
                elif constraint.startswith('<='):
                    upper_nums = re.findall(r'\d+', constraint[2:])
                    if upper_nums:
                        upper_bound = [int(n) for n in upper_nums]

            if not actual_nums:
                return False

            actual_version = [int(n) for n in actual_nums[:3]]

            # Pad versions to same length for comparison
            if lower_bound:
                while len(actual_version) < len(lower_bound):
                    actual_version.append(0)
                while len(lower_bound) < len(actual_version):
                    lower_bound.append(0)
                if actual_version < lower_bound:
                    return False

            if upper_bound:
                while len(actual_version) < len(upper_bound):
                    actual_version.append(0)
                while len(upper_bound) < len(actual_version):
                    upper_bound.append(0)
                if actual_version >= upper_bound:
                    return False

            return True
        except (ValueError, IndexError):
            # If parsing fails, treat as not matching
            return False

    def _is_downgrade(self, current: str, expected: str) -> bool:
        """Check if current version is a downgrade from expected.

        Unparsable version constraints are treated as "not a detected downgrade"
        by design, allowing graceful fallback to manual review.
        """
        try:
            # Simple heuristic: check if current has lower starting version
            current_nums = re.findall(r'\d+', current.split(',')[0])
            expected_nums = re.findall(r'\d+', expected.split(',')[0])
            if current_nums and expected_nums:
                return int(current_nums[0]) < int(expected_nums[0])
        except (ValueError, IndexError):
            # Unparsable version constraints are gracefully treated as not a downgrade.
            # This allows manual review of edge cases (e.g., pre-releases, local versions)
            # without blocking validation.
            pass
        return False

    def generate_report(self, output_file: Path) -> None:
        """Generate JSON report of validation results."""
        report = {
            'status': 'pass' if not self.issues else 'fail',
            'total_issues': len(self.issues),
            'issues': self.issues,
            'critical_packages': CRITICAL_PACKAGES,
        }
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate dependency consistency across all requirement files'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate JSON report'
    )
    parser.add_argument(
        '--report-file',
        type=Path,
        default=Path('.codex/dependency_validation_report.json'),
        help='Output path for JSON report'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error code if any issues found (warnings-only mode by default)'
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = Path.cwd()
    if not (repo_root / 'pyproject.toml').exists():
        print("Error: pyproject.toml not found in current directory")
        sys.exit(1)

    # Validate
    validator = DependencyValidator(repo_root)
    success = validator.check_consistency()

    if args.report:
        validator.generate_report(args.report_file)

    # Exit logic: strict mode fails on any issues, non-strict mode is warnings-only (always succeeds)
    if args.strict and not success:
        sys.exit(1)

    # In non-strict mode, always return 0 (warnings-only)
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())
