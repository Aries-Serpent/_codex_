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

from .budget import TokenBudgetEnforcer

# Enhanced modules (v2)
from .clustering import SemanticClusterer
from .context_cache import ContextCache
from .deduplicator import SemanticDeduplicator
from .fingerprint import StatementFingerprinter
from .guardrails import LoopGuardrail
from .hierarchical_memory import HierarchicalMemory, MemoryItem, MemoryLayer
from .memory import ContextMemory
from .normalizer import ContextNormalizer
from .observability import ContextObserver
from .priority_queue import ContextPriorityQueue, Priority
from .pruning import PriorityPruner
from .sliding_window import SlidingWindowManager, WindowStrategy

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
    "HARD_TOKEN_CEILING",
    "SOFT_TOKEN_CAP",
    "SOFT_CAP_THRESHOLD",
]

# Token limits per Global Policies
HARD_TOKEN_CEILING = 64_000
SOFT_TOKEN_CAP = 56_000
SOFT_CAP_THRESHOLD = 0.90  # 90% of soft cap triggers summarization
