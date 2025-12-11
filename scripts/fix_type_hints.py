#!/usr/bin/env python3
"""
Type Hints Fixer

Automatically detects and fixes missing typing imports in Python files.

Features:
- AST-based detection of type hint usage
- Auto-adds missing imports from typing module
- Supports dry-run mode for safe preview
- Batch processing of multiple files

Usage:
    python scripts/fix_type_hints.py --file path/to/file.py
    python scripts/fix_type_hints.py --directory scripts/ --dry-run
    python scripts/fix_type_hints.py --file myfile.py --fix
"""

import argparse
import ast
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Common typing imports
TYPING_NAMES = {
    'Any', 'Dict', 'List', 'Set', 'Tuple', 'Optional', 'Union',
    'Callable', 'Iterable', 'Iterator', 'Sequence', 'Mapping',
    'TypeVar', 'Generic', 'Type', 'cast', 'overload',
    'ClassVar', 'Final', 'Literal', 'Protocol', 'runtime_checkable'
}


class TypeHintVisitor(ast.NodeVisitor):
    """AST visitor to detect type hint usage."""
    
    def __init__(self):
        self.used_types: Set[str] = set()
        self.imported_from_typing: Set[str] = set()
        self.has_typing_import = False
        self.typing_import_line = None
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports from typing module."""
        if node.module == 'typing':
            self.has_typing_import = True
            self.typing_import_line = node.lineno
            for alias in node.names:
                if alias.name == '*':
                    self.imported_from_typing.update(TYPING_NAMES)
                else:
                    self.imported_from_typing.add(alias.name)
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name) -> None:
        """Track usage of typing names."""
        if node.id in TYPING_NAMES:
            self.used_types.add(node.id)
        self.generic_visit(node)
    
    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Track subscripted types like List[int]."""
        if isinstance(node.value, ast.Name) and node.value.id in TYPING_NAMES:
            self.used_types.add(node.value.id)
        self.generic_visit(node)
    
    def visit_arg(self, node: ast.arg) -> None:
        """Track type annotations in function arguments."""
        if node.annotation:
            self._extract_types_from_annotation(node.annotation)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track return type annotations."""
        if node.returns:
            self._extract_types_from_annotation(node.returns)
        self.generic_visit(node)
    
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Track variable annotations."""
        if node.annotation:
            self._extract_types_from_annotation(node.annotation)
        self.generic_visit(node)
    
    def _extract_types_from_annotation(self, annotation: ast.AST) -> None:
        """Extract type names from annotation."""
        if isinstance(annotation, ast.Name) and annotation.id in TYPING_NAMES:
            self.used_types.add(annotation.id)
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name) and annotation.value.id in TYPING_NAMES:
                self.used_types.add(annotation.value.id)
            # Recursively extract from subscript elements
            if isinstance(annotation.slice, ast.Tuple):
                for elt in annotation.slice.elts:
                    self._extract_types_from_annotation(elt)
            else:
                self._extract_types_from_annotation(annotation.slice)


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a Python file for typing import issues.
    
    Returns:
        Dictionary with analysis results
    """
    if not file_path.exists() or file_path.suffix != '.py':
        return {"error": "Not a Python file or doesn't exist"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        visitor = TypeHintVisitor()
        visitor.visit(tree)
        
        missing = visitor.used_types - visitor.imported_from_typing
        
        return {
            "file": str(file_path),
            "used_types": sorted(visitor.used_types),
            "imported": sorted(visitor.imported_from_typing),
            "missing": sorted(missing),
            "has_typing_import": visitor.has_typing_import,
            "typing_import_line": visitor.typing_import_line,
            "needs_fix": len(missing) > 0
        }
    
    except (SyntaxError, UnicodeDecodeError) as e:
        logger.warning(f"Could not parse {file_path}: {e}")
        return {"error": str(e)}


def fix_imports(file_path: Path, analysis: Dict, dry_run: bool = True) -> bool:
    """
    Fix missing typing imports in a file.
    
    Returns:
        True if fixed successfully, False otherwise
    """
    if not analysis.get("needs_fix"):
        return False
    
    missing = analysis["missing"]
    if not missing:
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find where to insert the import
        insert_line = 0
        has_typing_import = analysis.get("has_typing_import")
        typing_line = analysis.get("typing_import_line")
        
        if has_typing_import and typing_line:
            # Update existing import
            for i, line in enumerate(lines):
                if i + 1 == typing_line:
                    # Parse existing import
                    if 'from typing import' in line:
                        # Extract current imports
                        import_part = line.split('import')[1].strip()
                        current_imports = [x.strip() for x in import_part.rstrip('\n').split(',')]
                        
                        # Add missing imports
                        all_imports = sorted(set(current_imports + list(missing)))
                        new_import = f"from typing import {', '.join(all_imports)}\n"
                        lines[i] = new_import
                        break
        else:
            # Find appropriate place to add import
            # After other imports or after docstring
            in_docstring = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Handle docstrings
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if not in_docstring:
                        in_docstring = True
                        if stripped.endswith('"""') or stripped.endswith("'''"):
                            in_docstring = False
                    else:
                        in_docstring = False
                    continue
                
                if in_docstring:
                    continue
                
                # Skip comments and blank lines at start
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Found first real line
                if stripped.startswith('import ') or stripped.startswith('from '):
                    continue
                else:
                    insert_line = i
                    break
            
            # Insert new import
            new_import = f"from typing import {', '.join(sorted(missing))}\n"
            if insert_line > 0 and lines[insert_line - 1].strip():
                lines.insert(insert_line, new_import)
            else:
                lines.insert(insert_line, new_import)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would add/update: from typing import {', '.join(sorted(missing))}")
            return True
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info(f"Fixed {file_path}: Added {', '.join(sorted(missing))}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to fix {file_path}: {e}")
        return False


def process_directory(directory: Path, dry_run: bool = True, fix: bool = False) -> Dict[str, int]:
    """Process all Python files in a directory."""
    stats = {
        "total": 0,
        "needs_fix": 0,
        "fixed": 0,
        "errors": 0
    }
    
    for py_file in directory.rglob('*.py'):
        stats["total"] += 1
        analysis = analyze_file(py_file)
        
        if "error" in analysis:
            stats["errors"] += 1
            continue
        
        if analysis.get("needs_fix"):
            stats["needs_fix"] += 1
            logger.info(f"\n{py_file}: Missing {analysis['missing']}")
            
            if fix:
                if fix_imports(py_file, analysis, dry_run):
                    stats["fixed"] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Fix missing typing imports in Python files'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Python file to analyze/fix'
    )
    parser.add_argument(
        '--directory',
        type=Path,
        help='Directory to scan recursively'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would be changed without modifying files (default: True)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Actually apply fixes (disables dry-run)'
    )
    
    args = parser.parse_args()
    
    dry_run = args.dry_run and not args.fix
    
    if dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be modified")
        logger.info("=" * 60)
        logger.info("")
    
    if args.file:
        analysis = analyze_file(args.file)
        
        if "error" in analysis:
            logger.error(f"Error: {analysis['error']}")
            return 1
        
        if analysis.get("needs_fix"):
            logger.info(f"\nFile: {args.file}")
            logger.info(f"Used types: {analysis['used_types']}")
            logger.info(f"Imported: {analysis['imported']}")
            logger.info(f"Missing: {analysis['missing']}")
            
            if args.fix or dry_run:
                fix_imports(args.file, analysis, dry_run)
        else:
            logger.info(f"✅ {args.file}: No missing imports")
        
        return 0
    
    elif args.directory:
        stats = process_directory(args.directory, dry_run, args.fix or dry_run)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Summary:")
        logger.info(f"  Total files: {stats['total']}")
        logger.info(f"  Need fixes: {stats['needs_fix']}")
        if args.fix:
            logger.info(f"  Fixed: {stats['fixed']}")
        logger.info(f"  Errors: {stats['errors']}")
        logger.info(f"{'='*60}")
        
        return 0 if stats['errors'] == 0 else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
