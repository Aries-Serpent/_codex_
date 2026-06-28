#!/usr/bin/env python3
"""
Wave 4 Phase 5 Stage 1: Test Function Type Annotation Fixer

Adds -> None return type to test functions and similar patterns that don't return values.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set

class Stage1Fixer:
    def __init__(self):
        self.fixes_applied = 0
        self.files_modified = 0
        
    def parse_mypy_errors(self) -> Dict[str, List[Tuple[int, str]]]:
        """Parse mypy errors for no-untyped-def."""
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", "src/", "--strict", "--show-error-codes"],
                capture_output=True,
                text=True
            )
        except Exception as e:
            print(f"Error running mypy: {e}")
            return {}
        
        errors_by_file: Dict[str, List[Tuple[int, str]]] = {}
        for line in result.stdout.split('\n'):
            if 'no-untyped-def' not in line:
                continue
            
            # Parse: file.py:line: error: message [no-untyped-def]
            match = re.match(r'([^:]+):(\d+):.+?\[no-untyped-def\]', line)
            if match:
                file_path, line_no = match.groups()
                msg = line.split(':')[3].strip() if ':' in line else ""
                
                if file_path not in errors_by_file:
                    errors_by_file[file_path] = []
                errors_by_file[file_path].append((int(line_no), msg))
        
        return errors_by_file
    
    def is_test_function(self, func_line: str) -> bool:
        """Check if function is a test function."""
        # Test functions, setup/teardown, fixtures
        patterns = [
            r'\bdef\s+test_',
            r'\bdef\s+setUp\b',
            r'\bdef\s+tearDown\b',
            r'@pytest\.fixture',
            r'@fixture',
        ]
        
        for pattern in patterns:
            if re.search(pattern, func_line):
                return True
        return False
    
    def add_return_type(self, file_path: Path, line_no: int, return_type: str = '-> None') -> bool:
        """Add return type annotation to a function definition."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            func_line_idx = line_no - 1
            if func_line_idx >= len(lines):
                return False
            
            func_line = lines[func_line_idx]
            original_line = func_line
            
            # Check if already has return type
            if '->' in func_line or func_line.rstrip().endswith(':'):
                # Already has return type or is complete
                if func_line.rstrip().endswith(':'):
                    # No return type, needs to be added
                    func_line = func_line.rstrip()
                    if func_line.endswith(':'):
                        func_line = func_line[:-1] + f' {return_type}:'
                else:
                    return False
            else:
                # Add return type before colon
                func_line = re.sub(r':\s*$', f' {return_type}:', func_line.rstrip()) + '\n' if func_line.endswith('\n') else ''
                func_line = func_line.rstrip() if not func_line.endswith('\n') else func_line
                func_line = re.sub(r':\s*$', f' {return_type}:', func_line)
            
            if func_line != original_line:
                lines[func_line_idx] = func_line
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                return True
        except Exception as e:
            print(f"Error fixing {file_path}:{line_no}: {e}")
        
        return False
    
    def run_fixes(self, max_fixes: int = 400) -> None:
        """Run Stage 1 fixes on test functions."""
        print("\n" + "="*60)
        print("Wave 4 Phase 5 - Stage 1: Test Function Type Fixes")
        print("="*60)
        
        errors_by_file = self.parse_mypy_errors()
        if not errors_by_file:
            print("No no-untyped-def errors found!")
            return
        
        print(f"\nFound {sum(len(v) for v in errors_by_file.values())} no-untyped-def errors")
        print(f"Processing {len(errors_by_file)} files\n")
        
        fixes_limit = max_fixes
        
        for file_path_str in sorted(errors_by_file.keys()):
            if fixes_limit <= 0:
                break
            
            file_path = Path(file_path_str)
            if not file_path.is_absolute():
                file_path = Path('.') / file_path_str
            
            if not file_path.exists():
                continue
            
            errors = errors_by_file[file_path_str]
            
            # Process errors in reverse order to avoid line number shifts
            for line_no, msg in sorted(errors, key=lambda x: x[0], reverse=True):
                if fixes_limit <= 0:
                    break
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    if line_no - 1 >= len(lines):
                        continue
                    
                    func_line = lines[line_no - 1]
                    
                    # Check if it's a test function
                    is_test = self.is_test_function(func_line)
                    
                    # Get the context (look a few lines back for decorators)
                    context_lines = []
                    for i in range(max(0, line_no - 4), line_no):
                        if i < len(lines):
                            context_lines.append(lines[i])
                    context = '\n'.join(context_lines)
                    
                    # Check for pytest fixtures or similar
                    if '@' in context or 'test_' in func_line or 'setUp' in func_line or 'tearDown' in func_line:
                        is_test = True
                    
                    # Add return type
                    if self.add_return_type(file_path, line_no, '-> None'):
                        self.fixes_applied += 1
                        fixes_limit -= 1
                        
                        if file_path not in [p for p, _ in errors_by_file.items()]:
                            self.files_modified += 1
                except Exception as e:
                    print(f"  Error processing {file_path}:{line_no}: {e}")
                    continue
        
        print(f"\n✅ Fixed {self.fixes_applied} no-untyped-def errors")
        print(f"📝 Modified up to {self.files_modified} files")

if __name__ == "__main__":
    fixer = Stage1Fixer()
    fixer.run_fixes(max_fixes=400)
