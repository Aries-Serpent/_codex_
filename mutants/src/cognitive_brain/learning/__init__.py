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
    "OutcomeAnalyzer",
    "RLAlgorithm",
    "QLearning",
    "DQN",
    "PPO",
    "ReplayBuffer",
    "StrategyOptimizer",
    "AlgorithmType",
    "StrategyMetrics",
]
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
