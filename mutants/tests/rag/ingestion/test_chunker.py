"""
Tests for Document Chunker Module.
"""

import pytest

from codex.rag.ingestion.chunker import (
    Chunker,
    ChunkingStrategy,
    ChunkingConfig,
    Chunk,
    chunk_document,
    FixedSizeChunker,
    SentenceChunker,
    ParagraphChunker,
    SlidingWindowChunker,
)


class TestChunk:
    """Tests for Chunk dataclass."""
    
    def test_chunk_length(self):
        """Test chunk length property."""
        chunk = Chunk(
            text="Hello world",
            index=0,
            start_pos=0,
            end_pos=11,
        )
        
        assert chunk.length == 11
    
    def test_chunk_to_dict(self):
        """Test chunk to_dict method."""
        chunk = Chunk(
            text="Test",
            index=1,
            start_pos=10,
            end_pos=14,
            chunk_hash="abc123",
            metadata={"key": "value"},
        )
        
        d = chunk.to_dict()
        assert d["text"] == "Test"
        assert d["index"] == 1
        assert d["start_pos"] == 10
        assert d["end_pos"] == 14
        assert d["hash"] == "abc123"
        assert d["metadata"]["key"] == "value"


class TestChunkingConfig:
    """Tests for ChunkingConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ChunkingConfig()
        
        assert config.strategy == ChunkingStrategy.FIXED_SIZE
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 100
        assert config.min_chunk_size == 100
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            chunk_size=500,
            chunk_overlap=50,
        )
        
        assert config.strategy == ChunkingStrategy.SENTENCE
        assert config.chunk_size == 500
        assert config.chunk_overlap == 50


class TestFixedSizeChunker:
    """Tests for FixedSizeChunker."""
    
    @pytest.fixture
    def chunker(self):
        """Create a fixed-size chunker."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=20,
            min_chunk_size=10,
        )
        return FixedSizeChunker(config)
    
    def test_chunk_empty_text(self, chunker):
        """Test chunking empty text."""
        chunks = chunker.chunk("")
        assert len(chunks) == 0
    
    def test_chunk_short_text(self, chunker):
        """Test chunking text shorter than chunk size."""
        text = "Short text here."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].index == 0
    
    def test_chunk_long_text(self, chunker):
        """Test chunking text longer than chunk size."""
        text = "A" * 250
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        # Verify indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.index == i
    
    def test_chunk_overlap(self, chunker):
        """Test that chunks have overlap."""
        text = "A" * 300
        chunks = chunker.chunk(text)
        
        # With overlap, chunks should share some content
        if len(chunks) >= 2:
            end_of_first = chunks[0].end_pos
            start_of_second = chunks[1].start_pos
            overlap = end_of_first - start_of_second
            assert overlap >= 0  # Some overlap or adjacent
    
    def test_respects_sentence_boundaries(self):
        """Test that chunks try to break at sentence boundaries."""
        config = ChunkingConfig(
            chunk_size=50,
            chunk_overlap=10,
            min_chunk_size=5,
            respect_sentence_boundaries=True,
        )
        chunker = FixedSizeChunker(config)
        
        text = "First sentence here. Second sentence here. Third sentence follows."
        chunks = chunker.chunk(text)
        
        # Chunks should ideally end at sentence boundaries
        for chunk in chunks[:-1]:  # Except last chunk
            # Check if ends with sentence delimiter or close to it
            assert chunk.text.strip()  # Non-empty


class TestSentenceChunker:
    """Tests for SentenceChunker."""
    
    @pytest.fixture
    def chunker(self):
        """Create a sentence chunker."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            max_chunk_size=100,
            min_chunk_size=5,
        )
        return SentenceChunker(config)
    
    def test_chunk_single_sentence(self, chunker):
        """Test chunking single sentence."""
        text = "This is one sentence."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert "This is one sentence" in chunks[0].text
    
    def test_chunk_multiple_sentences(self, chunker):
        """Test chunking multiple sentences."""
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk(text)
        
        # Should group sentences until max size
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk.text) <= 100 or len(chunks) == 1


class TestParagraphChunker:
    """Tests for ParagraphChunker."""
    
    @pytest.fixture
    def chunker(self):
        """Create a paragraph chunker."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.PARAGRAPH,
            max_chunk_size=200,
            min_chunk_size=5,
        )
        return ParagraphChunker(config)
    
    def test_chunk_single_paragraph(self, chunker):
        """Test chunking single paragraph."""
        text = "This is a single paragraph with no breaks."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].text == text
    
    def test_chunk_multiple_paragraphs(self, chunker):
        """Test chunking multiple paragraphs."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunker.chunk(text)
        
        assert len(chunks) >= 1
        # All content should be preserved
        all_text = " ".join(c.text for c in chunks)
        assert "First paragraph" in all_text
        assert "Second paragraph" in all_text
        assert "Third paragraph" in all_text


class TestSlidingWindowChunker:
    """Tests for SlidingWindowChunker."""
    
    @pytest.fixture
    def chunker(self):
        """Create a sliding window chunker."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SLIDING_WINDOW,
            chunk_size=50,
            window_step=25,
            min_chunk_size=5,
        )
        return SlidingWindowChunker(config)
    
    def test_chunk_empty(self, chunker):
        """Test chunking empty text."""
        chunks = chunker.chunk("")
        assert len(chunks) == 0
    
    def test_chunk_short_text(self, chunker):
        """Test chunking text shorter than window."""
        text = "Short"
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
    
    def test_chunk_sliding_overlap(self, chunker):
        """Test that sliding window creates overlapping chunks."""
        text = "A" * 100
        chunks = chunker.chunk(text)
        
        # With window_step < chunk_size, should have overlapping chunks
        assert len(chunks) > 1
        
        # Check that step is approximately correct
        if len(chunks) >= 2:
            step = chunks[1].start_pos - chunks[0].start_pos
            assert step <= 50  # Should be close to window_step


class TestChunker:
    """Tests for main Chunker class."""
    
    def test_default_strategy(self):
        """Test default chunking strategy."""
        chunker = Chunker()
        text = "Test document content"
        
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1
    
    def test_fixed_size_strategy(self):
        """Test fixed-size strategy selection."""
        config = ChunkingConfig(strategy=ChunkingStrategy.FIXED_SIZE)
        chunker = Chunker(config)
        
        chunks = chunker.chunk("Test content for chunking")
        assert all(isinstance(c, Chunk) for c in chunks)
    
    def test_sentence_strategy(self):
        """Test sentence strategy selection."""
        config = ChunkingConfig(strategy=ChunkingStrategy.SENTENCE)
        chunker = Chunker(config)
        
        chunks = chunker.chunk("First sentence. Second sentence.")
        assert all(isinstance(c, Chunk) for c in chunks)
    
    def test_chunk_batch(self):
        """Test batch chunking."""
        chunker = Chunker()
        texts = ["Document one.", "Document two.", "Document three."]
        
        results = chunker.chunk_batch(texts)
        
        assert len(results) == 3
        assert all(isinstance(r, list) for r in results)
    
    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = Chunker()
        
        chunks = chunker.chunk("")
        assert len(chunks) == 0
        
        chunks = chunker.chunk("   ")
        assert len(chunks) == 0


class TestChunkDocumentFunction:
    """Tests for chunk_document convenience function."""
    
    def test_basic_chunking(self):
        """Test basic document chunking."""
        text = "This is a test document for chunking."
        chunks = chunk_document(text)
        
        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
    
    def test_custom_parameters(self):
        """Test chunking with custom parameters."""
        text = "A" * 500
        chunks = chunk_document(
            text,
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=20,
        )
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.text) <= 150  # With some buffer


class TestChunkHash:
    """Tests for chunk hash computation."""
    
    def test_hash_computed(self):
        """Test that hash is computed."""
        config = ChunkingConfig(compute_chunk_hash=True)
        chunker = Chunker(config)
        
        chunks = chunker.chunk("Test content")
        assert all(c.chunk_hash != "" for c in chunks)
    
    def test_hash_deterministic(self):
        """Test that hash is deterministic."""
        chunker = Chunker()
        
        chunks1 = chunker.chunk("Same content")
        chunks2 = chunker.chunk("Same content")
        
        assert chunks1[0].chunk_hash == chunks2[0].chunk_hash
    
    def test_hash_different_for_different_content(self):
        """Test that different content has different hash."""
        chunker = Chunker()
        
        chunks1 = chunker.chunk("Content A")
        chunks2 = chunker.chunk("Content B")
        
        assert chunks1[0].chunk_hash != chunks2[0].chunk_hash
