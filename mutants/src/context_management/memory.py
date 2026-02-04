"""
Context Memory

External memory management for long-context handling with chunking,
RAG integration, map-reduce summarization, and streaming support.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator, Optional

logger = logging.getLogger(__name__)
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


@dataclass
class MemoryChunk:
    """A chunk of content stored in memory."""

    chunk_id: str
    content: str
    summary: Optional[str] = None
    token_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    priority: int = 50
    metadata: dict = field(default_factory=dict)

    def access(self):
        """Record an access to this chunk."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class RetrievalResult:
    """Result of a memory retrieval operation."""

    chunks: list[MemoryChunk]
    total_tokens: int
    query_used: str
    retrieval_method: str


class ContextMemory:
    """
    External memory for long-context handling.

    Features:
    - Chunked storage with automatic splitting
    - Summary generation for chunks
    - RAG-style retrieval (when embeddings available)
    - Map-reduce summarization
    - Streaming content support
    - Persistence to disk
    """

    def xǁContextMemoryǁ__init____mutmut_orig(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_1(
        self,
        max_chunk_tokens: int = 2001,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_2(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100001,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_3(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = None
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_4(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = None
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_5(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = None
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_6(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = None
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_7(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = None
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_8(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter and (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_9(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: None)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_10(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) / 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_11(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 5)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_12(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = None

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_13(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = None
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_14(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = None  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_15(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = None

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_16(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 1

        # Load from storage if exists
        if storage_path and storage_path.exists():
            self._load_from_storage()

    def xǁContextMemoryǁ__init____mutmut_17(
        self,
        max_chunk_tokens: int = 2000,
        max_total_tokens: int = 100000,
        storage_path: Optional[Path] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
        embedder: Optional[Callable[[str], list[float]]] = None,
    ):
        """
        Initialize memory.

        Args:
            max_chunk_tokens: Maximum tokens per chunk
            max_total_tokens: Maximum total tokens in memory
            storage_path: Path for persistent storage
            summarizer: Function to summarize content
            token_counter: Function to count tokens
            embedder: Function to generate embeddings for RAG
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.max_total_tokens = max_total_tokens
        self.storage_path = storage_path
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)
        self._embedder = embedder

        # Chunk storage
        self._chunks: dict[str, MemoryChunk] = {}
        self._embeddings: dict[str, list[float]] = {}  # chunk_id -> embedding

        # Current token count
        self._total_tokens = 0

        # Load from storage if exists
        if storage_path or storage_path.exists():
            self._load_from_storage()
    
    xǁContextMemoryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ__init____mutmut_1': xǁContextMemoryǁ__init____mutmut_1, 
        'xǁContextMemoryǁ__init____mutmut_2': xǁContextMemoryǁ__init____mutmut_2, 
        'xǁContextMemoryǁ__init____mutmut_3': xǁContextMemoryǁ__init____mutmut_3, 
        'xǁContextMemoryǁ__init____mutmut_4': xǁContextMemoryǁ__init____mutmut_4, 
        'xǁContextMemoryǁ__init____mutmut_5': xǁContextMemoryǁ__init____mutmut_5, 
        'xǁContextMemoryǁ__init____mutmut_6': xǁContextMemoryǁ__init____mutmut_6, 
        'xǁContextMemoryǁ__init____mutmut_7': xǁContextMemoryǁ__init____mutmut_7, 
        'xǁContextMemoryǁ__init____mutmut_8': xǁContextMemoryǁ__init____mutmut_8, 
        'xǁContextMemoryǁ__init____mutmut_9': xǁContextMemoryǁ__init____mutmut_9, 
        'xǁContextMemoryǁ__init____mutmut_10': xǁContextMemoryǁ__init____mutmut_10, 
        'xǁContextMemoryǁ__init____mutmut_11': xǁContextMemoryǁ__init____mutmut_11, 
        'xǁContextMemoryǁ__init____mutmut_12': xǁContextMemoryǁ__init____mutmut_12, 
        'xǁContextMemoryǁ__init____mutmut_13': xǁContextMemoryǁ__init____mutmut_13, 
        'xǁContextMemoryǁ__init____mutmut_14': xǁContextMemoryǁ__init____mutmut_14, 
        'xǁContextMemoryǁ__init____mutmut_15': xǁContextMemoryǁ__init____mutmut_15, 
        'xǁContextMemoryǁ__init____mutmut_16': xǁContextMemoryǁ__init____mutmut_16, 
        'xǁContextMemoryǁ__init____mutmut_17': xǁContextMemoryǁ__init____mutmut_17
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁContextMemoryǁ__init____mutmut_orig)
    xǁContextMemoryǁ__init____mutmut_orig.__name__ = 'xǁContextMemoryǁ__init__'

    def xǁContextMemoryǁstore__mutmut_orig(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_1(
        self,
        content: str,
        priority: int = 51,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_2(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = False,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_3(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = None
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_4(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(None)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_5(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = None

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_6(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = None
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_7(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(None)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_8(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = None

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_9(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(None)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_10(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens - token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_11(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count >= self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_12(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_13(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    return  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_14(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = ""
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_15(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary or self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_16(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = None
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_17(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(None)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_18(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(None)
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_19(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(None, exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_20(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=None)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_21(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_22(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", )

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_23(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("XXFailed to summarize chunk; storing without summaryXX", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_24(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_25(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("FAILED TO SUMMARIZE CHUNK; STORING WITHOUT SUMMARY", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_26(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = None

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_27(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=None,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_28(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=None,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_29(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=None,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_30(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=None,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_31(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=None,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_32(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=None,
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_33(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_34(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_35(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_36(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_37(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_38(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_39(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata and {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_40(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = None
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_41(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens = token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_42(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens -= token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_43(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(None)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_44(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = None
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_45(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(None)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_46(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(None)
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_47(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(None, chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_48(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", None, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_49(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=None)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_50(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_51(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_52(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to embed chunk %s; proceeding without embedding", chunk_id, )

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_53(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("XXFailed to embed chunk %s; proceeding without embeddingXX", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_54(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("failed to embed chunk %s; proceeding without embedding", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def xǁContextMemoryǁstore__mutmut_55(
        self,
        content: str,
        priority: int = 50,
        metadata: Optional[dict] = None,
        generate_summary: bool = True,
    ) -> list[str]:
        """
        Store content in memory, chunking if necessary.

        Args:
            content: Content to store
            priority: Priority for retrieval/eviction
            metadata: Additional metadata
            generate_summary: Whether to generate summary

        Returns:
            list of chunk IDs created
        """
        # Split into chunks
        chunks = self._split_into_chunks(content)
        chunk_ids = []

        for chunk_content in chunks:
            chunk_id = self._generate_chunk_id(chunk_content)
            token_count = self._token_counter(chunk_content)

            # Ensure we have room
            while self._total_tokens + token_count > self.max_total_tokens:
                if not self._evict_lowest_priority():
                    break  # Can't evict anything

            # Generate summary if requested
            summary = None
            if generate_summary and self._summarizer:
                try:
                    summary = self._summarizer(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Failed to summarize chunk; storing without summary", exc_info=exc)

            # Create chunk
            chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                summary=summary,
                token_count=token_count,
                priority=priority,
                metadata=metadata or {},
            )

            self._chunks[chunk_id] = chunk
            self._total_tokens += token_count
            chunk_ids.append(chunk_id)

            # Generate embedding if available
            if self._embedder:
                try:
                    self._embeddings[chunk_id] = self._embedder(chunk_content)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("FAILED TO EMBED CHUNK %S; PROCEEDING WITHOUT EMBEDDING", chunk_id, exc_info=exc)

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids
    
    xǁContextMemoryǁstore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁstore__mutmut_1': xǁContextMemoryǁstore__mutmut_1, 
        'xǁContextMemoryǁstore__mutmut_2': xǁContextMemoryǁstore__mutmut_2, 
        'xǁContextMemoryǁstore__mutmut_3': xǁContextMemoryǁstore__mutmut_3, 
        'xǁContextMemoryǁstore__mutmut_4': xǁContextMemoryǁstore__mutmut_4, 
        'xǁContextMemoryǁstore__mutmut_5': xǁContextMemoryǁstore__mutmut_5, 
        'xǁContextMemoryǁstore__mutmut_6': xǁContextMemoryǁstore__mutmut_6, 
        'xǁContextMemoryǁstore__mutmut_7': xǁContextMemoryǁstore__mutmut_7, 
        'xǁContextMemoryǁstore__mutmut_8': xǁContextMemoryǁstore__mutmut_8, 
        'xǁContextMemoryǁstore__mutmut_9': xǁContextMemoryǁstore__mutmut_9, 
        'xǁContextMemoryǁstore__mutmut_10': xǁContextMemoryǁstore__mutmut_10, 
        'xǁContextMemoryǁstore__mutmut_11': xǁContextMemoryǁstore__mutmut_11, 
        'xǁContextMemoryǁstore__mutmut_12': xǁContextMemoryǁstore__mutmut_12, 
        'xǁContextMemoryǁstore__mutmut_13': xǁContextMemoryǁstore__mutmut_13, 
        'xǁContextMemoryǁstore__mutmut_14': xǁContextMemoryǁstore__mutmut_14, 
        'xǁContextMemoryǁstore__mutmut_15': xǁContextMemoryǁstore__mutmut_15, 
        'xǁContextMemoryǁstore__mutmut_16': xǁContextMemoryǁstore__mutmut_16, 
        'xǁContextMemoryǁstore__mutmut_17': xǁContextMemoryǁstore__mutmut_17, 
        'xǁContextMemoryǁstore__mutmut_18': xǁContextMemoryǁstore__mutmut_18, 
        'xǁContextMemoryǁstore__mutmut_19': xǁContextMemoryǁstore__mutmut_19, 
        'xǁContextMemoryǁstore__mutmut_20': xǁContextMemoryǁstore__mutmut_20, 
        'xǁContextMemoryǁstore__mutmut_21': xǁContextMemoryǁstore__mutmut_21, 
        'xǁContextMemoryǁstore__mutmut_22': xǁContextMemoryǁstore__mutmut_22, 
        'xǁContextMemoryǁstore__mutmut_23': xǁContextMemoryǁstore__mutmut_23, 
        'xǁContextMemoryǁstore__mutmut_24': xǁContextMemoryǁstore__mutmut_24, 
        'xǁContextMemoryǁstore__mutmut_25': xǁContextMemoryǁstore__mutmut_25, 
        'xǁContextMemoryǁstore__mutmut_26': xǁContextMemoryǁstore__mutmut_26, 
        'xǁContextMemoryǁstore__mutmut_27': xǁContextMemoryǁstore__mutmut_27, 
        'xǁContextMemoryǁstore__mutmut_28': xǁContextMemoryǁstore__mutmut_28, 
        'xǁContextMemoryǁstore__mutmut_29': xǁContextMemoryǁstore__mutmut_29, 
        'xǁContextMemoryǁstore__mutmut_30': xǁContextMemoryǁstore__mutmut_30, 
        'xǁContextMemoryǁstore__mutmut_31': xǁContextMemoryǁstore__mutmut_31, 
        'xǁContextMemoryǁstore__mutmut_32': xǁContextMemoryǁstore__mutmut_32, 
        'xǁContextMemoryǁstore__mutmut_33': xǁContextMemoryǁstore__mutmut_33, 
        'xǁContextMemoryǁstore__mutmut_34': xǁContextMemoryǁstore__mutmut_34, 
        'xǁContextMemoryǁstore__mutmut_35': xǁContextMemoryǁstore__mutmut_35, 
        'xǁContextMemoryǁstore__mutmut_36': xǁContextMemoryǁstore__mutmut_36, 
        'xǁContextMemoryǁstore__mutmut_37': xǁContextMemoryǁstore__mutmut_37, 
        'xǁContextMemoryǁstore__mutmut_38': xǁContextMemoryǁstore__mutmut_38, 
        'xǁContextMemoryǁstore__mutmut_39': xǁContextMemoryǁstore__mutmut_39, 
        'xǁContextMemoryǁstore__mutmut_40': xǁContextMemoryǁstore__mutmut_40, 
        'xǁContextMemoryǁstore__mutmut_41': xǁContextMemoryǁstore__mutmut_41, 
        'xǁContextMemoryǁstore__mutmut_42': xǁContextMemoryǁstore__mutmut_42, 
        'xǁContextMemoryǁstore__mutmut_43': xǁContextMemoryǁstore__mutmut_43, 
        'xǁContextMemoryǁstore__mutmut_44': xǁContextMemoryǁstore__mutmut_44, 
        'xǁContextMemoryǁstore__mutmut_45': xǁContextMemoryǁstore__mutmut_45, 
        'xǁContextMemoryǁstore__mutmut_46': xǁContextMemoryǁstore__mutmut_46, 
        'xǁContextMemoryǁstore__mutmut_47': xǁContextMemoryǁstore__mutmut_47, 
        'xǁContextMemoryǁstore__mutmut_48': xǁContextMemoryǁstore__mutmut_48, 
        'xǁContextMemoryǁstore__mutmut_49': xǁContextMemoryǁstore__mutmut_49, 
        'xǁContextMemoryǁstore__mutmut_50': xǁContextMemoryǁstore__mutmut_50, 
        'xǁContextMemoryǁstore__mutmut_51': xǁContextMemoryǁstore__mutmut_51, 
        'xǁContextMemoryǁstore__mutmut_52': xǁContextMemoryǁstore__mutmut_52, 
        'xǁContextMemoryǁstore__mutmut_53': xǁContextMemoryǁstore__mutmut_53, 
        'xǁContextMemoryǁstore__mutmut_54': xǁContextMemoryǁstore__mutmut_54, 
        'xǁContextMemoryǁstore__mutmut_55': xǁContextMemoryǁstore__mutmut_55
    }
    
    def store(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁstore__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁstore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store.__signature__ = _mutmut_signature(xǁContextMemoryǁstore__mutmut_orig)
    xǁContextMemoryǁstore__mutmut_orig.__name__ = 'xǁContextMemoryǁstore'

    def xǁContextMemoryǁretrieve__mutmut_orig(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_1(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 1,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_2(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = True,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_3(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = None

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_4(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens and self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_5(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens / 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_6(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 6

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_7(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = None

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_8(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority > min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_9(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder or self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_10(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query or self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_11(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = None
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_12(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(None, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_13(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, None)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_14(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_15(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, )
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_16(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = None
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_17(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "XXembedding_similarityXX"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_18(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "EMBEDDING_SIMILARITY"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_19(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=None, reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_20(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=None
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_21(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_22(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_23(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: None, reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_24(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=False
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_25(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = None

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_26(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "XXpriority_recencyXX"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_27(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "PRIORITY_RECENCY"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_28(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = None
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_29(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = None

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_30(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 1

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_31(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = None
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_32(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries or chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_33(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = None

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_34(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(None)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_35(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens - tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_36(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens < max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_37(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(None)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_38(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens = tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_39(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens -= tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_40(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=None,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_41(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=None,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_42(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=None,
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_43(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=None,
        )

    def xǁContextMemoryǁretrieve__mutmut_44(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            total_tokens=total_tokens,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_45(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            query_used=query or "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_46(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_47(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "",
            )

    def xǁContextMemoryǁretrieve__mutmut_48(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query and "",
            retrieval_method=retrieval_method,
        )

    def xǁContextMemoryǁretrieve__mutmut_49(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        min_priority: int = 0,
        use_summaries: bool = False,
    ) -> RetrievalResult:
        """
        Retrieve content from memory.

        Args:
            query: Query for similarity search (if embeddings available)
            max_tokens: Maximum tokens to return
            min_priority: Minimum priority to include
            use_summaries: Use summaries instead of full content

        Returns:
            RetrievalResult with matching chunks
        """
        max_tokens = max_tokens or self.max_chunk_tokens * 5

        # Filter by priority
        candidates = [c for c in self._chunks.values() if c.priority >= min_priority]

        # Sort by relevance
        if query and self._embedder and self._embeddings:
            # Use embedding similarity
            candidates = self._rank_by_similarity(query, candidates)
            retrieval_method = "embedding_similarity"
        else:
            # Sort by recency and access count
            candidates.sort(
                key=lambda c: (c.priority, c.access_count, c.last_accessed), reverse=True
            )
            retrieval_method = "priority_recency"

        # Collect chunks within token budget
        selected = []
        total_tokens = 0

        for chunk in candidates:
            content = chunk.summary if use_summaries and chunk.summary else chunk.content
            tokens = self._token_counter(content)

            if total_tokens + tokens <= max_tokens:
                chunk.access()
                selected.append(chunk)
                total_tokens += tokens

        return RetrievalResult(
            chunks=selected,
            total_tokens=total_tokens,
            query_used=query or "XXXX",
            retrieval_method=retrieval_method,
        )
    
    xǁContextMemoryǁretrieve__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁretrieve__mutmut_1': xǁContextMemoryǁretrieve__mutmut_1, 
        'xǁContextMemoryǁretrieve__mutmut_2': xǁContextMemoryǁretrieve__mutmut_2, 
        'xǁContextMemoryǁretrieve__mutmut_3': xǁContextMemoryǁretrieve__mutmut_3, 
        'xǁContextMemoryǁretrieve__mutmut_4': xǁContextMemoryǁretrieve__mutmut_4, 
        'xǁContextMemoryǁretrieve__mutmut_5': xǁContextMemoryǁretrieve__mutmut_5, 
        'xǁContextMemoryǁretrieve__mutmut_6': xǁContextMemoryǁretrieve__mutmut_6, 
        'xǁContextMemoryǁretrieve__mutmut_7': xǁContextMemoryǁretrieve__mutmut_7, 
        'xǁContextMemoryǁretrieve__mutmut_8': xǁContextMemoryǁretrieve__mutmut_8, 
        'xǁContextMemoryǁretrieve__mutmut_9': xǁContextMemoryǁretrieve__mutmut_9, 
        'xǁContextMemoryǁretrieve__mutmut_10': xǁContextMemoryǁretrieve__mutmut_10, 
        'xǁContextMemoryǁretrieve__mutmut_11': xǁContextMemoryǁretrieve__mutmut_11, 
        'xǁContextMemoryǁretrieve__mutmut_12': xǁContextMemoryǁretrieve__mutmut_12, 
        'xǁContextMemoryǁretrieve__mutmut_13': xǁContextMemoryǁretrieve__mutmut_13, 
        'xǁContextMemoryǁretrieve__mutmut_14': xǁContextMemoryǁretrieve__mutmut_14, 
        'xǁContextMemoryǁretrieve__mutmut_15': xǁContextMemoryǁretrieve__mutmut_15, 
        'xǁContextMemoryǁretrieve__mutmut_16': xǁContextMemoryǁretrieve__mutmut_16, 
        'xǁContextMemoryǁretrieve__mutmut_17': xǁContextMemoryǁretrieve__mutmut_17, 
        'xǁContextMemoryǁretrieve__mutmut_18': xǁContextMemoryǁretrieve__mutmut_18, 
        'xǁContextMemoryǁretrieve__mutmut_19': xǁContextMemoryǁretrieve__mutmut_19, 
        'xǁContextMemoryǁretrieve__mutmut_20': xǁContextMemoryǁretrieve__mutmut_20, 
        'xǁContextMemoryǁretrieve__mutmut_21': xǁContextMemoryǁretrieve__mutmut_21, 
        'xǁContextMemoryǁretrieve__mutmut_22': xǁContextMemoryǁretrieve__mutmut_22, 
        'xǁContextMemoryǁretrieve__mutmut_23': xǁContextMemoryǁretrieve__mutmut_23, 
        'xǁContextMemoryǁretrieve__mutmut_24': xǁContextMemoryǁretrieve__mutmut_24, 
        'xǁContextMemoryǁretrieve__mutmut_25': xǁContextMemoryǁretrieve__mutmut_25, 
        'xǁContextMemoryǁretrieve__mutmut_26': xǁContextMemoryǁretrieve__mutmut_26, 
        'xǁContextMemoryǁretrieve__mutmut_27': xǁContextMemoryǁretrieve__mutmut_27, 
        'xǁContextMemoryǁretrieve__mutmut_28': xǁContextMemoryǁretrieve__mutmut_28, 
        'xǁContextMemoryǁretrieve__mutmut_29': xǁContextMemoryǁretrieve__mutmut_29, 
        'xǁContextMemoryǁretrieve__mutmut_30': xǁContextMemoryǁretrieve__mutmut_30, 
        'xǁContextMemoryǁretrieve__mutmut_31': xǁContextMemoryǁretrieve__mutmut_31, 
        'xǁContextMemoryǁretrieve__mutmut_32': xǁContextMemoryǁretrieve__mutmut_32, 
        'xǁContextMemoryǁretrieve__mutmut_33': xǁContextMemoryǁretrieve__mutmut_33, 
        'xǁContextMemoryǁretrieve__mutmut_34': xǁContextMemoryǁretrieve__mutmut_34, 
        'xǁContextMemoryǁretrieve__mutmut_35': xǁContextMemoryǁretrieve__mutmut_35, 
        'xǁContextMemoryǁretrieve__mutmut_36': xǁContextMemoryǁretrieve__mutmut_36, 
        'xǁContextMemoryǁretrieve__mutmut_37': xǁContextMemoryǁretrieve__mutmut_37, 
        'xǁContextMemoryǁretrieve__mutmut_38': xǁContextMemoryǁretrieve__mutmut_38, 
        'xǁContextMemoryǁretrieve__mutmut_39': xǁContextMemoryǁretrieve__mutmut_39, 
        'xǁContextMemoryǁretrieve__mutmut_40': xǁContextMemoryǁretrieve__mutmut_40, 
        'xǁContextMemoryǁretrieve__mutmut_41': xǁContextMemoryǁretrieve__mutmut_41, 
        'xǁContextMemoryǁretrieve__mutmut_42': xǁContextMemoryǁretrieve__mutmut_42, 
        'xǁContextMemoryǁretrieve__mutmut_43': xǁContextMemoryǁretrieve__mutmut_43, 
        'xǁContextMemoryǁretrieve__mutmut_44': xǁContextMemoryǁretrieve__mutmut_44, 
        'xǁContextMemoryǁretrieve__mutmut_45': xǁContextMemoryǁretrieve__mutmut_45, 
        'xǁContextMemoryǁretrieve__mutmut_46': xǁContextMemoryǁretrieve__mutmut_46, 
        'xǁContextMemoryǁretrieve__mutmut_47': xǁContextMemoryǁretrieve__mutmut_47, 
        'xǁContextMemoryǁretrieve__mutmut_48': xǁContextMemoryǁretrieve__mutmut_48, 
        'xǁContextMemoryǁretrieve__mutmut_49': xǁContextMemoryǁretrieve__mutmut_49
    }
    
    def retrieve(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁretrieve__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁretrieve__mutmut_mutants"), args, kwargs, self)
        return result 
    
    retrieve.__signature__ = _mutmut_signature(xǁContextMemoryǁretrieve__mutmut_orig)
    xǁContextMemoryǁretrieve__mutmut_orig.__name__ = 'xǁContextMemoryǁretrieve'

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_orig(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_1(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_2(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "XXNo summarizer availableXX"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_3(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "no summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_4(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "NO SUMMARIZER AVAILABLE"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_5(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = None

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_6(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids and self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_7(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid not in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_8(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_9(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "XXNo chunks to summarizeXX"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_10(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "no chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_11(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "NO CHUNKS TO SUMMARIZE"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_12(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = None
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_13(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(None)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_14(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = None
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_15(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(None)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_16(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = None
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_17(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(None)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_18(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(None)
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_19(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(None, exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_20(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=None)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_21(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_22(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", )
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_23(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("XXChunk summarization failed; using fallback contentXX", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_24(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_25(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("CHUNK SUMMARIZATION FAILED; USING FALLBACK CONTENT", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_26(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(None)

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_27(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] - "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_28(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:201] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_29(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "XX...XX")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_30(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) != 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_31(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 2:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_32(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[1]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_33(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = None
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_34(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(None)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_35(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "XX\n\nXX".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_36(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(None)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_37(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(None)
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_38(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning(None, exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_39(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", exc_info=None)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_40(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning(exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_41(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Failed to summarize combined content; returning raw aggregation", )
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_42(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("XXFailed to summarize combined content; returning raw aggregationXX", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_43(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("failed to summarize combined content; returning raw aggregation", exc_info=exc)
            return combined

    def xǁContextMemoryǁmap_reduce_summarize__mutmut_44(self, chunk_ids: Optional[list[str]] = None) -> str:
        """
        Generate summary using map-reduce pattern.

        Args:
            chunk_ids: Specific chunks to summarize (all if None)

        Returns:
            Combined summary
        """
        if not self._summarizer:
            return "No summarizer available"

        chunks = [
            self._chunks[cid] for cid in (chunk_ids or self._chunks.keys()) if cid in self._chunks
        ]

        if not chunks:
            return "No chunks to summarize"

        # Map phase: summarize each chunk
        summaries = []
        for chunk in chunks:
            if chunk.summary:
                summaries.append(chunk.summary)
            else:
                try:
                    summary = self._summarizer(chunk.content)
                    chunk.summary = summary
                    summaries.append(summary)
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning("Chunk summarization failed; using fallback content", exc_info=exc)
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("FAILED TO SUMMARIZE COMBINED CONTENT; RETURNING RAW AGGREGATION", exc_info=exc)
            return combined
    
    xǁContextMemoryǁmap_reduce_summarize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁmap_reduce_summarize__mutmut_1': xǁContextMemoryǁmap_reduce_summarize__mutmut_1, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_2': xǁContextMemoryǁmap_reduce_summarize__mutmut_2, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_3': xǁContextMemoryǁmap_reduce_summarize__mutmut_3, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_4': xǁContextMemoryǁmap_reduce_summarize__mutmut_4, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_5': xǁContextMemoryǁmap_reduce_summarize__mutmut_5, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_6': xǁContextMemoryǁmap_reduce_summarize__mutmut_6, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_7': xǁContextMemoryǁmap_reduce_summarize__mutmut_7, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_8': xǁContextMemoryǁmap_reduce_summarize__mutmut_8, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_9': xǁContextMemoryǁmap_reduce_summarize__mutmut_9, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_10': xǁContextMemoryǁmap_reduce_summarize__mutmut_10, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_11': xǁContextMemoryǁmap_reduce_summarize__mutmut_11, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_12': xǁContextMemoryǁmap_reduce_summarize__mutmut_12, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_13': xǁContextMemoryǁmap_reduce_summarize__mutmut_13, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_14': xǁContextMemoryǁmap_reduce_summarize__mutmut_14, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_15': xǁContextMemoryǁmap_reduce_summarize__mutmut_15, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_16': xǁContextMemoryǁmap_reduce_summarize__mutmut_16, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_17': xǁContextMemoryǁmap_reduce_summarize__mutmut_17, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_18': xǁContextMemoryǁmap_reduce_summarize__mutmut_18, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_19': xǁContextMemoryǁmap_reduce_summarize__mutmut_19, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_20': xǁContextMemoryǁmap_reduce_summarize__mutmut_20, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_21': xǁContextMemoryǁmap_reduce_summarize__mutmut_21, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_22': xǁContextMemoryǁmap_reduce_summarize__mutmut_22, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_23': xǁContextMemoryǁmap_reduce_summarize__mutmut_23, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_24': xǁContextMemoryǁmap_reduce_summarize__mutmut_24, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_25': xǁContextMemoryǁmap_reduce_summarize__mutmut_25, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_26': xǁContextMemoryǁmap_reduce_summarize__mutmut_26, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_27': xǁContextMemoryǁmap_reduce_summarize__mutmut_27, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_28': xǁContextMemoryǁmap_reduce_summarize__mutmut_28, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_29': xǁContextMemoryǁmap_reduce_summarize__mutmut_29, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_30': xǁContextMemoryǁmap_reduce_summarize__mutmut_30, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_31': xǁContextMemoryǁmap_reduce_summarize__mutmut_31, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_32': xǁContextMemoryǁmap_reduce_summarize__mutmut_32, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_33': xǁContextMemoryǁmap_reduce_summarize__mutmut_33, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_34': xǁContextMemoryǁmap_reduce_summarize__mutmut_34, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_35': xǁContextMemoryǁmap_reduce_summarize__mutmut_35, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_36': xǁContextMemoryǁmap_reduce_summarize__mutmut_36, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_37': xǁContextMemoryǁmap_reduce_summarize__mutmut_37, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_38': xǁContextMemoryǁmap_reduce_summarize__mutmut_38, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_39': xǁContextMemoryǁmap_reduce_summarize__mutmut_39, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_40': xǁContextMemoryǁmap_reduce_summarize__mutmut_40, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_41': xǁContextMemoryǁmap_reduce_summarize__mutmut_41, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_42': xǁContextMemoryǁmap_reduce_summarize__mutmut_42, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_43': xǁContextMemoryǁmap_reduce_summarize__mutmut_43, 
        'xǁContextMemoryǁmap_reduce_summarize__mutmut_44': xǁContextMemoryǁmap_reduce_summarize__mutmut_44
    }
    
    def map_reduce_summarize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁmap_reduce_summarize__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁmap_reduce_summarize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    map_reduce_summarize.__signature__ = _mutmut_signature(xǁContextMemoryǁmap_reduce_summarize__mutmut_orig)
    xǁContextMemoryǁmap_reduce_summarize__mutmut_orig.__name__ = 'xǁContextMemoryǁmap_reduce_summarize'

    def xǁContextMemoryǁstream_retrieve__mutmut_orig(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_1(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = None

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_2(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=None)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_3(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = None
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_4(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = None
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_5(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(None)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_6(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens >= max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_7(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = None
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_8(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(None, max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_9(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, None)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_10(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(max_tokens_per_chunk)
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk

    def xǁContextMemoryǁstream_retrieve__mutmut_11(
        self, query: Optional[str] = None, max_tokens_per_chunk: Optional[int] = None
    ) -> Iterator[tuple[str, MemoryChunk]]:
        """
        Stream content from memory chunk by chunk.

        Yields:
            Tuples of (content, chunk) for streaming processing
        """
        result = self.retrieve(query=query)

        for chunk in result.chunks:
            content = chunk.content
            if max_tokens_per_chunk:
                # Further split if needed
                tokens = self._token_counter(content)
                if tokens > max_tokens_per_chunk:
                    # Split into smaller pieces
                    pieces = self._split_content(content, )
                    for piece in pieces:
                        yield piece, chunk
                else:
                    yield content, chunk
            else:
                yield content, chunk
    
    xǁContextMemoryǁstream_retrieve__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁstream_retrieve__mutmut_1': xǁContextMemoryǁstream_retrieve__mutmut_1, 
        'xǁContextMemoryǁstream_retrieve__mutmut_2': xǁContextMemoryǁstream_retrieve__mutmut_2, 
        'xǁContextMemoryǁstream_retrieve__mutmut_3': xǁContextMemoryǁstream_retrieve__mutmut_3, 
        'xǁContextMemoryǁstream_retrieve__mutmut_4': xǁContextMemoryǁstream_retrieve__mutmut_4, 
        'xǁContextMemoryǁstream_retrieve__mutmut_5': xǁContextMemoryǁstream_retrieve__mutmut_5, 
        'xǁContextMemoryǁstream_retrieve__mutmut_6': xǁContextMemoryǁstream_retrieve__mutmut_6, 
        'xǁContextMemoryǁstream_retrieve__mutmut_7': xǁContextMemoryǁstream_retrieve__mutmut_7, 
        'xǁContextMemoryǁstream_retrieve__mutmut_8': xǁContextMemoryǁstream_retrieve__mutmut_8, 
        'xǁContextMemoryǁstream_retrieve__mutmut_9': xǁContextMemoryǁstream_retrieve__mutmut_9, 
        'xǁContextMemoryǁstream_retrieve__mutmut_10': xǁContextMemoryǁstream_retrieve__mutmut_10, 
        'xǁContextMemoryǁstream_retrieve__mutmut_11': xǁContextMemoryǁstream_retrieve__mutmut_11
    }
    
    def stream_retrieve(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁstream_retrieve__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁstream_retrieve__mutmut_mutants"), args, kwargs, self)
        return result 
    
    stream_retrieve.__signature__ = _mutmut_signature(xǁContextMemoryǁstream_retrieve__mutmut_orig)
    xǁContextMemoryǁstream_retrieve__mutmut_orig.__name__ = 'xǁContextMemoryǁstream_retrieve'

    def xǁContextMemoryǁget_chunk__mutmut_orig(self, chunk_id: str) -> Optional[MemoryChunk]:
        """Get a specific chunk by ID."""
        chunk = self._chunks.get(chunk_id)
        if chunk:
            chunk.access()
        return chunk

    def xǁContextMemoryǁget_chunk__mutmut_1(self, chunk_id: str) -> Optional[MemoryChunk]:
        """Get a specific chunk by ID."""
        chunk = None
        if chunk:
            chunk.access()
        return chunk

    def xǁContextMemoryǁget_chunk__mutmut_2(self, chunk_id: str) -> Optional[MemoryChunk]:
        """Get a specific chunk by ID."""
        chunk = self._chunks.get(None)
        if chunk:
            chunk.access()
        return chunk
    
    xǁContextMemoryǁget_chunk__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁget_chunk__mutmut_1': xǁContextMemoryǁget_chunk__mutmut_1, 
        'xǁContextMemoryǁget_chunk__mutmut_2': xǁContextMemoryǁget_chunk__mutmut_2
    }
    
    def get_chunk(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁget_chunk__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁget_chunk__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_chunk.__signature__ = _mutmut_signature(xǁContextMemoryǁget_chunk__mutmut_orig)
    xǁContextMemoryǁget_chunk__mutmut_orig.__name__ = 'xǁContextMemoryǁget_chunk'

    def xǁContextMemoryǁdelete_chunk__mutmut_orig(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_1(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id not in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_2(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = None
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_3(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(None)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_4(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens = chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_5(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens += chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_6(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(None, None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_7(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(None)
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_8(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, )
            return True
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_9(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return False
        return False

    def xǁContextMemoryǁdelete_chunk__mutmut_10(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return True
    
    xǁContextMemoryǁdelete_chunk__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁdelete_chunk__mutmut_1': xǁContextMemoryǁdelete_chunk__mutmut_1, 
        'xǁContextMemoryǁdelete_chunk__mutmut_2': xǁContextMemoryǁdelete_chunk__mutmut_2, 
        'xǁContextMemoryǁdelete_chunk__mutmut_3': xǁContextMemoryǁdelete_chunk__mutmut_3, 
        'xǁContextMemoryǁdelete_chunk__mutmut_4': xǁContextMemoryǁdelete_chunk__mutmut_4, 
        'xǁContextMemoryǁdelete_chunk__mutmut_5': xǁContextMemoryǁdelete_chunk__mutmut_5, 
        'xǁContextMemoryǁdelete_chunk__mutmut_6': xǁContextMemoryǁdelete_chunk__mutmut_6, 
        'xǁContextMemoryǁdelete_chunk__mutmut_7': xǁContextMemoryǁdelete_chunk__mutmut_7, 
        'xǁContextMemoryǁdelete_chunk__mutmut_8': xǁContextMemoryǁdelete_chunk__mutmut_8, 
        'xǁContextMemoryǁdelete_chunk__mutmut_9': xǁContextMemoryǁdelete_chunk__mutmut_9, 
        'xǁContextMemoryǁdelete_chunk__mutmut_10': xǁContextMemoryǁdelete_chunk__mutmut_10
    }
    
    def delete_chunk(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁdelete_chunk__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁdelete_chunk__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete_chunk.__signature__ = _mutmut_signature(xǁContextMemoryǁdelete_chunk__mutmut_orig)
    xǁContextMemoryǁdelete_chunk__mutmut_orig.__name__ = 'xǁContextMemoryǁdelete_chunk'

    def xǁContextMemoryǁget_stats__mutmut_orig(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_1(self) -> dict:
        """Get memory statistics."""
        return {
            "XXchunk_countXX": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_2(self) -> dict:
        """Get memory statistics."""
        return {
            "CHUNK_COUNT": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_3(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "XXtotal_tokensXX": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_4(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "TOTAL_TOKENS": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_5(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "XXmax_tokensXX": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_6(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "MAX_TOKENS": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_7(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "XXusage_ratioXX": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_8(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "USAGE_RATIO": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_9(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens * self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_10(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "XXhas_embeddingsXX": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_11(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "HAS_EMBEDDINGS": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_12(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(None),
            "has_summarizer": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_13(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "XXhas_summarizerXX": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_14(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "HAS_SUMMARIZER": self._summarizer is not None,
        }

    def xǁContextMemoryǁget_stats__mutmut_15(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is None,
        }
    
    xǁContextMemoryǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁget_stats__mutmut_1': xǁContextMemoryǁget_stats__mutmut_1, 
        'xǁContextMemoryǁget_stats__mutmut_2': xǁContextMemoryǁget_stats__mutmut_2, 
        'xǁContextMemoryǁget_stats__mutmut_3': xǁContextMemoryǁget_stats__mutmut_3, 
        'xǁContextMemoryǁget_stats__mutmut_4': xǁContextMemoryǁget_stats__mutmut_4, 
        'xǁContextMemoryǁget_stats__mutmut_5': xǁContextMemoryǁget_stats__mutmut_5, 
        'xǁContextMemoryǁget_stats__mutmut_6': xǁContextMemoryǁget_stats__mutmut_6, 
        'xǁContextMemoryǁget_stats__mutmut_7': xǁContextMemoryǁget_stats__mutmut_7, 
        'xǁContextMemoryǁget_stats__mutmut_8': xǁContextMemoryǁget_stats__mutmut_8, 
        'xǁContextMemoryǁget_stats__mutmut_9': xǁContextMemoryǁget_stats__mutmut_9, 
        'xǁContextMemoryǁget_stats__mutmut_10': xǁContextMemoryǁget_stats__mutmut_10, 
        'xǁContextMemoryǁget_stats__mutmut_11': xǁContextMemoryǁget_stats__mutmut_11, 
        'xǁContextMemoryǁget_stats__mutmut_12': xǁContextMemoryǁget_stats__mutmut_12, 
        'xǁContextMemoryǁget_stats__mutmut_13': xǁContextMemoryǁget_stats__mutmut_13, 
        'xǁContextMemoryǁget_stats__mutmut_14': xǁContextMemoryǁget_stats__mutmut_14, 
        'xǁContextMemoryǁget_stats__mutmut_15': xǁContextMemoryǁget_stats__mutmut_15
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁContextMemoryǁget_stats__mutmut_orig)
    xǁContextMemoryǁget_stats__mutmut_orig.__name__ = 'xǁContextMemoryǁget_stats'

    def xǁContextMemoryǁclear__mutmut_orig(self):
        """Clear all memory."""
        self._chunks.clear()
        self._embeddings.clear()
        self._total_tokens = 0

    def xǁContextMemoryǁclear__mutmut_1(self):
        """Clear all memory."""
        self._chunks.clear()
        self._embeddings.clear()
        self._total_tokens = None

    def xǁContextMemoryǁclear__mutmut_2(self):
        """Clear all memory."""
        self._chunks.clear()
        self._embeddings.clear()
        self._total_tokens = 1
    
    xǁContextMemoryǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁclear__mutmut_1': xǁContextMemoryǁclear__mutmut_1, 
        'xǁContextMemoryǁclear__mutmut_2': xǁContextMemoryǁclear__mutmut_2
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁclear__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁContextMemoryǁclear__mutmut_orig)
    xǁContextMemoryǁclear__mutmut_orig.__name__ = 'xǁContextMemoryǁclear'

    def xǁContextMemoryǁ_split_into_chunks__mutmut_orig(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_1(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = None

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_2(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(None)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_3(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens < self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_4(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = None
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_5(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split(None)
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_6(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("XX\n\nXX")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_7(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = None
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_8(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = None
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_9(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = None

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_10(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 1

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_11(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = None

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_12(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(None)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_13(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens - para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_14(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens >= self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_15(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append(None)

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_16(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(None))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_17(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("XX\n\nXX".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_18(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens >= self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_19(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(None)
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_20(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(None, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_21(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, None))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_22(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_23(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, ))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_24(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = None
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_25(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = None
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_26(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(None)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_27(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens = para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_28(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens -= para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_29(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append(None)

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_30(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(None))

        return chunks

    def xǁContextMemoryǁ_split_into_chunks__mutmut_31(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._token_counter(para)

            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                if para_tokens > self.max_chunk_tokens:
                    # Split large paragraph
                    chunks.extend(self._split_content(para, self.max_chunk_tokens))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("XX\n\nXX".join(current_chunk))

        return chunks
    
    xǁContextMemoryǁ_split_into_chunks__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_split_into_chunks__mutmut_1': xǁContextMemoryǁ_split_into_chunks__mutmut_1, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_2': xǁContextMemoryǁ_split_into_chunks__mutmut_2, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_3': xǁContextMemoryǁ_split_into_chunks__mutmut_3, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_4': xǁContextMemoryǁ_split_into_chunks__mutmut_4, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_5': xǁContextMemoryǁ_split_into_chunks__mutmut_5, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_6': xǁContextMemoryǁ_split_into_chunks__mutmut_6, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_7': xǁContextMemoryǁ_split_into_chunks__mutmut_7, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_8': xǁContextMemoryǁ_split_into_chunks__mutmut_8, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_9': xǁContextMemoryǁ_split_into_chunks__mutmut_9, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_10': xǁContextMemoryǁ_split_into_chunks__mutmut_10, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_11': xǁContextMemoryǁ_split_into_chunks__mutmut_11, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_12': xǁContextMemoryǁ_split_into_chunks__mutmut_12, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_13': xǁContextMemoryǁ_split_into_chunks__mutmut_13, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_14': xǁContextMemoryǁ_split_into_chunks__mutmut_14, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_15': xǁContextMemoryǁ_split_into_chunks__mutmut_15, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_16': xǁContextMemoryǁ_split_into_chunks__mutmut_16, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_17': xǁContextMemoryǁ_split_into_chunks__mutmut_17, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_18': xǁContextMemoryǁ_split_into_chunks__mutmut_18, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_19': xǁContextMemoryǁ_split_into_chunks__mutmut_19, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_20': xǁContextMemoryǁ_split_into_chunks__mutmut_20, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_21': xǁContextMemoryǁ_split_into_chunks__mutmut_21, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_22': xǁContextMemoryǁ_split_into_chunks__mutmut_22, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_23': xǁContextMemoryǁ_split_into_chunks__mutmut_23, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_24': xǁContextMemoryǁ_split_into_chunks__mutmut_24, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_25': xǁContextMemoryǁ_split_into_chunks__mutmut_25, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_26': xǁContextMemoryǁ_split_into_chunks__mutmut_26, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_27': xǁContextMemoryǁ_split_into_chunks__mutmut_27, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_28': xǁContextMemoryǁ_split_into_chunks__mutmut_28, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_29': xǁContextMemoryǁ_split_into_chunks__mutmut_29, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_30': xǁContextMemoryǁ_split_into_chunks__mutmut_30, 
        'xǁContextMemoryǁ_split_into_chunks__mutmut_31': xǁContextMemoryǁ_split_into_chunks__mutmut_31
    }
    
    def _split_into_chunks(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_split_into_chunks__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_split_into_chunks__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _split_into_chunks.__signature__ = _mutmut_signature(xǁContextMemoryǁ_split_into_chunks__mutmut_orig)
    xǁContextMemoryǁ_split_into_chunks__mutmut_orig.__name__ = 'xǁContextMemoryǁ_split_into_chunks'

    def xǁContextMemoryǁ_split_content__mutmut_orig(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_1(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = None
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_2(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = None
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_3(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = None
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_4(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = None

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_5(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 1

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_6(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = None
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_7(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(None)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_8(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens - word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_9(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens >= max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_10(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(None)
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_11(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(None))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_12(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append("XX XX".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_13(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = None
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_14(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = None
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_15(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(None)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_16(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens = word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_17(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens -= word_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_18(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(None)

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_19(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append(" ".join(None))

        return pieces

    def xǁContextMemoryǁ_split_content__mutmut_20(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_counter(word)
            if current_tokens + word_tokens > max_tokens:
                if current:
                    pieces.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            pieces.append("XX XX".join(current))

        return pieces
    
    xǁContextMemoryǁ_split_content__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_split_content__mutmut_1': xǁContextMemoryǁ_split_content__mutmut_1, 
        'xǁContextMemoryǁ_split_content__mutmut_2': xǁContextMemoryǁ_split_content__mutmut_2, 
        'xǁContextMemoryǁ_split_content__mutmut_3': xǁContextMemoryǁ_split_content__mutmut_3, 
        'xǁContextMemoryǁ_split_content__mutmut_4': xǁContextMemoryǁ_split_content__mutmut_4, 
        'xǁContextMemoryǁ_split_content__mutmut_5': xǁContextMemoryǁ_split_content__mutmut_5, 
        'xǁContextMemoryǁ_split_content__mutmut_6': xǁContextMemoryǁ_split_content__mutmut_6, 
        'xǁContextMemoryǁ_split_content__mutmut_7': xǁContextMemoryǁ_split_content__mutmut_7, 
        'xǁContextMemoryǁ_split_content__mutmut_8': xǁContextMemoryǁ_split_content__mutmut_8, 
        'xǁContextMemoryǁ_split_content__mutmut_9': xǁContextMemoryǁ_split_content__mutmut_9, 
        'xǁContextMemoryǁ_split_content__mutmut_10': xǁContextMemoryǁ_split_content__mutmut_10, 
        'xǁContextMemoryǁ_split_content__mutmut_11': xǁContextMemoryǁ_split_content__mutmut_11, 
        'xǁContextMemoryǁ_split_content__mutmut_12': xǁContextMemoryǁ_split_content__mutmut_12, 
        'xǁContextMemoryǁ_split_content__mutmut_13': xǁContextMemoryǁ_split_content__mutmut_13, 
        'xǁContextMemoryǁ_split_content__mutmut_14': xǁContextMemoryǁ_split_content__mutmut_14, 
        'xǁContextMemoryǁ_split_content__mutmut_15': xǁContextMemoryǁ_split_content__mutmut_15, 
        'xǁContextMemoryǁ_split_content__mutmut_16': xǁContextMemoryǁ_split_content__mutmut_16, 
        'xǁContextMemoryǁ_split_content__mutmut_17': xǁContextMemoryǁ_split_content__mutmut_17, 
        'xǁContextMemoryǁ_split_content__mutmut_18': xǁContextMemoryǁ_split_content__mutmut_18, 
        'xǁContextMemoryǁ_split_content__mutmut_19': xǁContextMemoryǁ_split_content__mutmut_19, 
        'xǁContextMemoryǁ_split_content__mutmut_20': xǁContextMemoryǁ_split_content__mutmut_20
    }
    
    def _split_content(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_split_content__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_split_content__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _split_content.__signature__ = _mutmut_signature(xǁContextMemoryǁ_split_content__mutmut_orig)
    xǁContextMemoryǁ_split_content__mutmut_orig.__name__ = 'xǁContextMemoryǁ_split_content'

    def xǁContextMemoryǁ_generate_chunk_id__mutmut_orig(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content[:100]}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def xǁContextMemoryǁ_generate_chunk_id__mutmut_1(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = None
        hash_input = f"{content[:100]}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def xǁContextMemoryǁ_generate_chunk_id__mutmut_2(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = datetime.now().isoformat()
        hash_input = None
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def xǁContextMemoryǁ_generate_chunk_id__mutmut_3(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content[:101]}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def xǁContextMemoryǁ_generate_chunk_id__mutmut_4(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content[:100]}:{timestamp}"
        return hashlib.sha256(None).hexdigest()[:16]

    def xǁContextMemoryǁ_generate_chunk_id__mutmut_5(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content[:100]}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:17]
    
    xǁContextMemoryǁ_generate_chunk_id__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_generate_chunk_id__mutmut_1': xǁContextMemoryǁ_generate_chunk_id__mutmut_1, 
        'xǁContextMemoryǁ_generate_chunk_id__mutmut_2': xǁContextMemoryǁ_generate_chunk_id__mutmut_2, 
        'xǁContextMemoryǁ_generate_chunk_id__mutmut_3': xǁContextMemoryǁ_generate_chunk_id__mutmut_3, 
        'xǁContextMemoryǁ_generate_chunk_id__mutmut_4': xǁContextMemoryǁ_generate_chunk_id__mutmut_4, 
        'xǁContextMemoryǁ_generate_chunk_id__mutmut_5': xǁContextMemoryǁ_generate_chunk_id__mutmut_5
    }
    
    def _generate_chunk_id(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_generate_chunk_id__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_generate_chunk_id__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_chunk_id.__signature__ = _mutmut_signature(xǁContextMemoryǁ_generate_chunk_id__mutmut_orig)
    xǁContextMemoryǁ_generate_chunk_id__mutmut_orig.__name__ = 'xǁContextMemoryǁ_generate_chunk_id'

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_orig(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), key=lambda c: (c.priority, c.access_count, c.last_accessed)
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_1(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), key=lambda c: (c.priority, c.access_count, c.last_accessed)
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_2(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return True

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), key=lambda c: (c.priority, c.access_count, c.last_accessed)
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_3(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = None

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_4(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            None, key=lambda c: (c.priority, c.access_count, c.last_accessed)
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_5(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), key=None
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_6(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            key=lambda c: (c.priority, c.access_count, c.last_accessed)
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_7(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_8(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), key=lambda c: None
        )

        return self.delete_chunk(candidate.chunk_id)

    def xǁContextMemoryǁ_evict_lowest_priority__mutmut_9(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(), key=lambda c: (c.priority, c.access_count, c.last_accessed)
        )

        return self.delete_chunk(None)
    
    xǁContextMemoryǁ_evict_lowest_priority__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_evict_lowest_priority__mutmut_1': xǁContextMemoryǁ_evict_lowest_priority__mutmut_1, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_2': xǁContextMemoryǁ_evict_lowest_priority__mutmut_2, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_3': xǁContextMemoryǁ_evict_lowest_priority__mutmut_3, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_4': xǁContextMemoryǁ_evict_lowest_priority__mutmut_4, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_5': xǁContextMemoryǁ_evict_lowest_priority__mutmut_5, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_6': xǁContextMemoryǁ_evict_lowest_priority__mutmut_6, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_7': xǁContextMemoryǁ_evict_lowest_priority__mutmut_7, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_8': xǁContextMemoryǁ_evict_lowest_priority__mutmut_8, 
        'xǁContextMemoryǁ_evict_lowest_priority__mutmut_9': xǁContextMemoryǁ_evict_lowest_priority__mutmut_9
    }
    
    def _evict_lowest_priority(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_evict_lowest_priority__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_evict_lowest_priority__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _evict_lowest_priority.__signature__ = _mutmut_signature(xǁContextMemoryǁ_evict_lowest_priority__mutmut_orig)
    xǁContextMemoryǁ_evict_lowest_priority__mutmut_orig.__name__ = 'xǁContextMemoryǁ_evict_lowest_priority'

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_orig(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_1(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_2(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = None
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_3(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(None)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_4(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(None)
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_5(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning(None, exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_6(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=None)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_7(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning(exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_8(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", )
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_9(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("XXQuery embedding failed; falling back to existing orderXX", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_10(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_11(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("QUERY EMBEDDING FAILED; FALLING BACK TO EXISTING ORDER", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_12(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = None
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_13(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id not in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_14(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = None
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_15(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    None, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_16(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, None
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_17(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_18(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_19(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append(None)
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_20(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append(None)

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_21(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 1.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_22(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=None, reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_23(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=None)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_24(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_25(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], )
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_26(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: None, reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_27(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[2], reverse=True)
        return [chunk for chunk, _ in scored]

    def xǁContextMemoryǁ_rank_by_similarity__mutmut_28(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.warning("Query embedding failed; falling back to existing order", exc_info=exc)
            return chunks

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.chunk_id in self._embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, self._embeddings[chunk.chunk_id]
                )
                scored.append((chunk, similarity))
            else:
                scored.append((chunk, 0.0))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=False)
        return [chunk for chunk, _ in scored]
    
    xǁContextMemoryǁ_rank_by_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_rank_by_similarity__mutmut_1': xǁContextMemoryǁ_rank_by_similarity__mutmut_1, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_2': xǁContextMemoryǁ_rank_by_similarity__mutmut_2, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_3': xǁContextMemoryǁ_rank_by_similarity__mutmut_3, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_4': xǁContextMemoryǁ_rank_by_similarity__mutmut_4, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_5': xǁContextMemoryǁ_rank_by_similarity__mutmut_5, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_6': xǁContextMemoryǁ_rank_by_similarity__mutmut_6, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_7': xǁContextMemoryǁ_rank_by_similarity__mutmut_7, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_8': xǁContextMemoryǁ_rank_by_similarity__mutmut_8, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_9': xǁContextMemoryǁ_rank_by_similarity__mutmut_9, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_10': xǁContextMemoryǁ_rank_by_similarity__mutmut_10, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_11': xǁContextMemoryǁ_rank_by_similarity__mutmut_11, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_12': xǁContextMemoryǁ_rank_by_similarity__mutmut_12, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_13': xǁContextMemoryǁ_rank_by_similarity__mutmut_13, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_14': xǁContextMemoryǁ_rank_by_similarity__mutmut_14, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_15': xǁContextMemoryǁ_rank_by_similarity__mutmut_15, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_16': xǁContextMemoryǁ_rank_by_similarity__mutmut_16, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_17': xǁContextMemoryǁ_rank_by_similarity__mutmut_17, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_18': xǁContextMemoryǁ_rank_by_similarity__mutmut_18, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_19': xǁContextMemoryǁ_rank_by_similarity__mutmut_19, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_20': xǁContextMemoryǁ_rank_by_similarity__mutmut_20, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_21': xǁContextMemoryǁ_rank_by_similarity__mutmut_21, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_22': xǁContextMemoryǁ_rank_by_similarity__mutmut_22, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_23': xǁContextMemoryǁ_rank_by_similarity__mutmut_23, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_24': xǁContextMemoryǁ_rank_by_similarity__mutmut_24, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_25': xǁContextMemoryǁ_rank_by_similarity__mutmut_25, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_26': xǁContextMemoryǁ_rank_by_similarity__mutmut_26, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_27': xǁContextMemoryǁ_rank_by_similarity__mutmut_27, 
        'xǁContextMemoryǁ_rank_by_similarity__mutmut_28': xǁContextMemoryǁ_rank_by_similarity__mutmut_28
    }
    
    def _rank_by_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_rank_by_similarity__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_rank_by_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _rank_by_similarity.__signature__ = _mutmut_signature(xǁContextMemoryǁ_rank_by_similarity__mutmut_orig)
    xǁContextMemoryǁ_rank_by_similarity__mutmut_orig.__name__ = 'xǁContextMemoryǁ_rank_by_similarity'

    def xǁContextMemoryǁ_cosine_similarity__mutmut_orig(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_1(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) == len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_2(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 1.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_3(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = None
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_4(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(None)
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_5(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x / y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_6(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(None, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_7(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, None))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_8(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_9(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, ))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_10(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = None
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_11(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) * 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_12(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(None) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_13(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x / x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_14(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 1.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_15(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = None

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_16(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) * 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_17(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(None) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_18(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x / x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_19(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 1.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_20(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 and norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_21(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a != 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_22(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 1 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_23(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b != 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_24(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 1:
            return 0.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_25(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 1.0

        return dot / (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_26(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot * (norm_a * norm_b)

    def xǁContextMemoryǁ_cosine_similarity__mutmut_27(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a / norm_b)
    
    xǁContextMemoryǁ_cosine_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_cosine_similarity__mutmut_1': xǁContextMemoryǁ_cosine_similarity__mutmut_1, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_2': xǁContextMemoryǁ_cosine_similarity__mutmut_2, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_3': xǁContextMemoryǁ_cosine_similarity__mutmut_3, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_4': xǁContextMemoryǁ_cosine_similarity__mutmut_4, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_5': xǁContextMemoryǁ_cosine_similarity__mutmut_5, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_6': xǁContextMemoryǁ_cosine_similarity__mutmut_6, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_7': xǁContextMemoryǁ_cosine_similarity__mutmut_7, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_8': xǁContextMemoryǁ_cosine_similarity__mutmut_8, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_9': xǁContextMemoryǁ_cosine_similarity__mutmut_9, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_10': xǁContextMemoryǁ_cosine_similarity__mutmut_10, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_11': xǁContextMemoryǁ_cosine_similarity__mutmut_11, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_12': xǁContextMemoryǁ_cosine_similarity__mutmut_12, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_13': xǁContextMemoryǁ_cosine_similarity__mutmut_13, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_14': xǁContextMemoryǁ_cosine_similarity__mutmut_14, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_15': xǁContextMemoryǁ_cosine_similarity__mutmut_15, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_16': xǁContextMemoryǁ_cosine_similarity__mutmut_16, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_17': xǁContextMemoryǁ_cosine_similarity__mutmut_17, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_18': xǁContextMemoryǁ_cosine_similarity__mutmut_18, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_19': xǁContextMemoryǁ_cosine_similarity__mutmut_19, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_20': xǁContextMemoryǁ_cosine_similarity__mutmut_20, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_21': xǁContextMemoryǁ_cosine_similarity__mutmut_21, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_22': xǁContextMemoryǁ_cosine_similarity__mutmut_22, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_23': xǁContextMemoryǁ_cosine_similarity__mutmut_23, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_24': xǁContextMemoryǁ_cosine_similarity__mutmut_24, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_25': xǁContextMemoryǁ_cosine_similarity__mutmut_25, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_26': xǁContextMemoryǁ_cosine_similarity__mutmut_26, 
        'xǁContextMemoryǁ_cosine_similarity__mutmut_27': xǁContextMemoryǁ_cosine_similarity__mutmut_27
    }
    
    def _cosine_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_cosine_similarity__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_cosine_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cosine_similarity.__signature__ = _mutmut_signature(xǁContextMemoryǁ_cosine_similarity__mutmut_orig)
    xǁContextMemoryǁ_cosine_similarity__mutmut_orig.__name__ = 'xǁContextMemoryǁ_cosine_similarity'

    def xǁContextMemoryǁ_save_to_storage__mutmut_orig(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_1(self):
        """Save memory to storage."""
        if self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_2(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=None, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_3(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=None)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_4(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_5(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, )

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_6(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=False, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_7(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=False)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_8(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = None

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_9(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "XXchunksXX": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_10(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "CHUNKS": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_11(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "XXcontentXX": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_12(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "CONTENT": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_13(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "XXsummaryXX": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_14(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "SUMMARY": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_15(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "XXtoken_countXX": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_16(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "TOKEN_COUNT": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_17(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "XXpriorityXX": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_18(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "PRIORITY": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_19(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "XXmetadataXX": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_20(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "METADATA": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_21(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(None, "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_22(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", None) as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_23(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open("w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_24(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", ) as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_25(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path * "memory.json", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_26(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "XXmemory.jsonXX", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_27(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "MEMORY.JSON", "w") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_28(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "XXwXX") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_29(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "W") as f:
            json.dump(data, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_30(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(None, f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_31(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, None)

    def xǁContextMemoryǁ_save_to_storage__mutmut_32(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(f)

    def xǁContextMemoryǁ_save_to_storage__mutmut_33(self):
        """Save memory to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        data = {
            "chunks": {
                cid: {
                    "content": c.content,
                    "summary": c.summary,
                    "token_count": c.token_count,
                    "priority": c.priority,
                    "metadata": c.metadata,
                }
                for cid, c in self._chunks.items()
            }
        }

        with open(self.storage_path / "memory.json", "w") as f:
            json.dump(data, )
    
    xǁContextMemoryǁ_save_to_storage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_save_to_storage__mutmut_1': xǁContextMemoryǁ_save_to_storage__mutmut_1, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_2': xǁContextMemoryǁ_save_to_storage__mutmut_2, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_3': xǁContextMemoryǁ_save_to_storage__mutmut_3, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_4': xǁContextMemoryǁ_save_to_storage__mutmut_4, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_5': xǁContextMemoryǁ_save_to_storage__mutmut_5, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_6': xǁContextMemoryǁ_save_to_storage__mutmut_6, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_7': xǁContextMemoryǁ_save_to_storage__mutmut_7, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_8': xǁContextMemoryǁ_save_to_storage__mutmut_8, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_9': xǁContextMemoryǁ_save_to_storage__mutmut_9, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_10': xǁContextMemoryǁ_save_to_storage__mutmut_10, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_11': xǁContextMemoryǁ_save_to_storage__mutmut_11, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_12': xǁContextMemoryǁ_save_to_storage__mutmut_12, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_13': xǁContextMemoryǁ_save_to_storage__mutmut_13, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_14': xǁContextMemoryǁ_save_to_storage__mutmut_14, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_15': xǁContextMemoryǁ_save_to_storage__mutmut_15, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_16': xǁContextMemoryǁ_save_to_storage__mutmut_16, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_17': xǁContextMemoryǁ_save_to_storage__mutmut_17, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_18': xǁContextMemoryǁ_save_to_storage__mutmut_18, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_19': xǁContextMemoryǁ_save_to_storage__mutmut_19, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_20': xǁContextMemoryǁ_save_to_storage__mutmut_20, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_21': xǁContextMemoryǁ_save_to_storage__mutmut_21, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_22': xǁContextMemoryǁ_save_to_storage__mutmut_22, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_23': xǁContextMemoryǁ_save_to_storage__mutmut_23, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_24': xǁContextMemoryǁ_save_to_storage__mutmut_24, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_25': xǁContextMemoryǁ_save_to_storage__mutmut_25, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_26': xǁContextMemoryǁ_save_to_storage__mutmut_26, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_27': xǁContextMemoryǁ_save_to_storage__mutmut_27, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_28': xǁContextMemoryǁ_save_to_storage__mutmut_28, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_29': xǁContextMemoryǁ_save_to_storage__mutmut_29, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_30': xǁContextMemoryǁ_save_to_storage__mutmut_30, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_31': xǁContextMemoryǁ_save_to_storage__mutmut_31, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_32': xǁContextMemoryǁ_save_to_storage__mutmut_32, 
        'xǁContextMemoryǁ_save_to_storage__mutmut_33': xǁContextMemoryǁ_save_to_storage__mutmut_33
    }
    
    def _save_to_storage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_save_to_storage__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_save_to_storage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _save_to_storage.__signature__ = _mutmut_signature(xǁContextMemoryǁ_save_to_storage__mutmut_orig)
    xǁContextMemoryǁ_save_to_storage__mutmut_orig.__name__ = 'xǁContextMemoryǁ_save_to_storage'

    def xǁContextMemoryǁ_load_from_storage__mutmut_orig(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_1(self):
        """Load memory from storage."""
        if self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_2(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = None
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_3(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path * "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_4(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "XXmemory.jsonXX"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_5(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "MEMORY.JSON"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_6(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_7(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(None) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_8(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = None

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_9(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(None)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_10(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get(None, {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_11(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", None).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_12(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get({}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_13(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", ).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_14(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("XXchunksXX", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_15(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("CHUNKS", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_16(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = None
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_17(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=None,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_18(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=None,
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_19(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=None,
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_20(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=None,
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_21(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=None,
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_22(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=None,
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_23(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_24(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_25(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_26(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_27(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_28(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_29(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["XXcontentXX"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_30(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["CONTENT"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_31(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get(None),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_32(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("XXsummaryXX"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_33(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("SUMMARY"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_34(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get(None, 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_35(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", None),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_36(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get(0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_37(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", ),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_38(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("XXtoken_countXX", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_39(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("TOKEN_COUNT", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_40(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 1),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_41(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get(None, 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_42(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", None),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_43(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get(50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_44(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", ),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_45(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("XXpriorityXX", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_46(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("PRIORITY", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_47(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 51),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_48(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get(None, {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_49(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", None),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_50(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get({}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_51(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", ),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_52(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("XXmetadataXX", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_53(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("METADATA", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_54(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = None
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_55(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens = chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_56(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens -= chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_57(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(None)
            logger.error("Failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_58(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error(None, path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_59(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", None, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_60(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, exc_info=None)

    def xǁContextMemoryǁ_load_from_storage__mutmut_61(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error(path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_62(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_63(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("Failed to load memory from %s", path, )

    def xǁContextMemoryǁ_load_from_storage__mutmut_64(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("XXFailed to load memory from %sXX", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_65(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("failed to load memory from %s", path, exc_info=exc)

    def xǁContextMemoryǁ_load_from_storage__mutmut_66(self):
        """Load memory from storage."""
        if not self.storage_path:
            return

        path = self.storage_path / "memory.json"
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for cid, chunk_data in data.get("chunks", {}).items():
                chunk = MemoryChunk(
                    chunk_id=cid,
                    content=chunk_data["content"],
                    summary=chunk_data.get("summary"),
                    token_count=chunk_data.get("token_count", 0),
                    priority=chunk_data.get("priority", 50),
                    metadata=chunk_data.get("metadata", {}),
                )
                self._chunks[cid] = chunk
                self._total_tokens += chunk.token_count
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.error("FAILED TO LOAD MEMORY FROM %S", path, exc_info=exc)
    
    xǁContextMemoryǁ_load_from_storage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextMemoryǁ_load_from_storage__mutmut_1': xǁContextMemoryǁ_load_from_storage__mutmut_1, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_2': xǁContextMemoryǁ_load_from_storage__mutmut_2, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_3': xǁContextMemoryǁ_load_from_storage__mutmut_3, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_4': xǁContextMemoryǁ_load_from_storage__mutmut_4, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_5': xǁContextMemoryǁ_load_from_storage__mutmut_5, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_6': xǁContextMemoryǁ_load_from_storage__mutmut_6, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_7': xǁContextMemoryǁ_load_from_storage__mutmut_7, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_8': xǁContextMemoryǁ_load_from_storage__mutmut_8, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_9': xǁContextMemoryǁ_load_from_storage__mutmut_9, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_10': xǁContextMemoryǁ_load_from_storage__mutmut_10, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_11': xǁContextMemoryǁ_load_from_storage__mutmut_11, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_12': xǁContextMemoryǁ_load_from_storage__mutmut_12, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_13': xǁContextMemoryǁ_load_from_storage__mutmut_13, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_14': xǁContextMemoryǁ_load_from_storage__mutmut_14, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_15': xǁContextMemoryǁ_load_from_storage__mutmut_15, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_16': xǁContextMemoryǁ_load_from_storage__mutmut_16, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_17': xǁContextMemoryǁ_load_from_storage__mutmut_17, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_18': xǁContextMemoryǁ_load_from_storage__mutmut_18, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_19': xǁContextMemoryǁ_load_from_storage__mutmut_19, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_20': xǁContextMemoryǁ_load_from_storage__mutmut_20, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_21': xǁContextMemoryǁ_load_from_storage__mutmut_21, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_22': xǁContextMemoryǁ_load_from_storage__mutmut_22, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_23': xǁContextMemoryǁ_load_from_storage__mutmut_23, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_24': xǁContextMemoryǁ_load_from_storage__mutmut_24, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_25': xǁContextMemoryǁ_load_from_storage__mutmut_25, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_26': xǁContextMemoryǁ_load_from_storage__mutmut_26, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_27': xǁContextMemoryǁ_load_from_storage__mutmut_27, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_28': xǁContextMemoryǁ_load_from_storage__mutmut_28, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_29': xǁContextMemoryǁ_load_from_storage__mutmut_29, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_30': xǁContextMemoryǁ_load_from_storage__mutmut_30, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_31': xǁContextMemoryǁ_load_from_storage__mutmut_31, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_32': xǁContextMemoryǁ_load_from_storage__mutmut_32, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_33': xǁContextMemoryǁ_load_from_storage__mutmut_33, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_34': xǁContextMemoryǁ_load_from_storage__mutmut_34, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_35': xǁContextMemoryǁ_load_from_storage__mutmut_35, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_36': xǁContextMemoryǁ_load_from_storage__mutmut_36, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_37': xǁContextMemoryǁ_load_from_storage__mutmut_37, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_38': xǁContextMemoryǁ_load_from_storage__mutmut_38, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_39': xǁContextMemoryǁ_load_from_storage__mutmut_39, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_40': xǁContextMemoryǁ_load_from_storage__mutmut_40, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_41': xǁContextMemoryǁ_load_from_storage__mutmut_41, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_42': xǁContextMemoryǁ_load_from_storage__mutmut_42, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_43': xǁContextMemoryǁ_load_from_storage__mutmut_43, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_44': xǁContextMemoryǁ_load_from_storage__mutmut_44, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_45': xǁContextMemoryǁ_load_from_storage__mutmut_45, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_46': xǁContextMemoryǁ_load_from_storage__mutmut_46, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_47': xǁContextMemoryǁ_load_from_storage__mutmut_47, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_48': xǁContextMemoryǁ_load_from_storage__mutmut_48, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_49': xǁContextMemoryǁ_load_from_storage__mutmut_49, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_50': xǁContextMemoryǁ_load_from_storage__mutmut_50, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_51': xǁContextMemoryǁ_load_from_storage__mutmut_51, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_52': xǁContextMemoryǁ_load_from_storage__mutmut_52, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_53': xǁContextMemoryǁ_load_from_storage__mutmut_53, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_54': xǁContextMemoryǁ_load_from_storage__mutmut_54, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_55': xǁContextMemoryǁ_load_from_storage__mutmut_55, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_56': xǁContextMemoryǁ_load_from_storage__mutmut_56, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_57': xǁContextMemoryǁ_load_from_storage__mutmut_57, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_58': xǁContextMemoryǁ_load_from_storage__mutmut_58, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_59': xǁContextMemoryǁ_load_from_storage__mutmut_59, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_60': xǁContextMemoryǁ_load_from_storage__mutmut_60, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_61': xǁContextMemoryǁ_load_from_storage__mutmut_61, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_62': xǁContextMemoryǁ_load_from_storage__mutmut_62, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_63': xǁContextMemoryǁ_load_from_storage__mutmut_63, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_64': xǁContextMemoryǁ_load_from_storage__mutmut_64, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_65': xǁContextMemoryǁ_load_from_storage__mutmut_65, 
        'xǁContextMemoryǁ_load_from_storage__mutmut_66': xǁContextMemoryǁ_load_from_storage__mutmut_66
    }
    
    def _load_from_storage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextMemoryǁ_load_from_storage__mutmut_orig"), object.__getattribute__(self, "xǁContextMemoryǁ_load_from_storage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_from_storage.__signature__ = _mutmut_signature(xǁContextMemoryǁ_load_from_storage__mutmut_orig)
    xǁContextMemoryǁ_load_from_storage__mutmut_orig.__name__ = 'xǁContextMemoryǁ_load_from_storage'
