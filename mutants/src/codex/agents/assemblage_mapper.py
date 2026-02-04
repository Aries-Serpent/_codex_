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
from typing import Any, Dict, List, Optional, Set

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
    capabilities: Set[AgentCapability]
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

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
    agents: Set[Agent]
    purpose: str
    state: AssemblageState = AssemblageState.FORMING
    territorialization: float = 0.5  # 0.0 (fluid) to 1.0 (rigid)
    formed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dissolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_collective_capabilities(self) -> Set[AgentCapability]:
        """Get all capabilities available in this assemblage."""
        capabilities: Set[AgentCapability] = set()
        for agent in self.agents:
            capabilities.update(agent.capabilities)
        return capabilities

    def can_accomplish(self, required_capabilities: Set[AgentCapability]) -> bool:
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
        LOGGER.debug(
            f"Removed agent {agent.agent_id} from assemblage {self.assemblage_id}"
        )

    def territorialize(self, amount: float) -> None:
        """
        Increase territorialization (make more stable/rigid).

        Args:
            amount: Amount to increase (0.0 to 1.0)
        """
        self.territorialization = min(1.0, self.territorialization + amount)
        LOGGER.debug(
            f"Assemblage {self.assemblage_id} territorialized to "
            f"{self.territorialization:.2%}"
        )

    def deterritorialize(self, amount: float) -> None:
        """
        Decrease territorialization (make more fluid/flexible).

        Args:
            amount: Amount to decrease (0.0 to 1.0)
        """
        self.territorialization = max(0.0, self.territorialization - amount)
        LOGGER.debug(
            f"Assemblage {self.assemblage_id} deterritorialized to "
            f"{self.territorialization:.2%}"
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
        >>> print(f"Assemblage has {len(assemblage.agents)} agents")
    """

    def xǁAssemblageMapperǁ__init____mutmut_orig(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info("AssemblageMapper initialized")

    def xǁAssemblageMapperǁ__init____mutmut_1(self) -> None:
        self.agents: Dict[str, Agent] = None
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info("AssemblageMapper initialized")

    def xǁAssemblageMapperǁ__init____mutmut_2(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = None
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info("AssemblageMapper initialized")

    def xǁAssemblageMapperǁ__init____mutmut_3(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = None
        LOGGER.info("AssemblageMapper initialized")

    def xǁAssemblageMapperǁ__init____mutmut_4(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info(None)

    def xǁAssemblageMapperǁ__init____mutmut_5(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info("XXAssemblageMapper initializedXX")

    def xǁAssemblageMapperǁ__init____mutmut_6(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info("assemblagemapper initialized")

    def xǁAssemblageMapperǁ__init____mutmut_7(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.assemblages: Dict[str, Assemblage] = {}
        self.assemblage_history: List[Assemblage] = []
        LOGGER.info("ASSEMBLAGEMAPPER INITIALIZED")
    
    xǁAssemblageMapperǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁ__init____mutmut_1': xǁAssemblageMapperǁ__init____mutmut_1, 
        'xǁAssemblageMapperǁ__init____mutmut_2': xǁAssemblageMapperǁ__init____mutmut_2, 
        'xǁAssemblageMapperǁ__init____mutmut_3': xǁAssemblageMapperǁ__init____mutmut_3, 
        'xǁAssemblageMapperǁ__init____mutmut_4': xǁAssemblageMapperǁ__init____mutmut_4, 
        'xǁAssemblageMapperǁ__init____mutmut_5': xǁAssemblageMapperǁ__init____mutmut_5, 
        'xǁAssemblageMapperǁ__init____mutmut_6': xǁAssemblageMapperǁ__init____mutmut_6, 
        'xǁAssemblageMapperǁ__init____mutmut_7': xǁAssemblageMapperǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAssemblageMapperǁ__init____mutmut_orig)
    xǁAssemblageMapperǁ__init____mutmut_orig.__name__ = 'xǁAssemblageMapperǁ__init__'

    def xǁAssemblageMapperǁregister_agent__mutmut_orig(self, agent: Agent) -> None:
        """Register an agent in the mapper."""
        self.agents[agent.agent_id] = agent
        LOGGER.info(
            f"Registered agent {agent.agent_id} with capabilities: "
            f"{[c.value for c in agent.capabilities]}"
        )

    def xǁAssemblageMapperǁregister_agent__mutmut_1(self, agent: Agent) -> None:
        """Register an agent in the mapper."""
        self.agents[agent.agent_id] = None
        LOGGER.info(
            f"Registered agent {agent.agent_id} with capabilities: "
            f"{[c.value for c in agent.capabilities]}"
        )

    def xǁAssemblageMapperǁregister_agent__mutmut_2(self, agent: Agent) -> None:
        """Register an agent in the mapper."""
        self.agents[agent.agent_id] = agent
        LOGGER.info(
            None
        )
    
    xǁAssemblageMapperǁregister_agent__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁregister_agent__mutmut_1': xǁAssemblageMapperǁregister_agent__mutmut_1, 
        'xǁAssemblageMapperǁregister_agent__mutmut_2': xǁAssemblageMapperǁregister_agent__mutmut_2
    }
    
    def register_agent(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁregister_agent__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁregister_agent__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_agent.__signature__ = _mutmut_signature(xǁAssemblageMapperǁregister_agent__mutmut_orig)
    xǁAssemblageMapperǁregister_agent__mutmut_orig.__name__ = 'xǁAssemblageMapperǁregister_agent'

    def xǁAssemblageMapperǁunregister_agent__mutmut_orig(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.active = False
            del self.agents[agent_id]
            LOGGER.info(f"Unregistered agent {agent_id}")

    def xǁAssemblageMapperǁunregister_agent__mutmut_1(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id not in self.agents:
            agent = self.agents[agent_id]
            agent.active = False
            del self.agents[agent_id]
            LOGGER.info(f"Unregistered agent {agent_id}")

    def xǁAssemblageMapperǁunregister_agent__mutmut_2(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = None
            agent.active = False
            del self.agents[agent_id]
            LOGGER.info(f"Unregistered agent {agent_id}")

    def xǁAssemblageMapperǁunregister_agent__mutmut_3(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.active = None
            del self.agents[agent_id]
            LOGGER.info(f"Unregistered agent {agent_id}")

    def xǁAssemblageMapperǁunregister_agent__mutmut_4(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.active = True
            del self.agents[agent_id]
            LOGGER.info(f"Unregistered agent {agent_id}")

    def xǁAssemblageMapperǁunregister_agent__mutmut_5(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.active = False
            del self.agents[agent_id]
            LOGGER.info(None)
    
    xǁAssemblageMapperǁunregister_agent__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁunregister_agent__mutmut_1': xǁAssemblageMapperǁunregister_agent__mutmut_1, 
        'xǁAssemblageMapperǁunregister_agent__mutmut_2': xǁAssemblageMapperǁunregister_agent__mutmut_2, 
        'xǁAssemblageMapperǁunregister_agent__mutmut_3': xǁAssemblageMapperǁunregister_agent__mutmut_3, 
        'xǁAssemblageMapperǁunregister_agent__mutmut_4': xǁAssemblageMapperǁunregister_agent__mutmut_4, 
        'xǁAssemblageMapperǁunregister_agent__mutmut_5': xǁAssemblageMapperǁunregister_agent__mutmut_5
    }
    
    def unregister_agent(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁunregister_agent__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁunregister_agent__mutmut_mutants"), args, kwargs, self)
        return result 
    
    unregister_agent.__signature__ = _mutmut_signature(xǁAssemblageMapperǁunregister_agent__mutmut_orig)
    xǁAssemblageMapperǁunregister_agent__mutmut_orig.__name__ = 'xǁAssemblageMapperǁunregister_agent'

    def xǁAssemblageMapperǁfind_agents_with_capability__mutmut_orig(
        self, capability: AgentCapability
    ) -> List[Agent]:
        """Find all agents with a specific capability."""
        return [
            agent
            for agent in self.agents.values()
            if agent.active and agent.can_perform(capability)
        ]

    def xǁAssemblageMapperǁfind_agents_with_capability__mutmut_1(
        self, capability: AgentCapability
    ) -> List[Agent]:
        """Find all agents with a specific capability."""
        return [
            agent
            for agent in self.agents.values()
            if agent.active or agent.can_perform(capability)
        ]

    def xǁAssemblageMapperǁfind_agents_with_capability__mutmut_2(
        self, capability: AgentCapability
    ) -> List[Agent]:
        """Find all agents with a specific capability."""
        return [
            agent
            for agent in self.agents.values()
            if agent.active and agent.can_perform(None)
        ]
    
    xǁAssemblageMapperǁfind_agents_with_capability__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁfind_agents_with_capability__mutmut_1': xǁAssemblageMapperǁfind_agents_with_capability__mutmut_1, 
        'xǁAssemblageMapperǁfind_agents_with_capability__mutmut_2': xǁAssemblageMapperǁfind_agents_with_capability__mutmut_2
    }
    
    def find_agents_with_capability(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁfind_agents_with_capability__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁfind_agents_with_capability__mutmut_mutants"), args, kwargs, self)
        return result 
    
    find_agents_with_capability.__signature__ = _mutmut_signature(xǁAssemblageMapperǁfind_agents_with_capability__mutmut_orig)
    xǁAssemblageMapperǁfind_agents_with_capability__mutmut_orig.__name__ = 'xǁAssemblageMapperǁfind_agents_with_capability'

    def xǁAssemblageMapperǁform_assemblage__mutmut_orig(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_1(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = None
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_2(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = None

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_3(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability not in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_4(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                break

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_5(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = None
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_6(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(None)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_7(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_8(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    None
                )
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
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_9(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = None
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_10(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[1]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_11(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(None)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_12(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(None)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_13(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = None

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_14(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=None,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_15(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=None,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_16(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=None,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_17(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=None,
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_18(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_19(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            purpose=purpose,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_20(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            metadata=metadata or {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_21(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_22(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
                return None

            # Add first available agent with this capability
            agent = agents_with_cap[0]
            selected_agents.add(agent)
            covered_capabilities.update(agent.capabilities)

        assemblage = Assemblage(
            assemblage_id=assemblage_id,
            agents=selected_agents,
            purpose=purpose,
            metadata=metadata and {},
        )

        self.assemblages[assemblage_id] = assemblage
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_23(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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

        self.assemblages[assemblage_id] = None
        LOGGER.info(
            f"Formed assemblage {assemblage_id} with {len(selected_agents)} agents"
        )

        return assemblage

    def xǁAssemblageMapperǁform_assemblage__mutmut_24(
        self,
        assemblage_id: str,
        required_capabilities: Set[AgentCapability],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
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
        selected_agents: Set[Agent] = set()
        covered_capabilities: Set[AgentCapability] = set()

        # Greedy selection: add agents until all capabilities are covered
        for capability in required_capabilities:
            if capability in covered_capabilities:
                continue

            agents_with_cap = self.find_agents_with_capability(capability)
            if not agents_with_cap:
                LOGGER.warning(
                    f"No agents available with capability {capability.value}"
                )
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
        LOGGER.info(
            None
        )

        return assemblage
    
    xǁAssemblageMapperǁform_assemblage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁform_assemblage__mutmut_1': xǁAssemblageMapperǁform_assemblage__mutmut_1, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_2': xǁAssemblageMapperǁform_assemblage__mutmut_2, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_3': xǁAssemblageMapperǁform_assemblage__mutmut_3, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_4': xǁAssemblageMapperǁform_assemblage__mutmut_4, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_5': xǁAssemblageMapperǁform_assemblage__mutmut_5, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_6': xǁAssemblageMapperǁform_assemblage__mutmut_6, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_7': xǁAssemblageMapperǁform_assemblage__mutmut_7, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_8': xǁAssemblageMapperǁform_assemblage__mutmut_8, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_9': xǁAssemblageMapperǁform_assemblage__mutmut_9, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_10': xǁAssemblageMapperǁform_assemblage__mutmut_10, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_11': xǁAssemblageMapperǁform_assemblage__mutmut_11, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_12': xǁAssemblageMapperǁform_assemblage__mutmut_12, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_13': xǁAssemblageMapperǁform_assemblage__mutmut_13, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_14': xǁAssemblageMapperǁform_assemblage__mutmut_14, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_15': xǁAssemblageMapperǁform_assemblage__mutmut_15, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_16': xǁAssemblageMapperǁform_assemblage__mutmut_16, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_17': xǁAssemblageMapperǁform_assemblage__mutmut_17, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_18': xǁAssemblageMapperǁform_assemblage__mutmut_18, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_19': xǁAssemblageMapperǁform_assemblage__mutmut_19, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_20': xǁAssemblageMapperǁform_assemblage__mutmut_20, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_21': xǁAssemblageMapperǁform_assemblage__mutmut_21, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_22': xǁAssemblageMapperǁform_assemblage__mutmut_22, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_23': xǁAssemblageMapperǁform_assemblage__mutmut_23, 
        'xǁAssemblageMapperǁform_assemblage__mutmut_24': xǁAssemblageMapperǁform_assemblage__mutmut_24
    }
    
    def form_assemblage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁform_assemblage__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁform_assemblage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    form_assemblage.__signature__ = _mutmut_signature(xǁAssemblageMapperǁform_assemblage__mutmut_orig)
    xǁAssemblageMapperǁform_assemblage__mutmut_orig.__name__ = 'xǁAssemblageMapperǁform_assemblage'

    def xǁAssemblageMapperǁactivate_assemblage__mutmut_orig(self, assemblage_id: str) -> None:
        """Activate an assemblage for work."""
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.ACTIVE
            LOGGER.info(f"Activated assemblage {assemblage_id}")

    def xǁAssemblageMapperǁactivate_assemblage__mutmut_1(self, assemblage_id: str) -> None:
        """Activate an assemblage for work."""
        if assemblage_id not in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.ACTIVE
            LOGGER.info(f"Activated assemblage {assemblage_id}")

    def xǁAssemblageMapperǁactivate_assemblage__mutmut_2(self, assemblage_id: str) -> None:
        """Activate an assemblage for work."""
        if assemblage_id in self.assemblages:
            assemblage = None
            assemblage.state = AssemblageState.ACTIVE
            LOGGER.info(f"Activated assemblage {assemblage_id}")

    def xǁAssemblageMapperǁactivate_assemblage__mutmut_3(self, assemblage_id: str) -> None:
        """Activate an assemblage for work."""
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = None
            LOGGER.info(f"Activated assemblage {assemblage_id}")

    def xǁAssemblageMapperǁactivate_assemblage__mutmut_4(self, assemblage_id: str) -> None:
        """Activate an assemblage for work."""
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.ACTIVE
            LOGGER.info(None)
    
    xǁAssemblageMapperǁactivate_assemblage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁactivate_assemblage__mutmut_1': xǁAssemblageMapperǁactivate_assemblage__mutmut_1, 
        'xǁAssemblageMapperǁactivate_assemblage__mutmut_2': xǁAssemblageMapperǁactivate_assemblage__mutmut_2, 
        'xǁAssemblageMapperǁactivate_assemblage__mutmut_3': xǁAssemblageMapperǁactivate_assemblage__mutmut_3, 
        'xǁAssemblageMapperǁactivate_assemblage__mutmut_4': xǁAssemblageMapperǁactivate_assemblage__mutmut_4
    }
    
    def activate_assemblage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁactivate_assemblage__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁactivate_assemblage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    activate_assemblage.__signature__ = _mutmut_signature(xǁAssemblageMapperǁactivate_assemblage__mutmut_orig)
    xǁAssemblageMapperǁactivate_assemblage__mutmut_orig.__name__ = 'xǁAssemblageMapperǁactivate_assemblage'

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_orig(self, assemblage_id: str) -> None:
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

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_1(self, assemblage_id: str) -> None:
        """
        Dissolve an assemblage.

        Following Deleuze: assemblages are temporary. When purpose is complete,
        they dissolve and agents return to independent existence.
        """
        if assemblage_id not in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.DISSOLVED
            assemblage.dissolved_at = datetime.now(timezone.utc)

            # Move to history
            self.assemblage_history.append(assemblage)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_2(self, assemblage_id: str) -> None:
        """
        Dissolve an assemblage.

        Following Deleuze: assemblages are temporary. When purpose is complete,
        they dissolve and agents return to independent existence.
        """
        if assemblage_id in self.assemblages:
            assemblage = None
            assemblage.state = AssemblageState.DISSOLVED
            assemblage.dissolved_at = datetime.now(timezone.utc)

            # Move to history
            self.assemblage_history.append(assemblage)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_3(self, assemblage_id: str) -> None:
        """
        Dissolve an assemblage.

        Following Deleuze: assemblages are temporary. When purpose is complete,
        they dissolve and agents return to independent existence.
        """
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = None
            assemblage.dissolved_at = datetime.now(timezone.utc)

            # Move to history
            self.assemblage_history.append(assemblage)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_4(self, assemblage_id: str) -> None:
        """
        Dissolve an assemblage.

        Following Deleuze: assemblages are temporary. When purpose is complete,
        they dissolve and agents return to independent existence.
        """
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.DISSOLVED
            assemblage.dissolved_at = None

            # Move to history
            self.assemblage_history.append(assemblage)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_5(self, assemblage_id: str) -> None:
        """
        Dissolve an assemblage.

        Following Deleuze: assemblages are temporary. When purpose is complete,
        they dissolve and agents return to independent existence.
        """
        if assemblage_id in self.assemblages:
            assemblage = self.assemblages[assemblage_id]
            assemblage.state = AssemblageState.DISSOLVED
            assemblage.dissolved_at = datetime.now(None)

            # Move to history
            self.assemblage_history.append(assemblage)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_6(self, assemblage_id: str) -> None:
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
            self.assemblage_history.append(None)
            del self.assemblages[assemblage_id]

            LOGGER.info(f"Dissolved assemblage {assemblage_id}")

    def xǁAssemblageMapperǁdissolve_assemblage__mutmut_7(self, assemblage_id: str) -> None:
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

            LOGGER.info(None)
    
    xǁAssemblageMapperǁdissolve_assemblage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁdissolve_assemblage__mutmut_1': xǁAssemblageMapperǁdissolve_assemblage__mutmut_1, 
        'xǁAssemblageMapperǁdissolve_assemblage__mutmut_2': xǁAssemblageMapperǁdissolve_assemblage__mutmut_2, 
        'xǁAssemblageMapperǁdissolve_assemblage__mutmut_3': xǁAssemblageMapperǁdissolve_assemblage__mutmut_3, 
        'xǁAssemblageMapperǁdissolve_assemblage__mutmut_4': xǁAssemblageMapperǁdissolve_assemblage__mutmut_4, 
        'xǁAssemblageMapperǁdissolve_assemblage__mutmut_5': xǁAssemblageMapperǁdissolve_assemblage__mutmut_5, 
        'xǁAssemblageMapperǁdissolve_assemblage__mutmut_6': xǁAssemblageMapperǁdissolve_assemblage__mutmut_6, 
        'xǁAssemblageMapperǁdissolve_assemblage__mutmut_7': xǁAssemblageMapperǁdissolve_assemblage__mutmut_7
    }
    
    def dissolve_assemblage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁdissolve_assemblage__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁdissolve_assemblage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    dissolve_assemblage.__signature__ = _mutmut_signature(xǁAssemblageMapperǁdissolve_assemblage__mutmut_orig)
    xǁAssemblageMapperǁdissolve_assemblage__mutmut_orig.__name__ = 'xǁAssemblageMapperǁdissolve_assemblage'

    def xǁAssemblageMapperǁget_active_assemblages__mutmut_orig(self) -> List[Assemblage]:
        """Get all active assemblages."""
        return [
            a for a in self.assemblages.values() if a.state == AssemblageState.ACTIVE
        ]

    def xǁAssemblageMapperǁget_active_assemblages__mutmut_1(self) -> List[Assemblage]:
        """Get all active assemblages."""
        return [
            a for a in self.assemblages.values() if a.state != AssemblageState.ACTIVE
        ]
    
    xǁAssemblageMapperǁget_active_assemblages__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁget_active_assemblages__mutmut_1': xǁAssemblageMapperǁget_active_assemblages__mutmut_1
    }
    
    def get_active_assemblages(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁget_active_assemblages__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁget_active_assemblages__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_active_assemblages.__signature__ = _mutmut_signature(xǁAssemblageMapperǁget_active_assemblages__mutmut_orig)
    xǁAssemblageMapperǁget_active_assemblages__mutmut_orig.__name__ = 'xǁAssemblageMapperǁget_active_assemblages'

    def xǁAssemblageMapperǁget_agent_assemblages__mutmut_orig(self, agent_id: str) -> List[Assemblage]:
        """Get all assemblages that include a specific agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return []

        return [
            assemblage
            for assemblage in self.assemblages.values()
            if agent in assemblage.agents
        ]

    def xǁAssemblageMapperǁget_agent_assemblages__mutmut_1(self, agent_id: str) -> List[Assemblage]:
        """Get all assemblages that include a specific agent."""
        agent = None
        if not agent:
            return []

        return [
            assemblage
            for assemblage in self.assemblages.values()
            if agent in assemblage.agents
        ]

    def xǁAssemblageMapperǁget_agent_assemblages__mutmut_2(self, agent_id: str) -> List[Assemblage]:
        """Get all assemblages that include a specific agent."""
        agent = self.agents.get(None)
        if not agent:
            return []

        return [
            assemblage
            for assemblage in self.assemblages.values()
            if agent in assemblage.agents
        ]

    def xǁAssemblageMapperǁget_agent_assemblages__mutmut_3(self, agent_id: str) -> List[Assemblage]:
        """Get all assemblages that include a specific agent."""
        agent = self.agents.get(agent_id)
        if agent:
            return []

        return [
            assemblage
            for assemblage in self.assemblages.values()
            if agent in assemblage.agents
        ]

    def xǁAssemblageMapperǁget_agent_assemblages__mutmut_4(self, agent_id: str) -> List[Assemblage]:
        """Get all assemblages that include a specific agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return []

        return [
            assemblage
            for assemblage in self.assemblages.values()
            if agent not in assemblage.agents
        ]
    
    xǁAssemblageMapperǁget_agent_assemblages__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁget_agent_assemblages__mutmut_1': xǁAssemblageMapperǁget_agent_assemblages__mutmut_1, 
        'xǁAssemblageMapperǁget_agent_assemblages__mutmut_2': xǁAssemblageMapperǁget_agent_assemblages__mutmut_2, 
        'xǁAssemblageMapperǁget_agent_assemblages__mutmut_3': xǁAssemblageMapperǁget_agent_assemblages__mutmut_3, 
        'xǁAssemblageMapperǁget_agent_assemblages__mutmut_4': xǁAssemblageMapperǁget_agent_assemblages__mutmut_4
    }
    
    def get_agent_assemblages(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁget_agent_assemblages__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁget_agent_assemblages__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_agent_assemblages.__signature__ = _mutmut_signature(xǁAssemblageMapperǁget_agent_assemblages__mutmut_orig)
    xǁAssemblageMapperǁget_agent_assemblages__mutmut_orig.__name__ = 'xǁAssemblageMapperǁget_agent_assemblages'

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_orig(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_1(self, assemblage: Assemblage) -> float:
        """
        Calculate the capacity score of an assemblage.

        Capacity = (Active Agents × Avg Capabilities) × (1 - Territorialization)

        Higher scores indicate more capable and flexible assemblages.

        Args:
            assemblage: The assemblage to evaluate

        Returns:
            Capacity score
        """
        active_agents = None
        if active_agents == 0:
            return 0.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_2(self, assemblage: Assemblage) -> float:
        """
        Calculate the capacity score of an assemblage.

        Capacity = (Active Agents × Avg Capabilities) × (1 - Territorialization)

        Higher scores indicate more capable and flexible assemblages.

        Args:
            assemblage: The assemblage to evaluate

        Returns:
            Capacity score
        """
        active_agents = sum(None)
        if active_agents == 0:
            return 0.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_3(self, assemblage: Assemblage) -> float:
        """
        Calculate the capacity score of an assemblage.

        Capacity = (Active Agents × Avg Capabilities) × (1 - Territorialization)

        Higher scores indicate more capable and flexible assemblages.

        Args:
            assemblage: The assemblage to evaluate

        Returns:
            Capacity score
        """
        active_agents = sum(2 for agent in assemblage.agents if agent.active)
        if active_agents == 0:
            return 0.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_4(self, assemblage: Assemblage) -> float:
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
        if active_agents != 0:
            return 0.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_5(self, assemblage: Assemblage) -> float:
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
        if active_agents == 1:
            return 0.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_6(self, assemblage: Assemblage) -> float:
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
            return 1.0

        total_capabilities = sum(len(agent.capabilities) for agent in assemblage.agents)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_7(self, assemblage: Assemblage) -> float:
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

        total_capabilities = None
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_8(self, assemblage: Assemblage) -> float:
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

        total_capabilities = sum(None)
        avg_capabilities = total_capabilities / active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_9(self, assemblage: Assemblage) -> float:
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
        avg_capabilities = None

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_10(self, assemblage: Assemblage) -> float:
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
        avg_capabilities = total_capabilities * active_agents

        # Fluidity factor (less territorialized = more capacity)
        fluidity = 1.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_11(self, assemblage: Assemblage) -> float:
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
        fluidity = None

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_12(self, assemblage: Assemblage) -> float:
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
        fluidity = 1.0 + assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_13(self, assemblage: Assemblage) -> float:
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
        fluidity = 2.0 - assemblage.territorialization

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_14(self, assemblage: Assemblage) -> float:
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

        capacity = None
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_15(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents * avg_capabilities / (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_16(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents / avg_capabilities * (0.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_17(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents * avg_capabilities * (0.5 - 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_18(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents * avg_capabilities * (1.5 + 0.5 * fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_19(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents * avg_capabilities * (0.5 + 0.5 / fluidity)
        return capacity

    def xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_20(self, assemblage: Assemblage) -> float:
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

        capacity = active_agents * avg_capabilities * (0.5 + 1.5 * fluidity)
        return capacity
    
    xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_1': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_1, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_2': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_2, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_3': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_3, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_4': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_4, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_5': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_5, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_6': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_6, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_7': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_7, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_8': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_8, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_9': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_9, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_10': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_10, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_11': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_11, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_12': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_12, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_13': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_13, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_14': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_14, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_15': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_15, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_16': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_16, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_17': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_17, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_18': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_18, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_19': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_19, 
        'xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_20': xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_20
    }
    
    def calculate_assemblage_capacity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    calculate_assemblage_capacity.__signature__ = _mutmut_signature(xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_orig)
    xǁAssemblageMapperǁcalculate_assemblage_capacity__mutmut_orig.__name__ = 'xǁAssemblageMapperǁcalculate_assemblage_capacity'

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_orig(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_1(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
    ) -> None:
        """
        Optimize an assemblage by adding/removing agents.

        This is a form of deterritorialization - breaking the fixed structure
        to better meet new needs.

        Args:
            assemblage_id: ID of assemblage to optimize
            target_capabilities: Desired capabilities
        """
        if assemblage_id in self.assemblages:
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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_2(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
            LOGGER.warning(None)
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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_3(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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

        assemblage = None

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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_4(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
        current_caps = None
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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_5(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
        missing_caps = None

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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_6(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
        missing_caps = target_capabilities + current_caps

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

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_7(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                agents = None
                if agents and agents[0] not in assemblage.agents:
                    assemblage.add_agent(agents[0])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_8(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                agents = self.find_agents_with_capability(None)
                if agents and agents[0] not in assemblage.agents:
                    assemblage.add_agent(agents[0])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_9(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                if agents or agents[0] not in assemblage.agents:
                    assemblage.add_agent(agents[0])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_10(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                if agents and agents[1] not in assemblage.agents:
                    assemblage.add_agent(agents[0])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_11(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                if agents and agents[0] in assemblage.agents:
                    assemblage.add_agent(agents[0])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_12(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                    assemblage.add_agent(None)

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_13(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
                    assemblage.add_agent(agents[1])

            # Deterritorialize (make more fluid) after changes
            assemblage.deterritorialize(0.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_14(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
            assemblage.deterritorialize(None)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_15(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
            assemblage.deterritorialize(1.2)
            LOGGER.info(f"Optimized assemblage {assemblage_id}, added agents")

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity

    def xǁAssemblageMapperǁoptimize_assemblage__mutmut_16(
        self, assemblage_id: str, target_capabilities: Set[AgentCapability]
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
            LOGGER.info(None)

        # Remove agents with redundant capabilities (if assemblage is over-staffed)
        # This would be a more complex algorithm - skipped for brevity
    
    xǁAssemblageMapperǁoptimize_assemblage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁoptimize_assemblage__mutmut_1': xǁAssemblageMapperǁoptimize_assemblage__mutmut_1, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_2': xǁAssemblageMapperǁoptimize_assemblage__mutmut_2, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_3': xǁAssemblageMapperǁoptimize_assemblage__mutmut_3, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_4': xǁAssemblageMapperǁoptimize_assemblage__mutmut_4, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_5': xǁAssemblageMapperǁoptimize_assemblage__mutmut_5, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_6': xǁAssemblageMapperǁoptimize_assemblage__mutmut_6, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_7': xǁAssemblageMapperǁoptimize_assemblage__mutmut_7, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_8': xǁAssemblageMapperǁoptimize_assemblage__mutmut_8, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_9': xǁAssemblageMapperǁoptimize_assemblage__mutmut_9, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_10': xǁAssemblageMapperǁoptimize_assemblage__mutmut_10, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_11': xǁAssemblageMapperǁoptimize_assemblage__mutmut_11, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_12': xǁAssemblageMapperǁoptimize_assemblage__mutmut_12, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_13': xǁAssemblageMapperǁoptimize_assemblage__mutmut_13, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_14': xǁAssemblageMapperǁoptimize_assemblage__mutmut_14, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_15': xǁAssemblageMapperǁoptimize_assemblage__mutmut_15, 
        'xǁAssemblageMapperǁoptimize_assemblage__mutmut_16': xǁAssemblageMapperǁoptimize_assemblage__mutmut_16
    }
    
    def optimize_assemblage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁoptimize_assemblage__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁoptimize_assemblage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    optimize_assemblage.__signature__ = _mutmut_signature(xǁAssemblageMapperǁoptimize_assemblage__mutmut_orig)
    xǁAssemblageMapperǁoptimize_assemblage__mutmut_orig.__name__ = 'xǁAssemblageMapperǁoptimize_assemblage'

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_orig(self) -> Dict[str, Any]:
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_1(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = None

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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_2(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "XXidXX": agent.agent_id,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_3(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "ID": agent.agent_id,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_4(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "id": agent.agent_id,
                "XXtypeXX": agent.agent_type,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_5(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "id": agent.agent_id,
                "TYPE": agent.agent_type,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_6(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "id": agent.agent_id,
                "type": agent.agent_type,
                "XXcapabilitiesXX": [c.value for c in agent.capabilities],
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_7(self) -> Dict[str, Any]:
        """
        Export the current assemblage map for visualization.

        Returns:
            Dictionary with agents, assemblages, and relationships
        """
        agents_data = [
            {
                "id": agent.agent_id,
                "type": agent.agent_type,
                "CAPABILITIES": [c.value for c in agent.capabilities],
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_8(self) -> Dict[str, Any]:
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
                "XXactiveXX": agent.active,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_9(self) -> Dict[str, Any]:
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
                "ACTIVE": agent.active,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_10(self) -> Dict[str, Any]:
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

        assemblages_data = None

        return {
            "agents": agents_data,
            "assemblages": assemblages_data,
            "stats": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_11(self) -> Dict[str, Any]:
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
                "XXidXX": assemblage.assemblage_id,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_12(self) -> Dict[str, Any]:
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
                "ID": assemblage.assemblage_id,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_13(self) -> Dict[str, Any]:
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
                "XXpurposeXX": assemblage.purpose,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_14(self) -> Dict[str, Any]:
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
                "PURPOSE": assemblage.purpose,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_15(self) -> Dict[str, Any]:
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
                "XXstateXX": assemblage.state.value,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_16(self) -> Dict[str, Any]:
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
                "STATE": assemblage.state.value,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_17(self) -> Dict[str, Any]:
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
                "XXterritorializationXX": assemblage.territorialization,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_18(self) -> Dict[str, Any]:
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
                "TERRITORIALIZATION": assemblage.territorialization,
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_19(self) -> Dict[str, Any]:
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
                "XXagentsXX": [a.agent_id for a in assemblage.agents],
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_20(self) -> Dict[str, Any]:
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
                "AGENTS": [a.agent_id for a in assemblage.agents],
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_21(self) -> Dict[str, Any]:
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
                "XXcapabilitiesXX": [c.value for c in assemblage.get_collective_capabilities()],
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_22(self) -> Dict[str, Any]:
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
                "CAPABILITIES": [c.value for c in assemblage.get_collective_capabilities()],
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_23(self) -> Dict[str, Any]:
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
                "XXcapacityXX": self.calculate_assemblage_capacity(assemblage),
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_24(self) -> Dict[str, Any]:
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
                "CAPACITY": self.calculate_assemblage_capacity(assemblage),
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_25(self) -> Dict[str, Any]:
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
                "capacity": self.calculate_assemblage_capacity(None),
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

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_26(self) -> Dict[str, Any]:
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
            "XXagentsXX": agents_data,
            "assemblages": assemblages_data,
            "stats": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_27(self) -> Dict[str, Any]:
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
            "AGENTS": agents_data,
            "assemblages": assemblages_data,
            "stats": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_28(self) -> Dict[str, Any]:
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
            "XXassemblagesXX": assemblages_data,
            "stats": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_29(self) -> Dict[str, Any]:
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
            "ASSEMBLAGES": assemblages_data,
            "stats": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_30(self) -> Dict[str, Any]:
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
            "XXstatsXX": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_31(self) -> Dict[str, Any]:
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
            "STATS": {
                "total_agents": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_32(self) -> Dict[str, Any]:
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
                "XXtotal_agentsXX": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_33(self) -> Dict[str, Any]:
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
                "TOTAL_AGENTS": len(self.agents),
                "active_assemblages": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_34(self) -> Dict[str, Any]:
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
                "XXactive_assemblagesXX": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_35(self) -> Dict[str, Any]:
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
                "ACTIVE_ASSEMBLAGES": len(self.get_active_assemblages()),
                "dissolved_assemblages": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_36(self) -> Dict[str, Any]:
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
                "XXdissolved_assemblagesXX": len(self.assemblage_history),
            },
        }

    def xǁAssemblageMapperǁexport_assemblage_map__mutmut_37(self) -> Dict[str, Any]:
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
                "DISSOLVED_ASSEMBLAGES": len(self.assemblage_history),
            },
        }
    
    xǁAssemblageMapperǁexport_assemblage_map__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁexport_assemblage_map__mutmut_1': xǁAssemblageMapperǁexport_assemblage_map__mutmut_1, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_2': xǁAssemblageMapperǁexport_assemblage_map__mutmut_2, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_3': xǁAssemblageMapperǁexport_assemblage_map__mutmut_3, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_4': xǁAssemblageMapperǁexport_assemblage_map__mutmut_4, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_5': xǁAssemblageMapperǁexport_assemblage_map__mutmut_5, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_6': xǁAssemblageMapperǁexport_assemblage_map__mutmut_6, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_7': xǁAssemblageMapperǁexport_assemblage_map__mutmut_7, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_8': xǁAssemblageMapperǁexport_assemblage_map__mutmut_8, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_9': xǁAssemblageMapperǁexport_assemblage_map__mutmut_9, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_10': xǁAssemblageMapperǁexport_assemblage_map__mutmut_10, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_11': xǁAssemblageMapperǁexport_assemblage_map__mutmut_11, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_12': xǁAssemblageMapperǁexport_assemblage_map__mutmut_12, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_13': xǁAssemblageMapperǁexport_assemblage_map__mutmut_13, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_14': xǁAssemblageMapperǁexport_assemblage_map__mutmut_14, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_15': xǁAssemblageMapperǁexport_assemblage_map__mutmut_15, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_16': xǁAssemblageMapperǁexport_assemblage_map__mutmut_16, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_17': xǁAssemblageMapperǁexport_assemblage_map__mutmut_17, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_18': xǁAssemblageMapperǁexport_assemblage_map__mutmut_18, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_19': xǁAssemblageMapperǁexport_assemblage_map__mutmut_19, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_20': xǁAssemblageMapperǁexport_assemblage_map__mutmut_20, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_21': xǁAssemblageMapperǁexport_assemblage_map__mutmut_21, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_22': xǁAssemblageMapperǁexport_assemblage_map__mutmut_22, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_23': xǁAssemblageMapperǁexport_assemblage_map__mutmut_23, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_24': xǁAssemblageMapperǁexport_assemblage_map__mutmut_24, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_25': xǁAssemblageMapperǁexport_assemblage_map__mutmut_25, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_26': xǁAssemblageMapperǁexport_assemblage_map__mutmut_26, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_27': xǁAssemblageMapperǁexport_assemblage_map__mutmut_27, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_28': xǁAssemblageMapperǁexport_assemblage_map__mutmut_28, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_29': xǁAssemblageMapperǁexport_assemblage_map__mutmut_29, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_30': xǁAssemblageMapperǁexport_assemblage_map__mutmut_30, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_31': xǁAssemblageMapperǁexport_assemblage_map__mutmut_31, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_32': xǁAssemblageMapperǁexport_assemblage_map__mutmut_32, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_33': xǁAssemblageMapperǁexport_assemblage_map__mutmut_33, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_34': xǁAssemblageMapperǁexport_assemblage_map__mutmut_34, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_35': xǁAssemblageMapperǁexport_assemblage_map__mutmut_35, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_36': xǁAssemblageMapperǁexport_assemblage_map__mutmut_36, 
        'xǁAssemblageMapperǁexport_assemblage_map__mutmut_37': xǁAssemblageMapperǁexport_assemblage_map__mutmut_37
    }
    
    def export_assemblage_map(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁexport_assemblage_map__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁexport_assemblage_map__mutmut_mutants"), args, kwargs, self)
        return result 
    
    export_assemblage_map.__signature__ = _mutmut_signature(xǁAssemblageMapperǁexport_assemblage_map__mutmut_orig)
    xǁAssemblageMapperǁexport_assemblage_map__mutmut_orig.__name__ = 'xǁAssemblageMapperǁexport_assemblage_map'

    def xǁAssemblageMapperǁget_stats__mutmut_orig(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_1(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "XXtotal_agentsXX": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_2(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "TOTAL_AGENTS": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_3(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "XXactive_agentsXX": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_4(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "ACTIVE_AGENTS": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_5(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(None),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_6(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(2 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_7(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "XXtotal_assemblagesXX": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_8(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "TOTAL_ASSEMBLAGES": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_9(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "XXactive_assemblagesXX": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_10(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "ACTIVE_ASSEMBLAGES": len(self.get_active_assemblages()),
            "dissolved_assemblages": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_11(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "XXdissolved_assemblagesXX": len(self.assemblage_history),
        }

    def xǁAssemblageMapperǁget_stats__mutmut_12(self) -> Dict[str, Any]:
        """Get statistics about agents and assemblages."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "total_assemblages": len(self.assemblages),
            "active_assemblages": len(self.get_active_assemblages()),
            "DISSOLVED_ASSEMBLAGES": len(self.assemblage_history),
        }
    
    xǁAssemblageMapperǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAssemblageMapperǁget_stats__mutmut_1': xǁAssemblageMapperǁget_stats__mutmut_1, 
        'xǁAssemblageMapperǁget_stats__mutmut_2': xǁAssemblageMapperǁget_stats__mutmut_2, 
        'xǁAssemblageMapperǁget_stats__mutmut_3': xǁAssemblageMapperǁget_stats__mutmut_3, 
        'xǁAssemblageMapperǁget_stats__mutmut_4': xǁAssemblageMapperǁget_stats__mutmut_4, 
        'xǁAssemblageMapperǁget_stats__mutmut_5': xǁAssemblageMapperǁget_stats__mutmut_5, 
        'xǁAssemblageMapperǁget_stats__mutmut_6': xǁAssemblageMapperǁget_stats__mutmut_6, 
        'xǁAssemblageMapperǁget_stats__mutmut_7': xǁAssemblageMapperǁget_stats__mutmut_7, 
        'xǁAssemblageMapperǁget_stats__mutmut_8': xǁAssemblageMapperǁget_stats__mutmut_8, 
        'xǁAssemblageMapperǁget_stats__mutmut_9': xǁAssemblageMapperǁget_stats__mutmut_9, 
        'xǁAssemblageMapperǁget_stats__mutmut_10': xǁAssemblageMapperǁget_stats__mutmut_10, 
        'xǁAssemblageMapperǁget_stats__mutmut_11': xǁAssemblageMapperǁget_stats__mutmut_11, 
        'xǁAssemblageMapperǁget_stats__mutmut_12': xǁAssemblageMapperǁget_stats__mutmut_12
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAssemblageMapperǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁAssemblageMapperǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁAssemblageMapperǁget_stats__mutmut_orig)
    xǁAssemblageMapperǁget_stats__mutmut_orig.__name__ = 'xǁAssemblageMapperǁget_stats'
