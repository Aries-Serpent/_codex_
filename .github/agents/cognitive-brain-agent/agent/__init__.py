"""
Cognitive Brain Agent - GitHub Copilot Agent for Cognitive Enhancement.

This agent integrates the Cognitive Brain system with GitHub Copilot's
agent framework for enhanced pattern recognition and learning.
"""
from .brain_processor import CognitiveBrainProcessor
from .pda_engine import PDAEngine
from .aftermath_handler import AfterMathHandler
from .learning_integrator import LearningIntegrator

__all__ = [
    "CognitiveBrainProcessor",
    "PDAEngine",
    "AfterMathHandler",
    "LearningIntegrator",
]

__version__ = "0.1.0"
