"""
Network Topology Management for Multi-Agent Systems.

This module implements dynamic network topology management for multi-agent
quantum systems, supporting various topologies including star, mesh, ring,
and hybrid configurations.

PDA Loop Tags: [INIT] Topology management framework
AfterMath Tags: Phase 8.2 - Multi-Agent Orchestration
"""

import logging
from enum import Enum
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class NetworkTopology(Enum):
    """Supported network topology types."""

    STAR = "star"
    MESH = "mesh"
    RING = "ring"
    HYBRID = "hybrid"


class TopologyManager:
    """
    Manages network topology for multi-agent quantum systems.

    This class provides functionality for configuring, optimizing, and
    managing network topologies that connect multiple quantum agents.
    It supports dynamic reconfiguration based on correlation thresholds.

    PDA Loop: [MANAGE] Network topology and agent connections
    AfterMath: Enables efficient multi-agent communication patterns

    Attributes:
        topology_type: Current network topology configuration
        num_agents: Number of agents in the network
        adjacency_matrix: Matrix representing agent connections
        agent_ids: List of agent identifiers
    """

    def __init__(self):
        """
        Initialize the topology manager.

        PDA Loop: [INIT] Create empty topology manager
        """
        self.topology_type: Optional[NetworkTopology] = None
        self.num_agents: int = 0
        self.adjacency_matrix: Optional[np.ndarray] = None
        self.agent_ids: list[str] = []
        self.correlation_matrix: Optional[np.ndarray] = None

        logger.info("TopologyManager initialized")

    def configure_topology(
        self,
        topology_type: NetworkTopology,
        num_agents: int,
        agent_ids: Optional[list[str]] = None,
    ) -> np.ndarray:
        """
        Configure the network topology.

        Creates an adjacency matrix representing the connections between
        agents based on the specified topology type.

        Args:
            topology_type: Type of network topology to create
            num_agents: Number of agents in the network
            agent_ids: Optional list of agent IDs (generated if not provided)

        Returns:
            Adjacency matrix (num_agents x num_agents)

        Raises:
            ValueError: If num_agents < 2 or invalid topology type

        PDA Loop: [CONFIG] Create topology adjacency matrix
        AfterMath: Network structure configured for agent communication
        """
        if num_agents < 2:
            raise ValueError(f"Need at least 2 agents, got {num_agents}")

        self.topology_type = topology_type
        self.num_agents = num_agents

        # Generate agent IDs if not provided
        if agent_ids is None:
            self.agent_ids = [f"agent_{i}" for i in range(num_agents)]
        else:
            if len(agent_ids) != num_agents:
                raise ValueError(
                    f"Length of agent_ids ({len(agent_ids)}) must match num_agents ({num_agents})"
                )
            self.agent_ids = agent_ids.copy()

        # Create adjacency matrix based on topology type
        if topology_type == NetworkTopology.STAR:
            self.adjacency_matrix = self._create_star_topology(num_agents)
        elif topology_type == NetworkTopology.MESH:
            self.adjacency_matrix = self._create_mesh_topology(num_agents)
        elif topology_type == NetworkTopology.RING:
            self.adjacency_matrix = self._create_ring_topology(num_agents)
        elif topology_type == NetworkTopology.HYBRID:
            self.adjacency_matrix = self._create_hybrid_topology(num_agents)
        else:
            raise ValueError(f"Unknown topology type: {topology_type}")

        # Initialize correlation matrix
        self.correlation_matrix = np.zeros((num_agents, num_agents))

        logger.info(f"Configured {topology_type.value} topology with {num_agents} agents")
        return self.adjacency_matrix.copy()

    def _create_star_topology(self, num_agents: int) -> np.ndarray:
        """
        Create a star topology with a central hub.

        In a star topology, all agents connect to a central hub (agent 0).

        Args:
            num_agents: Number of agents

        Returns:
            Adjacency matrix for star topology

        PDA Loop: [CREATE] Star topology pattern
        """
        adj = np.zeros((num_agents, num_agents))

        # Connect all agents to the hub (agent 0)
        for i in range(1, num_agents):
            adj[0, i] = 1
            adj[i, 0] = 1  # Bidirectional

        return adj

    def _create_mesh_topology(self, num_agents: int) -> np.ndarray:
        """
        Create a full mesh topology.

        In a mesh topology, every agent is connected to every other agent.

        Args:
            num_agents: Number of agents

        Returns:
            Adjacency matrix for mesh topology

        PDA Loop: [CREATE] Full mesh topology pattern
        """
        adj = np.ones((num_agents, num_agents))

        # Remove self-connections
        np.fill_diagonal(adj, 0)

        return adj

    def _create_ring_topology(self, num_agents: int) -> np.ndarray:
        """
        Create a ring topology.

        In a ring topology, agents are connected in a circle, where each
        agent connects to its two neighbors.

        Args:
            num_agents: Number of agents

        Returns:
            Adjacency matrix for ring topology

        PDA Loop: [CREATE] Ring topology pattern
        """
        adj = np.zeros((num_agents, num_agents))

        # Connect each agent to its neighbors in the ring
        for i in range(num_agents):
            next_agent = (i + 1) % num_agents
            adj[i, next_agent] = 1
            adj[next_agent, i] = 1  # Bidirectional

        return adj

    def _create_hybrid_topology(self, num_agents: int) -> np.ndarray:
        """
        Create a hybrid topology combining star and ring.

        First half of agents form a star, second half form a ring,
        with connections between the groups.

        Args:
            num_agents: Number of agents

        Returns:
            Adjacency matrix for hybrid topology

        PDA Loop: [CREATE] Hybrid topology pattern
        """
        adj = np.zeros((num_agents, num_agents))

        # Split agents into two groups
        mid = num_agents // 2

        # First group: star topology (hub at index 0)
        for i in range(1, mid):
            adj[0, i] = 1
            adj[i, 0] = 1

        # Second group: ring topology
        for i in range(mid, num_agents):
            next_agent = mid + ((i - mid + 1) % (num_agents - mid))
            adj[i, next_agent] = 1
            adj[next_agent, i] = 1

        # Connect the groups (hub to first ring agent)
        if num_agents > mid:
            adj[0, mid] = 1
            adj[mid, 0] = 1

        return adj

    def get_neighbors(self, agent_id: str) -> list[str]:
        """
        Get the list of neighboring agents for a given agent.

        Args:
            agent_id: ID of the agent

        Returns:
            List of neighboring agent IDs

        Raises:
            ValueError: If agent_id is not in the topology
            ValueError: If topology has not been configured

        PDA Loop: [QUERY] Find agent neighbors in topology
        """
        if self.adjacency_matrix is None:
            raise ValueError("Topology has not been configured")

        if agent_id not in self.agent_ids:
            raise ValueError(f"Agent {agent_id} not found in topology")

        agent_idx = self.agent_ids.index(agent_id)
        neighbor_indices = np.where(self.adjacency_matrix[agent_idx] == 1)[0]

        return [self.agent_ids[idx] for idx in neighbor_indices]

    def update_correlation(self, agent1_id: str, agent2_id: str, correlation: float) -> None:
        """
        Update the correlation value between two agents.

        Args:
            agent1_id: ID of first agent
            agent2_id: ID of second agent
            correlation: Correlation value (should be in [-1, 1])

        Raises:
            ValueError: If agent IDs are invalid or topology not configured

        PDA Loop: [UPDATE] Record agent correlation measurement
        """
        if self.correlation_matrix is None:
            raise ValueError("Topology has not been configured")

        if agent1_id not in self.agent_ids:
            raise ValueError(f"Agent {agent1_id} not found in topology")
        if agent2_id not in self.agent_ids:
            raise ValueError(f"Agent {agent2_id} not found in topology")

        if not -1.0 <= correlation <= 1.0:
            logger.warning(f"Correlation {correlation} outside expected range [-1, 1], clamping")
            correlation = max(-1.0, min(1.0, correlation))

        idx1 = self.agent_ids.index(agent1_id)
        idx2 = self.agent_ids.index(agent2_id)

        # Update correlation matrix (symmetric)
        self.correlation_matrix[idx1, idx2] = correlation
        self.correlation_matrix[idx2, idx1] = correlation

        logger.debug(f"Updated correlation between {agent1_id} and {agent2_id}: {correlation:.3f}")

    def optimize_topology(self, correlation_threshold: float = 0.75) -> int:
        """
        Optimize topology based on correlation measurements.

        Adjusts connections to maintain high-correlation links and prune
        low-correlation links. This enables dynamic topology adaptation.

        Args:
            correlation_threshold: Minimum correlation to maintain connection

        Returns:
            Number of connections modified

        Raises:
            ValueError: If topology or correlations not configured

        PDA Loop: [OPTIMIZE] Adapt topology based on correlations
        AfterMath: Network optimized for high-correlation agent pairs
        """
        if self.adjacency_matrix is None or self.correlation_matrix is None:
            raise ValueError("Topology and correlations must be configured first")

        modifications = 0
        n = self.num_agents

        # Create a new adjacency matrix
        new_adj = self.adjacency_matrix.copy()

        # Check each pair of agents
        for i in range(n):
            for j in range(i + 1, n):
                current_connection = self.adjacency_matrix[i, j]
                correlation = abs(self.correlation_matrix[i, j])  # Use absolute value

                # If correlation is measured and differs from threshold
                if correlation > 0:  # Only optimize if we have correlation data
                    should_connect = correlation >= correlation_threshold

                    if should_connect and current_connection == 0:
                        # Add connection for high correlation
                        new_adj[i, j] = 1
                        new_adj[j, i] = 1
                        modifications += 1
                        logger.debug(
                            f"Added connection between {self.agent_ids[i]} and "
                            f"{self.agent_ids[j]} (correlation: {correlation:.3f})"
                        )
                    elif not should_connect and current_connection == 1:
                        # Remove connection for low correlation
                        # But preserve minimum connectivity (don't isolate agents)
                        if np.sum(new_adj[i]) > 1 and np.sum(new_adj[j]) > 1:
                            new_adj[i, j] = 0
                            new_adj[j, i] = 0
                            modifications += 1
                            logger.debug(
                                f"Removed connection between {self.agent_ids[i]} and "
                                f"{self.agent_ids[j]} (correlation: {correlation:.3f})"
                            )

        # Update the adjacency matrix
        self.adjacency_matrix = new_adj

        logger.info(
            f"Topology optimization complete: {modifications} connections modified "
            f"(threshold: {correlation_threshold})"
        )
        return modifications

    def get_topology_statistics(self) -> dict[str, Any]:
        """
        Get statistics about the current topology.

        Returns:
            Dictionary with topology statistics

        PDA Loop: [ANALYZE] Compute topology metrics
        """
        if self.adjacency_matrix is None:
            return {"configured": False}

        total_connections = int(np.sum(self.adjacency_matrix)) // 2  # Divide by 2 for undirected
        max_possible = (self.num_agents * (self.num_agents - 1)) // 2
        density = total_connections / max_possible if max_possible > 0 else 0

        # Calculate average degree
        degrees = np.sum(self.adjacency_matrix, axis=1)
        avg_degree = np.mean(degrees)

        stats = {
            "configured": True,
            "topology_type": self.topology_type.value if self.topology_type else None,
            "num_agents": self.num_agents,
            "total_connections": total_connections,
            "max_possible_connections": max_possible,
            "density": density,
            "average_degree": float(avg_degree),
            "min_degree": int(np.min(degrees)),
            "max_degree": int(np.max(degrees)),
        }

        # Add correlation stats if available
        if self.correlation_matrix is not None:
            correlations = self.correlation_matrix[np.triu_indices(self.num_agents, k=1)]
            measured = correlations[correlations != 0]
            if len(measured) > 0:
                stats["avg_correlation"] = float(np.mean(np.abs(measured)))
                stats["max_correlation"] = float(np.max(np.abs(measured)))
                stats["min_correlation"] = float(np.min(np.abs(measured)))
                stats["measured_correlations"] = len(measured)

        return stats

    def reset_topology(self) -> None:
        """
        Reset the topology configuration.

        PDA Loop: [CLEANUP] Clear topology state
        """
        self.topology_type = None
        self.num_agents = 0
        self.adjacency_matrix = None
        self.agent_ids = []
        self.correlation_matrix = None
        logger.info("Topology reset")
