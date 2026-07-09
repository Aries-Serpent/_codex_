"""Standardized AST node representation (language-agnostic).

Design patterns from:
- libcst.MetadataWrapper
- tree-sitter Node
- Roslyn SyntaxNode
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class NodeType(Enum):
    """Supported AST node types."""

    MODULE = "module"
    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    CLASS = "class"
    LAMBDA = "lambda"
    IMPORT = "import"
    FROM_IMPORT = "from_import"
    STATEMENT = "statement"
    EXPRESSION = "expression"
    DECORATOR = "decorator"
    COMPREHENSION = "comprehension"


@dataclass
class SourceLocation:
    """Pinpoint source code location."""

    file_path: Path
    line_start: int
    column_start: int
    line_end: int
    column_end: int

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_start}:{self.column_start}"


@dataclass
class StandardizedASTNode:
    """Language-agnostic AST node representation.

    Attributes:
        node_id: Unique identifier within codebase
        type: Node type (NodeType enum)
        name: Identifier (function name, class name, etc.)
        source_location: File + line/column information
        children: Child nodes (empty for leaf nodes)
        parent: Parent node reference (None for root)
        docstring: Documentation string (if present)
        decorators: Applied decorators (if any)
        type_hints: Type annotations (param → type mappings)
        metadata: Language-specific metadata
    """

    node_id: str
    type: NodeType
    name: str
    source_location: SourceLocation

    children: list[StandardizedASTNode] = field(default_factory=list)
    parent: Optional[StandardizedASTNode] = None
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    type_hints: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: StandardizedASTNode) -> None:
        """Add child node and set parent reference."""
        child.parent = self
        self.children.append(child)

    def __eq__(self, other: object) -> bool:
        """Equality by node_id, consistent with __hash__."""
        if not isinstance(other, StandardizedASTNode):
            return NotImplemented
        return self.node_id == other.node_id

    def __hash__(self) -> int:
        """Hash by node_id so StandardizedASTNode can be used in sets/dict keys."""
        return hash(self.node_id)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (JSON-compatible)."""
        return {
            "node_id": self.node_id,
            "type": self.type.value,
            "name": self.name,
            "source_location": {
                "file": str(self.source_location.file_path),
                "line_start": self.source_location.line_start,
                "line_end": self.source_location.line_end,
                "column_start": self.source_location.column_start,
                "column_end": self.source_location.column_end,
            },
            "children": [c.node_id for c in self.children],
            "docstring": self.docstring,
            "decorators": self.decorators,
            "type_hints": self.type_hints,
            "metadata": self.metadata,
        }

    def walk(self) -> Any:
        """Depth-first tree traversal."""
        yield self
        for child in self.children:
            yield from child.walk()

    def get_depth(self) -> int:
        """Get node depth in tree."""
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1
