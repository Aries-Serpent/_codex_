"""Stub cleanup utilities for identifying and resolving NotImplementedError and TODO items.

This module helps track and resolve stubs, TODOs, and FIXMEs in the codebase.
Enhanced with AST-based abstract method detection to avoid false positives.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = ["StubAnalyzer", "StubInfo", "find_stubs", "prioritize_stubs"]


@dataclass
class StubInfo:
    """Information about a stub/TODO in the codebase.

    Attributes:
        file_path: Path to file containing stub
        line_number: Line number
        stub_type: Type of stub (NotImplementedError, TODO, FIXME)
        message: Message/description
        priority: Priority level (P0, P1, P2)
        context: Surrounding code context
    """

    file_path: Path
    line_number: int
    stub_type: str
    message: str
    priority: str = "P2"
    context: Optional[str] = None

    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self.priority} {self.file_path}:{self.line_number} [{self.stub_type}] {self.message}"
        )


class StubAnalyzer:
    """Analyzer for finding and categorizing stubs in code."""

    def __init__(self, source_dirs: Optional[list[Path]] = None):
        """Initialize stub analyzer.

        Args:
            source_dirs: list of source directories to analyze
        """
        if source_dirs is None:
            source_dirs = [Path("src"), Path("training")]

        self.source_dirs = [Path(d) for d in source_dirs]
        self.stubs: list[StubInfo] = []

    def analyze(self) -> list[StubInfo]:
        """Analyze source directories for stubs using AST-based detection.

        Returns:
            list of StubInfo objects
        """
        self.stubs = []

        for source_dir in self.source_dirs:
            if not source_dir.exists():
                continue

            # Find all Python files
            for py_file in source_dir.rglob("*.py"):
                self._analyze_file(py_file)

        return self.stubs

    def _is_abstract_method(self, file_path: Path, line_number: int) -> bool:
        """
        Check if a NotImplementedError at given line is part of an abstract method.

        Uses AST to detect:
        - Methods decorated with @abstractmethod
        - Classes inheriting from ABC
        - Methods with NotImplementedError in abstract classes

        Args:
            file_path: Path to Python file
            line_number: Line number of NotImplementedError

        Returns:
            True if this is an intentional abstract method pattern
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            # Build a mapping from function nodes to their parent class nodes (O(n) complexity)
            func_to_class = {}
            for class_node in ast.walk(tree):
                if isinstance(class_node, ast.ClassDef):
                    for node in class_node.body:
                        if isinstance(node, ast.FunctionDef):
                            func_to_class[node] = class_node

            # Find the function node at the given line
            for func_node in func_to_class:
                if hasattr(func_node, "lineno") and hasattr(func_node, "end_lineno"):
                    if (
                        func_node.lineno
                        <= line_number
                        <= (func_node.end_lineno or func_node.lineno)
                    ):
                        # Check for @abstractmethod decorator
                        for decorator in func_node.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                                return True
                            if (
                                isinstance(decorator, ast.Attribute)
                                and decorator.attr == "abstractmethod"
                            ):
                                return True

                        # Check if method is in an ABC class or Protocol
                        parent_class = func_to_class.get(func_node)
                        if parent_class:
                            for base in parent_class.bases:
                                if isinstance(base, ast.Name) and base.id in ("ABC", "Protocol"):
                                    return True
                                if isinstance(base, ast.Attribute) and base.attr in (
                                    "ABC",
                                    "Protocol",
                                ):
                                    return True

            # Also check for top-level functions (not in classes)
            for node in ast.walk(tree):  # type: ignore[assignment]
                if isinstance(node, ast.FunctionDef) and node not in func_to_class:
                    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                        if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                            # Check for @abstractmethod decorator on standalone functions
                            for decorator in node.decorator_list:
                                if (
                                    isinstance(decorator, ast.Name)
                                    and decorator.id == "abstractmethod"
                                ):
                                    return True
                                if (
                                    isinstance(decorator, ast.Attribute)
                                    and decorator.attr == "abstractmethod"
                                ):
                                    return True

        except (IOError, OSError, SyntaxError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug(f"Failed to parse {file_path} for abstract method detection: <ERROR_TYPE>")

        return False

    def _analyze_file(self, file_path: Path):
        """Analyze a single file for stubs.

        Args:
            file_path: Path to Python file
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Enhanced analysis with AST-based abstract method detection
            for i, line in enumerate(lines, start=1):
                line_lower = line.lower()

                # Check for NotImplementedError with AST validation
                if "notimplementederror" in line_lower:
                    # Only flag if it's an actual raise statement
                    stripped = line.strip()
                    if stripped.startswith("raise ") and "NotImplementedError" in line:
                        # Use AST to check if this is an abstract method
                        is_abstract = self._is_abstract_method(file_path, i)

                        if is_abstract:
                            # Skip abstract methods - they're intentional design patterns
                            logger.debug(f"Skipping abstract method at {file_path}:{i}")
                            continue

                        priority = "P0"  # Actual raise statements are P0

                        # Try to extract message
                        if "(" in line and ")" in line:
                            message_part = line.split("(", 1)[1].rsplit(")", 1)[0]
                            message = message_part.strip("\"'")
                        else:
                            message = "NotImplementedError"

                        self.stubs.append(
                            StubInfo(
                                file_path=file_path,
                                line_number=i,
                                stub_type="NotImplementedError",
                                message=message,
                                priority=priority,
                                context=line.strip(),
                            )
                        )

                # Check for TODO
                if "todo" in line_lower and "#" in line:
                    priority = self._determine_priority(line)
                    message = line.split("#", 1)[1].strip()

                    self.stubs.append(
                        StubInfo(
                            file_path=file_path,
                            line_number=i,
                            stub_type="TODO",
                            message=message,
                            priority=priority,
                            context=line.strip(),
                        )
                    )

                # Check for FIXME
                if "fixme" in line_lower and "#" in line:
                    priority = self._determine_priority(line)
                    message = line.split("#", 1)[1].strip()

                    self.stubs.append(
                        StubInfo(
                            file_path=file_path,
                            line_number=i,
                            stub_type="FIXME",
                            message=message,
                            priority=priority,
                            context=line.strip(),
                        )
                    )

        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning(f"Failed to analyze {file_path}: <ERROR_TYPE>")

    def _determine_priority(self, line: str) -> str:
        """Determine priority from line content.

        Args:
            line: Source code line

        Returns:
            Priority level (P0, P1, P2)
        """
        line_upper = line.upper()

        if "P0" in line_upper or "CRITICAL" in line_upper or "BLOCKING" in line_upper:
            return "P0"
        if "P1" in line_upper or "HIGH" in line_upper or "IMPORTANT" in line_upper:
            return "P1"
        return "P2"

    def get_by_priority(self, priority: str) -> list[StubInfo]:
        """Get stubs by priority level.

        Args:
            priority: Priority level (P0, P1, P2)

        Returns:
            list of stubs with specified priority
        """
        return [stub for stub in self.stubs if stub.priority == priority]

    def get_by_type(self, stub_type: str) -> list[StubInfo]:
        """Get stubs by type.

        Args:
            stub_type: Type of stub (NotImplementedError, TODO, FIXME)

        Returns:
            list of stubs with specified type
        """
        return [stub for stub in self.stubs if stub.stub_type == stub_type]

    def get_summary(self) -> dict:
        """Get summary of stub analysis.

        Returns:
            Summary dict with counts by priority and type
        """
        return {
            "total": len(self.stubs),
            "by_priority": {
                "P0": len(self.get_by_priority("P0")),
                "P1": len(self.get_by_priority("P1")),
                "P2": len(self.get_by_priority("P2")),
            },
            "by_type": {
                "NotImplementedError": len(self.get_by_type("NotImplementedError")),
                "TODO": len(self.get_by_type("TODO")),
                "FIXME": len(self.get_by_type("FIXME")),
            },
        }


def find_stubs(source_dirs: Optional[list[Path]] = None) -> list[StubInfo]:
    """Find all stubs in source directories (convenience function).

    Args:
        source_dirs: list of source directories to analyze

    Returns:
        list of StubInfo objects
    """
    analyzer = StubAnalyzer(source_dirs=source_dirs)
    return analyzer.analyze()


def prioritize_stubs(stubs: list[StubInfo]) -> list[StubInfo]:
    """Sort stubs by priority (P0 first, then P1, then P2).

    Args:
        stubs: list of StubInfo objects

    Returns:
        Sorted list with P0 first
    """
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    return sorted(
        stubs,
        key=lambda s: (
            priority_order.get(s.priority, 3),
            str(s.file_path),
            s.line_number,
        ),
    )


def generate_stub_report(output_path: Path | str, source_dirs: Optional[list[Path]] = None):
    """Generate stub analysis report.

    Args:
        output_path: Path where report will be saved
        source_dirs: list of source directories to analyze
    """
    analyzer = StubAnalyzer(source_dirs=source_dirs)
    stubs = analyzer.analyze()
    sorted_stubs = prioritize_stubs(stubs)

    summary = analyzer.get_summary()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Stub Analysis Report\n\n")
        f.write(f"**Total Stubs**: {summary['total']}\n\n")

        f.write("## Summary by Priority\n\n")
        for priority in ["P0", "P1", "P2"]:
            count = summary["by_priority"][priority]
            f.write(f"- **{priority}**: {count}\n")

        f.write("\n## Summary by Type\n\n")
        for stub_type, count in summary["by_type"].items():
            f.write(f"- **{stub_type}**: {count}\n")

        f.write("\n## Detailed list\n\n")

        for priority in ["P0", "P1", "P2"]:
            priority_stubs = [s for s in sorted_stubs if s.priority == priority]
            if not priority_stubs:
                continue

            f.write(f"\n### {priority} Priority ({len(priority_stubs)} items)\n\n")

            for stub in priority_stubs:
                f.write(f"**{stub.file_path}:{stub.line_number}** [{stub.stub_type}]\n")
                f.write(f"- Message: {stub.message}\n")
                if stub.context:
                    f.write(f"- Context: `{stub.context}`\n")
                f.write("\n")

    logger.info(f"Stub report generated: {output_path}")
    logger.info("\n✓ Stub analysis complete:")
    logger.info(f"  Total stubs: {summary['total']}")
    logger.info(f"  P0: {summary['by_priority']['P0']}")
    logger.info(f"  P1: {summary['by_priority']['P1']}")
    logger.info(f"  P2: {summary['by_priority']['P2']}")
    logger.info(f"  Report: {output_path}")
