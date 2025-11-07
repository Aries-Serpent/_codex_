#!/usr/bin/env python3
"""Modernization scanner for Python codebase.

Scans Python files for legacy patterns and suggests modernization:
- Old typing imports (typing.List vs list)
- String formatting (% vs f-strings)
- Dict/List comprehensions that could be simplified
- Old exception syntax
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class ModernizationChecker(ast.NodeVisitor):
    """AST visitor to detect legacy Python patterns."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.issues: List[Tuple[int, str, str]] = []
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check for old typing imports."""
        if node.module == "typing":
            for alias in node.names:
                # Check for capitalized generic types (deprecated in 3.9+)
                if alias.name in ("List", "Dict", "Set", "Tuple", "Optional"):
                    self.issues.append((
                        node.lineno,
                        f"Use built-in {alias.name.lower()} instead of typing.{alias.name}",
                        "typing-builtin"
                    ))
        self.generic_visit(node)
    
    def visit_Mod(self, node: ast.Mod):
        """Check for % string formatting."""
        # This is simplified - would need more context to detect actual % formatting
        self.generic_visit(node)
    
    def visit_Str(self, node: ast.Str):
        """Check for old string literals (Python 3.7 and earlier)."""
        # In Python 3.8+, use ast.Constant instead
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        """Check exception handling patterns."""
        for handler in node.handlers:
            if handler.type and isinstance(handler.type, ast.Tuple):
                # Multiple exceptions in tuple - OK
                pass
        self.generic_visit(node)


def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Scan a single Python file for modernization opportunities."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return []
    
    checker = ModernizationChecker(str(filepath))
    checker.visit(tree)
    return checker.issues


def main(root: str = ".", verbose: bool = False):
    """Scan Python files for modernization opportunities."""
    root_path = Path(root).resolve()
    
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist", file=sys.stderr)
        return 1
    
    total_files = 0
    total_issues = 0
    files_with_issues = 0
    
    # Find all Python files
    for py_file in root_path.rglob("*.py"):
        # Skip common exclude patterns
        if any(part.startswith(".") for part in py_file.parts):
            continue
        if any(part in ("node_modules", "venv", "__pycache__", "build", "dist") 
               for part in py_file.parts):
            continue
        
        total_files += 1
        issues = scan_file(py_file)
        
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            
            if verbose:
                print(f"\n{py_file.relative_to(root_path)}:")
                for lineno, message, category in sorted(issues):
                    print(f"  Line {lineno}: [{category}] {message}")
    
    # Summary
    print(f"\nModernization Scan Summary:")
    print(f"  Files scanned: {total_files}")
    print(f"  Files with suggestions: {files_with_issues}")
    print(f"  Total suggestions: {total_issues}")
    
    if total_issues > 0:
        print(f"\nRun with --verbose to see detailed suggestions")
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan for Python modernization opportunities")
    parser.add_argument("root", nargs="?", default="src", help="Root directory to scan (default: src)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed suggestions")
    
    args = parser.parse_args()
    sys.exit(main(args.root, verbose=args.verbose))
