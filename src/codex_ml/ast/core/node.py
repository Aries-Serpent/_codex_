"""
Core AST node data structures.

Provides language-agnostic representations for AST nodes, source locations,
and analysis findings.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class SourceLocation:
    """Precise source code location.

    Represents a span in source code with file path, line numbers, and columns.

    Attributes:
        file_path: Path to the source file
        line_start: Starting line number (1-indexed)
        line_end: Ending line number (1-indexed)
        column_start: Starting column number (0-indexed)
        column_end: Ending column number (0-indexed)
    """

    file_path: Path
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0

    def __str__(self) -> str:
        """Format as 'file:line:col'."""
        return f"{self.file_path}:{self.line_start}:{self.column_start}"

    def __repr__(self) -> str:
        return (
            f"SourceLocation({self.file_path!r}, {self.line_start}, {self.line_end}, "
            f"{self.column_start}, {self.column_end})"
        )

    @classmethod
    def from_string(cls, location: str) -> "SourceLocation":
        """Parse 'file:line:col' format.

        Args:
            location: String in format 'file:line:col' or 'file:line' or 'file'

        Returns:
            SourceLocation instance
        """
        parts = location.split(":")
        file_path = Path(parts[0])
        line = int(parts[1]) if len(parts) > 1 else 1
        col = int(parts[2]) if len(parts) > 2 else 0
        return cls(
            file_path=file_path,
            line_start=line,
            line_end=line,
            column_start=col,
            column_end=col,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": str(self.file_path),
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end": self.column_end,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceLocation":
        """Create from dictionary."""
        return cls(
            file_path=Path(data["file_path"]),
            line_start=data["line_start"],
            line_end=data["line_end"],
            column_start=data.get("column_start", 0),
            column_end=data.get("column_end", 0),
        )


@dataclass
class StandardizedASTNode:
    """Language-agnostic AST node representation.

    Provides a unified structure for representing AST nodes from any
    programming language, enabling cross-language analysis.

    Attributes:
        node_id: Unique identifier for this node
        type: Node type (e.g., 'function', 'class', 'import')
        name: Node name (e.g., function name, class name)
        parent: Reference to parent node (None for root)
        children: List of child nodes
        location: Source code location
        metadata: Extensible metadata dictionary
    """

    node_id: str
    type: str
    name: str
    parent: Optional["StandardizedASTNode"] = None
    children: List["StandardizedASTNode"] = field(default_factory=list)
    location: Optional[SourceLocation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate node after initialization."""
        if not self.node_id:
            self.node_id = str(uuid.uuid4())

    @property
    def depth(self) -> int:
        """Calculate tree depth from root."""
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    @property
    def is_leaf(self) -> bool:
        """Check if this node has no children."""
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        """Check if this node has no parent."""
        return self.parent is None

    def add_child(self, child: "StandardizedASTNode") -> None:
        """Add a child node, setting its parent reference."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "StandardizedASTNode") -> bool:
        """Remove a child node, clearing its parent reference."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False

    def find_by_type(self, node_type: str) -> List["StandardizedASTNode"]:
        """Find all descendant nodes of a given type."""
        results = []
        if self.type == node_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find_by_type(node_type))
        return results

    def find_by_name(self, name: str) -> List["StandardizedASTNode"]:
        """Find all descendant nodes with a given name."""
        results = []
        if self.name == name:
            results.append(self)
        for child in self.children:
            results.extend(child.find_by_name(name))
        return results

    def walk(self) -> List["StandardizedASTNode"]:
        """Iterate over all nodes in the tree (pre-order traversal)."""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.walk())
        return nodes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "type": self.type,
            "name": self.name,
            "location": self.location.to_dict() if self.location else None,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional["StandardizedASTNode"] = None) -> "StandardizedASTNode":
        """Create from dictionary."""
        location = SourceLocation.from_dict(data["location"]) if data.get("location") else None
        node = cls(
            node_id=data["node_id"],
            type=data["type"],
            name=data["name"],
            parent=parent,
            location=location,
            metadata=data.get("metadata", {}),
        )
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data, parent=node)
            node.children.append(child)
        return node

    def __repr__(self) -> str:
        return f"StandardizedASTNode(type={self.type!r}, name={self.name!r}, children={len(self.children)})"


@dataclass
class Finding:
    """Analysis finding from an AST analyzer.

    Represents a code quality issue, pattern match, or metric violation
    discovered during AST analysis.

    Attributes:
        finding_id: Unique identifier
        type: Finding type (e.g., 'high_complexity', 'unused_import')
        severity: Severity level ('info', 'warning', 'error', 'critical')
        message: Human-readable description
        location: Source code location
        analyzer: Name of the analyzer that produced this finding
        metadata: Additional context
    """

    finding_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    severity: str = "info"
    message: str = ""
    location: Optional[SourceLocation] = None
    analyzer: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate severity level."""
        valid_severities = {"info", "warning", "error", "critical"}
        if self.severity not in valid_severities:
            self.severity = "info"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "finding_id": self.finding_id,
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "location": self.location.to_dict() if self.location else None,
            "analyzer": self.analyzer,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Finding":
        """Create from dictionary."""
        location = SourceLocation.from_dict(data["location"]) if data.get("location") else None
        return cls(
            finding_id=data.get("finding_id", str(uuid.uuid4())),
            type=data.get("type", ""),
            severity=data.get("severity", "info"),
            message=data.get("message", ""),
            location=location,
            analyzer=data.get("analyzer", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return f"Finding(type={self.type!r}, severity={self.severity!r}, message={self.message[:50]!r}...)"
