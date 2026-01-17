#!/usr/bin/env python3
"""
Validate pytest test environment and plugin availability.

This script checks that all required pytest plugins are installed and
accessible before running the test suite.
"""

import sys
from typing import List, Tuple


def check_plugin(name: str, import_name: str) -> Tuple[bool, str]:
    """
    Check if a pytest plugin is available.
    
    Args:
        name: Human-readable plugin name
        import_name: Python import name for the plugin
    
    Returns:
        Tuple of (success: bool, message: str)
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
    
    Args:
        args: List of pytest arguments to test
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    import subprocess
    
    try:
        result = subprocess.run(
            ["pytest", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, f"✗ pytest --help failed with code {result.returncode}"
        
        help_text = result.stdout
        missing_args = [arg for arg in args if arg not in help_text]
        
        if missing_args:
            return False, f"✗ pytest missing support for: {', '.join(missing_args)}"
        
        return True, f"✓ pytest supports all required arguments: {', '.join(args)}"
    except subprocess.TimeoutExpired:
        return False, "✗ pytest --help timed out"
    except Exception as e:
        return False, f"✗ Error checking pytest args: {e}"


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
    
    # Summary
    print("=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Test environment is ready")
        print("=" * 70)
        return 0
    else:
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
