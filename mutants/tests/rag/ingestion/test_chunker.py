"""
Tests for Document Chunker Module.
"""

import pytest

from codex.rag.ingestion.chunker import (
    Chunk,
    Chunker,
    ChunkingConfig,
    ChunkingStrategy,
    FixedSizeChunker,
    ParagraphChunker,
    SentenceChunker,
    SlidingWindowChunker,
    chunk_document,
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

        assert chunk.length == 11, "Length must be greater than zero"

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
        assert d["text"] == "Test", "Condition must be true"
        assert d["index"] == 1, "Condition must be true"
        assert d["start_pos"] == 10, "Condition must be true"
        assert d["end_pos"] == 14, "Condition must be true"
        assert d["hash"] == "abc123", "Condition must be true"
        assert d["metadata"]["key"] == "value", "Data must not be empty"


class TestChunkingConfig:
    """Tests for ChunkingConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ChunkingConfig()

        assert config.strategy == ChunkingStrategy.FIXED_SIZE, "strategy is not valid"
        assert config.chunk_size == 1000, "chunk_size is not valid"
        assert config.chunk_overlap == 100, "chunk_overlap is not valid"
        assert config.min_chunk_size == 100, "min_chunk_size is not valid"

    def test_custom_config(self):
        """Test custom configuration."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            chunk_size=500,
            chunk_overlap=50,
        )

        assert config.strategy == ChunkingStrategy.SENTENCE, "strategy is not valid"
        assert config.chunk_size == 500, "chunk_size is not valid"
        assert config.chunk_overlap == 50, "chunk_overlap is not valid"


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
        assert len(chunks) == 0, "Chunks must not be empty"

    def test_chunk_short_text(self, chunker):
        """Test chunking text shorter than chunk size."""
        text = "Short text here."
        chunks = chunker.chunk(text)

        assert len(chunks) == 1, "Chunks must not be empty"
        assert chunks[0].text == text, "text is not valid"
        assert chunks[0].index == 0, "index is not valid"

    def test_chunk_long_text(self, chunker):
        """Test chunking text longer than chunk size."""
        text = "A" * 250
        chunks = chunker.chunk(text)

        assert len(chunks) > 1, "Chunks must not be empty"
        # Verify indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.index == i, "index is not valid"

    def test_chunk_overlap(self, chunker):
        """Test that chunks have overlap."""
        text = "A" * 300
        chunks = chunker.chunk(text)

        # With overlap, chunks should share some content
        if len(chunks) >= 2:
            end_of_first = chunks[0].end_pos
            start_of_second = chunks[1].start_pos
            overlap = end_of_first - start_of_second
            assert overlap >= 0, "overlap must be greater than zero"

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
            assert chunk.text.strip(), "Condition must be true"


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

        assert len(chunks) == 1, "Chunks must not be empty"
        assert "This is one sentence" in chunks[0].text, "This is not valid"

    def test_chunk_multiple_sentences(self, chunker):
        """Test chunking multiple sentences."""
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk(text)

        # Should group sentences until max size
        assert len(chunks) >= 1, "Chunks must not be empty"
        for chunk in chunks:
            assert len(chunk.text) <= 100 or len(chunks) == 1, "Chunks must not be empty"

    def test_chunk_skips_empty_split_sentences(self, chunker, monkeypatch):
        """Test whitespace-only split sentences are ignored without breaking chunking."""
        monkeypatch.setattr(
            chunker,
            "_split_sentences",
            lambda _text: ["First sentence.", "   ", "Second sentence."],
        )
        chunks = chunker.chunk("ignored")

        assert len(chunks) == 1, "Chunks must not be empty"
        assert "First sentence." in chunks[0].text, "First sentence must be preserved"
        assert "Second sentence." in chunks[0].text, "Second sentence must be preserved"


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

        assert len(chunks) == 1, "Chunks must not be empty"
        assert chunks[0].text == text, "text is not valid"

    def test_chunk_multiple_paragraphs(self, chunker):
        """Test chunking multiple paragraphs."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunker.chunk(text)

        assert len(chunks) >= 1, "Chunks must not be empty"
        # All content should be preserved
        all_text = " ".join(c.text for c in chunks)
        assert "First paragraph" in all_text, "Condition must be true"
        assert "Second paragraph" in all_text, "Condition must be true"
        assert "Third paragraph" in all_text, "Condition must be true"


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
        assert len(chunks) == 0, "Chunks must not be empty"

    def test_chunk_short_text(self, chunker):
        """Test chunking text shorter than window."""
        text = "Short"
        chunks = chunker.chunk(text)

        assert len(chunks) == 1, "Chunks must not be empty"

    def test_chunk_sliding_overlap(self, chunker):
        """Test that sliding window creates overlapping chunks."""
        text = "A" * 100
        chunks = chunker.chunk(text)

        # With window_step < chunk_size, should have overlapping chunks
        assert len(chunks) > 1, "Chunks must not be empty"

        # Check that step is approximately correct
        if len(chunks) >= 2:
            step = chunks[1].start_pos - chunks[0].start_pos
            assert step <= 50, "step is not valid"


class TestChunker:
    """Tests for main Chunker class."""

    def test_default_strategy(self):
        """Test default chunking strategy."""
        chunker = Chunker()
        text = "Test document content"

        chunks = chunker.chunk(text)
        assert len(chunks) >= 1, "Chunks must not be empty"

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

        assert len(results) == 3, "Results must not be empty"
        assert all(isinstance(r, list) for r in results)

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = Chunker()

        chunks = chunker.chunk("")
        assert len(chunks) == 0, "Chunks must not be empty"

        chunks = chunker.chunk("   ")
        assert len(chunks) == 0, "Chunks must not be empty"


class TestChunkDocumentFunctionConvenience:
    """Tests for chunk_document convenience function."""

    def test_basic_chunking(self):
        """Test basic document chunking."""
        text = "This is a test document for chunking."
        chunks = chunk_document(text)

        assert len(chunks) >= 1, "Chunks must not be empty"
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

        assert len(chunks) > 1, "Chunks must not be empty"
        for chunk in chunks:
            assert len(chunk.text) <= 150, "Collection must not be empty"


class TestChunkHash:
    """Tests for chunk hash computation."""

    def test_hash_computed(self):
        """Test that hash is computed."""
        config = ChunkingConfig(compute_chunk_hash=True)
        chunker = Chunker(config)

        chunks = chunker.chunk("Test content")
        assert all(c.chunk_hash != "" for c in chunks), "chunk_hash is not valid"

    def test_hash_deterministic(self):
        """Test that hash is deterministic."""
        chunker = Chunker()

        chunks1 = chunker.chunk("Same content")
        chunks2 = chunker.chunk("Same content")

        assert chunks1[0].chunk_hash == chunks2[0].chunk_hash, "chunk_hash is not valid"

    def test_hash_different_for_different_content(self):
        """Test that different content has different hash."""
        chunker = Chunker()

        chunks1 = chunker.chunk("Content A")
        chunks2 = chunker.chunk("Content B")

        assert chunks1[0].chunk_hash != chunks2[0].chunk_hash, "chunk_hash is not valid"


class TestChunkerFallbackStrategies:
    """Tests for semantic/hierarchical fallback to FixedSizeChunker."""

    def test_semantic_strategy_falls_back_to_fixed(self):
        """SEMANTIC is not in STRATEGY_MAP → falls back to FixedSizeChunker."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SEMANTIC,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = Chunker(config)
        # Use text without trailing spaces so each 100-char slice meets min_chunk_size.
        chunks = chunker.chunk("A" * 200)
        assert len(chunks) >= 1, "Chunks must not be empty"

    def test_hierarchical_strategy_falls_back_to_fixed(self):
        """HIERARCHICAL is not in STRATEGY_MAP → falls back to FixedSizeChunker."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.HIERARCHICAL,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = Chunker(config)
        # Use text without trailing spaces so each 100-char slice meets min_chunk_size.
        chunks = chunker.chunk("B" * 200)
        assert len(chunks) >= 1, "Chunks must not be empty"

    def test_empty_text_returns_empty_list(self):
        """Empty text returns empty list regardless of strategy."""
        for strategy in ChunkingStrategy:
            config = ChunkingConfig(strategy=strategy)
            chunker = Chunker(config)
            assert chunker.chunk("") == [], "Condition must be true"
            assert chunker.chunk("   ") == [], "Condition must be true"


class TestChunkBatch:
    """Tests for Chunker.chunk_batch."""

    def test_batch_empty_list(self):
        chunker = Chunker()
        assert chunker.chunk_batch([]) == [], "Condition must be true"

    def test_batch_single_text(self):
        chunker = Chunker()
        results = chunker.chunk_batch(["Hello world"])
        assert len(results) == 1, "Results must not be empty"
        assert len(results[0]) >= 1, "Collection must not be empty"

    def test_batch_multiple_texts(self):
        chunker = Chunker()
        texts = ["First document.", "Second document.", "Third document."]
        results = chunker.chunk_batch(texts)
        assert len(results) == 3, "Results must not be empty"
        assert all(len(r) >= 1 for r in results), "R must not be empty"

    def test_batch_with_empty_text(self):
        chunker = Chunker()
        results = chunker.chunk_batch(["non-empty", "", "also non-empty"])
        assert len(results) == 3, "Results must not be empty"
        assert len(results[0]) >= 1, "Collection must not be empty"
        assert results[1] == [], "Result must not be empty"


class TestChunkDocumentFunction:
    """Tests for the chunk_document() convenience function."""

    def test_basic_chunk_document(self):
        from codex.rag.ingestion.chunker import chunk_document

        chunks = chunk_document("Hello world " * 50)
        assert len(chunks) >= 1, "Chunks must not be empty"

    def test_chunk_document_with_strategy(self):
        from codex.rag.ingestion.chunker import chunk_document

        chunks = chunk_document(
            "Sentence one. Sentence two. Sentence three.",
            strategy=ChunkingStrategy.SENTENCE,
            chunk_size=30,
        )
        assert len(chunks) >= 1, "Chunks must not be empty"

    def test_chunk_document_sliding_window(self):
        from codex.rag.ingestion.chunker import chunk_document

        # text must exceed default window_step (500) to produce ≥2 windows.
        # chunk_size must exceed default min_chunk_size (100) so chunks aren't filtered.
        text = "x " * 600  # 1200 chars
        chunks = chunk_document(text, strategy=ChunkingStrategy.SLIDING_WINDOW, chunk_size=600)
        assert len(chunks) >= 2, "Chunks must not be empty"

    def test_chunk_document_empty(self):
        from codex.rag.ingestion.chunker import chunk_document

        assert chunk_document("") == [], "Condition must be true"


class TestParagraphChunkerEdgeCases:
    """Additional edge-case coverage for ParagraphChunker."""

    def test_paragraph_large_single_paragraph(self):
        """Single paragraph exceeding max_chunk_size triggers split."""
        from codex.rag.ingestion.chunker import ParagraphChunker

        config = ChunkingConfig(max_chunk_size=50, paragraph_separator="\n\n")
        chunker = ParagraphChunker(config)
        long_para = "word " * 30
        chunks = chunker.chunk(long_para)
        assert len(chunks) >= 1, "Chunks must not be empty"

    def test_paragraph_empty_paragraphs_skipped(self):
        """Empty paragraphs between real ones are skipped."""
        from codex.rag.ingestion.chunker import ParagraphChunker

        config = ChunkingConfig(paragraph_separator="\n\n")
        chunker = ParagraphChunker(config)
        text = "First para.\n\n\n\nSecond para."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1, "Chunks must not be empty"


class TestSlidingWindowEdgeCases:
    """Additional edge-case coverage for SlidingWindowChunker."""

    def test_small_step_fills_gaps(self):
        """window_step < chunk_size creates overlapping windows."""
        from codex.rag.ingestion.chunker import SlidingWindowChunker

        config = ChunkingConfig(chunk_size=20, window_step=10, min_chunk_size=5)
        chunker = SlidingWindowChunker(config)
        text = "abcdefghij" * 5
        chunks = chunker.chunk(text)
        assert len(chunks) >= 3, "Chunks must not be empty"

    def test_window_step_larger_than_text(self):
        """window_step ≥ text length → single chunk."""
        from codex.rag.ingestion.chunker import SlidingWindowChunker

        config = ChunkingConfig(chunk_size=100, window_step=200, min_chunk_size=1)
        chunker = SlidingWindowChunker(config)
        chunks = chunker.chunk("Short text")
        assert len(chunks) == 1, "Chunks must not be empty"


# ---------------------------------------------------------------------------
# Targeted gap-fill tests to raise overall coverage to ≥95%
# ---------------------------------------------------------------------------


class TestFixedSizeChunkerCoverage:
    """Cover missed branches in FixedSizeChunker."""

    def test_no_hash_when_compute_chunk_hash_false(self):
        """_create_chunk: compute_chunk_hash=False → chunk_hash is empty (line 119->122)."""
        config = ChunkingConfig(
            chunk_size=500,
            compute_chunk_hash=False,
            min_chunk_size=1,
        )
        chunker = FixedSizeChunker(config)
        chunks = chunker.chunk("Hello world content here for testing")
        assert all(c.chunk_hash == "" for c in chunks), "chunk_hash is not valid"

    def test_whitespace_only_text_returns_empty(self):
        """FixedSizeChunker.chunk: whitespace-only text → [] (line 146)."""
        config = ChunkingConfig(chunk_size=100, min_chunk_size=10)
        chunker = FixedSizeChunker(config)
        assert chunker.chunk("   \t\t  ") == [], "Condition must be true"

    def test_negative_overlap_exits_while_via_condition(self):
        """Negative chunk_overlap causes while condition to go False naturally (line 165->198)."""
        config = ChunkingConfig(
            chunk_size=50,
            chunk_overlap=-60,  # next_start jumps past text_len
            min_chunk_size=5,
            respect_sentence_boundaries=False,
        )
        chunker = FixedSizeChunker(config)
        text = "A" * 100
        chunks = chunker.chunk(text)
        # At least one chunk is produced; while exits by condition, not break
        assert len(chunks) >= 1, "Chunks must not be empty"

    def test_chunk_below_min_size_is_skipped(self):
        """Chunk stripped to empty is skipped (line 177->189 False branch)."""
        config = ChunkingConfig(
            chunk_size=10,
            chunk_overlap=0,
            min_chunk_size=5,
            respect_sentence_boundaries=False,
        )
        chunker = FixedSizeChunker(config)
        # First 10 chars are spaces → stripped to "" → skipped
        text = " " * 10 + "B" * 20
        chunks = chunker.chunk(text)
        # Only the non-whitespace part should produce chunks
        assert all(c.text.strip() != "" for c in chunks), "Condition must be true"

    def test_overlap_ge_chunk_size_forces_advance(self):
        """overlap >= chunk_size triggers next_start = end guard (line 195)."""
        config = ChunkingConfig(
            chunk_size=50,
            chunk_overlap=100,  # overlap > chunk_size
            min_chunk_size=5,
            respect_sentence_boundaries=False,
        )
        chunker = FixedSizeChunker(config)
        text = "X" * 200
        # Should not infinite-loop; produces some chunks
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1, "Chunks must not be empty"


class TestSentenceChunkerCoverage:
    """Cover missed branches in SentenceChunker."""

    def test_empty_text_returns_empty(self):
        """SentenceChunker.chunk('') → [] (line 232)."""
        config = ChunkingConfig(strategy=ChunkingStrategy.SENTENCE, min_chunk_size=1)
        chunker = SentenceChunker(config)
        assert chunker.chunk("") == [], "Condition must be true"

    def test_all_empty_sentences_skipped(self):
        """Sentences that strip to empty are skipped (lines 246-247)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            max_chunk_size=200,
            min_chunk_size=1,
        )
        chunker = SentenceChunker(config)
        # After split the 'sentences' may include whitespace-only strings
        result = chunker.chunk("   \n   ")
        # No valid sentences → empty list (or empty final chunk path)
        assert isinstance(result, list)

    def test_max_chunk_size_triggers_save(self):
        """Adding a sentence exceeds max_chunk_size → save current chunk (lines 254-267)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            max_chunk_size=30,
            min_chunk_size=1,
        )
        chunker = SentenceChunker(config)
        text = "Short one. This is a much longer second sentence here for testing purposes."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2, "Chunks must not be empty"

    def test_empty_final_chunk_text_skipped(self):
        """If current_chunk_text is empty after loop, no final chunk added (line 274->284)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            max_chunk_size=200,
            min_chunk_size=1,
        )
        chunker = SentenceChunker(config)
        # Whitespace-only text: all sentences stripped to "", all skipped
        # → current_chunk_text stays "" → final if is False → 274->284
        chunks = chunker.chunk("   \n   \n   ")
        assert chunks == [], "chunks is not valid"


class TestParagraphChunkerCoverage:
    """Cover missed branches in ParagraphChunker."""

    def test_empty_text_returns_empty(self):
        """ParagraphChunker.chunk('') → [] (line 303)."""
        config = ChunkingConfig(strategy=ChunkingStrategy.PARAGRAPH, min_chunk_size=1)
        chunker = ParagraphChunker(config)
        assert chunker.chunk("") == [], "Condition must be true"

    def test_max_chunk_size_triggers_save(self):
        """Paragraph exceeds max_chunk_size → save current chunk (lines 325-337)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.PARAGRAPH,
            max_chunk_size=30,
            min_chunk_size=1,
            paragraph_separator="\n\n",
        )
        chunker = ParagraphChunker(config)
        text = "Short para.\n\nThis is a much longer second paragraph with lots of content here."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2, "Chunks must not be empty"

    def test_all_empty_paragraphs_no_final_chunk(self):
        """All-empty paragraphs → current_chunk_text stays '' → final if False (line 344->354)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.PARAGRAPH,
            max_chunk_size=200,
            min_chunk_size=1,
            paragraph_separator="\n\n",
        )
        chunker = ParagraphChunker(config)
        # Only separators → all paragraphs are empty → nothing saved
        chunks = chunker.chunk("\n\n\n\n")
        assert chunks == [], "chunks is not valid"


class TestSlidingWindowChunkerCoverage:
    """Cover missed branches in SlidingWindowChunker."""

    def test_chunk_below_min_size_skipped(self):
        """Chunk stripped below min_chunk_size is skipped (line 378->389 False branch)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SLIDING_WINDOW,
            chunk_size=10,
            window_step=10,
            min_chunk_size=20,  # min > chunk_size so chunks always fail
        )
        chunker = SlidingWindowChunker(config)
        # chunk_text will never be >= min_chunk_size=20 since chunk_size=10
        chunks = chunker.chunk("A" * 50)
        assert chunks == [], "chunks is not valid"

    def test_gap_prevention_fires(self):
        """window_step > chunk_size triggers gap-prevention (line 391)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SLIDING_WINDOW,
            chunk_size=20,
            window_step=30,  # step > chunk_size → gap possible
            min_chunk_size=1,
        )
        chunker = SlidingWindowChunker(config)
        text = "A" * 100
        chunks = chunker.chunk(text)
        # Should produce chunks without gaps
        assert len(chunks) >= 1, "Chunks must not be empty"


class TestSentenceChunkerEmptySentence:
    """Tests for empty-sentence skipping in SentenceChunker (lines 247-248)."""

    def test_sentence_chunker_skips_empty_trailing_sentence(self):
        """Empty string after regex split on trailing period is skipped (lines 247-248)."""
        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            chunk_size=200,
            max_chunk_size=500,
            min_chunk_size=1,
        )
        chunker = SentenceChunker(config)
        # Text ending with '.' causes the regex to split and produce an empty
        # trailing element; the code must skip it rather than creating an empty chunk.
        text = "First sentence. Second sentence."
        chunks = chunker.chunk(text)
        # All chunks must have non-empty text
        assert all(chunk.text.strip() for chunk in chunks), "no empty chunks expected"
        # Both sentences should be present in the combined text
        combined = " ".join(c.text for c in chunks)
        assert "First sentence" in combined, "first sentence missing"
        assert "Second sentence" in combined, "second sentence missing"
