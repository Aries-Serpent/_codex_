"""Tests for src/codex/cognitive/context_compressor.py — Phase 10B coverage.

Covers CompressionStrategy, ContextType, CompressedContext, TokenEstimator,
KeyPointExtractor, SentenceScorer, ExtractiveSummarizer, ContextPrioritizer,
ContextIndex, and ContextCompressor.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from codex.cognitive.context_compressor import (
    CompressedContext,
    CompressionStrategy,
    ContextCompressor,
    ContextIndex,
    ContextPrioritizer,
    ContextType,
    ExtractiveSummarizer,
    KeyPointExtractor,
    SentenceScorer,
    TokenEstimator,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_compression_strategy_values(self):
        assert CompressionStrategy.EXTRACTIVE.value == "extractive", "Value must be initialized"
        assert CompressionStrategy.ABSTRACTIVE.value == "abstractive", "Value must be initialized"
        assert CompressionStrategy.HYBRID.value == "hybrid", "Value must be initialized"

    def test_context_type_values(self):
        assert ContextType.SESSION_LOG.value == "session_log", "Value must be initialized"
        assert ContextType.ERRORS_FIXES.value == "errors_fixes", "Value must be initialized"


# ---------------------------------------------------------------------------
# CompressedContext
# ---------------------------------------------------------------------------


class TestCompressedContext:
    @pytest.fixture()
    def ctx(self):
        return CompressedContext(
            context_id="CTX-00001",
            context_type=ContextType.SESSION_LOG,
            original_size=1000,
            compressed_size=200,
            compression_ratio=0.2,
            summary="Session summary",
            key_points=["fixed imports", "added tests"],
            preserved_items=["CRITICAL: do not merge"],
            created_at=datetime.now(timezone.utc),
            source_session="S42",
            relevance_score=0.9,
            expiry_weight=0.8,
        )

    def test_to_dict_keys(self, ctx):
        d = ctx.to_dict()
        assert "context_id" in d, "Condition must be true"
        assert "compression_ratio" in d, "Condition must be true"
        assert d["context_type"] == "session_log", "Condition must be true"

    def test_roundtrip(self, ctx):
        d = ctx.to_dict()
        restored = CompressedContext.from_dict(d)
        assert restored.context_id == ctx.context_id, "context_id is not valid"
        assert restored.compression_ratio == ctx.compression_ratio, "compression_ratio is not valid"
        assert restored.key_points == ctx.key_points, "key_points is not valid"


# ---------------------------------------------------------------------------
# TokenEstimator
# ---------------------------------------------------------------------------


class TestTokenEstimator:
    def test_estimate_tokens(self):
        result = TokenEstimator.estimate_tokens("Hello world test string")
        assert result == len("Hello world test string") // 4, "Result must not be empty"

    def test_estimate_empty(self):
        assert TokenEstimator.estimate_tokens("") == 0, "TokenEstimat is not valid"

    def test_estimate_tokens_list(self):
        items = ["hello", "world"]
        result = TokenEstimator.estimate_tokens_list(items)
        expected = sum(len(s) // 4 for s in items)
        assert result == expected, "Result must not be empty"


# ---------------------------------------------------------------------------
# KeyPointExtractor
# ---------------------------------------------------------------------------


class TestKeyPointExtractor:
    @pytest.fixture()
    def extractor(self):
        return KeyPointExtractor()

    def test_extract_fix(self, extractor):
        text = "Fixed the broken import in module X.\nSome other line."
        points = extractor.extract(text)
        assert len(points) >= 1, "Points must not be empty"
        assert points[0][1] == "fix", "Condition must be true"

    def test_extract_feature(self, extractor):
        text = "Implemented new caching layer for queries."
        points = extractor.extract(text)
        assert len(points) >= 1, "Points must not be empty"
        assert points[0][1] == "feature", "Condition must be true"

    def test_extract_max_points(self, extractor):
        text = "\n".join([f"Fixed issue number {i} in the system" for i in range(20)])
        points = extractor.extract(text, max_points=5)
        assert len(points) <= 5, "Points must not be empty"

    def test_skip_short_lines(self, extractor):
        text = "Hi\nBye\n"
        points = extractor.extract(text)
        assert points == [], "points is not valid"


# ---------------------------------------------------------------------------
# SentenceScorer
# ---------------------------------------------------------------------------


class TestSentenceScorer:
    @pytest.fixture()
    def scorer(self):
        return SentenceScorer()

    def test_high_importance_words(self, scorer):
        score_important = scorer.score("Critical security fix resolved the blocking issue")
        score_mundane = scorer.score("updated the readme file today")
        assert score_important > score_mundane, "score_important must be greater than zero"

    def test_empty_sentence(self, scorer):
        assert scorer.score("") == 0.0, "sc is not valid"


# ---------------------------------------------------------------------------
# ExtractiveSummarizer
# ---------------------------------------------------------------------------


class TestExtractiveSummarizer:
    @pytest.fixture()
    def summarizer(self):
        return ExtractiveSummarizer(target_ratio=0.3)

    def test_summarize_basic(self, summarizer):
        text = (
            "Critical security fix applied. "
            "Updated the readme. "
            "Fixed import errors. "
            "Added new tests. "
            "Cleaned up logs."
        )
        result = summarizer.summarize(text)
        assert len(result) > 0, "Result must not be empty"
        assert result.endswith("."), "Result must not be empty"

    def test_summarize_empty(self, summarizer):
        assert summarizer.summarize("") == "", "Condition must be true"

    def test_summarize_single_sentence(self, summarizer):
        result = summarizer.summarize("Important security update applied")
        assert len(result) > 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# ContextPrioritizer
# ---------------------------------------------------------------------------


class TestContextPrioritizer:
    @pytest.fixture()
    def prioritizer(self):
        return ContextPrioritizer(decay_factor=0.95)

    def test_recent_higher_relevance(self, prioritizer):
        recent = prioritizer.calculate_relevance(datetime.now(timezone.utc), access_count=0)
        old = prioritizer.calculate_relevance(
            datetime.now(timezone.utc) - timedelta(days=30), access_count=0
        )
        assert recent > old, "recent must be greater than zero"

    def test_access_count_boost(self, prioritizer):
        no_access = prioritizer.calculate_relevance(datetime.now(timezone.utc), access_count=0)
        with_access = prioritizer.calculate_relevance(datetime.now(timezone.utc), access_count=10)
        assert with_access > no_access, "with_access must be greater than zero"

    def test_prioritize_list(self, prioritizer):
        now = datetime.now(timezone.utc)
        items = [
            CompressedContext(
                context_id=f"CTX-{i}",
                context_type=ContextType.SESSION_LOG,
                original_size=100,
                compressed_size=20,
                compression_ratio=0.2,
                summary=f"summary {i}",
                key_points=[],
                preserved_items=[],
                created_at=now - timedelta(days=i * 10),
                source_session=f"S{i}",
            )
            for i in range(5)
        ]
        result = prioritizer.prioritize(items, max_items=3)
        assert len(result) == 3, "Result must not be empty"
        # Most recent should be first
        assert result[0].context_id == "CTX-0", "Result must not be empty"


# ---------------------------------------------------------------------------
# ContextIndex
# ---------------------------------------------------------------------------


class TestContextIndex:
    @pytest.fixture()
    def index(self, tmp_path):
        return ContextIndex(index_path=tmp_path / "index.json")

    def _make_ctx(self, ctx_id="CTX-1", ctx_type=ContextType.SESSION_LOG):
        return CompressedContext(
            context_id=ctx_id,
            context_type=ctx_type,
            original_size=100,
            compressed_size=20,
            compression_ratio=0.2,
            summary="test",
            key_points=[],
            preserved_items=[],
            created_at=datetime.now(timezone.utc),
            source_session="S1",
        )

    def test_add_and_get(self, index):
        ctx = self._make_ctx()
        index.add(ctx)
        assert index.get("CTX-1") is not None, "Value must be initialized"

    def test_get_missing(self, index):
        assert index.get("nonexistent") is None, "Condition must be true"

    def test_get_by_type(self, index):
        index.add(self._make_ctx("CTX-1", ContextType.SESSION_LOG))
        index.add(self._make_ctx("CTX-2", ContextType.ERRORS_FIXES))
        results = index.get_by_type(ContextType.SESSION_LOG)
        assert len(results) == 1, "Results must not be empty"

    def test_get_recent(self, index):
        for i in range(5):
            index.add(self._make_ctx(f"CTX-{i}"))
        recent = index.get_recent(limit=3)
        assert len(recent) == 3, "Recent must not be empty"

    def test_count(self, index):
        assert index.count() == 0, "Count must be greater than zero"
        index.add(self._make_ctx())
        assert index.count() == 1, "Count must be greater than zero"

    def test_persistence(self, tmp_path):
        path = tmp_path / "index.json"
        idx1 = ContextIndex(index_path=path)
        idx1.add(self._make_ctx())

        idx2 = ContextIndex(index_path=path)
        assert idx2.count() == 1, "Count must be greater than zero"

    def test_corrupt_index(self, tmp_path):
        path = tmp_path / "index.json"
        path.write_text("{corrupt")
        idx = ContextIndex(index_path=path)
        assert idx.count() == 0, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# ContextCompressor
# ---------------------------------------------------------------------------


class TestContextCompressor:
    @pytest.fixture()
    def compressor(self, tmp_path):
        return ContextCompressor(
            index_path=tmp_path / "index.json",
            target_compression=0.3,
        )

    def test_generate_id(self, compressor):
        id1 = compressor._generate_id()
        id2 = compressor._generate_id()
        assert id1 != id2, "id1 is not valid"
        assert id1.startswith("CTX-"), "Condition must be true"
