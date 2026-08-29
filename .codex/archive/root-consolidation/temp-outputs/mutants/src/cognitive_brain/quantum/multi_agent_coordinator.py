"""
Multi-Agent Coordination for Quantum Cognitive Brain.

This module implements multi-agent coordination using quantum-inspired principles,
enabling multiple agents to reach consensus on decisions through various voting
strategies.

PDA Loop Tags: [INIT] Multi-agent coordination framework
AfterMath Tags: Phase 8.2 - Multi-Agent Orchestration
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class VotingStrategy(Enum):
    """Voting strategies for consensus building."""

    MAJORITY = "majority"
    WEIGHTED = "weighted"
    CONFIDENCE_BASED = "confidence_based"


@dataclass
class AgentDecision:
    """
    Represents a decision made by an agent.

    PDA Loop: [DATA] Agent decision container
    """

    agent_id: str
    decision: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate agent decision."""
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")


@dataclass
class AgentInfo:
    """
    Information about a registered agent.

    PDA Loop: [DATA] Agent metadata storage
    """

    agent_id: str
    role: str
    weight: float = 1.0
    active: bool = True
    decisions_made: int = 0
    last_active: datetime = field(default_factory=datetime.now)


class MultiAgentCoordinator:
    """
    Coordinates decisions across multiple agents using quantum-inspired principles.

    This class implements multi-agent coordination with support for various
    consensus strategies including majority voting, weighted voting, and
    confidence-based voting.

    PDA Loop: [PROCESS] Multi-agent coordination and consensus building
    AfterMath: Enables scalable decision-making across N agents

    Attributes:
        agents: Dictionary of registered agents
        decision_history: List of past consensus decisions
        voting_strategy: Current voting strategy
    """

    def __init__(self, voting_strategy: VotingStrategy = VotingStrategy.MAJORITY):
        """
        Initialize the multi-agent coordinator.

        Args:
            voting_strategy: Strategy for reaching consensus (default: MAJORITY)

        PDA Loop: [INIT] Initialize coordinator with voting strategy
        """
        self.agents: dict[str, AgentInfo] = {}
        self.decision_history: list[dict[str, Any]] = []
        self.voting_strategy = voting_strategy
        self._lock = False  # Simple lock for concurrent operations

        logger.info(f"MultiAgentCoordinator initialized with strategy: {voting_strategy.value}")

    def register_agent(self, agent_id: str, role: str, weight: float = 1.0) -> None:
        """
        Register a new agent in the coordination system.

        Args:
            agent_id: Unique identifier for the agent
            role: Role or function of the agent
            weight: Voting weight for weighted strategies (default: 1.0)

        Raises:
            ValueError: If agent_id is empty or already exists

        PDA Loop: [ACTION] Register agent for coordination
        AfterMath: Agent can now participate in consensus decisions
        """
        if not agent_id:
            raise ValueError("agent_id cannot be empty")

        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} is already registered")

        if weight < 0:
            raise ValueError(f"Agent weight must be non-negative, got {weight}")

        self.agents[agent_id] = AgentInfo(
            agent_id=agent_id,
            role=role,
            weight=weight,
            active=True,
            decisions_made=0,
            last_active=datetime.now(timezone.utc),
        )

        logger.info(f"Registered agent: {agent_id} with role: {role}, weight: {weight}")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the coordination system.

        Args:
            agent_id: Unique identifier for the agent

        Raises:
            ValueError: If agent_id doesn't exist

        PDA Loop: [ACTION] Remove agent from coordination
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} is not registered")

        del self.agents[agent_id]
        logger.info(f"Unregistered agent: {agent_id}")

    def broadcast_update(self, agent_id: str, state: dict[str, Any]) -> None:
        """
        Broadcast a state update from one agent to all others.

        Args:
            agent_id: ID of the agent sending the update
            state: State information to broadcast

        Raises:
            ValueError: If agent_id is not registered

        PDA Loop: [ACTION] Broadcast agent state to all participants
        AfterMath: Enables information sharing across agents
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} is not registered")

        # Update agent's last active timestamp
        self.agents[agent_id].last_active = datetime.now(timezone.utc)

        # In a real implementation, this would send the state to other agents
        # For now, we log it
        logger.debug(f"Broadcasting update from {agent_id}: {state}")

    def coordinate_decision(self, context: dict[str, Any]) -> str:
        """
        Coordinate a decision across all active agents.

        This method simulates requesting decisions from all agents and
        reaching consensus based on the configured voting strategy.

        Args:
            context: Context information for the decision

        Returns:
            Final consensus decision

        PDA Loop: [PROCESS] Coordinate multi-agent decision making
        AfterMath: Produces consensus decision from multiple agents
        """
        if not self.agents:
            raise ValueError("No agents registered for coordination")

        # Simulate collecting decisions from all active agents
        # In a real implementation, this would query each agent
        decisions: list[AgentDecision] = []

        for agent_id, agent_info in self.agents.items():
            if agent_info.active:
                # Simulate agent decision (in reality, would call agent)
                decision = self._simulate_agent_decision(agent_id, context)
                decisions.append(decision)
                agent_info.decisions_made += 1
                agent_info.last_active = datetime.now(timezone.utc)

        if not decisions:
            raise ValueError("No active agents available for decision")

        # Reach consensus
        consensus = self.reach_consensus(decisions)

        # Record in history
        self.decision_history.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "context": context,
                "decisions": decisions,
                "consensus": consensus,
                "num_agents": len(decisions),
            }
        )

        logger.info(f"Consensus reached: {consensus} from {len(decisions)} agents")
        return consensus

    def _simulate_agent_decision(self, agent_id: str, context: dict[str, Any]) -> AgentDecision:
        """
        Simulate an agent making a decision.

        In a production system, this would call the actual agent's decision logic.

        Args:
            agent_id: ID of the agent
            context: Decision context

        Returns:
            Simulated agent decision

        PDA Loop: [SIMULATE] Generate agent decision for testing
        """
        # Simple simulation based on context
        decision_options = ["approve", "reject", "defer"]

        # Use agent_id hash for deterministic simulation
        agent_hash = hash(agent_id) % len(decision_options)
        decision = decision_options[agent_hash]

        # Simulate confidence based on context
        confidence = 0.6 + (hash(str(context)) % 40) / 100.0

        return AgentDecision(
            agent_id=agent_id,
            decision=decision,
            confidence=confidence,
            metadata={"simulated": True},
        )

    def reach_consensus(self, decisions: list[AgentDecision]) -> str:
        """
        Reach consensus from multiple agent decisions.

        Uses the configured voting strategy to determine the final decision.

        Args:
            decisions: List of agent decisions

        Returns:
            Consensus decision

        Raises:
            ValueError: If decisions list is empty

        PDA Loop: [DECISION] Apply voting strategy for consensus
        AfterMath: Produces final decision from agent votes
        """
        if not decisions:
            raise ValueError("Cannot reach consensus with no decisions")

        if self.voting_strategy == VotingStrategy.MAJORITY:
            return self._majority_vote(decisions)
        if self.voting_strategy == VotingStrategy.WEIGHTED:
            return self._weighted_vote(decisions)
        if self.voting_strategy == VotingStrategy.CONFIDENCE_BASED:
            return self._confidence_based_vote(decisions)
        raise ValueError(f"Unknown voting strategy: {self.voting_strategy}")

    def _majority_vote(self, decisions: list[AgentDecision]) -> str:
        """
        Simple majority voting.

        Args:
            decisions: List of agent decisions

        Returns:
            Decision with most votes

        PDA Loop: [CALCULATE] Count votes and select majority
        """
        vote_counts: dict[str, int] = {}

        for decision in decisions:
            vote_counts[decision.decision] = vote_counts.get(decision.decision, 0) + 1

        # Find decision with max votes
        max_votes = max(vote_counts.values())
        candidates = [d for d, v in vote_counts.items() if v == max_votes]

        # If tie, use confidence as tie-breaker
        if len(candidates) > 1:
            logger.warning(f"Tie in majority vote: {candidates}. Using confidence tie-breaker.")
            return self._confidence_based_vote([d for d in decisions if d.decision in candidates])

        return candidates[0]

    def _weighted_vote(self, decisions: list[AgentDecision]) -> str:
        """
        Weighted voting based on agent weights.

        Args:
            decisions: List of agent decisions

        Returns:
            Decision with highest weighted vote

        PDA Loop: [CALCULATE] Apply agent weights to votes
        """
        weighted_votes: dict[str, float] = {}

        for decision in decisions:
            agent_info = self.agents.get(decision.agent_id)
            weight = agent_info.weight if agent_info else 1.0

            weighted_votes[decision.decision] = weighted_votes.get(decision.decision, 0.0) + weight

        # Find decision with max weighted votes
        max_weight = max(weighted_votes.values())
        candidates = [d for d, w in weighted_votes.items() if w == max_weight]

        # If tie, use confidence as tie-breaker
        if len(candidates) > 1:
            logger.warning(f"Tie in weighted vote: {candidates}. Using confidence tie-breaker.")
            return self._confidence_based_vote([d for d in decisions if d.decision in candidates])

        return candidates[0]

    def _confidence_based_vote(self, decisions: list[AgentDecision]) -> str:
        """
        Voting based on agent confidence levels.

        Args:
            decisions: List of agent decisions

        Returns:
            Decision with highest total confidence

        PDA Loop: [CALCULATE] Sum confidence scores per decision
        """
        confidence_sums: dict[str, float] = {}

        for decision in decisions:
            confidence_sums[decision.decision] = (
                confidence_sums.get(decision.decision, 0.0) + decision.confidence
            )

        # Find decision with max confidence
        max_confidence = max(confidence_sums.values())
        candidates = [d for d, c in confidence_sums.items() if abs(c - max_confidence) < 1e-6]

        # If still tied (very rare), use first alphabetically
        if len(candidates) > 1:
            logger.warning(f"Tie in confidence vote: {candidates}. Using alphabetical tie-breaker.")
            return sorted(candidates)[0]

        return candidates[0]

    def get_agent_statistics(self) -> dict[str, Any]:
        """
        Get statistics about registered agents.

        Returns:
            Dictionary with agent statistics

        PDA Loop: [ANALYZE] Compute coordination statistics
        """
        active_count = sum(1 for a in self.agents.values() if a.active)
        total_decisions = sum(a.decisions_made for a in self.agents.values())

        return {
            "total_agents": len(self.agents),
            "active_agents": active_count,
            "inactive_agents": len(self.agents) - active_count,
            "total_decisions": total_decisions,
            "decision_history_size": len(self.decision_history),
            "voting_strategy": self.voting_strategy.value,
        }

    def set_voting_strategy(self, strategy: VotingStrategy) -> None:
        """
        Change the voting strategy.

        Args:
            strategy: New voting strategy to use

        PDA Loop: [CONFIG] Update coordination strategy
        """
        self.voting_strategy = strategy
        logger.info(f"Voting strategy changed to: {strategy.value}")

    def clear_history(self) -> None:
        """
        Clear the decision history.

        PDA Loop: [CLEANUP] Reset decision history
        """
        self.decision_history.clear()
        logger.info("Decision history cleared")
