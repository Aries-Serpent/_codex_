"""Universal Python Parser using libcst.

Parses Python source code into StandardizedASTNode representation.
Provides fallback to stdlib ast module for graceful degradation.

Design: FR-AST-001 (Universal Parser)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast  # noqa: E402
import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

from .node import NodeType, SourceLocation, StandardizedASTNode  # noqa: E402

# Try to import libcst for enhanced parsing
try:
    import libcst as cst

    MetadataWrapper = cst.metadata.MetadataWrapper
    PositionProvider = cst.metadata.PositionProvider
    LIBCST_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    LIBCST_AVAILABLE = False
    cst = None
    MetadataWrapper = None
    PositionProvider = None


class ParseError(Exception):
    """Raised when parsing fails."""

    def __init__(self, message: str, file_path: Optional[Path] = None, line: int = 0):
        self.file_path = file_path
        self.line = line
        super().__init__(message)


class UniversalParser:
    """Universal Python parser with libcst primary and ast fallback.

    Attributes:
        use_libcst: Whether to use libcst (True) or stdlib ast (False)
        strict: Whether to raise errors on parse failures
    """

    def __init__(self, use_libcst: bool = True, strict: bool = False):
        """Initialize parser.

        Args:
            use_libcst: Use libcst if available (default True)
            strict: Raise ParseError on failures (default False)
        """
        self.use_libcst = use_libcst and LIBCST_AVAILABLE
        self.strict = strict
        self._node_counter = 0

    def _generate_node_id(self, prefix: str = "node") -> str:
        """Generate unique node ID."""
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"

    def parse_file(self, file_path: str | Path) -> Optional[StandardizedASTNode]:
        """Parse a Python file into StandardizedASTNode tree.

        Args:
            file_path: Path to Python file

        Returns:
            Root StandardizedASTNode or None on failure
        """
        file_path = Path(file_path)
        if not file_path.exists():
            if self.strict:
                raise ParseError(f"File not found: {file_path}", file_path)
            return None

        try:
            code = file_path.read_text(encoding="utf-8", errors="ignore")
            return self.parse_string(code, file_path)
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            if self.strict:
                raise ParseError(str(e), file_path) from e
            return None

    def parse_string(
        self, code: str, file_path: Optional[Path] = None
    ) -> Optional[StandardizedASTNode]:
        """Parse Python source code string.

        Args:
            code: Python source code
            file_path: Optional file path for source location

        Returns:
            Root StandardizedASTNode or None on failure
        """
        file_path = file_path or Path("<string>")

        if self.use_libcst:
            return self._parse_with_libcst(code, file_path)
        return self._parse_with_ast(code, file_path)

    def _parse_with_libcst(self, code: str, file_path: Path) -> Optional[StandardizedASTNode]:
        """Parse using libcst for enhanced CST preservation."""
        try:
            tree = cst.parse_module(code)
            wrapper = MetadataWrapper(tree)

            # Create root module node
            root = StandardizedASTNode(
                node_id=self._generate_node_id("module"),
                type=NodeType.MODULE,
                name=file_path.stem,
                source_location=SourceLocation(file_path, 1, 0, len(code.splitlines()), 0),
                metadata={
                    "parser": "libcst",
                    "hash": hashlib.sha256(code.encode()).hexdigest(),
                },
            )

            # Extract children using visitor
            visitor = _LibCSTExtractor(file_path, self._generate_node_id)
            wrapper.visit(visitor)

            for child in visitor.nodes:
                root.add_child(child)

            return root

        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            if self.strict:
                raise ParseError(str(e), file_path) from e
            # Fallback to stdlib ast
            return self._parse_with_ast(code, file_path)

    def _parse_with_ast(self, code: str, file_path: Path) -> Optional[StandardizedASTNode]:
        """Parse using stdlib ast module (fallback)."""
        try:
            tree = ast.parse(code, filename=str(file_path))

            # Create root module node
            root = StandardizedASTNode(
                node_id=self._generate_node_id("module"),
                type=NodeType.MODULE,
                name=file_path.stem,
                source_location=SourceLocation(file_path, 1, 0, len(code.splitlines()), 0),
                metadata={
                    "parser": "ast",
                    "hash": hashlib.sha256(code.encode()).hexdigest(),
                },
            )

            # Extract top-level definitions
            for node in ast.iter_child_nodes(tree):
                child = self._convert_ast_node(node, file_path)
                if child:
                    root.add_child(child)

            return root

        except SyntaxError as e:
            type(e).__name__
            logger.debug("SyntaxError: <ERROR_TYPE>")
            if self.strict:
                raise ParseError(str(e), file_path, e.lineno or 0) from e
            return None

    def _convert_ast_node(self, node: ast.AST, file_path: Path) -> Optional[StandardizedASTNode]:
        """Convert stdlib ast node to StandardizedASTNode."""
        node_type = None
        name = ""
        docstring = None
        decorators: list[str] = []
        type_hints: dict[str, Any] = {}

        if isinstance(node, ast.FunctionDef):
            node_type = NodeType.FUNCTION
            name = node.name
            docstring = ast.get_docstring(node)
            decorators = [self._decorator_to_str(d) for d in node.decorator_list]
            type_hints = self._extract_type_hints(node)

        elif isinstance(node, ast.AsyncFunctionDef):
            node_type = NodeType.ASYNC_FUNCTION
            name = node.name
            docstring = ast.get_docstring(node)
            decorators = [self._decorator_to_str(d) for d in node.decorator_list]
            type_hints = self._extract_type_hints(node)

        elif isinstance(node, ast.ClassDef):
            node_type = NodeType.CLASS
            name = node.name
            docstring = ast.get_docstring(node)
            decorators = [self._decorator_to_str(d) for d in node.decorator_list]

        elif isinstance(node, ast.Import):
            node_type = NodeType.IMPORT
            name = ", ".join(alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom):
            node_type = NodeType.FROM_IMPORT
            module = node.module or ""
            name = f"from {module} import {', '.join(alias.name for alias in node.names)}"

        elif isinstance(node, ast.Lambda):
            node_type = NodeType.LAMBDA
            name = "<lambda>"

        else:
            # Skip other node types for now
            return None

        # Get source location
        line_start = getattr(node, "lineno", 1)
        col_start = getattr(node, "col_offset", 0)
        line_end = getattr(node, "end_lineno", line_start)
        col_end = getattr(node, "end_col_offset", col_start)

        location = SourceLocation(file_path, line_start, col_start, line_end, col_end)

        result = StandardizedASTNode(
            node_id=self._generate_node_id(node_type.value),
            type=node_type,
            name=name,
            source_location=location,
            docstring=docstring,
            decorators=decorators,
            type_hints=type_hints,
        )

        # Recursively process children for classes
        if isinstance(node, ast.ClassDef):
            for child_node in node.body:
                child = self._convert_ast_node(child_node, file_path)
                if child:
                    result.add_child(child)

        return result

    def _decorator_to_str(self, decorator: ast.expr) -> str:
        """Convert decorator AST node to string."""
        if isinstance(decorator, ast.Name):
            return f"@{decorator.id}"
        if isinstance(decorator, ast.Attribute):
            return f"@{ast.unparse(decorator)}"
        if isinstance(decorator, ast.Call):
            return f"@{ast.unparse(decorator)}"
        return "@<unknown>"

    def _extract_type_hints(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
        """Extract type hints from function definition."""
        hints = {}

        # Return type
        if node.returns:
            hints["return"] = ast.unparse(node.returns)

        # Parameter types
        for arg in node.args.args:
            if arg.annotation:
                hints[arg.arg] = ast.unparse(arg.annotation)

        return hints


class _LibCSTExtractor(cst.CSTVisitor if LIBCST_AVAILABLE else object):  # type: ignore[misc]
    """LibCST visitor to extract nodes."""

    def __init__(self, file_path: Path, id_generator) -> None:
        self.file_path = file_path
        self.id_generator = id_generator
        self.nodes: list[StandardizedASTNode] = []

    if LIBCST_AVAILABLE:
        METADATA_DEPENDENCIES = (PositionProvider,)

        def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
            """Visit function definition."""
            pos = self.get_metadata(PositionProvider, node)
            location = SourceLocation(
                self.file_path,
                pos.start.line,
                pos.start.column,
                pos.end.line,
                pos.end.column,
            )

            # Extract docstring
            docstring = None
            if node.body and node.body.body:
                first_stmt = node.body.body[0]
                if isinstance(first_stmt, cst.SimpleStatementLine):
                    for stmt in first_stmt.body:
                        if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.SimpleString):
                            docstring = stmt.value.value.strip("\"'")
                            break

            # Extract decorators
            decorators = []
            for dec in node.decorators:
                dec_name = dec.decorator
                if isinstance(dec_name, cst.Name):
                    decorators.append(f"@{dec_name.value}")
                elif isinstance(dec_name, cst.Attribute):
                    decorators.append(f"@{dec_name.attr.value}")
                elif isinstance(dec_name, cst.Call):
                    if isinstance(dec_name.func, cst.Name):
                        decorators.append(f"@{dec_name.func.value}(...)")

            # Determine if async
            is_async = node.asynchronous is not None
            node_type = NodeType.ASYNC_FUNCTION if is_async else NodeType.FUNCTION

            self.nodes.append(
                StandardizedASTNode(
                    node_id=self.id_generator(node_type.value),
                    type=node_type,
                    name=node.name.value,
                    source_location=location,
                    docstring=docstring,
                    decorators=decorators,
                )
            )
            return False  # Don't visit children

        def visit_ClassDef(self, node: cst.ClassDef) -> bool:
            """Visit class definition."""
            pos = self.get_metadata(PositionProvider, node)
            location = SourceLocation(
                self.file_path,
                pos.start.line,
                pos.start.column,
                pos.end.line,
                pos.end.column,
            )

            # Extract docstring
            docstring = None
            if node.body and node.body.body:
                first_stmt = node.body.body[0]
                if isinstance(first_stmt, cst.SimpleStatementLine):
                    for stmt in first_stmt.body:
                        if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.SimpleString):
                            docstring = stmt.value.value.strip("\"'")
                            break

            # Extract decorators
            decorators = []
            for dec in node.decorators:
                dec_name = dec.decorator
                if isinstance(dec_name, cst.Name):
                    decorators.append(f"@{dec_name.value}")

            self.nodes.append(
                StandardizedASTNode(
                    node_id=self.id_generator("class"),
                    type=NodeType.CLASS,
                    name=node.name.value,
                    source_location=location,
                    docstring=docstring,
                    decorators=decorators,
                )
            )
            return False  # Don't visit children


# Convenience function
def parse_python(source: str | Path, strict: bool = False) -> Optional[StandardizedASTNode]:
    """Parse Python source into StandardizedASTNode tree.

    Args:
        source: File path or source code string
        strict: Raise exceptions on errors

    Returns:
        Root StandardizedASTNode or None
    """
    parser = UniversalParser(strict=strict)

    if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        return parser.parse_file(source)
    return parser.parse_string(source)
