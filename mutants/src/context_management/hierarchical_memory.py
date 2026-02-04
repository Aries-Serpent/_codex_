"""
Hierarchical Memory System

Implements three-layer memory architecture based on cognitive science research:
- Episodic Memory: Session-specific context and interactions
- Semantic Memory: Long-term knowledge and learned patterns
- Working Memory: Immediate context for current task

Reference: Anthropic 2024 - Effective Context Engineering for AI Agents
"""

import hashlib
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
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


class MemoryLayer(Enum):
    """Memory layer types."""

    WORKING = "working"  # Immediate context (high priority, limited capacity)
    EPISODIC = "episodic"  # Session-specific (medium priority, session-scoped)
    SEMANTIC = "semantic"  # Long-term knowledge (low priority, persistent)


@dataclass
class MemoryItem:
    """An item stored in memory."""

    content: str
    layer: MemoryLayer
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = 1.0
    decay_rate: float = 0.1
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]

    @property
    def age_seconds(self) -> float:
        """Age of item in seconds."""
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def staleness_seconds(self) -> float:
        """Time since last access."""
        return (datetime.now() - self.last_accessed).total_seconds()

    @property
    def effective_importance(self) -> float:
        """
        Calculate importance with temporal decay.

        Implements exponential decay based on age and staleness.
        """
        # Age decay (half-life varies by layer)
        if self.layer == MemoryLayer.WORKING:
            half_life_hours = 0.5  # 30 minutes
        elif self.layer == MemoryLayer.EPISODIC:
            half_life_hours = 24  # 1 day
        else:
            half_life_hours = 168  # 1 week

        age_hours = self.age_seconds / 3600
        age_factor = math.exp(-0.693 * age_hours / half_life_hours)

        # Access recency boost
        stale_hours = self.staleness_seconds / 3600
        recency_factor = math.exp(-0.693 * stale_hours / (half_life_hours / 2))

        # Access frequency boost (log scale)
        frequency_boost = math.log1p(self.access_count) * 0.1

        return self.importance * age_factor * recency_factor + frequency_boost

    @property
    def token_estimate(self) -> int:
        """Estimate token count."""
        return len(self.content) // 4 + 1


@dataclass
class MemoryStats:
    """Statistics for a memory layer."""

    item_count: int
    total_tokens: int
    average_importance: float
    oldest_age_hours: float
    most_accessed_count: int


class HierarchicalMemory:
    """
    Three-layer hierarchical memory system.

    Provides:
    - Automatic promotion/demotion between layers
    - Temporal decay for staleness handling
    - Importance-based retrieval
    - Cross-layer deduplication
    """

    # Default capacity limits (in tokens)
    DEFAULT_WORKING_LIMIT = 8_000
    DEFAULT_EPISODIC_LIMIT = 32_000
    DEFAULT_SEMANTIC_LIMIT = 64_000

    def xǁHierarchicalMemoryǁ__init____mutmut_orig(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_1(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = False,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_2(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = False,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_3(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = None
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_4(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = None
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_5(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = None

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_6(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = None

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def xǁHierarchicalMemoryǁ__init____mutmut_7(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = None
    
    xǁHierarchicalMemoryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁ__init____mutmut_1': xǁHierarchicalMemoryǁ__init____mutmut_1, 
        'xǁHierarchicalMemoryǁ__init____mutmut_2': xǁHierarchicalMemoryǁ__init____mutmut_2, 
        'xǁHierarchicalMemoryǁ__init____mutmut_3': xǁHierarchicalMemoryǁ__init____mutmut_3, 
        'xǁHierarchicalMemoryǁ__init____mutmut_4': xǁHierarchicalMemoryǁ__init____mutmut_4, 
        'xǁHierarchicalMemoryǁ__init____mutmut_5': xǁHierarchicalMemoryǁ__init____mutmut_5, 
        'xǁHierarchicalMemoryǁ__init____mutmut_6': xǁHierarchicalMemoryǁ__init____mutmut_6, 
        'xǁHierarchicalMemoryǁ__init____mutmut_7': xǁHierarchicalMemoryǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁ__init____mutmut_orig)
    xǁHierarchicalMemoryǁ__init____mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁ__init__'

    def xǁHierarchicalMemoryǁstore__mutmut_orig(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_1(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 2.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_2(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = None
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_3(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(None).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_4(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:17]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_5(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash not in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_6(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = None
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_7(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = None
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_8(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(None)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_9(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = None
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_10(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count = 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_11(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count -= 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_12(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 2
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_13(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return False, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_14(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = None

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_15(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=None,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_16(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=None,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_17(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=None,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_18(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=None,
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_19(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=None,
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_20(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=None,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_21(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_22(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_23(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_24(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_25(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_26(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_27(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags and [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_28(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata and {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_29(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = None

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_30(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(None, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_31(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, None)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_32(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_33(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, )

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_34(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = None
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_35(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = None

        return True, warning

    def xǁHierarchicalMemoryǁstore__mutmut_36(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now()
                existing_item.access_count += 1
                return True, f"Duplicate found in {existing_layer.value} memory, updated access"

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return False, warning
    
    xǁHierarchicalMemoryǁstore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁstore__mutmut_1': xǁHierarchicalMemoryǁstore__mutmut_1, 
        'xǁHierarchicalMemoryǁstore__mutmut_2': xǁHierarchicalMemoryǁstore__mutmut_2, 
        'xǁHierarchicalMemoryǁstore__mutmut_3': xǁHierarchicalMemoryǁstore__mutmut_3, 
        'xǁHierarchicalMemoryǁstore__mutmut_4': xǁHierarchicalMemoryǁstore__mutmut_4, 
        'xǁHierarchicalMemoryǁstore__mutmut_5': xǁHierarchicalMemoryǁstore__mutmut_5, 
        'xǁHierarchicalMemoryǁstore__mutmut_6': xǁHierarchicalMemoryǁstore__mutmut_6, 
        'xǁHierarchicalMemoryǁstore__mutmut_7': xǁHierarchicalMemoryǁstore__mutmut_7, 
        'xǁHierarchicalMemoryǁstore__mutmut_8': xǁHierarchicalMemoryǁstore__mutmut_8, 
        'xǁHierarchicalMemoryǁstore__mutmut_9': xǁHierarchicalMemoryǁstore__mutmut_9, 
        'xǁHierarchicalMemoryǁstore__mutmut_10': xǁHierarchicalMemoryǁstore__mutmut_10, 
        'xǁHierarchicalMemoryǁstore__mutmut_11': xǁHierarchicalMemoryǁstore__mutmut_11, 
        'xǁHierarchicalMemoryǁstore__mutmut_12': xǁHierarchicalMemoryǁstore__mutmut_12, 
        'xǁHierarchicalMemoryǁstore__mutmut_13': xǁHierarchicalMemoryǁstore__mutmut_13, 
        'xǁHierarchicalMemoryǁstore__mutmut_14': xǁHierarchicalMemoryǁstore__mutmut_14, 
        'xǁHierarchicalMemoryǁstore__mutmut_15': xǁHierarchicalMemoryǁstore__mutmut_15, 
        'xǁHierarchicalMemoryǁstore__mutmut_16': xǁHierarchicalMemoryǁstore__mutmut_16, 
        'xǁHierarchicalMemoryǁstore__mutmut_17': xǁHierarchicalMemoryǁstore__mutmut_17, 
        'xǁHierarchicalMemoryǁstore__mutmut_18': xǁHierarchicalMemoryǁstore__mutmut_18, 
        'xǁHierarchicalMemoryǁstore__mutmut_19': xǁHierarchicalMemoryǁstore__mutmut_19, 
        'xǁHierarchicalMemoryǁstore__mutmut_20': xǁHierarchicalMemoryǁstore__mutmut_20, 
        'xǁHierarchicalMemoryǁstore__mutmut_21': xǁHierarchicalMemoryǁstore__mutmut_21, 
        'xǁHierarchicalMemoryǁstore__mutmut_22': xǁHierarchicalMemoryǁstore__mutmut_22, 
        'xǁHierarchicalMemoryǁstore__mutmut_23': xǁHierarchicalMemoryǁstore__mutmut_23, 
        'xǁHierarchicalMemoryǁstore__mutmut_24': xǁHierarchicalMemoryǁstore__mutmut_24, 
        'xǁHierarchicalMemoryǁstore__mutmut_25': xǁHierarchicalMemoryǁstore__mutmut_25, 
        'xǁHierarchicalMemoryǁstore__mutmut_26': xǁHierarchicalMemoryǁstore__mutmut_26, 
        'xǁHierarchicalMemoryǁstore__mutmut_27': xǁHierarchicalMemoryǁstore__mutmut_27, 
        'xǁHierarchicalMemoryǁstore__mutmut_28': xǁHierarchicalMemoryǁstore__mutmut_28, 
        'xǁHierarchicalMemoryǁstore__mutmut_29': xǁHierarchicalMemoryǁstore__mutmut_29, 
        'xǁHierarchicalMemoryǁstore__mutmut_30': xǁHierarchicalMemoryǁstore__mutmut_30, 
        'xǁHierarchicalMemoryǁstore__mutmut_31': xǁHierarchicalMemoryǁstore__mutmut_31, 
        'xǁHierarchicalMemoryǁstore__mutmut_32': xǁHierarchicalMemoryǁstore__mutmut_32, 
        'xǁHierarchicalMemoryǁstore__mutmut_33': xǁHierarchicalMemoryǁstore__mutmut_33, 
        'xǁHierarchicalMemoryǁstore__mutmut_34': xǁHierarchicalMemoryǁstore__mutmut_34, 
        'xǁHierarchicalMemoryǁstore__mutmut_35': xǁHierarchicalMemoryǁstore__mutmut_35, 
        'xǁHierarchicalMemoryǁstore__mutmut_36': xǁHierarchicalMemoryǁstore__mutmut_36
    }
    
    def store(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁstore__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁstore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁstore__mutmut_orig)
    xǁHierarchicalMemoryǁstore__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁstore'

    def xǁHierarchicalMemoryǁretrieve__mutmut_orig(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_1(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 1.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_2(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 11,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_3(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = None

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_4(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = None

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_5(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(None)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_6(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance <= min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_7(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    break

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_8(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags or not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_9(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_10(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(None):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_11(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t not in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_12(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    break

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_13(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query or query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_14(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.upper() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_15(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_16(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.upper():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_17(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    break

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_18(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(None)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_19(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=None, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_20(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=None)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_21(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_22(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, )

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_23(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: None, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_24(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=False)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_25(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = None
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_26(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = None
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_27(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 1
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_28(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens - item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_29(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate < max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_30(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(None)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_31(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens = item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_32(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens -= item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_33(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = None

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_34(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = None

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_35(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = None
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_36(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count = 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_37(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count -= 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def xǁHierarchicalMemoryǁretrieve__mutmut_38(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now()
            item.access_count += 2

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results
    
    xǁHierarchicalMemoryǁretrieve__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁretrieve__mutmut_1': xǁHierarchicalMemoryǁretrieve__mutmut_1, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_2': xǁHierarchicalMemoryǁretrieve__mutmut_2, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_3': xǁHierarchicalMemoryǁretrieve__mutmut_3, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_4': xǁHierarchicalMemoryǁretrieve__mutmut_4, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_5': xǁHierarchicalMemoryǁretrieve__mutmut_5, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_6': xǁHierarchicalMemoryǁretrieve__mutmut_6, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_7': xǁHierarchicalMemoryǁretrieve__mutmut_7, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_8': xǁHierarchicalMemoryǁretrieve__mutmut_8, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_9': xǁHierarchicalMemoryǁretrieve__mutmut_9, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_10': xǁHierarchicalMemoryǁretrieve__mutmut_10, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_11': xǁHierarchicalMemoryǁretrieve__mutmut_11, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_12': xǁHierarchicalMemoryǁretrieve__mutmut_12, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_13': xǁHierarchicalMemoryǁretrieve__mutmut_13, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_14': xǁHierarchicalMemoryǁretrieve__mutmut_14, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_15': xǁHierarchicalMemoryǁretrieve__mutmut_15, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_16': xǁHierarchicalMemoryǁretrieve__mutmut_16, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_17': xǁHierarchicalMemoryǁretrieve__mutmut_17, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_18': xǁHierarchicalMemoryǁretrieve__mutmut_18, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_19': xǁHierarchicalMemoryǁretrieve__mutmut_19, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_20': xǁHierarchicalMemoryǁretrieve__mutmut_20, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_21': xǁHierarchicalMemoryǁretrieve__mutmut_21, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_22': xǁHierarchicalMemoryǁretrieve__mutmut_22, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_23': xǁHierarchicalMemoryǁretrieve__mutmut_23, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_24': xǁHierarchicalMemoryǁretrieve__mutmut_24, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_25': xǁHierarchicalMemoryǁretrieve__mutmut_25, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_26': xǁHierarchicalMemoryǁretrieve__mutmut_26, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_27': xǁHierarchicalMemoryǁretrieve__mutmut_27, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_28': xǁHierarchicalMemoryǁretrieve__mutmut_28, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_29': xǁHierarchicalMemoryǁretrieve__mutmut_29, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_30': xǁHierarchicalMemoryǁretrieve__mutmut_30, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_31': xǁHierarchicalMemoryǁretrieve__mutmut_31, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_32': xǁHierarchicalMemoryǁretrieve__mutmut_32, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_33': xǁHierarchicalMemoryǁretrieve__mutmut_33, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_34': xǁHierarchicalMemoryǁretrieve__mutmut_34, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_35': xǁHierarchicalMemoryǁretrieve__mutmut_35, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_36': xǁHierarchicalMemoryǁretrieve__mutmut_36, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_37': xǁHierarchicalMemoryǁretrieve__mutmut_37, 
        'xǁHierarchicalMemoryǁretrieve__mutmut_38': xǁHierarchicalMemoryǁretrieve__mutmut_38
    }
    
    def retrieve(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁretrieve__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁretrieve__mutmut_mutants"), args, kwargs, self)
        return result 
    
    retrieve.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁretrieve__mutmut_orig)
    xǁHierarchicalMemoryǁretrieve__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁretrieve'

    def xǁHierarchicalMemoryǁget_working_context__mutmut_orig(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=100,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_1(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = None
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_2(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=None,
            max_items=100,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_3(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=None,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_4(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=100,
            max_tokens=None,
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_5(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            max_items=100,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_6(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_7(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=100,
            )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_8(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=101,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def xǁHierarchicalMemoryǁget_working_context__mutmut_9(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=100,
            max_tokens=max_tokens and self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]
    
    xǁHierarchicalMemoryǁget_working_context__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁget_working_context__mutmut_1': xǁHierarchicalMemoryǁget_working_context__mutmut_1, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_2': xǁHierarchicalMemoryǁget_working_context__mutmut_2, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_3': xǁHierarchicalMemoryǁget_working_context__mutmut_3, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_4': xǁHierarchicalMemoryǁget_working_context__mutmut_4, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_5': xǁHierarchicalMemoryǁget_working_context__mutmut_5, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_6': xǁHierarchicalMemoryǁget_working_context__mutmut_6, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_7': xǁHierarchicalMemoryǁget_working_context__mutmut_7, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_8': xǁHierarchicalMemoryǁget_working_context__mutmut_8, 
        'xǁHierarchicalMemoryǁget_working_context__mutmut_9': xǁHierarchicalMemoryǁget_working_context__mutmut_9
    }
    
    def get_working_context(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁget_working_context__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁget_working_context__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_working_context.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁget_working_context__mutmut_orig)
    xǁHierarchicalMemoryǁget_working_context__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁget_working_context'

    def xǁHierarchicalMemoryǁpromote__mutmut_orig(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_1(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_2(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return True

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_3(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = None

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_4(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = None

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_5(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 2, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_6(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 3, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_7(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 4}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_8(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] < layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_9(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return True  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_10(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = None
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_11(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(None)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_12(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = None

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_13(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(None, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_14(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, None)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_15(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_16(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, )

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_17(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = None
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_18(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = None

        return True

    def xǁHierarchicalMemoryǁpromote__mutmut_19(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return False
    
    xǁHierarchicalMemoryǁpromote__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁpromote__mutmut_1': xǁHierarchicalMemoryǁpromote__mutmut_1, 
        'xǁHierarchicalMemoryǁpromote__mutmut_2': xǁHierarchicalMemoryǁpromote__mutmut_2, 
        'xǁHierarchicalMemoryǁpromote__mutmut_3': xǁHierarchicalMemoryǁpromote__mutmut_3, 
        'xǁHierarchicalMemoryǁpromote__mutmut_4': xǁHierarchicalMemoryǁpromote__mutmut_4, 
        'xǁHierarchicalMemoryǁpromote__mutmut_5': xǁHierarchicalMemoryǁpromote__mutmut_5, 
        'xǁHierarchicalMemoryǁpromote__mutmut_6': xǁHierarchicalMemoryǁpromote__mutmut_6, 
        'xǁHierarchicalMemoryǁpromote__mutmut_7': xǁHierarchicalMemoryǁpromote__mutmut_7, 
        'xǁHierarchicalMemoryǁpromote__mutmut_8': xǁHierarchicalMemoryǁpromote__mutmut_8, 
        'xǁHierarchicalMemoryǁpromote__mutmut_9': xǁHierarchicalMemoryǁpromote__mutmut_9, 
        'xǁHierarchicalMemoryǁpromote__mutmut_10': xǁHierarchicalMemoryǁpromote__mutmut_10, 
        'xǁHierarchicalMemoryǁpromote__mutmut_11': xǁHierarchicalMemoryǁpromote__mutmut_11, 
        'xǁHierarchicalMemoryǁpromote__mutmut_12': xǁHierarchicalMemoryǁpromote__mutmut_12, 
        'xǁHierarchicalMemoryǁpromote__mutmut_13': xǁHierarchicalMemoryǁpromote__mutmut_13, 
        'xǁHierarchicalMemoryǁpromote__mutmut_14': xǁHierarchicalMemoryǁpromote__mutmut_14, 
        'xǁHierarchicalMemoryǁpromote__mutmut_15': xǁHierarchicalMemoryǁpromote__mutmut_15, 
        'xǁHierarchicalMemoryǁpromote__mutmut_16': xǁHierarchicalMemoryǁpromote__mutmut_16, 
        'xǁHierarchicalMemoryǁpromote__mutmut_17': xǁHierarchicalMemoryǁpromote__mutmut_17, 
        'xǁHierarchicalMemoryǁpromote__mutmut_18': xǁHierarchicalMemoryǁpromote__mutmut_18, 
        'xǁHierarchicalMemoryǁpromote__mutmut_19': xǁHierarchicalMemoryǁpromote__mutmut_19
    }
    
    def promote(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁpromote__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁpromote__mutmut_mutants"), args, kwargs, self)
        return result 
    
    promote.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁpromote__mutmut_orig)
    xǁHierarchicalMemoryǁpromote__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁpromote'

    def xǁHierarchicalMemoryǁdemote__mutmut_orig(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_1(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_2(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return True

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_3(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = None

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_4(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = None

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_5(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 2, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_6(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 3, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_7(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 4}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_8(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] > layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_9(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return True  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_10(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = None
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_11(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(None)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_12(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = None

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_13(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(None, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_14(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, None)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_15(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_16(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, )

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_17(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = None
        self._hash_to_layer[content_hash] = target_layer

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_18(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = None

        return True

    def xǁHierarchicalMemoryǁdemote__mutmut_19(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {MemoryLayer.SEMANTIC: 1, MemoryLayer.EPISODIC: 2, MemoryLayer.WORKING: 3}

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return False
    
    xǁHierarchicalMemoryǁdemote__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁdemote__mutmut_1': xǁHierarchicalMemoryǁdemote__mutmut_1, 
        'xǁHierarchicalMemoryǁdemote__mutmut_2': xǁHierarchicalMemoryǁdemote__mutmut_2, 
        'xǁHierarchicalMemoryǁdemote__mutmut_3': xǁHierarchicalMemoryǁdemote__mutmut_3, 
        'xǁHierarchicalMemoryǁdemote__mutmut_4': xǁHierarchicalMemoryǁdemote__mutmut_4, 
        'xǁHierarchicalMemoryǁdemote__mutmut_5': xǁHierarchicalMemoryǁdemote__mutmut_5, 
        'xǁHierarchicalMemoryǁdemote__mutmut_6': xǁHierarchicalMemoryǁdemote__mutmut_6, 
        'xǁHierarchicalMemoryǁdemote__mutmut_7': xǁHierarchicalMemoryǁdemote__mutmut_7, 
        'xǁHierarchicalMemoryǁdemote__mutmut_8': xǁHierarchicalMemoryǁdemote__mutmut_8, 
        'xǁHierarchicalMemoryǁdemote__mutmut_9': xǁHierarchicalMemoryǁdemote__mutmut_9, 
        'xǁHierarchicalMemoryǁdemote__mutmut_10': xǁHierarchicalMemoryǁdemote__mutmut_10, 
        'xǁHierarchicalMemoryǁdemote__mutmut_11': xǁHierarchicalMemoryǁdemote__mutmut_11, 
        'xǁHierarchicalMemoryǁdemote__mutmut_12': xǁHierarchicalMemoryǁdemote__mutmut_12, 
        'xǁHierarchicalMemoryǁdemote__mutmut_13': xǁHierarchicalMemoryǁdemote__mutmut_13, 
        'xǁHierarchicalMemoryǁdemote__mutmut_14': xǁHierarchicalMemoryǁdemote__mutmut_14, 
        'xǁHierarchicalMemoryǁdemote__mutmut_15': xǁHierarchicalMemoryǁdemote__mutmut_15, 
        'xǁHierarchicalMemoryǁdemote__mutmut_16': xǁHierarchicalMemoryǁdemote__mutmut_16, 
        'xǁHierarchicalMemoryǁdemote__mutmut_17': xǁHierarchicalMemoryǁdemote__mutmut_17, 
        'xǁHierarchicalMemoryǁdemote__mutmut_18': xǁHierarchicalMemoryǁdemote__mutmut_18, 
        'xǁHierarchicalMemoryǁdemote__mutmut_19': xǁHierarchicalMemoryǁdemote__mutmut_19
    }
    
    def demote(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁdemote__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁdemote__mutmut_mutants"), args, kwargs, self)
        return result 
    
    demote.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁdemote__mutmut_orig)
    xǁHierarchicalMemoryǁdemote__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁdemote'

    def xǁHierarchicalMemoryǁclear_layer__mutmut_orig(self, layer: MemoryLayer):
        """Clear all items from a layer."""
        for content_hash in list(self._memory[layer].keys()):
            del self._hash_to_layer[content_hash]
        self._memory[layer].clear()

    def xǁHierarchicalMemoryǁclear_layer__mutmut_1(self, layer: MemoryLayer):
        """Clear all items from a layer."""
        for content_hash in list(None):
            del self._hash_to_layer[content_hash]
        self._memory[layer].clear()
    
    xǁHierarchicalMemoryǁclear_layer__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁclear_layer__mutmut_1': xǁHierarchicalMemoryǁclear_layer__mutmut_1
    }
    
    def clear_layer(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁclear_layer__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁclear_layer__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_layer.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁclear_layer__mutmut_orig)
    xǁHierarchicalMemoryǁclear_layer__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁclear_layer'

    def xǁHierarchicalMemoryǁclear_all__mutmut_orig(self):
        """Clear all memory layers."""
        for layer in MemoryLayer:
            self.clear_layer(layer)

    def xǁHierarchicalMemoryǁclear_all__mutmut_1(self):
        """Clear all memory layers."""
        for layer in MemoryLayer:
            self.clear_layer(None)
    
    xǁHierarchicalMemoryǁclear_all__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁclear_all__mutmut_1': xǁHierarchicalMemoryǁclear_all__mutmut_1
    }
    
    def clear_all(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁclear_all__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁclear_all__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_all.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁclear_all__mutmut_orig)
    xǁHierarchicalMemoryǁclear_all__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁclear_all'

    def xǁHierarchicalMemoryǁget_stats__mutmut_orig(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_1(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = None
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_2(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = None

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_3(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(None)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_4(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = None
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_5(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(None)
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_6(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_7(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = None
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_8(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=None,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_9(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=None,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_10(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=None,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_11(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=None,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_12(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=None,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_13(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_14(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_15(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_16(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_17(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_18(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=1,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_19(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=1,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_20(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=1.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_21(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=1.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_22(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=1,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_23(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = None
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_24(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(None)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_25(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = None
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_26(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) * len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_27(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(None) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_28(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = None
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_29(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) * 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_30(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(None) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_31(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3601
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_32(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = None

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_33(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(None)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_34(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = None

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_35(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=None,
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_36(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=None,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_37(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=None,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_38(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=None,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_39(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=None,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_40(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_41(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_42(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_43(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    most_accessed_count=most_accessed,
                )

        return stats

    def xǁHierarchicalMemoryǁget_stats__mutmut_44(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    )

        return stats
    
    xǁHierarchicalMemoryǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁget_stats__mutmut_1': xǁHierarchicalMemoryǁget_stats__mutmut_1, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_2': xǁHierarchicalMemoryǁget_stats__mutmut_2, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_3': xǁHierarchicalMemoryǁget_stats__mutmut_3, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_4': xǁHierarchicalMemoryǁget_stats__mutmut_4, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_5': xǁHierarchicalMemoryǁget_stats__mutmut_5, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_6': xǁHierarchicalMemoryǁget_stats__mutmut_6, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_7': xǁHierarchicalMemoryǁget_stats__mutmut_7, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_8': xǁHierarchicalMemoryǁget_stats__mutmut_8, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_9': xǁHierarchicalMemoryǁget_stats__mutmut_9, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_10': xǁHierarchicalMemoryǁget_stats__mutmut_10, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_11': xǁHierarchicalMemoryǁget_stats__mutmut_11, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_12': xǁHierarchicalMemoryǁget_stats__mutmut_12, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_13': xǁHierarchicalMemoryǁget_stats__mutmut_13, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_14': xǁHierarchicalMemoryǁget_stats__mutmut_14, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_15': xǁHierarchicalMemoryǁget_stats__mutmut_15, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_16': xǁHierarchicalMemoryǁget_stats__mutmut_16, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_17': xǁHierarchicalMemoryǁget_stats__mutmut_17, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_18': xǁHierarchicalMemoryǁget_stats__mutmut_18, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_19': xǁHierarchicalMemoryǁget_stats__mutmut_19, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_20': xǁHierarchicalMemoryǁget_stats__mutmut_20, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_21': xǁHierarchicalMemoryǁget_stats__mutmut_21, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_22': xǁHierarchicalMemoryǁget_stats__mutmut_22, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_23': xǁHierarchicalMemoryǁget_stats__mutmut_23, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_24': xǁHierarchicalMemoryǁget_stats__mutmut_24, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_25': xǁHierarchicalMemoryǁget_stats__mutmut_25, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_26': xǁHierarchicalMemoryǁget_stats__mutmut_26, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_27': xǁHierarchicalMemoryǁget_stats__mutmut_27, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_28': xǁHierarchicalMemoryǁget_stats__mutmut_28, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_29': xǁHierarchicalMemoryǁget_stats__mutmut_29, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_30': xǁHierarchicalMemoryǁget_stats__mutmut_30, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_31': xǁHierarchicalMemoryǁget_stats__mutmut_31, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_32': xǁHierarchicalMemoryǁget_stats__mutmut_32, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_33': xǁHierarchicalMemoryǁget_stats__mutmut_33, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_34': xǁHierarchicalMemoryǁget_stats__mutmut_34, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_35': xǁHierarchicalMemoryǁget_stats__mutmut_35, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_36': xǁHierarchicalMemoryǁget_stats__mutmut_36, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_37': xǁHierarchicalMemoryǁget_stats__mutmut_37, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_38': xǁHierarchicalMemoryǁget_stats__mutmut_38, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_39': xǁHierarchicalMemoryǁget_stats__mutmut_39, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_40': xǁHierarchicalMemoryǁget_stats__mutmut_40, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_41': xǁHierarchicalMemoryǁget_stats__mutmut_41, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_42': xǁHierarchicalMemoryǁget_stats__mutmut_42, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_43': xǁHierarchicalMemoryǁget_stats__mutmut_43, 
        'xǁHierarchicalMemoryǁget_stats__mutmut_44': xǁHierarchicalMemoryǁget_stats__mutmut_44
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁget_stats__mutmut_orig)
    xǁHierarchicalMemoryǁget_stats__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁget_stats'

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_orig(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_1(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = None
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_2(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(None)
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_3(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = None

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_4(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens - needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_5(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens < limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_6(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = None
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_7(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 1
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_8(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = None

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_9(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(None, key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_10(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=None)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_11(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_12(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), )

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_13(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: None)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_14(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit or items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_15(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens - needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_16(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens >= limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_17(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = None

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_18(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(None)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_19(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(1)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_20(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote or layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_21(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer == MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_22(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = None
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_23(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer != MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_24(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(None, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_25(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, None)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_26(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_27(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, )
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_28(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens = item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_29(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens += item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_30(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count = 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_31(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count -= 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_32(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 2

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_33(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count >= 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_34(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 1:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None
    
    xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_1': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_1, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_2': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_2, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_3': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_3, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_4': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_4, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_5': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_5, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_6': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_6, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_7': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_7, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_8': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_8, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_9': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_9, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_10': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_10, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_11': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_11, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_12': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_12, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_13': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_13, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_14': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_14, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_15': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_15, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_16': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_16, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_17': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_17, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_18': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_18, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_19': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_19, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_20': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_20, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_21': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_21, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_22': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_22, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_23': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_23, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_24': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_24, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_25': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_25, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_26': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_26, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_27': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_27, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_28': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_28, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_29': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_29, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_30': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_30, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_31': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_31, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_32': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_32, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_33': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_33, 
        'xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_34': xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_34
    }
    
    def _ensure_capacity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _ensure_capacity.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_orig)
    xǁHierarchicalMemoryǁ_ensure_capacity__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁ_ensure_capacity'

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_orig(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_1(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = None  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_2(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 6  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_3(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(None):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_4(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count > promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_5(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(None, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_6(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, None)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_7(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_8(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, )

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_9(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(None):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_10(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count > promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_11(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(None, MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_12(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, None)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_13(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(MemoryLayer.EPISODIC)

    def xǁHierarchicalMemoryǁ_check_promotions__mutmut_14(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, )
    
    xǁHierarchicalMemoryǁ_check_promotions__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHierarchicalMemoryǁ_check_promotions__mutmut_1': xǁHierarchicalMemoryǁ_check_promotions__mutmut_1, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_2': xǁHierarchicalMemoryǁ_check_promotions__mutmut_2, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_3': xǁHierarchicalMemoryǁ_check_promotions__mutmut_3, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_4': xǁHierarchicalMemoryǁ_check_promotions__mutmut_4, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_5': xǁHierarchicalMemoryǁ_check_promotions__mutmut_5, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_6': xǁHierarchicalMemoryǁ_check_promotions__mutmut_6, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_7': xǁHierarchicalMemoryǁ_check_promotions__mutmut_7, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_8': xǁHierarchicalMemoryǁ_check_promotions__mutmut_8, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_9': xǁHierarchicalMemoryǁ_check_promotions__mutmut_9, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_10': xǁHierarchicalMemoryǁ_check_promotions__mutmut_10, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_11': xǁHierarchicalMemoryǁ_check_promotions__mutmut_11, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_12': xǁHierarchicalMemoryǁ_check_promotions__mutmut_12, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_13': xǁHierarchicalMemoryǁ_check_promotions__mutmut_13, 
        'xǁHierarchicalMemoryǁ_check_promotions__mutmut_14': xǁHierarchicalMemoryǁ_check_promotions__mutmut_14
    }
    
    def _check_promotions(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHierarchicalMemoryǁ_check_promotions__mutmut_orig"), object.__getattribute__(self, "xǁHierarchicalMemoryǁ_check_promotions__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _check_promotions.__signature__ = _mutmut_signature(xǁHierarchicalMemoryǁ_check_promotions__mutmut_orig)
    xǁHierarchicalMemoryǁ_check_promotions__mutmut_orig.__name__ = 'xǁHierarchicalMemoryǁ_check_promotions'
