#!/usr/bin/env python3
"""
Dependency Consistency Validator

Validates that all dependency files (pyproject.toml, requirements*.txt) have consistent
version constraints for critical packages. Prevents accidental downgrades or misalignments.

Usage:
    python scripts/ci/validate_dependency_consistency.py              # Validate only
    python scripts/ci/validate_dependency_consistency.py --fix       # Fix inconsistencies
    python scripts/ci/validate_dependency_consistency.py --report    # Generate report
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional

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
        """Parse a requirement line into (package_name, version_spec)."""
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        # Handle torch special case with index URL
        if "--index-url" in line or "--extra-index-url" in line:
            return None

        # Match package==version or package>=version,<version patterns
        match = re.match(
            r'([a-zA-Z0-9\-_.]+)\s*([=<>!~\[\]0-9.,+\s\+a-zA-Z]*)',
            line.split('#')[0]  # Remove inline comments
        )
        if match:
            pkg = match.group(1).lower().replace('_', '-')
            version = match.group(2).strip()
            if version:
                return (pkg, version)
        return None

    def read_pyproject_deps(self, filepath: Path) -> Dict[str, str]:
        """Extract dependencies from pyproject.toml."""
        deps = {}
        with open(filepath) as f:
            content = f.read()

        in_deps_section = False
        for line in content.split('\n'):
            if 'dependencies = [' in line:
                in_deps_section = True
                continue
            if in_deps_section:
                if line.strip().startswith(']'):
                    break
                parsed = self.parse_requirement(line)
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
        """Check all files for consistency."""
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
                    if actual == expected_version:
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

    def _is_downgrade(self, current: str, expected: str) -> bool:
        """Check if current version is a downgrade from expected."""
        try:
            # Simple heuristic: check if current has lower starting version
            current_nums = re.findall(r'\d+', current.split(',')[0])
            expected_nums = re.findall(r'\d+', expected.split(',')[0])
            if current_nums and expected_nums:
                return int(current_nums[0]) < int(expected_nums[0])
        except (ValueError, IndexError):
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
        help='Exit with error code if any issues found'
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

    if args.strict and not success:
        sys.exit(1)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
