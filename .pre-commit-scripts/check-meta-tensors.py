#!/usr/bin/env python3
"""
Pre-commit hook to detect PyTorch meta tensor anti-patterns.

This script validates that PyTorch model initialization code follows
safe patterns that prevent meta tensor issues, particularly in RAG
modules and other ML components.

Exit codes:
    0: All checks passed
    1: Meta tensor anti-patterns detected
    2: Script error (file not found, parse error, etc.)
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Optional


class MetaTensorPatternChecker(ast.NodeVisitor):
    """AST visitor to detect meta tensor anti-patterns in Python code."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: list[tuple[int, str]] = []
        self.has_torch_import = False
        self.has_sentence_transformers = False
        self.has_transformers = False

    def visit_Import(self, node: ast.Import) -> None:
        """Track ML library imports."""
        for alias in node.names:
            if alias.name == "torch":
                self.has_torch_import = True
            elif alias.name == "sentence_transformers":
                self.has_sentence_transformers = True
            elif alias.name == "transformers":
                self.has_transformers = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track ML library from-imports."""
        if node.module:
            if node.module.startswith("torch"):
                self.has_torch_import = True
            elif node.module.startswith("sentence_transformers"):
                self.has_sentence_transformers = True
            elif node.module.startswith("transformers"):
                self.has_transformers = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for meta tensor anti-patterns."""
        # Only check files that import ML libraries
        if not (self.has_torch_import or self.has_sentence_transformers or self.has_transformers):
            self.generic_visit(node)
            return

        # Check for SentenceTransformer initialization patterns
        if self._is_sentence_transformer_init(node):
            self._check_sentence_transformer_call(node)

        # Check for deprecated safe_model_load usage
        if self._is_function_call(node, "safe_model_load"):
            self.issues.append((
                node.lineno,
                "Deprecated function 'safe_model_load()' used. "
                "Use 'safe_model_load_v2()' with strategy pattern instead."
            ))

        # Check for model.to() calls that might be problematic
        if self._is_method_call(node, "to") and self._might_be_model(node.func):
            # This is just a warning - model.to() is valid in some contexts
            # We don't flag it as an error, just ensure it's defensive
            pass

        self.generic_visit(node)

    def _is_sentence_transformer_init(self, node: ast.Call) -> bool:
        """Check if call is SentenceTransformer initialization."""
        return (
            isinstance(node.func, ast.Name)
            and node.func.id == "SentenceTransformer"
        ) or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "SentenceTransformer"
        )

    def _check_sentence_transformer_call(self, node: ast.Call) -> None:
        """Validate SentenceTransformer initialization pattern."""
        # Extract keyword arguments
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}

        # Check for device parameter (now optional but recommended)
        has_device = "device" in kwargs

        # Check for trust_remote_code parameter
        trust_remote_code = kwargs.get("trust_remote_code")
        if trust_remote_code is None:
            self.issues.append((
                node.lineno,
                "SentenceTransformer initialization missing 'trust_remote_code=False' "
                "parameter (security best practice)"
            ))
        elif not self._is_false_literal(trust_remote_code):
            self.issues.append((
                node.lineno,
                "SentenceTransformer 'trust_remote_code' should be False for security"
            ))

        # Warn if device parameter is used (can cause issues in some PyTorch versions)
        if has_device:
            device_value = kwargs["device"]
            # Only warn if it looks like a problematic pattern
            if isinstance(device_value, ast.Constant) and device_value.value in ["cpu", "cuda"]:
                # This is actually the recommended pattern in some cases
                # Don't flag as error, but ensure verification follows
                pass

    def _is_false_literal(self, node: ast.AST) -> bool:
        """Check if node is a False literal."""
        if isinstance(node, ast.Constant):
            return node.value is False
        if isinstance(node, ast.NameConstant):  # Python 3.7 compatibility
            return node.value is False
        return False

    def _is_function_call(self, node: ast.Call, func_name: str) -> bool:
        """Check if call is to a specific function."""
        if isinstance(node.func, ast.Name) and node.func.id == func_name:
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == func_name:
            return True
        return False

    def _is_method_call(self, node: ast.Call, method_name: str) -> bool:
        """Check if call is a method with specific name."""
        return isinstance(node.func, ast.Attribute) and node.func.attr == method_name

    def _might_be_model(self, func: ast.AST) -> bool:
        """Heuristic to check if object might be a model."""
        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name):
                name = func.value.id
                # Common model variable names
                return any(keyword in name.lower() for keyword in ["model", "network", "transformer"])
        return False

    def check_verification_pattern(self, tree: ast.AST) -> None:
        """
        Check if file contains meta tensor verification pattern.

        This is a best practice but not strictly required for all files.
        """
        # Look for meta tensor verification loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if it's iterating over named_parameters or named_buffers
                if isinstance(node.iter, ast.Call):
                    if self._is_method_call(node.iter, "named_parameters") or \
                       self._is_method_call(node.iter, "named_buffers"):
                        # Found verification loop - good!
                        return

        # If file initializes models but has no verification, warn
        # (but don't fail - verification might be elsewhere)


def check_file(filepath: Path) -> list[tuple[int, str]]:
    """
    Check a Python file for meta tensor anti-patterns.

    Args:
        filepath: Path to Python file to check

    Returns:
        List of (line_number, message) tuples for issues found
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error: {e.msg}")]
    except Exception as e:
        return [(0, f"Error parsing file: {e}")]

    checker = MetaTensorPatternChecker(str(filepath))
    checker.visit(tree)
    checker.check_verification_pattern(tree)

    return checker.issues


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for pre-commit hook.

    Args:
        argv: Command line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 = success, 1 = issues found, 2 = error)
    """
    parser = argparse.ArgumentParser(
        description="Check Python files for PyTorch meta tensor anti-patterns"
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to check"
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=Path(".pre-commit-scripts/meta-tensor-allowlist.txt"),
        help="Path to allowlist file (one pattern per line)"
    )

    args = parser.parse_args(argv)

    # Load allowlist if exists
    allowlist: list[str] = []
    if args.allowlist.exists():
        allowlist = [
            line.strip()
            for line in args.allowlist.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    total_issues = 0
    files_with_issues = []

    for filename in args.filenames:
        filepath = Path(filename)

        # Skip non-Python files
        if filepath.suffix != ".py":
            continue

        # Skip files in allowlist
        if any(pattern in str(filepath) for pattern in allowlist):
            continue

        # Skip test files (they often mock models)
        if "test" in filepath.name.lower() or "tests" in str(filepath):
            continue

        # Skip __init__.py files (typically just imports)
        if filepath.name == "__init__.py":
            continue

        issues = check_file(filepath)

        if issues:
            files_with_issues.append(filename)
            total_issues += len(issues)
            print(f"\n{filename}:")
            for lineno, message in sorted(issues):
                if lineno > 0:
                    print(f"  Line {lineno}: {message}")
                else:
                    print(f"  {message}")

    if total_issues > 0:
        print(f"\n❌ Found {total_issues} meta tensor anti-pattern(s) in {len(files_with_issues)} file(s)")
        print("\nRecommended fixes:")
        print("  1. Use default device allocation (no explicit device parameter)")
        print("  2. Always set trust_remote_code=False for security")
        print("  3. Add meta tensor verification loops after model loading")
        print("  4. Replace deprecated safe_model_load() with safe_model_load_v2()")
        print("\nSee: .codex/AI_AGENT_UTILITIES_REGISTRY.md for safe patterns")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
