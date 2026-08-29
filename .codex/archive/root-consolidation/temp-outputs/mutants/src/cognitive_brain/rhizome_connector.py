"""
Rhizomatic Connection Tracker

Implements Deleuzian rhizome principles for cognitive module connections.
Following the pattern: "any point can be connected to any other point"

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#rhizomatic-architecture
Philosophical Foundation: Deleuze & Guattari - A Thousand Plateaus (1980)

Core Principles:
1. Connection: Any module can connect to any other
2. Heterogeneity: Multiple different types of connections
3. Multiplicity: No unity, only assemblages
4. Asignifying Rupture: Can be broken and reconnected elsewhere
5. Cartography: Must be mappable (memory, not fixed map)
6. Decalcomania: No models, only performances
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Types of rhizomatic connections between modules."""

    DIRECT = "direct"  # Direct function/method call
    DATA_FLOW = "data_flow"  # Data passed between modules
    EVENT = "event"  # Event-based communication
    SHARED_STATE = "shared_state"  # Shared memory/state
    TEMPORAL = "temporal"  # Time-based causation
    EMERGENT = "emergent"  # Emergent connection (discovered pattern)


class RuptureType(Enum):
    """Types of ruptures (breaks) in connections."""

    INTENTIONAL = "intentional"  # Deliberately broken
    TRANSIENT = "transient"  # Temporary disconnection
    REFACTORED = "refactored"  # Changed during refactoring
    DETERRITORIALIZED = "deterritorialized"  # Broken for innovation


@dataclass
class RhizomaticNode:
    """
    A node in the rhizomatic network.

    Unlike tree nodes, rhizomatic nodes have no inherent parent-child
    relationships. All connections are lateral and non-hierarchical.
    """

    module_path: str
    node_type: str  # e.g., "cognitive_module", "rag_component", "cli_handler"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    active: bool = True

    def __hash__(self) -> int:
        return hash(self.module_path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RhizomaticNode):
            return False
        return self.module_path == other.module_path


@dataclass
class RhizomaticConnection:
    """
    A connection between two nodes in the rhizome.

    Connections are non-hierarchical and can be of multiple types simultaneously.
    """

    source: RhizomaticNode
    target: RhizomaticNode
    connection_types: set[ConnectionType]
    strength: float = 1.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    use_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(
                f"Connection strength must be between 0.0 and 1.0, got {self.strength}"
            )

    def record_use(self) -> None:
        """Record that this connection was used."""
        self.last_used = datetime.now(timezone.utc)
        self.use_count += 1


@dataclass
class Rupture:
    """
    A rupture (break) in a connection.

    Following Deleuze: "The rhizome may be broken, shattered at a given spot,
    but it will start up again on one of its old lines, or on new lines."
    """

    connection: RhizomaticConnection
    rupture_type: RuptureType
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = None
    reconnection_path: Optional[str] = None  # Where it reconnected


class RhizomeConnector:
    """
    Tracks and manages rhizomatic connections between cognitive modules.

    Unlike hierarchical dependency graphs, the rhizome allows:
    - Non-hierarchical connections
    - Multiple simultaneous paths between nodes
    - Dynamic connection creation/destruction
    - Emergent patterns and assemblages

    Example:
        >>> connector = RhizomeConnector()
        >>> node_a = RhizomaticNode("src.cognitive_brain.base", "cognitive_module")
        >>> node_b = RhizomaticNode("src.codex.rag.indexer", "rag_component")
        >>> connector.add_node(node_a)
        >>> connector.add_node(node_b)
        >>> connector.connect(node_a, node_b, {ConnectionType.DATA_FLOW})
        >>> score = connector.calculate_rhizomaticity()
        >>> print(f"Rhizomaticity: {score:.2%}")
    """

    def __init__(self) -> None:
        self.nodes: dict[str, RhizomaticNode] = {}
        self.connections: list[RhizomaticConnection] = []
        self.ruptures: list[Rupture] = []
        LOGGER.info("RhizomeConnector initialized")

    def add_node(self, node: RhizomaticNode) -> None:
        """Add a node to the rhizome."""
        if node.module_path in self.nodes:
            LOGGER.warning(f"Node {node.module_path} already exists, skipping")
            return

        self.nodes[node.module_path] = node
        LOGGER.debug(f"Added node: {node.module_path} (type: {node.node_type})")

    def connect(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RhizomaticConnection:
        """
        Create a connection between two nodes.

        Args:
            source: Source node
            target: Target node
            connection_types: Types of connections (can be multiple)
            strength: Connection strength (0.0 to 1.0)
            metadata: Optional metadata

        Returns:
            The created connection
        """
        # Ensure both nodes exist
        if source.module_path not in self.nodes:
            self.add_node(source)
        if target.module_path not in self.nodes:
            self.add_node(target)

        connection = RhizomaticConnection(
            source=source,
            target=target,
            connection_types=connection_types,
            strength=strength,
            metadata=metadata or {},
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def rupture_connection(
        self,
        connection: RhizomaticConnection,
        rupture_type: RuptureType,
        reason: Optional[str] = None,
    ) -> Rupture:
        """
        Break a connection (creating a rupture).

        Following Deleuze, ruptures are not failures but opportunities for
        new connections on different lines.
        """
        rupture = Rupture(
            connection=connection,
            rupture_type=rupture_type,
            reason=reason,
        )

        # Remove the connection
        if connection in self.connections:
            self.connections.remove(connection)

        self.ruptures.append(rupture)
        LOGGER.info(
            f"Ruptured connection {connection.source.module_path} -> "
            f"{connection.target.module_path} (type: {rupture_type.value})"
        )
        return rupture

    def calculate_rhizomaticity(self) -> float:
        """
        Calculate the rhizomaticity score.

        Rhizomaticity = Connections / Max_Possible_Connections

        Where:
        - 0.0 = Tree structure (minimal connections)
        - 1.0 = Fully connected rhizome

        Goal: R > 0.5 (more rhizomatic than tree-like)

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#philosophical-metrics
        """
        num_nodes = len(self.nodes)
        if num_nodes <= 1:
            return 0.0

        num_connections = len(self.connections)
        max_connections = (num_nodes * (num_nodes - 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def find_assemblages(self, min_nodes: int = 3) -> list[set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: list[set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: dict[str, set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: set[str] = set()

        def dfs(node_path: str, current_assemblage: set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def get_connection_strength_matrix(self) -> dict[tuple[str, str], float]:
        """
        Get a matrix of connection strengths between nodes.

        Returns:
            Dictionary mapping (source_path, target_path) to strength
        """
        matrix: dict[tuple[str, str], float] = {}

        for conn in self.connections:
            key = (conn.source.module_path, conn.target.module_path)
            matrix[key] = conn.strength

        return matrix

    def export_graph_data(self) -> dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "id": node.module_path,
                "type": node.node_type,
                "active": node.active,
                "created_at": node.created_at.isoformat(),
            }
            for node in self.nodes.values()
        ]

        edges_data = [
            {
                "source": conn.source.module_path,
                "target": conn.target.module_path,
                "types": [ct.value for ct in conn.connection_types],
                "strength": conn.strength,
                "use_count": conn.use_count,
            }
            for conn in self.connections
        ]

        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "metrics": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }
