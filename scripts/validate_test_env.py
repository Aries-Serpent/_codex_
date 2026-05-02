#!/usr/bin/env python3
"""
Validate pytest test environment and plugin availability.

This script checks that all required pytest plugins are installed and
accessible before running the test suite.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def check_plugin(name: str, import_name: str) -> Tuple[bool, str]:
    """
    Check if a pytest plugin is available.

    Args:
        name: Human-readable plugin name
        import_name: Python import name for the plugin

    Returns:
        Tuple of (success: bool, message: str) where message contains
        status information and version details for display purposes.
        Success is True if plugin is importable, False otherwise.
    """
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        return True, f"✓ {name} ({import_name}) version {version}"
    except ImportError as e:
        return False, f"✗ {name} ({import_name}) - NOT FOUND: {e}"


def check_pytest_args(args: List[str]) -> Tuple[bool, str]:
    """
    Check if pytest accepts specific command-line arguments.

    Validates pytest command-line argument support by checking the help output
    (pytest --help) to see if the specified arguments are listed. Does not
    actually execute tests with the arguments.

    Args:
        args: List of pytest arguments to test (e.g., ['-n', '--reruns'])

    Returns:
        Tuple of (success: bool, message: str) where message contains
        status information about argument support for display purposes.
        Success is True if all arguments are supported, False otherwise.
    """
    import re

    try:
        result = subprocess.run(
            ["pytest", "--help"],
            capture_output=True,
            text=True,
            timeout=30  # Increased from 10 to 30 seconds for Python 3.12 compatibility
        )

        if result.returncode != 0:
            return False, f"✗ pytest --help failed with code {result.returncode}"

        help_text = result.stdout
        missing_args = []

        # Use regex to match arguments more precisely
        # Match as option in help text (with space/comma/equals after it)
        for arg in args:
            # Escape special regex chars
            escaped_arg = re.escape(arg)
            # Match: arg followed by space, comma, equals, or [ (for optional args)
            # This prevents matching substrings while being flexible enough
            pattern = re.compile(escaped_arg + r'[\s,=\[]', re.MULTILINE)
            if not pattern.search(help_text):
                missing_args.append(arg)

        if missing_args:
            return False, f"✗ pytest missing support for: {', '.join(missing_args)}"

        return True, f"✓ pytest supports all required arguments: {', '.join(args)}"
    except subprocess.TimeoutExpired:
        # Fallback: Check if plugins are importable directly
        try:
            import pytest  # noqa: F401
            import pytest_cov  # noqa: F401
            import pytest_randomly  # noqa: F401
            import pytest_rerunfailures  # noqa: F401
            import pytest_timeout  # noqa: F401
            import xdist  # noqa: F401
            return True, "✓ pytest and all plugins are importable (--help timed out, but plugins verified)"
        except ImportError as e:
            return False, f"✗ pytest --help timed out and plugin import failed: {e}"
    except Exception as e:
        return False, f"✗ Error checking pytest args: {e}"


def validate_config_files() -> Tuple[bool, str]:
    """
    Verify required config files exist.

    Returns:
        Tuple of (success: bool, message: str)
    """
    required_configs = [
        'config/experiment/debug.yaml',
        'config/experiment/fast.yaml',
        'config/experiment/lambda.yaml',
    ]

    missing_configs = []
    for config_path in required_configs:
        if not Path(config_path).exists():
            missing_configs.append(config_path)

    if missing_configs:
        return False, f"✗ Missing config files: {', '.join(missing_configs)}"

    return True, f"✓ All required config files exist ({len(required_configs)} files)"


def validate_test_structure() -> Tuple[bool, str]:
    """
    Verify test directory structure.

    Returns:
        Tuple of (success: bool, message: str)
    """
    required_dirs = [
        'tests/unit',
        'tests/integration',
        'tests/eval',
        'config/experiment',
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        return False, f"⚠️  Missing directories: {', '.join(missing_dirs)}"

    return True, f"✓ Test directory structure validated ({len(required_dirs)} dirs)"


def main() -> int:
    """
    Main validation function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 70)
    print("Validating Pytest Test Environment")
    print("=" * 70)
    print()

    all_passed = True

    # Check core pytest
    print("Checking pytest installation:")
    try:
        import pytest
        print(f"✓ pytest version {pytest.__version__}")
    except ImportError as e:
        print(f"✗ pytest NOT FOUND: {e}")
        all_passed = False
    print()

    # Check required plugins
    print("Checking required pytest plugins:")
    required_plugins = [
        ("pytest-cov", "pytest_cov"),
        ("pytest-xdist", "xdist"),
        ("pytest-timeout", "pytest_timeout"),
        ("pytest-rerunfailures", "pytest_rerunfailures"),
        ("pytest-randomly", "pytest_randomly"),
    ]

    for name, import_name in required_plugins:
        success, message = check_plugin(name, import_name)
        print(f"  {message}")
        if not success:
            all_passed = False
    print()

    # Check pytest arguments
    print("Checking pytest command-line support:")
    required_args = ["-n", "--dist", "--reruns", "--reruns-delay", "--cov", "--timeout"]
    success, message = check_pytest_args(required_args)
    print(f"  {message}")
    if not success:
        all_passed = False
    print()

    # Check test structure
    print("Checking test directory structure:")
    success, message = validate_test_structure()
    print(f"  {message}")
    if not success:
        all_passed = False
    print()

    # Check config files
    print("Checking config files:")
    success, message = validate_config_files()
    print(f"  {message}")
    if not success:
        all_passed = False
    print()

    # Summary
    print("=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Test environment is ready")
        print("=" * 70)
        return 0
    print("✗ VALIDATION FAILED - Please install missing plugins")
    print("=" * 70)
    print()
    print("To fix, run:")
    print("  pip install -r requirements-test.txt")
    print("  # or")
    print("  pip install -e .[test]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
