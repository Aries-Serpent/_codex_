#!/usr/bin/env python3
"""
Stub Cleanup and Analysis Tool

This module provides AST-based stub detection and cleanup capabilities:
1. AST-based stub detection (not regex)
2. Self-reference exclusion (filters out valid abstract methods)
3. Configurable detection patterns
4. Automated cleanup suggestions

Per gap analysis Phase A.3 requirements.
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class StubInfo:
    """Information about a detected stub."""

    file_path: str
    line_number: int
    function_name: str
    stub_type: str  # 'pass', 'ellipsis', 'not_implemented', 'todo'
    is_abstract: bool = False
    is_protocol: bool = False
    parent_class: Optional[str] = None
    docstring: Optional[str] = None
    confidence: float = 1.0  # Confidence this is actually a stub needing fix

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "function_name": self.function_name,
            "stub_type": self.stub_type,
            "is_abstract": self.is_abstract,
            "is_protocol": self.is_protocol,
            "parent_class": self.parent_class,
            "docstring": self.docstring,
            "confidence": self.confidence,
        }


@dataclass
class StubAnalysisResult:
    """Result of stub analysis for a file or directory."""

    total_functions: int = 0
    total_stubs: int = 0
    stubs: List[StubInfo] = field(default_factory=list)
    excluded_stubs: List[StubInfo] = field(default_factory=list)  # Valid abstracts
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_functions": self.total_functions,
            "total_stubs": self.total_stubs,
            "stubs": [s.to_dict() for s in self.stubs],
            "excluded_stubs": [s.to_dict() for s in self.excluded_stubs],
            "errors": self.errors,
        }


class StubDetector(ast.NodeVisitor):
    """AST-based stub detector.

    Detects stub implementations including:
    - Functions with only `pass`
    - Functions with only `...` (ellipsis)
    - Functions that only raise NotImplementedError
    - Functions with TODO/FIXME in docstring or body

    Excludes:
    - Abstract methods (decorated with @abstractmethod)
    - Protocol methods (in Protocol classes)
    - Property getters/setters with minimal body
    """

    # Class names that indicate protocol/interface patterns
    PROTOCOL_BASES = {"Protocol", "ABC", "Interface", "Abstract"}

    def __init__(self, file_path: str, exclude_abstract: bool = True):
        self.file_path = file_path
        self.exclude_abstract = exclude_abstract
        self.stubs: List[StubInfo] = []
        self.excluded: List[StubInfo] = []
        self.total_functions = 0
        self.current_class: Optional[str] = None
        self.current_class_is_abstract = False
        self._class_bases: Set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class context for method analysis."""
        old_class = self.current_class
        old_is_abstract = self.current_class_is_abstract
        old_bases = self._class_bases

        self.current_class = node.name

        # Check if class inherits from abstract/protocol bases
        self._class_bases = set()
        for base in node.bases:
            if isinstance(base, ast.Name):
                self._class_bases.add(base.id)
            elif isinstance(base, ast.Attribute):
                self._class_bases.add(base.attr)

        self.current_class_is_abstract = bool(self._class_bases & self.PROTOCOL_BASES)

        # Visit class body
        self.generic_visit(node)

        # Restore context
        self.current_class = old_class
        self.current_class_is_abstract = old_is_abstract
        self._class_bases = old_bases

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function/method for stub patterns."""
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze async function for stub patterns."""
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Analyze a function node for stub patterns."""
        self.total_functions += 1

        # Check decorators
        is_abstract = self._has_abstract_decorator(node)
        is_property = self._has_property_decorator(node)

        # Get docstring
        docstring = ast.get_docstring(node)

        # Analyze body
        stub_type = self._detect_stub_type(node)

        if stub_type is None:
            return  # Not a stub

        # Check for TODO in docstring
        has_todo = False
        if docstring and any(marker in docstring.upper() for marker in ["TODO", "FIXME", "XXX"]):
            has_todo = True
            if stub_type == "pass":
                stub_type = "todo"

        # Create stub info
        stub = StubInfo(
            file_path=self.file_path,
            line_number=node.lineno,
            function_name=node.name,
            stub_type=stub_type,
            is_abstract=is_abstract,
            is_protocol=self.current_class_is_abstract,
            parent_class=self.current_class,
            docstring=docstring[:100] if docstring else None,
        )

        # Determine if this should be excluded
        should_exclude = False

        if self.exclude_abstract:
            # Exclude abstract methods
            if is_abstract:
                should_exclude = True
                stub.confidence = 0.1

            # Exclude protocol methods
            if self.current_class_is_abstract and stub_type in ("pass", "ellipsis"):
                should_exclude = True
                stub.confidence = 0.2

            # Exclude property stubs with docstrings (common pattern)
            if is_property and docstring and stub_type in ("pass", "ellipsis"):
                should_exclude = True
                stub.confidence = 0.3

        # Adjust confidence based on context
        if stub.parent_class and "Base" in stub.parent_class:
            stub.confidence *= 0.5
        if stub.parent_class and "Abstract" in stub.parent_class:
            stub.confidence *= 0.3
        if has_todo:
            stub.confidence = max(stub.confidence, 0.8)  # TODOs are likely real stubs

        if should_exclude:
            self.excluded.append(stub)
        else:
            self.stubs.append(stub)

    def _has_abstract_decorator(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function has @abstractmethod decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in (
                "abstractmethod",
                "abstractproperty",
            ):
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr in (
                "abstractmethod",
                "abstractproperty",
            ):
                return True
        return False

    def _has_property_decorator(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function has @property decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr in (
                "property",
                "setter",
                "getter",
                "deleter",
            ):
                return True
        return False

    def _detect_stub_type(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Optional[str]:
        """Detect the type of stub implementation.

        Returns:
            Stub type string or None if not a stub
        """
        body = node.body

        # Skip docstring if present
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str):
                body = body[1:]

        if not body:
            return "empty"

        # Single statement body
        if len(body) == 1:
            stmt = body[0]

            # pass statement
            if isinstance(stmt, ast.Pass):
                return "pass"

            # Ellipsis (...)
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value is ...:
                    return "ellipsis"

            # raise NotImplementedError
            if isinstance(stmt, ast.Raise):
                if isinstance(stmt.exc, ast.Call):
                    if isinstance(stmt.exc.func, ast.Name):
                        if stmt.exc.func.id == "NotImplementedError":
                            return "not_implemented"
                elif isinstance(stmt.exc, ast.Name):
                    if stmt.exc.id == "NotImplementedError":
                        return "not_implemented"

        return None


def analyze_file(file_path: Path, exclude_abstract: bool = True) -> StubAnalysisResult:
    """Analyze a single Python file for stubs.

    Args:
        file_path: Path to Python file
        exclude_abstract: Whether to exclude abstract methods

    Returns:
        StubAnalysisResult with detected stubs
    """
    result = StubAnalysisResult()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))

        detector = StubDetector(str(file_path), exclude_abstract=exclude_abstract)
        detector.visit(tree)

        result.total_functions = detector.total_functions
        result.stubs = detector.stubs
        result.excluded_stubs = detector.excluded
        result.total_stubs = len(detector.stubs)

    except SyntaxError as e:
        logger.debug(f"SyntaxError: {e}")
        result.errors.append(f"Syntax error in {file_path}: {e}")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        result.errors.append(f"Error analyzing {file_path}: {e}")

    return result


def analyze_directory(
    directory: Path,
    exclude_abstract: bool = True,
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
) -> StubAnalysisResult:
    """Analyze all Python files in a directory.

    Args:
        directory: Directory to analyze
        exclude_abstract: Whether to exclude abstract methods
        include_patterns: Glob patterns to include (default: **/*.py)
        exclude_patterns: Glob patterns to exclude

    Returns:
        Combined StubAnalysisResult
    """
    if include_patterns is None:
        include_patterns = ["**/*.py"]

    if exclude_patterns is None:
        exclude_patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/conftest.py",
            "**/setup.py",
            "**/__pycache__/**",
            "**/venv/**",
            "**/.venv/**",
            "**/node_modules/**",
        ]

    combined = StubAnalysisResult()

    # Find all Python files
    python_files = set()
    for pattern in include_patterns:
        python_files.update(directory.glob(pattern))

    # Apply exclusions
    for pattern in exclude_patterns:
        excluded = set(directory.glob(pattern))
        python_files -= excluded

    # Analyze each file
    for file_path in sorted(python_files):
        if not file_path.is_file():
            continue

        result = analyze_file(file_path, exclude_abstract=exclude_abstract)

        combined.total_functions += result.total_functions
        combined.total_stubs += result.total_stubs
        combined.stubs.extend(result.stubs)
        combined.excluded_stubs.extend(result.excluded_stubs)
        combined.errors.extend(result.errors)

    return combined


def generate_report(result: StubAnalysisResult, format: str = "text") -> str:
    """Generate a report from analysis results.

    Args:
        result: Analysis results
        format: Output format ('text', 'json', 'markdown')

    Returns:
        Formatted report string
    """
    if format == "json":
        return json.dumps(result.to_dict(), indent=2)

    if format == "markdown":
        lines = [
            "# Stub Analysis Report",
            "",
            "## Summary",
            f"- Total functions analyzed: {result.total_functions}",
            f"- Stubs detected: {result.total_stubs}",
            f"- Excluded (valid abstract): {len(result.excluded_stubs)}",
            f"- Errors: {len(result.errors)}",
            "",
        ]

        if result.stubs:
            lines.append("## Detected Stubs")
            lines.append("")
            lines.append("| File | Line | Function | Type | Class | Confidence |")
            lines.append("|------|------|----------|------|-------|------------|")

            for stub in sorted(result.stubs, key=lambda s: (-s.confidence, s.file_path)):
                lines.append(
                    f"| `{stub.file_path}` | {stub.line_number} | "
                    f"`{stub.function_name}` | {stub.stub_type} | "
                    f"{stub.parent_class or '-'} | {stub.confidence:.2f} |"
                )
            lines.append("")

        if result.errors:
            lines.append("## Errors")
            lines.append("")
            for error in result.errors:
                lines.append(f"- {error}")
            lines.append("")

        return "\n".join(lines)

    # Default: text format
    lines = [
        "=" * 60,
        "Stub Analysis Report",
        "=" * 60,
        f"Total functions: {result.total_functions}",
        f"Stubs detected:  {result.total_stubs}",
        f"Excluded:        {len(result.excluded_stubs)}",
        f"Errors:          {len(result.errors)}",
        "=" * 60,
    ]

    if result.stubs:
        lines.append("\nDetected Stubs (sorted by confidence):")
        lines.append("-" * 60)

        for stub in sorted(result.stubs, key=lambda s: (-s.confidence, s.file_path)):
            class_info = f" ({stub.parent_class})" if stub.parent_class else ""
            lines.append(
                f"  [{stub.confidence:.2f}] {stub.file_path}:{stub.line_number} "
                f"- {stub.function_name}{class_info} [{stub.stub_type}]"
            )

    if result.errors:
        lines.append("\nErrors:")
        lines.append("-" * 60)
        for error in result.errors:
            lines.append(f"  {error}")

    return "\n".join(lines)


def main():
    """Main entry point for stub cleanup tool."""
    parser = argparse.ArgumentParser(description="AST-based stub detection and cleanup tool")
    parser.add_argument(
        "path", type=Path, nargs="?", default=Path("."), help="File or directory to analyze"
    )
    parser.add_argument(
        "--format", "-f", choices=["text", "json", "markdown"], default="text", help="Output format"
    )
    parser.add_argument(
        "--include-abstract", action="store_true", help="Include abstract methods in results"
    )
    parser.add_argument(
        "--min-confidence", type=float, default=0.5, help="Minimum confidence threshold"
    )
    parser.add_argument("--output", "-o", type=Path, help="Output file (default: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Analyze
    if args.path.is_file():
        result = analyze_file(args.path, exclude_abstract=not args.include_abstract)
    else:
        result = analyze_directory(args.path, exclude_abstract=not args.include_abstract)

    # Filter by confidence
    result.stubs = [s for s in result.stubs if s.confidence >= args.min_confidence]
    result.total_stubs = len(result.stubs)

    # Generate report
    report = generate_report(result, format=args.format)

    # Output
    if args.output:
        args.output.write_text(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Exit with error if stubs found
    sys.exit(1 if result.total_stubs > 0 else 0)


if __name__ == "__main__":
    main()
