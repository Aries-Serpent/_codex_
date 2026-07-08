"""
Context Memory

External memory management for long-context handling with chunking,
RAG integration, map-reduce summarization, and streaming support.
"""

import hashlib
import json
import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryChunk:
    """A chunk of content stored in memory."""

    chunk_id: str
    content: str
    summary: Optional[str] = None
    token_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    priority: int = 50
    metadata: dict = field(default_factory=dict)

    def access(self):
        """Record an access to this chunk."""
        self.last_accessed = datetime.now(UTC)
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

    def __init__(
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

    def store(
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
                except (ConnectionError, TimeoutError) as exc:
                    type(exc).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning(
                        "Failed to summarize chunk; storing without summary",
                        exc_info=exc,
                    )

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
                except (ValueError, TypeError, RuntimeError) as exc:
                    type(exc).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning(
                        "Failed to embed chunk %s; proceeding without embedding",
                        chunk_id,
                        exc_info=exc,
                    )

        # Persist if storage configured
        if self.storage_path:
            self._save_to_storage()

        return chunk_ids

    def retrieve(
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
                key=lambda c: (c.priority, c.access_count, c.last_accessed),
                reverse=True,
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

    def map_reduce_summarize(self, chunk_ids: Optional[list[str]] = None) -> str:
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
                except (ValueError, TypeError, RuntimeError) as exc:
                    type(exc).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning(
                        "Chunk summarization failed; using fallback content",
                        exc_info=exc,
                    )
                    summaries.append(chunk.content[:200] + "...")

        # Reduce phase: combine summaries
        if len(summaries) == 1:
            return summaries[0]

        combined = "\n\n".join(summaries)
        try:
            return self._summarizer(combined)
        except (ValueError, TypeError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning(
                "Failed to summarize combined content; returning raw aggregation",
                exc_info=exc,
            )
            return combined

    def stream_retrieve(
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

    def get_chunk(self, chunk_id: str) -> Optional[MemoryChunk]:
        """Get a specific chunk by ID."""
        chunk = self._chunks.get(chunk_id)
        if chunk:
            chunk.access()
        return chunk

    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from memory."""
        if chunk_id in self._chunks:
            chunk = self._chunks.pop(chunk_id)
            self._total_tokens -= chunk.token_count
            self._embeddings.pop(chunk_id, None)
            return True
        return False

    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            "chunk_count": len(self._chunks),
            "total_tokens": self._total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": self._total_tokens / self.max_total_tokens,
            "has_embeddings": bool(self._embeddings),
            "has_summarizer": self._summarizer is not None,
        }

    def clear(self):
        """Clear all memory."""
        self._chunks.clear()
        self._embeddings.clear()
        self._total_tokens = 0

    def _split_into_chunks(self, content: str) -> list[str]:
        """Split content into chunks based on token limit."""
        tokens = self._token_counter(content)

        if tokens <= self.max_chunk_tokens:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk: list[Any] = []
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

    def _split_content(self, content: str, max_tokens: int) -> list[str]:
        """Split content into pieces of max_tokens."""
        pieces = []
        words = content.split()
        current: list[Any] = []
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

    def _generate_chunk_id(self, content: str) -> str:
        """Generate unique ID for chunk."""
        timestamp = datetime.now(UTC).isoformat()
        hash_input = f"{content[:100]}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _evict_lowest_priority(self) -> bool:
        """Evict lowest priority chunk to make room."""
        if not self._chunks:
            return False

        # Find lowest priority, least accessed chunk
        candidate = min(
            self._chunks.values(),
            key=lambda c: (c.priority, c.access_count, c.last_accessed),
        )

        return self.delete_chunk(candidate.chunk_id)

    def _rank_by_similarity(self, query: str, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        """Rank chunks by embedding similarity to query."""
        if not self._embedder:
            return chunks

        try:
            query_embedding = self._embedder(query)
        except (ValueError, TypeError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
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

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def _save_to_storage(self):
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

    def _load_from_storage(self):
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
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to load memory from %s", path, exc_info=exc)
