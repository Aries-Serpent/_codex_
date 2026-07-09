"""Orchestration integration for cognitive brain.

This module provides brain-aware orchestration capabilities, enabling
orchestrating agents to make smarter routing decisions based on pattern
matching, success rates, and learned behaviors.

Phase 1.4 of Long-term Cognitive Brain Planset.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# Default paths
DEFAULT_PATTERN_STORE = Path(".codex/cognitive_brain/pattern_learning_store.json")
DEFAULT_MANIFEST = Path(".codex/cognitive_brain/agent_integration_manifest.json")


class OrchestrationPattern(Enum):
    """Orchestration patterns for agent coordination."""

    SEQUENTIAL_CHAIN = "sequential_chain"
    PARALLEL_FAN_OUT = "parallel_fan_out"
    CONDITIONAL_ROUTING = "conditional_routing"
    HIERARCHICAL_DELEGATION = "hierarchical"


@dataclass
class OrchestrationDecision:
    """Result of an orchestration decision."""

    selected_agents: list[str]
    pattern: OrchestrationPattern
    confidence: float
    reasoning: str
    pattern_matches: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class OrchestrationResult:
    """Result of orchestrated execution."""

    orchestrator_id: str
    agents_executed: list[str]
    pattern_used: OrchestrationPattern
    success: bool
    learnings: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0


# 11 orchestrating agents with their patterns
ORCHESTRATING_AGENTS: dict[str, dict[str, Any]] = {
    "artifact-monitor-agent": {
        "pattern": OrchestrationPattern.HIERARCHICAL_DELEGATION,
        "capability": "pattern_routing",
        "delegates_to": [
            "ci-testing-agent",
            "ci-log-retrieval-agent",
            "workflow-ci-fixer",
        ],
        "description": "Monitors CI/CD artifacts and delegates to specialist agents",
    },
    "coverage-roadmap-agent": {
        "pattern": OrchestrationPattern.SEQUENTIAL_CHAIN,
        "capability": "test_coordination",
        "delegates_to": [
            "coverage-gapfill-agent",
            "test-enhancement-agent",
            "tokenization-coverage-agent",
        ],
        "description": "Coordinates test coverage improvement workflow",
    },
    "repository-hygiene-agent": {
        "pattern": OrchestrationPattern.HIERARCHICAL_DELEGATION,
        "capability": "cleanup_coordination",
        "delegates_to": [
            "root-organizer-agent",
            "documentation-consolidator",
            "code-analysis-agent",
        ],
        "description": "Orchestrates comprehensive repository cleanup",
    },
    "integration-test-runner": {
        "pattern": OrchestrationPattern.PARALLEL_FAN_OUT,
        "capability": "cross_component_testing",
        "delegates_to": ["test-alignment-fixer", "test-coverage-monitor"],
        "description": "Runs integration tests across services in parallel",
    },
    "rag-module-management-agent": {
        "pattern": OrchestrationPattern.HIERARCHICAL_DELEGATION,
        "capability": "rag_coordination",
        "delegates_to": [
            "rag-index-manager",
            "meta-tensor-validator",
            "rag-meta-tensor-regression-agent",
        ],
        "description": "Coordinates RAG module operations",
    },
    "reference-updater-agent": {
        "pattern": OrchestrationPattern.SEQUENTIAL_CHAIN,
        "capability": "atomic_updates",
        "delegates_to": ["link-validator-agent", "documentation-consolidator"],
        "description": "Atomic reference updates across codebase",
    },
    "root-organizer-agent": {
        "pattern": OrchestrationPattern.SEQUENTIAL_CHAIN,
        "capability": "safe_reorganization",
        "delegates_to": ["reference-updater-agent"],
        "description": "Safe incremental root folder reorganization",
    },
    "tokenization-coverage-agent": {
        "pattern": OrchestrationPattern.SEQUENTIAL_CHAIN,
        "capability": "tokenization_improvements",
        "delegates_to": ["test-coverage-monitor"],
        "description": "Improves tokenization test coverage",
    },
    "workflow-management-agent": {
        "pattern": OrchestrationPattern.HIERARCHICAL_DELEGATION,
        "capability": "workflow_orchestration",
        "delegates_to": ["workflow-ci-fixer", "artifact-monitor-agent"],
        "description": "Orchestrates workflow operations",
    },
    "code-analysis-agent": {
        "pattern": OrchestrationPattern.PARALLEL_FAN_OUT,
        "capability": "multi_analysis",
        "delegates_to": [],
        "description": "Parallel code quality analysis",
    },
    "codex-reviewer-agent": {
        "pattern": OrchestrationPattern.CONDITIONAL_ROUTING,
        "capability": "review_logic",
        "delegates_to": [
            "security-alert-verification-agent",
            "codeql-alert-resolution-agent",
        ],
        "description": "Quantum-inspired PR reviewer with conditional routing",
    },
}


class BrainAwareOrchestrator:
    """Orchestrator with cognitive brain integration.

    Provides enhanced routing decisions based on pattern matching,
    success rates, and learned behaviors from the cognitive brain.
    """

    def __init__(
        self,
        orchestrator_id: str,
        pattern_store_path: Path | None = None,
        manifest_path: Path | None = None,
    ):
        """Initialize a brain-aware orchestrator.

        Args:
            orchestrator_id: ID of the orchestrating agent
            pattern_store_path: Path to pattern store (optional)
            manifest_path: Path to integration manifest (optional)
        """
        self.orchestrator_id = orchestrator_id
        self.pattern_store_path = pattern_store_path or DEFAULT_PATTERN_STORE
        self.manifest_path = manifest_path or DEFAULT_MANIFEST

        # Validate orchestrator
        if orchestrator_id not in ORCHESTRATING_AGENTS:
            raise ValueError(
                f"Unknown orchestrator: {orchestrator_id}. "
                f"Valid orchestrators: {list(ORCHESTRATING_AGENTS.keys())}"
            )

        self.config = ORCHESTRATING_AGENTS[orchestrator_id]
        self.pattern = self.config["pattern"]
        self.capability = self.config["capability"]
        self.delegates_to = self.config["delegates_to"]

        # Load brain data
        self._patterns: list[dict[str, Any]] = []
        self._manifest: dict[str, Any] = {}
        self._load_brain_data()

    def _load_brain_data(self) -> None:
        """Load pattern store and manifest."""
        # Load patterns
        if self.pattern_store_path.exists():
            try:
                with open(self.pattern_store_path) as f:
                    data = json.load(f)
                    self._patterns = data.get("patterns", [])
            except (json.JSONDecodeError, OSError):
                self._patterns = []

        # Load manifest
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    self._manifest = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._manifest = {}

    def query_patterns(self, symptom: str) -> list[dict[str, Any]]:
        """Query patterns matching a symptom.

        Args:
            symptom: Symptom text to search for

        Returns:
            List of matching patterns sorted by success rate
        """
        matches = []
        symptom_lower = symptom.lower()

        for pattern in self._patterns:
            # Check if symptom matches pattern keywords or symptoms
            keywords = [kw.lower() for kw in pattern.get("keywords", [])]
            symptoms = [s.lower() for s in pattern.get("symptoms", [])]

            if any(kw in symptom_lower for kw in keywords) or any(
                s in symptom_lower for s in symptoms
            ):
                matches.append(pattern)

        # Sort by success rate
        return sorted(matches, key=lambda p: p.get("success_rate", 0.5), reverse=True)

    def recommend_agents(self, task_description: str, min_success_rate: float = 0.7) -> list[str]:
        """Recommend agents based on task description and success rates.

        Args:
            task_description: Description of the task
            min_success_rate: Minimum success rate threshold

        Returns:
            List of recommended agent IDs
        """
        # First check pattern matches
        patterns = self.query_patterns(task_description)

        recommended: set[str] = set()

        # Add agents from matching patterns
        for pattern in patterns:
            if pattern.get("success_rate", 0) >= min_success_rate:
                # Add related agents
                category = pattern.get("category", "")
                if category:
                    category_agents = self._get_agents_by_category(category)
                    recommended.update(category_agents)

        # Always include delegates
        recommended.update(self.delegates_to)

        return list(recommended)

    def _get_agents_by_category(self, category: str) -> list[str]:
        """Get integrated agents by category."""
        agents = self._manifest.get("agents", {})
        return [
            agent_id
            for agent_id, data in agents.items()
            if data.get("category", "").lower() == category.lower()
        ]

    def make_routing_decision(self, task_description: str) -> OrchestrationDecision:
        """Make a brain-informed routing decision.

        Args:
            task_description: Description of the task

        Returns:
            OrchestrationDecision with selected agents and reasoning
        """
        patterns = self.query_patterns(task_description)
        recommended = self.recommend_agents(task_description)

        # Determine confidence based on pattern match quality
        if patterns:
            confidence = max(p.get("success_rate", 0.5) for p in patterns)
        elif recommended:
            confidence = 0.6  # Base confidence for delegates
        else:
            confidence = 0.4  # Low confidence if no patterns match

        # Build reasoning
        pattern_ids = [p.get("id", "unknown") for p in patterns[:3]]
        if patterns:
            reasoning = f"Selected based on {len(patterns)} pattern match(es): {pattern_ids}"
        else:
            reasoning = f"Using default delegates for {self.orchestrator_id}"

        return OrchestrationDecision(
            selected_agents=recommended or self.delegates_to,
            pattern=self.pattern,
            confidence=confidence,
            reasoning=reasoning,
            pattern_matches=pattern_ids,
        )

    def execute_sequential_chain(
        self,
        agents: list[str],
        task_fn: Callable[[str], bool] | None = None,
    ) -> OrchestrationResult:
        """Execute agents in sequence (A → B → C).

        Args:
            agents: List of agent IDs to execute in order
            task_fn: Optional function to call for each agent

        Returns:
            OrchestrationResult with execution details
        """
        learnings: list[dict[str, Any]] = []
        executed: list[str] = []
        success = True

        for agent_id in agents:
            executed.append(agent_id)
            if task_fn:
                agent_success = task_fn(agent_id)
                if not agent_success:
                    success = False
                    break
            learnings.append(
                {
                    "agent_id": agent_id,
                    "step": len(executed),
                    "status": "executed",
                }
            )

        return OrchestrationResult(
            orchestrator_id=self.orchestrator_id,
            agents_executed=executed,
            pattern_used=OrchestrationPattern.SEQUENTIAL_CHAIN,
            success=success,
            learnings=learnings,
        )

    def execute_parallel_fan_out(
        self,
        agents: list[str],
        task_fn: Callable[[str], bool] | None = None,
    ) -> OrchestrationResult:
        """Execute agents in parallel (fan-out pattern).

        Note: In actual implementation, this would use async/threading.
        This version simulates parallel execution.

        Args:
            agents: List of agent IDs to execute in parallel
            task_fn: Optional function to call for each agent

        Returns:
            OrchestrationResult with execution details
        """
        learnings: list[dict[str, Any]] = []
        results: dict[str, bool] = {}

        for agent_id in agents:
            agent_success = True
            if task_fn:
                agent_success = task_fn(agent_id)
            results[agent_id] = agent_success
            learnings.append(
                {
                    "agent_id": agent_id,
                    "parallel_batch": 1,
                    "success": agent_success,
                }
            )

        all_success = all(results.values())

        return OrchestrationResult(
            orchestrator_id=self.orchestrator_id,
            agents_executed=list(agents),
            pattern_used=OrchestrationPattern.PARALLEL_FAN_OUT,
            success=all_success,
            learnings=learnings,
        )

    def execute_conditional_routing(
        self,
        condition: str,
        agents_map: dict[str, list[str]],
        task_fn: Callable[[str], bool] | None = None,
    ) -> OrchestrationResult:
        """Execute agents based on condition routing.

        Args:
            condition: Condition key to route on
            agents_map: Map of condition values to agent lists
            task_fn: Optional function to call for each agent

        Returns:
            OrchestrationResult with execution details
        """
        # Use brain patterns to determine route
        patterns = self.query_patterns(condition)
        selected_route = "default"

        if patterns:
            # Use first matching pattern's category
            top_pattern = patterns[0]
            pattern_category = top_pattern.get("category", "default")
            if pattern_category in agents_map:
                selected_route = pattern_category

        agents_to_run = agents_map.get(selected_route, [])
        learnings: list[dict[str, Any]] = [
            {"condition": condition, "route_selected": selected_route}
        ]

        executed: list[str] = []
        success = True

        for agent_id in agents_to_run:
            executed.append(agent_id)
            if task_fn:
                agent_success = task_fn(agent_id)
                if not agent_success:
                    success = False

        return OrchestrationResult(
            orchestrator_id=self.orchestrator_id,
            agents_executed=executed,
            pattern_used=OrchestrationPattern.CONDITIONAL_ROUTING,
            success=success,
            learnings=learnings,
        )

    def aggregate_learnings(self, results: list[OrchestrationResult]) -> dict[str, Any]:
        """Aggregate learnings from multiple orchestration results.

        Args:
            results: List of orchestration results

        Returns:
            Aggregated learning summary
        """
        total_agents = 0
        successful = 0
        patterns_used: dict[str, int] = {}

        for result in results:
            total_agents += len(result.agents_executed)
            if result.success:
                successful += 1

            pattern_name = result.pattern_used.value
            patterns_used[pattern_name] = patterns_used.get(pattern_name, 0) + 1

        return {
            "total_orchestrations": len(results),
            "total_agents_executed": total_agents,
            "successful_orchestrations": successful,
            "success_rate": successful / len(results) if results else 0,
            "patterns_used": patterns_used,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def get_orchestrating_agents() -> dict[str, dict[str, Any]]:
    """Get all orchestrating agents.

    Returns:
        Dictionary of orchestrating agents with their configs
    """
    return ORCHESTRATING_AGENTS.copy()


def get_orchestrating_agent_count() -> int:
    """Get count of orchestrating agents.

    Returns:
        Number of orchestrating agents (11)
    """
    return len(ORCHESTRATING_AGENTS)


def integrate_orchestrating_agents(
    manifest_path: Path | None = None,
) -> list[str]:
    """Integrate all orchestrating agents into the manifest.

    Args:
        manifest_path: Path to manifest file

    Returns:
        List of integrated agent IDs
    """
    manifest_path = manifest_path or DEFAULT_MANIFEST

    # Load existing manifest
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError):
            manifest = {}

    if "agents" not in manifest:
        manifest["agents"] = {}

    # Add orchestrating agents
    for agent_id, config in ORCHESTRATING_AGENTS.items():
        manifest["agents"][agent_id] = {
            "category": "orchestration",
            "capability": config["capability"],
            "pattern": config["pattern"].value,
            "delegates_to": config["delegates_to"],
            "integration_date": datetime.now(timezone.utc).isoformat(),
            "brain_enabled": True,
        }

    # Update metadata
    manifest["metadata"] = manifest.get("metadata", {})
    manifest["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    manifest["metadata"]["total_agents"] = len(manifest["agents"])
    manifest["metadata"]["orchestrating_agents"] = len(ORCHESTRATING_AGENTS)

    # Save manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return list(ORCHESTRATING_AGENTS.keys())


def create_orchestrator(orchestrator_id: str) -> BrainAwareOrchestrator:
    """Create a brain-aware orchestrator.

    Args:
        orchestrator_id: ID of the orchestrating agent

    Returns:
        BrainAwareOrchestrator instance
    """
    return BrainAwareOrchestrator(orchestrator_id)
