#!/usr/bin/env python3
"""Batch migrator for print → logging statements."""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Optional


def migrate_print_to_logger(source: str, file_path: Path) -> tuple[str, int]:
    """Migrate print statements to logger calls.
    
    Returns:
        (modified_source, num_migrated)
    """
    lines = source.split('\n')
    migrated = 0
    has_logger_import = False
    import_insertion_idx = 0
    
    # Check for existing logger import
    for i, line in enumerate(lines):
        if 'from codex.logging.structured_logger import logger' in line:
            has_logger_import = True
            break
        if line.startswith(('from ', 'import ')) or (i > 0 and lines[i-1].startswith(('from ', 'import '))):
            import_insertion_idx = i + 1
    
    # Add logger import if needed
    if not has_logger_import and 'print(' in source:
        # Find the right place to insert
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith(('from ', 'import ')):
                last_import_idx = i
        
        if last_import_idx > 0:
            lines.insert(last_import_idx + 1, 'from codex.logging.structured_logger import logger')
        elif lines and lines[0].startswith(('from ', 'import ')):
            lines.insert(1, 'from codex.logging.structured_logger import logger')
        else:
            lines.insert(0, 'from codex.logging.structured_logger import logger')
    
    # Migrate print statements
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line
        
        # Skip if no print statement
        if 'print(' not in line:
            new_lines.append(line)
            i += 1
            continue
        
        # Skip docstrings and string literals
        if '"""' in line or "'''" in line:
            new_lines.append(line)
            i += 1
            continue
        
        # Pattern: print(..., file=sys.stderr)  → logger.error(...)
        if 'file=sys.stderr' in line or 'file = sys.stderr' in line:
            line = re.sub(
                r'print\s*\(\s*([^,)]+)\s*,\s*file\s*=\s*sys\.stderr\s*\)',
                r'logger.error(\1)',
                line
            )
            if line != original_line:
                migrated += 1
                line = re.sub(r'\s*#\s*codeql\[.*?\]', '', line)
        
        # Pattern: print("-" * N) → (remove)
        elif re.search(r'print\s*\(\s*["\'][−−−\-=\s]*["\']\s*(\*\s*\d+)?\s*\)', line):
            line = ''
            migrated += 1
        
        # Pattern: print() → (remove)
        elif re.search(r'^\s*print\s*\(\s*\)\s*$', line):
            line = ''
            migrated += 1
        
        # Pattern: print(something) → logger.info(something)
        elif 'print(' in line:
            match = re.search(r'print\s*\(([^)]*)\)', line)
            if match:
                args = match.group(1).strip()
                # Replace print with logger.info
                line = re.sub(
                    r'print\s*\(([^)]+)\)',
                    r'logger.info(\1)',
                    line,
                    count=1
                )
                if line != original_line:
                    migrated += 1
                    line = re.sub(r'\s*#\s*codeql\[.*?\]', '', line)
        
        new_lines.append(line)
        i += 1
    
    new_source = '\n'.join(new_lines)
    
    # Validate syntax
    try:
        ast.parse(new_source)
    except SyntaxError:
        return source, 0  # Return unchanged if syntax error
    
    return new_source, migrated


def main():
    """Batch migrate files."""
    os.chdir('/home/runner/work/_codex_/_codex_')
    
    targets = [
        ('src/codex_ml', 'ML Library'),
        ('tests', 'Tests'),
        ('src/codex', 'Core'),
    ]
    
    total_migrated = 0
    
    for target_dir, label in targets:
        target_path = Path(target_dir)
        if not target_path.exists():
            continue
        
        # Find all Python files with print statements
        py_files = list(target_path.glob('**/*.py'))
        files_to_migrate = []
        
        for f in py_files:
            try:
                content = f.read_text()
                if 'print(' in content and 'from codex.logging.structured_logger import logger' not in content:
                    files_to_migrate.append(f)
            except Exception:
                pass
        
        print(f'\n{label}: {len(files_to_migrate)} files to migrate')
        
        for file_path in sorted(files_to_migrate):
            try:
                source = file_path.read_text()
                new_source, num_migrated = migrate_print_to_logger(source, file_path)
                
                if num_migrated > 0:
                    file_path.write_text(new_source)
                    total_migrated += num_migrated
                    print(f'  ✓ {str(file_path)}: {num_migrated} statements')
            except Exception as e:
                print(f'  ✗ {str(file_path)}: {e}')
    
    print(f'\nTotal migrated: {total_migrated} statements')
    return 0


if __name__ == '__main__':
    sys.exit(main())
