#!/usr/bin/env python3
"""Wave 2 Print→Logging Migration Script.

Automatically migrates print() statements to structured logging across:
- src/codex_ml/ (~268 statements)
- tests/ (~628 statements)  
- src/codex/ (remaining statements)

Uses proven Wave 1 patterns:
1. Simple: print("msg") → logger.info("msg")
2. Errors: print("err", file=sys.stderr) → logger.error("err")
3. Formatted: print(f"...") → logger.info("...")
4. Separators: Remove entirely (no logging)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Optional


class PrintMigrator(ast.NodeTransformer):
    """AST-based migrator that identifies and replaces print() calls."""

    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.print_statements = []
        self.has_logger_import = False
        self.replacements = {}

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track if logger is already imported."""
        if node.module == 'codex.logging.structured_logger':
            for alias in node.names:
                if alias.name == 'logger':
                    self.has_logger_import = True
        return node

    def visit_Call(self, node: ast.Call):
        """Find and mark print() calls for migration."""
        self.generic_visit(node)
        
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.print_statements.append(node)
            
        return node


def migrate_file(file_path: Path) -> tuple[int, Optional[str]]:
    """Migrate a single Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple of (num_migrated, error_message)
    """
    source = file_path.read_text()
    
    # Skip if no print statements
    if 'print(' not in source:
        return 0, None
    
    # Skip if already has logger import
    if 'from codex.logging.structured_logger import logger' in source:
        return 0, None
    
    lines = source.split('\n')
    migrated = 0
    
    # Phase 1: Add logger import after other imports
    import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            import_idx = i
        elif line.strip() and not (line.startswith('from ') or line.startswith('import ')):
            break
    
    # Insert logger import after last import
    if import_idx > 0 or lines[0].startswith(('from ', 'import ')):
        lines.insert(import_idx + 1, 'from codex.logging.structured_logger import logger')
    else:
        lines.insert(0, 'from codex.logging.structured_logger import logger')
    
    # Phase 2: Replace print() calls
    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line
        
        # Skip docstrings and comments
        if '"""' in line or "'''" in line or line.strip().startswith('#'):
            i += 1
            continue
        
        # Check if line contains print(
        if 'print(' not in line:
            i += 1
            continue
        
        # Pattern 1: print("message", file=sys.stderr)
        if 'file=sys.stderr' in line:
            line = re.sub(
                r'print\s*\(\s*([^,)]+)\s*,\s*file=sys\.stderr\s*\)',
                r'logger.error(\1)',
                line
            )
            if line != original_line:
                migrated += 1
        
        # Pattern 2: print("-" * N) - separators (remove)
        if re.search(r'print\s*\(\s*["\'][−−−\s\-=]*["\']\s*(\s*\*\s*\d+)?\s*\)', line):
            if '=' not in line or '#' in line:  # Preserve commented lines
                lines[i] = ''
                migrated += 1
                i += 1
                continue
        
        # Pattern 3: print() with no args - remove empty prints
        if re.search(r'print\s*\(\s*\)', line):
            lines[i] = ''
            migrated += 1
            i += 1
            continue
        
        # Pattern 4: Simple print() calls
        if 'print(' in line:
            # Extract the print arguments
            match = re.search(r'print\s*\(([^)]+)\)', line)
            if match:
                args = match.group(1)
                
                # Build logger call based on context
                if args.strip().startswith('f"') or args.strip().startswith("f'"):
                    # Formatted string
                    logger_call = f'logger.info({args})'
                else:
                    # Regular string
                    logger_call = f'logger.info({args})'
                
                line = re.sub(
                    r'print\s*\([^)]+\)',
                    logger_call,
                    line,
                    count=1
                )
                if line != original_line:
                    migrated += 1
        
        if line != original_line:
            # Remove codeql comments
            line = re.sub(r'\s*#\s*codeql\[.*?\]', '', line)
        
        lines[i] = line
        i += 1
    
    # Write back only if we made changes
    if migrated > 0:
        new_source = '\n'.join(lines)
        try:
            # Validate syntax
            ast.parse(new_source)
            file_path.write_text(new_source)
            return migrated, None
        except SyntaxError as e:
            return 0, f"Syntax error: {e}"
    
    return 0, None


def main():
    """Run Wave 2 migrations."""
    targets = [
        ('src/codex_ml', 'Sub-Wave 2.1: ML Library'),
        ('tests', 'Sub-Wave 2.2: Tests'),
        ('src/codex', 'Sub-Wave 2.3: Core'),
    ]
    
    total_migrated = 0
    total_files = 0
    
    for target_dir, label in targets:
        target_path = Path(target_dir)
        if not target_path.exists():
            continue
        
        print(f'\n{label}')
        print('=' * 60)
        
        files_with_print = list(target_path.glob('**/*.py'))
        files_with_print = [f for f in files_with_print if 'print(' in f.read_text()]
        
        subwave_migrated = 0
        
        for file_path in sorted(files_with_print):
            migrated, error = migrate_file(file_path)
            if migrated > 0:
                total_migrated += migrated
                subwave_migrated += migrated
                total_files += 1
                print(f'✓ {file_path.relative_to(Path.cwd())}: {migrated} statements')
            elif error:
                print(f'✗ {file_path.relative_to(Path.cwd())}: {error}')
        
        print(f'\n{label} Summary: {subwave_migrated} statements migrated')
    
    print(f'\n{"="*60}')
    print(f'TOTAL: {total_migrated} statements migrated across {total_files} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
