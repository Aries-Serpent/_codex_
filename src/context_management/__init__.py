"""
Context Management System

Production-grade context tracking, deduplication, and token-budget enforcement
for agent loops and prompt assembly.

Modules:
- normalizer: Text normalization and standardization
- fingerprint: Statement fingerprinting for deduplication
- deduplicator: Semantic deduplication engine
- budget: Token budget enforcement
- pruning: Priority-based context pruning
- guardrails: Loop guardrails and recovery
- memory: External memory and chunking
- observability: Structured logging and metrics
"""

from .normalizer import ContextNormalizer
from .fingerprint import StatementFingerprinter
from .deduplicator import SemanticDeduplicator
from .budget import TokenBudgetEnforcer
from .pruning import PriorityPruner
from .guardrails import LoopGuardrail
from .memory import ContextMemory
from .observability import ContextObserver

__all__ = [
    "ContextNormalizer",
    "StatementFingerprinter",
    "SemanticDeduplicator",
    "TokenBudgetEnforcer",
    "PriorityPruner",
    "LoopGuardrail",
    "ContextMemory",
    "ContextObserver",
]

# Token limits per Global Policies
HARD_TOKEN_CEILING = 64_000
SOFT_TOKEN_CAP = 56_000
SOFT_CAP_THRESHOLD = 0.90  # 90% of soft cap triggers summarization
