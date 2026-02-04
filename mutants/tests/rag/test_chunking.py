"""Tests for RAG pipeline components."""

from __future__ import annotations

import pytest


class TestChunkingPipeline:
    """Test suite for the ChunkingPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create a chunking pipeline for testing."""
        from src.rag.pipelines.chunking import ChunkingPipeline, ChunkingConfig

        config = ChunkingConfig(
            chunk_size=100,
            chunk_overlap=20,
        )
        return ChunkingPipeline(config)

    def test_chunk_empty_text(self, pipeline):
        """Test handling of empty text."""
        chunks = pipeline.chunk_text("")
        assert chunks == []

    def test_chunk_none_text(self, pipeline):
        """Test handling of None text."""
        chunks = pipeline.chunk_text(None)
        assert chunks == []

    def test_chunk_small_text(self, pipeline):
        """Test chunking text smaller than chunk size."""
        text = "Hello world"
        chunks = pipeline.chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0].content == text

    def test_chunk_with_metadata(self, pipeline):
        """Test that metadata is preserved in chunks."""
        text = "Test text for chunking"
        metadata = {"source": "test", "type": "example"}

        chunks = pipeline.chunk_text(text, metadata=metadata)

        assert len(chunks) >= 1
        assert chunks[0].metadata["source"] == "test"
        assert chunks[0].metadata["type"] == "example"

    def test_chunk_large_text(self, pipeline):
        """Test chunking text larger than chunk size."""
        text = "A" * 500  # 500 characters

        chunks = pipeline.chunk_text(text)

        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.length > 0

    def test_chunk_indices_are_valid(self, pipeline):
        """Test that chunk indices are valid."""
        text = "Hello world. This is a test. Another sentence here."

        chunks = pipeline.chunk_text(text)

        for chunk in chunks:
            assert chunk.start_index >= 0
            assert chunk.end_index <= len(text)
            assert chunk.start_index < chunk.end_index


class TestChunk:
    """Test the Chunk dataclass."""

    def test_chunk_length_property(self):
        """Test the length property."""
        from src.rag.pipelines.chunking import Chunk

        chunk = Chunk(
            content="Hello world",
            start_index=0,
            end_index=11,
        )

        assert chunk.length == 11

    def test_chunk_metadata_default(self):
        """Test default metadata is empty dict."""
        from src.rag.pipelines.chunking import Chunk

        chunk = Chunk(content="Test", start_index=0, end_index=4)

        assert chunk.metadata == {}
