#!/usr/bin/env python3
"""
Fix Exception Logging Phase2

Purpose:
    Main execution script

Usage:
    python scripts/security/fix_exception_logging_phase2.py [options]

    Examples:
    $ python scripts/security/fix_exception_logging_phase2.py --help

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


def needs_logging_import(content: str) -> bool:
    """Check if file needs logging import."""
    return 'import logging' not in content

def needs_logger_declaration(content: str) -> bool:
    """Check if file needs logger declaration."""
    return 'logger = logging.getLogger' not in content

def add_logging_infrastructure(content: str) -> str:
    """Add logging import and logger declaration."""
    lines = content.split('\n')

    # Add import logging after shebang/docstring
    import_pos = 0
    in_docstring = False
    for i, line in enumerate(lines):
        if line.startswith('"""') or line.startswith("'''"):
            in_docstring = not in_docstring
        elif not in_docstring and (line.startswith('import ') or line.startswith('from ')):
            import_pos = i + 1
            break
        elif not in_docstring and line.strip() and not line.startswith('#'):
            import_pos = i
            break

    if needs_logging_import(content):
        lines.insert(import_pos, 'import logging')
        import_pos += 1

    if needs_logger_declaration(content):
        lines.insert(import_pos, 'logger = logging.getLogger(__name__)')

    return '\n'.join(lines)

def fix_exception_handlers(file_path: Path) -> int:
    """Fix exception handlers in a file to add logging."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        fixes = 0

        # Skip if file is mostly tests or already has lots of logging
        if 'test_' in str(file_path) or content.count('logger.') > 20:
            return 0

        # Add logging infrastructure if needed
        if 'except' in content:
            content = add_logging_infrastructure(content)

        # Pattern 1: except: with no logging (any code after)
        pattern1 = r'(except:\s*\n)((?:\s+)(?!logger\.|logging\.|pass|raise|return)([^\n]+))'
        def repl1(match):
            indent = len(match.group(2)) - len(match.group(2).lstrip())
            spaces = ' ' * indent
            return f'{match.group(1)}{spaces}logger.warning("Exception in {file_path.name}", exc_info=True)\n{match.group(2)}'

        new_content = re.sub(pattern1, repl1, content)
        if new_content != content:
            fixes += 1
            content = new_content

        # Pattern 2: except Exception: with no logging
        pattern2 = r'(except\s+Exception:\s*\n)((?:\s+)(?!logger\.|logging\.|pass|raise|return)([^\n]+))'
        def repl2(match):
            indent = len(match.group(2)) - len(match.group(2).lstrip())
            spaces = ' ' * indent
            return f'{match.group(1)}{spaces}logger.warning("Exception occurred", exc_info=True)\n{match.group(2)}'

        new_content = re.sub(pattern2, repl2, content)
        if new_content != content:
            fixes += 1
            content = new_content

        # Pattern 3: except SpecificError: without as e, and no logging
        pattern3 = r'(except\s+([A-Z][a-zA-Z]+(?:Error|Exception)):\s*\n)((?:\s+)(?!logger\.|logging\.|pass|raise|return)([^\n]+))'
        def repl3(match):
            error_type = match.group(2)
            indent = len(match.group(3)) - len(match.group(3).lstrip())
            spaces = ' ' * indent
            return f'except {error_type} as e:\n{spaces}logger.warning(f"{error_type}: {{e}}", exc_info=True)\n{match.group(3)}'

        new_content = re.sub(pattern3, repl3, content)
        if new_content != content:
            fixes += 1
            content = new_content

        # Pattern 4: try-except with continue but no logging
        pattern4 = r'(except[^:]*:\s*\n)(\s+)(continue)'
        replacement4 = r'\1\2logger.debug("Exception caught, continuing", exc_info=True)\n\2\3'
        new_content = re.sub(pattern4, replacement4, content)
        if new_content != content:
            fixes += 1
            content = new_content

        # Pattern 5: try-except with return but no logging
        pattern5 = r'(except[^:]*:\s*\n)(\s+)(return (?!logger))'
        replacement5 = r'\1\2logger.debug("Exception caught, returning", exc_info=True)\n\2\3'
        new_content = re.sub(pattern5, replacement5, content)
        if new_content != content:
            fixes += 1
            content = new_content

        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return fixes

        return 0
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return 0

def main():
    """Fix all Python files."""
    base_dir = REPO_ROOT
    total_fixes = 0
    files_fixed = 0

    print("🔧 Phase 2: Enhanced Exception Handler Logging\n")

    # Process src/ directory
    for py_file in (base_dir / 'src').rglob('*.py'):
        fixes = fix_exception_handlers(py_file)
        if fixes > 0:
            print(f"✅ {py_file.relative_to(base_dir)}: {fixes} handlers")
            total_fixes += fixes
            files_fixed += 1

    # Process agents/ directory
    for py_file in (base_dir / 'agents').rglob('*.py'):
        fixes = fix_exception_handlers(py_file)
        if fixes > 0:
            print(f"✅ {py_file.relative_to(base_dir)}: {fixes} handlers")
            total_fixes += fixes
            files_fixed += 1

    # Process scripts/ directory (selected)
    for pattern in ['scripts/security/*.py', 'scripts/analysis/*.py', 'scripts/*.py']:
        for py_file in base_dir.glob(pattern):
            if py_file.is_file():
                fixes = fix_exception_handlers(py_file)
                if fixes > 0:
                    print(f"✅ {py_file.relative_to(base_dir)}: {fixes} handlers")
                    total_fixes += fixes
                    files_fixed += 1

    print("\n📊 Summary:")
    print(f"   Files modified: {files_fixed}")
    print(f"   Exception handlers improved: {total_fixes}")
    print("   Target coverage: >70%")

    return 0

if __name__ == '__main__':
    sys.exit(main())
