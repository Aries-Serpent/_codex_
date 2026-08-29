"""
AST Pattern Library and Consistency Tests

Provides reusable AST patterns for code analysis and ensures
consistent AST usage across the codebase.
"""

import ast
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ASTPattern:
    """A reusable AST pattern for code analysis."""

    name: str
    description: str
    node_type: type
    matcher: Callable[[ast.AST], bool]

    def matches(self, node: ast.AST) -> bool:
        """Check if node matches this pattern."""
        if not isinstance(node, self.node_type):
            return False
        return self.matcher(node)


class ASTPatternLibrary:
    """Library of common AST patterns for code analysis."""

    def __init__(self):
        self.patterns: dict[str, ASTPattern] = {}
        self._register_default_patterns()

    def _register_default_patterns(self) -> None:
        """Register default patterns."""
        # Abstract method pattern
        self.register(
            ASTPattern(
                name="abstract_method",
                description="Methods decorated with @abstractmethod",
                node_type=ast.FunctionDef,
                matcher=lambda n: (
                    any(
                        isinstance(d, ast.Name) and d.id == "abstractmethod"
                        for d in n.decorator_list
                    )
                    if hasattr(n, "decorator_list")
                    else False
                ),
            )
        )

        # Stub implementation pattern (raise NotImplementedError)
        self.register(
            ASTPattern(
                name="stub_implementation",
                description="Functions that only raise NotImplementedError",
                node_type=ast.FunctionDef,
                matcher=self._is_stub_implementation,
            )
        )

        # Async function pattern
        self.register(
            ASTPattern(
                name="async_function",
                description="Async function definitions",
                node_type=ast.AsyncFunctionDef,
                matcher=lambda n: True,
            )
        )

        # Class with __init__ pattern
        self.register(
            ASTPattern(
                name="class_with_init",
                description="Classes that define __init__",
                node_type=ast.ClassDef,
                matcher=lambda n: any(
                    isinstance(item, ast.FunctionDef) and item.name == "__init__" for item in n.body
                ),
            )
        )

        # Dataclass pattern
        self.register(
            ASTPattern(
                name="dataclass",
                description="Classes decorated with @dataclass",
                node_type=ast.ClassDef,
                matcher=lambda n: (
                    any(
                        (isinstance(d, ast.Name) and d.id == "dataclass")
                        or (
                            isinstance(d, ast.Call)
                            and isinstance(d.func, ast.Name)
                            and d.func.id == "dataclass"
                        )
                        for d in n.decorator_list
                    )
                    if hasattr(n, "decorator_list")
                    else False
                ),
            )
        )

        # Import from pattern
        self.register(
            ASTPattern(
                name="import_from",
                description="From X import Y statements",
                node_type=ast.ImportFrom,
                matcher=lambda n: True,
            )
        )

        # TODO comment pattern (in docstrings)
        self.register(
            ASTPattern(
                name="todo_in_docstring",
                description="Functions with TODO in docstring",
                node_type=ast.FunctionDef,
                matcher=lambda n: (
                    ast.get_docstring(n) is not None and "TODO" in ast.get_docstring(n).upper()
                ),
            )
        )

    def _is_stub_implementation(self, node: ast.FunctionDef) -> bool:
        """Check if function is a stub (only raises NotImplementedError)."""
        # Filter out docstrings and pass statements
        meaningful_stmts = [
            stmt
            for stmt in node.body
            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
            and not isinstance(stmt, ast.Pass)
        ]

        if len(meaningful_stmts) == 1:
            stmt = meaningful_stmts[0]
            if isinstance(stmt, ast.Raise):
                exc = stmt.exc
                if isinstance(exc, ast.Call):
                    if isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                        return True
                elif isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                    return True
        return False

    def register(self, pattern: ASTPattern) -> None:
        """Register a pattern."""
        self.patterns[pattern.name] = pattern

    def get(self, name: str) -> Optional[ASTPattern]:
        """Get a pattern by name."""
        return self.patterns.get(name)

    def find_matches(self, tree: ast.AST, pattern_name: str) -> list[ast.AST]:
        """Find all nodes matching a pattern."""
        pattern = self.get(pattern_name)
        if not pattern:
            return []

        matches = []
        for node in ast.walk(tree):
            if pattern.matches(node):
                matches.append(node)
        return matches

    def analyze_file(self, file_path: Path) -> dict[str, list[dict[str, Any]]]:
        """Analyze a file for all patterns."""
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return {}

        results = {}
        for name, pattern in self.patterns.items():
            matches = self.find_matches(tree, name)
            if matches:
                results[name] = [
                    {
                        "name": getattr(node, "name", "unknown"),
                        "line": node.lineno if hasattr(node, "lineno") else 0,
                    }
                    for node in matches
                ]
        return results


# Tests


def test_pattern_library_init():
    """Test pattern library initialization."""
    lib = ASTPatternLibrary()
    assert len(lib.patterns) > 0, "Collection must not be empty"
    assert "abstract_method" in lib.patterns, "Condition must be true"
    assert "stub_implementation" in lib.patterns, "Condition must be true"


def test_abstract_method_detection():
    """Test detection of abstract methods."""
    source = """
from abc import abstractmethod

class Base:
    @abstractmethod
    def process(self):
        pass
"""
    lib = ASTPatternLibrary()
    tree = ast.parse(source)
    matches = lib.find_matches(tree, "abstract_method")
    assert len(matches) == 1, "Matches must not be empty"
    assert matches[0].name == "process", "name is not valid"


def test_stub_detection():
    """Test detection of stub implementations."""
    source = """
def not_implemented():
    raise NotImplementedError("TODO")

def real_impl():
    return 42
"""
    lib = ASTPatternLibrary()
    tree = ast.parse(source)
    matches = lib.find_matches(tree, "stub_implementation")
    assert len(matches) == 1, "Matches must not be empty"
    assert matches[0].name == "not_implemented", "name is not valid"


def test_dataclass_detection():
    """Test detection of dataclasses."""
    source = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

class Regular:
    pass
"""
    lib = ASTPatternLibrary()
    tree = ast.parse(source)
    matches = lib.find_matches(tree, "dataclass")
    assert len(matches) == 1, "Matches must not be empty"
    assert matches[0].name == "Point", "name is not valid"


def test_class_with_init_detection():
    """Test detection of classes with __init__."""
    source = """
class WithInit:
    def __init__(self):
        pass

class WithoutInit:
    def other(self):
        pass
"""
    lib = ASTPatternLibrary()
    tree = ast.parse(source)
    matches = lib.find_matches(tree, "class_with_init")
    assert len(matches) == 1, "Matches must not be empty"
    assert matches[0].name == "WithInit", "name is not valid"


def test_async_function_detection():
    """Test detection of async functions."""
    source = """
async def async_func():
    await something()

def sync_func():
    pass
"""
    lib = ASTPatternLibrary()
    tree = ast.parse(source)
    matches = lib.find_matches(tree, "async_function")
    assert len(matches) == 1, "Matches must not be empty"


def test_analyze_file(tmp_path):
    """Test file analysis."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
from dataclasses import dataclass

@dataclass
class Config:
    name: str
    value: int

def process():
    raise NotImplementedError()
""")

    lib = ASTPatternLibrary()
    results = lib.analyze_file(test_file)

    assert "dataclass" in results, "Result must not be empty"
    assert "stub_implementation" in results, "Result must not be empty"
    assert len(results["dataclass"]) == 1, "Collection must not be empty"
    assert results["dataclass"][0]["name"] == "Config", "Result must not be empty"
