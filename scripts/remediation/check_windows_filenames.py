#!/usr/bin/env python3
"""
Pre-commit hook to prevent Windows-incompatible filenames.

Returns non-zero exit code if illegal characters are detected.
"""
import sys
from pathlib import Path


WINDOWS_ILLEGAL_CHARS = set('<>:"/\\|?*')


def check_filename(filepath: str) -> bool:
    """
    Check if filename contains Windows-illegal characters.
    
    Returns:
        True if valid, False if contains illegal characters
    """
    filename = Path(filepath).name
    illegal = WINDOWS_ILLEGAL_CHARS.intersection(set(filename))
    
    if illegal:
        print(f"❌ {filepath}")
        print(f"   Contains illegal character(s): {', '.join(repr(c) for c in illegal)}")
        return False
    
    return True


def main(argv=None):
    argv = argv or sys.argv[1:]
    
    if not argv:
        print("No files to check")
        return 0
    
    violations = []
    
    for filepath in argv:
        if not check_filename(filepath):
            violations.append(filepath)
    
    if violations:
        print(f"\n⚠️  Found {len(violations)} file(s) with Windows-incompatible names")
        print("   Fix by renaming or using codex.utils.path_utils.sanitize_filename()")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
