"""
YAML AST Adapter for Codex AST Framework.

Provides YAML parsing capabilities with standardized node representation.
"""

import uuid
from pathlib import Path
from typing import Any, Optional

import yaml

from .base_adapter import BaseASTAdapter, StandardizedASTNode


class YAMLASTAdapter(BaseASTAdapter):
    """
    AST adapter for YAML files.

    Parses YAML documents into standardized AST representation, extracting
    structure, keys, values, and metadata.

    Example:
        >>> adapter = YAMLASTAdapter()
        >>> root = adapter.parse("key: value\\nlist:\\n  - item1")
        >>> nodes = adapter.find_nodes_by_type("mapping")
        >>> len(nodes)
        1
    """

    def __init__(self) -> None:
        super().__init__()
        self._current_file: Optional[Path] = None

    def parse(self, source: str, file_path: Optional[Path] = None) -> StandardizedASTNode:
        """
        Parse YAML source into standardized AST.

        Args:
            source: YAML source code as string
            file_path: Optional path to source file

        Returns:
            Root StandardizedASTNode representing the YAML document

        Raises:
            ValueError: If YAML parsing fails
        """
        # Use provided file_path or fall back to self.file_path
        effective_path = file_path or self.file_path
        self._current_file = effective_path

        try:
            # Parse YAML
            data = yaml.safe_load(source)

            # Create root document node
            root = StandardizedASTNode(
                node_id=str(uuid.uuid4()),
                node_type="document",
                name="<yaml_document>",
                file_path=effective_path,
                line_start=1,
                line_end=len(source.splitlines()),
                column_start=0,
                column_end=0,
                children=[],
                metadata={"yaml_version": "1.2"},
            )

            # Convert YAML data to AST nodes
            if data is not None:
                child_node = self._convert_to_node(data, parent=root)
                root.children.append(child_node)

            # Store root for later access
            self.root_node = root

            return root

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML: {e}") from e

    def _convert_to_node(
        self,
        data: Any,
        parent: Optional[StandardizedASTNode] = None,
        key: Optional[str] = None,
    ) -> StandardizedASTNode:
        """
        Convert YAML data structure to StandardizedASTNode.

        Args:
            data: YAML data (dict, list, scalar)
            parent: Parent node
            key: Key name if this is a mapping value

        Returns:
            StandardizedASTNode representing the data
        """
        if isinstance(data, dict):
            # Mapping node
            node = StandardizedASTNode(
                node_id=str(uuid.uuid4()),
                node_type="mapping",
                name=key or "<mapping>",
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
            # Sequence node
            node = StandardizedASTNode(
                node_id=str(uuid.uuid4()),
                node_type="sequence",
                name=key or "<sequence>",
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

        # Scalar node (string, int, float, bool, None)
        return StandardizedASTNode(
            node_id=str(uuid.uuid4()),
            node_type="scalar",
            name=key or "<scalar>",
            children=[],
            metadata={
                "value": data,
                "value_type": type(data).__name__,
                "is_null": data is None,
            },
            parent=parent,
        )

    def traverse(self, node: Optional[StandardizedASTNode] = None) -> list[StandardizedASTNode]:
        """
        Traverse AST depth-first, yielding all nodes.

        Args:
            node: Root node to start traversal (defaults to self.root_node)

        Returns:
            List of all nodes in depth-first order
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
            node_type: Type to search for ("mapping", "sequence", "scalar", "document")

        Returns:
            List of matching nodes
        """
        if not self.root_node:
            return []

        matching_nodes = []
        for node in self.traverse(self.root_node):
            if node.node_type == node_type:
                matching_nodes.append(node)

        return matching_nodes

    def get_value_at_path(self, path: str) -> Optional[Any]:
        """
        Get value at YAML path (e.g., "config.database.host").

        Args:
            path: Dot-separated path to value

        Returns:
            Value at path, or None if not found
        """
        if not self.root_node or not self.root_node.children:
            return None

        parts = path.split(".")
        current = self.root_node.children[0]  # First child is the data root

        for part in parts:
            if current.node_type != "mapping":
                return None

            # Find child with matching name
            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break

            if not found:
                return None

        # Return value if it's a scalar
        if current.node_type == "scalar":
            return current.metadata.get("value")

        return None

    def get_keys(self, node: Optional[StandardizedASTNode] = None) -> list[str]:
        """
        Get all keys from a mapping node.

        Args:
            node: Mapping node (uses root if None)

        Returns:
            List of keys
        """
        if node is None:
            node = self.root_node

        if not node or node.node_type != "mapping":
            return []

        return node.metadata.get("keys", [])

    def extract_metadata(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Extract metadata from YAML node.

        Args:
            node: Node to extract metadata from

        Returns:
            Dictionary of metadata
        """
        metadata = {
            "node_type": node.node_type,
            "name": node.name,
        }

        if node.node_type == "mapping":
            metadata["keys"] = node.metadata.get("keys", [])
            metadata["size"] = node.metadata.get("size", 0)
        elif node.node_type == "sequence":
            metadata["length"] = node.metadata.get("length", 0)
            metadata["item_types"] = node.metadata.get("item_types", [])
        elif node.node_type == "scalar":
            metadata["value"] = node.metadata.get("value")  # type: ignore[assignment]
            metadata["value_type"] = node.metadata.get("value_type")  # type: ignore[assignment]
            metadata["is_null"] = node.metadata.get("is_null", False)

        return metadata
