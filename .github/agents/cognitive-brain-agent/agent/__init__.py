"""
Cognitive Brain Agent - GitHub Copilot Agent for Cognitive Enhancement.

This agent integrates the Cognitive Brain system with GitHub Copilot's
agent framework for enhanced pattern recognition and learning.
"""
from .aftermath_handler import AfterMathHandler
from .brain_processor import CognitiveBrainProcessor
from .learning_integrator import LearningIntegrator
from .pda_engine import PDAEngine

__all__ = [
    "CognitiveBrainProcessor",
    "PDAEngine",
    "AfterMathHandler",
    "LearningIntegrator",
]

__version__ = "0.1.0"
