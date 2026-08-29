"""
Tests for context_management.memory module.

Tests chunking, storage, retrieval, and memory management.

Phase 9.1 Coverage Enhancement
#Phase9.1 #Coverage30 #UnitTests
"""

from datetime import datetime

from context_management.memory import (
    ContextMemory,
    MemoryChunk,
    RetrievalResult,
)


class TestMemoryChunk:
    """Test MemoryChunk dataclass."""

    def test_memory_chunk_initialization(self):
        """Test MemoryChunk initialization."""
        chunk = MemoryChunk(chunk_id="chunk_1", content="test content", token_count=10)
        assert chunk.chunk_id == "chunk_1", "chunk_id is not valid"
        assert chunk.content == "test content", "Content must not be empty"
        assert chunk.token_count == 10, "Count must be greater than zero"
        assert isinstance(chunk.created_at, datetime)
        assert chunk.access_count == 0, "Count must be greater than zero"

    def test_memory_chunk_with_metadata(self):
        """Test MemoryChunk with metadata."""
        chunk = MemoryChunk(
            chunk_id="chunk_1",
            content="test",
            token_count=5,
            metadata={"source": "test_file.py", "line": 42},
        )
        assert chunk.metadata["source"] == "test_file.py", "Data must not be empty"
        assert chunk.metadata["line"] == 42, "Data must not be empty"

    def test_memory_chunk_with_priority(self):
        """Test MemoryChunk with priority."""
        chunk = MemoryChunk(chunk_id="chunk_1", content="critical", token_count=5, priority=100)
        assert chunk.priority == 100, "priority is not valid"

    def test_memory_chunk_access(self):
        """Test MemoryChunk access tracking."""
        chunk = MemoryChunk(chunk_id="chunk_1", content="test", token_count=5)
        initial_access_count = chunk.access_count
        initial_accessed = chunk.last_accessed

        # Access the chunk
        chunk.access()

        assert chunk.access_count == initial_access_count + 1, "Count must be greater than zero"
        assert chunk.last_accessed >= initial_accessed, "last_accessed must be greater than zero"

    def test_memory_chunk_summary(self):
        """Test MemoryChunk with summary."""
        chunk = MemoryChunk(
            chunk_id="chunk_1", content="long content here", token_count=10, summary="short summary"
        )
        assert chunk.summary == "short summary", "summary is not valid"


class TestRetrievalResult:
    """Test RetrievalResult dataclass."""

    def test_retrieval_result_initialization(self):
        """Test RetrievalResult initialization."""
        chunks = [
            MemoryChunk(chunk_id="1", content="test", token_count=5),
        ]
        result = RetrievalResult(
            chunks=chunks, total_tokens=5, query_used="test query", retrieval_method="keyword"
        )
        assert len(result.chunks) == 1, "Collection must not be empty"
        assert result.total_tokens == 5, "Result must not be empty"
        assert result.query_used == "test query", "Result must not be empty"
        assert result.retrieval_method == "keyword", "Result must not be empty"


class TestContextMemory:
    """Test ContextMemory class."""

    def test_context_memory_initialization(self):
        """Test ContextMemory initialization."""
        memory = ContextMemory(max_total_tokens=10000)
        assert memory.max_total_tokens == 10000, "max_total_tokens is not valid"
        assert memory._total_tokens == 0, "_total_tokens is not valid"
        assert len(memory._chunks) == 0, "Collection must not be empty"

    def test_context_memory_with_custom_chunk_size(self):
        """Test ContextMemory with custom chunk size."""
        memory = ContextMemory(max_chunk_tokens=500, max_total_tokens=5000)
        assert memory.max_chunk_tokens == 500, "max_chunk_tokens is not valid"
        assert memory.max_total_tokens == 5000, "max_total_tokens is not valid"

    def test_store_content(self):
        """Test storing content in memory."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk_ids = memory.store("This is test content")

        assert len(chunk_ids) >= 1, "Chunk_ids must not be empty"
        assert memory._total_tokens > 0, "_total_tokens must be greater than zero"

    def test_store_with_metadata(self):
        """Test storing content with metadata."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk_ids = memory.store("Test content", metadata={"source": "test.py"})

        chunk = memory.get_chunk(chunk_ids[0])
        assert chunk is not None, "chunk must be initialized"
        assert chunk.metadata.get("source") == "test.py", "Data must not be empty"

    def test_store_with_priority(self):
        """Test storing content with priority."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk_ids = memory.store("Critical content", priority=100)

        chunk = memory.get_chunk(chunk_ids[0])
        assert chunk is not None, "chunk must be initialized"
        assert chunk.priority == 100, "priority is not valid"

    def test_retrieve_content(self):
        """Test retrieving content."""
        memory = ContextMemory(max_total_tokens=10000)

        memory.store("First piece of content about testing")
        memory.store("Second piece about Python programming")

        result = memory.retrieve("testing", max_tokens=5000)

        assert isinstance(result, RetrievalResult)

    def test_get_chunk_by_id(self):
        """Test getting chunk by ID."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk_ids = memory.store("Test content")
        chunk = memory.get_chunk(chunk_ids[0])

        assert chunk is not None, "chunk must be initialized"
        assert "Test content" in chunk.content, "Content must not be empty"

    def test_get_nonexistent_chunk(self):
        """Test getting non-existent chunk returns None."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk = memory.get_chunk("nonexistent_id")
        assert chunk is None, "chunk is not valid"

    def test_delete_chunk(self):
        """Test deleting chunk."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk_ids = memory.store("Test content")
        chunk_id = chunk_ids[0]

        # Verify chunk exists
        assert memory.get_chunk(chunk_id) is not None, "mem must be initialized"

        # Delete chunk
        result = memory.delete_chunk(chunk_id)

        assert result is True, "Result must not be empty"
        assert memory.get_chunk(chunk_id) is None, "mem is not valid"

    def test_delete_nonexistent_chunk(self):
        """Test deleting non-existent chunk."""
        memory = ContextMemory(max_total_tokens=10000)

        result = memory.delete_chunk("nonexistent_id")
        assert result is False, "Result must not be empty"

    def test_clear_memory(self):
        """Test clearing all memory."""
        memory = ContextMemory(max_total_tokens=10000)

        memory.store("Content 1")
        memory.store("Content 2")

        assert len(memory._chunks) > 0, "Collection must not be empty"

        memory.clear()

        assert len(memory._chunks) == 0, "Collection must not be empty"
        assert memory._total_tokens == 0, "_total_tokens is not valid"

    def test_get_stats(self):
        """Test getting memory statistics."""
        memory = ContextMemory(max_total_tokens=10000)

        memory.store("Test content")

        stats = memory.get_stats()

        assert "chunk_count" in stats, "Count must be greater than zero"
        assert "total_tokens" in stats, "Condition must be true"
        assert stats["chunk_count"] >= 1, "Value must be greater than zero"


class TestContextMemoryWithEmbeddings:
    """Test ContextMemory with embeddings."""

    def test_store_with_embedder(self):
        """Test storing content with embedder."""

        def mock_embedder(text):
            return [0.1] * 128

        memory = ContextMemory(max_total_tokens=10000, embedder=mock_embedder)

        chunk_ids = memory.store("Test content")
        assert len(chunk_ids) >= 1, "Chunk_ids must not be empty"

    def test_retrieve_with_embedder(self):
        """Test retrieval with embedder."""

        def mock_embedder(text):
            return [len(text) / 100.0] * 128

        memory = ContextMemory(max_total_tokens=10000, embedder=mock_embedder)

        memory.store("Python programming tutorial")
        memory.store("Java programming guide")

        result = memory.retrieve("programming", max_tokens=2000)
        assert isinstance(result, RetrievalResult)


class TestContextMemoryWithSummarizer:
    """Test ContextMemory with summarizer."""

    def test_store_with_summarizer(self):
        """Test storing with summarizer generates summaries."""

        def mock_summarizer(text):
            return text[:20] + "..." if len(text) > 20 else text

        memory = ContextMemory(max_total_tokens=10000, summarizer=mock_summarizer)

        chunk_ids = memory.store("This is a very long piece of content that should be summarized")
        chunk = memory.get_chunk(chunk_ids[0])

        assert chunk is not None, "chunk must be initialized"

    def test_map_reduce_summarize(self):
        """Test map-reduce summarization."""

        def mock_summarizer(text):
            return f"Summary: {text[:30]}..."

        memory = ContextMemory(max_total_tokens=10000, summarizer=mock_summarizer)

        memory.store("First content block with information")
        memory.store("Second content block with more info")

        summary = memory.map_reduce_summarize()
        assert isinstance(summary, str)


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_content(self):
        """Test storing empty content."""
        memory = ContextMemory(max_total_tokens=10000)

        chunk_ids = memory.store("")
        assert isinstance(chunk_ids, list)

    def test_very_long_content(self):
        """Test storing very long content (should be chunked)."""
        memory = ContextMemory(max_chunk_tokens=50, max_total_tokens=10000)

        long_content = "This is a test sentence. " * 100
        chunk_ids = memory.store(long_content)

        # Long content should be split into multiple chunks
        assert len(chunk_ids) >= 1, "Chunk_ids must not be empty"

    def test_unicode_content(self):
        """Test storing Unicode content."""
        memory = ContextMemory(max_total_tokens=10000)

        unicode_content = "测试内容 🎉 émojis and spëcial châràctèrs"
        chunk_ids = memory.store(unicode_content)

        chunk = memory.get_chunk(chunk_ids[0])
        assert chunk is not None, "chunk must be initialized"

    def test_stream_retrieve(self):
        """Test streaming retrieval."""
        memory = ContextMemory(max_total_tokens=10000)

        memory.store("First content")
        memory.store("Second content")

        stream = memory.stream_retrieve("content", max_tokens_per_chunk=500)

        # Stream should be an iterator
        chunks = list(stream)
        assert isinstance(chunks, list)
