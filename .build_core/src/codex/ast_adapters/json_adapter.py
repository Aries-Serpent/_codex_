"""
JSON AST Adapter for Codex AST Framework.

Provides JSON parsing capabilities with standardized node representation.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Optional

from .base_adapter import BaseASTAdapter, StandardizedASTNode


class JSONASTAdapter(BaseASTAdapter):
    """
    AST adapter for JSON files.

    Parses JSON documents into standardized AST representation, extracting
    structure, keys, values, and metadata.

    Example:
        >>> adapter = JSONASTAdapter()
        >>> root = adapter.parse('{"key": "value", "list": [1, 2, 3]}')
        >>> nodes = adapter.find_nodes_by_type("object")
        >>> len(nodes)
        1
    """

    def __init__(self) -> None:
        super().__init__()
        self._current_file: Optional[Path] = None

    def parse(self, source: str, file_path: Optional[Path] = None) -> StandardizedASTNode:
        """
        Parse JSON source into standardized AST.

        Args:
            source: JSON source code as string
            file_path: Optional path to source file

        Returns:
            Root StandardizedASTNode representing the JSON document

        Raises:
            ValueError: If JSON parsing fails
        """
        # Use provided file_path or fall back to self.file_path
        effective_path = file_path or self.file_path
        self._current_file = effective_path

        try:
            # Parse JSON
            data = json.loads(source)

            # Create root document node
            root = StandardizedASTNode(
                node_id=str(uuid.uuid4()),
                node_type="document",
                name="<json_document>",
                file_path=effective_path,
                line_start=1,
                line_end=len(source.splitlines()),
                column_start=0,
                column_end=0,
                children=[],
                metadata={"encoding": "utf-8"},
            )

            # Convert JSON data to AST nodes
            if data is not None:
                child_node = self._convert_to_node(data, parent=root)
                root.children.append(child_node)

            # Store root for later access
            self.root_node = root

            return root

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}") from e

    def _convert_to_node(
        self,
        data: Any,
        parent: Optional[StandardizedASTNode] = None,
        key: Optional[str] = None,
    ) -> StandardizedASTNode:
        """
        Convert JSON data structure to StandardizedASTNode.

        Args:
            data: JSON data (dict, list, scalar)
            parent: Parent node
            key: Key name if this is an object value

        Returns:
            StandardizedASTNode representing the data
        """
        if isinstance(data, dict):
            # Object node
            node = StandardizedASTNode(
                node_id=str(uuid.uuid4()),
                node_type="object",
                name=key or "<object>",
                children=[],
                metadata={"keys": list(data.keys()), "size": len(data)},
                parent=parent,
            )

            # Add child nodes for each key-value pair
            for k, v in data.items():
                child = self._convert_to_node(v, parent=node, key=k)
                node.children.append(child)

            return node

        if isinstance(data, list):
            # Array node
            node = StandardizedASTNode(
                node_id=str(uuid.uuid4()),
                node_type="array",
                name=key or "<array>",
                children=[],
                metadata={
                    "length": len(data),
                    "item_types": [type(item).__name__ for item in data],
                },
                parent=parent,
            )

            # Add child nodes for each item
            for i, item in enumerate(data):
                child = self._convert_to_node(item, parent=node, key=f"[{i}]")
                node.children.append(child)

            return node

        # Primitive node (string, int, float, bool, None)
        return StandardizedASTNode(
            node_id=str(uuid.uuid4()),
            node_type="primitive",
            name=key or "<primitive>",
            children=[],
            metadata={
                "value": data,
                "value_type": type(data).__name__,
                "is_null": data is None,
            },
            parent=parent,
        )

    def extract_metadata(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Extract JSON-specific metadata from a node.

        Args:
            node: Node to extract metadata from

        Returns:
            Dictionary of metadata
        """
        metadata = node.metadata.copy()

        if node.node_type == "object":
            metadata["node_type"] = "JSON object"
            metadata["key_count"] = len(metadata.get("keys", []))
        elif node.node_type == "array":
            metadata["node_type"] = "JSON array"
            metadata["element_count"] = metadata.get("length", 0)
        elif node.node_type == "primitive":
            metadata["node_type"] = "JSON primitive"
            metadata["json_type"] = metadata.get("value_type", "unknown")

        return metadata

    def get_value_at_path(self, path: str) -> Any:
        """
        Get value at a specific path in the JSON structure.

        Path uses dot notation for objects and brackets for arrays.
        Example: "config.database.host" or "items[0].name"

        Args:
            path: Dot-separated path to value

        Returns:
            Value at the path, or None if not found
        """
        if not self.root_node or not self.root_node.children:
            return None

        # Start from the first child (actual data root)
        current = self.root_node.children[0]
        parts = path.split(".")

        for part in parts:
            # Handle array indexing
            if "[" in part and "]" in part:
                key = part.split("[")[0]
                index_str = part.split("[")[1].split("]")[0]

                # Find the key first
                if key:
                    found = False
                    for child in current.children:
                        if child.name == key:
                            current = child
                            found = True
                            break
                    if not found:
                        return None

                # Then navigate to array index
                try:
                    index = int(index_str)
                    if index < len(current.children):
                        current = current.children[index]
                    else:
                        return None
                except (ValueError, IndexError):
                    return None
            else:
                # Regular key access
                found = False
                for child in current.children:
                    if child.name == part:
                        current = child
                        found = True
                        break
                if not found:
                    return None

        # Return the value if it's a primitive
        if current.node_type == "primitive":
            return current.metadata.get("value")

        return current
