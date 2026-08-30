#!/usr/bin/env python3
"""
Fix Shell True

Purpose:
    Main execution script

Usage:
    python scripts/security/fix_shell_true.py [options]

    Examples:
    $ python scripts/security/fix_shell_true.py --help

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


def fix_shell_true_in_file(file_path: Path) -> bool:
    """Fix shell=False in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Check if file has subprocess.call with shell=False
        if 'shell=False' not in content:
            return False

        # Skip files that are documentation, tests, or already have nosec comments
        if any(x in str(file_path) for x in ['docs/', 'tests/security/', 'semgrep_rules/', '.md']):
            return False

        # Pattern 1: subprocess.call(shlex.split(cmd) if isinstance(cmd, str) else cmd, shell=False) → subprocess.call(shlex.split(cmd), shell=False)
        # Only fix simple cases where cmd is a single variable
        if re.search(r'subprocess\.call\([^,]+,\s*shell=False\)', content):
            # Add shlex import if not present
            if 'import shlex' not in content and 'from shlex import' not in content:
                # Find the subprocess import line and add shlex after it
                content = re.sub(
                    r'(import subprocess\b)',
                    r'\1\nimport shlex',
                    content,
                    count=1
                )

            # Replace subprocess.call(shlex.split(cmd) if isinstance(cmd, str) else cmd, shell=False) with safe version
            content = re.sub(
                r'subprocess\.call\(([a-zA-Z_][a-zA-Z0-9_]*),\s*shell=False\)',
                r'subprocess.call(shlex.split(\1) if isinstance(\1, str) else \1, shell=False)',
                content
            )

        # Pattern 2: subprocess.run(..., shell=False, ...) → subprocess.run(..., shell=False, ...)
        content = re.sub(
            r'\bshell=True\b',
            'shell=False',
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
            if fix_shell_true_in_file(py_file):
                print(f"✅ Fixed: {py_file.relative_to(base_dir)}")
                fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files with shell=False issues")
    return 0

if __name__ == '__main__':
    sys.exit(main())
