"""
Assemblage Mapper for AI Agents

Implements Deleuzian assemblage theory for mapping and coordinating AI agents.

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#assemblage-theory
Philosophical Foundation: Deleuze & Guattari - A Thousand Plateaus (1980)

Core Concepts:
- Assemblage: Temporary collection of heterogeneous elements
- No essential unity, defined by capacities (what it can do)
- Relations of exteriority (parts can exist independently)
- Territorialization and deterritorialization processes

An assemblage of agents is:
- NOT a fixed team structure
- NOT a hierarchical organization
- BUT a temporary configuration based on current capacities and needs
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Capabilities that agents can possess."""

    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MENTORING = "mentoring"


class AssemblageState(Enum):
    """States of an assemblage."""

    FORMING = "forming"  # Coming together
    ACTIVE = "active"  # Actively working
    DISSOLVING = "dissolving"  # Breaking apart
    DISSOLVED = "dissolved"  # No longer exists


@dataclass
class Agent:
    """
    An AI agent with capabilities.

    Following Deleuze: defined by what it can do (capacities), not by essence.
    """

    agent_id: str
    agent_type: str  # e.g., "github_copilot", "custom_agent", "ci_bot"
    capabilities: set[AgentCapability]
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.agent_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Agent):
            return False
        return self.agent_id == other.agent_id

    def can_perform(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities


@dataclass
class Assemblage:
    """
    An assemblage of agents working together.

    Following Deleuze:
    - Temporary configuration (not permanent team)
    - Defined by collective capacities
    - Parts maintain independence (relations of exteriority)
    - Can be territorialized (stable) or deterritorialized (fluid)
    """

    assemblage_id: str
    agents: set[Agent]
    purpose: str
    state: AssemblageState = AssemblageState.FORMING
    territorialization: float = 0.5  # 0.0 (fluid) to 1.0 (rigid)
    formed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dissolved_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_collective_capabilities(self) -> set[AgentCapability]:
        """Get all capabilities available in this assemblage."""
        capabilities: set[AgentCapability] = set()
        for agent in self.agents:
            capabilities.update(agent.capabilities)
        return capabilities

    def can_accomplish(self, required_capabilities: set[AgentCapability]) -> bool:
        """Check if assemblage has all required capabilities."""
        collective = self.get_collective_capabilities()
        return required_capabilities.issubset(collective)

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the assemblage."""
        self.agents.add(agent)
        LOGGER.debug(f"Added agent {agent.agent_id} to assemblage {self.assemblage_id}")

    def remove_agent(self, agent: Agent) -> None:
        """Remove an agent from the assemblage."""
        self.agents.discard(agent)
        LOGGER.debug(f"Removed agent {agent.agent_id} from assemblage {self.assemblage_id}")

    def territorialize(self, amount: float) -> None:
        """
        Increase territorialization (make more stable/rigid).

        Args:
            amount: Amount to increase (0.0 to 1.0)
        """
        self.territorialization = min(1.0, self.territorialization + amount)
        LOGGER.debug(
            f"Assemblage {self.assemblage_id} territorialized to {self.territorialization:.2%}"
        )

    def deterritorialize(self, amount: float) -> None:
        """
        Decrease territorialization (make more fluid/flexible).

        Args:
            amount: Amount to decrease (0.0 to 1.0)
        """
        self.territorialization = max(0.0, self.territorialization - amount)
        LOGGER.debug(
            f"Assemblage {self.assemblage_id} deterritorialized to {self.territorialization:.2%}"
        )


class AssemblageMapper:
    """
    Maps and coordinates assemblages of AI agents.

    Implements Deleuzian assemblage theory for dynamic agent coordination.

    Example:
        >>> mapper = AssemblageMapper()
        >>> agent1 = Agent("copilot-1", "github_copilot", {AgentCapability.CODE_GENERATION})
        >>> agent2 = Agent("reviewer-1", "code_reviewer", {AgentCapability.CODE_REVIEW})
        >>> mapper.register_agent(agent1)
        >>> mapper.register_agent(agent2)
        >>> assemblage = mapper.form_assemblage(
        ...     "review_task",
        ...     {AgentCapability.CODE_GENERATION, AgentCapability.CODE_REVIEW},
        ...     purpose="Review generated code"
        ... )
        >>> logger.info(f"Assemblage has {len(assemblage.agents)} agents")
    """

    def __init__(self) -> None:
        self.agents: dict[str, Agent] = {}
        self.assemblages: dict[str, Assemblage] = {}
        self.assemblage_history: list[Assemblage] = []
        LOGGER.info("AssemblageMapper initialized")

    def register_agent(self, agent: Agent) -> None:
        """Register an agent in the mapper."""
        self.agents[agent.agent_id] = agent
        LOGGER.info(
            f"Registered agent {agent.agent_id} with capabilities: "
            f"{[c.value for c in agent.capabilities]}"
        )

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.active = False
            del self.agents[agent_id]
            LOGGER.info(f"Unregistered agent {agent_id}")

    def find_agents_with_capability(self, capability: AgentCapability) -> list[Agent]:
        """Find all agents with a specific capability."""
        return [
            agent
            for agent in self.agents.values()
            if agent.active and agent.can_perform(capability)
        ]

    def form_assemblage(
        self,
        assemblage_id: str,
        required_capabilities: set[AgentCapability],
        purpose: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Assemblage]:
        """
        Form an assemblage with agents that collectively have required capabilities.

        Args:
            assemblage_id: Unique identifier for assemblage
            required_capabilities: Set of required capabilities
            purpose: Purpose of the assemblage
            metadata: Optional metadata

        Returns:
            Formed assemblage, or None if capabilities cannot be met
        """
        # Find agents that can contribute
        selected_agents: set[Agent] = set()
        covered_capabilities: set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(f"No agents available with capability {capability.value}")
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents")

        return assemblage

    def activate_assemblage(self, assemblage_id: str) -> None:
        """Activate an assemblage for work."""
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.ACTIVE
            LOGGER.info(f"Activated assemblage {assemblage_id}")

    def dissolve_assemblage(self, assemblage_id: str) -> None:
        """
        Dissolve an assemblage.

        Following Deleuze: assemblages are temporary. When purpose is complete,
        they dissolve and agents return to independent existence.
        """
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.DISSOLVED
            assemblage.dissolved_at = datetime.now(timezone.utc)

            # Move to history
            self.assemblage_history.append(assemblage)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def get_active_assemblages(self) -> list[Assemblage]:
        """Get all active assemblages."""
        return [a for a in self.assemblages.values() if a.state == AssemblageState.ACTIVE]

    def get_agent_assemblages(self, agent_id: str) -> list[Assemblage]:
        """Get all assemblages that include a specific agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return []

        return [
            assemblage for assemblage in self.assemblages.values() if agent in assemblage.agents
        ]

    def calculate_assemblage_capacity(self, assemblage: Assemblage) -> float:
        """
        Calculate the capacity score of an assemblage.

        Capacity = (Active Agents × Avg Capabilities) × (1 - Territorialization)

        Higher scores indicate more capable and flexible assemblages.

        Args:
            assemblage: The assemblage to evaluate

        Returns:
            Capacity score
        """
        active_agents = sum(1 for agent in assemblage.agents if agent.active)
        if active_agents == 0:
            return 0.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        return active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)

    def optimize_assemblage(
        self, assemblage_id: str, target_capabilities: set[AgentCapability]
    ) -> None:
        """
        Optimize an assemblage by adding/removing agents.

        This is a form of deterritorialization - breaking the fixed structure
        to better meet new needs.

        Args:
            assemblage_id: ID of assemblage to optimize
            target_capabilities: Desired capabilities
        """
        if assemblage_id not in self.assemblages:
            LOGGER.warning(f"Assemblage {assemblage_id} not found")
            return

        assemblage = self.assemblages[assemblage_id]

        # Check if we need additional capabilities
        current_caps = assemblage.get_collective_capabilities()
        missing_caps = target_capabilities - current_caps

        if missing_caps:
            # Add agents with missing capabilities
            for cap in missing_caps:
                agents = self.find_agents_with_capability(cap)
                if agents and agents[0] not in assemblage.agents:
                    assemblage.add_agent(agents[0])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def export_assemblage_map(self) -> dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "id": agent.agent_id,
                "type": agent.agent_type,
                "capabilities": [c.value for c in agent.capabilities],
                "active": agent.active,
            }
            for agent in self.agents.values()
        ]

        assemblages_data = [
            {
                "id": assemblage.assemblage_id,
                "purpose": assemblage.purpose,
                "state": assemblage.state.value,
                "territorialization": assemblage.territorialization,
                "agents": [a.agent_id for a in assemblage.agents],
                "capabilities": [c.value for c in assemblage.get_collective_capabilities()],
                "capacity": self.calculate_assemblage_capacity(assemblage),
            }
            for assemblage in self.assemblages.values()
        ]

        return {
            "agents": agents_data,
            "assemblages": assemblages_data,
            "stats": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }
