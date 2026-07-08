"""
Tests for Query Rewriter Module.
"""

import pytest

pytest.importorskip("numpy")

from codex.retrieval.query_rewriter import (
    DecomposeRewriter,
    ExpansionRewriter,
    HybridRewriter,
    MultiQueryRewriter,
    NormalizeRewriter,
    QueryRewriteConfig,
    QueryRewriter,
    QueryRewriteStrategy,
    RewrittenQuery,
    rewrite_query,
)


class TestRewrittenQuery:
    """Tests for RewrittenQuery dataclass."""

    def test_creation(self):
        """Test creating a rewritten query."""
        query = RewrittenQuery(
            original_query="test query",
            rewritten_query="test query normalized",
            strategy=QueryRewriteStrategy.NORMALIZE,
        )

        assert query.original_query == "test query", "original_query is not valid"
        assert query.rewritten_query == "test query normalized", "rewritten_query is not valid"
        assert query.strategy == QueryRewriteStrategy.NORMALIZE, "strategy is not valid"

    def test_query_hash(self):
        """Test query hash generation."""
        query = RewrittenQuery(
            original_query="test",
            rewritten_query="test",
            strategy=QueryRewriteStrategy.NONE,
        )

        assert len(query.query_hash) == 12, "Collection must not be empty"

    def test_to_dict(self):
        """Test converting to dictionary."""
        query = RewrittenQuery(
            original_query="test",
            rewritten_query="test normalized",
            strategy=QueryRewriteStrategy.NORMALIZE,
            expansions=["synonym1"],
        )

        d = query.to_dict()
        assert d["original_query"] == "test", "Condition must be true"
        assert d["strategy"] == "normalize", "Condition must be true"
        assert "synonym1" in d["expansions"], "Condition must be true"


class TestQueryRewriteConfig:
    """Tests for QueryRewriteConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = QueryRewriteConfig()

        assert config.strategy == QueryRewriteStrategy.NORMALIZE, "strategy is not valid"
        assert config.lowercase is True, "lowercase is not valid"
        assert config.remove_punctuation is True, "remove_punctuation is not valid"

    def test_custom_config(self):
        """Test custom configuration."""
        config = QueryRewriteConfig(
            strategy=QueryRewriteStrategy.EXPAND,
            max_expansions=10,
            lowercase=False,
        )

        assert config.strategy == QueryRewriteStrategy.EXPAND, "strategy is not valid"
        assert config.max_expansions == 10, "max_expansions is not valid"
        assert config.lowercase is False, "lowercase is not valid"


class TestNormalizeRewriter:
    """Tests for NormalizeRewriter."""

    @pytest.fixture
    def rewriter(self):
        config = QueryRewriteConfig(strategy=QueryRewriteStrategy.NORMALIZE)
        return NormalizeRewriter(config)

    def test_lowercase(self, rewriter):
        """Test lowercase conversion."""
        result = rewriter.rewrite("Hello World")
        assert result.rewritten_query == "hello world", "Result must not be empty"

    def test_remove_punctuation(self, rewriter):
        """Test punctuation removal."""
        result = rewriter.rewrite("hello, world!")
        assert "," not in result.rewritten_query
        assert "!" not in result.rewritten_query, "Result must not be empty"

    def test_normalize_whitespace(self, rewriter):
        """Test whitespace normalization."""
        result = rewriter.rewrite("hello    world")
        assert result.rewritten_query == "hello world", "Result must not be empty"

    def test_remove_stopwords(self):
        """Test stopword removal when enabled."""
        config = QueryRewriteConfig(remove_stopwords=True)
        rewriter = NormalizeRewriter(config)

        result = rewriter.rewrite("the quick brown fox")
        assert "the" not in result.rewritten_query, "Result must not be empty"


class TestExpansionRewriter:
    """Tests for ExpansionRewriter."""

    @pytest.fixture
    def rewriter(self):
        config = QueryRewriteConfig(
            strategy=QueryRewriteStrategy.EXPAND,
            max_expansions=3,
        )
        return ExpansionRewriter(config)

    def test_expand_with_synonyms(self, rewriter):
        """Test expansion with synonyms."""
        result = rewriter.rewrite("quick function")

        # "quick" should expand to synonyms like "fast", "rapid", "speedy"
        # "function" should expand to "method", "procedure", "routine"
        assert len(result.expansions) > 0, "Collection must not be empty"
        # Check for any known synonyms
        known_synonyms = {"fast", "rapid", "speedy", "method", "procedure", "routine"}
        assert any(exp in known_synonyms for exp in result.expansions), "Result must not be empty"

    def test_no_expansion_for_unknown_words(self, rewriter):
        """Test that unknown words don't expand."""
        result = rewriter.rewrite("xyzabc123")

        # No synonyms for made-up word
        assert len(result.expansions) == 0, "Collection must not be empty"

    def test_expansion_limit(self):
        """Test that expansions are limited."""
        config = QueryRewriteConfig(max_expansions=2)
        rewriter = ExpansionRewriter(config)

        result = rewriter.rewrite("quick big good")

        # Should be limited to max_expansions
        assert len(result.expansions) <= 2, "Collection must not be empty"


class TestDecomposeRewriter:
    """Tests for DecomposeRewriter."""

    @pytest.fixture
    def rewriter(self):
        config = QueryRewriteConfig(
            strategy=QueryRewriteStrategy.DECOMPOSE,
            max_sub_queries=3,
        )
        return DecomposeRewriter(config)

    def test_decompose_conjunction(self, rewriter):
        """Test decomposition on conjunctions."""
        result = rewriter.rewrite("python and javascript")

        assert len(result.sub_queries) >= 1, "Collection must not be empty"

    def test_decompose_long_query(self, rewriter):
        """Test decomposition of long query."""
        result = rewriter.rewrite("how to implement a function in python that does sorting")

        assert len(result.sub_queries) >= 1, "Collection must not be empty"

    def test_simple_query_not_decomposed(self, rewriter):
        """Test that simple queries have minimal decomposition."""
        result = rewriter.rewrite("python")

        assert len(result.sub_queries) >= 1, "Collection must not be empty"
        assert "python" in result.sub_queries[0], "Result must not be empty"


class TestHybridRewriter:
    """Tests for HybridRewriter."""

    @pytest.fixture
    def rewriter(self):
        config = QueryRewriteConfig(strategy=QueryRewriteStrategy.HYBRID)
        return HybridRewriter(config)

    def test_hybrid_generates_both(self, rewriter):
        """Test that hybrid generates both dense and sparse queries."""
        result = rewriter.rewrite("quick function")

        assert "dense_query" in result.metadata, "Result must not be empty"
        assert "sparse_query" in result.metadata, "Result must not be empty"

    def test_hybrid_weights(self, rewriter):
        """Test that weights are included."""
        result = rewriter.rewrite("test query")

        assert "sparse_weight" in result.metadata, "Result must not be empty"
        assert "dense_weight" in result.metadata, "Result must not be empty"


class TestMultiQueryRewriter:
    """Tests for MultiQueryRewriter."""

    @pytest.fixture
    def rewriter(self):
        config = QueryRewriteConfig(
            strategy=QueryRewriteStrategy.MULTI,
            num_variants=3,
        )
        return MultiQueryRewriter(config)

    def test_generates_variants(self, rewriter):
        """Test that multiple variants are generated."""
        result = rewriter.rewrite("find the quick brown fox function")

        # Should have sub_queries with variants
        assert len(result.sub_queries) >= 1, "Collection must not be empty"

    def test_variant_limit(self):
        """Test that variants are limited."""
        config = QueryRewriteConfig(num_variants=2)
        rewriter = MultiQueryRewriter(config)

        result = rewriter.rewrite("a very long query with many words")

        assert len(result.sub_queries) <= 2, "Collection must not be empty"


class TestQueryRewriter:
    """Tests for main QueryRewriter class."""

    def test_none_strategy(self):
        """Test NONE strategy returns original."""
        config = QueryRewriteConfig(strategy=QueryRewriteStrategy.NONE)
        rewriter = QueryRewriter(config)

        result = rewriter.rewrite("Test Query!")

        assert result.original_query == "Test Query!", "Result must not be empty"
        assert result.rewritten_query == "Test Query!", "Result must not be empty"

    def test_normalize_strategy(self):
        """Test NORMALIZE strategy."""
        config = QueryRewriteConfig(strategy=QueryRewriteStrategy.NORMALIZE)
        rewriter = QueryRewriter(config)

        result = rewriter.rewrite("Test Query!")

        assert result.rewritten_query == "test query", "Result must not be empty"

    def test_expand_strategy(self):
        """Test EXPAND strategy."""
        config = QueryRewriteConfig(strategy=QueryRewriteStrategy.EXPAND)
        rewriter = QueryRewriter(config)

        result = rewriter.rewrite("quick search")

        assert result.strategy == QueryRewriteStrategy.EXPAND, "Result must not be empty"

    def test_caching(self):
        """Test that results are cached."""
        config = QueryRewriteConfig(enable_cache=True)
        rewriter = QueryRewriter(config)

        result1 = rewriter.rewrite("test query")
        result2 = rewriter.rewrite("test query")

        # Both should return same result (cached)
        assert result1.rewritten_query == result2.rewritten_query, "Result must not be empty"

    def test_cache_stats(self):
        """Test cache statistics."""
        config = QueryRewriteConfig(enable_cache=True)
        rewriter = QueryRewriter(config)

        rewriter.rewrite("query1")
        rewriter.rewrite("query2")

        stats = rewriter.get_cache_stats()
        assert stats["size"] == 2, "Condition must be true"

    def test_clear_cache(self):
        """Test clearing cache."""
        config = QueryRewriteConfig(enable_cache=True)
        rewriter = QueryRewriter(config)

        rewriter.rewrite("query1")
        assert rewriter.get_cache_stats()["size"] == 1, "Condition must be true"

        rewriter.clear_cache()
        assert rewriter.get_cache_stats()["size"] == 0, "Condition must be true"

    def test_batch_rewrite(self):
        """Test batch rewriting."""
        rewriter = QueryRewriter()

        queries = ["query one", "query two", "query three"]
        results = rewriter.rewrite_batch(queries)

        assert len(results) == 3, "Results must not be empty"
        assert all(isinstance(r, RewrittenQuery) for r in results)

    def test_empty_query(self):
        """Test with empty query."""
        rewriter = QueryRewriter()

        result = rewriter.rewrite("")
        assert result.rewritten_query == "", "Result must not be empty"

        result = rewriter.rewrite("   ")
        assert result.rewritten_query == "   ", "Result must not be empty"


class TestRewriteQueryFunction:
    """Tests for rewrite_query convenience function."""

    def test_basic_rewrite(self):
        """Test basic rewrite function."""
        result = rewrite_query("Test Query")

        assert isinstance(result, RewrittenQuery)
        assert result.rewritten_query == "test query", "Result must not be empty"

    def test_with_custom_strategy(self):
        """Test with custom strategy."""
        result = rewrite_query(
            "quick test",
            strategy=QueryRewriteStrategy.EXPAND,
        )

        assert result.strategy == QueryRewriteStrategy.EXPAND, "Result must not be empty"
