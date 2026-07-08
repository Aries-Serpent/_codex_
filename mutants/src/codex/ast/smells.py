"""Code Smell Detection Engine.

Detects common code quality issues and anti-patterns.
Design: FR-AST-007 (Code Smell Detector)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast  # noqa: E402
import re  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from enum import Enum  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402


class SmellSeverity(Enum):
    """Code smell severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SmellCategory(Enum):
    """Code smell categories."""

    COMPLEXITY = "complexity"
    NAMING = "naming"
    STRUCTURE = "structure"
    DUPLICATION = "duplication"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"


@dataclass
class CodeSmell:
    """Detected code smell."""

    rule_id: str
    message: str
    severity: SmellSeverity
    category: SmellCategory
    file_path: Path
    line_start: int
    line_end: int
    suggestion: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "file": str(self.file_path),
            "line_start": self.line_start,
            "line_end": self.line_end,
            "suggestion": self.suggestion,
            "metadata": self.metadata,
        }


@dataclass
class SmellRule:
    """Code smell detection rule."""

    rule_id: str
    name: str
    description: str
    severity: SmellSeverity
    category: SmellCategory
    detector: Callable[[ast.AST, Path], list[CodeSmell]]
    enabled: bool = True


class CodeSmellDetector:
    """Detects code smells in Python source code.

    Configurable rules engine supporting:
    - Built-in rules (complexity, naming, structure)
    - Custom rule registration
    - Severity filtering
    - Category filtering
    """

    # Thresholds
    MAX_FUNCTION_LENGTH = 50
    MAX_FUNCTION_ARGS = 5
    MAX_NESTED_DEPTH = 4
    MAX_CYCLOMATIC_COMPLEXITY = 10
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 40

    def __init__(self) -> None:
        """Initialize detector with default rules."""
        self.rules: dict[str, SmellRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register built-in detection rules."""
        # Complexity rules
        self.register_rule(
            SmellRule(
                rule_id="SMELL-C001",
                name="Long Function",
                description="Function exceeds maximum line count",
                severity=SmellSeverity.WARNING,
                category=SmellCategory.COMPLEXITY,
                detector=self._detect_long_functions,
            )
        )

        self.register_rule(
            SmellRule(
                rule_id="SMELL-C002",
                name="Too Many Arguments",
                description="Function has too many parameters",
                severity=SmellSeverity.WARNING,
                category=SmellCategory.COMPLEXITY,
                detector=self._detect_many_args,
            )
        )

        self.register_rule(
            SmellRule(
                rule_id="SMELL-C003",
                name="Deep Nesting",
                description="Code has excessive nesting depth",
                severity=SmellSeverity.WARNING,
                category=SmellCategory.COMPLEXITY,
                detector=self._detect_deep_nesting,
            )
        )

        # Naming rules
        self.register_rule(
            SmellRule(
                rule_id="SMELL-N001",
                name="Short Name",
                description="Identifier name is too short",
                severity=SmellSeverity.INFO,
                category=SmellCategory.NAMING,
                detector=self._detect_short_names,
            )
        )

        self.register_rule(
            SmellRule(
                rule_id="SMELL-N002",
                name="Non-PEP8 Name",
                description="Name doesn't follow PEP 8 conventions",
                severity=SmellSeverity.INFO,
                category=SmellCategory.NAMING,
                detector=self._detect_non_pep8_names,
            )
        )

        # Structure rules
        self.register_rule(
            SmellRule(
                rule_id="SMELL-S001",
                name="God Class",
                description="Class has too many methods",
                severity=SmellSeverity.ERROR,
                category=SmellCategory.STRUCTURE,
                detector=self._detect_god_class,
            )
        )

        self.register_rule(
            SmellRule(
                rule_id="SMELL-S002",
                name="Empty Except",
                description="Empty except clause catches all exceptions",
                severity=SmellSeverity.ERROR,
                category=SmellCategory.STRUCTURE,
                detector=self._detect_empty_except,
            )
        )

        # Maintainability rules
        self.register_rule(
            SmellRule(
                rule_id="SMELL-M001",
                name="Missing Docstring",
                description="Public function/class lacks docstring",
                severity=SmellSeverity.INFO,
                category=SmellCategory.MAINTAINABILITY,
                detector=self._detect_missing_docstrings,
            )
        )

        self.register_rule(
            SmellRule(
                rule_id="SMELL-M002",
                name="Magic Number",
                description="Unexplained numeric literal in code",
                severity=SmellSeverity.INFO,
                category=SmellCategory.MAINTAINABILITY,
                detector=self._detect_magic_numbers,
            )
        )

    def register_rule(self, rule: SmellRule) -> None:
        """Register a detection rule."""
        self.rules[rule.rule_id] = rule

    def disable_rule(self, rule_id: str) -> None:
        """Disable a rule by ID."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False

    def enable_rule(self, rule_id: str) -> None:
        """Enable a rule by ID."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True

    def detect_file(self, file_path: str | Path) -> list[CodeSmell]:
        """Detect code smells in a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            list of detected code smells
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return []

        try:
            code = file_path.read_text(encoding="utf-8", errors="ignore")
            return self.detect_string(code, file_path)
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            return []

    def detect_string(self, code: str, file_path: Optional[Path] = None) -> list[CodeSmell]:
        """Detect code smells in Python source code.

        Args:
            code: Python source code
            file_path: Optional file path for reporting

        Returns:
            list of detected code smells
        """
        file_path = file_path or Path("<string>")
        smells: list[CodeSmell] = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            type(e).__name__
            logger.debug("SyntaxError: <ERROR_TYPE>")
            return smells

        for rule in self.rules.values():
            if rule.enabled:
                detected = rule.detector(tree, file_path)
                smells.extend(detected)

        return sorted(smells, key=lambda s: (s.line_start, s.rule_id))

    def detect_directory(
        self,
        directory: str | Path,
        exclude_patterns: Optional[list[str]] = None,
    ) -> dict[str, list[CodeSmell]]:
        """Detect code smells in all Python files in directory.

        Args:
            directory: Directory path
            exclude_patterns: Glob patterns to exclude

        Returns:
            Dictionary mapping file paths to smell lists
        """
        directory = Path(directory)
        exclude_patterns = exclude_patterns or []
        results: dict[str, list[CodeSmell]] = {}

        for py_file in directory.rglob("*.py"):
            # Check exclusions
            excluded = any(py_file.match(pattern) for pattern in exclude_patterns)
            if excluded:
                continue

            smells = self.detect_file(py_file)
            if smells:
                results[str(py_file)] = smells

        return results

    # Detection implementations

    def _detect_long_functions(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect functions exceeding maximum length."""
        smells = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                line_start = node.lineno
                line_end = getattr(node, "end_lineno", line_start)
                length = line_end - line_start + 1

                if length > self.MAX_FUNCTION_LENGTH:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-C001",
                            message=f"Function '{node.name}' is {length} lines (max: {self.MAX_FUNCTION_LENGTH})",  # noqa: E501
                            severity=SmellSeverity.WARNING,
                            category=SmellCategory.COMPLEXITY,
                            file_path=file_path,
                            line_start=line_start,
                            line_end=line_end,
                            suggestion=f"Consider breaking down '{node.name}' into smaller functions",  # noqa: E501
                            metadata={"length": length, "function": node.name},
                        )
                    )
        return smells

    def _detect_many_args(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect functions with too many arguments."""
        smells = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count all argument types
                args = node.args
                arg_count = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
                # Subtract 'self' or 'cls' for methods
                if args.args and args.args[0].arg in ("self", "cls"):
                    arg_count -= 1

                if arg_count > self.MAX_FUNCTION_ARGS:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-C002",
                            message=f"Function '{node.name}' has {arg_count} arguments (max: {self.MAX_FUNCTION_ARGS})",  # noqa: E501
                            severity=SmellSeverity.WARNING,
                            category=SmellCategory.COMPLEXITY,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            suggestion="Consider using a configuration object or breaking into multiple functions",  # noqa: E501
                            metadata={"arg_count": arg_count, "function": node.name},
                        )
                    )
        return smells

    def _detect_deep_nesting(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect deeply nested code blocks."""
        smells = []

        def check_depth(node: ast.AST, depth: int = 0) -> None:
            # Increment depth for control structures
            nesting_nodes = (
                ast.If,
                ast.For,
                ast.While,
                ast.With,
                ast.Try,
                ast.ExceptHandler,
            )
            if isinstance(node, nesting_nodes):
                depth += 1
                if depth > self.MAX_NESTED_DEPTH:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-C003",
                            message=f"Code is nested {depth} levels deep (max: {self.MAX_NESTED_DEPTH})",  # noqa: E501
                            severity=SmellSeverity.WARNING,
                            category=SmellCategory.COMPLEXITY,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            suggestion="Consider early returns or extracting helper functions",
                            metadata={"depth": depth},
                        )
                    )

            for child in ast.iter_child_nodes(node):
                check_depth(child, depth)

        check_depth(tree)
        return smells

    def _detect_short_names(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect identifiers with very short names."""
        smells = []
        # Allowed short names
        allowed = {"i", "j", "k", "x", "y", "z", "n", "m", "f", "e", "_"}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.name) < self.MIN_NAME_LENGTH and node.name not in allowed:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-N001",
                            message=f"Function name '{node.name}' is too short",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.NAMING,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Use descriptive names that indicate the function's purpose",
                        )
                    )
            elif isinstance(node, ast.ClassDef):
                if len(node.name) < self.MIN_NAME_LENGTH:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-N001",
                            message=f"Class name '{node.name}' is too short",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.NAMING,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Use descriptive class names",
                        )
                    )
        return smells

    def _detect_non_pep8_names(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect names that don't follow PEP 8 conventions."""
        smells = []
        snake_case = re.compile(r"^[a-z_][a-z0-9_]*$")
        pascal_case = re.compile(r"^[A-Z][a-zA-Z0-9]*$")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Functions should be snake_case
                if not snake_case.match(node.name) and not node.name.startswith("_"):
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-N002",
                            message=f"Function '{node.name}' should use snake_case",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.NAMING,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Rename to use lowercase with underscores",
                        )
                    )
            elif isinstance(node, ast.ClassDef):
                # Classes should be PascalCase
                if not pascal_case.match(node.name):
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-N002",
                            message=f"Class '{node.name}' should use PascalCase",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.NAMING,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Rename using CapitalizedWords convention",
                        )
                    )
        return smells

    def _detect_god_class(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect classes with too many methods (God Class anti-pattern)."""
        smells = []
        max_methods = 20

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(
                    1
                    for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                )

                if method_count > max_methods:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-S001",
                            message=f"Class '{node.name}' has {method_count} methods (max: {max_methods})",  # noqa: E501
                            severity=SmellSeverity.ERROR,
                            category=SmellCategory.STRUCTURE,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            suggestion="Consider splitting into smaller, focused classes",
                            metadata={"method_count": method_count, "class": node.name},
                        )
                    )
        return smells

    def _detect_empty_except(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect empty except clauses (bare except or pass-only)."""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check for bare except
                if node.type is None:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-S002",
                            message="Bare 'except:' catches all exceptions including KeyboardInterrupt",  # noqa: E501
                            severity=SmellSeverity.ERROR,
                            category=SmellCategory.STRUCTURE,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            suggestion="Specify the exception type: except (IOError, OSError):",
                        )
                    )
                elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-S002",
                            message="Broad 'except (IOError, OSError):' may hide unexpected failures",  # noqa: E501
                            severity=SmellSeverity.WARNING,
                            category=SmellCategory.STRUCTURE,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            suggestion="Prefer specific exception types whenever possible",
                        )
                    )

                # Check for pass-only handler
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-S002",
                            message="Exception handler only contains 'pass' - exception is silently ignored",  # noqa: E501
                            severity=SmellSeverity.WARNING,
                            category=SmellCategory.STRUCTURE,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            suggestion="At minimum, log the exception",
                        )
                    )
        return smells

    def _detect_missing_docstrings(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect public functions and classes without docstrings."""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private/protected functions
                if node.name.startswith("_"):
                    continue

                if ast.get_docstring(node) is None:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-M001",
                            message=f"Public function '{node.name}' lacks a docstring",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.MAINTAINABILITY,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Add a docstring describing the function's purpose, parameters, and return value",  # noqa: E501
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue

                if ast.get_docstring(node) is None:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-M001",
                            message=f"Public class '{node.name}' lacks a docstring",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.MAINTAINABILITY,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Add a docstring describing the class's purpose and usage",
                        )
                    )
        return smells

    def _detect_magic_numbers(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """Detect unexplained numeric literals (magic numbers)."""
        smells = []
        # Common acceptable values
        allowed = {0, 1, 2, -1, 100, 1000, 0.5}

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in allowed and abs(node.value) > 2:
                    smells.append(
                        CodeSmell(
                            rule_id="SMELL-M002",
                            message=f"Magic number {node.value} should be a named constant",
                            severity=SmellSeverity.INFO,
                            category=SmellCategory.MAINTAINABILITY,
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            suggestion="Extract to a named constant with descriptive name",
                            metadata={"value": node.value},
                        )
                    )
        return smells


# Convenience function
def detect_smells(source: str | Path) -> list[CodeSmell]:
    """Detect code smells in Python source.

    Args:
        source: File path or source code string

    Returns:
        list of detected code smells
    """
    detector = CodeSmellDetector()

    if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        return detector.detect_file(source)
    return detector.detect_string(source)
