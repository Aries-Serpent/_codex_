"""
Cognitive Agent Core Framework
Unified base classes and utilities for all cognitive agents in the _codex_ ecosystem.

This module provides:
- CognitiveAgent: Abstract base class with PDA Loop pattern
- CognitiveBrain: Centralized learning and storage (SQLite)
- PatternRecognizer: Automated pattern detection
- AgentOrchestrator: Multi-agent workflow coordination

#AFTERMATH_PATTERN_IDENTIFIED: unified_agent_framework
All agents share common patterns for consistency and learning.
"""

from .base_agent import CognitiveAgent
from .cognitive_brain import CognitiveBrain
from .pattern_recognizer import (
    PatternRecognizer,
    PatternMatcher,
    Pattern,
    ExceptionPatternMatcher,
    ImportPatternMatcher,
    TestPatternMatcher,
    DocstringPatternMatcher,
)
from .orchestrator import (
    AgentOrchestrator,
    AgentTask,
    TaskStatus,
)

__all__ = [
    # Base classes
    "CognitiveAgent",
    "CognitiveBrain",
    
    # Pattern recognition
    "PatternRecognizer",
    "PatternMatcher",
    "Pattern",
    "ExceptionPatternMatcher",
    "ImportPatternMatcher",
    "TestPatternMatcher",
    "DocstringPatternMatcher",
    
    # Orchestration
    "AgentOrchestrator",
    "AgentTask",
    "TaskStatus",
]

__version__ = "1.0.0"
