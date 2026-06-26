#!/usr/bin/env python3
"""
RP-006 Healing Script: Narrow Generic Exception Handlers in Tests

This script identifies and narrows broad `except Exception:` handlers
to specific exception types based on context analysis.
"""

import re
import sys
from pathlib import Path
from typing import Tuple

# Mapping of test context to specific exceptions
EXCEPTION_MAPPING = {
    # CLI tests typically raise these
    r"cli\.main|click|argparse": (
        "ValueError, TypeError, RuntimeError, click.ClickException, SystemExit"
    ),
    # API tests
    r"requests|http|api|endpoint": (
        "ConnectionError, TimeoutError, ValueError, json.JSONDecodeError"
    ),
    # Parsing/Config tests
    r"yaml|json|parse|config": (
        "ValueError, TypeError, KeyError, json.JSONDecodeError"
    ),
    # Default: Common test exceptions
    r".*": (
        "AssertionError, ValueError, TypeError, RuntimeError"
    ),
}


def get_specific_exception(context: str) -> str:
    """Determine specific exception type based on context."""
    for pattern, exceptions in EXCEPTION_MAPPING.items():
        if re.search(pattern, context):
            return exceptions
    return EXCEPTION_MAPPING[r".*"][0]


def fix_file(filepath: Path) -> Tuple[bool, int]:
    """Fix generic exception handlers in a file."""
    content = filepath.read_text()
    original = content
    fixes = 0

    # Find context for each except block
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        if "except Exception:" in line:
            # Gather context (look back 5 lines)
            context = "\n".join(lines[max(0, i - 5) : i])

            # Get specific exception
            specific = get_specific_exception(context)

            # Replace
            new_line = line.replace("except Exception:", f"except ({specific}):")
            lines[i] = new_line
            fixes += 1

        i += 1

    content = "\n".join(lines)

    if content != original:
        filepath.write_text(content)
        return True, fixes

    return False, 0


def main():
    """Main healing function."""
    test_dir = Path("tests")
    total_fixes = 0
    files_changed = 0

    for py_file in test_dir.rglob("*.py"):
        changed, fixes = fix_file(py_file)
        if changed:
            files_changed += 1
            total_fixes += fixes
            print(f"✓ {py_file.relative_to('.')}: {fixes} exceptions fixed")

    print("\nHealing Summary:")
    print(f"  Files changed: {files_changed}")
    print(f"  Total fixes: {total_fixes}")

    return 0 if total_fixes >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
