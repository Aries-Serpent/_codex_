#!/usr/bin/env python3
"""
Auto Document Python

Purpose:
    Main execution script

Usage:
    python scripts/auto_document_python.py [options]

    Examples:
    $ python scripts/auto_document_python.py --help

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



import ast
import sys
from pathlib import Path


def analyze_module(file_path: Path) -> tuple[bool, list[str]]:
    """
    Analyze a Python module for missing documentation.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Tuple of (has_module_doc, missing_items)
        where missing_items is a list of undocumented classes/functions

    Raises:
        SyntaxError: If the Python file has syntax errors
    """
    with open(file_path) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file_path}: {e}")
            return False, []

    # Check module docstring
    has_module_doc = ast.get_docstring(tree) is not None

    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                missing.append(f"{node.__class__.__name__}: {node.name}")

    return has_module_doc, missing

def generate_module_docstring(file_path: Path) -> str:
    """
    Generate a module-level docstring based on file path and contents.

    Args:
        file_path: Path to the Python module

    Returns:
        Generated docstring text
    """
    module_name = file_path.stem
    # Capitalize and add spaces
    title = module_name.replace('_', ' ').title()

    return f'''"""
{title} Module

This module provides functionality for {title.lower()}.

Usage:
    from {file_path.parent.name}.{module_name} import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""
'''

def add_module_docstring(file_path: Path) -> bool:
    """
    Add a module docstring to a Python file that lacks one.

    Args:
        file_path: Path to the Python file

    Returns:
        True if docstring was added, False otherwise
    """
    with open(file_path) as f:
        content = f.read()

    # Skip if already has triple quotes at start
    if content.strip().startswith('"""') or content.strip().startswith("'''"):
        return False

    docstring = generate_module_docstring(file_path)

    # Insert after shebang and imports if present
    lines = content.split('\n')
    insert_idx = 0

    # Skip shebang
    if lines and lines[0].startswith('#!'):
        insert_idx = 1

    # Skip encoding declarations
    if insert_idx < len(lines) and 'coding' in lines[insert_idx]:
        insert_idx += 1

    # Insert docstring
    lines.insert(insert_idx, docstring)

    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))

    return True

def process_directory(directory: Path) -> dict:
    """
    Process all Python files in a directory.

    Args:
        directory: Directory to process

    Returns:
        Dictionary with statistics
    """
    stats = {
        'processed': 0,
        'documented': 0,
        'errors': 0
    }

    for py_file in directory.rglob('*.py'):
        if '__pycache__' in str(py_file) or 'test_' in py_file.name:
            continue

        stats['processed'] += 1

        try:
            has_doc, _missing = analyze_module(py_file)
            if not has_doc:
                if add_module_docstring(py_file):
                    stats['documented'] += 1
                    print(f"✅ Added module docstring to {py_file}")
            else:
                print(f"✓  {py_file} already documented")
        except Exception as e:
            stats['errors'] += 1
            print(f"❌ Error processing {py_file}: {e}")

    return stats

def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/auto_document_python.py [module_path|--all]")
        sys.exit(1)

    directory = Path('src') if sys.argv[1] == '--all' else Path(sys.argv[1])

    if not directory.exists():
        print(f"❌ Path {directory} does not exist")
        sys.exit(1)

    print(f"📚 Processing Python modules in {directory}")
    print("="*60)

    stats = process_directory(directory)

    print("\n" + "="*60)
    print("📊 Documentation Statistics:")
    print(f"   Processed: {stats['processed']} files")
    print(f"   Documented: {stats['documented']} files")
    print(f"   Errors: {stats['errors']} files")
    print(f"   Success Rate: {(stats['documented']/max(stats['processed'],1))*100:.1f}%")

if __name__ == '__main__':
    main()
