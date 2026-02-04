"""
Context Management System

Production-grade context tracking, deduplication, and token-budget enforcement
for agent loops and prompt assembly.

Core Modules:
- normalizer: Text normalization and standardization
- fingerprint: Statement fingerprinting for deduplication
- deduplicator: Semantic deduplication engine
- budget: Token budget enforcement
- pruning: Priority-based context pruning
- guardrails: Loop guardrails and recovery
- memory: External memory and chunking
- observability: Structured logging and metrics

Enhanced Modules (v2):
- clustering: Semantic clustering with embeddings support
- priority_queue: Priority queue with decay scoring
- sliding_window: Token window management
- hierarchical_memory: Episodic, semantic, and working memory layers
- context_cache: Static context caching across requests
- graph_memory: Entity-relationship graph storage
"""

from .normalizer import ContextNormalizer
from .fingerprint import StatementFingerprinter
from .deduplicator import SemanticDeduplicator
from .budget import TokenBudgetEnforcer
from .pruning import PriorityPruner
from .guardrails import LoopGuardrail
from .memory import ContextMemory
from .observability import ContextObserver

# Enhanced modules (v2)
from .clustering import SemanticClusterer
from .priority_queue import ContextPriorityQueue, Priority
from .sliding_window import SlidingWindowManager, WindowStrategy
from .hierarchical_memory import HierarchicalMemory, MemoryLayer, MemoryItem
from .context_cache import ContextCache

__all__ = [
    # Core modules
    "ContextNormalizer",
    "StatementFingerprinter",
    "SemanticDeduplicator",
    "TokenBudgetEnforcer",
    "PriorityPruner",
    "LoopGuardrail",
    "ContextMemory",
    "ContextObserver",
    # Enhanced modules (v2)
    "SemanticClusterer",
    "ContextPriorityQueue",
    "Priority",
    "SlidingWindowManager",
    "WindowStrategy",
    "HierarchicalMemory",
    "MemoryLayer",
    "MemoryItem",
    "ContextCache",
]

# Token limits per Global Policies
HARD_TOKEN_CEILING = 64_000
SOFT_TOKEN_CAP = 56_000
SOFT_CAP_THRESHOLD = 0.90  # 90% of soft cap triggers summarization
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
