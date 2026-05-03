#!/usr/bin/env python3
"""
Fix deprecated datetime.now(timezone.utc) calls across the codebase.

This script:
1. Replaces datetime.now(timezone.utc) with datetime.now(timezone.utc)
2. Adds timezone import where needed
3. Handles various import patterns
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Set


def fix_datetime_file(filepath: Path) -> bool:
    """Fix datetime.now(timezone.utc) usage in a single file."""
    try:
        content = filepath.read_text()
        original = content

        # Check if file uses datetime.now(timezone.utc)
        if 'datetime.now(timezone.utc)' not in content and '_dt.datetime.now(_dt.timezone.utc)' not in content:
            return False

        # Replace datetime.now(timezone.utc) with datetime.now(timezone.utc)
        content = content.replace('datetime.now(timezone.utc)', 'datetime.now(timezone.utc)')

        # Replace _dt.datetime.now(_dt.timezone.utc) with _dt.datetime.now(_dt.timezone.utc)
        content = content.replace('_dt.datetime.now(_dt.timezone.utc)', '_dt.datetime.now(_dt.timezone.utc)')

        # Add timezone import if needed
        if 'datetime.now(timezone.utc)' in content or '_dt.datetime.now(_dt.timezone.utc)' in content:
            # Check if timezone is already imported
            has_timezone = False

            # Check various import patterns
            if re.search(r'from datetime import.*timezone', content) or (re.search(r'import datetime as _dt', content) and 'timezone.utc' in content):
                has_timezone = True

            if not has_timezone:
                # Find datetime import line and add timezone
                # Pattern 1: from datetime import ...
                pattern1 = r'(from datetime import [^;\n]+)'
                match = re.search(pattern1, content)
                if match:
                    import_line = match.group(1)
                    if 'timezone' not in import_line:
                        new_import = import_line.rstrip() + ', timezone'
                        content = content.replace(import_line, new_import)
                        has_timezone = True

                # Pattern 2: import datetime (as alias)
                if not has_timezone:
                    # For import datetime or import datetime as _dt
                    # timezone is accessed via datetime.timezone or _dt.timezone
                    # No additional import needed
                    if 'import datetime' in content:
                        has_timezone = True

        if content != original:
            filepath.write_text(content)
            return True
        return False

    except Exception as e:
        print(f"Error fixing {filepath}: {e}", file=sys.stderr)
        return False


def main() -> int:
    """Main entry point."""
    repo_root = Path.cwd()
    scripts_dir = repo_root / 'scripts'
    if not scripts_dir.exists():
        print("Error: scripts/ directory not found", file=sys.stderr)
        return 1

    fixed_files: Set[Path] = set()
    error_files: Set[Path] = set()

    print("🔄 Fixing deprecated datetime.now(timezone.utc) calls...\n")

    for py_file in scripts_dir.rglob('*.py'):
        try:
            if fix_datetime_file(py_file):
                fixed_files.add(py_file)
                print(f"  ✅ Fixed: {py_file.relative_to(repo_root)}")
        except Exception as e:
            error_files.add(py_file)
            print(f"  ❌ Error: {py_file.relative_to(repo_root)}: {e}")

    print("\n📊 Summary:")
    print(f"  ✅ Fixed: {len(fixed_files)} files")
    if error_files:
        print(f"  ❌ Errors: {len(error_files)} files")

    return 0 if not error_files else 1


if __name__ == '__main__':
    sys.exit(main())
