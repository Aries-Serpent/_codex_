#!/usr/bin/env python3
"""
Validate test structure before execution.

Checks:
1. All test directories have __init__.py
2. All test_*.py files are valid Python syntax
3. conftest.py loads without errors
"""

import ast
import sys
from pathlib import Path


def check_init_files(tests_dir: Path) -> list[str]:
    """Check that all test directories have __init__.py files."""
    missing = []
    for subdir in tests_dir.rglob("*"):
        if subdir.is_dir() and not subdir.name.startswith(("__", ".")):
            # Check if it contains test files
            has_tests = any(f.name.startswith("test_") for f in subdir.glob("*.py"))
            if has_tests:
                init_file = subdir / "__init__.py"
                if not init_file.exists():
                    missing.append(str(subdir.relative_to(tests_dir)))
    return missing


def check_syntax(tests_dir: Path) -> list[tuple[str, str]]:
    """Check that all test files have valid Python syntax."""
    errors = []
    for test_file in tests_dir.rglob("test_*.py"):
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                ast.parse(f.read(), filename=str(test_file))
        except SyntaxError as e:
            errors.append((str(test_file.relative_to(tests_dir)), str(e)))
    return errors


def check_conftest(tests_dir: Path) -> tuple[bool, str]:
    """Check if conftest.py can be loaded."""
    conftest = tests_dir / "conftest.py"
    if not conftest.exists():
        return True, "No conftest.py found (optional)"

    try:
        # Add tests directory to path for import
        sys.path.insert(0, str(tests_dir.parent))
        sys.path.insert(0, str(tests_dir.parent / "src"))

        # Try to compile it
        with open(conftest, "r", encoding="utf-8") as f:
            compile(f.read(), str(conftest), "exec")
        return True, "conftest.py syntax valid"
    except Exception as e:
        return False, f"conftest.py error: {e}"


def main():
    """Run all validation checks."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    tests_dir = repo_root / "tests"

    print("=== Test Structure Validation ===")
    print(f"Tests directory: {tests_dir}")
    print()

    # Check 1: __init__.py files
    print("Check 1: __init__.py files in test directories")
    missing_init = check_init_files(tests_dir)
    if missing_init:
        print(f"⚠️  {len(missing_init)} directories missing __init__.py:")
        for path in missing_init[:10]:  # Show first 10
            print(f"  - {path}")
        if len(missing_init) > 10:
            print(f"  ... and {len(missing_init) - 10} more")
    else:
        print("✓ All test directories have __init__.py")
    print()

    # Check 2: Python syntax
    print("Check 2: Python syntax in test files")
    syntax_errors = check_syntax(tests_dir)
    if syntax_errors:
        print(f"❌ {len(syntax_errors)} files with syntax errors:")
        for path, error in syntax_errors[:5]:  # Show first 5
            print(f"  - {path}: {error}")
        if len(syntax_errors) > 5:
            print(f"  ... and {len(syntax_errors) - 5} more")
        return 1
    print("✓ All test files have valid syntax")
    print()

    # Check 3: conftest.py
    print("Check 3: conftest.py loading")
    conftest_ok, conftest_msg = check_conftest(tests_dir)
    if conftest_ok:
        print(f"✓ {conftest_msg}")
    else:
        print(f"⚠️  {conftest_msg}")
    print()

    # Summary
    print("=== Validation Summary ===")
    if missing_init:
        print(f"⚠️  {len(missing_init)} directories need __init__.py")
    if syntax_errors:
        print(f"❌ {len(syntax_errors)} files have syntax errors")
        return 1
    if not conftest_ok:
        print("⚠️  conftest.py has issues (non-blocking)")

    if not syntax_errors:
        print("✅ Test structure validation passed")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
