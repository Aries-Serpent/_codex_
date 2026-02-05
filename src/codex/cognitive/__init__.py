"""
Codex Cognitive Brain Module

This module provides the cognitive brain infrastructure for AI agent coordination,
including:
- AgentBrainInterface: Standard interface for agent-brain communication
- Pattern learning and retrieval
- Session state management
- Objective tracking
"""

from codex.cognitive.brain_interface import (
    AgentBrainInterface,
    AgentContext,
    PatternMatch,
    LearningFeedback,
    BrainResponse,
)

__all__ = [
    "AgentBrainInterface",
    "AgentContext",
    "PatternMatch",
    "LearningFeedback",
    "BrainResponse",
]

__version__ = "1.0.0"
