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
from typing import Any, Dict, List, Optional, Set, Tuple

LOGGER = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
    metadata: Dict[str, Any] = field(default_factory=dict)
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
    connection_types: Set[ConnectionType]
    strength: float = 1.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    use_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

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

    def xǁRhizomeConnectorǁ__init____mutmut_orig(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = []
        LOGGER.info("RhizomeConnector initialized")

    def xǁRhizomeConnectorǁ__init____mutmut_1(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = None
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = []
        LOGGER.info("RhizomeConnector initialized")

    def xǁRhizomeConnectorǁ__init____mutmut_2(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = None
        self.ruptures: List[Rupture] = []
        LOGGER.info("RhizomeConnector initialized")

    def xǁRhizomeConnectorǁ__init____mutmut_3(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = None
        LOGGER.info("RhizomeConnector initialized")

    def xǁRhizomeConnectorǁ__init____mutmut_4(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = []
        LOGGER.info(None)

    def xǁRhizomeConnectorǁ__init____mutmut_5(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = []
        LOGGER.info("XXRhizomeConnector initializedXX")

    def xǁRhizomeConnectorǁ__init____mutmut_6(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = []
        LOGGER.info("rhizomeconnector initialized")

    def xǁRhizomeConnectorǁ__init____mutmut_7(self) -> None:
        self.nodes: Dict[str, RhizomaticNode] = {}
        self.connections: List[RhizomaticConnection] = []
        self.ruptures: List[Rupture] = []
        LOGGER.info("RHIZOMECONNECTOR INITIALIZED")
    
    xǁRhizomeConnectorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁ__init____mutmut_1': xǁRhizomeConnectorǁ__init____mutmut_1, 
        'xǁRhizomeConnectorǁ__init____mutmut_2': xǁRhizomeConnectorǁ__init____mutmut_2, 
        'xǁRhizomeConnectorǁ__init____mutmut_3': xǁRhizomeConnectorǁ__init____mutmut_3, 
        'xǁRhizomeConnectorǁ__init____mutmut_4': xǁRhizomeConnectorǁ__init____mutmut_4, 
        'xǁRhizomeConnectorǁ__init____mutmut_5': xǁRhizomeConnectorǁ__init____mutmut_5, 
        'xǁRhizomeConnectorǁ__init____mutmut_6': xǁRhizomeConnectorǁ__init____mutmut_6, 
        'xǁRhizomeConnectorǁ__init____mutmut_7': xǁRhizomeConnectorǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁ__init____mutmut_orig)
    xǁRhizomeConnectorǁ__init____mutmut_orig.__name__ = 'xǁRhizomeConnectorǁ__init__'

    def xǁRhizomeConnectorǁadd_node__mutmut_orig(self, node: RhizomaticNode) -> None:
        """Add a node to the rhizome."""
        if node.module_path in self.nodes:
            LOGGER.warning(f"Node {node.module_path} already exists, skipping")
            return

        self.nodes[node.module_path] = node
        LOGGER.debug(f"Added node: {node.module_path} (type: {node.node_type})")

    def xǁRhizomeConnectorǁadd_node__mutmut_1(self, node: RhizomaticNode) -> None:
        """Add a node to the rhizome."""
        if node.module_path not in self.nodes:
            LOGGER.warning(f"Node {node.module_path} already exists, skipping")
            return

        self.nodes[node.module_path] = node
        LOGGER.debug(f"Added node: {node.module_path} (type: {node.node_type})")

    def xǁRhizomeConnectorǁadd_node__mutmut_2(self, node: RhizomaticNode) -> None:
        """Add a node to the rhizome."""
        if node.module_path in self.nodes:
            LOGGER.warning(None)
            return

        self.nodes[node.module_path] = node
        LOGGER.debug(f"Added node: {node.module_path} (type: {node.node_type})")

    def xǁRhizomeConnectorǁadd_node__mutmut_3(self, node: RhizomaticNode) -> None:
        """Add a node to the rhizome."""
        if node.module_path in self.nodes:
            LOGGER.warning(f"Node {node.module_path} already exists, skipping")
            return

        self.nodes[node.module_path] = None
        LOGGER.debug(f"Added node: {node.module_path} (type: {node.node_type})")

    def xǁRhizomeConnectorǁadd_node__mutmut_4(self, node: RhizomaticNode) -> None:
        """Add a node to the rhizome."""
        if node.module_path in self.nodes:
            LOGGER.warning(f"Node {node.module_path} already exists, skipping")
            return

        self.nodes[node.module_path] = node
        LOGGER.debug(None)
    
    xǁRhizomeConnectorǁadd_node__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁadd_node__mutmut_1': xǁRhizomeConnectorǁadd_node__mutmut_1, 
        'xǁRhizomeConnectorǁadd_node__mutmut_2': xǁRhizomeConnectorǁadd_node__mutmut_2, 
        'xǁRhizomeConnectorǁadd_node__mutmut_3': xǁRhizomeConnectorǁadd_node__mutmut_3, 
        'xǁRhizomeConnectorǁadd_node__mutmut_4': xǁRhizomeConnectorǁadd_node__mutmut_4
    }
    
    def add_node(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁadd_node__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁadd_node__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_node.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁadd_node__mutmut_orig)
    xǁRhizomeConnectorǁadd_node__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁadd_node'

    def xǁRhizomeConnectorǁconnect__mutmut_orig(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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

    def xǁRhizomeConnectorǁconnect__mutmut_1(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 2.0,
        metadata: Optional[Dict[str, Any]] = None,
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

    def xǁRhizomeConnectorǁconnect__mutmut_2(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
        if source.module_path in self.nodes:
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

    def xǁRhizomeConnectorǁconnect__mutmut_3(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            self.add_node(None)
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

    def xǁRhizomeConnectorǁconnect__mutmut_4(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
        if target.module_path in self.nodes:
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

    def xǁRhizomeConnectorǁconnect__mutmut_5(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            self.add_node(None)

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

    def xǁRhizomeConnectorǁconnect__mutmut_6(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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

        connection = None

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_7(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            source=None,
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

    def xǁRhizomeConnectorǁconnect__mutmut_8(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            target=None,
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

    def xǁRhizomeConnectorǁconnect__mutmut_9(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            connection_types=None,
            strength=strength,
            metadata=metadata or {},
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_10(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            strength=None,
            metadata=metadata or {},
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_11(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            metadata=None,
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_12(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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

    def xǁRhizomeConnectorǁconnect__mutmut_13(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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

    def xǁRhizomeConnectorǁconnect__mutmut_14(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            strength=strength,
            metadata=metadata or {},
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_15(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            metadata=metadata or {},
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_16(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_17(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            metadata=metadata and {},
        )

        self.connections.append(connection)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_18(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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

        self.connections.append(None)
        LOGGER.debug(
            f"Connected {source.module_path} -> {target.module_path} "
            f"(types: {[ct.value for ct in connection_types]})"
        )
        return connection

    def xǁRhizomeConnectorǁconnect__mutmut_19(
        self,
        source: RhizomaticNode,
        target: RhizomaticNode,
        connection_types: Set[ConnectionType],
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
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
            None
        )
        return connection
    
    xǁRhizomeConnectorǁconnect__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁconnect__mutmut_1': xǁRhizomeConnectorǁconnect__mutmut_1, 
        'xǁRhizomeConnectorǁconnect__mutmut_2': xǁRhizomeConnectorǁconnect__mutmut_2, 
        'xǁRhizomeConnectorǁconnect__mutmut_3': xǁRhizomeConnectorǁconnect__mutmut_3, 
        'xǁRhizomeConnectorǁconnect__mutmut_4': xǁRhizomeConnectorǁconnect__mutmut_4, 
        'xǁRhizomeConnectorǁconnect__mutmut_5': xǁRhizomeConnectorǁconnect__mutmut_5, 
        'xǁRhizomeConnectorǁconnect__mutmut_6': xǁRhizomeConnectorǁconnect__mutmut_6, 
        'xǁRhizomeConnectorǁconnect__mutmut_7': xǁRhizomeConnectorǁconnect__mutmut_7, 
        'xǁRhizomeConnectorǁconnect__mutmut_8': xǁRhizomeConnectorǁconnect__mutmut_8, 
        'xǁRhizomeConnectorǁconnect__mutmut_9': xǁRhizomeConnectorǁconnect__mutmut_9, 
        'xǁRhizomeConnectorǁconnect__mutmut_10': xǁRhizomeConnectorǁconnect__mutmut_10, 
        'xǁRhizomeConnectorǁconnect__mutmut_11': xǁRhizomeConnectorǁconnect__mutmut_11, 
        'xǁRhizomeConnectorǁconnect__mutmut_12': xǁRhizomeConnectorǁconnect__mutmut_12, 
        'xǁRhizomeConnectorǁconnect__mutmut_13': xǁRhizomeConnectorǁconnect__mutmut_13, 
        'xǁRhizomeConnectorǁconnect__mutmut_14': xǁRhizomeConnectorǁconnect__mutmut_14, 
        'xǁRhizomeConnectorǁconnect__mutmut_15': xǁRhizomeConnectorǁconnect__mutmut_15, 
        'xǁRhizomeConnectorǁconnect__mutmut_16': xǁRhizomeConnectorǁconnect__mutmut_16, 
        'xǁRhizomeConnectorǁconnect__mutmut_17': xǁRhizomeConnectorǁconnect__mutmut_17, 
        'xǁRhizomeConnectorǁconnect__mutmut_18': xǁRhizomeConnectorǁconnect__mutmut_18, 
        'xǁRhizomeConnectorǁconnect__mutmut_19': xǁRhizomeConnectorǁconnect__mutmut_19
    }
    
    def connect(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁconnect__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁconnect__mutmut_mutants"), args, kwargs, self)
        return result 
    
    connect.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁconnect__mutmut_orig)
    xǁRhizomeConnectorǁconnect__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁconnect'

    def xǁRhizomeConnectorǁrupture_connection__mutmut_orig(
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_1(
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
        rupture = None

        # Remove the connection
        if connection in self.connections:
            self.connections.remove(connection)

        self.ruptures.append(rupture)
        LOGGER.info(
            f"Ruptured connection {connection.source.module_path} -> "
            f"{connection.target.module_path} (type: {rupture_type.value})"
        )
        return rupture

    def xǁRhizomeConnectorǁrupture_connection__mutmut_2(
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
            connection=None,
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_3(
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
            rupture_type=None,
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_4(
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
            reason=None,
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_5(
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_6(
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_7(
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

    def xǁRhizomeConnectorǁrupture_connection__mutmut_8(
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
        if connection not in self.connections:
            self.connections.remove(connection)

        self.ruptures.append(rupture)
        LOGGER.info(
            f"Ruptured connection {connection.source.module_path} -> "
            f"{connection.target.module_path} (type: {rupture_type.value})"
        )
        return rupture

    def xǁRhizomeConnectorǁrupture_connection__mutmut_9(
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
            self.connections.remove(None)

        self.ruptures.append(rupture)
        LOGGER.info(
            f"Ruptured connection {connection.source.module_path} -> "
            f"{connection.target.module_path} (type: {rupture_type.value})"
        )
        return rupture

    def xǁRhizomeConnectorǁrupture_connection__mutmut_10(
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

        self.ruptures.append(None)
        LOGGER.info(
            f"Ruptured connection {connection.source.module_path} -> "
            f"{connection.target.module_path} (type: {rupture_type.value})"
        )
        return rupture

    def xǁRhizomeConnectorǁrupture_connection__mutmut_11(
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
            None
        )
        return rupture
    
    xǁRhizomeConnectorǁrupture_connection__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁrupture_connection__mutmut_1': xǁRhizomeConnectorǁrupture_connection__mutmut_1, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_2': xǁRhizomeConnectorǁrupture_connection__mutmut_2, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_3': xǁRhizomeConnectorǁrupture_connection__mutmut_3, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_4': xǁRhizomeConnectorǁrupture_connection__mutmut_4, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_5': xǁRhizomeConnectorǁrupture_connection__mutmut_5, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_6': xǁRhizomeConnectorǁrupture_connection__mutmut_6, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_7': xǁRhizomeConnectorǁrupture_connection__mutmut_7, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_8': xǁRhizomeConnectorǁrupture_connection__mutmut_8, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_9': xǁRhizomeConnectorǁrupture_connection__mutmut_9, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_10': xǁRhizomeConnectorǁrupture_connection__mutmut_10, 
        'xǁRhizomeConnectorǁrupture_connection__mutmut_11': xǁRhizomeConnectorǁrupture_connection__mutmut_11
    }
    
    def rupture_connection(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁrupture_connection__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁrupture_connection__mutmut_mutants"), args, kwargs, self)
        return result 
    
    rupture_connection.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁrupture_connection__mutmut_orig)
    xǁRhizomeConnectorǁrupture_connection__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁrupture_connection'

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_orig(self) -> float:
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

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_1(self) -> float:
        """
        Calculate the rhizomaticity score.

        Rhizomaticity = Connections / Max_Possible_Connections

        Where:
        - 0.0 = Tree structure (minimal connections)
        - 1.0 = Fully connected rhizome

        Goal: R > 0.5 (more rhizomatic than tree-like)

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#philosophical-metrics
        """
        num_nodes = None
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

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_2(self) -> float:
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
        if num_nodes < 1:
            return 0.0

        num_connections = len(self.connections)
        max_connections = (num_nodes * (num_nodes - 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_3(self) -> float:
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
        if num_nodes <= 2:
            return 0.0

        num_connections = len(self.connections)
        max_connections = (num_nodes * (num_nodes - 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_4(self) -> float:
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
            return 1.0

        num_connections = len(self.connections)
        max_connections = (num_nodes * (num_nodes - 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_5(self) -> float:
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

        num_connections = None
        max_connections = (num_nodes * (num_nodes - 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_6(self) -> float:
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
        max_connections = None

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_7(self) -> float:
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
        max_connections = (num_nodes * (num_nodes - 1)) * 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_8(self) -> float:
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
        max_connections = (num_nodes / (num_nodes - 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_9(self) -> float:
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
        max_connections = (num_nodes * (num_nodes + 1)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_10(self) -> float:
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
        max_connections = (num_nodes * (num_nodes - 2)) / 2

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_11(self) -> float:
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
        max_connections = (num_nodes * (num_nodes - 1)) / 3

        score = num_connections / max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_12(self) -> float:
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

        score = None

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_13(self) -> float:
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

        score = num_connections * max_connections if max_connections > 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_14(self) -> float:
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

        score = num_connections / max_connections if max_connections >= 0 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_15(self) -> float:
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

        score = num_connections / max_connections if max_connections > 1 else 0.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_16(self) -> float:
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

        score = num_connections / max_connections if max_connections > 0 else 1.0

        LOGGER.debug(
            f"Rhizomaticity: {score:.2%} "
            f"({num_connections} connections / {max_connections:.0f} possible)"
        )
        return score

    def xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_17(self) -> float:
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
            None
        )
        return score
    
    xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_1': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_1, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_2': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_2, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_3': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_3, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_4': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_4, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_5': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_5, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_6': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_6, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_7': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_7, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_8': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_8, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_9': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_9, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_10': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_10, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_11': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_11, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_12': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_12, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_13': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_13, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_14': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_14, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_15': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_15, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_16': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_16, 
        'xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_17': xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_17
    }
    
    def calculate_rhizomaticity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    calculate_rhizomaticity.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_orig)
    xǁRhizomeConnectorǁcalculate_rhizomaticity__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁcalculate_rhizomaticity'

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_orig(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_1(self, min_nodes: int = 4) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_2(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = None

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_3(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = None
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_4(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(None)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_5(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(None)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_6(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = None

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_7(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path not in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_8(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(None)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_9(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(None)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_10(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(None, current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_11(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, None)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_12(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_13(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, )

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path not in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_14(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
            """Depth-first search to find connected components."""
            if node_path in visited:
                return
            visited.add(node_path)
            current_assemblage.add(node_path)

            for neighbor_path in adjacency[node_path]:
                dfs(neighbor_path, current_assemblage)

        # Find connected components (assemblages)
        for node_path in self.nodes:
            if node_path in visited:
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_15(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = None
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_16(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(None, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_17(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, None)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_18(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_19(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, )

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_20(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) > min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_21(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = None
                    assemblages.append(assemblage_nodes)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_22(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(None)

        LOGGER.info(f"Found {len(assemblages)} assemblages (min_nodes={min_nodes})")
        return assemblages

    def xǁRhizomeConnectorǁfind_assemblages__mutmut_23(self, min_nodes: int = 3) -> List[Set[RhizomaticNode]]:
        """
        Find assemblages (clusters of interconnected nodes).

        An assemblage is a temporary collection of heterogeneous elements
        with no essential unity, defined by their capacities.

        Args:
            min_nodes: Minimum nodes to form an assemblage

        Returns:
            List of assemblages (sets of connected nodes)
        """
        assemblages: List[Set[RhizomaticNode]] = []

        # Build adjacency map
        adjacency: Dict[str, Set[str]] = {path: set() for path in self.nodes}
        for conn in self.connections:
            adjacency[conn.source.module_path].add(conn.target.module_path)
            adjacency[conn.target.module_path].add(conn.source.module_path)

        visited: Set[str] = set()

        def dfs(node_path: str, current_assemblage: Set[str]) -> None:
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
                assemblage_paths: Set[str] = set()
                dfs(node_path, assemblage_paths)

                if len(assemblage_paths) >= min_nodes:
                    assemblage_nodes = {self.nodes[path] for path in assemblage_paths}
                    assemblages.append(assemblage_nodes)

        LOGGER.info(None)
        return assemblages
    
    xǁRhizomeConnectorǁfind_assemblages__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁfind_assemblages__mutmut_1': xǁRhizomeConnectorǁfind_assemblages__mutmut_1, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_2': xǁRhizomeConnectorǁfind_assemblages__mutmut_2, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_3': xǁRhizomeConnectorǁfind_assemblages__mutmut_3, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_4': xǁRhizomeConnectorǁfind_assemblages__mutmut_4, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_5': xǁRhizomeConnectorǁfind_assemblages__mutmut_5, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_6': xǁRhizomeConnectorǁfind_assemblages__mutmut_6, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_7': xǁRhizomeConnectorǁfind_assemblages__mutmut_7, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_8': xǁRhizomeConnectorǁfind_assemblages__mutmut_8, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_9': xǁRhizomeConnectorǁfind_assemblages__mutmut_9, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_10': xǁRhizomeConnectorǁfind_assemblages__mutmut_10, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_11': xǁRhizomeConnectorǁfind_assemblages__mutmut_11, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_12': xǁRhizomeConnectorǁfind_assemblages__mutmut_12, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_13': xǁRhizomeConnectorǁfind_assemblages__mutmut_13, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_14': xǁRhizomeConnectorǁfind_assemblages__mutmut_14, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_15': xǁRhizomeConnectorǁfind_assemblages__mutmut_15, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_16': xǁRhizomeConnectorǁfind_assemblages__mutmut_16, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_17': xǁRhizomeConnectorǁfind_assemblages__mutmut_17, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_18': xǁRhizomeConnectorǁfind_assemblages__mutmut_18, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_19': xǁRhizomeConnectorǁfind_assemblages__mutmut_19, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_20': xǁRhizomeConnectorǁfind_assemblages__mutmut_20, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_21': xǁRhizomeConnectorǁfind_assemblages__mutmut_21, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_22': xǁRhizomeConnectorǁfind_assemblages__mutmut_22, 
        'xǁRhizomeConnectorǁfind_assemblages__mutmut_23': xǁRhizomeConnectorǁfind_assemblages__mutmut_23
    }
    
    def find_assemblages(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁfind_assemblages__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁfind_assemblages__mutmut_mutants"), args, kwargs, self)
        return result 
    
    find_assemblages.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁfind_assemblages__mutmut_orig)
    xǁRhizomeConnectorǁfind_assemblages__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁfind_assemblages'

    def xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_orig(self) -> Dict[Tuple[str, str], float]:
        """
        Get a matrix of connection strengths between nodes.

        Returns:
            Dictionary mapping (source_path, target_path) to strength
        """
        matrix: Dict[Tuple[str, str], float] = {}

        for conn in self.connections:
            key = (conn.source.module_path, conn.target.module_path)
            matrix[key] = conn.strength

        return matrix

    def xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_1(self) -> Dict[Tuple[str, str], float]:
        """
        Get a matrix of connection strengths between nodes.

        Returns:
            Dictionary mapping (source_path, target_path) to strength
        """
        matrix: Dict[Tuple[str, str], float] = None

        for conn in self.connections:
            key = (conn.source.module_path, conn.target.module_path)
            matrix[key] = conn.strength

        return matrix

    def xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_2(self) -> Dict[Tuple[str, str], float]:
        """
        Get a matrix of connection strengths between nodes.

        Returns:
            Dictionary mapping (source_path, target_path) to strength
        """
        matrix: Dict[Tuple[str, str], float] = {}

        for conn in self.connections:
            key = None
            matrix[key] = conn.strength

        return matrix

    def xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_3(self) -> Dict[Tuple[str, str], float]:
        """
        Get a matrix of connection strengths between nodes.

        Returns:
            Dictionary mapping (source_path, target_path) to strength
        """
        matrix: Dict[Tuple[str, str], float] = {}

        for conn in self.connections:
            key = (conn.source.module_path, conn.target.module_path)
            matrix[key] = None

        return matrix
    
    xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_1': xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_1, 
        'xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_2': xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_2, 
        'xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_3': xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_3
    }
    
    def get_connection_strength_matrix(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_connection_strength_matrix.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_orig)
    xǁRhizomeConnectorǁget_connection_strength_matrix__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁget_connection_strength_matrix'

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_orig(self) -> Dict[str, Any]:
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_1(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = None

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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_2(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "XXidXX": node.module_path,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_3(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "ID": node.module_path,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_4(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "id": node.module_path,
                "XXtypeXX": node.node_type,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_5(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "id": node.module_path,
                "TYPE": node.node_type,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_6(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "id": node.module_path,
                "type": node.node_type,
                "XXactiveXX": node.active,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_7(self) -> Dict[str, Any]:
        """
        Export rhizome data for visualization.

        Returns:
            Dictionary with nodes, edges, and metrics
        """
        nodes_data = [
            {
                "id": node.module_path,
                "type": node.node_type,
                "ACTIVE": node.active,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_8(self) -> Dict[str, Any]:
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
                "XXcreated_atXX": node.created_at.isoformat(),
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_9(self) -> Dict[str, Any]:
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
                "CREATED_AT": node.created_at.isoformat(),
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_10(self) -> Dict[str, Any]:
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

        edges_data = None

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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_11(self) -> Dict[str, Any]:
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
                "XXsourceXX": conn.source.module_path,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_12(self) -> Dict[str, Any]:
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
                "SOURCE": conn.source.module_path,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_13(self) -> Dict[str, Any]:
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
                "XXtargetXX": conn.target.module_path,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_14(self) -> Dict[str, Any]:
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
                "TARGET": conn.target.module_path,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_15(self) -> Dict[str, Any]:
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
                "XXtypesXX": [ct.value for ct in conn.connection_types],
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_16(self) -> Dict[str, Any]:
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
                "TYPES": [ct.value for ct in conn.connection_types],
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_17(self) -> Dict[str, Any]:
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
                "XXstrengthXX": conn.strength,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_18(self) -> Dict[str, Any]:
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
                "STRENGTH": conn.strength,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_19(self) -> Dict[str, Any]:
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
                "XXuse_countXX": conn.use_count,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_20(self) -> Dict[str, Any]:
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
                "USE_COUNT": conn.use_count,
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

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_21(self) -> Dict[str, Any]:
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
            "XXnodesXX": nodes_data,
            "edges": edges_data,
            "metrics": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_22(self) -> Dict[str, Any]:
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
            "NODES": nodes_data,
            "edges": edges_data,
            "metrics": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_23(self) -> Dict[str, Any]:
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
            "XXedgesXX": edges_data,
            "metrics": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_24(self) -> Dict[str, Any]:
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
            "EDGES": edges_data,
            "metrics": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_25(self) -> Dict[str, Any]:
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
            "XXmetricsXX": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_26(self) -> Dict[str, Any]:
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
            "METRICS": {
                "rhizomaticity": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_27(self) -> Dict[str, Any]:
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
                "XXrhizomaticityXX": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_28(self) -> Dict[str, Any]:
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
                "RHIZOMATICITY": self.calculate_rhizomaticity(),
                "num_nodes": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_29(self) -> Dict[str, Any]:
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
                "XXnum_nodesXX": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_30(self) -> Dict[str, Any]:
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
                "NUM_NODES": len(self.nodes),
                "num_connections": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_31(self) -> Dict[str, Any]:
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
                "XXnum_connectionsXX": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_32(self) -> Dict[str, Any]:
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
                "NUM_CONNECTIONS": len(self.connections),
                "num_ruptures": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_33(self) -> Dict[str, Any]:
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
                "XXnum_rupturesXX": len(self.ruptures),
            },
        }

    def xǁRhizomeConnectorǁexport_graph_data__mutmut_34(self) -> Dict[str, Any]:
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
                "NUM_RUPTURES": len(self.ruptures),
            },
        }
    
    xǁRhizomeConnectorǁexport_graph_data__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁexport_graph_data__mutmut_1': xǁRhizomeConnectorǁexport_graph_data__mutmut_1, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_2': xǁRhizomeConnectorǁexport_graph_data__mutmut_2, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_3': xǁRhizomeConnectorǁexport_graph_data__mutmut_3, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_4': xǁRhizomeConnectorǁexport_graph_data__mutmut_4, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_5': xǁRhizomeConnectorǁexport_graph_data__mutmut_5, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_6': xǁRhizomeConnectorǁexport_graph_data__mutmut_6, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_7': xǁRhizomeConnectorǁexport_graph_data__mutmut_7, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_8': xǁRhizomeConnectorǁexport_graph_data__mutmut_8, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_9': xǁRhizomeConnectorǁexport_graph_data__mutmut_9, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_10': xǁRhizomeConnectorǁexport_graph_data__mutmut_10, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_11': xǁRhizomeConnectorǁexport_graph_data__mutmut_11, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_12': xǁRhizomeConnectorǁexport_graph_data__mutmut_12, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_13': xǁRhizomeConnectorǁexport_graph_data__mutmut_13, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_14': xǁRhizomeConnectorǁexport_graph_data__mutmut_14, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_15': xǁRhizomeConnectorǁexport_graph_data__mutmut_15, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_16': xǁRhizomeConnectorǁexport_graph_data__mutmut_16, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_17': xǁRhizomeConnectorǁexport_graph_data__mutmut_17, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_18': xǁRhizomeConnectorǁexport_graph_data__mutmut_18, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_19': xǁRhizomeConnectorǁexport_graph_data__mutmut_19, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_20': xǁRhizomeConnectorǁexport_graph_data__mutmut_20, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_21': xǁRhizomeConnectorǁexport_graph_data__mutmut_21, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_22': xǁRhizomeConnectorǁexport_graph_data__mutmut_22, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_23': xǁRhizomeConnectorǁexport_graph_data__mutmut_23, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_24': xǁRhizomeConnectorǁexport_graph_data__mutmut_24, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_25': xǁRhizomeConnectorǁexport_graph_data__mutmut_25, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_26': xǁRhizomeConnectorǁexport_graph_data__mutmut_26, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_27': xǁRhizomeConnectorǁexport_graph_data__mutmut_27, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_28': xǁRhizomeConnectorǁexport_graph_data__mutmut_28, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_29': xǁRhizomeConnectorǁexport_graph_data__mutmut_29, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_30': xǁRhizomeConnectorǁexport_graph_data__mutmut_30, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_31': xǁRhizomeConnectorǁexport_graph_data__mutmut_31, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_32': xǁRhizomeConnectorǁexport_graph_data__mutmut_32, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_33': xǁRhizomeConnectorǁexport_graph_data__mutmut_33, 
        'xǁRhizomeConnectorǁexport_graph_data__mutmut_34': xǁRhizomeConnectorǁexport_graph_data__mutmut_34
    }
    
    def export_graph_data(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁexport_graph_data__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁexport_graph_data__mutmut_mutants"), args, kwargs, self)
        return result 
    
    export_graph_data.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁexport_graph_data__mutmut_orig)
    xǁRhizomeConnectorǁexport_graph_data__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁexport_graph_data'

    def xǁRhizomeConnectorǁget_stats__mutmut_orig(self) -> Dict[str, Any]:
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

    def xǁRhizomeConnectorǁget_stats__mutmut_1(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "XXnodesXX": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_2(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "NODES": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_3(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "XXconnectionsXX": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_4(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "CONNECTIONS": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_5(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "XXrupturesXX": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_6(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "RUPTURES": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_7(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "XXrhizomaticityXX": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_8(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "RHIZOMATICITY": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_9(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "XXavg_connections_per_nodeXX": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_10(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "AVG_CONNECTIONS_PER_NODE": (
                len(self.connections) / len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_11(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) * len(self.nodes) if self.nodes else 0.0
            ),
        }

    def xǁRhizomeConnectorǁget_stats__mutmut_12(self) -> Dict[str, Any]:
        """Get statistics about the rhizome."""
        return {
            "nodes": len(self.nodes),
            "connections": len(self.connections),
            "ruptures": len(self.ruptures),
            "rhizomaticity": self.calculate_rhizomaticity(),
            "avg_connections_per_node": (
                len(self.connections) / len(self.nodes) if self.nodes else 1.0
            ),
        }
    
    xǁRhizomeConnectorǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRhizomeConnectorǁget_stats__mutmut_1': xǁRhizomeConnectorǁget_stats__mutmut_1, 
        'xǁRhizomeConnectorǁget_stats__mutmut_2': xǁRhizomeConnectorǁget_stats__mutmut_2, 
        'xǁRhizomeConnectorǁget_stats__mutmut_3': xǁRhizomeConnectorǁget_stats__mutmut_3, 
        'xǁRhizomeConnectorǁget_stats__mutmut_4': xǁRhizomeConnectorǁget_stats__mutmut_4, 
        'xǁRhizomeConnectorǁget_stats__mutmut_5': xǁRhizomeConnectorǁget_stats__mutmut_5, 
        'xǁRhizomeConnectorǁget_stats__mutmut_6': xǁRhizomeConnectorǁget_stats__mutmut_6, 
        'xǁRhizomeConnectorǁget_stats__mutmut_7': xǁRhizomeConnectorǁget_stats__mutmut_7, 
        'xǁRhizomeConnectorǁget_stats__mutmut_8': xǁRhizomeConnectorǁget_stats__mutmut_8, 
        'xǁRhizomeConnectorǁget_stats__mutmut_9': xǁRhizomeConnectorǁget_stats__mutmut_9, 
        'xǁRhizomeConnectorǁget_stats__mutmut_10': xǁRhizomeConnectorǁget_stats__mutmut_10, 
        'xǁRhizomeConnectorǁget_stats__mutmut_11': xǁRhizomeConnectorǁget_stats__mutmut_11, 
        'xǁRhizomeConnectorǁget_stats__mutmut_12': xǁRhizomeConnectorǁget_stats__mutmut_12
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRhizomeConnectorǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁRhizomeConnectorǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁRhizomeConnectorǁget_stats__mutmut_orig)
    xǁRhizomeConnectorǁget_stats__mutmut_orig.__name__ = 'xǁRhizomeConnectorǁget_stats'
