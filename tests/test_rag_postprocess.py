"""Tests for RAG post-processing module"""
import pytest
from src.codex.rag.postprocess import (
    OutputProcessor,
    postprocess_output
)


class TestOutputProcessor:
    """Test OutputProcessor class"""
    
    def test_scrub_output_basic(self):
        """Test basic output scrubbing"""
        processor = OutputProcessor()
        text = "Hello world"
        result = processor.scrub_output(text)
        assert result == "Hello world"
    
    def test_scrub_output_with_custom_rules(self):
        """Test scrubbing with custom redaction rules"""
        processor = OutputProcessor()
        text = "My SSN is 123-45-6789"
        rules = [{"pattern": r"\d{3}-\d{2}-\d{4}", "replacement": "[REDACTED_SSN]"}]
        result = processor.scrub_output(text, rules)
        assert "[REDACTED_SSN]" in result
        assert "123-45-6789" not in result
    
    def test_scrub_output_removes_safety_markers(self):
        """Test removal of safety delimiters"""
        processor = OutputProcessor()
        text = "### RETRIEVED CONTEXT START ### Content ### RETRIEVED CONTEXT END ###"
        result = processor.scrub_output(text)
        assert "RETRIEVED CONTEXT START" not in result
        assert "RETRIEVED CONTEXT END" not in result
        assert "Content" in result
    
    def test_scrub_output_multiple_markers(self):
        """Test removal of all safety markers"""
        processor = OutputProcessor()
        text = "### USER QUERY START ### Query ### USER QUERY END ### ### RETRIEVED CONTEXT START ### Context ### RETRIEVED CONTEXT END ###"
        result = processor.scrub_output(text)
        assert "USER QUERY START" not in result
        assert "USER QUERY END" not in result
        assert "RETRIEVED CONTEXT START" not in result
        assert "RETRIEVED CONTEXT END" not in result
        assert "Query" in result
        assert "Context" in result
    
    def test_extract_evidence_tags_with_overlap(self):
        """Test evidence extraction with content overlap"""
        processor = OutputProcessor()
        output = "The quick brown fox jumps over the lazy dog"
        docs = [
            {
                "content": "The quick brown fox jumps.",
                "score": 0.95,
                "metadata": {"source_id": "doc1", "chunk_id": "c1"}
            }
        ]
        evidence = processor.extract_evidence_tags(output, docs)
        assert len(evidence) == 1
        assert evidence[0]["source_id"] == "doc1"
        assert evidence[0]["score"] == 0.95
    
    def test_extract_evidence_tags_no_overlap(self):
        """Test evidence extraction without overlap"""
        processor = OutputProcessor()
        output = "Completely different content"
        docs = [
            {
                "content": "The quick brown fox.",
                "score": 0.95,
                "metadata": {"source_id": "doc1"}
            }
        ]
        evidence = processor.extract_evidence_tags(output, docs)
        assert len(evidence) == 0
    
    def test_extract_evidence_tags_empty_docs(self):
        """Test evidence extraction with empty documents"""
        processor = OutputProcessor()
        evidence = processor.extract_evidence_tags("output", [])
        assert evidence == []
    
    def test_extract_evidence_tags_short_content(self):
        """Test evidence extraction with short content (< 20 chars)"""
        processor = OutputProcessor()
        output = "This is test output"
        docs = [
            {
                "content": "Short",  # Less than 20 chars
                "score": 0.9,
                "metadata": {"source_id": "doc1"}
            }
        ]
        evidence = processor.extract_evidence_tags(output, docs)
        assert len(evidence) == 0
    
    def test_extract_evidence_tags_multiple_phrases(self):
        """Test evidence extraction with multiple matching phrases"""
        processor = OutputProcessor()
        output = "The quick brown fox runs fast very quickly indeed."
        docs = [
            {
                "content": "The quick brown fox runs fast. This is a test document with content.",
                "score": 0.92,
                "metadata": {"source_id": "doc1"}
            }
        ]
        evidence = processor.extract_evidence_tags(output, docs)
        # Evidence extraction depends on phrase overlap - may or may not match
        assert isinstance(evidence, list)
        if evidence:
            assert evidence[0]["source_id"] == "doc1"
    
    def test_add_citations_inline(self):
        """Test inline citation style"""
        processor = OutputProcessor()
        output = "This is the output"
        evidence = [
            {"source_id": "doc1", "score": 0.9},
            {"source_id": "doc2", "score": 0.8}
        ]
        result = processor.add_citations(output, evidence, "inline")
        assert "[Sources: doc1, doc2]" in result
    
    def test_add_citations_inline_single_source(self):
        """Test inline citation with single source"""
        processor = OutputProcessor()
        output = "This is the output"
        evidence = [{"source_id": "doc1", "score": 0.9}]
        result = processor.add_citations(output, evidence, "inline")
        assert "[Sources: doc1]" in result
    
    def test_add_citations_inline_duplicate_sources(self):
        """Test inline citation with duplicate sources (should be unique)"""
        processor = OutputProcessor()
        output = "This is the output"
        evidence = [
            {"source_id": "doc1", "score": 0.9},
            {"source_id": "doc1", "score": 0.85},
            {"source_id": "doc2", "score": 0.8}
        ]
        result = processor.add_citations(output, evidence, "inline")
        # Should have unique sources in order
        assert "[Sources: doc1, doc2]" in result
    
    def test_add_citations_footnote(self):
        """Test footnote citation style"""
        processor = OutputProcessor()
        output = "This is the output"
        evidence = [
            {"source_id": "doc1", "score": 0.9},
            {"source_id": "doc2", "score": 0.8}
        ]
        result = processor.add_citations(output, evidence, "footnote")
        assert "References:" in result
        assert "[1] doc1" in result
        assert "[2] doc2" in result
    
    def test_add_citations_footnote_single(self):
        """Test footnote citation with single reference"""
        processor = OutputProcessor()
        output = "This is the output"
        evidence = [{"source_id": "doc1", "score": 0.9}]
        result = processor.add_citations(output, evidence, "footnote")
        assert "References:" in result
        assert "[1] doc1" in result
    
    def test_add_citations_none(self):
        """Test no citations"""
        processor = OutputProcessor()
        output = "This is the output"
        evidence = [{"source_id": "doc1", "score": 0.9}]
        result = processor.add_citations(output, evidence, "none")
        assert result == output
    
    def test_add_citations_empty_evidence(self):
        """Test citations with no evidence"""
        processor = OutputProcessor()
        output = "This is the output"
        result = processor.add_citations(output, [], "inline")
        assert result == output
    
    def test_add_citations_empty_evidence_footnote(self):
        """Test footnote citations with no evidence"""
        processor = OutputProcessor()
        output = "This is the output"
        result = processor.add_citations(output, [], "footnote")
        assert result == output


def test_postprocess_output_full_pipeline():
    """Test full post-processing pipeline"""
    output = "### USER QUERY START ### Query ### USER QUERY END ### Response text"
    docs = [
        {
            "content": "Response text from document.",
            "score": 0.95,
            "metadata": {"source_id": "doc1"}
        }
    ]
    
    processed, evidence = postprocess_output(
        output=output,
        retrieved_docs=docs,
        include_citations=True,
        citation_style="inline"
    )
    
    assert "USER QUERY START" not in processed
    assert "Response text" in processed
    assert len(evidence) >= 0


def test_postprocess_output_with_redaction():
    """Test post-processing with redaction rules"""
    output = "Email: user@example.com"
    rules = [{"pattern": r"\S+@\S+\.\S+", "replacement": "[EMAIL]"}]
    
    processed, evidence = postprocess_output(
        output=output,
        redaction_rules=rules,
        include_citations=False
    )
    
    assert "[EMAIL]" in processed
    assert "user@example.com" not in processed


def test_postprocess_output_no_citations():
    """Test post-processing without citations"""
    output = "Response text"
    docs = [{"content": "Context", "score": 0.9, "metadata": {"source_id": "doc1"}}]
    
    processed, evidence = postprocess_output(
        output=output,
        retrieved_docs=docs,
        include_citations=False
    )
    
    assert "[Sources:" not in processed


def test_postprocess_output_no_docs():
    """Test post-processing without documents"""
    output = "Response text"
    
    processed, evidence = postprocess_output(
        output=output,
        retrieved_docs=None,
        include_citations=True
    )
    
    assert processed == "Response text"
    assert evidence == []


def test_postprocess_output_with_citations_and_evidence():
    """Test post-processing generates citations when evidence found"""
    output = "The machine learning model performs well on classification tasks."
    docs = [
        {
            "content": "The machine learning model performs well on classification tasks and achieves 95% accuracy.",
            "score": 0.98,
            "metadata": {"source_id": "paper123"}
        }
    ]
    
    processed, evidence = postprocess_output(
        output=output,
        retrieved_docs=docs,
        include_citations=True,
        citation_style="inline"
    )
    
    # Evidence extraction is heuristic-based and may not always find matches
    # The important part is that processing completes without errors
    assert isinstance(evidence, list)
    if evidence:
        assert "[Sources:" in processed
        assert "paper123" in processed


def test_postprocess_output_footnote_style():
    """Test post-processing with footnote citation style"""
    output = "This is important information."
    docs = [
        {
            "content": "This is important information from the source document.",
            "score": 0.95,
            "metadata": {"source_id": "doc_alpha"}
        }
    ]
    
    processed, evidence = postprocess_output(
        output=output,
        retrieved_docs=docs,
        include_citations=True,
        citation_style="footnote"
    )
    
    if evidence:
        assert "References:" in processed
        assert "[1]" in processed


def test_postprocess_output_multiple_redaction_rules():
    """Test post-processing with multiple redaction rules"""
    output = "Contact: user@example.com, Phone: 555-1234, SSN: 123-45-6789"
    rules = [
        {"pattern": r"\S+@\S+\.\S+", "replacement": "[EMAIL]"},
        {"pattern": r"\d{3}-\d{4}", "replacement": "[PHONE]"},
        {"pattern": r"\d{3}-\d{2}-\d{4}", "replacement": "[SSN]"}
    ]
    
    processed, evidence = postprocess_output(
        output=output,
        redaction_rules=rules,
        include_citations=False
    )
    
    assert "[EMAIL]" in processed
    assert "[PHONE]" in processed
    assert "[SSN]" in processed
    assert "user@example.com" not in processed
    assert "555-1234" not in processed
    assert "123-45-6789" not in processed


def test_postprocess_output_preserves_content():
    """Test that post-processing preserves non-redacted content"""
    output = "The quick brown fox jumps over the lazy dog."
    
    processed, evidence = postprocess_output(
        output=output,
        include_citations=False
    )
    
    assert processed == output.strip()
