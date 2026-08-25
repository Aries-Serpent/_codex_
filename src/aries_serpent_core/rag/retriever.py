"""
RAG Retriever Module
Provides semantic search over FAISS indices with provenance tracking.
"""

import hashlib
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from time import time
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None


class Retriever:
    """
    Semantic retriever using FAISS indices with provenance tracking.

    Supports loading persisted indices and querying with configurable top-k results.
    Returns results with full provenance (file, line ranges, scores, timestamps).
    """

    def __init__(
        self,
        index_dir: str = ".codex/tenants",
        index_name: str = "default",
        tenant_id: str = "default",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize retriever with index location and embedding model.

        Args:
            index_dir: Base directory containing tenant indices
            index_name: Name of the index to load
            tenant_id: Tenant identifier for multi-tenancy
            model_name: Embedding model name for query encoding
            cache_dir: Optional cache directory for model weights
        """
        self.index_dir = index_dir
        self.index_name = index_name
        self.tenant_id = tenant_id
        self.model_name = model_name
        self.cache_dir = cache_dir

        self.faiss_index = None
        self.chunks_metadata: list[dict[str, Any]] = []
        self.index_metadata: dict[str, Any] = {}
        self.model = None

        self._load_index()
        self._load_model()

    def _load_index(self) -> None:
        """Load FAISS index and metadata from disk."""
        from aries_serpent_core.rag.indexer import load_index

        try:
            self.faiss_index, self.chunks_metadata, self.index_metadata = load_index(
                index_name=self.index_name,
                tenant_id=self.tenant_id,
                index_dir=self.index_dir,
            )
            logger.info("Loaded index with %d chunks", len(self.chunks_metadata))
        except FileNotFoundError as e:
            type(e).__name__
            logger.warning("Index not found; use indexer.py to build an index first")
            # Allow initialization without an index for testing
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.error("Error loading index")
            raise

    def _load_model(self) -> None:
        """Load embedding model for query encoding."""
        if SentenceTransformer is None:
            logger.warning(
                "sentence-transformers not installed; using TF-IDF fallback for query encoding"
            )
            self._load_tfidf_fallback_model()
            return

        try:
            from aries_serpent_core.rag._model_utils import safe_load_sentence_transformer

            logger.info("Loading query embedding model")

            self.model = safe_load_sentence_transformer(self.model_name, self.cache_dir)

        except (RuntimeError, OSError, ValueError, NotImplementedError) as e:
            type(e).__name__
            logger.warning("Failed to load query embedding model; using TF-IDF fallback")
            self._load_tfidf_fallback_model()
        except TypeError as e:
            type(e).__name__
            logger.error("Error loading embedding model")
            raise

    def _load_tfidf_fallback_model(self) -> None:
        """Load an offline TF-IDF model fitted on indexed chunks."""
        from aries_serpent_core.rag.embeddings import TfidfEmbeddingProvider

        chunk_texts = [
            chunk.get("text", "").strip()
            for chunk in self.chunks_metadata
            if chunk.get("text", "").strip()
        ]
        if not chunk_texts:
            raise ImportError("TF-IDF fallback requires chunk text metadata to fit query encoder")

        dimension = int(
            self.index_metadata.get("dimension")
            or (self.faiss_index.d if self.faiss_index is not None else 384)
        )
        provider = TfidfEmbeddingProvider(max_features=max(1, dimension))
        provider.encode(chunk_texts)
        self.model = provider
        logger.info(
            "Loaded TF-IDF fallback query model with %s fitted chunks",
            len(chunk_texts),
        )

    def query(
        self, q: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> list[dict[str, Any]]:
        """
        Query the index with a text query and return top-k results.

        Args:
            q: Query text
            top_k: Number of results to return
            min_score: Optional minimum similarity score threshold (lower L2 distance = better)

        Returns:
            List of result dictionaries with fields:
            - text: chunk text
            - file: source file path (if available)
            - start_line: start line number (estimated)
            - end_line: end line number (estimated)
            - score: L2 distance (lower is better)
            - generated_at: timestamp of result generation
        """
        if not self.faiss_index:
            logger.error("No index loaded. Cannot perform query.")
            return []

        if not q or not q.strip():
            logger.warning("Empty query provided")
            return []

        if top_k <= 0:
            logger.warning("top_k must be positive, using default of 5")
            top_k = 5

        # Encode query
        logger.debug("Encoding query input")
        query_embedding = self.model.encode(
            [q], convert_to_numpy=True, show_progress_bar=False, device="cpu"
        )

        # Search index
        logger.debug("Searching index for top %d results", top_k)
        distances, indices = self.faiss_index.search(query_embedding.astype(np.float32), top_k)

        # Build results with provenance
        results = []
        timestamp = datetime.now(UTC).isoformat()

        effective_top_k = min(top_k, len(indices[0]))
        for _, (idx, distance) in enumerate(
            zip(indices[0][:effective_top_k], distances[0][:effective_top_k], strict=False)
        ):
            # Skip invalid indices
            if idx < 0 or idx >= len(self.chunks_metadata):
                continue

            # Apply score threshold if specified
            if min_score is not None and distance > min_score:
                continue

            chunk = self.chunks_metadata[idx]

            # Estimate line numbers from character positions
            # This is approximate - actual line numbers would require file re-reading
            start_line = self._estimate_line_number(chunk.get("start", 0))
            end_line = self._estimate_line_number(chunk.get("end", 0))

            result = {
                "text": chunk.get("text", ""),
                "file": self._extract_file_from_metadata(chunk),
                "start_line": start_line,
                "end_line": end_line,
                "score": float(distance),
                "generated_at": timestamp,
                "chunk_id": chunk.get("id", idx),
                "text_hash": chunk.get("text_hash", ""),
            }

            results.append(result)

        logger.info("Retrieved %d results for query", len(results))
        return results

    def _estimate_line_number(self, char_pos: int, chars_per_line: int = 80) -> int:
        """
        Estimate line number from character position using a fixed heuristic.

        This is an approximate helper that uses a fixed average characters-per-line
        heuristic. It does **not** re-read source files or use precomputed line
        offsets, so results should be treated as best-effort only.

        Args:
            char_pos: Character position in file.
            chars_per_line: Estimated average characters per line (default 80).

        Returns:
            Estimated line number (1-indexed).

        Note:
            This uses a simple heuristic based on ``chars_per_line`` (default 80).

            **Warning**: This estimation may be significantly inaccurate for files
            with varying line lengths (e.g., markdown with long paragraphs vs code
            with short lines). For production use, or when you need precise
            line-level attribution, you should implement one of the following
            strategies *outside* of this helper:

            - Store actual line numbers or line offsets during chunking.
            - Calculate an average line length from the original source files and
              pass a more accurate ``chars_per_line`` value.
            - Re-read the original files at query time to map character positions
              to exact line numbers.
        """
        if char_pos <= 0:
            return 1
        return max(1, (char_pos // chars_per_line) + 1)

    def _extract_file_from_metadata(self, chunk: dict[str, Any]) -> str:
        """
        Extract source file path from chunk or index metadata.

        Args:
            chunk: Chunk metadata dictionary

        Returns:
            File path or "unknown"
        """
        # Check if chunk has direct file reference
        if "file" in chunk:
            return chunk["file"]

        # Try to extract from index metadata
        if "files" in self.index_metadata:
            files = self.index_metadata["files"]
            if files and len(files) > 0:
                # This is a simplification - proper implementation would track
                # which file each chunk came from
                return files[0].get("file", "unknown")

        return "unknown"

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the loaded index.

        Returns:
            Dictionary with index statistics
        """
        return {
            "index_name": self.index_name,
            "tenant_id": self.tenant_id,
            "num_vectors": self.faiss_index.ntotal if self.faiss_index else 0,
            "num_chunks": len(self.chunks_metadata),
            "index_metadata": self.index_metadata,
        }

    def reload(self) -> None:
        """Reload the index from disk (useful if index was updated)."""
        logger.info("Reloading index from disk")
        self._load_index()


class MultiIndexRetriever:
    """
    Retriever that can query across multiple indices and merge results.

    Useful for querying across different document collections or tenants.
    """

    def __init__(
        self,
        indices: list[dict[str, str]],
        index_dir: str = ".codex/tenants",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        Initialize multi-index retriever.

        Args:
            indices: List of dicts with 'index_name' and 'tenant_id' keys
            index_dir: Base directory for indices
            model_name: Embedding model name
        """
        self.retrievers: list[Any] = []

        for idx_config in indices:
            try:
                retriever = Retriever(
                    index_dir=index_dir,
                    index_name=idx_config["index_name"],
                    tenant_id=idx_config.get("tenant_id", "default"),
                    model_name=model_name,
                )
                # Only add retriever if it successfully loaded an index
                if retriever.faiss_index is not None:
                    self.retrievers.append(retriever)
                else:
                    logger.warning(
                        f"Skipping index {idx_config.get('index_name')}: no index loaded"
                    )
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.warning(f"Failed to load index {idx_config.get('index_name')}: <ERROR_TYPE>")

        logger.info(f"Initialized with {len(self.retrievers)} indices")

    def query(
        self, q: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> list[dict[str, Any]]:
        """
        Query all indices and merge results by score.

        Args:
            q: Query text
            top_k: Total number of results to return across all indices
            min_score: Optional minimum similarity score threshold

        Returns:
            Merged and sorted list of results from all indices
        """
        all_results = []

        # Query each index
        for retriever in self.retrievers:
            try:
                results = retriever.query(q, top_k=top_k * 2, min_score=min_score)
                # Add index info to results
                for r in results:
                    r["index_name"] = retriever.index_name
                    r["tenant_id"] = retriever.tenant_id
                all_results.extend(results)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.warning(f"Error querying index {retriever.index_name}: <ERROR_TYPE>")

        # Sort by score (lower is better for L2 distance)
        all_results.sort(key=lambda x: x["score"])

        # Return top_k
        return all_results[:top_k]

    def get_stats(self) -> list[dict[str, Any]]:
        """Get statistics for all loaded indices."""
        return [r.get_stats() for r in self.retrievers]


# ============================================================================
# Cached Retriever with LRU Cache (Phase B)
# ============================================================================


class LRUCache:
    """
    Simple LRU (Least Recently Used) cache implementation.

    Maintains a fixed-size cache that evicts the least recently used item
    when capacity is reached. Used for caching query results in CachedRetriever.

    Attributes:
        maxsize: Maximum number of items in cache
        cache: Ordered dictionary maintaining insertion order
        hits: Number of cache hits
        misses: Number of cache misses
    """

    def __init__(self, maxsize: int = 1000):
        """
        Initialize LRU cache.

        Args:
            maxsize: Maximum cache size (default: 1000)
        """
        self.maxsize = maxsize
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        """
        Put value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            # Update existing key value and mark as most-recently-used
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Add new key
            self.cache[key] = value
            # Evict oldest if over capacity
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }


class CachedRetriever(Retriever):
    """
    Retriever with LRU query result caching for improved performance.

    Caches query results to avoid repeated FAISS searches for identical or
    similar queries. Particularly useful for expanded context workflows
    (64k-512k tokens) where repeated queries are common.

    Features:
        - LRU cache with configurable size and TTL
        - Automatic cache invalidation based on TTL
        - Cache statistics and monitoring
        - Optional query normalization for better hit rates

    Example:
        >>> cached = CachedRetriever(
        ...     index_name="docs",
        ...     tenant_id="customer_a",
        ...     cache_ttl=3600,  # 1 hour
        ...     cache_maxsize=1000
        ... )
        >>> results = cached.query_with_cache("how to use API")
        >>> stats = cached.get_cache_stats()
        >>> logger.info(f"Hit rate: {stats['hit_rate']:.2%}")
    """

    def __init__(
        self,
        index_dir: str = ".codex/tenants",
        index_name: str = "default",
        tenant_id: str = "default",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        cache_maxsize: int = 1000,
        normalize_queries: bool = True,
    ):
        """
        Initialize cached retriever.

        Args:
            index_dir: Base directory containing tenant indices
            index_name: Name of the index to load
            tenant_id: Tenant identifier for multi-tenancy
            model_name: Embedding model name for query encoding
            cache_dir: Optional cache directory for model weights
            cache_ttl: Time-to-live for cache entries in seconds (default: 3600)
            cache_maxsize: Maximum number of cache entries (default: 1000)
            normalize_queries: Whether to normalize queries before caching (default: True)
        """
        super().__init__(index_dir, index_name, tenant_id, model_name, cache_dir)

        self.cache_ttl = cache_ttl
        self.normalize_queries = normalize_queries
        self.query_cache = LRUCache(maxsize=cache_maxsize)
        self.cache_timestamps: dict[str, float] = {}  # Track when entries were cached

        logger.info(f"Initialized CachedRetriever with TTL={cache_ttl}s, maxsize={cache_maxsize}")

    def _normalize_query(self, q: str) -> str:
        """
        Normalize query for better cache hit rates.

        Args:
            q: Original query

        Returns:
            Normalized query
        """
        if not self.normalize_queries:
            return q

        # Convert to lowercase and strip whitespace
        normalized = q.lower().strip()

        # Remove extra whitespace
        return " ".join(normalized.split())

    def _make_cache_key(self, q: str, top_k: int, min_score: Optional[float]) -> str:
        """
        Create cache key from query parameters.

        Args:
            q: Query text
            top_k: Number of results
            min_score: Minimum score threshold

        Returns:
            Cache key string
        """
        normalized_q = self._normalize_query(q)

        # Create key from query + parameters
        key_str = f"{normalized_q}|{top_k}|{min_score}"

        # Hash for consistent key length
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]

        return f"query_{key_hash}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached entry is still valid based on TTL.

        Args:
            cache_key: Cache key to check

        Returns:
            True if cache entry is valid, False otherwise
        """
        if cache_key not in self.cache_timestamps:
            return False

        cached_time = self.cache_timestamps[cache_key]
        current_time = time()

        return (current_time - cached_time) < self.cache_ttl

    def query_with_cache(
        self, q: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> list[dict[str, Any]]:
        """
        Query with caching support.

        Checks cache before performing FAISS search. Returns cached results
        if available and not expired, otherwise performs search and caches result.

        Args:
            q: Query text
            top_k: Number of results to return
            min_score: Optional minimum similarity score threshold

        Returns:
            List of result dictionaries (same format as Retriever.query)
        """
        # Create cache key
        cache_key = self._make_cache_key(q, top_k, min_score)

        # Check if valid cached entry exists
        if self._is_cache_valid(cache_key):
            cached_results = self.query_cache.get(cache_key)
            if cached_results is not None:
                logger.debug(f"Cache HIT for query: {q[:50]}...")
                return cached_results

        # Cache miss or expired - remove expired entry if exists
        if cache_key in self.query_cache.cache:
            del self.query_cache.cache[cache_key]
            if cache_key in self.cache_timestamps:
                del self.cache_timestamps[cache_key]

        # Cache miss - perform actual query and manually track miss
        logger.debug(f"Cache MISS for query: {q[:50]}...")
        self.query_cache.misses += 1  # Explicit miss tracking
        results = self.query(q, top_k=top_k, min_score=min_score)

        # Cache results
        self.query_cache.put(cache_key, results)
        self.cache_timestamps[cache_key] = time()

        return results

    def clear_cache(self) -> None:
        """Clear all cached query results."""
        self.query_cache.clear()
        self.cache_timestamps.clear()
        logger.info("Query cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache metrics including hit rate, size, etc.
        """
        cache_stats = self.query_cache.get_stats()
        cache_stats["ttl"] = self.cache_ttl
        cache_stats["normalize_queries"] = self.normalize_queries
        cache_stats["valid_entries"] = sum(
            1 for key in self.cache_timestamps if self._is_cache_valid(key)
        )
        return cache_stats

    def invalidate_expired(self) -> None:
        """Manually invalidate all expired cache entries."""
        current_time = time()
        expired_keys = [
            key
            for key, timestamp in self.cache_timestamps.items()
            if (current_time - timestamp) >= self.cache_ttl
        ]

        for key in expired_keys:
            if key in self.query_cache.cache:
                del self.query_cache.cache[key]
            del self.cache_timestamps[key]

        logger.info(f"Invalidated {len(expired_keys)} expired cache entries")


class RAGRetriever:
    """Lightweight device-aware retriever facade.

    Provides the ``RAGRetriever`` name expected by device-placement tests and
    external callers while delegating heavy index/model loading to :class:`Retriever`.

    This class intentionally performs *no* model or index loading at construction
    time so that it can be instantiated safely in environments where the default
    HuggingFace model is not cached.  Call :meth:`load` to initialise a full
    :class:`Retriever` when the index and model are available.
    """

    def __init__(self, device: str = "cpu") -> None:
        self.device = device
        self._retriever: Optional[Retriever] = None

    def load(
        self,
        index_dir: str = ".codex/tenants",
        index_name: str = "default",
        tenant_id: str = "default",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ) -> "RAGRetriever":
        """Lazily initialise the underlying :class:`Retriever`."""
        self._retriever = Retriever(
            index_dir=index_dir,
            index_name=index_name,
            tenant_id=tenant_id,
            model_name=model_name,
            cache_dir=cache_dir,
        )
        return self

    def query(self, query_text: str, top_k: int = 5, min_score: float = 0.0) -> list[Any]:
        """Delegate query to the underlying retriever (requires :meth:`load` first)."""
        if self._retriever is None:
            raise RuntimeError(
                "RAGRetriever is not initialised. "
                "Call RAGRetriever.load(index_dir=..., model_name=...) before querying."
            )
        return self._retriever.query(query_text, top_k=top_k, min_score=min_score)
