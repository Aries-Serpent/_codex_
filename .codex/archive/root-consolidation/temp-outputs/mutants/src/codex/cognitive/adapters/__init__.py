"""
Cognitive Brain Adapters Module

This module provides adapter classes for integrating specific agent types
with the AgentBrainInterface.

Adapters provide category-specific functionality while maintaining
the standard interface contract.
"""

from codex.cognitive.brain_interface import (
    AgentBrainInterface,
    AgentCategory,
    AgentContext,
    PatternMatch,
)

__all__ = [
    "AgentBrainInterface",
    "AgentCategory",
    "AgentContext",
    "BaseBrainAdapter",
    "CICDAdapter",
    "PatternMatch",
    "SecurityAdapter",
    "TestingAdapter",
]


class BaseBrainAdapter:
    """
    Base adapter class for category-specific brain integration.

    Subclasses can override methods to provide category-specific
    behavior while maintaining the standard interface.
    """

    def __init__(self, agent_id: str, **kwargs) -> None:
        """
        Initialize the adapter.

        Args:
            agent_id: Unique identifier for the agent
            **kwargs: Additional arguments passed to AgentBrainInterface
        """
        self.brain = AgentBrainInterface(agent_id=agent_id, **kwargs)
        self.agent_id = agent_id

    def query_patterns(self, symptoms, **kwargs) -> None:
        """Query patterns with optional category filtering."""
        return self.brain.query_patterns(symptoms, **kwargs)

    def submit_learning(self, pattern_id: str, outcome: str, **kwargs) -> None:
        """Submit learning feedback."""
        return self.brain.submit_learning(pattern_id, outcome, **kwargs)

    def diagnose(self, symptoms, **kwargs) -> None:
        """Perform diagnosis."""
        return self.brain.diagnose(symptoms, **kwargs)


class CICDAdapter(BaseBrainAdapter):
    """
    Adapter for CI/CD agents.

    Provides CI/CD-specific pattern querying and learning submission.
    """

    CATEGORY = "ci_cd"

    def query_patterns(self, symptoms, **kwargs) -> None:
        """Query CI/CD-specific patterns."""
        kwargs.setdefault("category", self.CATEGORY)
        return super().query_patterns(symptoms, **kwargs)


class TestingAdapter(BaseBrainAdapter):
    """
    Adapter for testing agents.

    Provides testing-specific pattern querying and learning submission.
    """

    CATEGORY = "testing"

    def query_patterns(self, symptoms, **kwargs) -> None:
        """Query testing-specific patterns."""
        kwargs.setdefault("category", self.CATEGORY)
        return super().query_patterns(symptoms, **kwargs)


class SecurityAdapter(BaseBrainAdapter):
    """
    Adapter for security agents.

    Provides security-specific pattern querying and learning submission.
    """

    CATEGORY = "security"

    def query_patterns(self, symptoms, **kwargs) -> None:
        """Query security-specific patterns."""
        kwargs.setdefault("category", self.CATEGORY)
        return super().query_patterns(symptoms, **kwargs)
