#!/usr/bin/env python3
"""
Fix Exception Logging Phase3

Purpose:
    Main execution script

Usage:
    python scripts/security/fix_exception_logging_phase3.py [options]

    Examples:
    $ python scripts/security/fix_exception_logging_phase3.py --help

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
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

logger = logging.getLogger(__name__)


def comprehensive_fix(file_path: Path) -> int:
    """Apply comprehensive exception logging fixes."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        fixes = 0

        # Skip test files
        if 'test_' in str(file_path) or '/tests/' in str(file_path):
            return 0

        # Ensure logging infrastructure
        if 'except' in content:
            if 'import logging' not in content:
                # Add after first non-comment, non-docstring line
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_pos = i + 1
                        else:
                            insert_pos = i
                        break
                lines.insert(insert_pos, 'import logging')
                content = '\n'.join(lines)

            if 'logger = logging.getLogger' not in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'import logging' in line:
                        lines.insert(i + 1, 'logger = logging.getLogger(__name__)')
                        break
                content = '\n'.join(lines)

        # Comprehensive pattern matching for all exception types

        # Pattern 1: except with any specific exception type but no logging
        pattern1 = r'except\s+([A-Z][a-zA-Z0-9_]+(?:Error|Exception|Warning)?)\s+as\s+(\w+):\s*\n(\s+)(?!logger\.|logging\.)(.*?)$'
        def repl1(match):
            exc_type, exc_var, indent, code = match.groups()
            if not code.strip():
                return match.group(0)  # Empty handler
            return f'except {exc_type} as {exc_var}:\n{indent}logger.debug(f"{exc_type}: {{{exc_var}}}")\n{indent}{code}'

        new_content = re.sub(pattern1, repl1, content, flags=re.MULTILINE)
        if new_content != content:
            fixes += content.count('except ') - new_content.count('except ')
            content = new_content

        # Pattern 2: except with tuple of exceptions
        pattern2 = r'except\s+\(([^)]+)\)\s+as\s+(\w+):\s*\n(\s+)(?!logger\.|logging\.)(.*?)$'
        def repl2(match):
            exc_types, exc_var, indent, code = match.groups()
            if not code.strip():
                return match.group(0)
            return f'except ({exc_types}) as {exc_var}:\n{indent}logger.debug(f"Exception: {{{exc_var}}}")\n{indent}{code}'

        new_content = re.sub(pattern2, repl2, content, flags=re.MULTILINE)
        if new_content != content:
            fixes += 1
            content = new_content

        # Pattern 3: except KeyError, ValueError, etc. without as clause
        pattern3 = r'except\s+([A-Z][a-zA-Z0-9_]+(?:Error|Exception)):\s*\n(\s+)(?!logger\.|logging\.|pass\s*$|raise\s*$)(.*?)$'
        def repl3(match):
            exc_type, indent, code = match.groups()
            if not code.strip() or code.strip() == 'pass' or code.strip().startswith('raise'):
                return match.group(0)
            return f'except {exc_type} as e:\n{indent}logger.debug(f"{exc_type}: {{e}}")\n{indent}{code}'

        new_content = re.sub(pattern3, repl3, content, flags=re.MULTILINE)
        if new_content != content:
            fixes += 1
            content = new_content

        # Pattern 4: bare except with code (not pass/raise)
        pattern4 = r'except:\s*\n(\s+)(?!logger\.|logging\.|pass\s*$|raise\s*$)(.*?)$'
        def repl4(match):
            indent, code = match.groups()
            if not code.strip() or code.strip() == 'pass' or code.strip().startswith('raise'):
                return match.group(0)
            return f'except Exception as e:\n{indent}logger.debug(f"Exception: {{e}}")\n{indent}{code}'

        new_content = re.sub(pattern4, repl4, content, flags=re.MULTILINE)
        if new_content != content:
            fixes += 1
            content = new_content

        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return max(1, fixes)

        return 0
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return 0

def main():
    """Run comprehensive fix on all files."""
    base_dir = REPO_ROOT
    total_fixes = 0
    files_fixed = 0

    print("🔧 Phase 3: Comprehensive Exception Logging Coverage\n")

    # Process all directories
    for directory in ['src', 'agents', 'scripts']:
        dir_path = base_dir / directory
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob('*.py'):
            # Skip test files
            if 'test_' in py_file.name or '/tests/' in str(py_file):
                continue

            fixes = comprehensive_fix(py_file)
            if fixes > 0:
                print(f"✅ {py_file.relative_to(base_dir)}")
                total_fixes += fixes
                files_fixed += 1

    print("\n📊 Phase 3 Summary:")
    print(f"   Files modified: {files_fixed}")
    print(f"   Handlers improved: {total_fixes}")
    print("   Target: >70% logging coverage")

    return 0

if __name__ == '__main__':
    sys.exit(main())
