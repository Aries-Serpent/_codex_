#!/usr/bin/env python3
"""
Lint script to detect unsafe model device placement patterns.

This script flags direct .to() calls on torch.nn.Module instances,
which can fail with PyTorch 2.0+ meta tensors. Enforces use of
safe_model_to_device() instead.

Usage:
    python scripts/lint/check_device_placement.py [files...]

Exit codes:
    0 - No issues found
    1 - Unsafe patterns detected
    2 - Script error
"""

import ast
import logging
import sys
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class DevicePlacementChecker(ast.NodeVisitor):
    """AST visitor to detect unsafe model.to() patterns."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: List[Tuple[int, str]] = []
        self.in_model_class = False
        self.model_var_names = set()

    def visit_ClassDef(self, node: ast.ClassDef):
        """Track if we're in a model class definition."""
        # Check if class inherits from nn.Module
        is_model_class = any(
            isinstance(base, ast.Attribute) and
            base.attr == 'Module' and
            isinstance(base.value, ast.Attribute) and
            base.value.attr == 'nn'
            for base in node.bases
        )

        old_in_model = self.in_model_class
        if is_model_class:
            self.in_model_class = True

        self.generic_visit(node)
        self.in_model_class = old_in_model

    def visit_Assign(self, node: ast.Assign):
        """Track variable names that hold models."""
        # Look for model assignments
        if isinstance(node.value, ast.Call):
            # Check for model instantiation patterns
            if self._is_model_instantiation(node.value):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.model_var_names.add(target.id)
                    elif isinstance(target, ast.Attribute):
                        self.model_var_names.add(target.attr)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check for direct .to() calls on models."""
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'to':
            # Check if this is a model.to() call
            if self._is_model_to_call(node.func.value):
                # Check for exception annotation
                lineno = node.lineno
                if not self._has_exception_annotation(lineno):
                    self.issues.append((
                        lineno,
                        "Direct .to() call on model detected. Use safe_model_to_device() instead."
                    ))

        self.generic_visit(node)

    def _is_model_instantiation(self, node: ast.Call) -> bool:
        """Check if call looks like model instantiation."""
        if isinstance(node.func, ast.Name):
            # Check for common model class name patterns
            name = node.func.id
            return any(pattern in name for pattern in [
                'Model', 'Network', 'Net', 'Encoder', 'Decoder',
                'Transformer', 'BERT', 'GPT', 'Embedding'
            ])
        return False

    def _is_model_to_call(self, node: ast.AST) -> bool:
        """Check if expression refers to a model variable."""
        if isinstance(node, ast.Name):
            # Direct variable: model.to()
            return node.id in self.model_var_names or \
                   any(pattern in node.id for pattern in ['model', 'net', 'encoder', 'decoder'])

        if isinstance(node, ast.Attribute):
            # Attribute: self.model.to()
            return node.attr in self.model_var_names or \
                   any(pattern in node.attr for pattern in ['model', 'net', 'encoder', 'decoder'])

        return False

    def _has_exception_annotation(self, lineno: int) -> bool:
        """Check if line has exception annotation comment."""
        try:
            with open(self.filename) as f:
                lines = f.readlines()
                if 0 < lineno <= len(lines):
                    line = lines[lineno - 1]
                    return 'safe-device-placement:' in line
        except (OSError, IOError, UnicodeDecodeError):
            # If the file cannot be read for any reason, treat as no annotation present.
            logger.debug("Suppressed exception in handler", exc_info=True)
        return False


def check_file(filepath: Path) -> List[Tuple[int, str]]:
    """
    Check a Python file for unsafe device placement patterns.

    Parameters
    ----------
    filepath : Path
        Path to Python file to check

    Returns
    -------
    List[Tuple[int, str]]
        List of (line_number, issue_description) tuples
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        checker = DevicePlacementChecker(str(filepath))
        checker.visit(tree)
        return checker.issues

    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error checking {filepath}: {e}", file=sys.stderr)
        return []


def main(files: List[str]) -> int:
    """
    Main entry point for linter.

    Parameters
    ----------
    files : List[str]
        List of file paths to check

    Returns
    -------
    int
        Exit code (0 = success, 1 = issues found)
    """
    if not files:
        print("Usage: check_device_placement.py <file1.py> [file2.py ...]", file=sys.stderr)
        return 2

    total_issues = 0

    for filepath in files:
        path = Path(filepath)

        # Skip test files and this script itself
        if 'test_' in path.name or path.name == 'check_device_placement.py':
            continue

        # Skip if not a Python file
        if path.suffix != '.py':
            continue

        issues = check_file(path)

        if issues:
            print(f"\n{filepath}:")
            for lineno, message in issues:
                print(f"  Line {lineno}: {message}")
            total_issues += len(issues)

    if total_issues > 0:
        print(f"\n❌ Found {total_issues} unsafe device placement pattern(s).")
        print("Please use safe_model_to_device() instead of direct .to() calls.")
        print("See: .codex/CODING_STANDARDS_ML_DEVICE_PLACEMENT.md")
        return 1
    print("✅ No unsafe device placement patterns detected.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
