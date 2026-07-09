"""
Query Rewriting and Expansion Module

Provides query optimization capabilities:
- Query expansion (synonyms, related terms)
- Query rewriting (normalization, clarification)
- Hybrid query generation (sparse + dense)
- Multi-query strategies
"""

import hashlib
import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from codex.logging.structured_logger import logger


class QueryRewriteStrategy(Enum):
    """Available query rewrite strategies."""

    NONE = "none"  # No rewriting
    NORMALIZE = "normalize"  # Basic normalization
    EXPAND = "expand"  # Query expansion
    DECOMPOSE = "decompose"  # Break into sub-queries
    HYBRID = "hybrid"  # Generate both sparse and dense versions
    MULTI = "multi"  # Generate multiple query variants


@dataclass
class QueryRewriteConfig:
    """Configuration for query rewriting."""

    strategy: QueryRewriteStrategy = QueryRewriteStrategy.NORMALIZE

    # Normalization options
    lowercase: bool = True
    remove_punctuation: bool = True
    remove_stopwords: bool = False
    stem_words: bool = False

    # Expansion options
    max_expansions: int = 5
    expansion_method: str = "synonyms"  # synonyms, embeddings, llm

    # Decomposition options
    max_sub_queries: int = 3

    # Hybrid options
    sparse_weight: float = 0.3
    dense_weight: float = 0.7

    # Multi-query options
    num_variants: int = 3

    # Caching
    enable_cache: bool = True
    cache_size: int = 1000


@dataclass
class RewrittenQuery:
    """Represents a rewritten query."""

    original_query: str
    rewritten_query: str
    strategy: QueryRewriteStrategy
    expansions: list[str] = field(default_factory=list)
    sub_queries: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def query_hash(self) -> str:
        """Generate hash for caching."""
        return hashlib.sha256(self.original_query.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_query": self.original_query,
            "rewritten_query": self.rewritten_query,
            "strategy": self.strategy.value,
            "expansions": self.expansions,
            "sub_queries": self.sub_queries,
            "metadata": self.metadata,
        }


class BaseQueryRewriter(ABC):
    """Base class for query rewrite strategies."""

    def __init__(self, config: QueryRewriteConfig):
        self.config = config

    @abstractmethod
    def rewrite(self, query: str) -> RewrittenQuery:
        """Rewrite the query."""


class NormalizeRewriter(BaseQueryRewriter):
    """
    Basic query normalization.

    Applies cleaning and normalization:
    - Lowercase conversion
    - Punctuation removal
    - Whitespace normalization
    - Optional stopword removal
    """

    # Common English stopwords
    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "that",
        "the",
        "to",
        "was",
        "were",
        "will",
        "with",
    }

    def rewrite(self, query: str) -> RewrittenQuery:
        """Normalize the query."""
        normalized = query

        # Lowercase
        if self.config.lowercase:
            normalized = normalized.lower()

        # Remove punctuation
        if self.config.remove_punctuation:
            normalized = re.sub(r"[^\w\s]", " ", normalized)

        # Normalize whitespace
        normalized = " ".join(normalized.split())

        # Remove stopwords
        if self.config.remove_stopwords:
            words = normalized.split()
            words = [w for w in words if w not in self.STOPWORDS]
            normalized = " ".join(words)

        return RewrittenQuery(
            original_query=query,
            rewritten_query=normalized,
            strategy=QueryRewriteStrategy.NORMALIZE,
            metadata={"normalized": True},
        )


class ExpansionRewriter(BaseQueryRewriter):
    """
    Query expansion using synonyms and related terms.

    Expands the query with:
    - Synonyms from a word list
    - Related terms
    - Spelling corrections
    """

    # Simple synonym map (can be expanded or loaded from file)
    SYNONYM_MAP = {
        "quick": ["fast", "rapid", "speedy"],
        "big": ["large", "huge", "enormous"],
        "small": ["little", "tiny", "compact"],
        "good": ["great", "excellent", "fine"],
        "bad": ["poor", "terrible", "awful"],
        "new": ["latest", "recent", "fresh"],
        "old": ["ancient", "former", "previous"],
        "help": ["assist", "support", "aid"],
        "find": ["search", "locate", "discover"],
        "show": ["display", "present", "demonstrate"],
        "create": ["make", "build", "generate"],
        "delete": ["remove", "erase", "clear"],
        "update": ["modify", "change", "edit"],
        "error": ["bug", "issue", "problem", "exception"],
        "function": ["method", "procedure", "routine"],
        "class": ["type", "object", "model"],
        "file": ["document", "record", "data"],
        "user": ["client", "customer", "account"],
        "api": ["interface", "endpoint", "service"],
        "database": ["db", "storage", "repository"],
    }

    def rewrite(self, query: str) -> RewrittenQuery:
        """Expand the query with synonyms."""
        # First normalize
        normalizer = NormalizeRewriter(self.config)
        normalized = normalizer.rewrite(query)

        # Find expansions with global limit
        words = normalized.rewritten_query.lower().split()
        expansions: set[Any] = set()
        max_per_word = max(1, self.config.max_expansions // max(1, len(words)))

        for word in words:
            if word in self.SYNONYM_MAP:
                # Limit per word to ensure fair distribution
                for synonym in self.SYNONYM_MAP[word][:max_per_word]:
                    if len(expansions) >= self.config.max_expansions:
                        break
                    expansions.add(synonym)

        expansions = list(expansions)[: self.config.max_expansions]  # type: ignore[assignment]

        # Build expanded query
        if expansions:
            expanded_query = f"{normalized.rewritten_query} {' '.join(expansions)}"
        else:
            expanded_query = normalized.rewritten_query

        return RewrittenQuery(
            original_query=query,
            rewritten_query=expanded_query,
            strategy=QueryRewriteStrategy.EXPAND,
            expansions=expansions,  # type: ignore[arg-type]
            metadata={"expansion_count": len(expansions)},
        )


class DecomposeRewriter(BaseQueryRewriter):
    """
    Query decomposition into sub-queries.

    Breaks complex queries into simpler sub-queries
    for more targeted retrieval.
    """

    def rewrite(self, query: str) -> RewrittenQuery:
        """Decompose the query into sub-queries."""
        # Normalize first
        normalizer = NormalizeRewriter(self.config)
        normalized = normalizer.rewrite(query)

        sub_queries = []
        query_text = normalized.rewritten_query

        # Strategy 1: Split on conjunctions
        conjunctions = ["and", "or", "but", "also", "as well as"]
        for conj in conjunctions:
            if f" {conj} " in query_text:
                parts = query_text.split(f" {conj} ")
                sub_queries.extend([p.strip() for p in parts if p.strip()])
                break

        # Strategy 2: Split on question words
        if not sub_queries:
            question_patterns = [
                r"(what|how|why|when|where|who)\s+",
                r"\?",
            ]
            for pattern in question_patterns:
                if re.search(pattern, query_text, re.IGNORECASE):
                    # Keep the original as the main query
                    sub_queries = [query_text]
                    break

        # Strategy 3: Extract key phrases
        if not sub_queries:
            # Simple noun phrase extraction (can be enhanced with NLP)
            words = query_text.split()
            if len(words) > 4:
                # Create sub-queries from chunks
                chunk_size = max(2, len(words) // 2)
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i : i + chunk_size])
                    if chunk.strip():
                        sub_queries.append(chunk)

        # Limit sub-queries
        sub_queries = sub_queries[: self.config.max_sub_queries]

        # If no decomposition possible, use original
        if not sub_queries:
            sub_queries = [query_text]

        return RewrittenQuery(
            original_query=query,
            rewritten_query=query_text,
            strategy=QueryRewriteStrategy.DECOMPOSE,
            sub_queries=sub_queries,
            metadata={"sub_query_count": len(sub_queries)},
        )


class HybridRewriter(BaseQueryRewriter):
    """
    Hybrid query generator for sparse+dense retrieval.

    Generates both sparse (keyword-based) and dense
    (semantic) versions of the query.
    """

    def rewrite(self, query: str) -> RewrittenQuery:
        """Generate hybrid query representations."""
        # Normalize for dense
        normalizer = NormalizeRewriter(self.config)
        normalized = normalizer.rewrite(query)

        # For sparse: extract keywords and apply expansion
        expander = ExpansionRewriter(self.config)
        expanded = expander.rewrite(query)

        # Build hybrid representation
        dense_query = normalized.rewritten_query
        sparse_query = expanded.rewritten_query

        return RewrittenQuery(
            original_query=query,
            rewritten_query=dense_query,  # Use dense as primary
            strategy=QueryRewriteStrategy.HYBRID,
            expansions=expanded.expansions,
            metadata={
                "dense_query": dense_query,
                "sparse_query": sparse_query,
                "sparse_weight": self.config.sparse_weight,
                "dense_weight": self.config.dense_weight,
            },
        )


class MultiQueryRewriter(BaseQueryRewriter):
    """
    Multi-query generation for improved recall.

    Generates multiple query variants to capture
    different aspects of the user intent.
    """

    def rewrite(self, query: str) -> RewrittenQuery:
        """Generate multiple query variants."""
        # Start with normalized query
        normalizer = NormalizeRewriter(self.config)
        normalized = normalizer.rewrite(query)

        variants = [normalized.rewritten_query]

        # Variant 1: Expanded query
        if len(variants) < self.config.num_variants:
            expander = ExpansionRewriter(self.config)
            expanded = expander.rewrite(query)
            if expanded.rewritten_query != normalized.rewritten_query:
                variants.append(expanded.rewritten_query)

        # Variant 2: Key terms only
        if len(variants) < self.config.num_variants:
            words = normalized.rewritten_query.split()
            if len(words) > 2:
                # Keep only content words (simple heuristic: longer words)
                key_words = [w for w in words if len(w) > 3]
                if key_words and len(key_words) < len(words):
                    variants.append(" ".join(key_words))

        # Variant 3: First half / second half for long queries
        if len(variants) < self.config.num_variants:
            words = normalized.rewritten_query.split()
            if len(words) > 6:
                half = len(words) // 2
                variants.append(" ".join(words[:half]))

        # Limit variants
        variants = variants[: self.config.num_variants]

        return RewrittenQuery(
            original_query=query,
            rewritten_query=normalized.rewritten_query,
            strategy=QueryRewriteStrategy.MULTI,
            sub_queries=variants,
            metadata={"variant_count": len(variants)},
        )


class QueryRewriter:
    """
    Main query rewriter class that dispatches to appropriate strategy.

    Example:
        config = QueryRewriteConfig(
            strategy=QueryRewriteStrategy.EXPAND,
            max_expansions=5,
        )
        rewriter = QueryRewriter(config)

        rewritten = rewriter.rewrite("find quick function")
        logger.info(rewritten.rewritten_query)
        logger.info(rewritten.expansions)
    """

    STRATEGY_MAP = {
        QueryRewriteStrategy.NORMALIZE: NormalizeRewriter,
        QueryRewriteStrategy.EXPAND: ExpansionRewriter,
        QueryRewriteStrategy.DECOMPOSE: DecomposeRewriter,
        QueryRewriteStrategy.HYBRID: HybridRewriter,
        QueryRewriteStrategy.MULTI: MultiQueryRewriter,
    }

    def __init__(self, config: Optional[QueryRewriteConfig] = None):
        """Initialize query rewriter with configuration."""
        self.config = config or QueryRewriteConfig()

        # Initialize cache
        self._cache: dict[str, RewrittenQuery] = {}

        if self.config.strategy == QueryRewriteStrategy.NONE:
            self._rewriter = None
        else:
            rewriter_class = self.STRATEGY_MAP.get(self.config.strategy, NormalizeRewriter)
            self._rewriter = rewriter_class(self.config)  # type: ignore[abstract]

    def rewrite(self, query: str) -> RewrittenQuery:
        """
        Rewrite the query.

        Args:
            query: Original query string

        Returns:
            RewrittenQuery object with rewritten query and metadata
        """
        if not query or not query.strip():
            return RewrittenQuery(
                original_query=query,
                rewritten_query=query,
                strategy=self.config.strategy,
            )

        # Check cache
        cache_key = hashlib.sha256(query.encode()).hexdigest()[:12]
        if self.config.enable_cache and cache_key in self._cache:
            logger.debug(f"Query cache hit for: {query[:50]}...")
            return self._cache[cache_key]

        # No rewriting
        if self.config.strategy == QueryRewriteStrategy.NONE:
            result = RewrittenQuery(
                original_query=query,
                rewritten_query=query,
                strategy=QueryRewriteStrategy.NONE,
            )
        else:
            result = self._rewriter.rewrite(query)  # type: ignore[union-attr]

        # Update cache
        if self.config.enable_cache:
            if len(self._cache) >= self.config.cache_size:
                # Evict oldest entries (simple FIFO)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[cache_key] = result

        logger.debug(
            f"Query rewritten: '{query[:50]}...' -> '{result.rewritten_query[:50]}...' "
            f"({result.strategy.value})"
        )

        return result

    def rewrite_batch(self, queries: Sequence[str]) -> list[RewrittenQuery]:
        """
        Rewrite multiple queries.

        Args:
            queries: List of query strings

        Returns:
            List of RewrittenQuery objects
        """
        return [self.rewrite(q) for q in queries]

    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._cache.clear()
        logger.debug("Query rewriter cache cleared")

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.config.cache_size,
        }


def rewrite_query(
    query: str,
    strategy: QueryRewriteStrategy = QueryRewriteStrategy.NORMALIZE,
    **kwargs: Any,
) -> RewrittenQuery:
    """
    Convenience function to rewrite a query.

    Args:
        query: Query string
        strategy: Rewrite strategy
        **kwargs: Additional config options

    Returns:
        RewrittenQuery object
    """
    config = QueryRewriteConfig(strategy=strategy, **kwargs)
    rewriter = QueryRewriter(config)
    return rewriter.rewrite(query)
