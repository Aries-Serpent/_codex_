#!/usr/bin/env python3
"""
Print to Logger Converter

AST-based refactoring tool to convert print() calls to appropriate logger calls.

Features:
- Detects print() statements in modules with logging
- Suggests appropriate log level based on context
- Auto-converts with dry-run mode
- Preserves formatting and f-strings
- Handles multiple arguments

Usage:
    python scripts/convert_print_to_logger.py --file path/to/file.py --dry-run
    python scripts/convert_print_to_logger.py --directory scripts/ --fix
"""

import argparse
import ast
import logging
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Cache AST unparse availability (Python 3.9+)
HAS_AST_UNPARSE = hasattr(ast, 'unparse')


class PrintDetector(ast.NodeVisitor):
    """AST visitor to detect print() calls."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.print_calls: List[Tuple[int, str, str]] = []  # (line, context, suggested_level)
        self.has_logging_import = False
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check if logging is imported."""
        if node.module == 'logging':
            self.has_logging_import = True
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check if logging is imported."""
        for alias in node.names:
            if alias.name == 'logging':
                self.has_logging_import = True
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Detect print() calls."""
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            # Determine context and suggest log level
            level = self._suggest_log_level(node)
            
            # Get the print statement
            try:
                context = ast.unparse(node) if HAS_AST_UNPARSE else "print(...)"
            except:
                context = "print(...)"
            
            self.print_calls.append((node.lineno, context, level))
        
        self.generic_visit(node)
    
    def _suggest_log_level(self, node: ast.Call) -> str:
        """Suggest appropriate log level based on context."""
        # Check arguments for keywords
        args_str = ""
        for arg in node.args:
            try:
                if HAS_AST_UNPARSE:
                    args_str += ast.unparse(arg).lower()
                else:
                    args_str += str(arg).lower()
            except:
                pass
        
        # Check for error/warning indicators
        if any(word in args_str for word in ['error', 'fail', 'exception', 'fatal']):
            return 'error'
        elif any(word in args_str for word in ['warning', 'warn', 'caution']):
            return 'warning'
        elif any(word in args_str for word in ['debug', 'trace']):
            return 'debug'
        else:
            return 'info'


def analyze_file(file_path: Path) -> Tuple[bool, List[Tuple[int, str, str]]]:
    """
    Analyze a Python file for print() calls.
    
    Returns:
        (has_logging_import, list of print calls)
    """
    if not file_path.exists() or file_path.suffix != '.py':
        return False, []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        detector = PrintDetector(str(file_path))
        detector.visit(tree)
        
        return detector.has_logging_import, detector.print_calls
    
    except (SyntaxError, UnicodeDecodeError) as e:
        logger.warning(f"Could not parse {file_path}: {e}")
        return False, []


def convert_print_to_logger(
    file_path: Path,
    print_calls: List[Tuple[int, str, str]],
    dry_run: bool = True
) -> bool:
    """
    Convert print() calls to logger calls.
    
    Returns:
        True if conversions were made, False otherwise
    """
    if not print_calls:
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        changes_made = False
        
        # Sort by line number descending to maintain line numbers
        for line_num, context, level in sorted(print_calls, reverse=True, key=lambda x: x[0]):
            if 1 <= line_num <= len(lines):
                original_line = lines[line_num - 1]
                
                # Convert print(...) to logger.level(...)
                new_line = convert_print_statement(original_line, level)
                
                if new_line != original_line:
                    if dry_run:
                        logger.info(f"[DRY RUN] Line {line_num}:")
                        logger.info(f"  - {original_line.rstrip()}")
                        logger.info(f"  + {new_line.rstrip()}")
                    else:
                        lines[line_num - 1] = new_line
                    changes_made = True
        
        if not dry_run and changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            logger.info(f"Converted {len(print_calls)} print() call(s) in {file_path}")
        
        return changes_made
    
    except Exception as e:
        logger.error(f"Failed to convert {file_path}: {e}")
        return False


def convert_print_statement(line: str, level: str) -> str:
    """
    Convert a single print() statement to logger call.
    
    Uses AST parsing to robustly handle quoted strings, f-strings, and multiple arguments.
    Falls back to regex patterns if AST parsing fails.
    
    Preserves indentation and comments.
    
    Limitations: 
    - May not handle all edge cases with complex nested expressions
    - Comments within the print statement may not be preserved correctly
    """
    # Preserve indentation
    indent = ""
    stripped = line.lstrip()
    if stripped != line:
        indent = line[:len(line) - len(stripped)]
    
    # Try to parse the line as Python code using AST
    try:
        # Extract comment if present
        comment = ""
        if "#" in line:
            code_part = line[:line.index("#")]
            comment = " " + line[line.index("#"):]
        else:
            code_part = line
        
        tree = ast.parse(code_part.strip())
        
        # Find print calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Name) and call.func.id == "print":
                    # Use ast.unparse if available (Python 3.9+), else fallback to regex
                    if HAS_AST_UNPARSE:
                        # Reconstruct arguments
                        args_src = [ast.unparse(arg) for arg in call.args]
                        logger_call = f"{indent}logger.{level}({', '.join(args_src)}){comment}"
                        return logger_call
                    else:
                        # Fallback to regex for older Python versions
                        break
    except Exception:
        # If AST parsing fails, fallback to regex patterns
        pass
    
    # Fallback: Use regex patterns (with documented limitations)
    # These patterns may not correctly handle nested quotes or escaped quotes
    patterns = [
        # print(f"...")
        (r'print\((f["\'].*?["\'])\)', rf'logger.{level}(\1)'),
        # print("...")
        (r'print\((["\'].*?["\'])\)', rf'logger.{level}(\1)'),
        # print(variable)
        (r'print\(([^)]+)\)', rf'logger.{level}(\1)'),
    ]
    
    result = line
    for pattern, replacement in patterns:
        new_result = re.sub(pattern, replacement, result)
        if new_result != result:
            result = new_result
            break
    
    return result


def add_logging_import(file_path: Path, dry_run: bool = True) -> bool:
    """Add logging import if not present."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find where to insert import
        insert_line = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                insert_line = i + 1
            elif stripped and not stripped.startswith('#'):
                break
        
        # Add import and logger setup
        import_lines = [
            "import logging\n",
            "\n",
            "logger = logging.getLogger(__name__)\n",
            "\n"
        ]
        
        if dry_run:
            logger.info(f"[DRY RUN] Would add logging import at line {insert_line + 1}")
            return True
        
        lines[insert_line:insert_line] = import_lines
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info(f"Added logging import to {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to add logging import to {file_path}: {e}")
        return False


def process_directory(directory: Path, fix: bool = False, dry_run: bool = True) -> dict:
    """Process all Python files in a directory."""
    stats = {
        "total": 0,
        "with_prints": 0,
        "needs_import": 0,
        "converted": 0,
        "total_prints": 0
    }
    
    for py_file in directory.rglob('*.py'):
        stats["total"] += 1
        has_logging, print_calls = analyze_file(py_file)
        
        if print_calls:
            stats["with_prints"] += 1
            stats["total_prints"] += len(print_calls)
            
            logger.info(f"\n{py_file}: Found {len(print_calls)} print() call(s)")
            for line, context, level in print_calls:
                logger.info(f"  Line {line} → logger.{level}()")
            
            if not has_logging:
                stats["needs_import"] += 1
                logger.info(f"  ⚠️  No logging import found")
                if fix:
                    add_logging_import(py_file, dry_run)
            
            if fix:
                if convert_print_to_logger(py_file, print_calls, dry_run):
                    stats["converted"] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Convert print() calls to logger calls'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Python file to analyze/convert'
    )
    parser.add_argument(
        '--directory',
        type=Path,
        help='Directory to scan recursively'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Apply conversions (disables dry-run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would be changed without modifying files (default: True)'
    )
    
    args = parser.parse_args()
    
    dry_run = args.dry_run if not args.fix else False
    
    if dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be modified")
        logger.info("=" * 60)
        logger.info("")
    
    if args.file:
        has_logging, print_calls = analyze_file(args.file)
        
        if print_calls:
            logger.info(f"\nFile: {args.file}")
            logger.info(f"Found {len(print_calls)} print() call(s):")
            for line, context, level in print_calls:
                logger.info(f"  Line {line}: {context} → logger.{level}()")
            
            if not has_logging:
                logger.info(f"\n⚠️  No logging import found")
                if args.fix or dry_run:
                    add_logging_import(args.file, dry_run)
            
            if args.fix or dry_run:
                convert_print_to_logger(args.file, print_calls, dry_run)
        else:
            logger.info(f"✅ {args.file}: No print() calls found")
        
        return 0
    
    elif args.directory:
        stats = process_directory(args.directory, args.fix or dry_run, dry_run)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Summary:")
        logger.info(f"  Total files: {stats['total']}")
        logger.info(f"  Files with print(): {stats['with_prints']}")
        logger.info(f"  Total print() calls: {stats['total_prints']}")
        logger.info(f"  Need logging import: {stats['needs_import']}")
        if args.fix:
            logger.info(f"  Files converted: {stats['converted']}")
        logger.info(f"{'='*60}")
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
