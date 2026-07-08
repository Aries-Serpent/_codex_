#!/usr/bin/env python3
"""AST-based print → logging migrator."""

import ast
import sys
import os
from pathlib import Path


class PrintCallFinder(ast.NodeVisitor):
    """Find all print() calls using AST."""
    
    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.print_calls = []
    
    def visit_Call(self, node):
        """Find print() calls."""
        # Check if this is a call to 'print'
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            # Record the line range
            start_line = node.lineno - 1
            end_line = node.end_lineno if node.end_lineno else node.lineno
            self.print_calls.append({
                'start': start_line,
                'end': end_line,
                'node': node
            })
        
        self.generic_visit(node)


def migrate_file_ast(source: str, file_path: Path) -> tuple[str, int]:
    """Migrate using AST to find print() calls."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, 0
    
    lines = source.split('\n')
    
    # Check for existing logger import
    has_logger = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'codex.logging.structured_logger':
                for alias in node.names:
                    if alias.name == 'logger':
                        has_logger = True
                        break
    
    # Find all print() calls
    finder = PrintCallFinder(lines)
    finder.visit(tree)
    
    if not finder.print_calls:
        return source, 0
    
    migrated = 0
    
    # Add logger import if needed
    if not has_logger:
        # Find insertion point (after last import)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith(('from ', 'import ')):
                insert_idx = i + 1
        lines.insert(insert_idx, 'from codex.logging.structured_logger import logger')
        
        # Adjust print call line numbers
        for call in finder.print_calls:
            call['start'] += 1
            call['end'] += 1
    
    # Process print calls in reverse order to avoid line number issues
    for call in sorted(finder.print_calls, key=lambda x: x['start'], reverse=True):
        start = call['start']
        end = call['end']
        
        # Extract the print statement
        print_lines = lines[start:end]
        print_source = '\n'.join(print_lines)
        
        # Check for file=sys.stderr
        if 'file=sys.stderr' in print_source or 'file = sys.stderr' in print_source:
            # Extract the message argument
            # For now, just replace print(..., file=sys.stderr) with logger.error(...)
            new_lines = []
            for line in print_lines:
                if 'file=sys.stderr' in line or 'file = sys.stderr' in line:
                    # Remove the file argument
                    line = line.replace('file=sys.stderr', '').replace('file = sys.stderr', '')
                    line = line.rstrip(',) ') + ')'
                    line = line.replace('print(', 'logger.error(')
                    migrated += 1
                new_lines.append(line)
            lines[start:end] = new_lines
        elif '"-' in print_source or "'-" in print_source:
            # Likely a separator, remove it
            lines[start:end] = []
            migrated += 1
        else:
            # Regular print, convert to logger.info
            new_lines = []
            for i, line in enumerate(print_lines):
                if i == 0:
                    line = line.replace('print(', 'logger.info(')
                    migrated += 1
                new_lines.append(line)
            lines[start:end] = new_lines
    
    # Remove codeql comments
    lines = [l.replace('  # codeql[py/clear-text-logging-sensitive-data]', '') for l in lines]
    
    new_source = '\n'.join(lines)
    
    # Validate syntax
    try:
        ast.parse(new_source)
    except SyntaxError:
        return source, 0
    
    return new_source, migrated


def main():
    """Run AST-based migration."""
    os.chdir('/home/runner/work/_codex_/_codex_')
    
    targets = [
        ('src/codex_ml', 'ML Library'),
        ('tests', 'Tests'),
        ('src/codex', 'Core'),
    ]
    
    total_migrated = 0
    total_files = 0
    
    for target_dir, label in targets:
        target_path = Path(target_dir)
        if not target_path.exists():
            continue
        
        py_files = list(target_path.glob('**/*.py'))
        files_done = 0
        
        for file_path in sorted(py_files):
            try:
                source = file_path.read_text()
                
                # Skip if already has logger
                if 'from codex.logging.structured_logger import logger' in source:
                    continue
                
                # Skip if no print
                if 'print(' not in source:
                    continue
                
                # Skip console.print (Rich library)
                if 'console.print' in source:
                    lines = source.split('\n')
                    has_real_print = False
                    for i, line in enumerate(lines):
                        if 'print(' in line and 'console.print' not in line:
                            has_real_print = True
                            break
                    if not has_real_print:
                        continue
                
                new_source, num_migrated = migrate_file_ast(source, file_path)
                
                if num_migrated > 0:
                    file_path.write_text(new_source)
                    total_migrated += num_migrated
                    total_files += 1
                    files_done += 1
                    
                    if files_done % 10 == 0:
                        print(f'  [{files_done}] {str(file_path)}: {num_migrated}')
            
            except Exception:
                pass
        
        print(f'{label}: {files_done} files, {total_migrated} total migrated so far\n')
    
    print(f'TOTAL: {total_migrated} statements migrated across {total_files} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
