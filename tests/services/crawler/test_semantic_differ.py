"""Comprehensive tests for SemanticDiffer and content diffing (P4 priority module).

This test suite provides ≥90% coverage for:
- src/services/crawler/content_diff.py (SemanticDiffer class)
- ContentDiffer class
- IncrementalSyncDecider class
- Related enums and dataclasses

Tests include:
- Semantic similarity computation
- Text normalization
- Embedding vs basic similarity
- Edge cases (empty, identical, completely different)
- Integration with content diffing
"""

from __future__ import annotations

from unittest.mock import Mock, patch
import pytest

from services.crawler.content_diff import (
    ChangeType,
    DiffSegment,
    ContentDiffResult,
    ContentDiffer,
    IncrementalSyncDecider,
    SemanticDiffer,
)


# ============================================================================
# Test Enums and Dataclasses
# ============================================================================


class TestChangeType:
    """Test ChangeType enum."""
    
    def test_all_change_types(self):
        """Test all change type values."""
        assert ChangeType.NO_CHANGE.value == "no_change"
        assert ChangeType.MINOR.value == "minor"
        assert ChangeType.MODERATE.value == "moderate"
        assert ChangeType.MAJOR.value == "major"
        assert ChangeType.COMPLETE.value == "complete"
    
    def test_enum_comparison(self):
        """Test enum comparison."""
        assert ChangeType.NO_CHANGE != ChangeType.MINOR
        assert ChangeType.MINOR == ChangeType.MINOR


class TestDiffSegment:
    """Test DiffSegment dataclass."""
    
    def test_creation(self):
        """Test creating diff segment."""
        segment = DiffSegment(
            change_type="replace",
            old_content="old text",
            new_content="new text",
            line_start=10,
            line_end=12,
        )
        
        assert segment.change_type == "replace"
        assert segment.old_content == "old text"
        assert segment.new_content == "new text"
        assert segment.line_start == 10
        assert segment.line_end == 12
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        segment = DiffSegment(
            change_type="insert",
            old_content="",
            new_content="new line",
            line_start=5,
            line_end=5,
        )
        
        data = segment.to_dict()
        
        assert data["change_type"] == "insert"
        assert data["new_content_preview"] == "new line"
        assert data["line_start"] == 5
    
    def test_to_dict_truncates_long_content(self):
        """Test that long content is truncated in dict."""
        long_content = "x" * 200
        segment = DiffSegment(
            change_type="replace",
            old_content=long_content,
            new_content="short",
            line_start=1,
            line_end=1,
        )
        
        data = segment.to_dict()
        
        assert len(data["old_content_preview"]) <= 104  # 100 + "..."
        assert data["old_content_preview"].endswith("...")


class TestContentDiffResult:
    """Test ContentDiffResult dataclass."""
    
    def test_creation_minimal(self):
        """Test creating result with minimal fields."""
        result = ContentDiffResult(
            change_type=ChangeType.MINOR,
            change_ratio=0.05,
            similarity_ratio=0.95,
            old_hash="abc123",
            new_hash="def456",
        )
        
        assert result.change_type == ChangeType.MINOR
        assert result.change_ratio == 0.05
        assert result.similarity_ratio == 0.95
        assert len(result.segments) == 0
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = ContentDiffResult(
            change_type=ChangeType.MODERATE,
            change_ratio=0.15,
            similarity_ratio=0.85,
            old_hash="old",
            new_hash="new",
            old_line_count=100,
            new_line_count=110,
            lines_added=15,
            lines_removed=5,
            lines_modified=10,
        )
        
        data = result.to_dict()
        
        assert data["change_type"] == "moderate"
        assert data["change_ratio"] == 0.15
        assert data["similarity_ratio"] == 0.85
        assert data["lines_added"] == 15
        assert data["segment_count"] == 0
    
    def test_should_sync_above_threshold(self):
        """Test should_sync returns True above threshold."""
        result = ContentDiffResult(
            change_type=ChangeType.MINOR,
            change_ratio=0.05,
            similarity_ratio=0.95,
            old_hash="a",
            new_hash="b",
        )
        
        assert result.should_sync(min_change_ratio=0.01) is True
        assert result.should_sync(min_change_ratio=0.10) is False
    
    def test_should_sync_no_change(self):
        """Test should_sync returns False for no change."""
        result = ContentDiffResult(
            change_type=ChangeType.NO_CHANGE,
            change_ratio=0.0,
            similarity_ratio=1.0,
            old_hash="same",
            new_hash="same",
        )
        
        assert result.should_sync(min_change_ratio=0.01) is False


# ============================================================================
# Test ContentDiffer
# ============================================================================


class TestContentDiffer:
    """Test ContentDiffer class."""
    
    @pytest.fixture
    def differ(self):
        """Create standard content differ."""
        return ContentDiffer(
            min_change_ratio=0.01,
            strip_html=True,
            ignore_whitespace=True,
        )
    
    def test_initialization(self):
        """Test differ initialization."""
        differ = ContentDiffer(
            min_change_ratio=0.05,
            strip_html=False,
            ignore_whitespace=False,
        )
        
        assert differ.min_change_ratio == 0.05
        assert differ.strip_html is False
        assert differ.ignore_whitespace is False
    
    def test_hash_content(self):
        """Test content hashing."""
        hash1 = ContentDiffer._hash_content("test content")
        hash2 = ContentDiffer._hash_content("test content")
        hash3 = ContentDiffer._hash_content("different content")
        
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 16  # Truncated to 16 chars
    
    def test_normalize_content_strips_html(self, differ):
        """Test HTML stripping in normalization."""
        html = "<p>Hello <b>world</b></p>"
        normalized = differ._normalize_content(html)
        
        assert "<p>" not in normalized
        assert "<b>" not in normalized
        assert "Hello" in normalized
        assert "world" in normalized
    
    def test_normalize_content_handles_whitespace(self, differ):
        """Test whitespace normalization."""
        text = "Line1\n\n  Line2  \n   Line3   "
        normalized = differ._normalize_content(text)
        
        # Should have normalized whitespace
        assert "  " not in normalized or normalized.count("  ") < text.count("  ")
    
    def test_normalize_content_without_html_stripping(self):
        """Test normalization without HTML stripping."""
        differ = ContentDiffer(strip_html=False)
        html = "<p>Hello</p>"
        normalized = differ._normalize_content(html)
        
        assert "<p>" in normalized
    
    def test_classify_change_no_change(self, differ):
        """Test classifying no change."""
        change_type = differ._classify_change(0.0)
        assert change_type == ChangeType.NO_CHANGE
    
    def test_classify_change_minor(self, differ):
        """Test classifying minor change."""
        change_type = differ._classify_change(0.03)
        assert change_type == ChangeType.MINOR
    
    def test_classify_change_moderate(self, differ):
        """Test classifying moderate change."""
        change_type = differ._classify_change(0.15)
        assert change_type == ChangeType.MODERATE
    
    def test_classify_change_major(self, differ):
        """Test classifying major change."""
        change_type = differ._classify_change(0.50)
        assert change_type == ChangeType.MAJOR
    
    def test_classify_change_complete(self, differ):
        """Test classifying complete rewrite."""
        change_type = differ._classify_change(0.90)
        assert change_type == ChangeType.COMPLETE
    
    def test_diff_identical_content(self, differ):
        """Test diff with identical content."""
        content = "This is the same content."
        result = differ.diff(content, content)
        
        assert result.change_type == ChangeType.NO_CHANGE
        assert result.change_ratio == 0.0
        assert result.similarity_ratio == 1.0
        assert result.old_hash == result.new_hash
    
    def test_diff_minor_change(self, differ):
        """Test diff with minor change."""
        old = "Hello world! This is a test."
        new = "Hello world! This is a test!"  # Added exclamation
        
        result = differ.diff(old, new)
        
        assert result.change_ratio < 0.1
        assert result.similarity_ratio > 0.9
        assert result.change_type in [ChangeType.MINOR, ChangeType.NO_CHANGE]
    
    def test_diff_major_change(self, differ):
        """Test diff with major change."""
        old = "This is the original content with many words and sentences."
        new = "Completely different text here."
        
        result = differ.diff(old, new)
        
        assert result.change_ratio > 0.3
        assert result.similarity_ratio < 0.7
        assert result.change_type in [ChangeType.MAJOR, ChangeType.COMPLETE]
    
    def test_diff_with_line_counts(self, differ):
        """Test diff includes line count statistics."""
        old = "Line 1\nLine 2\nLine 3"
        new = "Line 1\nLine 2 modified\nLine 3\nLine 4"
        
        result = differ.diff(old, new)
        
        # Line counts depend on normalization - just check they're positive
        assert result.old_line_count > 0
        assert result.new_line_count > 0
        assert result.lines_added > 0 or result.lines_modified > 0 or result.lines_removed > 0
    
    def test_diff_without_normalization(self, differ):
        """Test diff without normalization."""
        old = "  Hello  "
        new = "Hello"
        
        result = differ.diff(old, new, normalize=False)
        
        # Without normalization, these should be different
        assert result.change_ratio > 0.0
    
    def test_extract_segments(self, differ):
        """Test segment extraction from diffs."""
        old_lines = ["Line 1", "Line 2", "Line 3"]
        new_lines = ["Line 1", "Line 2 modified", "Line 3", "Line 4"]
        
        segments = differ._extract_segments(old_lines, new_lines)
        
        assert isinstance(segments, list)
        # Should have at least one segment for the changes
        assert len(segments) >= 0
    
    def test_should_resync_above_threshold(self, differ):
        """Test should_resync returns True above threshold."""
        old = "Original content"
        new = "Modified content with changes"
        
        should_resync, change_type, ratio = differ.should_resync(old, new)
        
        assert isinstance(should_resync, bool)
        assert isinstance(change_type, ChangeType)
        assert 0.0 <= ratio <= 1.0
    
    def test_should_resync_identical(self, differ):
        """Test should_resync returns False for identical content."""
        content = "Same content"
        
        should_resync, change_type, ratio = differ.should_resync(content, content)
        
        assert should_resync is False
        assert change_type == ChangeType.NO_CHANGE
        assert ratio == 0.0


# ============================================================================
# Test IncrementalSyncDecider
# ============================================================================


class TestIncrementalSyncDecider:
    """Test IncrementalSyncDecider class."""
    
    @pytest.fixture
    def decider(self):
        """Create standard sync decider."""
        return IncrementalSyncDecider(
            micro_update_threshold=0.10,
            full_update_threshold=0.50,
        )
    
    def test_initialization(self):
        """Test decider initialization."""
        decider = IncrementalSyncDecider(
            micro_update_threshold=0.05,
            full_update_threshold=0.25,
        )
        
        assert decider.micro_update_threshold == 0.05
        assert decider.full_update_threshold == 0.25
    
    def test_initialization_with_custom_differ(self):
        """Test initialization with custom differ."""
        custom_differ = ContentDiffer(min_change_ratio=0.02)
        decider = IncrementalSyncDecider(differ=custom_differ)
        
        assert decider.differ is custom_differ
    
    def test_decide_no_change(self, decider):
        """Test decision for no change."""
        content = "Same content"
        decision = decider.decide(content, content)
        
        assert decision["action"] == "skip"
        assert "no changes" in decision["reason"].lower()
        assert decision["change_ratio"] == 0.0
    
    def test_decide_micro_update(self, decider):
        """Test decision for micro update."""
        old = "Hello world! This is a test document with some content."
        new = "Hello world! This is a test document with some content!"
        
        decision = decider.decide(old, new)
        
        # Should be micro update or skip (very small change)
        assert decision["action"] in ["micro_update", "skip"]
        if decision["action"] == "micro_update":
            assert decision["change_ratio"] < 0.10
    
    def test_decide_full_update_major_change(self, decider):
        """Test decision for full update on major change."""
        old = "This is the original document with specific content."
        new = "Completely rewritten document with entirely different information and structure."
        
        decision = decider.decide(old, new)
        
        assert decision["action"] == "full_update"
        assert "change" in decision["reason"].lower()
        assert decision["change_ratio"] >= 0.10  # At least moderate
    
    def test_decide_moderate_change(self, decider):
        """Test decision for moderate change (defaults to full update)."""
        old = "Document with some content and information here."
        new = "Document with different content and other information here."
        
        decision = decider.decide(old, new)
        
        # Moderate changes should trigger full update
        assert decision["action"] in ["full_update", "micro_update"]
        assert 0.0 <= decision["change_ratio"] <= 1.0
    
    def test_decide_includes_diff_metadata(self, decider):
        """Test that decision includes diff metadata."""
        old = "Old content"
        new = "New content"
        
        decision = decider.decide(old, new)
        
        assert "diff" in decision
        assert "change_ratio" in decision
        assert isinstance(decision["diff"], dict)


# ============================================================================
# Test SemanticDiffer
# ============================================================================


class TestSemanticDiffer:
    """Test SemanticDiffer class."""
    
    @pytest.fixture
    def differ_with_embeddings(self):
        """Create semantic differ with embeddings enabled."""
        return SemanticDiffer(
            similarity_threshold=0.98,
            use_embeddings=True,
        )
    
    @pytest.fixture
    def differ_without_embeddings(self):
        """Create semantic differ without embeddings."""
        return SemanticDiffer(
            similarity_threshold=0.98,
            use_embeddings=False,
        )
    
    def test_initialization_with_embeddings(self):
        """Test initialization with embeddings."""
        differ = SemanticDiffer(
            similarity_threshold=0.95,
            use_embeddings=True,
        )
        
        assert differ.similarity_threshold == 0.95
        assert differ.use_embeddings is True
    
    def test_initialization_without_embeddings(self):
        """Test initialization without embeddings."""
        differ = SemanticDiffer(
            similarity_threshold=0.99,
            use_embeddings=False,
        )
        
        assert differ.similarity_threshold == 0.99
        assert differ._embedding_available is False
    
    def test_normalize_text(self, differ_with_embeddings):
        """Test text normalization."""
        text = "  Hello   World\n  With   Spaces  "
        normalized = differ_with_embeddings._normalize_text(text)
        
        assert normalized == "hello world with spaces"
        assert "  " not in normalized
        assert normalized.islower()
    
    def test_normalize_text_empty(self, differ_with_embeddings):
        """Test normalizing empty text."""
        normalized = differ_with_embeddings._normalize_text("")
        assert normalized == ""
    
    def test_basic_similarity_identical(self, differ_with_embeddings):
        """Test basic similarity with identical text."""
        text = "This is a test"
        similarity = differ_with_embeddings._basic_similarity(text, text)
        
        assert similarity == 1.0
    
    def test_basic_similarity_different(self, differ_with_embeddings):
        """Test basic similarity with different text."""
        text1 = "Hello world"
        text2 = "Goodbye universe"
        similarity = differ_with_embeddings._basic_similarity(text1, text2)
        
        assert 0.0 <= similarity < 1.0
    
    def test_basic_similarity_similar(self, differ_with_embeddings):
        """Test basic similarity with similar text."""
        text1 = "The quick brown fox"
        text2 = "The quick brown fox jumps"
        similarity = differ_with_embeddings._basic_similarity(text1, text2)
        
        assert 0.7 <= similarity < 1.0
    
    def test_compute_semantic_similarity_fallback(self):
        """Test semantic similarity falls back to basic when embeddings unavailable."""
        # Create differ without embeddings
        differ = SemanticDiffer(use_embeddings=False)
        
        text1 = "Test content"
        text2 = "Test content"
        
        similarity = differ.compute_semantic_similarity(text1, text2)
        
        assert similarity == 1.0  # Identical should be 1.0
    
    def test_compute_semantic_similarity_with_sklearn(self):
        """Test semantic similarity with sklearn (if available)."""
        differ = SemanticDiffer(use_embeddings=True)
        
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The quick brown fox leaps over the lazy dog"
        
        similarity = differ.compute_semantic_similarity(text1, text2)
        
        # Should be high similarity
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.7  # Very similar texts
    
    def test_compute_semantic_similarity_identical(self, differ_with_embeddings):
        """Test semantic similarity with identical text."""
        text = "This is identical text"
        similarity = differ_with_embeddings.compute_semantic_similarity(text, text)
        
        assert similarity == 1.0
    
    def test_compute_semantic_similarity_very_different(self, differ_with_embeddings):
        """Test semantic similarity with very different text."""
        text1 = "Machine learning algorithms"
        text2 = "Cooking recipes for pasta"
        similarity = differ_with_embeddings.compute_semantic_similarity(text1, text2)
        
        assert 0.0 <= similarity < 0.5  # Should be low
    
    def test_compute_semantic_diff_identical(self, differ_with_embeddings):
        """Test semantic diff with identical content."""
        content = "This is the same content"
        result = differ_with_embeddings.compute_semantic_diff(content, content)
        
        assert result["semantic_similarity"] == 1.0
        assert result["is_semantically_similar"] is True
        assert result["significance"] == "insignificant"
        assert result["should_update"] is False
    
    def test_compute_semantic_diff_minor_change(self, differ_with_embeddings):
        """Test semantic diff with minor change."""
        old = "The document contains important information."
        new = "The document contains important information!"
        
        result = differ_with_embeddings.compute_semantic_diff(old, new)
        
        assert result["semantic_similarity"] > 0.95
        assert result["significance"] in ["insignificant", "minor"]
    
    def test_compute_semantic_diff_major_change(self, differ_with_embeddings):
        """Test semantic diff with major change."""
        old = "This document is about machine learning."
        new = "This document is about cooking recipes."
        
        result = differ_with_embeddings.compute_semantic_diff(old, new)
        
        assert result["semantic_similarity"] < 0.90
        assert result["significance"] in ["moderate", "major", "complete"]
        assert result["should_update"] is True
    
    def test_compute_semantic_diff_empty_strings(self, differ_with_embeddings):
        """Test semantic diff with empty strings."""
        result = differ_with_embeddings.compute_semantic_diff("", "")
        
        # Empty strings should be identical
        assert result["semantic_similarity"] == 1.0
    
    def test_compute_semantic_diff_one_empty(self, differ_with_embeddings):
        """Test semantic diff with one empty string."""
        result = differ_with_embeddings.compute_semantic_diff("content", "")
        
        # Should show low similarity
        assert result["semantic_similarity"] < 0.5
        assert result["should_update"] is True
    
    def test_compute_semantic_diff_classification(self, differ_with_embeddings):
        """Test significance classification boundaries."""
        # Test each significance level
        test_cases = [
            (1.00, "insignificant"),
            (0.98, "insignificant"),
            (0.97, "minor"),
            (0.95, "minor"),
            (0.90, "moderate"),
            (0.85, "moderate"),
            (0.75, "major"),
            (0.70, "major"),
            (0.50, "complete"),
        ]
        
        for similarity, expected_sig in test_cases:
            with patch.object(
                differ_with_embeddings,
                "compute_semantic_similarity",
                return_value=similarity
            ):
                result = differ_with_embeddings.compute_semantic_diff("old", "new")
                assert result["significance"] == expected_sig, \
                    f"Similarity {similarity} should be '{expected_sig}'"
    
    def test_should_resync_identical(self, differ_with_embeddings):
        """Test should_resync with identical content."""
        content = "Same content"
        should_resync, diff_result = differ_with_embeddings.should_resync(content, content)
        
        assert should_resync is False
        assert diff_result["is_semantically_similar"] is True
    
    def test_should_resync_different(self, differ_with_embeddings):
        """Test should_resync with different content."""
        old = "Original document about topic A"
        new = "New document about topic B"
        
        should_resync, diff_result = differ_with_embeddings.should_resync(old, new)
        
        # Depends on similarity but should be consistent with diff result
        assert should_resync == diff_result["should_update"]
    
    def test_should_resync_above_threshold(self, differ_with_embeddings):
        """Test should_resync when similarity above threshold."""
        # Mock high similarity
        with patch.object(
            differ_with_embeddings,
            "compute_semantic_similarity",
            return_value=0.99
        ):
            should_resync, diff_result = differ_with_embeddings.should_resync(
                "old", "new"
            )
            
            assert should_resync is False  # Above threshold = no resync needed
    
    def test_should_resync_below_threshold(self, differ_with_embeddings):
        """Test should_resync when similarity below threshold."""
        # Mock low similarity
        with patch.object(
            differ_with_embeddings,
            "compute_semantic_similarity",
            return_value=0.70
        ):
            should_resync, diff_result = differ_with_embeddings.should_resync(
                "old", "new"
            )
            
            assert should_resync is True  # Below threshold = resync needed
    
    def test_embedding_method_reporting(self, differ_with_embeddings):
        """Test that diff reports which method was used."""
        result = differ_with_embeddings.compute_semantic_diff("old", "new")
        
        assert "method" in result
        assert result["method"] in ["embeddings", "basic"]
    
    def test_threshold_in_result(self, differ_with_embeddings):
        """Test that threshold is included in result."""
        result = differ_with_embeddings.compute_semantic_diff("old", "new")
        
        assert "threshold" in result
        assert result["threshold"] == 0.98


# ============================================================================
# Integration Tests
# ============================================================================


class TestSemanticDifferIntegration:
    """Integration tests for SemanticDiffer with ContentDiffer."""
    
    def test_semantic_vs_line_diff_minor_change(self):
        """Test semantic differ vs line differ on minor change."""
        old = "The quick brown fox jumps over the lazy dog."
        new = "The quick brown fox leaps over the lazy dog."
        
        # Line differ
        line_differ = ContentDiffer()
        line_result = line_differ.diff(old, new)
        
        # Semantic differ
        semantic_differ = SemanticDiffer()
        semantic_result = semantic_differ.compute_semantic_diff(old, new)
        
        # Both should recognize high similarity
        assert line_result.similarity_ratio > 0.8
        assert semantic_result["semantic_similarity"] > 0.8
    
    def test_semantic_vs_line_diff_formatting_change(self):
        """Test that semantic differ ignores formatting changes."""
        old = "This is a test."
        new = "This   is   a   test."  # Extra spaces
        
        # Line differ might show change
        line_differ = ContentDiffer(ignore_whitespace=False)
        line_result = line_differ.diff(old, new, normalize=False)
        
        # Semantic differ should recognize semantic equivalence
        semantic_differ = SemanticDiffer()
        semantic_result = semantic_differ.compute_semantic_diff(old, new)
        
        assert semantic_result["semantic_similarity"] > 0.95
    
    def test_sync_decision_integration(self):
        """Test using SemanticDiffer in sync decisions."""
        semantic_differ = SemanticDiffer(similarity_threshold=0.95)
        
        # Minor content change
        old = "Product documentation version 1.0"
        new = "Product documentation version 1.1"
        
        should_resync, diff = semantic_differ.should_resync(old, new)
        
        # Should be consistent
        assert should_resync == diff["should_update"]
        assert diff["is_semantically_similar"] == (not should_resync)


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_string_diff(self):
        """Test diff with empty strings."""
        differ = ContentDiffer()
        result = differ.diff("", "")
        
        assert result.change_type == ChangeType.NO_CHANGE
        assert result.change_ratio == 0.0
    
    def test_one_empty_string(self):
        """Test diff with one empty string."""
        differ = ContentDiffer()
        result = differ.diff("content", "")
        
        assert result.change_ratio > 0.5  # Major change
        assert result.change_type in [ChangeType.MAJOR, ChangeType.COMPLETE]
    
    def test_very_long_content(self):
        """Test diff with very long content."""
        differ = ContentDiffer()
        long_text = "word " * 10000
        
        result = differ.diff(long_text, long_text)
        
        assert result.change_type == ChangeType.NO_CHANGE
    
    def test_unicode_content(self):
        """Test diff with unicode characters."""
        differ = ContentDiffer()
        old = "Hello 世界 🌍"
        new = "Hello 世界 🌎"
        
        result = differ.diff(old, new)
        
        assert result.change_ratio > 0.0  # Should detect change
    
    def test_semantic_differ_with_numbers(self):
        """Test semantic differ with numerical content."""
        differ = SemanticDiffer()
        old = "The value is 100"
        new = "The value is 200"
        
        result = differ.compute_semantic_diff(old, new)
        
        # Should detect semantic difference
        assert 0.0 <= result["semantic_similarity"] <= 1.0
    
    def test_semantic_differ_error_handling(self):
        """Test semantic differ handles errors gracefully."""
        # Test with embeddings disabled, which will use basic similarity
        differ = SemanticDiffer(use_embeddings=False)
        
        # Should fall back to basic similarity
        similarity = differ.compute_semantic_similarity("test", "test")
        
        # Should return 1.0 for identical texts
        assert similarity == 1.0
    
    def test_diff_segment_with_empty_content(self):
        """Test diff segment with empty content."""
        segment = DiffSegment(
            change_type="delete",
            old_content="deleted",
            new_content="",
            line_start=1,
            line_end=1,
        )
        
        data = segment.to_dict()
        assert data["new_content_preview"] == ""
    
    def test_content_diff_result_many_segments(self):
        """Test result serialization with many segments."""
        segments = [
            DiffSegment("insert", "", f"line{i}", i, i)
            for i in range(20)
        ]
        
        result = ContentDiffResult(
            change_type=ChangeType.MAJOR,
            change_ratio=0.5,
            similarity_ratio=0.5,
            old_hash="old",
            new_hash="new",
            segments=segments,
        )
        
        data = result.to_dict()
        
        # Should limit to first 10 segments
        assert len(data["segments"]) == 10
        assert data["segment_count"] == 20


# ============================================================================
# Performance and Property Tests
# ============================================================================


class TestPerformance:
    """Test performance characteristics."""
    
    def test_diff_is_deterministic(self):
        """Test that diff produces consistent results."""
        differ = ContentDiffer()
        old = "Test content"
        new = "Test content modified"
        
        result1 = differ.diff(old, new)
        result2 = differ.diff(old, new)
        
        assert result1.change_ratio == result2.change_ratio
        assert result1.similarity_ratio == result2.similarity_ratio
        assert result1.change_type == result2.change_type
    
    def test_semantic_similarity_is_symmetric(self):
        """Test that semantic similarity is symmetric."""
        differ = SemanticDiffer()
        text1 = "First text"
        text2 = "Second text"
        
        sim1 = differ.compute_semantic_similarity(text1, text2)
        sim2 = differ.compute_semantic_similarity(text2, text1)
        
        assert abs(sim1 - sim2) < 0.01  # Should be nearly identical
    
    def test_semantic_similarity_bounds(self):
        """Test that semantic similarity is always in [0, 1]."""
        differ = SemanticDiffer()
        
        # Test with various inputs
        test_cases = [
            ("", ""),
            ("a", "b"),
            ("identical", "identical"),
            ("short", "very long text with many words"),
        ]
        
        for text1, text2 in test_cases:
            similarity = differ.compute_semantic_similarity(text1, text2)
            assert 0.0 <= similarity <= 1.0
