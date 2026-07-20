"""Memory module for codex_ml.

Provides short-term and long-term memory systems for cognitive operations,
including memory consolidation and lifecycle management.

Main Classes:
    - STMMemory: Short-term working memory
    - LTMMemory: Long-term persistent memory
    - MemoryConsolidation: STM to LTM consolidation engine
    - MemoryEntry: Individual memory entry
    - ConsolidationRecord: Record of consolidation operations
"""

from __future__ import annotations

from .consolidation import MemoryConsolidation
from .ltm import LTMMemory
from .schemas import ConsolidationRecord, MemoryEntry
from .stm import STMMemory

__all__ = [
    "STMMemory",
    "LTMMemory",
    "MemoryConsolidation",
    "MemoryEntry",
    "ConsolidationRecord",
]
