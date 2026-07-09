"""
Python AST adapter using libcst for robust parsing.

Provides Python-specific AST analysis with metadata extraction for:
- Functions and classes
- Decorators
- Type hints
- Docstrings
- Import statements
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import libcst as cst

    _LIBCST_AVAILABLE = True
except ImportError:  # pragma: no cover
    cst = None

    _LIBCST_AVAILABLE = False

from .base_adapter import BaseASTAdapter, StandardizedASTNode


class PythonASTAdapter(BaseASTAdapter):
    """
    Python AST adapter using libcst for concrete syntax tree parsing.

    libcst preserves formatting and provides full fidelity parsing,
    making it ideal for code analysis and transformation.
    """

    def __init__(self, file_path: Optional[Path] = None):
        """Initialize Python AST adapter."""
        if not _LIBCST_AVAILABLE:  # pragma: no cover
            raise ImportError(
                "libcst is required for PythonASTAdapter. "
                "Install it with: pip install libcst>=1.0.0"
            )
        super().__init__(file_path)
        self._cst_tree: Optional[cst.Module] = None

    def parse(self, source_code: str) -> StandardizedASTNode:
        """
        Parse Python source code using libcst.

        Args:
            source_code: Python source code string

        Returns:
            Root node of standardized AST

        Raises:
            SyntaxError: If Python code has syntax errors
        """
        try:
            self._cst_tree = cst.parse_module(source_code)
        except cst.ParserSyntaxError as e:
            raise SyntaxError(f"Python syntax error: {e}") from e

        # Create root node
        self.root_node = StandardizedASTNode(
            node_id=self._generate_node_id(),
            node_type="module",
            name="<module>",
            file_path=self.file_path,
            metadata={"language": "python"},
        )

        # Process the CST tree
        self._process_node(self._cst_tree, self.root_node)

        return self.root_node

    def _process_node(self, cst_node: cst.CSTNode, parent: StandardizedASTNode) -> None:
        """
        Recursively process CST nodes and build standardized tree.

        Args:
            cst_node: libcst node to process
            parent: Parent standardized node
        """
        # Process module body first
        if isinstance(cst_node, cst.Module):
            for stmt in cst_node.body:
                self._process_node(stmt, parent)
            return

        # Handle different node types
        if isinstance(cst_node, cst.FunctionDef):
            self._process_function(cst_node, parent)
            return  # Don't continue processing - children handled in _process_function

        if isinstance(cst_node, cst.ClassDef):
            self._process_class(cst_node, parent)
            return  # Don't continue processing - children handled in _process_class

        if isinstance(cst_node, (cst.Import, cst.ImportFrom)):
            self._process_import(cst_node, parent)
            return

        if isinstance(cst_node, cst.Assign):
            self._process_assignment(cst_node, parent)
            return

        # Recursively process children for other compound statements
        if hasattr(cst_node, "body"):
            if isinstance(cst_node.body, cst.IndentedBlock):
                for stmt in cst_node.body.body:
                    self._process_node(stmt, parent)
            elif isinstance(cst_node.body, (list, tuple)):
                for stmt in cst_node.body:
                    self._process_node(stmt, parent)

    def _process_function(self, func: cst.FunctionDef, parent: StandardizedASTNode) -> None:
        """Process function definition."""
        func_name = func.name.value

        # Extract position info if available
        # Note: Position metadata requires MetadataWrapper to be set up.
        # Without it, line_start/line_end will default to 0.
        # Wrapping the module in MetadataWrapper would provide accurate positions.
        pos = func.name.metadata.get("position", None) if hasattr(func.name, "metadata") else None
        line_start = pos.start.line if pos else 0
        line_end = pos.end.line if pos else 0

        # Create function node
        func_node = StandardizedASTNode(
            node_id=self._generate_node_id(),
            node_type="function",
            name=func_name,
            file_path=self.file_path,
            line_start=line_start,
            line_end=line_end,
            parent=parent,
            metadata=self._extract_function_metadata(func),
        )

        parent.children.append(func_node)

        # Process function body
        if isinstance(func.body, cst.IndentedBlock):
            for stmt in func.body.body:
                self._process_node(stmt, func_node)

    def _process_class(self, cls: cst.ClassDef, parent: StandardizedASTNode) -> None:
        """Process class definition."""
        cls_name = cls.name.value

        # Extract position info
        pos = cls.name.metadata.get("position", None) if hasattr(cls.name, "metadata") else None
        line_start = pos.start.line if pos else 0
        line_end = pos.end.line if pos else 0

        # Create class node
        cls_node = StandardizedASTNode(
            node_id=self._generate_node_id(),
            node_type="class",
            name=cls_name,
            file_path=self.file_path,
            line_start=line_start,
            line_end=line_end,
            parent=parent,
            metadata=self._extract_class_metadata(cls),
        )

        parent.children.append(cls_node)

        # Process class body
        if isinstance(cls.body, cst.IndentedBlock):
            for stmt in cls.body.body:
                self._process_node(stmt, cls_node)

    def _get_full_name(self, node: cst.CSTNode) -> str:
        """Extract full dotted name from libcst node (handles Name and Attribute)."""
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            return f"{self._get_full_name(node.value)}.{node.attr.value}"
        return str(node)

    def _process_import(self, imp: cst.CSTNode, parent: StandardizedASTNode) -> None:
        """Process import statement."""
        if isinstance(imp, cst.Import):
            for name in imp.names:
                if isinstance(name, cst.ImportAlias):
                    # Handle both simple names (import foo) and dotted names (import a.b.c)
                    import_name = self._get_full_name(name.name)

                    import_node = StandardizedASTNode(
                        node_id=self._generate_node_id(),
                        node_type="import",
                        name=import_name,
                        file_path=self.file_path,
                        parent=parent,
                        metadata={"alias": name.asname.name.value if name.asname else None},
                    )
                    parent.children.append(import_node)

        elif isinstance(imp, cst.ImportFrom):
            # Handle dotted module names in from imports
            module = self._get_full_name(imp.module) if imp.module else ""
            for name in imp.names:
                if isinstance(name, cst.ImportAlias):
                    imported_name = (
                        name.name.value if isinstance(name.name, cst.Name) else str(name.name)
                    )
                    full_name = f"{module}.{imported_name}" if module else imported_name

                    import_node = StandardizedASTNode(
                        node_id=self._generate_node_id(),
                        node_type="import_from",
                        name=full_name,
                        file_path=self.file_path,
                        parent=parent,
                        metadata={
                            "module": module,
                            "name": imported_name,
                            "alias": name.asname.name.value if name.asname else None,
                        },
                    )
                    parent.children.append(import_node)

    def _process_assignment(self, assign: cst.Assign, parent: StandardizedASTNode) -> None:
        """Process assignment statement."""
        # Extract variable names from targets
        for target in assign.targets:
            if isinstance(target.target, cst.Name):
                var_name = target.target.value

                assign_node = StandardizedASTNode(
                    node_id=self._generate_node_id(),
                    node_type="assignment",
                    name=var_name,
                    file_path=self.file_path,
                    parent=parent,
                    metadata={},
                )
                parent.children.append(assign_node)

    def _extract_function_metadata(self, func: cst.FunctionDef) -> dict[str, Any]:
        """Extract metadata from function definition."""
        metadata = {}

        # Extract decorators
        if func.decorators:
            metadata["decorators"] = [
                dec.decorator.value if isinstance(dec.decorator, cst.Name) else str(dec.decorator)
                for dec in func.decorators
            ]

        # Extract docstring
        if isinstance(func.body, cst.IndentedBlock) and func.body.body:
            first_stmt = func.body.body[0]
            if isinstance(first_stmt, cst.SimpleStatementLine):
                for node in first_stmt.body:
                    if isinstance(node, cst.Expr) and isinstance(node.value, cst.SimpleString):
                        metadata["docstring"] = node.value.value.strip("\"\"\"'''")

                        break

        # Extract parameters
        params = []
        for param in func.params.params:
            param_info = {"name": param.name.value}
            if param.annotation:
                param_info["type_hint"] = str(param.annotation.annotation)
            if param.default:
                param_info["default"] = str(param.default)
            params.append(param_info)
        metadata["parameters"] = params  # type: ignore[assignment]

        # Extract return type
        if func.returns:
            metadata["return_type"] = str(func.returns.annotation)  # type: ignore[assignment]

        return metadata

    def _extract_class_metadata(self, cls: cst.ClassDef) -> dict[str, Any]:
        """Extract metadata from class definition."""
        metadata = {}

        # Extract decorators
        if cls.decorators:
            metadata["decorators"] = [
                dec.decorator.value if isinstance(dec.decorator, cst.Name) else str(dec.decorator)
                for dec in cls.decorators
            ]

        # Extract base classes
        if cls.bases:
            metadata["bases"] = [
                base.value.value if isinstance(base.value, cst.Name) else str(base.value)
                for base in cls.bases
            ]

        # Extract docstring
        if isinstance(cls.body, cst.IndentedBlock) and cls.body.body:
            first_stmt = cls.body.body[0]
            if isinstance(first_stmt, cst.SimpleStatementLine):
                for node in first_stmt.body:
                    if isinstance(node, cst.Expr) and isinstance(node.value, cst.SimpleString):
                        metadata["docstring"] = node.value.value.strip("\"\"\"'''")

                        break

        return metadata

    def extract_metadata(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Extract Python-specific metadata from a standardized node.

        Args:
            node: Standardized AST node

        Returns:
            Dictionary of Python-specific metadata
        """
        # Metadata is already extracted during parsing and stored in node.metadata
        return node.metadata.copy()
