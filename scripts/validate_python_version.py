#!/usr/bin/env python3
"""
Python Version Validation Script

Validates that Python version is consistent across all configuration files
and meets the repository's Python 3.12 requirement.

Usage:
    python scripts/validate_python_version.py

Exit codes:
    0: All validations passed
    1: Validation failed
"""

from __future__ import annotations

import sys
from pathlib import Path

# Python 3.12+ required
if sys.version_info < (3, 12):
    print(f"❌ Python 3.12+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

try:
    import tomllib
except ImportError:
    print("❌ tomllib not available (Python 3.12+ has it built-in)")
    sys.exit(1)

# Expected versions
EXPECTED_VERSION = "3.12.10"
EXPECTED_MINOR = "3.12"
EXPECTED_RANGE = ">=3.12,<3.13"


def check_python_version_file() -> bool:
    """Check .python-version file exists and has correct version."""
    version_file = Path(".python-version")

    if not version_file.exists():
        print("❌ .python-version file not found")
        print("   Create it with: echo '3.12.10' > .python-version")
        return False

    version = version_file.read_text().strip()

    if version != EXPECTED_VERSION:
        print(f"❌ .python-version: expected '{EXPECTED_VERSION}', found '{version}'")
        return False

    print(f"✅ .python-version: {version}")
    return True


def check_pyproject_toml() -> bool:
    """Check pyproject.toml requires-python constraint."""
    pyproject = Path("pyproject.toml")

    if not pyproject.exists():
        print("⚠️  pyproject.toml not found (optional)")
        return True

    try:
        data = tomllib.loads(pyproject.read_text())
    except Exception as e:
        print(f"❌ Failed to parse pyproject.toml: {e}")
        return False

    requires_python = data.get("project", {}).get("requires-python", "")

    if not requires_python:
        print("❌ pyproject.toml: 'requires-python' not found in [project]")
        return False

    # Accept: ">=3.12,<3.13" (with or without spaces)
    normalized = requires_python.replace(" ", "")

    if normalized != EXPECTED_RANGE:
        print(f"❌ pyproject.toml: expected '{EXPECTED_RANGE}', found '{requires_python}'")
        return False

    print(f"✅ pyproject.toml: requires-python = \"{requires_python}\"")
    return True


def check_runtime_txt() -> bool:
    """Check runtime.txt if it exists (for Heroku/PaaS deployments)."""
    runtime_file = Path("runtime.txt")

    if not runtime_file.exists():
        print("ℹ️  runtime.txt not found (optional)")
        return True

    runtime = runtime_file.read_text().strip()
    expected_runtime = f"python-{EXPECTED_VERSION}"

    if runtime != expected_runtime:
        print(f"❌ runtime.txt: expected '{expected_runtime}', found '{runtime}'")
        return False

    print(f"✅ runtime.txt: {runtime}")
    return True


def check_current_python() -> bool:
    """Check currently running Python version."""
    current = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    if sys.version_info[:2] != (3, 12):
        print(f"❌ Current Python: {current} (expected 3.12.x)")
        return False

    print(f"✅ Current Python: {current}")
    return True


def main() -> int:
    """Run all validations."""
    print("🔍 Validating Python version configuration...\n")

    checks = [
        ("Python version file", check_python_version_file),
        ("pyproject.toml", check_pyproject_toml),
        ("runtime.txt", check_runtime_txt),
        ("Current Python", check_current_python),
    ]

    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"❌ {name}: Unexpected error: {e}")
            results.append(False)
        print()  # Blank line between checks

    # Summary
    passed = sum(results)
    total = len(results)

    print("=" * 60)
    if all(results):
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🎉 Python 3.12 version configuration is valid!")
        return 0
    failed = total - passed
    print(f"❌ {failed} check(s) failed ({passed}/{total} passed)")
    print("\n💡 Fix the issues above and run again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
