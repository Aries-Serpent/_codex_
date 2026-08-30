"""
Adaptive Learning Module for Cognitive Brain.

This module implements reinforcement learning and meta-learning capabilities
to continuously improve decision-making strategies based on outcome analysis.

Components:
    - OutcomeAnalyzer: Extracts learnings from decision outcomes
    - StrategyOptimizer: RL-based strategy optimization (Pre-commit 3-4)
    - MetaLearner: Cross-domain knowledge transfer (Pre-commit 5-6)

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Continuous learning and strategy improvement

Timeline: 6 pre-commit to commit cycles
"""

from cognitive_brain.learning.outcome_analyzer import OutcomeAnalyzer
from cognitive_brain.learning.rl_algorithms import (
    DQN,
    PPO,
    QLearning,
    ReplayBuffer,
    RLAlgorithm,
)
from cognitive_brain.learning.strategy_optimizer import (
    AlgorithmType,
    StrategyMetrics,
    StrategyOptimizer,
)

__all__ = [
    "DQN",
    "PPO",
    "AlgorithmType",
    "OutcomeAnalyzer",
    "QLearning",
    "RLAlgorithm",
    "ReplayBuffer",
    "StrategyMetrics",
    "StrategyOptimizer",
]
