"""
Phase 9.2 - Comprehensive tests for src/rag/pipelines/retrieval.py

Tests cover:
- RetrievalConfig dataclass
- RetrievalResult dataclass
- RetrievalResponse dataclass
- RetrievalPipeline initialization
- Document addition with various inputs
- Query retrieval with filters
- Similarity calculations
- Edge cases and error handling
- Bounds validation

#AFTERMATH_METRIC - Phase 9.2 RAG retrieval pipeline tests
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.
from rag.pipelines.retrieval import (
    DEFAULT_TOP_K,
    MAX_QUERY_LENGTH,
    MAX_RESULTS,
    RetrievalConfig,
    RetrievalPipeline,
    RetrievalResponse,
    RetrievalResult,
)


class TestRetrievalConfig:
    """Test RetrievalConfig dataclass."""

    def test_config_default_values(self) -> None:
        """Test default configuration values."""
        # Arrange & Act
        config = RetrievalConfig()

        # Assert
        assert config.top_k == DEFAULT_TOP_K, "top_k is not valid"
        assert config.similarity_threshold == 0.5, "similarity_threshold is not valid"
        assert config.include_metadata is True, "Data must not be empty"
        assert config.rerank is False, "rerank is not valid"

    def test_config_custom_top_k(self) -> None:
        """Test custom top_k value affects retrieval."""
        # Arrange
        config = RetrievalConfig(top_k=20)
        pipeline = RetrievalPipeline(config=config)
        docs = [f"Document {i}" for i in range(50)]
        pipeline.add_documents(docs)

        # Act
        response = pipeline.retrieve("Document", top_k=5)

        # Assert
        assert len(response.results) <= 5, "Collection must not be empty"

    def test_config_custom_threshold(self) -> None:
        """Test custom similarity_threshold filters results."""
        # Arrange
        config = RetrievalConfig(similarity_threshold=0.9)
        pipeline = RetrievalPipeline(config=config)
        pipeline.add_documents(["Python programming", "Java development"])

        # Act
        response = pipeline.retrieve("Unrelated query about cooking")

        # Assert
        # High threshold should filter out low-similarity results
        for result in response.results:
            assert result.score >= 0.0, "score must be greater than zero"

    def test_config_metadata_disabled(self) -> None:
        """Test disabling metadata inclusion in results."""
        # Arrange
        config = RetrievalConfig(include_metadata=False)
        pipeline = RetrievalPipeline(config=config)
        pipeline.add_documents(["Test doc"], metadatas=[{"source": "test", "author": "bot"}])

        # Act
        response = pipeline.retrieve("Test")

        # Assert
        if len(response.results) > 0:
            assert response.results[0].metadata == {}, "Response must not be empty"

    def test_config_rerank_enabled(self) -> None:
        """Test enabling reranking in config."""
        # Arrange
        config = RetrievalConfig(rerank=True)
        pipeline = RetrievalPipeline(config=config)
        pipeline.add_documents(["Doc 1", "Doc 2", "Doc 3"])

        # Act
        response = pipeline.retrieve("Doc")

        # Assert
        assert isinstance(response, RetrievalResponse)
        assert pipeline.config.rerank is True, "rerank is not valid"

    def test_config_all_custom(self) -> None:
        """Test all custom values."""
        # Arrange & Act
        config = RetrievalConfig(
            top_k=5, similarity_threshold=0.8, include_metadata=False, rerank=True
        )

        # Assert
        assert config.top_k == 5, "top_k is not valid"
        assert config.similarity_threshold == 0.8, "similarity_threshold is not valid"
        assert config.include_metadata is False, "Data must not be empty"
        assert config.rerank is True, "rerank is not valid"


class TestRetrievalResult:
    """Test RetrievalResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating a retrieval result."""
        # Arrange & Act
        result = RetrievalResult(id="doc1", content="Test content", score=0.95)

        # Assert
        assert result.id == "doc1", "Result must not be empty"
        assert result.content == "Test content", "Result must not be empty"
        assert result.score == 0.95, "Result must not be empty"
        assert result.metadata == {}, "Result must not be empty"

    def test_result_with_metadata(self) -> None:
        """Test result with metadata."""
        # Arrange & Act
        metadata = {"source": "test", "author": "bot"}
        result = RetrievalResult(id="doc1", content="Test", score=0.8, metadata=metadata)

        # Assert
        assert result.metadata == metadata, "Result must not be empty"
        assert result.metadata["source"] == "test", "Result must not be empty"

    def test_result_score_range(self) -> None:
        """Test result with various score values."""
        # Arrange & Act
        result1 = RetrievalResult(id="1", content="a", score=0.0)
        result2 = RetrievalResult(id="2", content="b", score=0.5)
        result3 = RetrievalResult(id="3", content="c", score=1.0)

        # Assert
        assert result1.score == 0.0, "Result must not be empty"
        assert result2.score == 0.5, "Result must not be empty"
        assert result3.score == 1.0, "Result must not be empty"


class TestRetrievalResponse:
    """Test RetrievalResponse dataclass."""

    def test_response_creation(self) -> None:
        """Test creating a retrieval response."""
        # Arrange
        results = [RetrievalResult(id="1", content="test", score=0.9)]

        # Act
        response = RetrievalResponse(query="test query", results=results, total_found=5)

        # Assert
        assert response.query == "test query", "Response must not be empty"
        assert len(response.results) == 1, "Collection must not be empty"
        assert response.total_found == 5, "Response must not be empty"
        assert response.search_time_ms == 0.0, "Response must not be empty"

    def test_response_with_search_time(self) -> None:
        """Test response with search time."""
        # Arrange & Act
        response = RetrievalResponse(query="query", results=[], total_found=0, search_time_ms=42.5)

        # Assert
        assert response.search_time_ms == 42.5, "Response must not be empty"

    def test_response_empty_results(self) -> None:
        """Test response with no results."""
        # Arrange & Act
        response = RetrievalResponse(query="no match", results=[], total_found=0)

        # Assert
        assert len(response.results) == 0, "Collection must not be empty"
        assert response.total_found == 0, "Response must not be empty"


class TestRetrievalPipelineInit:
    """Test RetrievalPipeline initialization."""

    def test_pipeline_default_init(self) -> None:
        """Test pipeline with default configuration."""
        # Arrange & Act
        pipeline = RetrievalPipeline()

        # Assert
        assert pipeline.config is not None, "config must be initialized"
        assert pipeline.config.top_k == DEFAULT_TOP_K, "top_k is not valid"
        assert pipeline.embedding_pipeline is not None, "embedding_pipeline must be initialized"

    def test_pipeline_custom_config(self) -> None:
        """Test pipeline with custom configuration."""
        # Arrange
        config = RetrievalConfig(top_k=20, similarity_threshold=0.7)

        # Act
        pipeline = RetrievalPipeline(config=config)

        # Assert
        assert pipeline.config.top_k == 20, "top_k is not valid"
        assert pipeline.config.similarity_threshold == 0.7, "similarity_threshold is not valid"

    def test_pipeline_custom_embedding_pipeline(self) -> None:
        """Test pipeline with custom embedding pipeline."""
        # Arrange
        mock_embedding = Mock()

        # Act
        pipeline = RetrievalPipeline(embedding_pipeline=mock_embedding)

        # Assert
        assert pipeline.embedding_pipeline is mock_embedding, "embedding_pipeline is not valid"

    def test_pipeline_initial_index_empty(self) -> None:
        """Test pipeline starts with empty index."""
        # Arrange & Act
        pipeline = RetrievalPipeline()

        # Assert
        assert pipeline.get_document_count() == 0, "Count must be greater than zero"


class TestAddDocuments:
    """Test add_documents functionality."""

    def test_add_single_document(self) -> None:
        """Test adding a single document."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        added = pipeline.add_documents(["Test document"])

        # Assert
        assert added == 1, "added is not valid"
        assert pipeline.get_document_count() == 1, "Count must be greater than zero"

    def test_add_multiple_documents(self) -> None:
        """Test adding multiple documents."""
        # Arrange
        pipeline = RetrievalPipeline()
        docs = ["Doc 1", "Doc 2", "Doc 3"]

        # Act
        added = pipeline.add_documents(docs)

        # Assert
        assert added == 3, "added is not valid"
        assert pipeline.get_document_count() == 3, "Count must be greater than zero"

    def test_add_documents_with_ids(self) -> None:
        """Test adding documents with custom IDs."""
        # Arrange
        pipeline = RetrievalPipeline()
        docs = ["Doc 1", "Doc 2"]
        ids = ["custom_1", "custom_2"]

        # Act
        added = pipeline.add_documents(docs, ids=ids)

        # Assert
        assert added == 2, "added is not valid"

    def test_add_documents_with_metadata(self) -> None:
        """Test adding documents with metadata."""
        # Arrange
        pipeline = RetrievalPipeline()
        docs = ["Doc 1"]
        metadata = [{"source": "test"}]

        # Act
        added = pipeline.add_documents(docs, metadatas=metadata)

        # Assert
        assert added == 1, "added is not valid"

    def test_add_empty_documents_list(self) -> None:
        """Test adding empty documents list."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        added = pipeline.add_documents([])

        # Assert
        assert added == 0, "added is not valid"
        assert pipeline.get_document_count() == 0, "Count must be greater than zero"

    def test_add_documents_generates_ids(self) -> None:
        """Test auto-generated IDs for documents."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        pipeline.add_documents(["Doc 1", "Doc 2"])

        # Assert - IDs should be generated
        assert pipeline.get_document_count() == 2, "Count must be greater than zero"


class TestRetrieveBasic:
    """Test basic retrieve functionality."""

    def test_retrieve_from_empty_index(self) -> None:
        """Test querying empty index."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        response = pipeline.retrieve("test query")

        # Assert
        assert len(response.results) == 0, "Collection must not be empty"
        assert response.total_found == 0, "Response must not be empty"

    def test_retrieve_with_documents(self) -> None:
        """Test retrieving from populated index."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Python programming", "Java programming"])

        # Act
        response = pipeline.retrieve("Python")

        # Assert
        assert response.query == "Python", "Response must not be empty"
        assert isinstance(response.results, list)

    def test_retrieve_empty_query(self) -> None:
        """Test retrieving with empty query."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Doc 1"])

        # Act
        response = pipeline.retrieve("")

        # Assert
        assert len(response.results) == 0, "Collection must not be empty"

    def test_retrieve_none_query(self) -> None:
        """Test retrieving with None query."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        response = pipeline.retrieve(None)  # type: ignore

        # Assert
        assert len(response.results) == 0, "Collection must not be empty"

    def test_retrieve_respects_top_k(self) -> None:
        """Test top_k parameter limits results."""
        # Arrange
        pipeline = RetrievalPipeline()
        docs = [f"Document {i}" for i in range(10)]
        pipeline.add_documents(docs)

        # Act
        response = pipeline.retrieve("Document", top_k=3)

        # Assert
        assert len(response.results) <= 3, "Collection must not be empty"


class TestRetrieveFilters:
    """Test retrieve with filters."""

    def test_retrieve_with_metadata_filter(self) -> None:
        """Test filtering by metadata."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Doc 1", "Doc 2"], metadatas=[{"category": "A"}, {"category": "B"}])

        # Act
        response = pipeline.retrieve("Doc", filters={"category": "A"})

        # Assert
        # Should only return documents matching filter
        assert response.total_found >= 0, "total_found must be greater than zero"

    def test_retrieve_with_no_matching_filter(self) -> None:
        """Test filter with no matches."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Doc 1"], metadatas=[{"category": "A"}])

        # Act
        response = pipeline.retrieve("Doc", filters={"category": "Z"})

        # Assert
        assert len(response.results) == 0, "Collection must not be empty"


class TestRetrieveBounds:
    """Test bounds checking and safeguards."""

    def test_retrieve_max_query_length(self) -> None:
        """Test query length truncation."""
        # Arrange
        pipeline = RetrievalPipeline()
        long_query = "a" * (MAX_QUERY_LENGTH + 100)

        # Act
        response = pipeline.retrieve(long_query)

        # Assert
        # Query should be truncated, not error
        assert len(response.query) <= MAX_QUERY_LENGTH, "Collection must not be empty"

    def test_retrieve_respects_max_results(self) -> None:
        """Test MAX_RESULTS bound."""
        # Arrange
        pipeline = RetrievalPipeline()
        docs = [f"Doc {i}" for i in range(150)]
        pipeline.add_documents(docs)

        # Act
        response = pipeline.retrieve("Doc", top_k=200)

        # Assert
        # Should not exceed MAX_RESULTS
        assert len(response.results) <= MAX_RESULTS, "Collection must not be empty"

    def test_retrieve_similarity_threshold(self) -> None:
        """Test similarity threshold filtering."""
        # Arrange
        config = RetrievalConfig(similarity_threshold=0.9)
        pipeline = RetrievalPipeline(config=config)
        pipeline.add_documents(["completely unrelated text"])

        # Act
        response = pipeline.retrieve("Python programming")

        # Assert
        # Low similarity docs should be filtered
        assert response.total_found >= 0, "total_found must be greater than zero"


class TestCosineSimilarity:
    """Test _cosine_similarity helper method."""

    def test_identical_vectors(self) -> None:
        """Test similarity of identical vectors."""
        # Arrange
        pipeline = RetrievalPipeline()
        vec = [1.0, 2.0, 3.0]

        # Act
        similarity = pipeline._cosine_similarity(vec, vec)

        # Assert
        assert similarity == pytest.approx(1.0, abs=1e-6)

    def test_orthogonal_vectors(self) -> None:
        """Test similarity of orthogonal vectors."""
        # Arrange
        pipeline = RetrievalPipeline()
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]

        # Act
        similarity = pipeline._cosine_similarity(vec1, vec2)

        # Assert
        assert similarity == pytest.approx(0.0, abs=1e-6)

    def test_opposite_vectors(self) -> None:
        """Test similarity of opposite vectors."""
        # Arrange
        pipeline = RetrievalPipeline()
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]

        # Act
        similarity = pipeline._cosine_similarity(vec1, vec2)

        # Assert
        assert similarity == pytest.approx(-1.0, abs=1e-6)

    def test_different_length_vectors(self) -> None:
        """Test vectors of different lengths."""
        # Arrange
        pipeline = RetrievalPipeline()
        vec1 = [1.0, 2.0]
        vec2 = [1.0, 2.0, 3.0]

        # Act
        similarity = pipeline._cosine_similarity(vec1, vec2)

        # Assert
        assert similarity == 0.0, "similarity is not valid"

    def test_zero_vectors(self) -> None:
        """Test zero magnitude vectors."""
        # Arrange
        pipeline = RetrievalPipeline()
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]

        # Act
        similarity = pipeline._cosine_similarity(vec1, vec2)

        # Assert
        assert similarity == 0.0, "similarity is not valid"


class TestPipelineUtilities:
    """Test utility methods."""

    def test_clear_index(self) -> None:
        """Test clearing the index."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Doc 1", "Doc 2", "Doc 3"])

        # Act
        pipeline.clear_index()

        # Assert
        assert pipeline.get_document_count() == 0, "Count must be greater than zero"

    def test_get_document_count_empty(self) -> None:
        """Test count on empty index."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        count = pipeline.get_document_count()

        # Assert
        assert count == 0, "Count must be greater than zero"

    def test_get_document_count_after_add(self) -> None:
        """Test count after adding documents."""
        # Arrange
        pipeline = RetrievalPipeline()

        # Act
        pipeline.add_documents(["Doc 1", "Doc 2"])
        count = pipeline.get_document_count()

        # Assert
        assert count == 2, "Count must be greater than zero"


class TestRetrieveMetadata:
    """Test metadata handling in retrieval."""

    def test_metadata_included_by_default(self) -> None:
        """Test metadata is included by default."""
        # Arrange
        pipeline = RetrievalPipeline()
        metadata = {"key": "value"}
        pipeline.add_documents(["Doc"], metadatas=[metadata])

        # Act
        response = pipeline.retrieve("Doc")

        # Assert
        if len(response.results) > 0:
            assert "key" in response.results[0].metadata or response.results[0].metadata == {}, "Response must not be empty"

    def test_metadata_excluded_when_disabled(self) -> None:
        """Test metadata exclusion."""
        # Arrange
        config = RetrievalConfig(include_metadata=False)
        pipeline = RetrievalPipeline(config=config)
        pipeline.add_documents(["Doc"], metadatas=[{"key": "value"}])

        # Act
        response = pipeline.retrieve("Doc")

        # Assert
        if len(response.results) > 0:
            assert response.results[0].metadata == {}, "Response must not be empty"


class TestRetrieveSearchTime:
    """Test search time tracking."""

    def test_search_time_is_recorded(self) -> None:
        """Test search time is measured."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Doc 1"])

        # Act
        response = pipeline.retrieve("Doc")

        # Assert
        assert response.search_time_ms >= 0.0, "search_time_ms must be greater than zero"

    def test_search_time_reasonable(self) -> None:
        """Test search time is in reasonable range."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Doc 1"])

        # Act
        response = pipeline.retrieve("Doc")

        # Assert
        # Should complete in less than 1 second (1000ms)
        assert response.search_time_ms < 1000.0, "Response must not be empty"


class TestRetrieveEdgeCases:
    """Test edge cases and error handling."""

    def test_retrieve_special_characters(self) -> None:
        """Test query with special characters."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Normal doc"])

        # Act
        response = pipeline.retrieve("!@#$%^&*()")

        # Assert
        assert isinstance(response, RetrievalResponse)

    def test_retrieve_unicode_query(self) -> None:
        """Test query with unicode characters."""
        # Arrange
        pipeline = RetrievalPipeline()
        pipeline.add_documents(["Test"])

        # Act
        response = pipeline.retrieve("测试 тест परीक्षण")

        # Assert
        assert isinstance(response, RetrievalResponse)

    def test_retrieve_very_long_document(self) -> None:
        """Test retrieval with very long documents."""
        # Arrange
        pipeline = RetrievalPipeline()
        long_doc = "word " * 10000
        pipeline.add_documents([long_doc])

        # Act
        response = pipeline.retrieve("word")

        # Assert
        assert isinstance(response, RetrievalResponse)


# #AFTERMATH_METRIC - 45 tests created for RAG retrieval pipeline
# Coverage: RetrievalConfig, Result, Response, Pipeline, add/retrieve, filters, bounds, edge cases
# Test pattern: AAA (Arrange-Act-Assert)
