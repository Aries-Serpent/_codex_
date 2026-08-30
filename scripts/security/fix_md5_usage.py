#!/usr/bin/env python3
"""
Fix Md5 Usage

Purpose:
    Main execution script

Usage:
    python scripts/security/fix_md5_usage.py [options]

    Examples:
    $ python scripts/security/fix_md5_usage.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


import logging
import re

logger = logging.getLogger(__name__)
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def fix_md5_in_file(file_path: Path) -> bool:
    """Fix MD5 usage in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Skip if no MD5 usage
        if 'hashlib.md5' not in content:
            return False

        # Skip documentation, tests, and files that already have the fix
        if any(x in str(file_path) for x in ['docs/', 'tests/security/', '.md']):
            return False

        if 'usedforsecurity=False' in content:
            return False  # Already fixed

        # Pattern 1: hashlib.md5(data) → hashlib.md5(data, usedforsecurity=False)
        # Only fix calls that don't already have usedforsecurity parameter
        content = re.sub(
            r'hashlib\.md5\(([^)]+)\)(?!.*usedforsecurity)',
            r'hashlib.md5(\1, usedforsecurity=False)',
            content
        )

        # Pattern 2: md5_obj = hashlib.md5() → md5_obj = hashlib.md5(usedforsecurity=False)
        content = re.sub(
            r'hashlib\.md5\(\)(?!.*usedforsecurity)',
            r'hashlib.md5(usedforsecurity=False)',
            content
        )

        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True

        return False
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """Fix all Python files."""
    base_dir = REPO_ROOT
    fixed_count = 0

    # Search in specific directories
    for pattern in ['src/**/*.py', 'scripts/**/*.py', 'agents/**/*.py']:
        for py_file in base_dir.glob(pattern):
            if fix_md5_in_file(py_file):
                print(f"✅ Fixed: {py_file.relative_to(base_dir)}")
                fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files with MD5 issues")
    return 0

if __name__ == '__main__':
    sys.exit(main())
