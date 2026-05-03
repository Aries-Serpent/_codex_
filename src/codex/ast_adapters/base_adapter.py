"""
Base AST adapter interface for language-agnostic code analysis.

Defines the contract that all language-specific adapters must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class StandardizedASTNode:
    """
    Language-agnostic AST node representation.

    This standardized format allows uniform analysis across different languages.
    """

    # Identity (required)
    node_id: str
    node_type: str
    name: str

    # Source location
    file_path: Optional[Path] = None
    line_start: int = 0
    line_end: int = 0
    column_start: int = 0
    column_end: int = 0

    # Structure (with defaults)
    parent: Optional["StandardizedASTNode"] = None
    children: list["StandardizedASTNode"] = field(default_factory=list)

    # Metadata (extensible)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Original source
    source_text: Optional[str] = None

    @property
    def depth(self) -> int:
        """Calculate tree depth from root."""
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    @property
    def full_name(self) -> str:
        """Get fully qualified name including parent context."""
        if self.parent and self.parent.name:
            return f"{self.parent.full_name}.{self.name}"
        return self.name

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "file_path": str(self.file_path) if self.file_path else None,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "depth": self.depth,
            "metadata": self.metadata,
            "children_count": len(self.children),
        }


class BaseASTAdapter(ABC):
    """
    Abstract base class for language-specific AST adapters.

    All language adapters must implement these methods to provide
    standardized AST analysis capabilities.
    """

    def __init__(self, file_path: Optional[Path] = None):
        """
        Initialize the adapter.

        Args:
            file_path: Optional path to the file being analyzed
        """
        self.file_path = file_path
        self.root_node: Optional[StandardizedASTNode] = None
        self._node_counter = 0

    def _generate_node_id(self) -> str:
        """Generate unique node ID."""
        self._node_counter += 1
        return f"node_{self._node_counter}"

    @abstractmethod
    def parse(self, source_code: str) -> StandardizedASTNode:
        """
        Parse source code and return standardized AST root node.

        Args:
            source_code: Source code string to parse

        Returns:
            Root node of the standardized AST

        Raises:
            SyntaxError: If source code has syntax errors

        Note:
            Subclasses may add optional parameters (e.g., file_path) to their
            parse() signature. The base signature requires only source_code.
        """

    @abstractmethod
    def extract_metadata(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Extract language-specific metadata from a node.

        Args:
            node: Standardized AST node

        Returns:
            Dictionary of metadata (decorators, type hints, etc.)
        """

    def parse_file(self, file_path: Path) -> StandardizedASTNode:
        """
        Parse a file and return standardized AST.

        Args:
            file_path: Path to file to parse

        Returns:
            Root node of the standardized AST
        """
        self.file_path = file_path
        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()
        return self.parse(source_code)

    def traverse(self, node: Optional[StandardizedASTNode] = None) -> list[StandardizedASTNode]:
        """
        Traverse AST and return all nodes in depth-first order.

        Args:
            node: Starting node (defaults to root)

        Returns:
            List of all nodes in traversal order
        """
        if node is None:
            node = self.root_node

        if node is None:
            return []

        nodes = [node]
        for child in node.children:
            nodes.extend(self.traverse(child))

        return nodes

    def find_nodes_by_type(self, node_type: str) -> list[StandardizedASTNode]:
        """
        Find all nodes of a specific type.

        Args:
            node_type: Type of nodes to find

        Returns:
            List of matching nodes
        """
        all_nodes = self.traverse()
        return [node for node in all_nodes if node.node_type == node_type]

    def get_stats(self) -> dict[str, int]:
        """
        Get statistics about the AST.

        Returns:
            Dictionary with node counts by type
        """
        all_nodes = self.traverse()
        stats: dict[str, Any] = {}
        for node in all_nodes:
            stats[node.node_type] = stats.get(node.node_type, 0) + 1
        return stats
