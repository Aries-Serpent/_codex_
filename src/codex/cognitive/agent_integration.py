#!/usr/bin/env python3
"""Agent integration module for Cognitive Brain Phase 1.2.

This module provides utilities for integrating agents with the cognitive brain,
including pattern querying, learning feedback, and session state management.

Example:
    >>> from codex.cognitive.agent_integration import integrate_agent
    >>> brain = integrate_agent("ci-testing-agent")
    >>> patterns = brain.query_patterns("pytest collection error")
    >>> brain.submit_learning("TFR-001", "success", {"fix": "added import"})
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AgentCategory(Enum):
    """Categories of agents for cognitive brain integration."""

    CI_CD = "ci_cd"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    RAG_ML = "rag_ml"
    REPOSITORY = "repository"
    OTHER = "other"


@dataclass
class IntegratedAgent:
    """Represents an agent integrated with the cognitive brain."""

    agent_id: str
    category: AgentCategory
    integration_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    capabilities: list[str] = field(default_factory=list)
    patterns_accessed: int = 0
    learnings_submitted: int = 0
    last_access: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "category": self.category.value,
            "integration_date": self.integration_date,
            "capabilities": self.capabilities,
            "patterns_accessed": self.patterns_accessed,
            "learnings_submitted": self.learnings_submitted,
            "last_access": self.last_access,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IntegratedAgent:
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            category=AgentCategory(data["category"]),
            integration_date=data.get("integration_date", datetime.now(timezone.utc).isoformat()),
            capabilities=data.get("capabilities", []),
            patterns_accessed=data.get("patterns_accessed", 0),
            learnings_submitted=data.get("learnings_submitted", 0),
            last_access=data.get("last_access"),
        )


class AgentIntegrationRegistry:
    """Registry tracking all agents integrated with the cognitive brain."""

    def __init__(self, manifest_path: Path | str | None = None):
        """Initialize the registry.

        Args:
            manifest_path: Path to the integration manifest JSON file.
        """
        if manifest_path is None:
            manifest_path = Path(".codex/cognitive_brain/agent_integration_manifest.json")
        self.manifest_path = Path(manifest_path)
        self._agents: dict[str, IntegratedAgent] = {}
        self._load()

    def _load(self) -> None:
        """Load the manifest from disk."""
        if self.manifest_path.exists():
            try:
                data = json.loads(self.manifest_path.read_text())
                self._agents = {
                    agent_id: IntegratedAgent.from_dict(agent_data)
                    for agent_id, agent_data in data.get("agents", {}).items()
                }
            except (json.JSONDecodeError, KeyError):
                self._agents = {}
        else:
            self._agents = {}

    def save(self) -> None:
        """Save the manifest to disk."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_agents": len(self._agents),
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self._agents.items()},
        }
        self.manifest_path.write_text(json.dumps(data, indent=2))

    def register(
        self,
        agent_id: str,
        category: AgentCategory,
        capabilities: list[str] | None = None,
    ) -> IntegratedAgent:
        """Register an agent with the cognitive brain.

        Args:
            agent_id: Unique identifier for the agent.
            category: Category of the agent.
            capabilities: List of brain capabilities this agent uses.

        Returns:
            The registered IntegratedAgent.
        """
        if capabilities is None:
            capabilities = ["pattern_query", "learning_feedback"]

        agent = IntegratedAgent(
            agent_id=agent_id,
            category=category,
            capabilities=capabilities,
        )
        self._agents[agent_id] = agent
        return agent

    def get(self, agent_id: str) -> IntegratedAgent | None:
        """Get an integrated agent by ID."""
        return self._agents.get(agent_id)

    def is_integrated(self, agent_id: str) -> bool:
        """Check if an agent is integrated."""
        return agent_id in self._agents

    def list_by_category(self, category: AgentCategory) -> list[IntegratedAgent]:
        """List all integrated agents in a category."""
        return [a for a in self._agents.values() if a.category == category]

    def list_all(self) -> list[IntegratedAgent]:
        """List all integrated agents."""
        return list(self._agents.values())

    def record_access(self, agent_id: str) -> None:
        """Record that an agent accessed the brain."""
        if agent_id in self._agents:
            self._agents[agent_id].patterns_accessed += 1
            self._agents[agent_id].last_access = datetime.now(timezone.utc).isoformat()

    def record_learning(self, agent_id: str) -> None:
        """Record that an agent submitted a learning."""
        if agent_id in self._agents:
            self._agents[agent_id].learnings_submitted += 1
            self._agents[agent_id].last_access = datetime.now(timezone.utc).isoformat()

    @property
    def total_integrated(self) -> int:
        """Get total number of integrated agents."""
        return len(self._agents)

    def get_stats(self) -> dict[str, Any]:
        """Get integration statistics."""
        by_category: dict[str, int] = {}
        for agent in self._agents.values():
            cat = agent.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_agents": len(self._agents),
            "by_category": by_category,
            "total_pattern_accesses": sum(a.patterns_accessed for a in self._agents.values()),
            "total_learnings": sum(a.learnings_submitted for a in self._agents.values()),
        }


def integrate_agent(
    agent_id: str,
    category: AgentCategory | str = AgentCategory.OTHER,
    capabilities: list[str] | None = None,
    manifest_path: Path | str | None = None,
) -> IntegratedAgent:
    """Integrate an agent with the cognitive brain.

    This is the main entry point for agent integration. It registers
    the agent in the manifest and returns the IntegratedAgent object.

    Args:
        agent_id: Unique identifier for the agent.
        category: Category of the agent (string or AgentCategory).
        capabilities: List of brain capabilities this agent uses.
        manifest_path: Optional custom manifest path.

    Returns:
        The registered IntegratedAgent.

    Example:
        >>> agent = integrate_agent("ci-testing-agent", "ci_cd")
        >>> print(agent.agent_id)
        ci-testing-agent
    """
    if isinstance(category, str):
        category = AgentCategory(category)

    registry = AgentIntegrationRegistry(manifest_path)
    agent = registry.register(agent_id, category, capabilities)
    registry.save()
    return agent


# Pre-defined core agents for Phase 1.2
CORE_AGENTS = {
    # CI/CD Agents
    "ci-testing-agent": AgentCategory.CI_CD,
    "ci-log-retrieval-agent": AgentCategory.CI_CD,
    "workflow-ci-fixer": AgentCategory.CI_CD,
    "artifact-monitor-agent": AgentCategory.CI_CD,
    # Testing Agents
    "coverage-roadmap-agent": AgentCategory.TESTING,
    "test-alignment-fixer": AgentCategory.TESTING,
    "test-coverage-monitor": AgentCategory.TESTING,
    # Security Agents
    "security-alert-verification-agent": AgentCategory.SECURITY,
    "codeql-alert-resolution-agent": AgentCategory.SECURITY,
}

# Pre-defined extended agents for Phase 1.3
EXTENDED_AGENTS = {
    # Documentation Agents
    "documentation-consolidator": AgentCategory.DOCUMENTATION,
    "link-validator-agent": AgentCategory.DOCUMENTATION,
    "doc-freshness-checker": AgentCategory.DOCUMENTATION,
    # RAG/ML Agents
    "rag-index-manager": AgentCategory.RAG_ML,
    "meta-tensor-validator": AgentCategory.RAG_ML,
    "rag-meta-tensor-regression-agent": AgentCategory.RAG_ML,
    # Repository Agents
    "repository-hygiene-agent": AgentCategory.REPOSITORY,
    "root-organizer-agent": AgentCategory.REPOSITORY,
    "reference-updater-agent": AgentCategory.REPOSITORY,
}

# All integrated agents (Phase 1.2 + Phase 1.3)
ALL_INTEGRATED_AGENTS = {**CORE_AGENTS, **EXTENDED_AGENTS}


def integrate_core_agents(
    manifest_path: Path | str | None = None,
) -> list[IntegratedAgent]:
    """Integrate all core agents from Phase 1.2.

    Args:
        manifest_path: Optional custom manifest path.

    Returns:
        List of integrated agents.
    """
    registry = AgentIntegrationRegistry(manifest_path)

    integrated = []
    for agent_id, category in CORE_AGENTS.items():
        capabilities = ["pattern_query", "learning_feedback", "session_state"]
        if category == AgentCategory.CI_CD:
            capabilities.append("ci_diagnosis")
        elif category == AgentCategory.TESTING:
            capabilities.append("coverage_tracking")
        elif category == AgentCategory.SECURITY:
            capabilities.append("vulnerability_analysis")

        agent = registry.register(agent_id, category, capabilities)
        integrated.append(agent)

    registry.save()
    return integrated


def integrate_extended_agents(
    manifest_path: Path | str | None = None,
) -> list[IntegratedAgent]:
    """Integrate all extended agents from Phase 1.3.

    This includes Documentation, RAG/ML, and Repository agents.

    Args:
        manifest_path: Optional custom manifest path.

    Returns:
        List of integrated agents.
    """
    registry = AgentIntegrationRegistry(manifest_path)

    integrated = []
    for agent_id, category in EXTENDED_AGENTS.items():
        capabilities = ["pattern_query", "learning_feedback", "session_state"]
        if category == AgentCategory.DOCUMENTATION:
            capabilities.append("doc_analysis")
        elif category == AgentCategory.RAG_ML:
            capabilities.append("ml_operations")
        elif category == AgentCategory.REPOSITORY:
            capabilities.append("repo_management")

        agent = registry.register(agent_id, category, capabilities)
        integrated.append(agent)

    registry.save()
    return integrated


def integrate_all_agents(
    manifest_path: Path | str | None = None,
) -> list[IntegratedAgent]:
    """Integrate all agents (Core + Extended) from Phases 1.2 and 1.3.

    Args:
        manifest_path: Optional custom manifest path.

    Returns:
        List of all integrated agents.
    """
    registry = AgentIntegrationRegistry(manifest_path)

    integrated = []
    for agent_id, category in ALL_INTEGRATED_AGENTS.items():
        capabilities = ["pattern_query", "learning_feedback", "session_state"]
        if category == AgentCategory.CI_CD:
            capabilities.append("ci_diagnosis")
        elif category == AgentCategory.TESTING:
            capabilities.append("coverage_tracking")
        elif category == AgentCategory.SECURITY:
            capabilities.append("vulnerability_analysis")
        elif category == AgentCategory.DOCUMENTATION:
            capabilities.append("doc_analysis")
        elif category == AgentCategory.RAG_ML:
            capabilities.append("ml_operations")
        elif category == AgentCategory.REPOSITORY:
            capabilities.append("repo_management")

        agent = registry.register(agent_id, category, capabilities)
        integrated.append(agent)

    registry.save()
    return integrated


def get_extended_agent_count() -> int:
    """Get the count of extended agents for Phase 1.3."""
    return len(EXTENDED_AGENTS)


def get_total_agent_count() -> int:
    """Get the total count of all integrated agents."""
    return len(ALL_INTEGRATED_AGENTS)


def get_brain_integration_section(agent_id: str, category: AgentCategory) -> str:
    """Generate the Cognitive Brain Integration section for an agent doc.

    Args:
        agent_id: The agent identifier.
        category: The agent category.

    Returns:
        Markdown section to add to agent documentation.
    """
    category_adapters = {
        AgentCategory.CI_CD: "CICDAdapter",
        AgentCategory.TESTING: "TestingAdapter",
        AgentCategory.SECURITY: "SecurityAdapter",
        AgentCategory.DOCUMENTATION: "DocsAdapter",
        AgentCategory.RAG_ML: "RAGMLAdapter",
        AgentCategory.REPOSITORY: "RepoAdapter",
        AgentCategory.OTHER: "BaseAdapter",
    }

    adapter = category_adapters.get(category, "BaseAdapter")

    return f"""

## 🧠 Cognitive Brain Integration

> **Status**: ✅ Integrated (Phase 1.2)
> **Category**: {category.value}
> **Adapter**: {adapter}

### Brain Capabilities

This agent is integrated with the Cognitive Brain and can:

- **Query Patterns**: Access historical issue patterns for faster diagnosis
- **Submit Learnings**: Report successful resolutions to improve future sessions
- **Share Session State**: Maintain context across agent transitions
- **Check Objective Alignment**: Verify actions align with repository objectives

### Usage in Agent Workflow

```python
from codex.cognitive.brain_interface import AgentBrainInterface

# Initialize brain interface for this agent
brain = AgentBrainInterface(agent_id="{agent_id}")

# 1. Query patterns before diagnosis
patterns = brain.query_patterns("symptom keywords here")
for pattern in patterns:
    logger.info(f"Pattern: {{pattern['id']}} (success: {{pattern['success_rate']}})")

# 2. Check objective alignment
alignment = brain.check_alignment("proposed action description")
if alignment["aligned"]:
    # Proceed with action
    pass

# 3. Report learning after resolution
brain.submit_learning(
    pattern_id="TFR-001",  # or create new pattern
    outcome="success",  # or "failure"
    context={{
        "symptom": "original error message",
        "resolution": "fix applied",
        "files_changed": ["path/to/file.py"]
    }}
)

# 4. Update session state
brain.write_session_state({{
    "last_action": "diagnosis complete",
    "findings": ["issue 1", "issue 2"],
    "next_steps": ["fix 1", "validate"]
}})
```

### Integration Pattern

```
┌─────────────────────────────────────────────────────┐
│                 {agent_id:^35} │
├─────────────────────────────────────────────────────┤
│  1. Agent Activated                                 │
│         ↓                                           │
│  2. Query Brain for Relevant Patterns               │
│         ↓                                           │
│  3. Perform Diagnosis/Action                        │
│         ↓                                           │
│  4. Submit Learning Feedback                        │
│         ↓                                           │
│  5. Update Session State                            │
└─────────────────────────────────────────────────────┘
```

### Related Documentation

- [Agent Brain Protocol](.codex/docs/AGENT_BRAIN_PROTOCOL.md)
- [Pattern Learning Store](.codex/cognitive_brain/pattern_learning_store.json)
- [Brain Interface API](src/codex/cognitive/brain_interface.py)

**Last Updated**: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

"""


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--integrate-core":
        agents = integrate_core_agents()
        logger.info(f"Integrated {len(agents)} core agents:")
        for agent in agents:
            logger.info(f"  - {agent.agent_id} ({agent.category.value})")
    elif len(sys.argv) > 1 and sys.argv[1] == "--integrate-extended":
        agents = integrate_extended_agents()
        logger.info(f"Integrated {len(agents)} extended agents:")
        for agent in agents:
            logger.info(f"  - {agent.agent_id} ({agent.category.value})")
    elif len(sys.argv) > 1 and sys.argv[1] == "--integrate-all":
        agents = integrate_all_agents()
        logger.info(f"Integrated {len(agents)} total agents:")
        for agent in agents:
            logger.info(f"  - {agent.agent_id} ({agent.category.value})")
    elif len(sys.argv) > 1 and sys.argv[1] == "--stats":
        registry = AgentIntegrationRegistry()
        stats = registry.get_stats()
        logger.info(json.dumps(stats, indent=2))
    else:
        logger.info("Usage:")
        logger.info("  python -m codex.cognitive.agent_integration --integrate-core")
        logger.info("  python -m codex.cognitive.agent_integration --integrate-extended")
        logger.info("  python -m codex.cognitive.agent_integration --integrate-all")
        logger.info("  python -m codex.cognitive.agent_integration --stats")
